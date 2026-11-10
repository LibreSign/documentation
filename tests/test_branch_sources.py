"""Test branch isolation at the source-loader boundary, not per-page lists."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from versioning import build
from versioning.sources import branch_sources


class BranchSourceTests(unittest.TestCase):
    def test_release_uses_its_branch_without_inheriting_development_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            latest = root / "dev"
            stable = root / "stable"
            for directory, label in ((latest, "Development"), (stable, "Stable")):
                manual = directory / "developer_manual"
                manual.mkdir(parents=True)
                (manual / "index.rst").write_text(label)
            (latest / "developer_manual/new-feature.rst").write_text("New feature")
            with patch.object(build, "ROOT", latest), patch.object(
                build, "branch_sources",
                side_effect=lambda stage, slug, repository: latest if slug == "main" else stable,
            ):
                stage = root / "stage"
                first = build.source_tree(stage, "main", "developer_manual")
                second = build.source_tree(stage, "15", "developer_manual")
            self.assertTrue((first / "new-feature.rst").is_file())
            self.assertFalse((second / "new-feature.rst").exists())
            self.assertEqual((second / "index.rst").read_text(), "Stable")
            self.assertIn("'github_version': 'stable15'", (second / "conf.py").read_text())
            self.assertIn("'conf_py_path': '/developer_manual/'", (second / "conf.py").read_text())

    def test_missing_documentation_branch_does_not_fall_back_to_main(self):
        with tempfile.TemporaryDirectory() as temp, patch(
            "versioning.sources.subprocess.run", side_effect=FileNotFoundError("offline")
        ):
            # Errors must say which stable branch is required, not copy main.
            with self.assertRaisesRegex(ValueError, "stable15"):
                branch_sources(Path(temp), "15", repository=Path(temp))


if __name__ == "__main__":
    unittest.main()
