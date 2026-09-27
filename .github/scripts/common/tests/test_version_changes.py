"""Tests for the shared version snapshot operations."""

import unittest

from common.version_changes import apply_diffs, calculate_changes


class TestVersionChanges(unittest.TestCase):
    def test_nested_diff_includes_additions_and_updates_but_not_removals(self):
        old = {
            "network-operator": {"26.1": "26.1.1", "26.4": "26.4.1"},
            "ocp": {"4.21": "4.21.34"},
        }
        new = {
            "network-operator": {"26.4": "26.4.2", "26.7": "26.7.0"},
            "ocp": {"4.21": "4.21.34"},
        }

        self.assertEqual(
            calculate_changes(old, new),
            {"network-operator": {"26.4": "26.4.2", "26.7": "26.7.0"}},
        )

    def test_apply_diffs_preserves_existing_values_without_mutation(self):
        old = {
            "network-operator": {"26.1": "26.1.1", "26.4": "26.4.1"},
            "ocp": {"4.21": "4.21.34"},
        }
        changes = {"network-operator": {"26.4": "26.4.2", "26.7": "26.7.0"}}

        self.assertEqual(
            apply_diffs(old, changes),
            {
                "network-operator": {
                    "26.1": "26.1.1", "26.4": "26.4.2", "26.7": "26.7.0"
                },
                "ocp": {"4.21": "4.21.34"},
            },
        )
        self.assertEqual(old["network-operator"]["26.4"], "26.4.1")


if __name__ == "__main__":
    unittest.main()
