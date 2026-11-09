"""Publish navigable, isolated previews of not-yet-released documentation.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import quote

from versioning.build import ROOT, run_sphinx, source_tree
from versioning.verify import inspect_links

PREVIEW_MARKER = "<!-- libresign-documentation-preview-links -->"
REVIEW_MANUALS = ("user_manual", "admin_manual", "developer_manual")


def preview_unreleased(site: Path, preview_root: str) -> list[str]:
    """Render future-release overlays for PR review without publishing a release."""
    catalog = json.loads((site / "versions.json").read_text(encoding="utf-8"))
    versions = {entry["slug"]: entry for entry in catalog["versions"]}
    development = versions["main"]
    major = development["app_version"].split(".", 1)[0]
    if not re.fullmatch(r"[1-9][0-9]*", major):
        raise ValueError(f"Invalid development major: {major!r}")
    if not preview_root.startswith("https://"):
        raise ValueError("Preview links must use HTTPS")

    review = site / "_review"
    review.mkdir(exist_ok=True)
    routes = ["/", f"/{catalog['current_stable']}/",
              "/main/developer_manual/", "/_review/index.html"]
    candidates: list[tuple[str, str]] = []

    # An existing stable major is already fully rendered at /<major>/.
    # Never expose a synthetic stable site in the published version catalog.
    if major not in versions:
        overlay_root = ROOT / "versioned" / major
        for manual in REVIEW_MANUALS:
            overlay = overlay_root / manual
            if not overlay.is_dir():
                continue
            output = review / major / manual
            entry = {**development, "slug": major, "status": "development"}
            with tempfile.TemporaryDirectory(prefix="libresign-pr-review-") as tmp:
                source = source_tree(Path(tmp), major, manual)
                run_sphinx(source, output, entry, catalog)

            if manual == "developer_manual":
                # The preview reads the pinned *development* contract. It is
                # not a released stable OpenAPI and is never added to /16/.
                for filename in ("openapi.json", "openapi.provenance.json"):
                    source = site / "main/developer_manual/api" / filename
                    if not source.is_file():
                        raise ValueError(f"Missing development API: {source}")
                    shutil.copy2(source, output / "api" / filename)

            index = output / "index.html"
            if not index.is_file():
                raise ValueError(f"Missing preview index for {manual}")
            index_route = f"/_review/{major}/{manual}/index.html"
            routes.append(index_route)
            candidates.append((f"LibreSign {major} / {manual}", index_route))
            for rst in sorted(overlay.rglob("*.rst")):
                relative = rst.relative_to(overlay).with_suffix(".html")
                page = output / relative
                if not page.is_file():
                    raise ValueError(f"Sphinx did not render {rst.relative_to(ROOT)}")
                route = f"/_review/{major}/{manual}/{relative.as_posix()}"
                if route != index_route:
                    candidates.append((f"{major} / {manual} / {relative}", route))
                    routes.append(route)

            broken = [
                issue for page in output.rglob("*.html")
                for issue in inspect_links(site, page)
            ]
            if broken:
                raise ValueError("Broken unreleased-preview links:\n" +
                                 "\n".join(broken[:20]))

    # The navigation index is review-only; nothing under _review enters
    # versions.json, the version selector, or production Pages.
    links = "\n".join(
        '<li><a href="{}">{}</a></li>'.format(
            html.escape("../" + route.lstrip("/"), quote=True),
            html.escape(title),
        ) for title, route in candidates
    )
    message = ("Preview-only documentation; built from development application "
               "metadata and OpenAPI. Not a published stable LibreSign release.")
    (review / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<title>Preview-only documentation</title></head><body>'
        '<main><h1>Preview-only documentation</h1>'
        f'<p>{html.escape(message)}</p>'
        '<p><a href="../">Published-version PR preview</a></p>'
        f'<ul>{links}</ul></main></body></html>',
        encoding="utf-8",
    )

    root_url = preview_root.rstrip("/")
    comment = [
        PREVIEW_MARKER,
        "### Navigable documentation preview",
        "",
        f"- [All published documentation versions]({root_url}/)",
        f"- [Development manual (main)]({root_url}/main/developer_manual/)",
        f"- [Preview-only release pages]({root_url}/_review/)",
        "",
        "The preview is isolated from production. Unreleased pages use the",
        "development application contract for review, **not** a released",
        "stable LibreSign version. Sphinx, links and pinned OpenAPI are checked",
        "in CI; screenshots are not required.",
        "",
    ]
    if candidates:
        comment.extend(["**Unreleased pages available for review:**", ""])
        for title, route in candidates:
            comment.append(f"- [{title}]({root_url}{quote(route, safe='/')})")
    else:
        comment.append("No unpublished major-version overlay is present.")
    (review / "preview-comment.md").write_text(
        "\n".join(comment) + "\n", encoding="utf-8"
    )
    # These are the URLs the deployment workflow must verify on the real
    # preview origin, not just files checked in the checkout.
    unique_routes = list(dict.fromkeys(routes))
    for route in unique_routes:
        local = site / route.lstrip("/")
        if route.endswith("/"):
            local /= "index.html"
        if not local.is_file():
            raise ValueError(f"Preview route is missing: {route}")
    (review / "routes.txt").write_text(
        "\n".join(unique_routes) + "\n", encoding="utf-8"
    )
    return unique_routes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build review-only HTML for unpublished documentation")
    parser.add_argument("--site", type=Path, default=Path("_publish"))
    parser.add_argument("--preview-root", required=True)
    args = parser.parse_args()
    routes = preview_unreleased(args.site.resolve(), args.preview_root)
    print(f"Prepared {len(routes)} navigable preview URLs")


if __name__ == "__main__":
    main()
