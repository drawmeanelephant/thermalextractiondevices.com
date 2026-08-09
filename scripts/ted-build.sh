#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
BORIS_BIN=${BORIS_BIN:-$("$ROOT/scripts/ensure-boris.sh")}
CONTENT_DIR=${CONTENT_DIR:-content}
THEME=${THEME:-themes/cantilever}
DIST_DIR=${DIST_DIR:-dist/cantilever}
SITE_URL=${SITE_URL:-https://thermalextractiondevices.com}
BORIS_JOBS=${BORIS_JOBS:-1}

cd "$ROOT"

python3 scripts/ted_ids.py --root "$CONTENT_DIR" --map metadata/id-map.jsonl
python3 scripts/audit_markdown_links.py "$CONTENT_DIR"

"$BORIS_BIN" \
  --input "$CONTENT_DIR" \
  --theme "$THEME" \
  --html-dir "$DIST_DIR" \
  --sitemap \
  --site-url "$SITE_URL" \
  --layout-rule default glob:botanicals/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:changelog/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:cultivars/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:devices/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:guides/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:lab-results/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:law-and-use/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:manufacturers/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:products/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:reference/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:releases/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:safety/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:specs/* "$THEME/layouts/compact.html" \
  --layout-rule default glob:terpenes/* "$THEME/layouts/compact.html" \
  --jobs "$BORIS_JOBS"

python3 scripts/audit_html_ids.py "$DIST_DIR"

if [[ -f "$DIST_DIR/_boris/proof/checks.json" ]]; then
  bad_checks=$(jq -r '[.checks[] | select(.status != "passed" and .status != "not-applicable")] | length' "$DIST_DIR/_boris/proof/checks.json")
  if [[ "$bad_checks" -ne 0 ]]; then
    echo "Thermal Extraction Devices publication checks failed: $bad_checks check(s) are not green." >&2
    exit 1
  fi
fi

# Copy the committed security-headers manifest into the build output so
# Cloudflare Pages applies it on deploy. The source of truth is repo-root
# _headers; dist/ is generated and must never be edited directly.
if [[ -f "$ROOT/_headers" ]]; then
  cp "$ROOT/_headers" "$DIST_DIR/_headers"
  echo "==> Security headers manifest copied to $DIST_DIR/_headers"
fi

# Public-release audit hook. Audit failures and audit-tool errors are release
# failures; a broken audit cannot silently produce a deployable build.
if [[ -f "$ROOT/docs/audit-config.json" ]]; then
  set +e
  python3 scripts/audit_public_release.py --config docs/audit-config.json --root "$ROOT" >&2
  AUDIT_RC=$?
  set -e
  if [[ "$AUDIT_RC" -eq 0 ]]; then
    echo "==> Public-release audit passed"
  elif [[ "$AUDIT_RC" -eq 2 ]]; then
    echo "❌ Public-release audit tool failure (output above)" >&2
    exit 2
  else
    echo "❌ Public-release audit: blocking findings (output above)" >&2
    exit 1
  fi
fi

echo "Thermal Extraction Devices build passed: $DIST_DIR"
