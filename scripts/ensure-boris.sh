#!/bin/bash
set -Eeuo pipefail

# Ensure standard environment PATH
export PATH="${PATH:+$PATH:}/usr/bin:/bin"

ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TARGET_BIN="${ROOT}/bin/boris"
MANIFEST="${ROOT}/bin/boris.json"
CONFIG_FILE="${ROOT}/metadata/boris-version.json"

PROVISION_REQUESTED=false
for arg in "$@"; do
  if [[ "$arg" == "--provision" || "$arg" == "-p" ]]; then
    PROVISION_REQUESTED=true
  fi
done

# Read defaults from metadata/boris-version.json
CONFIG_DATA=$(python3 -c '
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    print(d.get("repository", ""))
    print(d.get("branch", ""))
    print(d.get("commit", ""))
    print(d.get("zig_version", ""))
except Exception:
    sys.exit(1)
' "${CONFIG_FILE}" 2>/dev/null || true)

DEFAULT_REPO=$(echo "$CONFIG_DATA" | sed -n '1p')
DEFAULT_BRANCH=$(echo "$CONFIG_DATA" | sed -n '2p')
DEFAULT_COMMIT=$(echo "$CONFIG_DATA" | sed -n '3p')
DEFAULT_ZIG_VER=$(echo "$CONFIG_DATA" | sed -n '4p')

BORIS_REPOSITORY="${BORIS_REPOSITORY:-${DEFAULT_REPO:-https://github.com/drawmeanelephant/boris.git}}"
BORIS_BRANCH="${BORIS_BRANCH:-${DEFAULT_BRANCH:-afterparty}}"
PINNED_COMMIT="${BORIS_COMMIT_OVERRIDE:-${BORIS_COMMIT:-${DEFAULT_COMMIT:-9505ec610364e25f12bc4ec13e69275051f143fa}}}"
ZIG_VERSION="${ZIG_VERSION:-${DEFAULT_ZIG_VER:-0.16.0}}"

write_manifest() {
  local binary_path="$1"
  local source_type="$2"
  local repository="$3"
  local branch="$4"
  local commit="$5"
  local zig_ver="$6"
  local manifest_path="$7"

  python3 -c '
import json, sys, hashlib, datetime, os
binary, source, repo, branch, commit, zig_ver, manifest = sys.argv[1:8]
abs_binary = os.path.abspath(binary)
built_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(binary, "rb") as f:
    checksum = hashlib.sha256(f.read()).hexdigest()
data = {
    "binary": abs_binary,
    "source": source,
    "repository": repo,
    "branch": branch,
    "commit": commit,
    "zig_version": zig_ver,
    "checksum": checksum,
    "built_at": built_at
}
with open(manifest, "w") as f:
    json.dump(data, f, indent=2)
' "${binary_path}" "${source_type}" "${repository}" "${branch}" "${commit}" "${zig_ver}" "${manifest_path}"
}

verify_manifest() {
  local binary_path="$1"
  local manifest_path="$2"
  local expected_commit="$3"

  python3 -c '
import json, sys, os, hashlib
binary, manifest, expected_commit = sys.argv[1:4]
if not os.path.exists(binary) or not os.access(binary, os.X_OK) or not os.path.exists(manifest):
    sys.exit(1)
try:
    with open(manifest, "r") as f:
        data = json.load(f)
    if data.get("commit") != expected_commit:
        sys.exit(1)
    with open(binary, "rb") as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest()
    if data.get("checksum") != actual_sha:
        sys.exit(1)
    sys.exit(0)
except Exception:
    sys.exit(1)
' "${binary_path}" "${manifest_path}" "${expected_commit}" 2>/dev/null
}

verify_zig_version() {
  local zig_bin="$1"
  if [[ -n "$zig_bin" ]] && command -v "$zig_bin" >/dev/null 2>&1; then
    local v
    v=$("$zig_bin" version 2>/dev/null || echo "")
    if [[ "$v" == "$ZIG_VERSION" ]]; then
      return 0
    fi
  fi
  return 1
}

# Resolve active Zig compiler binary if available
ZIG_CMD=""
if verify_zig_version "zig"; then
  ZIG_CMD="zig"
elif [[ -x "${ROOT}/.tools/zig/zig" ]] && verify_zig_version "${ROOT}/.tools/zig/zig"; then
  ZIG_CMD="${ROOT}/.tools/zig/zig"
fi

ACTUAL_ZIG_VERSION=""
if [[ -n "${ZIG_CMD}" ]]; then
  ACTUAL_ZIG_VERSION=$("${ZIG_CMD}" version 2>/dev/null || echo "")
fi

# 1. Respect explicit executable BORIS_BIN if set (resolving to absolute path)
if [[ -n "${BORIS_BIN:-}" && -x "${BORIS_BIN}" ]]; then
  ABS_BORIS_BIN=$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "${BORIS_BIN}")
  echo "${ABS_BORIS_BIN}"
  exit 0
