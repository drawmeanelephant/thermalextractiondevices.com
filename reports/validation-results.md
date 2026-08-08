# Validation Results

> Historical validation snapshot. This report predates the current California
> data collections and the roadmap/status coordination layer. For the current
> baseline, see docs/status.md and rerun the commands below.

Status: **historical PASS** — all gates were clean as of the recorded run.

## Commands executed

### 1. ID / form-id normalization and map regeneration

```
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl --write
normalized 58 pages; wrote metadata/id-map.jsonl
```

- Restoring in-scope replacements for `TED-0001`, `TGDE-0001`, and `TREF-0001` was required: `ted_ids.py` anchors each collection's canonical sequence on the prefix-matched anchor file. Deleting those files silently renumbers siblings, so the pages were replaced with in-scope content instead of deleted.
- `TSAFE-0001`, `TSPEC-0001` deleted cleanly (no sibling satellites; no renumbering).

### 2. Graph validation gate

```
export BORIS_BIN=./bin/boris
./bin/validate_graph.sh
```

Result:

```
==> Validating Thermal Extraction Devices form IDs
validated 58 pages; no files changed
==> Running Boris graph diagnostics
⚠️ Boris reported baseline diagnostics; parent edges remain valid.
==> Compiling primary Cantilever publication
validated 58 pages; no files changed
Markdown link audit: all local Markdown links resolve
HTML ID audit: 0 pages with duplicate IDs; 0 duplicate occurrences
Thermal Extraction Devices build passed: dist/cantilever
🎉 Graph, form IDs, HTML IDs, and publication checks passed cleanly.
```

### 3. Standalone markdown link audit

```
python3 scripts/audit_markdown_links.py content
Markdown link audit: all local Markdown links resolve
exit=0
```

Note: the audit resolves **file paths**, not logical IDs. A link to the TREF-0003 satellite must target `evidence-labels-and-claim-grammar.md`, not `TREF-0003.md`.

### 4. Publishing artifact export

```
BORIS_BIN=./bin/boris ./scripts/ted-publish.sh
==> Exporting Thermal Extraction Devices publishing artifacts to publish
validated 58 pages; no files changed
✅ llms.txt exported and is valid UTF-8
✅ Publishing export complete: publish
```

`publish/site/`, `publish/ir/`, `publish/rag/`, `publish/context/`, and `publish/llms.txt` all generated without error.

## Spot checks on built HTML (`dist/cantilever`)

- `devices/TED-0001.html` (Arizer Solo III): hybrid 80/20 convection claim attributed to manufacturer, heat levels to 220 °C, `Sources` footnotes render.
- `devices/TED-0002.html` (DynaVap M7): cap click 240 °C ± 10 °C and Low-Temp 215 °C ± 10 °C attributed to DynaVap FAQ; DynaCoil identified as concentrate accessory.
- `devices/TED-0003.html` (Mighty+): 1.4 cm³ chamber and 3300 mAh battery flagged as manufacturer figures; 18650 cell format flagged as third-party.
- `manufacturers/TMFR-0001.html` (Arizer): founded 2005 citation renders.
- `cultivars/TCUL-0001.html` (Blue Dream): sample/demonstration labeling renders on cultivar, product, and COA records.
- `terpenes/TTRP-0001.html` (α-bisabolol): NIST absence noted; secondary-literature reduced-pressure BP labeled as such.

## Remaining notes

- `scripts/ted_ids.py --write` regenerated `metadata/id-map.jsonl` (58 rows). This file is authoritative and derived from content; the regeneration is intentional.
- Build artifacts `dist/`, `publish/`, `site/` remain untracked (never committed).
