# Device Taxonomy Wave 1 — Taxonomy & Architecture Agent Report

**Branch:** `agent/device-taxonomy`
**HEAD (start):** `52109e2e2d15ee00e600159d2c037c094a867e59` (`github/main` after pull)
**Date:** 2026-08-08

## Summary

Established a technically useful device architecture taxonomy so that hundreds of future device pages do not devolve into inconsistent prose. The taxonomy models **five orthogonal axes** (heating mechanism, heat-generation mechanism, delivery mode, operating mode, power) instead of a single mutually-exclusive "type" field, adds a **ball-vape component model** (complete system / heater head / coil / PID controller / bowl / stand / bundle) that prevents retailer bundles from becoming unique models, and ships a machine-readable vocabulary plus a validation script that enforces it against `content/devices/*.md`.

## Files added

| File | Purpose |
| --- | --- |
| `content/reference/TREF-0004.md` | Published taxonomy standard (five axes, ball-vape model, reusable terminology, relation conventions, validation rules) |
| `metadata/device-taxonomy.json` | Machine-readable vocabulary: axes, ball-vape components, recognized descriptors, manufacturer slugs, tag aliases, contradiction rules TAX-01…TAX-05, advisory rules ADV-01…ADV-02 |
| `scripts/audit_device_taxonomy.py` | Validation script that audits `content/devices/*.md` against the vocabulary and rules |
| `tests/test_device_taxonomy.py` | 12 unit tests covering parsing, every TAX rule, both ADV rules, and vocabulary warnings |
| `docs/device-taxonomy-migration.md` | Migration recommendations: per-axis audit of all 24 device pages, ball-vape role mapping, tag change list, new-page process |
| `reports/device-taxonomy-wave-01.md` | This report |

## Files modified

| File | Change |
| --- | --- |
| `content/reference.md` | Added TREF-0004 to the Technical Reference Documents index |
| `bin/validate_graph.sh` | Added the taxonomy audit step to the validation gate (after `ted_ids.py`, before Boris check) |

## Entities created

- `reference/TREF-0004` — Device Architecture Taxonomy (published reference satellite).

## Graph relationships created

- `TREF-0004 relates_to reference/TREF-0001` (Physical Property Data Standards)
- `TREF-0004 relates_to reference/TREF-0003` (Evidence Labels and Claim Grammar)
- Documented relation conventions for device pages (device→manufacturer `relates_to`, successor `supersedes`, sibling/family `relates_to`; no invented relation kinds).

## Primary sources verified

No new material claims were published; this wave is a classification standard, not device data. The taxonomy's example classifications were cross-checked against the **already-verified device corpus** (`content/devices/*.md`, whose sources cite official product pages/manuals/CPSC records) and the manufacturer dossiers' source ledgers. Perplexity research reports were used only as discovery inputs for the industry landscape; every device-specific example in TREF-0004 traces to a published archive record, not to a Perplexity answer.

## Uncertain claims left unresolved

- Device classifications in `docs/device-taxonomy-migration.md` §2 (e.g., IOLITE power as "torch (butane tank)") are editorial mappings to the new axes; where a manufacturer does not publish an axis attribute (e.g., exact conduction/convection ratio beyond the Solo III 80/20 claim), the axis value reflects the page's existing attributed language.
- The `radiant` heating-mechanism value is used for halogen/IR-driven units per the taxonomy definition; no archive record currently tags `radiant`, so the value is defined but unexercised in the corpus.
- No industry-consensus definition exists for "ball vape" as a class; the taxonomy defines it operationally via the component model rather than asserting a market definition.

## Validation results

| Command | Result |
| --- | --- |
| `python3 scripts/audit_device_taxonomy.py content` | PASS — 0 errors, 0 warnings on current corpus |
| `python3 -m unittest tests.test_device_taxonomy -v` | PASS — 12/12 |
| `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl --write` | PASS — regenerated id map (166 → 167 rows, adds `reference/TREF-0004`) |
| `python3 scripts/audit_markdown_links.py content` | PASS — all local links resolve |
| `SKIP_RELEASE_AUDIT=1 ./bin/validate_graph.sh` | PASS (see below) |

## Research corpus records consumed

- `research/devices/industry/manufacturer-universe/artifact.md` (+ dated export) — manufacturer/product-family landscape used to scope the axes and ball-vape component classes.
- `research/devices/industry/research-prompts/source/2026-08-08-perplexity.md` — the [MANUFACTURER] deep-research prompt's candidate graph edges (manufacturer→manufactured→device, device→member_of→family, device→heating_method→convection) informed the relation and axis conventions; Perplexity content was not treated as evidence.
- `research/devices/manufacturers/cannabis-hardware/artifact.md` — ball-vape lineage (coil/PID/bowl/stand vocabulary, ZenLeaf station-vs-head split) grounding the component model.
- `research/_index/manifest.jsonl`, `research/_index/inventory.md`, `research/_index/unresolved.md`, `research/README.md` — identity/provenance conventions (resolved before classification).

## Suggested next work

1. **Wire the audit into CI** and require 0 errors on PRs (already part of `validate_graph.sh`; CI inherits it).
2. **Ball-vape deep-dive wave**: split the FlowerPot/ZenLeaf trees into explicit head vs system records (B2, F22, Whisper/Bliss/Fusion stations) using the component model, adding "Component Role" rows.
3. **Delivery-mode coverage**: add delivery-mode tags (`stem`, `injector`, `water-tool`, `direct-draw`, `whip`) to device pages opportunistically so the axis is populated corpus-wide.
4. **Extend the vocabulary** to `specs/TSPEC-*` records when that collection is first populated, reusing the same axes.
5. **Registry alignment**: extend the audit to cross-check device tags against manufacturer slug changes as new manufacturer records land.