fi

# 2. Return existing binary if present, executable, and manifest matches
if [[ -x "${TARGET_BIN}" ]]; then
  if verify_manifest "${TARGET_BIN}" "${MANIFEST}" "${PINNED_COMMIT}"; then
    echo "${TARGET_BIN}"
    exit 0
  else
    echo "==> Existing bin/boris does not match manifest or target commit (${PINNED_COMMIT})." >&2
  fi
fi

# 3. Check for local sibling repository (pre-built executable or build from source)
# Sibling HEAD must match PINNED_COMMIT
# Prebuilt binary requires verifiable matching manifest for PINNED_COMMIT
# Source build requires exact ZIG_VERSION compiler
SIBLING_CANDIDATES=(
  "${ROOT}/../boris"
  "${ROOT}/../boris/main"
)

mkdir -p "${ROOT}/bin"

for sibling in "${SIBLING_CANDIDATES[@]}"; do
  if [[ -d "${sibling}" ]]; then
    sibling_commit=$(git -C "${sibling}" rev-parse HEAD 2>/dev/null || echo "unknown")
    sibling_branch=$(git -C "${sibling}" branch --show-current 2>/dev/null || echo "${BORIS_BRANCH}")

    if [[ "${sibling_commit}" != "${PINNED_COMMIT}" ]]; then
      echo "==> Skipping sibling repository at ${sibling} (commit ${sibling_commit} != target commit ${PINNED_COMMIT})." >&2
      continue
    fi

    if [[ -x "${sibling}/zig-out/bin/boris" ]]; then
      sibling_manifest=""
      if [[ -f "${sibling}/bin/boris.json" ]]; then
        sibling_manifest="${sibling}/bin/boris.json"
      elif [[ -f "${sibling}/build-manifest.json" ]]; then
        sibling_manifest="${sibling}/build-manifest.json"
      fi

      if [[ -n "${sibling_manifest}" ]] && verify_manifest "${sibling}/zig-out/bin/boris" "${sibling_manifest}" "${PINNED_COMMIT}"; then
        echo "==> Attempting pre-built Boris binary from sibling repository (${sibling})..." >&2
        if cp "${sibling}/zig-out/bin/boris" "${TARGET_BIN}" 2>/dev/null; then
          chmod +x "${TARGET_BIN}"
          write_manifest "${TARGET_BIN}" "sibling" "${BORIS_REPOSITORY}" "${sibling_branch}" "${sibling_commit}" "${ACTUAL_ZIG_VERSION:-$ZIG_VERSION}" "${MANIFEST}"
          echo "${TARGET_BIN}"
          exit 0
        fi
      else
        echo "==> Skipping sibling pre-built binary at ${sibling} (no matching manifest for target commit ${PINNED_COMMIT})." >&2
      fi
    fi

    if [[ -f "${sibling}/build.zig" ]]; then
      if [[ -n "${ZIG_CMD}" ]] && verify_zig_version "${ZIG_CMD}"; then
        echo "==> Attempting Boris build from local sibling repository (${sibling})..." >&2
        if (cd "${sibling}" && "$ZIG_CMD" build 2>/dev/null) && [[ -x "${sibling}/zig-out/bin/boris" ]]; then
          if cp "${sibling}/zig-out/bin/boris" "${TARGET_BIN}" 2>/dev/null; then
            chmod +x "${TARGET_BIN}"
            write_manifest "${TARGET_BIN}" "sibling" "${BORIS_REPOSITORY}" "${sibling_branch}" "${sibling_commit}" "${ACTUAL_ZIG_VERSION}" "${MANIFEST}"
            echo "${TARGET_BIN}"
            exit 0
          fi
        fi
      else
        echo "==> Skipping sibling source build at ${sibling} (active Zig compiler version != ${ZIG_VERSION})." >&2
      fi
    fi
  fi
