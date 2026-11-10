"""Shared Sphinx overrides for every version/manual."""
from __future__ import annotations

import json
import os
import re
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
    site_root = os.environ.get("LIBRESIGN_DOC_BASE_PATH", "").rstrip("/")
    preview_pr = os.environ.get("LIBRESIGN_PREVIEW_PR", "")
    if site_root and (not re.fullmatch(r"/[A-Za-z0-9/_-]+", site_root)
                      or ".." in site_root or "//" in site_root):
        raise ValueError("Invalid documentation site base path")
    if preview_pr and not re.fullmatch(r"[1-9][0-9]*", preview_pr):
        raise ValueError("Invalid preview pull request number")

    manual = os.environ.get("LIBRESIGN_DOC_MANUAL", "main")
    review_prefix = os.environ.get("LIBRESIGN_DOC_REVIEW_PREFIX", "")
    if review_prefix not in ("", "/_review"):
        raise ValueError("Invalid review-only Sphinx path")
    config["notfound_urls_prefix"] = (
        f"{site_root}{review_prefix}/{slug}/" +
        (f"{manual}/" if manual != "main" else "")
    )
    config["release"] = app_version
    config["version"] = slug
    context = dict(config.get("html_context", {}))
    context.update({
        "libresign_site_root": site_root,
        "docs_home_href": f"{site_root}/",
        "libresign_preview_pr": preview_pr,
        "libresign_doc_manual": manual,
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
    config["html_css_files"] = ["version-switcher.css", "ecosystem-nav.css"]
    config["html_js_files"] = ["version-switcher.js", "ecosystem-nav.js"]
    config["rst_prolog"] = (
        f".. |LibreSignRelease| replace:: {app_version}\n"
        f".. |NextcloudRelease| replace:: {nextcloud}\n"
    )
