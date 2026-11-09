"""Shared documentation sections are copied without per-page build code."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from versioning import build


class SharedSourceTests(unittest.TestCase):
    def fixture(self, root: Path) -> None:
        (root / "developer_manual/integration").mkdir(parents=True)
        (root / "developer_manual/integration/index.rst").write_text("Architecture")
        (root / "developer_manual/integration/new-guide.rst").write_text("New guide")
        (root / "developer_manual/integration/_native-webhooks.inc").write_text(
            "Development completion event"
        )
        (root / "developer_manual/api").mkdir()
        (root / "developer_manual/api/openapi.rst").write_text("OpenAPI")
        (root / "developer_manual/html").mkdir()
        (root / "developer_manual/index.rst").write_text("Development manual")
        base = root / "versioned/base/developer_manual"
        (base / "integration").mkdir(parents=True)
        (base / "index.rst").write_text("Stable manual")
        (base / "integration/_native-webhooks.inc").write_text("Only polling")
        overlay = root / "versioned/16/developer_manual/integration"
        overlay.mkdir(parents=True)
        (overlay / "_native-webhooks.inc").write_text("Native event")
        (root / "versioned/shared.json").write_text(
            json.dumps({"developer_manual": ["integration"]})
        )

    def test_new_rst_is_shared_without_editing_python(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            with patch.object(build, "ROOT", root):
                stage = root / "build"
                stable = build.source_tree(stage, "15", "developer_manual")
                upcoming = build.source_tree(stage, "16", "developer_manual")
                dev = build.source_tree(stage, "main", "developer_manual")
            for source in (stable, upcoming, dev):
                self.assertTrue((source / "integration/new-guide.rst").is_file())
            self.assertEqual(
                (stable / "integration/_native-webhooks.inc").read_text(), "Only polling")
            self.assertEqual(
                (upcoming / "integration/_native-webhooks.inc").read_text(), "Native event")
            self.assertEqual((dev / "integration/_native-webhooks.inc").read_text(),
                             "Development completion event")
            self.assertFalse((stable / "integration/source-only.rst").exists())

    def test_unlisted_development_section_is_not_leaked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            (root / "developer_manual/experimental").mkdir()
            (root / "developer_manual/experimental/new.rst").write_text("Unreleased")
            with patch.object(build, "ROOT", root):
                stable = build.source_tree(root / "stage", "15", "developer_manual")
            self.assertFalse((stable / "experimental/new.rst").exists())

    def test_traversal_and_missing_sources_fail(self):
        for section in (".", "./", "../secrets", "/etc", "missing"):
            with self.subTest(section=section), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                (root / "versioned/shared.json").write_text(
                    json.dumps({"developer_manual": [section]})
                )
                with patch.object(build, "ROOT", root):
                    with self.assertRaises(ValueError):
                        build.source_tree(root / "stage", "15", "developer_manual")


if __name__ == "__main__":
    unittest.main()
