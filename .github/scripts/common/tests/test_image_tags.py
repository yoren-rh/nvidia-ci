"""Tests for shared NVCR tag discovery."""

import re
import unittest
from unittest.mock import MagicMock, call, patch

from common.image_tags import latest_stable_patches, list_nvcr_tags


class TestNVCRTags(unittest.TestCase):
    def test_selects_numeric_patch_and_ignores_unstable_tags(self):
        pattern = re.compile(r"^v(?P<line>\d{2}\.\d+)\.(?P<patch>\d+)$")

        self.assertEqual(
            latest_stable_patches(
                ["v26.7.9", "v26.7.10", "v26.7.11-rc.1", "v26.8.1", "latest"],
                pattern,
            ),
            {"26.7": "26.7.10", "26.8": "26.8.1"},
        )

    @patch("common.image_tags.requests.get")
    def test_fetches_tags_with_repository_scoped_token(self, get):
        auth_response = MagicMock()
        auth_response.json.return_value = {"token": "pull-token"}
        tags_response = MagicMock()
        tags_response.json.return_value = {"tags": ["v26.7.0", "v26.7.1"]}
        get.side_effect = [auth_response, tags_response]

        self.assertEqual(list_nvcr_tags("nvidia/cloud-native/network-operator", 12),
                         ["v26.7.0", "v26.7.1"])
        self.assertEqual(get.call_args_list, [
            call(
                "https://nvcr.io/proxy_auth?scope=repository:nvidia/cloud-native/network-operator:pull",
                timeout=12,
            ),
            call(
                "https://nvcr.io/v2/nvidia/cloud-native/network-operator/tags/list",
                headers={"Authorization": "Bearer pull-token"},
                timeout=12,
            ),
        ])
        auth_response.raise_for_status.assert_called_once_with()
        tags_response.raise_for_status.assert_called_once_with()

    @patch("common.image_tags.requests.get")
    def test_rejects_missing_token(self, get):
        get.return_value.json.return_value = {}

        with self.assertRaisesRegex(ValueError, "pull token"):
            list_nvcr_tags("nvidia/gpu-operator")
        get.assert_called_once()

    @patch("common.image_tags.requests.get")
    def test_rejects_invalid_tag_response(self, get):
        auth_response = MagicMock()
        auth_response.json.return_value = {"token": "pull-token"}
        tags_response = MagicMock()
        tags_response.json.return_value = {"tags": None}
        get.side_effect = [auth_response, tags_response]

        with self.assertRaisesRegex(ValueError, "invalid tag list"):
            list_nvcr_tags("nvidia/gpu-operator")


if __name__ == "__main__":
    unittest.main()
