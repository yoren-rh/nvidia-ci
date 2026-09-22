#!/usr/bin/env bash

# Get the directory where this script is located
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default to must-gather dir
ARTIFACT_DIR="${ARTIFACT_DIR:-must-gather}"


# Collect NFD operator must-gather
NFD_ARTIFACT_DIR="${ARTIFACT_DIR}/nfd-must-gather"
mkdir -p "${NFD_ARTIFACT_DIR}"
echo "Collecting NFD operator must-gather in ${NFD_ARTIFACT_DIR}"
OUTPUT_DIR="${NFD_ARTIFACT_DIR}" "$SCRIPTS_DIR/nfd-must-gather.sh"


# Collect Network Operator SOS report
NNO_ARTIFACT_DIR="${ARTIFACT_DIR}/nno-must-gather"
mkdir -p "${NNO_ARTIFACT_DIR}"
echo "Collecting Network Operator SOS report in ${NNO_ARTIFACT_DIR}"

if command -v kubectl >/dev/null 2>&1; then
	KUBECTL_BIN="$(command -v kubectl)"
elif command -v oc >/dev/null 2>&1; then
	KUBECTL_BIN="$(command -v oc)"
else
	echo "FATAL: neither 'kubectl' nor 'oc' found in PATH" >&2
	exit 1
fi

"$SCRIPTS_DIR/network-operator-sosreport.sh" \
	--output-dir "${NNO_ARTIFACT_DIR}" \
	--no-compress \
	--skip-report \
	--namespace nvidia-network-operator \
	--kubectl-path "${KUBECTL_BIN}"
