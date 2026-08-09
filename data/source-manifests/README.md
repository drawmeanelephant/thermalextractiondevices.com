# Jurisdiction Source Manifests

Reusable, jurisdiction-parametric registry of official and high-value sources
for state cannabis research. Schema and tooling:

* Model: `scripts/ingest/sources.py` (SourceEntry / SourceManifest)
* CLI: `scripts/source_manifest.py` (`--stubs`, `--validate`, `--render STATE`)
* Schema doc: `docs/jurisdiction-evidence-model.md` § source manifest section

## Layout

| Path | Meaning |
| --- | --- |
| `california.json` | Researched California source inventory (12 sources) |
| `massachusetts.json` | Researched Massachusetts source inventory (12 sources) |
| `stubs/<state>.json` | **Un-researched** stubs for the other 49 jurisdictions |

## Policy

* A manifest with `"researched": true` must list sources, an updated date, and
  a research-status statement.
* Stub manifests declare `"researched": false` and contain **no sources** —
  they exist so adding State #3 starts from a known shape, not to claim
  research that was not performed.
* `--stubs` never overwrites a researched manifest.
* `--validate` fails on unknown source classes, missing authority/URL, and any
  stub that claims sources.
