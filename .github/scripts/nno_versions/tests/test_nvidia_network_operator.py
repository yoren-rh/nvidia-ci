"""Tests for NVCR NNO release discovery."""

import unittest
from unittest.mock import patch

from nno_versions.nvidia_network_operator import (
    NVCR_REPOSITORY,
    fetch_operator_versions,
    latest_operator_versions,
)


class TestNetworkOperatorVersions(unittest.TestCase):
    def test_latest_stable_patch_per_release_line(self):
        tags = [
            "v26.7.0", "v26.7.2", "v26.7.1", "v26.4.1", "v26.4.10",
            "v26.7.3-rc.1", "v26.7.4-beta.2", "latest", "26.7.5",
        ]

        self.assertEqual(
            latest_operator_versions(tags),
            {"26.7": "26.7.2", "26.4": "26.4.10"},
        )

    @patch("nno_versions.nvidia_network_operator.list_nvcr_tags")
    def test_fetches_network_operator_tags(self, list_tags):
        list_tags.return_value = ["v26.7.0", "v26.7.1"]
        self.assertEqual(fetch_operator_versions(timeout_sec=12), {"26.7": "26.7.1"})
        list_tags.assert_called_once_with(NVCR_REPOSITORY, 12)


if __name__ == "__main__":
    unittest.main()
