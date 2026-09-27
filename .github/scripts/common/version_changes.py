"""Compare and update nested version snapshots without operator-specific policy."""

from common.utils import logger


def calculate_changes(old_versions: dict, new_versions: dict) -> dict:
    """Return added or changed values; keep removed keys out of the diff."""
    changes = {}
    for key, value in new_versions.items():
        if isinstance(value, dict):
            logger.info(f'Comparing versions under "{key}"')
            nested_changes = calculate_changes(old_versions.get(key, {}), value)
            if nested_changes:
                changes[key] = nested_changes
        elif key not in old_versions or old_versions[key] != value:
            logger.info(f'Key "{key}" has changed: {old_versions.get(key)} > {value}')
            changes[key] = value
    return changes


def apply_diffs(old_versions: dict, diffs: dict) -> dict:
    """Merge a version diff into a snapshot without mutating the original."""
    updated = dict(old_versions)
    for key, value in diffs.items():
        if isinstance(value, dict) and key in updated and isinstance(updated[key], dict):
            updated[key] = apply_diffs(updated[key], value)
        else:
            updated[key] = value
    return updated
