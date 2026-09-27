"""Registry tag discovery and stable release selection shared by operator checks."""

from collections.abc import Iterable
from typing import Pattern

import requests


def list_nvcr_tags(repository: str, timeout_sec: int = 30) -> list[str]:
    """Get image tags from a public NVCR repository with a scoped pull token."""
    auth_url = f"https://nvcr.io/proxy_auth?scope=repository:{repository}:pull"
    auth_response = requests.get(auth_url, timeout=timeout_sec)
    auth_response.raise_for_status()
    token = auth_response.json().get("token")
    if not token:
        raise ValueError(f"NVCR did not return a pull token for {repository}")

    tags_response = requests.get(
        f"https://nvcr.io/v2/{repository}/tags/list",
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout_sec,
    )
    tags_response.raise_for_status()
    tags = tags_response.json().get("tags")
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError(f"NVCR returned an invalid tag list for {repository}")

    return tags


def latest_stable_patches(tags: Iterable[str], pattern: Pattern[str]) -> dict[str, str]:
    """Keep the highest patch for each tag's named ``line`` capture group."""
    versions: dict[str, str] = {}
    highest_patches: dict[str, int] = {}
    for tag in tags:
        match = pattern.fullmatch(tag)
        if match is None:
            continue

        line = match.group("line")
        patch = int(match.group("patch"))
        if line not in highest_patches or patch > highest_patches[line]:
            highest_patches[line] = patch
            versions[line] = f"{line}.{patch}"

    return versions
