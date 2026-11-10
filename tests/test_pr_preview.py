"""Preview links must point to the real development source, not a fake release."""

import json
import tempfile
import unittest
from pathlib import Path

from versioning.pr_preview import preview_unreleased


class DevelopmentPreviewTests(unittest.TestCase):
    @staticmethod
    def fixture(root: Path) -> Path:
        site = root / "site"
        for path in ("index.html", "15/index.html", "main/developer_manual/index.html"):
            target = site / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("<html><body>Documentation</body></html>")
        (site / "versions.json").write_text(json.dumps({
            "current_stable": "15",
            "versions": [
                {"slug": "15", "status": "current"},
                {"slug": "main", "status": "development",
                 "app_version": "16.0.0-dev.1"},
            ],
        }))
        return site

    def test_development_preview_uses_single_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.fixture(Path(tmp))
            routes = preview_unreleased(site, "https://example.test/pr-130")
            self.assertIn("/main/developer_manual/", routes)
            self.assertIn("LibreSign 16", (site / "_review/index.html").read_text())
            self.assertFalse((site / "_review/16").exists())
            comment = (site / "_review/preview-comment.md").read_text()
            self.assertIn("/main/developer_manual/", comment)
            self.assertIn("QR code for preview link", comment)
            self.assertIn("https://qr.rossjrw.com/?color.dark=0d1117&url=", comment)
            self.assertIn("Built to branch [`gh-pages`]", comment)
            self.assertIn("GitHub Pages deployment", comment)
            self.assertIn("libresign-documentation-preview-links", comment)
            self.assertIn("[Review notes]", comment)

    def test_preview_uses_action_version_and_build_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.fixture(Path(tmp))
            preview_unreleased(site, "https://example.test/pr-130",
                               action_version="v1.8.1-4-g2a6da11",
                               built_at="2026-11-10 20:23 UTC")
            comment = (site / "_review/preview-comment.md").read_text()
            self.assertIn("[PR Preview Action](https://github.com/LibreSign/pr-preview-action) v1.8.1-4-g2a6da11", comment)
            self.assertIn("at 2026-11-10 20:23 UTC", comment)
            self.assertEqual(comment.count("libresign-documentation-preview-links"), 1)

    def test_unsafe_preview_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.fixture(Path(tmp))
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                preview_unreleased(site, 'https://example.test/"><script>')

    def test_missing_preview_source_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.fixture(Path(tmp))
            (site / "main/developer_manual/index.html").unlink()
            with self.assertRaisesRegex(ValueError, "Missing source"):
                preview_unreleased(site, "https://example.test/pr-130")

    def test_preview_requires_https(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.fixture(Path(tmp))
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                preview_unreleased(site, "http://example.test")


if __name__ == "__main__":
    unittest.main()
