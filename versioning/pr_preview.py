"""Publish navigable PR previews from the actual documentation branches.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

PREVIEW_MARKER = "<!-- libresign-documentation-preview-links -->"

def preview_comment(preview_url: str, major: str, *,
                    action_version: str = "", built_at: str = "") -> str:
    """Render the same preview card as the LibreSign and LibreCode websites."""
    if action_version and not re.fullmatch(r"[A-Za-z0-9._+-]{1,80}", action_version):
        raise ValueError("Invalid preview action version")
    timestamp = built_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", timestamp):
        raise ValueError("Invalid preview build timestamp")
    version = f" {action_version}" if action_version else ""
    qr_url = "https://qr.rossjrw.com/?color.dark=0d1117&url=" + preview_url
    pages = "https://github.com/LibreSign/site-preview"
    return "\n".join([
        f"[PR Preview Action](https://github.com/LibreSign/pr-preview-action){version}",
        ":---:",
        f'| <p><img src="{qr_url}" height="100" align="right" '
        f'alt="QR code for preview link"></p> :rocket: View preview at '
        f'<br> {preview_url} <br><br>',
        f'| <h6>Built to branch [`gh-pages`]({pages}/tree/gh-pages) at {timestamp}. '
        f'<br> Preview will be ready when the [GitHub Pages deployment]'
        f'({pages}/deployments) is complete. <br><br> </h6>',
        "",
        f"**Documentation:** [All versions]({preview_url}) · "
        f"[LibreSign {major} development manual]({preview_url}main/developer_manual/) · "
        f"[Review notes]({preview_url}_review/)",
        "",
        f"Preview is separate from production. LibreSign {major} has not been released; "
        "the development manual describes the upcoming version.",
        "",
        PREVIEW_MARKER,
        "",
    ])

def preview_unreleased(site: Path, preview_root: str, *,
                       action_version: str = "", built_at: str = "") -> list[str]:
    """Link to the real development manual; never invent a future release tree."""
    url_parts = urlsplit(preview_root)
    if (url_parts.scheme != "https" or not url_parts.hostname or
            url_parts.username or url_parts.password or url_parts.query or
            url_parts.fragment or not re.fullmatch(
                r"https://[A-Za-z0-9.-]+(?::[0-9]+)?(?:/[A-Za-z0-9_./-]*)?", preview_root)):
        raise ValueError("Preview links must use a safe HTTPS URL")
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
        preview_comment(f"{url}/", major, action_version=action_version,
                        built_at=built_at), encoding="utf-8",
    )
    (review / "routes.txt").write_text("\n".join(routes) + "\n", encoding="utf-8")
    return routes


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a preview for documentation")
    parser.add_argument("--site", type=Path, default=Path("_publish"))
    parser.add_argument("--preview-root", required=True)
    parser.add_argument("--action-version", default="")
    parser.add_argument("--built-at", default="")
    args = parser.parse_args()
    routes = preview_unreleased(args.site.resolve(), args.preview_root,
                                action_version=args.action_version,
                                built_at=args.built_at)
    print(f"Prepared {len(routes)} navigable preview URLs")


if __name__ == "__main__":
    main()
