# SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
# SPDX-License-Identifier: CC-BY-3.0

"""Canonical URLs, migration routes, and sitemap checks for published docs."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

PUBLIC_ORIGIN = "https://docs.libresign.coop"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
AUXILIARY = {"404.html", "genindex.html", "search.html"}
MANUALS = {"user_manual", "admin_manual", "developer_manual"}


def canonical_url(path: Path) -> str:
    """Return the single public URL used in HTML canonical and sitemap."""
    parts = path.parts
    if not parts or path.is_absolute() or ".." in parts:
        raise ValueError(f"Invalid published path: {path}")
    if path.name == "index.html":
        parent = path.parent.as_posix()
        return PUBLIC_ORIGIN + ("/" if parent == "." else f"/{parent}/")
    return f"{PUBLIC_ORIGIN}/{path.as_posix()}"


def _published_pages(site: Path, versions: set[str]) -> tuple[list[Path], list[Path]]:
    """Separate indexable content pages from generated Sphinx utility pages."""
    content, auxiliary = [], []
    for page in sorted(site.rglob("*.html")):
        path = page.relative_to(site)
        if path == Path("index.html"):
            content.append(page)
        elif path.parts[0] in versions and not any(part.startswith("_") for part in path.parts):
            if path.name in AUXILIARY or "swagger-ui" in path.parts:
                auxiliary.append(page)
            else:
                content.append(page)
    return content, auxiliary


def _add_head_tag(page: Path, tag: str, *, guard: str) -> None:
    markup = page.read_text(encoding="utf-8")
    if re.search(guard, markup, re.IGNORECASE):
        if tag not in markup:
            raise ValueError(f"Conflicting SEO metadata in {page}")
        return
    if "</head>" not in markup:
        raise ValueError(f"Missing HTML head in {page}")
    page.write_text(markup.replace("</head>", f"  {tag}\n</head>", 1), encoding="utf-8")


def _add_canonical(page: Path, url: str) -> None:
    tag = f'<link rel="canonical" href="{escape(url, quote=True)}" />'
    _add_head_tag(page, tag, guard=r'<link\b[^>]*\brel=["\']canonical["\']')


def _add_noindex(page: Path) -> None:
    tag = '<meta name="robots" content="noindex,follow" />'
    _add_head_tag(page, tag, guard=r'<meta\b[^>]*\bname=["\']robots["\']')


def mark_preview_noindex(directory: Path) -> None:
    for page in directory.rglob("*.html"):
        _add_noindex(page)


def apply_seo(site: Path, catalog: dict, *, preview: bool = False) -> None:
    """Publish canonical URLs only after all versions and redirects are assembled."""
    versions = {entry["slug"] for entry in catalog["versions"]}
    content, auxiliary = _published_pages(site, versions)
    if preview:
        mark_preview_noindex(site)
        (site / "sitemap.xml").unlink(missing_ok=True)
        (site / "robots.txt").unlink(missing_ok=True)
        return

    urls = []
    for page in content:
        url = canonical_url(page.relative_to(site))
        _add_canonical(page, url)
        urls.append(url)
    for page in auxiliary:
        _add_noindex(page)

    ET.register_namespace("", SITEMAP_NS)
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    for url in sorted(set(urls)):
        ET.SubElement(ET.SubElement(root, f"{{{SITEMAP_NS}}}url"),
                      f"{{{SITEMAP_NS}}}loc").text = url
    ET.ElementTree(root).write(site / "sitemap.xml", encoding="utf-8",
                               xml_declaration=True)
    (site / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_ORIGIN}/sitemap.xml\n",
        encoding="utf-8",
    )


def read_legacy_routes(root: Path) -> dict[str, str]:
    """The historic unversioned routes are an immutable migration contract."""
    routes = json.loads((root / "versioned/legacy-routes.json").read_text(encoding="utf-8"))
    if not isinstance(routes, dict) or not routes:
        raise ValueError("Legacy URL mapping must be a nonempty object")
    for old, target in routes.items():
        for value in (old, target):
            if not isinstance(value, str) or not value.endswith(".html"):
                raise ValueError(f"Unsafe legacy mapping: {old} => {target}")
            path = Path(value)
            if (path.is_absolute() or ".." in path.parts or
                    "//" in value or "\\" in value or
                    any(not component for component in path.parts)):
                raise ValueError(f"Unsafe legacy mapping: {old} => {target}")
        if len(Path(old).parts) < 2 or len(Path(target).parts) < 3:
            raise ValueError(f"Invalid legacy route shape: {old} => {target}")
        if Path(old).parts[0] not in MANUALS:
            raise ValueError(f"Legacy source is not a manual: {old}")
        if Path(target).parts[0] != "main" and not re.fullmatch(r"[1-9][0-9]*", Path(target).parts[0]):
            raise ValueError(f"Legacy destination is not pinned: {target}")
        if old.split("/")[0] != target.split("/")[1]:
            raise ValueError(f"Legacy destination changes manual: {old} => {target}")
        if Path(old).name != "index.html" and Path(target).name == "index.html":
            raise ValueError(f"Legacy article redirects to generic index: {old}")
    return routes


def verify_seo(site: Path, catalog: dict, *, preview: bool = False,
               root: Path | None = None) -> list[str]:
    """Check the generated artifact, not just its source configuration."""
    versions = {entry["slug"] for entry in catalog["versions"]}
    content, auxiliary = _published_pages(site, versions)
    errors = []
    if preview:
        for page in site.rglob("*.html"):
            if 'name="robots" content="noindex,follow"' not in page.read_text(encoding="utf-8"):
                errors.append(f"Preview page can be indexed: {page.relative_to(site)}")
        if (site / "sitemap.xml").exists():
            errors.append("Preview publishes production sitemap")
        return errors

    expected = {canonical_url(page.relative_to(site)) for page in content}
    if not (site / "sitemap.xml").is_file():
        errors.append("Missing sitemap.xml")
    else:
        try:
            tree = ET.parse(site / "sitemap.xml")
            actual = [item.text for item in tree.findall(f".//{{{SITEMAP_NS}}}loc")]
            if set(actual) != expected or len(actual) != len(expected):
                errors.append("Sitemap URLs differ from indexable content pages")
        except ET.ParseError as exc:
            errors.append(f"Invalid sitemap XML: {exc}")
    if not (site / "robots.txt").is_file() or (
        f"Sitemap: {PUBLIC_ORIGIN}/sitemap.xml" not in
        (site / "robots.txt").read_text(encoding="utf-8")
    ):
        errors.append("robots.txt must disclose the canonical sitemap")
    for page in content:
        expected_tag = f'<link rel="canonical" href="{canonical_url(page.relative_to(site))}" />'
        markup = page.read_text(encoding="utf-8")
        if markup.count(expected_tag) != 1:
            errors.append(f"Missing or duplicated canonical: {page.relative_to(site)}")
        if 'name="robots" content="noindex' in markup:
            errors.append(f"Production content has noindex: {page.relative_to(site)}")
    for page in auxiliary:
        if 'name="robots" content="noindex,follow"' not in page.read_text(encoding="utf-8"):
            errors.append(f"Utility page is indexable: {page.relative_to(site)}")
    if root is not None:
        for source, destination in read_legacy_routes(root).items():
            old_page, new_page = site / source, site / destination
            if not old_page.is_file() or not new_page.is_file():
                errors.append(f"Missing legacy mapping destination: {source} => {destination}")
                continue
            markup = old_page.read_text(encoding="utf-8")
            if f"url=/{destination}" not in markup or 'http-equiv=\'refresh\'' not in markup:
                errors.append(f"Incorrect legacy redirect: {source} => {destination}")
    return errors
