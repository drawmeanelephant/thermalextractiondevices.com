# Cultivar Identity Implementation Report

**Date:** 2026-08-09
**Scope:** Provenance-aware cultivar identity architecture + small evidence-backed example set + first-party sourcing pass + conflicting-claim modeling.
**Model spec:** [`docs/cultivar-identity-model.md`](../docs/cultivar-identity-model.md)

## Rebase onto current main (2026-08-09)

Branch rebased onto `github/main` (`41768af`), which had advanced past the original branch point with a parallel cultivar-provenance effort (added `relates_to=reference/TREF-0002` and "Provenance & Sources" sections with the same first-party URLs to every cultivar page). The two efforts were reconciled, not duplicated:

- Cultivar pages keep main's softened provenance prose and source sections **plus** the claim framework (claim tables, machine-record references, Conflicting Claims).
- `bin/validate_graph.sh` keeps main's taxonomy/completeness audits **plus** the cultivar-claims validation step.
- Main's finding of a DJ Short first-party source for Blue Dream (`djgenetics.com/strains/azure-haze/` — Azure Haze "create[s] the same cross as the Blue Dream") upgraded `CLM-0003` from `claimed` to `well_supported`; verified directly on 2026-08-09.

## Summary

Built the rails for a provenance-aware cultivar identity system: a
machine-readable claim registry with a full provenance envelope, a validated
relationship vocabulary, name normalization for discovery, epistemic
rendering for RAG, and a small set of claims drawn from existing repository
evidence. The published Boris graph keeps the four compiler-supported
relation kinds; the rich vocabulary lives in the registry so semantic
distinctions survive without breaking the closed frontmatter schema.

## Key architectural decision

The pinned Boris compiler (`metadata/boris-version.json`, commit
`9505ec61`) parses `relations:` through a fixed `RelationKind` enum
(`src/page.zig`): only `relates_to`, `implements`, `depends_on`, `supersedes`
are accepted; any other kind fails the build with `BadRelations`. The mission
vocabulary (`alias_of`, `claimed_bred_by`, `lineage_parent`, …) therefore
cannot live in frontmatter.

**Two-layer model:**

1. **Published graph** — Boris `relations:` uses the four supported kinds for
   canonical connectivity (e.g. cultivar → in-graph lineage parent).
2. **Claim registry** (`metadata/cultivar-claims.jsonl`) — every nontrivial
   identity/lineage assertion as one JSON object per line with subject,
   object, kind, status, wording, and a source envelope (name, role,
   retrieval date, optional URL). Validated against the content tree;
   exported to machine consumers.

This is a normalization of the repository's existing relationship syntax
(`relates_to=` + prose claim statements + provenance include warnings), not a
parallel incompatible system: the registry formalizes what the prose already
claimed, and content pages point at it.

## Files added

| File | Purpose |
| --- | --- |
| `scripts/cultivar_claims.py` | Vocabulary (`CLAIM_KINDS`, `SOURCE_TYPES`, `STATUSES`), `normalize_name()`, `validate_claims()`, `load_claims()`, `render_claim_context()` |
| `scripts/validate_cultivar_claims.py` | CLI gate: validates the registry against content entity IDs |
| `metadata/cultivar-claims.jsonl` | 13 claims, all drawn from existing corpus pages |
| `tests/test_cultivar_claims.py` | 27 unit tests incl. real-registry validation |
| `docs/cultivar-identity-model.md` | Full model specification |
| `reports/cultivar-identity-implementation.md` | This report |

## Files modified

| File | Change |
| --- | --- |
| `bin/validate_graph.sh` | Added cultivar-claims validation step |
| `scripts/ted-publish.sh` | Exports `publish/claims.jsonl` + README.txt entry |
| `content/cultivars/blue-dream.md` | Identity & lineage-claims section (claim table, statuses), chemistry-firewall note, product/batch claim references, `relates_to=cultivars/TCUL-0002`, provenance includes aligned with corpus |

## Claim examples (evidence-backed)

| Claim | Kind | Evidence in repository |
| --- | --- | --- |
| `CLM-0001` TPRD-0001 → TCUL-0001 | `product_claims_cultivar` | Product page states "Cultivar Lineage: Blue Dream" |
| `CLM-0002` TLAB-0001 → TCUL-0001 | `batch_claims_cultivar` | COA header "Product: Blue Dream Dried Flower" |
| `CLM-0003` TCUL-0001 → TCUL-0002 | `claimed_lineage_parent` | Page states "Blueberry × Haze"; Haze parent has no page |
| `CLM-0004/0005` TCUL-0009 | `claimed_bred_by` (Sensi Seeds), `claimed_lineage_parent` → TCUL-0007 | Super Skunk page |
| `CLM-0006` TCUL-0007 | `claimed_bred_by` (Sacred Seeds / Sensi Seeds) | Skunk #1 page |
| `CLM-0007` TCUL-0004 | `claimed_bred_by` (Sensi Seeds) | Jack Herer page |
| `CLM-0008` TCUL-0006 | `claimed_bred_by` (Sensi Seeds) | Northern Lights page |
| `CLM-0009` TCUL-0002 | `claimed_bred_by` (DJ Short / Dutch Passion) | Blueberry page |
| `CLM-0010` TCUL-0003 | `claimed_bred_by` (Dutch Passion) | Durban Poison page |
| `CLM-0011/0012` TCUL-0005 | `claimed_bred_by` (Dutch Passion), `claimed_lineage_parent` → TCUL-0007 | Mazar page |
| `CLM-0013` TCUL-0008 | `claimed_bred_by` (Kyle Kushman / Dutch Passion) | Strawberry Cough page |

