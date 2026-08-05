#!/bin/bash
set -Eeuo pipefail

export PATH="${PATH:+$PATH:}/usr/bin:/bin"

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

export BORIS_AUTO_PROVISION=1

echo "==> Resolving Boris compiler binary..."
BORIS_BIN=$(./scripts/ensure-boris.sh --provision)
export BORIS_BIN

echo "==> Running Thermal Extraction Devices graph validation gate..."
./bin/validate_graph.sh

echo "==> Building static site output..."
./scripts/ted-build.sh

echo "✅ Cloudflare build succeeded."
