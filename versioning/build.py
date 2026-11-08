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

ROOT = Path(__file__).resolve().parent.parent
MANUALS = ("main", "user_manual", "admin_manual", "developer_manual")


def source_tree(stage: Path, slug: str, manual: str) -> Path:
    target = stage / slug / manual
    if slug == "main":
        shutil.copytree(ROOT / manual, target)
    else:
        shutil.copytree(ROOT / "versioned/base" / manual, target)
        overlay = ROOT / "versioned" / slug / manual
        if overlay.exists():
            shutil.copytree(overlay, target, dirs_exist_ok=True)
        if manual == "developer_manual":
            shutil.copytree(ROOT / "developer_manual/html", target / "html")
            (target / "api").mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "developer_manual/api/openapi.rst",
                         target / "api/openapi.rst")
        # Keep these manuals independent of main while retaining the shared
        # Sphinx config and shared (version-neutral) Swagger UI assets.
        config = (
            "import os, sys\n"
            "from pathlib import Path\n"
            "root = Path(os.environ['LIBRESIGN_DOC_ROOT'])\n"
            "sys.path.insert(0, str(root))\n"
            "from conf import *\n"
            "html_context = {**html_context, 'conf_py_path': '/versioned/base/"
            + manual + "/'}\n"
            "html_logo = str(root / 'images/logo.png' if "
            "(root / 'images/logo.png').is_file() else "
            "root / 'main/images/logo.png')\n"
            "html_extra_path = [str(root / 'developer_manual/html')] "
            "if os.environ.get('LIBRESIGN_DOC_MANUAL') == 'developer_manual' "
            "else []\n"
        )
        (target / "conf.py").write_text(config, encoding="utf-8")
    return target


def run_sphinx(source: Path, destination: Path, entry: dict, catalog: dict) -> None:
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
        key=lambda v: (v["slug"] == "main",
                       -(int(v["slug"]) if v["slug"] != "main" else 0)),
    )
    environment = Environment(
        loader=FileSystemLoader(str(ROOT / "_templates")),
        autoescape=select_autoescape(["html"]),
    )
    return environment.get_template("home.html").render(
        versions=versions,
        current_stable=catalog["current_stable"],
        preview_pr=os.environ.get("LIBRESIGN_PREVIEW_PR", ""),
    )


def legacy_redirects(output: Path, current: str) -> None:
    destination = output / current
    if not (destination / "index.html").is_file():
        raise ValueError("Cannot create legacy redirects without stable landing page")
    catalog = json.loads((output / "versions.json").read_text(encoding="utf-8"))
    if catalog["current_stable"] != current:
        raise ValueError("Current stable line differs from published catalog")
    (output / "index.html").write_text(version_overview(catalog), encoding="utf-8")
    # Previous URLs did not include a version prefix. Preserve page paths
    # when the same page exists in current stable; otherwise go to that
    # manual's landing page, never silently to a development-only page.
    for manual in MANUALS[1:]:
        base = output / manual
        base.mkdir(parents=True, exist_ok=True)
        main_source = output / "main" / manual
        for page in main_source.rglob("*.html"):
            relative = page.relative_to(main_source)
            target = destination / manual / relative
            if not target.is_file():
                target = destination / manual / "index.html"
            redirect = base / relative
            redirect.parent.mkdir(parents=True, exist_ok=True)
            redirect.write_text(
                redirect_html("/" + str(target.relative_to(output)).replace(os.sep, "/")),
                encoding="utf-8",
            )
        (base / "index.html").write_text(
            redirect_html(f"/{current}/{manual}/"), encoding="utf-8",
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
            for manual in MANUALS:
                source = source_tree(stage, slug, manual)
                run_sphinx(source, output / slug / ("" if manual == "main" else manual), entry, catalog)
            api = output / slug / "developer_manual/api"
            api.mkdir(parents=True, exist_ok=True)
            (api / "openapi.json").write_bytes(contracts[slug])
            provenance = {
                "slug": slug, "branch": entry["branch"], "app_commit": entry["app_commit"],
                "app_version": entry["app_version"],
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
