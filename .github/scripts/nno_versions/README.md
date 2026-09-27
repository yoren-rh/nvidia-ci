# NNO version snapshot

`python -m nno_versions.update_versions` refreshes `versions.json` using stable
Network Operator image tags from NVCR and accepted OpenShift releases from the
OpenShift release stream. It keeps the newest patch in each selected release line.

`settings.json` defines the initial CI scope:

- `tracked_ocp_lines`: OCP minor lines with a planned Prow job. The current
  development job in openshift/release PR #85277 targets 4.22. NVIDIA validates
  Network Operator 26.7 on OCP 4.17–4.22; add another line here when its job is
  ready.
- `minimum_operator_line`: oldest NNO line eligible for tracking. NVIDIA lists
  26.7.x as supported and 26.4.x as deprecated as of September 2026.
- `operator_line_count`: number of newest eligible NNO lines to track. A new
  stable NNO line replaces the older line automatically when this is `1`.

Run locally from the repository root after installing
`gpu_operator_versions/requirements.txt`:

```sh
PYTHONPATH=.github/scripts python -m nno_versions.update_versions
```

Add `--dry-run` to print the proposed version diff and PR text without changing
`versions.json`. The `update-nno-versions.yaml` workflow is manual. Its default
run previews the change; selecting `create_pr` refreshes the snapshot and opens
a PR if the file changed. GitHub requires the workflow file on the repository's
default branch before it can be started manually. PR creation also requires the
repository's Actions setting that allows `GITHUB_TOKEN` to create pull requests.

`/test` command generation and DOCA/OFED pair selection are separate work.

Sources: [NVIDIA 26.7 platform support](https://docs.nvidia.com/networking/display/kubernetes2670/platform-support.html), [NNO development job](https://github.com/openshift/release/pull/85277).
