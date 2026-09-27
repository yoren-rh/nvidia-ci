#!/usr/bin/env python
import re
import requests


from gpu_operator_versions.settings import Settings
from common.utils import logger
from common.image_tags import latest_stable_patches, list_nvcr_tags

GPU_OPERATOR_NVCR_REPOSITORY = 'nvidia/gpu-operator'
GPU_OPERATOR_STABLE_TAG = re.compile(r'^v(?P<line>2\d\.\d+)\.(?P<patch>\d+)$')

GPU_OPERATOR_GHCR_AUTH_URL = 'https://ghcr.io/token?scope=repository:nvidia/gpu-operator/gpu-operator-bundle:pull'
GPU_OPERATOR_GHCR_LATEST_URL = 'https://ghcr.io/v2/nvidia/gpu-operator/gpu-operator-bundle/manifests/main-latest'

def get_operator_versions(settings: Settings) -> dict:
    logger.info('Listing tags of the GPU operator image')
    tags = list_nvcr_tags(GPU_OPERATOR_NVCR_REPOSITORY, settings.request_timeout_sec)
    logger.debug(f'Received GPU operator image tags: {tags}')
    return latest_stable_patches(tags, GPU_OPERATOR_STABLE_TAG)

def get_sha(settings: Settings) -> str:

    logger.info('Calling GHCR token endpoint for anonymous access')
    # No Content-Type needed for GET request without body
    auth_req = requests.get(GPU_OPERATOR_GHCR_AUTH_URL,
                            allow_redirects=True,
                            timeout=settings.request_timeout_sec)
    auth_req.raise_for_status()
    token = auth_req.json()['token']

    logger.info('Getting digest of the GPU operator OLM bundle')
    # NVIDIA now uses OCI index format (multi-platform manifest)
    # Using HEAD since we only need the Docker-Content-Digest header
    req = requests.head(GPU_OPERATOR_GHCR_LATEST_URL,
                        headers={
                            'Accept': 'application/vnd.oci.image.index.v1+json',
                            'Authorization': f'Bearer {token}'
                        },
                        timeout=settings.request_timeout_sec)
    req.raise_for_status()

    # For OCI index format, the digest is in the Docker-Content-Digest header
    digest = req.headers.get('Docker-Content-Digest', '')
    if not digest:
        logger.error(f'Docker-Content-Digest header not found in response headers: {req.headers}')
        msg = 'Digest not found in manifest response headers'
        raise ValueError(msg)

    logger.info(f'Successfully retrieved digest: {digest}')
    return digest
