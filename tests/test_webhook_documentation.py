"""The native webhook documentation must not leak into unverified stables.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
import json
import tempfile
import unittest
from pathlib import Path

from versioning.build import source_tree
from versioning.screenshots import development_webhook_screenshots, screenshot_plan


class WebhookDocumentationTests(unittest.TestCase):
    def test_only_development_line_contains_webhooks(self):
        with tempfile.TemporaryDirectory() as temp:
            development = source_tree(Path(temp), "main", "developer_manual")
            self.assertIn("webhooks/index", (development / "index.rst").read_text())
            self.assertTrue((development / "webhooks/index.rst").is_file())
            self.assertTrue((development / "webhooks/configuration.rst").is_file())
            self.assertTrue((development / "webhooks/signing_completion.rst").is_file())
            for version in ("13", "14", "15"):
                with self.subTest(version=version):
                    stable = source_tree(Path(temp), version, "developer_manual")
                    self.assertFalse((stable / "webhooks").exists())
                    self.assertNotIn("webhooks/index", (stable / "index.rst").read_text())

    def test_preview_screenshots_cover_all_main_webhook_pages(self):
        with tempfile.TemporaryDirectory() as temp:
            site = Path(temp)
            main = site / "main/developer_manual/webhooks"
            main.mkdir(parents=True)
            for page in ("index", "configuration", "signing_completion"):
                (main / f"{page}.html").write_text(page)
            snapshots = development_webhook_screenshots(site, ["15", "main"])
            self.assertEqual([s.filename for s in snapshots], [
                "webhooks-index-main.png",
                "webhooks-configuration-main.png",
                "webhooks-signing_completion-main.png",
            ])
            self.assertEqual(development_webhook_screenshots(site, ["15"]), [])
            (main / "configuration.html").unlink()
            with self.assertRaisesRegex(ValueError, "Missing webhook documentation page"):
                development_webhook_screenshots(site, ["15", "main"])


if __name__ == "__main__":
    unittest.main()
