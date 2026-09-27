"""Discover stable NVIDIA Network Operator image versions from NVCR."""

import re
from collections.abc import Iterable

from common.image_tags import latest_stable_patches, list_nvcr_tags

NVCR_REPOSITORY = "nvidia/cloud-native/network-operator"
STABLE_TAG = re.compile(r"^v(?P<line>\d{2}\.\d{1,2})\.(?P<patch>\d+)$")


def latest_operator_versions(tags: Iterable[str]) -> dict[str, str]:
    """Keep the highest stable patch for each NNO year/month release line."""
    return latest_stable_patches(tags, STABLE_TAG)


def fetch_operator_versions(timeout_sec: int = 30) -> dict[str, str]:
    """List public NVCR tags using a repository-scoped bearer token."""
    return latest_operator_versions(list_nvcr_tags(NVCR_REPOSITORY, timeout_sec))
