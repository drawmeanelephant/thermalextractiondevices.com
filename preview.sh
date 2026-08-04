#!/usr/bin/env bash
set -Eeuo pipefail

PORT=${1:-8000}
THEME=${2:-themes/cantilever}
DIST_DIR=${DIST_DIR:-dist/preview}

THEME="$THEME" DIST_DIR="$DIST_DIR" ./scripts/ted-build.sh

echo "✅ Site build complete: ./${DIST_DIR}"
echo "🚀 Serving http://localhost:${PORT}"
python3 -m http.server "$PORT" --directory "$DIST_DIR"