done

# 4. If non-remote resolution failed, verify if remote provisioning is permitted
if [[ "${BORIS_AUTO_PROVISION:-0}" != "1" && "${PROVISION_REQUESTED}" != "true" ]]; then
  echo "ERROR: Boris binary is not available at bin/boris (or manifest mismatched)." >&2
  echo "To resolve or provision the Boris compiler, run:" >&2
  echo "  ./scripts/ensure-boris.sh --provision" >&2
  exit 1
fi

echo "==> Provisioning Boris compiler (${PINNED_COMMIT})..." >&2

# Download Zig compiler if valid compiler binary is missing
mkdir -p "${ROOT}/.tools/cache/global" "${ROOT}/.tools/cache/local"
export ZIG_GLOBAL_CACHE_DIR="${ROOT}/.tools/cache/global"
export ZIG_LOCAL_CACHE_DIR="${ROOT}/.tools/cache/local"

if [[ -z "${ZIG_CMD}" ]]; then
  ZIG_DIR="${ROOT}/.tools/zig"
  echo "==> Provisioning Zig ${ZIG_VERSION} compiler..." >&2
  mkdir -p "${ROOT}/.tools"

  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
  ARCH=$(uname -m)
  if [[ "${OS}" == "darwin" ]]; then
    OS="macos"
  fi
  if [[ "${ARCH}" == "x86_64" ]]; then
    ARCH="x86_64"
  elif [[ "${ARCH}" == "arm64" || "${ARCH}" == "aarch64" ]]; then
    ARCH="aarch64"
  fi
  PLATFORM_KEY="${ARCH}-${OS}"

  EXPECTED_SHA=$(python3 -c '
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    print(d.get("zig_checksums", {}).get(sys.argv[2], ""))
except Exception:
    pass
' "${CONFIG_FILE}" "${PLATFORM_KEY}" 2>/dev/null || true)

  if [[ -z "${EXPECTED_SHA}" ]]; then
    echo "ERROR: No committed SHA-256 checksum found for platform ${PLATFORM_KEY} in ${CONFIG_FILE}" >&2
    exit 1
  fi

  ZIG_URL="https://ziglang.org/download/${ZIG_VERSION}/zig-${ARCH}-${OS}-${ZIG_VERSION}.tar.xz"
  ZIG_TAR_TMP="${ROOT}/.tools/zig-${ZIG_VERSION}-${PLATFORM_KEY}.tar.xz.tmp"
  ZIG_EXTRACT_TMP="${ROOT}/.tools/zig-extract.tmp"

  rm -rf "${ZIG_TAR_TMP}" "${ZIG_EXTRACT_TMP}"

  if ! curl -f -L -s -o "${ZIG_TAR_TMP}" "${ZIG_URL}"; then
    echo "ERROR: Failed to download Zig from ${ZIG_URL}" >&2
    rm -f "${ZIG_TAR_TMP}"
    exit 1
  fi

  ACTUAL_SHA=$(python3 -c '
import hashlib, sys
with open(sys.argv[1], "rb") as f:
    print(hashlib.sha256(f.read()).hexdigest())
' "${ZIG_TAR_TMP}")
  if [[ "${ACTUAL_SHA}" != "${EXPECTED_SHA}" ]]; then
    echo "ERROR: Zig download checksum mismatch for ${PLATFORM_KEY}!" >&2
    echo "  Expected: ${EXPECTED_SHA}" >&2
    echo "  Actual:   ${ACTUAL_SHA}" >&2
    rm -f "${ZIG_TAR_TMP}"
    exit 1
  fi

  mkdir -p "${ZIG_EXTRACT_TMP}"
  if ! tar -xJ -C "${ZIG_EXTRACT_TMP}" --strip-components=1 -f "${ZIG_TAR_TMP}"; then
    echo "ERROR: Failed to extract Zig archive." >&2
    rm -rf "${ZIG_TAR_TMP}" "${ZIG_EXTRACT_TMP}"
    exit 1
  fi

  rm -rf "${ZIG_DIR}"
  mv "${ZIG_EXTRACT_TMP}" "${ZIG_DIR}"
  rm -f "${ZIG_TAR_TMP}"
  ZIG_CMD="${ZIG_DIR}/zig"
fi

export PATH="$(dirname "${ZIG_CMD}"):${PATH}"
ACTUAL_ZIG_VERSION=$("${ZIG_CMD}" version 2>/dev/null || echo "${ZIG_VERSION}")

if [[ "${ACTUAL_ZIG_VERSION}" != "${ZIG_VERSION}" ]]; then
  echo "ERROR: Compiler binary version (${ACTUAL_ZIG_VERSION}) does not match configured Zig version (${ZIG_VERSION})" >&2
  exit 1
fi

BUILD_DIR="${ROOT}/.tools/boris-build"
rm -rf "${BUILD_DIR}"
echo "==> Fetching Boris compiler repository..." >&2
mkdir -p "${BUILD_DIR}"

if ! git clone --no-single-branch "${BORIS_REPOSITORY}" "${BUILD_DIR}" >&2; then
  echo "ERROR: Failed to clone Boris repository from ${BORIS_REPOSITORY}" >&2
  rm -rf "${BUILD_DIR}"
  exit 1
fi

echo "==> Checking out pinned commit ${PINNED_COMMIT}..." >&2
if ! (cd "${BUILD_DIR}" && git checkout "${PINNED_COMMIT}") >&2; then
  echo "ERROR: Failed to checkout Boris commit ${PINNED_COMMIT}" >&2
  rm -rf "${BUILD_DIR}"
  exit 1
fi

ACTUAL_COMMIT=$(git -C "${BUILD_DIR}" rev-parse HEAD 2>/dev/null || echo "")
if [[ "${ACTUAL_COMMIT}" != "${PINNED_COMMIT}" ]]; then
  echo "ERROR: Boris HEAD commit (${ACTUAL_COMMIT}) does not match pinned SHA (${PINNED_COMMIT})" >&2
  rm -rf "${BUILD_DIR}"
  exit 1
fi

echo "==> Compiling Boris executable..." >&2
if ! (cd "${BUILD_DIR}" && "$ZIG_CMD" build) >&2; then
  echo "ERROR: Boris compilation failed" >&2
  rm -rf "${BUILD_DIR}"
  exit 1
fi

if [[ ! -x "${BUILD_DIR}/zig-out/bin/boris" ]]; then
  echo "ERROR: Boris build failed to produce executable" >&2
  rm -rf "${BUILD_DIR}"
  exit 1
fi

cp "${BUILD_DIR}/zig-out/bin/boris" "${TARGET_BIN}"
chmod +x "${TARGET_BIN}"
write_manifest "${TARGET_BIN}" "remote" "${BORIS_REPOSITORY}" "${BORIS_BRANCH}" "${PINNED_COMMIT}" "${ACTUAL_ZIG_VERSION}" "${MANIFEST}"
rm -rf "${BUILD_DIR}"

echo "${TARGET_BIN}"
