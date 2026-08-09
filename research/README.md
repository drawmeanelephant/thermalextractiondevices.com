# Thermal Extraction Devices — Research Corpus

Normalized, provenance-preserving research library for **thermalextractiondevices.com**. Built from 195 research records — 142 Perplexity deep-research exports, 44 structured artifacts, and 9 archived-redundant files (research date: 2026-08-08).

> **Packaging note:** only `README.md` and the `_index/` files below are tracked in git. The
> 195 corpus files themselves (e.g., `compounds/terpenes/<slug>/`, `devices/…`) are kept
> out-of-band in the main worktree and hash-verified against `_index/manifest.jsonl`; see
> `reports/research-corpus-quality-audit.md` (finding M-2) and `reports/terpene-research-audit.md`.
> Content pages that cite `research/…` paths are referencing this corpus, which downstream
> agents must mirror from the main worktree to resolve.

## Directory conventions

```text
artifact.md
    = structured research result (agent-ready report)

source/YYYY-MM-DD-perplexity.md
    = raw/detailed research export and provenance
    (original prompt, Perplexity answer/context, research date,
     conversation metadata, model metadata, source list,
     search snippets, provenance trail)

source/YYYY-MM-DD-perplexity-02.md
    = a second, independent research run for the same subject

supplemental/
    = additional independent research

_archive/redundant/
    = confidently redundant material preserved temporarily

_archive/superseded/
    = older replaced artifacts

_archive/unresolved/
    = material whose identity/classification needs human review
```

Every original file appears exactly once in `_index/manifest.jsonl`, with its original path, SHA-256, byte size, canonical subject, aliases, research role, and disposition. File moves/renames preserve content byte-for-byte (verified by hash).

## Top-level layout

```text
research/
├── README.md
├── _index/          manifest.jsonl, inventory.md, duplicate-groups.md, unresolved.md,
│                    ingestion-queue.md (verification/ingestion work queue)
├── devices/
│   ├── manufacturers/<slug>/   artifact.md + source/ (one folder per manufacturer)
│   └── industry/               cross-manufacturer device-industry research
├── compounds/
│   ├── terpenes/<slug>/
│   ├── cannabinoids/<slug>/
│   └── other/                 aroma chemistry, flavonoids, volatile sulfur compounds, ...
├── cannabis/          cultivar-identity, chemotype-analysis, batch-variability,
│                      laboratory-comparability, post-harvest, thermal-aerosol,
│                      terpene-cooccurrence, effects-evidence
├── jurisdictions/     united-states/...
└── _archive/          redundant/, superseded/, unresolved/
```

## Identity & provenance rules

- **Subjects are determined from document content** (H1, prompt, canonical names, domains, source URLs) — never from truncated or generic filenames.
- **Aliases** (e.g. EpicVape/Epickai, XMAX/TopGreen, Smiss/Flowermate, 7th Floor/Elev8) are recorded in the manifest; related brands are **not** collapsed unless the research itself supports the corporate relationship.
- **Chemically distinct entities are never merged** (THCA ≠ THC, CBGA ≠ CBG, THCVA ≠ THCV, α-pinene ≠ β-pinene, cis/trans and enantiomer distinctions preserved inside documents).
- **Duplicates** are classified by SHA-256 / normalized-text comparison and archived, not deleted.
- **Independent research runs for the same subject are kept** as `source/YYYY-MM-DD-perplexity(-02).md`.

## Provenance chain

These files are **research inputs**, not primary evidence. The intended chain is:

```text
research corpus → source ledger → primary source → normalized site claim / graph edge
```

> **Research reports are discovery and synthesis inputs. Downstream publication must verify material claims against the primary sources referenced by the reports.**

## Tooling

The reusable normalization pipeline lives in `scripts/` (see `scripts/README.md`): scan → identify → compare → organize → index → validate.

## Quick reference

- `_index/manifest.jsonl` — machine-readable inventory (one JSON object per original file; carries `verification_status`, `primary_source_coverage`, `ingestion_status`, `target_collections`, `priority`)
- `_index/inventory.md` — counts, manufacturer coverage, research gaps
- `_index/duplicate-groups.md` — duplicate classification and archive candidates
- `_index/unresolved.md` — ambiguous files and how they were resolved
- `_index/ingestion-queue.md` — actionable ingestion/verification work queue by subject area
- `_index/verification-ledger.md` — primary-source verification results and errata for the Priority-1 subjects
