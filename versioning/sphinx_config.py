"""Shared Sphinx overrides for every version/manual."""
from __future__ import annotations

import json
import os
from pathlib import Path


def configure(config: dict) -> None:
    root = Path(__file__).resolve().parent.parent
    slug = os.environ.get("LIBRESIGN_DOC_VERSION", "main")
    app_version = os.environ.get("LIBRESIGN_APP_VERSION", "development")
    nextcloud = os.environ.get("LIBRESIGN_NEXTCLOUD_VERSION", "unspecified")
    app_sha = os.environ.get("LIBRESIGN_APP_SHA", "")
    status = os.environ.get("LIBRESIGN_DOC_STATUS", "development")
    raw_catalog = os.environ.get("LIBRESIGN_VERSION_CATALOG", "{}")
    catalog = json.loads(raw_catalog)

    manual = os.environ.get("LIBRESIGN_DOC_MANUAL", "main")
    config["notfound_urls_prefix"] = (
        f"/{slug}/" + (f"{manual}/" if manual != "main" else "")
    )
    config["release"] = app_version
    config["version"] = slug
    context = dict(config.get("html_context", {}))
    context.update({
        "libresign_doc_version": slug,
        "libresign_app_version": app_version,
        "libresign_nextcloud": nextcloud,
        "libresign_app_sha": app_sha,
        "libresign_doc_status": status,
        "libresign_versions": catalog.get("versions", [{
            "slug": slug, "status": status, "nextcloud_min": nextcloud,
            "nextcloud_max": nextcloud,
        }]),
    })
    config["html_context"] = context
    config["templates_path"] = [str(root / "_templates")]
    config["html_static_path"] = [str(root / "assets")]
    config["html_css_files"] = ["version-switcher.css"]
    config["html_js_files"] = ["version-switcher.js"]
    config["rst_prolog"] = (
        f".. |LibreSignRelease| replace:: {app_version}\n"
        f".. |NextcloudRelease| replace:: {nextcloud}\n"
    )
