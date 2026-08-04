#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
BORIS_BIN=${BORIS_BIN:-./bin/boris}
CONTENT_DIR=${CONTENT_DIR:-content}
PUBLISH_DIR=${PUBLISH_DIR:-publish}
THEME=${THEME:-themes/cantilever}
SITE_URL=${SITE_URL:-https://thermalextractiondevices.com}
BORIS_JOBS=${BORIS_JOBS:-1}

cd "$ROOT"

if [[ ! -x "$BORIS_BIN" ]]; then
  echo "ERROR: Boris binary is not executable: $BORIS_BIN" >&2
  exit 2
fi

mkdir -p "$PUBLISH_DIR"

echo "==> Exporting Thermal Extraction Devices publishing artifacts to $PUBLISH_DIR"
python3 scripts/ted_ids.py --root "$CONTENT_DIR" --map metadata/id-map.jsonl

"$BORIS_BIN" --input "$CONTENT_DIR" --theme "$THEME" --html-dir "$PUBLISH_DIR/site" --sitemap --site-url "$SITE_URL" --jobs "$BORIS_JOBS" --quiet
"$BORIS_BIN" --input "$CONTENT_DIR" --out "$PUBLISH_DIR/ir" --quiet
"$BORIS_BIN" --input "$CONTENT_DIR" --rag-dir "$PUBLISH_DIR/rag" --split-size 65536 --quiet
"$BORIS_BIN" --input "$CONTENT_DIR" --context-dir "$PUBLISH_DIR/context" --split-size 65536 --quiet

if "$BORIS_BIN" --input "$CONTENT_DIR" --llms-path "$PUBLISH_DIR/llms.txt" --quiet; then
  if python3 -c 'from pathlib import Path; import sys; Path(sys.argv[1]).read_text(encoding="utf-8")' "$PUBLISH_DIR/llms.txt"; then
    echo "✅ llms.txt exported and is valid UTF-8"
  fi
fi

cat > "$PUBLISH_DIR/README.txt" <<'EOF'
Thermal Extraction Devices publishing artifacts

site/     Public HTML site.
llms.txt  Public crawler/discovery index.
context/  Provenance-rich bundle for LLM context uploads.
rag/      Retrieval corpus for local or hosted RAG systems.
ir/       Machine-readable graph and reverse-index artifacts.
EOF

echo "✅ Publishing export complete: $PUBLISH_DIR"
