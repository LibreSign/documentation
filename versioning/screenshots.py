"""Capture version-specific Sphinx screenshots from the published catalog.

The version catalog is generated from LibreSign application manifests by
versioning.build. Never maintain release numbers in GitHub Actions.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SLUG = re.compile(r"(?:main|[1-9][0-9]*)\Z")

# This route is served in memory. It is never written to the published tree.
LIGHT_ROUTE = "/_capture-light.html"
LIGHT_PAGE = (
    b'<!doctype html><html lang="en"><head><meta charset="utf-8">'
    b'<script>localStorage.setItem("theme","light");'
    b'location.replace("./");</script></head></html>'
)


@dataclass(frozen=True)
class Screenshot:
    filename: str
    route: str


def development_webhook_screenshots(site: Path, slugs: list[str]) -> list[Screenshot]:
    section = site / "main/developer_manual/webhooks"
    if "main" not in slugs or not section.is_dir():
        return []
    pages = ("index", "configuration", "signing_completion")
    screenshots = []
    for name in pages:
        path = section / f"{name}.html"
        if not path.is_file():
            raise ValueError(f"Missing webhook documentation page: {path}")
        screenshots.append(Screenshot(
            f"webhooks-{name}-main.png",
            f"/main/developer_manual/webhooks/{name}.html",
        ))
    return screenshots


def screenshot_plan(site: Path) -> list[Screenshot]:
    """List only versions actually built for this publish candidate."""
    catalog_file = site / "versions.json"
    if not catalog_file.is_file():
        raise ValueError("The built site has no versions.json catalog")
    catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
    entries = catalog.get("versions")
    if not isinstance(entries, list) or not entries:
        raise ValueError("versions.json has no documentation versions")

    slugs = []
    for entry in entries:
        slug = entry.get("slug") if isinstance(entry, dict) else None
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            raise ValueError(f"Invalid documentation version: {slug!r}")
        if slug in slugs:
            raise ValueError(f"Duplicate documentation version: {slug}")
        if not (site / slug / "index.html").is_file():
            raise ValueError(f"Version {slug} is listed but has no built index.html")
        slugs.append(slug)

    current = catalog.get("current_stable")
    if current not in slugs or current == "main":
        raise ValueError("Current stable version is not present in the built site")
    api = site / current / "developer_manual/api/openapi.html"
    if not api.is_file():
        raise ValueError(f"Missing OpenAPI page for current stable {current}")
    if not (site / "index.html").is_file():
        raise ValueError("Missing documentation versions landing page")

    # Match the public index ordering, regardless of catalog insertion order.
    slugs.sort(key=lambda slug: (slug == "main",
                                -(int(slug) if slug != "main" else 0)))
    screenshots = [
        Screenshot("libresign-versions-home-dark.png", "/"),
        Screenshot("libresign-versions-home-light.png", LIGHT_ROUTE),
    ]
    screenshots.extend(development_webhook_screenshots(site, slugs))
    screenshots.extend(
        Screenshot(f"libresign-{slug}.png", f"/{slug}/")
        for slug in slugs
    )
    screenshots.append(
        Screenshot(f"openapi-{current}.png",
                   f"/{current}/developer_manual/api/openapi.html")
    )
    return screenshots


class PreviewHandler(SimpleHTTPRequestHandler):
    """Serve generated documentation without modifying its content."""

    def do_GET(self) -> None:
        if self.path == LIGHT_ROUTE:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(LIGHT_PAGE)))
            self.end_headers()
            self.wfile.write(LIGHT_PAGE)
            return
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        # CI output should focus on the screenshots, not Chrome asset requests.
        pass


def take_screenshots(site: Path, output: Path, browser: str | None = None) -> list[Path]:
    screenshots = screenshot_plan(site)
    chrome = browser or shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        raise RuntimeError("Google Chrome/Chromium is required for screenshots")

    output.mkdir(parents=True, exist_ok=True)
    handler = partial(PreviewHandler, directory=str(site))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            origin = f"http://127.0.0.1:{server.server_port}"
            files = []
            for spec in screenshots:
                destination = (output / spec.filename).resolve()
                # An isolated Chrome profile ensures the light screenshot
                # cannot affect the next version's preferred color scheme.
                with tempfile.TemporaryDirectory(prefix="libresign-chrome-") as profile:
                    command = [
                        chrome, "--headless", "--no-sandbox", "--disable-gpu",
                        "--disable-dev-shm-usage", "--hide-scrollbars",
                        "--virtual-time-budget=8000", "--window-size=1440,1100",
                        f"--user-data-dir={profile}",
                        f"--screenshot={destination}", origin + spec.route,
                    ]
                    try:
                        subprocess.run(
                            command, check=True, capture_output=True,
                            text=True, timeout=90,
                        )
                    except subprocess.CalledProcessError as error:
                        raise RuntimeError(
                            f"Chrome failed to capture {spec.route}: "
                            f"{error.stderr[-2000:]}"
                        ) from error
                if not destination.is_file() or destination.stat().st_size == 0:
                    raise RuntimeError(f"Missing or empty screenshot: {destination}")
                files.append(destination)
                print(f"Captured {spec.route} -> {destination.name}", flush=True)
            return files
        finally:
            server.shutdown()
            thread.join(timeout=10)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Screenshot the generated documentation versions dynamically"
    )
    parser.add_argument("--site", type=Path, default=Path("_publish"))
    parser.add_argument("--output", type=Path, default=Path("screenshots"))
    parser.add_argument("--browser", help="Chrome/Chromium executable (optional)")
    args = parser.parse_args()
    take_screenshots(args.site.resolve(), args.output.resolve(), args.browser)


if __name__ == "__main__":
    main()
