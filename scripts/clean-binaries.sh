#!/bin/bash
set -Eeuo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
BIN_DIR="${ROOT}/bin"
TOOLS_DIR="${ROOT}/.tools"

CLEAN_CACHE=false
for arg in "$@"; do
  if [[ "$arg" == "--all" || "$arg" == "--cache" ]]; then
    CLEAN_CACHE=true
  fi
done

echo "==> Cleaning provisioner-owned binary artifacts..."
count=0

if [[ -f "${BIN_DIR}/boris" ]]; then
  rm -f "${BIN_DIR}/boris"
  echo "  Removed: bin/boris"
  count=$((count + 1))
fi

if [[ -f "${BIN_DIR}/boris.json" ]]; then
  rm -f "${BIN_DIR}/boris.json"
  echo "  Removed: bin/boris.json"
  count=$((count + 1))
fi

if [[ "${CLEAN_CACHE}" == "true" && -d "${TOOLS_DIR}" ]]; then
  rm -rf "${TOOLS_DIR}"
  echo "  Removed: .tools/ cache directory"
fi

echo "✅ Cleaned ${count} provisioner artifact(s)."
