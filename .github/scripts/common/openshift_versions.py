"""Accepted OpenShift release discovery shared by operator version checks."""

import re
from collections.abc import Iterable

import requests
import semver

from common.utils import logger


RELEASE_URL_API = 'https://amd64.ocp.releases.ci.openshift.org/api/v1/releasestreams/accepted'


def latest_accepted_ocp_patches(
    accepted_versions: Iterable[str], ignored_versions: str | None = None
) -> dict[str, str]:
    """Keep the newest accepted patch for each OCP minor, honoring exact/minor ignores."""
    ignored_regex = re.compile(ignored_versions) if ignored_versions is not None else None
    versions: dict[str, str] = {}

    for version in accepted_versions:
        if ignored_regex is not None and ignored_regex.fullmatch(version):
            logger.debug(f'Exact version {version} is ignored')
            continue

        parsed = semver.VersionInfo.parse(version)
        minor = f'{parsed.major}.{parsed.minor}'
        if ignored_regex is not None and ignored_regex.fullmatch(minor):
            logger.debug(f'Version {version} is ignored because all {minor} are ignored')
            continue

        current = versions.get(minor)
        if current is None or parsed > semver.VersionInfo.parse(current):
            versions[minor] = version

    return versions


def fetch_accepted_ocp_versions(
    ignored_versions: str | None = None, timeout_sec: int = 30
) -> dict[str, str]:
    """Fetch accepted 4-stable releases and select the newest patch per minor."""
    if ignored_versions is not None:
        logger.info(f'Ignored versions: {ignored_versions}')
    logger.info('Listing accepted OpenShift versions')
    response = requests.get(RELEASE_URL_API, timeout=timeout_sec)
    response.raise_for_status()
    accepted_versions = response.json()['4-stable']
    logger.debug(f'Received OpenShift versions: {accepted_versions}')
    return latest_accepted_ocp_patches(accepted_versions, ignored_versions)
