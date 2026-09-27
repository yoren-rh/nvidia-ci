"""Track the newest accepted patch for each configured NNO and OCP release line."""

import argparse
import difflib
import json
import os
from pathlib import Path

from common.openshift_versions import fetch_accepted_ocp_versions
from common.version_changes import apply_diffs, calculate_changes
from nno_versions.nvidia_network_operator import fetch_operator_versions


SCRIPT_DIR = Path(__file__).parent


def select_tracked_versions(available: dict[str, str], tracked: list[str]) -> dict[str, str]:
    """Keep only release lines for which we intend to run CI."""
    return {line: available[line] for line in tracked if line in available}


def operator_lines_to_track(current: dict, available: dict, settings: dict) -> list[str]:
    """Select the newest NNO lines above the configured oldest supported line."""
    def line_key(line: str) -> tuple[int, int]:
        year, month = line.split(".")
        return int(year), int(month)

    minimum = line_key(settings["minimum_operator_line"])
    count = settings["operator_line_count"]
    if count < 1:
        raise ValueError("operator_line_count must be positive")
    lines = set(current.get("network-operator", {})) | set(available)
    return sorted((line for line in lines if line_key(line) >= minimum),
                  key=line_key, reverse=True)[:count]


def update_snapshot(
    current: dict, operator_versions: dict[str, str], ocp_versions: dict[str, str],
    settings: dict,
) -> tuple[dict, dict]:
    """Return the updated snapshot and its additions/patch changes.

    Retired lines are dropped from the snapshot when settings no longer track them.
    """
    tracked_operator = operator_lines_to_track(current, operator_versions, settings)
    tracked_ocp = settings["tracked_ocp_lines"]
    selected_current = {
        "network-operator": select_tracked_versions(
            current.get("network-operator", {}), tracked_operator
        ),
        "ocp": select_tracked_versions(current.get("ocp", {}), tracked_ocp),
    }
    selected_available = {
        "network-operator": select_tracked_versions(operator_versions, tracked_operator),
        "ocp": select_tracked_versions(ocp_versions, tracked_ocp),
    }
    changes = calculate_changes(selected_current, selected_available)
    return apply_diffs(selected_current, changes), changes


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the proposed version update and PR without writing files",
    )
    args = parser.parse_args(argv)

    settings_path = Path(os.getenv("SETTINGS_FILE_PATH", SCRIPT_DIR / "settings.json"))
    versions_path = Path(os.getenv("VERSION_FILE_PATH", SCRIPT_DIR / "versions.json"))
    timeout_sec = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

    with settings_path.open() as settings_file:
        settings = json.load(settings_file)
    original_text = versions_path.read_text()
    current = json.loads(original_text)

    operator_versions = fetch_operator_versions(timeout_sec)
    ocp_versions = fetch_accepted_ocp_versions(timeout_sec=timeout_sec)
    updated, _ = update_snapshot(current, operator_versions, ocp_versions, settings)
    updated_text = json.dumps(updated, indent=4) + "\n"

    if args.dry_run:
        if original_text == updated_text:
            print("No version changes. No PR would be opened.")
            return

        print("Would open PR: [Automatic] Update NNO versions")
        print("Proposed PR body: Refresh the tracked NNO and OpenShift versions.")
        print("Proposed versions.json change:")
        print("".join(difflib.unified_diff(
            original_text.splitlines(keepends=True),
            updated_text.splitlines(keepends=True),
            fromfile="versions.json (current)",
            tofile="versions.json (proposed)",
        )), end="")
        return

    versions_path.write_text(updated_text)


if __name__ == "__main__":
    main()
