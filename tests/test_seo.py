# SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
# SPDX-License-Identifier: CC-BY-3.0

"""Regression coverage for permanent URLs and indexable documentation."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from versioning.build import legacy_redirects
from versioning.seo import (
    PUBLIC_ORIGIN, apply_seo, canonical_url, mark_preview_noindex,
    read_legacy_routes, verify_seo,
)


class DocumentationSeoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.site = self.root / "site"
        self.site.mkdir()
        self.catalog = {"versions": [{"slug": "15"}, {"slug": "main"}],
                        "current_stable": "15"}

    def page(self, name: str, body: str = "<h1>Article</h1>"):
        path = self.site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"<!doctype html><html><head><title>Documentation</title></head>"
                        f"<body>{body}</body></html>", encoding="utf-8")
        return path

    def test_historic_routes_cover_all_existing_manual_pages(self):
        root = Path(__file__).resolve().parent.parent
        routes = read_legacy_routes(root)
        source = {f"{manual}/{p.relative_to(root / manual).with_suffix('.html')}"
                  for manual in ("user_manual", "admin_manual", "developer_manual")
                  for p in (root / manual).rglob("*.rst")}
        self.assertEqual(set(routes), source)
        self.assertEqual(len(routes), 46)
        self.assertEqual(routes["user_manual/functionality.html"],
                         "main/user_manual/functionality.html")
        self.assertEqual(routes["admin_manual/installation.html"],
                         "main/admin_manual/installation.html")
        self.assertEqual(routes["developer_manual/architecture.html"],
                         "main/developer_manual/architecture.html")

    def test_legacy_redirects_keep_individual_targets_across_new_stable(self):
        self.page("15/index.html")
        for name in ("15/user_manual/index.html",
                     "main/user_manual/functionality.html"):
            self.page(name)
        (self.site / "versions.json").write_text(
            json.dumps(self.catalog), encoding="utf-8")
        self.page("index.html", '<div id="main-content"></div>')
        with patch("versioning.build.version_overview", return_value=self.page("index.html").read_text()):
            legacy_redirects(self.site, "15", routes={
                "user_manual/index.html": "15/user_manual/index.html",
                "user_manual/functionality.html": "main/user_manual/functionality.html",
            })
        redirect = (self.site / "user_manual/functionality.html").read_text()
        self.assertIn("url=/main/user_manual/functionality.html", redirect)
        self.assertNotIn("url=/15/user_manual/index.html", redirect)

    def test_missing_redirect_destination_fails_before_deploy(self):
        self.page("15/index.html")
        (self.site / "versions.json").write_text(json.dumps(self.catalog))
        with self.assertRaisesRegex(ValueError, "Missing historical destination"):
            legacy_redirects(self.site, "15", routes={
                "user_manual/functionality.html": "main/user_manual/missing.html"
            })

    def test_published_sitemap_and_canonical_are_exact(self):
        self.page("index.html")
        self.page("15/index.html")
        self.page("15/user_manual/index.html")
        self.page("15/user_manual/guide.html")
        self.page("main/index.html")
        self.page("15/user_manual/search.html")
        self.page("15/user_manual/404.html")
        apply_seo(self.site, self.catalog)
        self.assertEqual(verify_seo(self.site, self.catalog), [])
        self.assertIn(f"{PUBLIC_ORIGIN}/15/user_manual/guide.html",
                      (self.site / "sitemap.xml").read_text())
        self.assertNotIn("search.html", (self.site / "sitemap.xml").read_text())
        self.assertIn('content="noindex,follow"',
                      (self.site / "15/user_manual/search.html").read_text())

    def test_preview_content_is_not_indexable(self):
        self.page("index.html")
        self.page("15/user_manual/guide.html")
        self.page("_review/16/developer_manual/index.html")
        apply_seo(self.site, self.catalog, preview=True)
        mark_preview_noindex(self.site / "_review")
        self.assertEqual(verify_seo(self.site, self.catalog, preview=True), [])
        self.assertFalse((self.site / "sitemap.xml").exists())

    def test_unsafe_and_generic_legacy_destinations_are_rejected(self):
        source = self.root / "src"
        (source / "versioned").mkdir(parents=True)
        for bad in ("15/user_manual/index.html", "../../private.html"):
            (source / "versioned/legacy-routes.json").write_text(json.dumps({
                "user_manual/functionality.html": bad
            }))
            with self.assertRaises(ValueError):
                read_legacy_routes(source)

    def test_canonical_has_stable_directory_semantics(self):
        self.assertEqual(canonical_url(Path("15/user_manual/index.html")),
                         f"{PUBLIC_ORIGIN}/15/user_manual/")
        self.assertEqual(canonical_url(Path("15/user_manual/guide.html")),
                         f"{PUBLIC_ORIGIN}/15/user_manual/guide.html")


if __name__ == "__main__":
    unittest.main()
