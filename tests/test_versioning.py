"""Regression tests for safe multiversion publishing and OpenAPI provenance."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from versioning.catalog import discover, manifest_info, operations, sha256
from versioning.build import redirect_html, version_overview
from versioning.publish import assemble
from versioning.verify import inspect_links, verify_site


def sample_spec(path: str) -> bytes:
    return json.dumps({
        "openapi": "3.0.3", "info": {"title": "LibreSign", "version": "1.0.0"},
        "paths": {path: {"get": {"responses": {"200": {"description": "ok"}}}}},
    }).encode()


def info(version: str, nc: int) -> bytes:
    return (f'<info><version>{version}</version><dependencies>'
            f'<nextcloud min-version="{nc}" max-version="{nc}"/>'
            '</dependencies></info>').encode()


class CatalogTests(unittest.TestCase):
    def test_future_line_comes_from_manifest(self):
        refs = {
            "main": "a" * 40,
            "stable33": "b" * 40, "stable34": "c" * 40,
            "stable35": "d" * 40, "stable36": "e" * 40,
        }
        data = {
            ("a" * 40, "appinfo/info.xml"): info("16.0.0-dev.2", 36),
            ("b" * 40, "appinfo/info.xml"): info("13.4.9", 33),
            ("c" * 40, "appinfo/info.xml"): info("14.2.9", 34),
            ("d" * 40, "appinfo/info.xml"): info("15.0.12", 35),
            ("e" * 40, "appinfo/info.xml"): info("16.0.0", 36),
        }
        for commit in refs.values():
            data[commit, "openapi.json"] = sample_spec("/" + commit[0])
        result, contracts = discover({"minimum_nextcloud": 33},
                                     refs, lambda sha, path: data[sha, path])
        self.assertEqual(result["current_stable"], "16")
        self.assertEqual([v["slug"] for v in result["versions"]],
                         ["16", "15", "14", "13", "main"])
        self.assertEqual(contracts["13"], sample_spec("/b"))
        self.assertEqual(result["versions"][-1]["status"], "development")

    def test_eol_comes_only_from_explicit_policy(self):
        refs = {"main": "a" * 40, "stable35": "b" * 40, "stable36": "c" * 40}
        data = {
            ("a" * 40, "appinfo/info.xml"): info("17.0.0-dev.1", 37),
            ("b" * 40, "appinfo/info.xml"): info("15.0.12", 35),
            ("c" * 40, "appinfo/info.xml"): info("16.0.0", 36),
        }
        for commit in refs.values():
            data[commit, "openapi.json"] = sample_spec("/only")
        policy = {"minimum_nextcloud": 33, "lifecycle": {
            "15": {"status": "eol", "eol_date": "2026-12-01"}}}
        result, _ = discover(policy, refs, lambda sha, path: data[sha, path])
        status = {v["slug"]: v["status"] for v in result["versions"]}
        self.assertEqual(status["15"], "eol")
        self.assertEqual(status["16"], "current")

    def test_manifest_and_branch_must_agree(self):
        refs = {"main": "a" * 40, "stable35": "b" * 40}
        def retrieve(sha, path):
            if path == "openapi.json":
                return sample_spec("/okay")
            return info("15.0.1", 34) if sha == "b"*40 else info("16.0.0-dev.1", 36)
        with self.assertRaisesRegex(ValueError, "does not match"):
            discover({"minimum_nextcloud": 33}, refs, retrieve)


class PublicationTests(unittest.TestCase):
    def test_updating_15_preserves_existing_13_14_and_main(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            published, incoming, result = (
                folder / "published", folder / "incoming", folder / "result")
            for path in (published, incoming):
                path.mkdir()
            entries = [{"slug": str(v), "status": "current" if v == 15 else "previous",
                        "app_commit": "a" * 40} for v in (15,14,13)]
            entries.append({"slug": "main", "status": "development",
                            "app_commit": "m" * 40})
            catalog = {"schema": 1, "current_stable": "15", "versions": entries}
            (published / "versions.json").write_text(json.dumps(catalog))
            for slug in ("13", "14", "15", "main"):
                (published / slug).mkdir()
                (published / slug / "index.html").write_text(slug + "-original")
            (published / "13" / "saved.html").write_text("do-not-erase")
            updated = json.loads(json.dumps(catalog))
            updated["versions"][0]["app_commit"] = "b" * 40
            (incoming / "versions.json").write_text(json.dumps(updated))
            (incoming / "15").mkdir()
            (incoming / "15/index.html").write_text("15-updated")
            result_catalog = assemble(incoming, result, "15", published)
            self.assertEqual((result / "13/saved.html").read_text(), "do-not-erase")
            self.assertEqual((result / "14/index.html").read_text(), "14-original")
            self.assertEqual((result / "main/index.html").read_text(), "main-original")
            self.assertEqual((result / "15/index.html").read_text(), "15-updated")
            self.assertEqual(result_catalog["versions"][1]["app_commit"], "a"*40)
            self.assertEqual(result_catalog["versions"][0]["app_commit"], "b"*40)

    def test_partial_without_existing_pages_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            built = folder / "built"
            built.mkdir()
            (built / "versions.json").write_text(json.dumps({"versions": [
                {"slug": "15"}]}))
            with self.assertRaisesRegex(ValueError, "requires existing"):
                assemble(built, folder / "deploy", "15")

    def test_redirect_keeps_parameters_and_fragment(self):
        markup = redirect_html("/15/developer_manual/api/openapi.html")
        self.assertIn("location.search", markup)
        self.assertIn("location.hash", markup)
        self.assertNotIn("/main/", markup)

    def test_preview_redirects_stay_under_isolated_origin(self):
        with patch.dict("os.environ", {
            "LIBRESIGN_DOC_BASE_PATH": "/site-preview/docs-preview/pr-126"
        }):
            markup = redirect_html("/15/user_manual/")
            self.assertIn(
                "/site-preview/docs-preview/pr-126/15/user_manual/", markup)
            self.assertNotIn("url=/15/user_manual/", markup)

    def test_preview_absolute_links_map_into_candidate_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "15").mkdir()
            page = root / "15/index.html"
            page.write_text(
                '<a href="/site-preview/docs-preview/pr-126/15/help.html">Help</a>'
            )
            (root / "15/help.html").touch()
            with patch.dict("os.environ", {
                "LIBRESIGN_DOC_BASE_PATH": "/site-preview/docs-preview/pr-126"
            }):
                self.assertEqual(inspect_links(root, page), [])
                (root / "15/help.html").unlink()
                self.assertEqual(len(inspect_links(root, page)), 1)

    def test_homepage_lists_latest_stable_first_and_main_last(self):
        catalog = {
            "current_stable": "15",
            "versions": [
                {"slug": "main", "status": "development", "nextcloud_min": 36,
                 "nextcloud_max": 36},
                {"slug": "13", "status": "previous", "nextcloud_min": 33,
                 "nextcloud_max": 33},
                {"slug": "15", "status": "current", "nextcloud_min": 35,
                 "nextcloud_max": 35},
                {"slug": "14", "status": "previous", "nextcloud_min": 34,
                 "nextcloud_max": 34},
            ],
        }
        page = version_overview(catalog)
        positions = [page.index(f'data-version="{v}"')
                     for v in ("15", "14", "13", "main")]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('href="15/developer_manual/"', page)
        self.assertIn('Latest stable', page)
        self.assertIn('Development (not a stable release)', page)
        self.assertNotIn('http-equiv="refresh"', page)

    def test_homepage_loads_theme_before_css_and_exposes_accessible_toggle(self):
        catalog = {"current_stable": "15", "versions": [
            {"slug": "15", "status": "current", "nextcloud_min": 35,
             "nextcloud_max": 35}]}
        page = version_overview(catalog)
        self.assertIn('id="themeSwitcher"', page)
        self.assertIn('aria-label="Dark mode"', page)
        self.assertIn('aria-pressed="false" hidden', page)
        self.assertLess(page.index('src="home-theme.js"'),
                        page.index('href="home.css"'))

    def test_homepage_preview_uses_relative_links(self):
        catalog = {"current_stable": "15", "versions": [
            {"slug": "15", "status": "current", "nextcloud_min": 35,
             "nextcloud_max": 35}]}
        with patch.dict("os.environ", {"LIBRESIGN_PREVIEW_PR": "126",
                                    "LIBRESIGN_DOC_BASE_PATH": "/site-preview/docs-preview/pr-126"}):
            page = version_overview(catalog)
        self.assertIn("Pull request preview", page)
        self.assertIn('href="15/admin_manual/"', page)
        self.assertNotIn('href="/15/admin_manual/"', page)
        self.assertIn('href="_review/"', page)
        with patch.dict("os.environ", {"LIBRESIGN_PREVIEW_PR": ""}):
            public_page = version_overview(catalog)
        self.assertNotIn('href="_review/"', public_page)

    def test_local_link_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "15").mkdir()
            page = root / "15/index.html"
            page.write_text('<a href="missing.html">Broken</a>')
            self.assertEqual(len(inspect_links(root, page)), 1)
            (root / "15/missing.html").touch()
            self.assertEqual(inspect_links(root, page), [])


if __name__ == "__main__":
    unittest.main()
