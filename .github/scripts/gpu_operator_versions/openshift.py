#!/usr/bin/env python
"""GPU version check adapter for shared OpenShift release discovery."""

from common.openshift_versions import RELEASE_URL_API, fetch_accepted_ocp_versions
from gpu_operator_versions.settings import Settings


def fetch_ocp_versions(settings: Settings) -> dict[str, str]:
    """Fetch accepted OCP versions using the GPU checker's settings."""
    return fetch_accepted_ocp_versions(
        settings.ignored_versions, settings.request_timeout_sec
    )