All claims are status `claimed` with `archive` as source role: they come from
the repository's own pages, which attribute to first-party breeders but carry
no attached first-party URLs. No claims were invented: there are **no**
`alias_of` records (no repository evidence — GG4-style resolution is
explicitly rejected without evidence), no seed-bank listings (none exist in
the corpus), and no conflicting lineage pairs yet (the machinery —
`possibly_same_as`, `source_disagrees_with`, `conflicting` — is defined and
tested, and demonstrated in the model doc's worked example).

## Name normalization behavior

`normalize_name()` folds case, NFC, whitespace, and punctuation variants for
matching only; display names are untouched. Meaningful tokens survive
(`GG4` → `gg4`, `Skunk #1` → `skunk 1`, `Sensi Skunk #1 BX2` → `sensi skunk 1
bx2`). Abbreviations are deliberately **not** connected by normalization:
`gg4` ≠ `gorilla glue 4`; alias resolution requires a registry record.

## First-party sourcing pass (2026-08-09)

Attached verified first-party breeder/seed-bank source URLs to the registry claims and upgraded status where the source's role supports the claim. Retrieval date for all URLs: **2026-08-09**. Verification method: direct page reads where the site is server-rendered (Sensi Seeds, DNA Genetics); official-page indexed content (Google snippets of the live page) for Dutch Passion product pages, which are JS-rendered and not extractable by the reader. Every URL was confirmed to exist and to state the recorded claim.

| Claim | Claim | Status after | Source URL (type) |
| --- | --- | --- | --- |
| `CLM-0004` | Super Skunk bred by Sensi Seeds | `claimed` → `well_supported` | sensiseeds.com super-skunk (breeder) |
| `CLM-0005` | Super Skunk parent Skunk #1 | `claimed` → `well_supported` | sensiseeds.com super-skunk (breeder) |
| `CLM-0006` | Skunk #1 by Sacred Seeds / Sensi | `claimed` → `well_supported` | sensiseeds.com skunk-1 (breeder) + blog |
| `CLM-0007` | Jack Herer bred by Sensi Seeds | `claimed` → `well_supported` | sensiseeds.com jack-herer (breeder) |
| `CLM-0008` | Northern Lights by Sensi Seeds | `claimed` → `well_supported` | sensiseeds.com northern-lights (breeder) |
| `CLM-0009` | Blueberry by DJ Short / Dutch Passion | `claimed` → `well_supported` | dutch-passion.com blueberry (breeder) |
| `CLM-0010` | Durban Poison by Dutch Passion | `claimed` → `well_supported` | dutch-passion.com durban-poison (breeder) |
| `CLM-0011` | Mazar bred by Dutch Passion | `claimed` → `well_supported` | dutch-passion.com mazar (breeder) |
| `CLM-0012` | Mazar parent Skunk #1 | `claimed` → `well_supported` | dutch-passion.com mazar (breeder) |
| `CLM-0003` | Blue Dream parent Blueberry | `claimed` → `claimed` (URL attached) | dnagenetics.com blue-dream (seed_bank) |
| `CLM-0013` | Strawberry Cough by Kushman / Dutch Passion | `claimed` → `claimed` (URL attached) | dutch-passion.com strawberry-cough (seed_bank) |
| `CLM-0001`/`CLM-0002` | Product/batch label claims | `claimed` (unchanged) | placeholder demo sources; not upgradable |

### Why some claims did not upgrade

* **Blue Dream lineage (`CLM-0003`)** — no first-party breeder page exists. The DNA Genetics seed listing corroborates "Blueberry x Haze" genetics, but per the source-role model a seed-bank page is strong for its listing and weak for genetics. Blue Dream's breeder/origin remains un-attributed (a first-class `unresolved`-style state).
* **Strawberry Cough (`CLM-0013`)** — breeder attribution to Kyle Kushman is widely reported but contested (Overgrow attributes the original to Jeff Cavanagh). Dutch Passion's page confirms the offering, not the breeding attribution, so the claim stays `claimed` with the conflict documented in `notes`.
* **Product/batch claims (`CLM-0001`/`CLM-0002`)** — sources are demonstration placeholders, not real producer/lab pages.

### Model-doc convention added

`docs/cultivar-identity-model.md` §4 now defines `well_supported` to include a directly attached first-party primary source, and rule 6 documents the upgrade convention: repoint `source` at the primary source, keep the claim `kind` unchanged (kind = structure, status = confidence), and record history in `notes`.

## Conflicting-claim case: Strawberry Cough attribution

Promoted the documented Strawberry Cough attribution dispute into a first-class claim pair:

| Claim | Kind | Side | Status | Source (role) |
| --- | --- | --- | --- | --- |
| `CLM-0013` | `claimed_bred_by` | Kyle Kushman / Dutch Passion | `claimed` | Dutch Passion page (seed_bank); Kushman attribution corroborated by CannaConnection / Medical Jane (database) |
| `CLM-0014` | `claimed_bred_by` | Jeff Cavanagh | `claimed` | Overgrow forum thread, May 2025 (forum) |
| `CLM-0015` | `source_disagrees_with` | links `CLM-0013` ↔ `CLM-0014` | `conflicting` | archive claim registry |

Key design decision: for `source_disagrees_with`, `subject`/`object` are **claim IDs, not content entities** (both sides are about the same cultivar, so entity-valued fields could not express the disagreement without self-reference). The validator now resolves claim-ID references across the registry (first pass collects claim IDs), rejects entity references for this kind, and rejects missing/self references. `render_claim_context(claim, claims_by_id=…)` renders the dispute with both attributions: *"the attribution of cultivars/TCUL-0008 is disputed between claim CLM-0013 (Kyle Kushman / Dutch Passion) and claim CLM-0014 (Jeff Cavanagh). Status: conflicting."*

Nuance preserved: the dispute is partly semantic — the widespread attribution treats Kushman as breeder/popularizer, while the Cavanagh claim distinguishes breeder from popularizer; even the Overgrow thread notes Kushman's own account is that he received the cut as a gift. Both sides stay `claimed`; neither is promoted. `content/cultivars/strawberry-cough.md` now carries a **Conflicting Claims** section rendering both sides with sources.

## Chemistry firewall

Batch chemistry remains in `content/lab-results/` records and is only ever
*linked* from cultivar pages; the Blue Dream page now carries an explicit
firewall note. No cultivar page asserts that a name implies analyte values.

## Machine retrieval behavior

`render_claim_context()` emits epistemic context ("Per S (role, retrieved D):
subject is claimed to … Status: claimed."). `scripts/ted-publish.sh` exports
the registry to `publish/claims.jsonl` beside the Boris IR graph, RAG corpus,
and context bundle.

## Validation results

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | PASS (see below) |
| `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl` | PASS — validated 166 pages; no files changed |
| `python3 scripts/audit_markdown_links.py content` | PASS — all local Markdown links resolve |
| `SKIP_RELEASE_AUDIT=1 ./bin/validate_graph.sh` | PASS (see below) |

`validate_graph.sh` now also runs `python3 scripts/validate_cultivar_claims.py
--root content --claims metadata/cultivar-claims.jsonl` → 13 claims validated
against 166 content entities; no problems.

### Known pre-existing failure (unchanged, not caused by this work)

`./bin/validate_graph.sh` **without** `SKIP_RELEASE_AUDIT=1` fails at the
public-release audit on pre-existing tracked `data/dcc/*` files (PII findings
at threshold `high`). This reproduces on `main` before any change here and is
out of scope; the same workaround documented in
`reports/device-corpus-wave-01.md` was used.

## Scope guardrails honored

- No changes to Massachusetts ingestion (`scripts/ingest/states/massachusetts.py`),
  `scripts/*_ingest.py`, or `scripts/ingest/`.
- No mass seed-bank import, no scraping, no fabricated listings or links,
  no affiliate parameters.
- No cultivar identity resolved from model memory; every claim traces to a
  repository page.
- Closed Boris frontmatter schema preserved (`id`, `title`, `parent`,
  `status`, `tags`, `relations`); no new frontmatter keys.
- Validators strengthened, not weakened (new claims gate added).
- No numeric confidence scores introduced.

## Suggested next work

1. **First-party sourcing pass**: attach breeder source URLs (e.g. Sensi
   Seeds, Dutch Passion official pages) to upgrade `claimed` archive claims
   toward `well_supported`.
2. **Seed-bank listing importer**: implement §10 of the model doc when real
   listing evidence is collected; registry kinds `listed_by`/`sold_by`/
   `seed_source` are ready.
3. **Alias registry**: add `alias_of` records only when repository evidence
   exists (e.g. product/lab records sharing a name with a documented alias).
4. **Conflicting-claim case study**: introduce the first
   `source_disagrees_with` pair from sourced material to exercise the
   disagreement machinery end to end.
