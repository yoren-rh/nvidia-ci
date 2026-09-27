"""NNO release-line policy tests."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from nno_versions.update_versions import main, update_snapshot


class TestUpdateSnapshot(unittest.TestCase):
    def test_tracks_only_configured_lines_and_newest_patches(self):
        settings = {
            "minimum_operator_line": "26.7",
            "operator_line_count": 1,
            "tracked_ocp_lines": ["4.21", "4.22"],
        }
        current = {
            "network-operator": {"26.4": "26.4.2", "26.7": "26.7.0"},
            "ocp": {"4.20": "4.20.40", "4.21": "4.21.34"},
        }
        discovered_operator = {"26.4": "26.4.2", "26.7": "26.7.1"}
        discovered_ocp = {
            "4.20": "4.20.41", "4.21": "4.21.35", "4.22": "4.22.16"
        }

        updated, changes = update_snapshot(
            current, discovered_operator, discovered_ocp, settings
        )

        self.assertEqual(updated, {
            "network-operator": {"26.7": "26.7.1"},
            "ocp": {"4.21": "4.21.35", "4.22": "4.22.16"},
        })
        self.assertEqual(changes, {
            "network-operator": {"26.7": "26.7.1"},
            "ocp": {"4.21": "4.21.35", "4.22": "4.22.16"},
        })
        self.assertEqual(current["network-operator"]["26.4"], "26.4.2")

    def test_keeps_last_known_patch_when_discovery_omits_tracked_line(self):
        settings = {
            "minimum_operator_line": "26.7",
            "operator_line_count": 1,
            "tracked_ocp_lines": ["4.22"],
        }
        current = {
            "network-operator": {"26.7": "26.7.0"},
            "ocp": {"4.22": "4.22.15"},
        }

        updated, changes = update_snapshot(current, {}, {}, settings)

        self.assertEqual(updated, current)
        self.assertEqual(changes, {})

    def test_new_operator_line_replaces_previous_line(self):
        settings = {
            "minimum_operator_line": "26.7",
            "operator_line_count": 1,
            "tracked_ocp_lines": ["4.22"],
        }
        current = {
            "network-operator": {"26.7": "26.7.0"},
            "ocp": {"4.22": "4.22.16"},
        }
        discovered_operator = {"26.7": "26.7.0", "26.10": "26.10.0"}

        updated, changes = update_snapshot(
            current, discovered_operator, {"4.22": "4.22.16"}, settings
        )

        self.assertEqual(updated["network-operator"], {"26.10": "26.10.0"})
        self.assertEqual(changes, {"network-operator": {"26.10": "26.10.0"}})

    def test_dry_run_prints_diff_without_changing_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            versions_path = Path(directory) / "versions.json"
            settings_path.write_text(json.dumps({
                "minimum_operator_line": "26.7",
                "operator_line_count": 1,
                "tracked_ocp_lines": ["4.22"],
            }))
            original = json.dumps({
                "network-operator": {"26.7": "26.7.0"},
                "ocp": {"4.22": "4.22.15"},
            }, indent=4) + "\n"
            versions_path.write_text(original)

            output = io.StringIO()
            with patch.dict(os.environ, {
                "SETTINGS_FILE_PATH": str(settings_path),
                "VERSION_FILE_PATH": str(versions_path),
            }), patch("nno_versions.update_versions.fetch_operator_versions",
                      return_value={"26.7": "26.7.0"}), patch(
                "nno_versions.update_versions.fetch_accepted_ocp_versions",
                return_value={"4.22": "4.22.16"},
            ), redirect_stdout(output):
                main(["--dry-run"])

            self.assertEqual(versions_path.read_text(), original)
            self.assertIn("Would open PR", output.getvalue())
            self.assertIn('+        "4.22": "4.22.16"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
