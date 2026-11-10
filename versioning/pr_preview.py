"""Publish navigable PR previews from the actual documentation branches.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

PREVIEW_MARKER = "<!-- libresign-documentation-preview-links -->"


def preview_unreleased(site: Path, preview_root: str) -> list[str]:
    """Link to the real development manual; never invent a future release tree."""
    if not preview_root.startswith("https://"):
        raise ValueError("Preview links must use HTTPS")
    catalog = json.loads((site / "versions.json").read_text(encoding="utf-8"))
    main = next(entry for entry in catalog["versions"] if entry["slug"] == "main")
    major = main["app_version"].split(".", 1)[0]
    if not re.fullmatch(r"[1-9][0-9]*", major):
        raise ValueError("Invalid development version")
    routes = ["/", f"/{catalog['current_stable']}/", "/main/developer_manual/",
              "/_review/index.html"]
    for route in routes[:-1]:
        target = site / route.lstrip("/") / "index.html"
        if not target.is_file():
            raise ValueError(f"Missing source for preview route: {route}")

    review = site / "_review"
    review.mkdir(exist_ok=True)
    url = preview_root.rstrip("/")
    development_url = f"{url}/main/developer_manual/"
    message = (
        f"<p>LibreSign {html.escape(major)} is in development. "
        "Documentation is edited in the main branch, not copied into "
        "a release-specific overlay.</p>"
    )
    (review / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<title>Preview-only documentation</title></head><body>'
        '<main><h1>Preview-only documentation</h1>' + message +
        '<p><a href="../main/developer_manual/">Development manual</a></p>'
        '</main></body></html>', encoding="utf-8",
    )
    (review / "preview-comment.md").write_text(
        "\n".join([
            PREVIEW_MARKER,
            "### Navigable documentation preview",
            "",
            f"- [All published versions]({url}/)",
            f"- [LibreSign {major} development manual]({development_url})",
            "",
            "This preview is isolated from production. Documentation for the"
            " next release lives in the development branch until it is released.",
            "",
        ]), encoding="utf-8",
    )
    (review / "routes.txt").write_text("\n".join(routes) + "\n", encoding="utf-8")
    return routes


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a preview for documentation")
    parser.add_argument("--site", type=Path, default=Path("_publish"))
    parser.add_argument("--preview-root", required=True)
    args = parser.parse_args()
    routes = preview_unreleased(args.site.resolve(), args.preview_root)
    print(f"Prepared {len(routes)} navigable preview URLs")


if __name__ == "__main__":
    main()
