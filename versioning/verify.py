"""Verify generated Sphinx pages and pinned OpenAPI contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from versioning.catalog import fetch_source, operations, validate_contract
from versioning.seo import verify_seo

REQUIRED_MANUALS = ("user_manual", "admin_manual", "developer_manual")


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs)
        if tag in ("a", "link", "script", "img"):
            key = "href" if tag in ("a", "link") else "src"
            if attrs.get(key):
                self.links.append(attrs[key])


def inspect_links(output: Path, page: Path) -> list[str]:
    errors = []
    parser = PageLinks()
    parser.feed(page.read_text(encoding="utf-8"))
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path or href.startswith("#"):
            continue
        path = unquote(url.path)
        site_root = os.environ.get("LIBRESIGN_DOC_BASE_PATH", "").rstrip("/")
        if site_root and path.startswith(site_root + "/"):
            path = path[len(site_root):]
        if path.startswith("/"):
            candidate = output / path.lstrip("/")
        else:
            candidate = page.parent / path
        if path.endswith("/"):
            candidate /= "index.html"
        elif candidate.is_dir():
            candidate /= "index.html"
        if not candidate.exists():
            errors.append(f"{page.relative_to(output)}: broken link {href}")
    return errors


def verify_site(output: Path, versions: list[str] | None = None,
                check_links: bool = True, fetch=fetch_source) -> dict:
    catalog = json.loads((output / "versions.json").read_text())
    all_versions = {entry["slug"]: entry for entry in catalog["versions"]}
    versions = list(all_versions) if versions is None else versions
    errors = []
    main_ops = None
    if (output / "main/developer_manual/api/openapi.json").is_file():
        main = json.loads((output / "main/developer_manual/api/openapi.json").read_text())
        main_ops = operations(main)
    for slug in versions:
        if slug not in all_versions:
            errors.append(f"Version {slug} is absent from the deployed catalog")
            continue
        entry = all_versions[slug]
        version_dir = output / slug
        for manual in ("", *REQUIRED_MANUALS):
            root = version_dir / manual
            index = root / "index.html"
            if not index.is_file():
                errors.append(f"Missing versioned index {index}")
                continue
            content = index.read_text(encoding="utf-8")
            if ('id="libresign-version-toggle"' not in content or
                    'class="rst-versions libresign-rst-versions"' not in content or
                    'id="libresign-version-menu"' not in content):
                errors.append(f"Missing version selector in {index}")
            if slug == "main" and "Development documentation" not in content:
                errors.append("Development version is not labelled as such")
        api = version_dir / "developer_manual/api"
        contract_file = api / "openapi.json"
        provenance_file = api / "openapi.provenance.json"
        if not contract_file.is_file() or not provenance_file.is_file():
            errors.append(f"Missing pinned OpenAPI/provenance for {slug}")
            continue
        contract_raw = contract_file.read_bytes()
        contract = json.loads(contract_raw)
        validate_contract(contract)
        try:
            from openapi_spec_validator import validate_spec
            validate_spec(contract)
        except ImportError:
            raise RuntimeError("openapi-spec-validator must be installed")
        except Exception as exc:
            errors.append(f"Invalid OpenAPI schema for {slug}: {exc}")
        provenance = json.loads(provenance_file.read_text())
        actual = hashlib.sha256(contract_raw).hexdigest()
        if (actual != provenance["openapi_sha256"] or
                actual != entry["openapi_sha256"]):
            errors.append(f"OpenAPI source hash mismatch for {slug}")
        for field in ("branch", "app_commit", "app_version",
                      "nextcloud_min", "nextcloud_max"):
            if entry[field] != provenance[field]:
                errors.append(f"OpenAPI provenance field differs: {slug}.{field}")
        if slug != "main" and (provenance["branch"] == "main" or
                                 not provenance["branch"].startswith("stable")):
            errors.append(f"Stable {slug} is displaying a development branch")
        openapi_page = (api / "openapi.html").read_text()
        if "raw.githubusercontent.com/LibreSign/libresign/refs/heads/main/openapi.json" in openapi_page:
            errors.append(f"OpenAPI page {slug} still loads main remotely")
        if 'url: "openapi.json"' not in openapi_page:
            errors.append(f"OpenAPI page {slug} does not load a local contract")
        pinned_bytes = fetch(entry["app_commit"], "openapi.json")
        pinned_ops = operations(json.loads(pinned_bytes))
        if hashlib.sha256(pinned_bytes).hexdigest() != actual:
            errors.append(f"Published OpenAPI does not match pinned source for {slug}")
        if slug != "main" and main_ops is not None:
            main_only = main_ops - pinned_ops
            leaked = main_only & operations(contract)
            if leaked:
                errors.append(f"Development-only operations leaked to {slug}: {sorted(leaked)}")
        if not (version_dir / "developer_manual/swagger-ui/swagger-ui-bundle.js").is_file():
            errors.append(f"Swagger UI assets missing for {slug}")
    homepage = output / "index.html"
    if homepage.is_file():
        home = homepage.read_text(encoding="utf-8")
        if ('id="main-content"' not in home or
                'Documentation by release' not in home):
            errors.append("Public homepage does not explain version selection")
        if ('src="home-theme.js"' not in home or
                'id="themeSwitcher"' not in home or
                not (output / "home-theme.js").is_file()):
            errors.append("Public homepage has no functioning shared theme switcher")
        expected_slugs = sorted(
            all_versions,
            key=lambda slug: (slug == "main", -(int(slug) if slug != "main" else 0)),
        )
        positions = [home.find(f'data-version="{slug}"') for slug in expected_slugs]
        if -1 in positions or positions != sorted(positions):
            errors.append("Homepage versions are not ordered newest stable first")
        if check_links:
            errors.extend(inspect_links(output, homepage))
    if check_links:
        for slug in versions:
            for page in (output / slug).rglob("*.html"):
                errors.extend(inspect_links(output, page))
    if (output / ".nojekyll").exists():
        errors.extend(verify_seo(output, catalog,
                                 preview=bool(os.environ.get("LIBRESIGN_PREVIEW_PR"))))
    if errors:
        raise ValueError("\n".join(errors[:60]))
    return {
        "verified_versions": versions,
        "contracts": {slug: all_versions[slug]["openapi_sha256"] for slug in versions},
        "html_files": sum(1 for slug in versions for _ in (output / slug).rglob("*.html")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", default="all")
    parser.add_argument("--no-links", action="store_true")
    args = parser.parse_args()
    versions = None if args.version == "all" else [args.version]
    print(json.dumps(verify_site(args.output, versions, not args.no_links), indent=2))


if __name__ == "__main__":
    main()
