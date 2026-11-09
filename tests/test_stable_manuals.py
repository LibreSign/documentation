"""Protect task-oriented documentation for every published stable release.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_PAGES = {
    "user_manual": ("start", "functionality", "faq", "support"),
    "admin_manual": ("installation", "configuration", "maintenance", "security"),
}


class StableManualCoverageTests(unittest.TestCase):
    def test_stable_manuals_have_real_tasks_in_toctree(self):
        for manual, pages in REQUIRED_PAGES.items():
            with self.subTest(manual=manual):
                source = ROOT / "versioned/base" / manual
                index = (source / "index.rst").read_text(encoding="utf-8")
                self.assertIn(".. toctree::", index)
                self.assertNotIn("being expanded", index)
                self.assertNotIn("intentionally omits unverified", index)
                for name in pages:
                    with self.subTest(manual=manual, page=name):
                        self.assertIn(f"   {name}\n", index)
                        content = (source / f"{name}.rst").read_text(encoding="utf-8")
                        self.assertGreater(len(content), 350)
                        self.assertIn("\n", content)

    def test_old_user_and_admin_articles_land_on_stable_topics(self):
        routes = json.loads((ROOT / "versioned/legacy-routes.json").read_text())
        for manual, pages in REQUIRED_PAGES.items():
            for page in pages:
                previous = "suport" if page == "support" else page
                old = f"{manual}/{previous}.html"
                with self.subTest(route=old):
                    self.assertEqual(routes[old], f"15/{manual}/{page}.html")
                    self.assertTrue((ROOT / "versioned/base" / manual / f"{page}.rst").is_file())

    def test_legacy_user_anchors_remain_available(self):
        content = (ROOT / "versioned/base/user_manual/functionality.rst").read_text()
        for anchor in ("main_screen", "add_signature", "see_signed_file"):
            with self.subTest(anchor=anchor):
                self.assertIn(f".. _{anchor}:", content)

    def test_faq_avoids_unqualified_legal_guarantees(self):
        content = (ROOT / "versioned/base/user_manual/faq.rst").read_text().lower()
        self.assertNotIn("meets all the requirements", content)
        self.assertIn("jurisdiction", content)
        self.assertIn("validation", content)


if __name__ == "__main__":
    unittest.main()
