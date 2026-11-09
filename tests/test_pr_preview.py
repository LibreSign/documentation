"""Review-only release previews must be navigable without screenshot tooling."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from versioning import pr_preview
from versioning.sphinx_config import configure


class UnreleasedPreviewTests(unittest.TestCase):
    def fixture(self, root: Path, *, released: bool = False) -> tuple[Path, Path]:
        site = root / "site"
        site.mkdir()
        (site / "index.html").write_text("<h1>Docs</h1>")
        main = site / "main/developer_manual/api"
        main.mkdir(parents=True)
        (main / "openapi.json").write_text("{}")
        (main / "openapi.provenance.json").write_text('{"branch":"main"}')
        (site / "main/developer_manual/index.html").write_text("Development")
        (site / "15/index.html").parent.mkdir()
        (site / "15/index.html").write_text("Stable")
        catalog = {
            "current_stable": "15",
            "versions": [
                {"slug": "15", "status": "current"},
                {"slug": "main", "status": "development",
                 "app_version": "16.0.0-dev.1", "app_commit": "a" * 40},
            ],
        }
        if released:
            catalog["versions"].insert(0, {"slug": "16", "status": "current"})
            (site / "16/index.html").parent.mkdir()
            (site / "16/index.html").write_text("Released")
        (site / "versions.json").write_text(json.dumps(catalog))
        sources = root / "source"
        overlay = sources / "versioned/16/developer_manual/webhooks"
        overlay.mkdir(parents=True)
        (overlay / "index.rst").write_text("Webhooks")
        (overlay / "new_event.rst").write_text("New event")
        return site, sources

    @staticmethod
    def fake_sphinx(source: Path, output: Path, entry: dict,
                    catalog: dict, *, review_only: bool = False) -> None:
        assert review_only
        output.mkdir(parents=True)
        (output / "index.html").write_text("Review manual")
        target = output / "webhooks"
        target.mkdir()
        (target / "index.html").write_text(
            '<a href="new_event.html">Event</a>')
        (target / "new_event.html").write_text("Native event")
        (output / "api").mkdir()
        (output / "api/openapi.html").write_text("OpenAPI")

    def test_future_pages_are_built_and_linked_without_filename_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, sources = self.fixture(Path(tmp))
            with patch.object(pr_preview, "ROOT", sources), \
                 patch.object(pr_preview, "source_tree", return_value=Path(tmp)), \
                 patch.object(pr_preview, "run_sphinx", side_effect=self.fake_sphinx):
                routes = pr_preview.preview_unreleased(site, "https://example.test/pr-7")
            self.assertIn("/_review/16/developer_manual/webhooks/new_event.html", routes)
            self.assertEqual((site / "_review/16/developer_manual/api/openapi.json")
                             .read_text(), "{}")
            self.assertIn("new_event.html", (site / "_review/preview-comment.md").read_text())
            self.assertIn("Preview-only documentation", (site / "_review/index.html").read_text())
            self.assertFalse((site / "16/developer_manual/index.html").exists())
            self.assertNotIn('"slug": "16"', (site / "versions.json").read_text())

    def test_invalid_overlay_page_cannot_be_silently_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, sources = self.fixture(Path(tmp))
            def incomplete(source, output, entry, catalog, *, review_only=False):
                self.fake_sphinx(source, output, entry, catalog, review_only=review_only)
                (output / "webhooks/new_event.html").unlink()
            with patch.object(pr_preview, "ROOT", sources), \
                 patch.object(pr_preview, "source_tree", return_value=Path(tmp)), \
                 patch.object(pr_preview, "run_sphinx", side_effect=incomplete):
                with self.assertRaisesRegex(ValueError, "did not render"):
                    pr_preview.preview_unreleased(site, "https://example.test/pr-7")

    def test_broken_links_in_review_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, sources = self.fixture(Path(tmp))
            def broken(source, output, entry, catalog, *, review_only=False):
                self.fake_sphinx(source, output, entry, catalog, review_only=review_only)
                (output / "webhooks/index.html").write_text(
                    '<a href="absent.html">Missing</a>')
            with patch.object(pr_preview, "ROOT", sources), \
                 patch.object(pr_preview, "source_tree", return_value=Path(tmp)), \
                 patch.object(pr_preview, "run_sphinx", side_effect=broken):
                with self.assertRaisesRegex(ValueError, "Broken unreleased-preview links"):
                    pr_preview.preview_unreleased(site, "https://example.test/pr-7")

    def test_released_major_uses_normal_version_and_no_synthetic_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, sources = self.fixture(Path(tmp), released=True)
            with patch.object(pr_preview, "ROOT", sources), \
                 patch.object(pr_preview, "run_sphinx") as sphinx:
                routes = pr_preview.preview_unreleased(site, "https://example.test/pr-7")
            sphinx.assert_not_called()
            self.assertNotIn("/_review/16/developer_manual/index.html", routes)
            self.assertTrue((site / "_review/index.html").is_file())
            self.assertFalse((site / "_review/16").exists())

    def test_review_404_assets_use_review_path_not_a_fake_stable_url(self):
        with patch.dict("os.environ", {
            "LIBRESIGN_DOC_BASE_PATH": "/site-preview/docs-preview/pr-127",
            "LIBRESIGN_DOC_VERSION": "16",
            "LIBRESIGN_DOC_MANUAL": "developer_manual",
            "LIBRESIGN_DOC_REVIEW_PREFIX": "/_review",
        }):
            config = {}
            configure(config)
        self.assertEqual(
            config["notfound_urls_prefix"],
            "/site-preview/docs-preview/pr-127/_review/16/developer_manual/",
        )
        self.assertEqual(
            config["html_context"]["libresign_site_root"],
            "/site-preview/docs-preview/pr-127",
        )

    def test_reject_non_https_preview_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, _ = self.fixture(Path(tmp))
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                pr_preview.preview_unreleased(site, "http://example.test")


if __name__ == "__main__":
    unittest.main()
