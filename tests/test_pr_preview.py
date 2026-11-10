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
            self.assertIn("/main/developer_manual/",
                          (site / "_review/preview-comment.md").read_text())

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
