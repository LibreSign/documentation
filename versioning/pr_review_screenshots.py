"""Render unreleased release documentation for visual review in a PR only.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from versioning.build import ROOT, run_sphinx, source_tree
from versioning.screenshots import Screenshot, take_screenshots


def render_screenshots(site: Path, preview_root: str) -> list[Path]:
    catalog = json.loads((site / "versions.json").read_text(encoding="utf-8"))
    versions = catalog["versions"]
    development = next(version for version in versions if version["slug"] == "main")
    next_major = development["app_version"].split(".", 1)[0]
    if not next_major.isdecimal():
        raise ValueError("Invalid development LibreSign release")
    overlay = ROOT / "versioned" / next_major / "developer_manual"
    if not overlay.is_dir():
        return []

    version = next((entry for entry in versions if entry["slug"] == next_major), None)
    if version is None:
        # Private PR review rendering only. Do not add an unreleased version to
        # the real site catalog, the production output or the version switcher.
        version = {**development, "slug": next_major, "status": "development"}
        with tempfile.TemporaryDirectory(prefix="libresign-doc-review-") as tmp:
            source = source_tree(Path(tmp), next_major, "developer_manual")
            output = site / "_review" / next_major / "developer_manual"
            run_sphinx(source, output, version, catalog)
    else:
        output = site / next_major / "developer_manual"

    plan = []
    for source in sorted(overlay.rglob("*.rst")):
        relative = source.relative_to(overlay).with_suffix(".html")
        if not (output / relative).is_file():
            raise ValueError(f"Sphinx did not render {relative}")
        route = (f"/_review/{next_major}/developer_manual/{relative.as_posix()}"
                 if version["status"] == "development" else
                 f"/{next_major}/developer_manual/{relative.as_posix()}")
        plan.append(Screenshot(
            f"docs-{next_major}-{'-'.join(relative.with_suffix('').parts)}.png", route
        ))

    destination = site / "_review" / "screenshots"
    images = take_screenshots(site, destination, plan=plan)
    if not images:
        return []

    base = preview_root.rstrip("/") + "/_review/screenshots/"
    lines = [
        "<!-- libresign-documentation-review-screenshots -->",
        f"### Rendered documentation — LibreSign {next_major} (unreleased preview)",
        "",
        "Screenshots generated from the Sphinx output for review. The new",
        "documentation is not published in versions 13–15 or the development",
        "`main` manual. Images are review evidence, not repository source files.",
        "",
    ]
    for image in images:
        title = image.stem.replace(f"docs-{next_major}-", "").replace("-", " / ")
        lines += [f"**{title}**", "", f"![{title}]({base}{image.name})", ""]
    (site / "_review" / "screenshots-comment.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return images


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--preview-root", required=True)
    args = parser.parse_args()
    images = render_screenshots(args.site, args.preview_root)
    print(f"Generated {len(images)} PR review screenshots")


if __name__ == "__main__":
    main()
