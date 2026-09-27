"""Tests for shared accepted OpenShift release discovery."""

import unittest
from unittest.mock import MagicMock, patch

from common.openshift_versions import (
    RELEASE_URL_API,
    fetch_accepted_ocp_versions,
    latest_accepted_ocp_patches,
)


class TestAcceptedOpenShiftVersions(unittest.TestCase):
    def test_selects_latest_patch_and_honors_exact_and_minor_ignores(self):
        self.assertEqual(
            latest_accepted_ocp_patches(
                ["4.21.9", "4.21.10", "4.22.0-rc.1", "4.22.0", "4.20.3"],
                r"4\.20|4\.22\.0",
            ),
            {"4.21": "4.21.10", "4.22": "4.22.0-rc.1"},
        )

    def test_no_ignore_pattern_keeps_all_minor_lines(self):
        self.assertEqual(
            latest_accepted_ocp_patches(["4.21.9", "4.22.0", "4.21.10"]),
            {"4.21": "4.21.10", "4.22": "4.22.0"},
        )

    @patch('common.openshift_versions.requests.get')
    def test_fetches_accepted_stream_without_gpu_settings(self, mock_get):
        response = MagicMock()
        response.json.return_value = {'4-stable': ['4.21.9', '4.21.10']}
        mock_get.return_value = response

        self.assertEqual(
            fetch_accepted_ocp_versions(r"4\.20", timeout_sec=12),
            {'4.21': '4.21.10'},
        )
        mock_get.assert_called_once_with(RELEASE_URL_API, timeout=12)
        response.raise_for_status.assert_called_once()


if __name__ == '__main__':
    unittest.main()
