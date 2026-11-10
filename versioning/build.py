"""Build isolated Sphinx sites with an exact LibreSign source revision per line.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from versioning.catalog import discover, get_version, load_policy
from versioning.sources import branch_sources

ROOT = Path(__file__).resolve().parent.parent
MANUALS = ("main", "user_manual", "admin_manual", "developer_manual")


def source_tree(stage: Path, slug: str, manual: str) -> Path:
    """Stage one manual from the checked-out documentation release branch."""
    repository = branch_sources(stage, slug, repository=ROOT)
    target = stage / slug / manual
    shutil.copytree(repository / manual, target)
    if slug != "main":
        # Sphinx renders temporary sources; GitHub edit links must still point
        # at the real file in the stableNN branch, not at a staging directory.
        config = (
            "import os, sys\n"
            "from pathlib import Path\n"
            "root = Path(os.environ['LIBRESIGN_DOC_ROOT'])\n"
            "sys.path.insert(0, str(root))\n"
            "from conf import *\n"
            "html_context = {**html_context, "
            f"'github_version': 'stable{slug}', "
            f"'conf_py_path': '/{manual}/'" + "}\n"
            "html_logo = str(root / 'images/logo.png')\n"
            "html_extra_path = [str(root / 'developer_manual/html')] "
            "if os.environ.get('LIBRESIGN_DOC_MANUAL') == 'developer_manual' "
            "else []\n"
        )
        (target / "conf.py").write_text(config, encoding="utf-8")
    return target


def run_sphinx(source: Path, destination: Path, entry: dict, catalog: dict, *,
               review_only: bool = False) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env.update({
        "LIBRESIGN_DOC_ROOT": str(ROOT),
        "LIBRESIGN_DOC_MANUAL": source.name,
        "LIBRESIGN_DOC_VERSION": entry["slug"],
        "LIBRESIGN_DOC_STATUS": entry["status"],
        "LIBRESIGN_APP_VERSION": entry["app_version"],
        "LIBRESIGN_NEXTCLOUD_VERSION": (
            str(entry["nextcloud_min"]) if
            entry["nextcloud_min"] == entry["nextcloud_max"] else
            f'{entry["nextcloud_min"]}-{entry["nextcloud_max"]}'
        ),
        "LIBRESIGN_APP_SHA": entry["app_commit"],
        "LIBRESIGN_VERSION_CATALOG": json.dumps(catalog),
    })
    if review_only:
        env["LIBRESIGN_DOC_REVIEW_PREFIX"] = "/_review"
    else:
        env.pop("LIBRESIGN_DOC_REVIEW_PREFIX", None)
    cmd = ["sphinx-build", "-b", "html", "-n"]
    if entry["slug"] != "main" or source.name == "developer_manual":
        cmd.extend(["-W", "--keep-going"])
    cmd.extend([str(source), str(destination)])
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)


def redirect_html(target: str) -> str:
    # A Pages preview is mounted under a nested URL prefix, not at /.
    site_root = os.environ.get("LIBRESIGN_DOC_BASE_PATH", "").rstrip("/")
    if site_root and target.startswith("/"):
        target = site_root + target
    quoted = html.escape(target, quote=True)
    json_target = json.dumps(target)
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<meta http-equiv='refresh' content='0; url={quoted}'>"
        f"<link rel='canonical' href='{quoted}'>"
        "<title>LibreSign documentation has moved</title></head><body>"
        f"<p>Moved to <a href='{quoted}'>{quoted}</a>.</p>"
        f"<script>location.replace({json_target} + location.search + "
        "location.hash);</script></body></html>"
    )


def version_overview(catalog: dict) -> str:
    """Generate the public entry page from the same version catalog as Sphinx."""
    versions = sorted(
        catalog["versions"],
        key=lambda v: (v["slug"] != "main",
                       -(int(v["slug"]) if v["slug"] != "main" else 0)),
    )
    stable = [entry for entry in versions
              if entry["slug"] != "main" and entry["status"] != "eol"]
    oldest_stable = min(stable, key=lambda entry: int(entry["slug"]))["slug"] if stable else None
    environment = Environment(
        loader=FileSystemLoader(str(ROOT / "_templates")),
        autoescape=select_autoescape(["html"]),
    )
    return environment.get_template("home.html").render(
        versions=versions,
        current_stable=catalog["current_stable"],
        oldest_stable=oldest_stable,
        docs_home_href="./",
        preview_pr=os.environ.get("LIBRESIGN_PREVIEW_PR", ""),
    )


def legacy_redirects(output: Path, current: str, *, routes: dict[str, str] | None = None) -> None:
    destination = output / current
    if not (destination / "index.html").is_file():
        raise ValueError("Cannot create legacy redirects without stable landing page")
    catalog = json.loads((output / "versions.json").read_text(encoding="utf-8"))
    if catalog["current_stable"] != current:
        raise ValueError("Current stable line differs from published catalog")
    (output / "index.html").write_text(version_overview(catalog), encoding="utf-8")
    if os.environ.get("LIBRESIGN_PREVIEW_PR"):
        # The homepage links to /_review/ before the later PR-only build
        # replaces this placeholder. Keep the initial link check strict.
        entry = output / "_review/index.html"
        entry.parent.mkdir(parents=True, exist_ok=True)
        entry.write_text(
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<title>Preview-only documentation</title></head><body>"
            "<main><h1>Preview-only documentation</h1>"
            "<p>Release-specific review pages are generated after validation.</p>"
            "</main></body></html>",
            encoding="utf-8",
        )
    # The previous unversioned URLs are a permanent migration interface.
    # Do not move their destinations when a future stable line is published.
    from versioning.seo import read_legacy_routes

    for old, target in (read_legacy_routes(ROOT) if routes is None else routes).items():
        destination_page = output / target
        if not destination_page.is_file():
            raise ValueError(f"Missing historical destination: {old} => {target}")
        legacy_page = output / old
        legacy_page.parent.mkdir(parents=True, exist_ok=True)
        legacy_page.write_text(
            redirect_html("/" + target),
            encoding="utf-8",
        )


def build(output: Path, selected: str = "all") -> dict:
    catalog, contracts = discover(load_policy(ROOT))
    slugs = [v["slug"] for v in catalog["versions"]]
    if selected != "all" and selected not in slugs:
        raise ValueError(f"Version {selected!r} not available in application manifests")
    targets = slugs if selected == "all" else [selected]
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="libresign-docs-source-") as tmp:
        stage = Path(tmp)
        for slug in targets:
            entry = get_version(catalog, slug)
            source = branch_sources(stage, slug, repository=ROOT)
            if slug == "main":
                entry["documentation_commit"] = subprocess.check_output(
                    ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                    text=True, timeout=20,
                ).strip()
            else:
                entry["documentation_commit"] = (
                    source / ".source-commit"
                ).read_text().strip()
            for manual in MANUALS:
                source = source_tree(stage, slug, manual)
                run_sphinx(source, output / slug / ("" if manual == "main" else manual), entry, catalog)
            api = output / slug / "developer_manual/api"
            api.mkdir(parents=True, exist_ok=True)
            (api / "openapi.json").write_bytes(contracts[slug])
            provenance = {
                "slug": slug, "branch": entry["branch"], "app_commit": entry["app_commit"],
                "app_version": entry["app_version"],
                "documentation_commit": entry["documentation_commit"],
                "source_url": entry["source_url"],
                "openapi_sha256": entry["openapi_sha256"],
                "manifest_sha256": entry["manifest_sha256"],
                "nextcloud_min": entry["nextcloud_min"],
                "nextcloud_max": entry["nextcloud_max"],
            }
            (api / "openapi.provenance.json").write_text(
                json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
            )
    (output / "versions.json").write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(ROOT / "assets/home.css", output / "home.css")
    shutil.copy2(ROOT / "assets/ecosystem-nav.css", output / "ecosystem-nav.css")
    shutil.copy2(ROOT / "assets/ecosystem-nav.js", output / "ecosystem-nav.js")
    shutil.copy2(ROOT / "assets/home-theme.js", output / "home-theme.js")
    shutil.copy2(ROOT / "images/logo.png", output / "logo.png")

    if selected == "all":
        legacy_redirects(output, catalog["current_stable"])
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_build")
    parser.add_argument("--version", default="all")
    args = parser.parse_args()
    build(args.output, args.version)


if __name__ == "__main__":
    main()
