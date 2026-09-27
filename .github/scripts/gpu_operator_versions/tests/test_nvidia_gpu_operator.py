"""Tests for GPU Operator NVCR release discovery."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gpu_operator_versions.nvidia_gpu_operator import get_operator_versions


class TestGPUOperatorVersions(unittest.TestCase):
    @patch("gpu_operator_versions.nvidia_gpu_operator.list_nvcr_tags")
    def test_keeps_latest_stable_patch_per_gpu_release_line(self, list_tags):
        list_tags.return_value = [
            "v26.3.0", "v26.3.2", "v26.3.10", "v26.7.0-rc.1",
            "v26.7.1", "latest", "v19.1.0",
        ]

        versions = get_operator_versions(SimpleNamespace(request_timeout_sec=12))

        self.assertEqual(versions, {"26.3": "26.3.10", "26.7": "26.7.1"})
        list_tags.assert_called_once_with("nvidia/gpu-operator", 12)


if __name__ == "__main__":
    unittest.main()
