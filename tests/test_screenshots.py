"""Screenshot discovery regression tests: no release number may be hardcoded."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from versioning.screenshots import (
    LIGHT_PAGE, LIGHT_ROUTE, Screenshot, screenshot_plan, take_screenshots,
)


class ScreenshotDiscoveryTests(unittest.TestCase):
    def make_site(self, root: Path, slugs: list[str], current: str) -> Path:
        site = root / "site"
        site.mkdir()
        (site / "index.html").write_text("<h1>Version index</h1>")
        (site / "versions.json").write_text(json.dumps({
            "schema": 1, "versions": [{"slug": slug} for slug in slugs],
            "current_stable": current,
        }))
        for slug in slugs:
            target = site / slug
            target.mkdir()
            (target / "index.html").write_text(f"<h1>{slug}</h1>")
            (target / "developer_manual/api").mkdir(parents=True)
            (target / "developer_manual/api/openapi.html").write_text("OpenAPI")
            (target / "developer_manual/api/external-email-signers.html").write_text("Guest")
        return site

    def test_future_major_is_discovered_from_catalog_without_code_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(
                Path(temp), ["main", "13", "16", "14", "15"], current="16"
            )
            plan = screenshot_plan(site)
            self.assertEqual(
                [s.filename for s in plan], [
                    "libresign-versions-home-dark.png",
                    "libresign-versions-home-light.png",
                    "libresign-16.png", "libresign-15.png", "libresign-14.png",
                    "libresign-13.png", "libresign-main.png", "openapi-16.png",
                    "external-email-signers-16.png", "external-email-signers-15.png",
                    "external-email-signers-14.png", "external-email-signers-13.png",
                    "external-email-signers-main.png",
                ],
            )
            self.assertEqual(plan[1].route, LIGHT_ROUTE)
            self.assertEqual(plan[-1].route, "/main/developer_manual/api/external-email-signers.html")

    def test_new_version_does_not_require_a_workflow_edit(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["15", "main"], current="15")
            before = {item.filename for item in screenshot_plan(site)}
            extra = site / "17"
            (extra / "developer_manual/api").mkdir(parents=True)
            (extra / "index.html").write_text("version 17")
            (extra / "developer_manual/api/openapi.html").write_text("schema")
            (extra / "developer_manual/api/external-email-signers.html").write_text("Guest")
            catalog = json.loads((site / "versions.json").read_text())
            catalog["versions"].insert(0, {"slug": "17"})
            catalog["current_stable"] = "17"
            (site / "versions.json").write_text(json.dumps(catalog))
            after = {item.filename for item in screenshot_plan(site)}
            self.assertIn("libresign-17.png", after - before)
            self.assertIn("openapi-17.png", after)
            self.assertNotIn("openapi-15.png", after)

    def test_missing_documented_version_fails_instead_of_silent_skip(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["15", "14", "main"], "15")
            (site / "14/index.html").unlink()
            with self.assertRaisesRegex(ValueError, "14.*index.html"):
                screenshot_plan(site)

    def test_missing_active_openapi_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["15", "main"], "15")
            (site / "15/developer_manual/api/openapi.html").unlink()
            with self.assertRaisesRegex(ValueError, "OpenAPI"):
                screenshot_plan(site)

    def test_invalid_slugs_rejected_before_building_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["15", "main"], "15")
            catalog = json.loads((site / "versions.json").read_text())
            catalog["versions"].append({"slug": "../main"})
            (site / "versions.json").write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError, "Invalid documentation version"):
                screenshot_plan(site)

    def test_duplicate_entries_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["15", "main"], "15")
            catalog = json.loads((site / "versions.json").read_text())
            catalog["versions"].append({"slug": "15"})
            (site / "versions.json").write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                screenshot_plan(site)

    def test_no_stable_version_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["main"], current="15")
            with self.assertRaisesRegex(ValueError, "Current stable"):
                screenshot_plan(site)

    def test_light_theme_capture_is_ephemeral(self):
        # The generated candidate remains untouched; the transient HTML sets
        # localStorage.theme just as the manual's dark-mode extension does.
        self.assertIn(b'localStorage.setItem("theme","light")', LIGHT_PAGE)
        with tempfile.TemporaryDirectory() as temp:
            site = self.make_site(Path(temp), ["15", "main"], "15")
            with patch("versioning.screenshots.subprocess.run") as run:
                # Missing screenshots must not make the CI step silently pass.
                with self.assertRaisesRegex(RuntimeError, "Missing or empty screenshot"):
                    take_screenshots(site, Path(temp) / "screenshots", browser="/bin/true")
                run.assert_called_once()
            self.assertFalse((site / LIGHT_ROUTE.lstrip("/")).exists())


if __name__ == "__main__":
    unittest.main()
