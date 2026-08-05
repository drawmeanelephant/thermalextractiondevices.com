# Ingestion Audit — Repository State vs. Task Assumptions

Status: **completed** · Date: 2026-08-05 · Author: Freebuff ingestion agent

This document is the first deliverable of the Massachusetts Cannabis Control
Commission (CCC) ingestion task. The task prompt assumed a California DCC
ingestion implementation existed in this repository and asked that it be
refactored into shared machinery with Massachusetts added as the *second*
state. **That assumption is false for this repository.** This audit records,
with evidence, what actually exists, what this means for the work, and the
decisions taken as a result.

---

## 1. What the task prompt assumed exists

The prompt directed the agent to inspect, before changing anything:

```text
scripts/dcc_ingest.py        scripts/dcc_sync.py       scripts/ted_ids.py
scripts/ted-publish.sh       scripts/ted-build.sh      bin/validate_graph.sh
content/jurisdictions/       content/licenses/         content/organizations/
content/testing-laboratories/ content/recalls/         content/contaminants/
content/datasets/            content/requirements/     data/dcc/
metadata/id-map.jsonl
```

and to "inspect the latest California DCC ingestion commit" before working.

## 2. What actually exists (evidence)

**Git history (all refs, `git log --all --oneline`):**

```text
2ad7d56 feat: add automated Boris compiler resolution and provisioning system
d9018c9 feat: integrate Content Truck 01 payload (8 cultivars, 2 references, 4 guides, 3 includes, and evidence-structured indexes)
02cda0b feat: enable deterministic split-size RAG and context bundling in publish pipeline
10fa195 style: update theme to dark botanical aesthetic with self-hosted Inter font
ee98fd2 feat: add new collection categories to theme navigation sidebar and index
eadd7ba feat: scaffold Boris entity graph taxonomy and starter records
01a42d7 Update Cloudflare Pages project name to thermalextractiondevices and pass API tokens
4a22b6f Initialize Thermal Extraction Devices Boris static site architecture
```

There is **no commit** mentioning California, DCC, ingestion, licenses,
jurisdictions, or licensing anywhere in the repository history, including all
remote-tracking branches (`origin/main`, `origin/agent-1..4`).

**File inventory (verified by `ls`, `find`, and ripgrep):**

| Prompt path | Exists? | Reality |
| --- | --- | --- |
| `scripts/dcc_ingest.py` | No | Directory holds only `ted_ids.py`, `ted-build.sh`, `ted-publish.sh`, `ensure-boris.sh`, `clean-binaries.sh`, `test_ensure_boris.py`, `audit_markdown_links.py`, `audit_html_ids.py`, `cloudflare-build.sh` |
| `scripts/dcc_sync.py` | No | — |
| `data/dcc/`, `data/` | No | No `data/` directory at all |
| `content/jurisdictions/` … `content/requirements/` | No | Existing collections: botanicals, changelog, cultivars, devices, guides, includes, lab-results, law-and-use, manufacturers, products, reference, releases, safety, specs, terpenes |
| `metadata/id-map.jsonl` | Yes | 60 lines; only the 14 pre-existing collections |
| `metadata/id-policy.json` | Yes | Identity rules for the 14 pre-existing collections |

Ripgrep for `dcc`, `california`, `ingest`, `jurisdiction`, `license`
across the tree returned only one incidental match (a cultivar provenance
note mentioning California breeding).

## 3. What the repository actually is

`thermalextractiondevices.com` is a **production Boris static-site scaffold**
(8 commits, all linear):

* **Compiler**: Boris (`github.com/drawmeanelephant/boris`, `afterparty`
  branch, pinned commit `9505ec6`), Zig 0.16.0. Provisioned by
  `scripts/ensure-boris.sh` (checksummed download + pinned-commit build).
* **Theme**: `themes/cantilever/` (hardcoded navigation sidebar + search UI).
* **ID tooling**: `scripts/ted_ids.py` — deterministic form IDs per
  collection (`<collection>/<PREFIX>-NNNN`), collision detection, trunk
  discovery, migration map writer/validator. Prefixes are registered
  per-collection in this file.
* **Validation gate**: `bin/validate_graph.sh` → `ted_ids.py` →
  `boris check` → `ted-build.sh` (HTML build, sitemap, layout rules, HTML ID
  audit, `_boris/proof/checks.json`).
* **Publication**: `scripts/ted-publish.sh` → HTML, IR, RAG, Context,
  `llms.txt` exports.
* **Tests**: none beyond `scripts/test_ensure_boris.py` (Boris provisioning).
* **CI**: `.github/workflows/ci.yml` (validate+build) and `deploy.yml`
  (Cloudflare Pages deploy) both gate on `bin/validate_graph.sh`.

## 4. Answers to the audit questions the prompt posed

Because the California implementation does not exist, the prompt's audit
questions are answered against the repository as found:

1. **Which California functions are reusable?** None exist. The genuinely
   reusable machinery in this repo is the ID tooling (`ted_ids.py`) and the
   build/validation/publication shell scripts. The new shared ingestion
   package (`scripts/ingest/`) is built fresh and reuses those scripts by
   invocation, not by import.
2. **Which behavior is hardcoded to California?** None. The only
   jurisdiction-agnostic hardcoding is the collection→prefix table in
   `ted_ids.py`, which this task extends.
3. **Which files are generated versus editorial?** Currently all content is
   editorial. This task introduces generated content under new collections;
   `metadata/id-map.jsonl` continues to record editorial IDs, while generated
   IDs are persisted in `data/massachusetts-ccc/id-map.json`.
4. **How are stable IDs allocated?** By `ted_ids.py`: existing form IDs are
   preserved/normalized, missing ones allocated from the next unused
   `<PREFIX>-NNNN`. This task adds nine collection prefixes
   (`TJUR, TLIC, TORG, TSTL, TCNT, TDTS, TREQ, TSAD, TAFP`).
5. **Which raw/normalized artifacts are committed?** None today (no data
   tree). The new policy: only small durable records under
   `data/massachusetts-ccc/`; large raw/normalized files live under
   `var/ingest/massachusetts-ccc/`, gitignored.
6. **Is `dcc_sync.py` still needed?** It never existed; there is no competing
   California workflow to deprecate, and no second canonical path is created.
7. **Which tests/publication gates exercise ingestion output?** None did.
   This task adds a `tests/` suite and a privacy scan wired into the
   validation gate.

## 5. Decisions taken because of the discrepancy

* Massachusetts is implemented as the **first** state-backed ingestion in this
  repository, not the second. The "California regression" workstream reduces
  to *do not regress the existing Boris build/ID tooling*, which is covered by
  `ted_ids.py` validation, the Markdown-link audit, and the Boris graph build.
* The shared package layout from the prompt
  (`scripts/ingest/core.py, fetch.py, storage.py, schema.py, diff.py, ids.py,
  markdown.py, validation.py, states/…`) is adopted as specified; the
  `states/california.py` adapter is intentionally **not** created (nothing to
  port). `states/massachusetts.py` is the reference adapter.
* New collections (`jurisdictions, licenses, organizations,
  testing-laboratories, contaminants, datasets, requirements,
  safety-advisories, affected-products`) are added to the ID registry and the
  theme navigation.
* Privacy-sensitive fields found in real source schemas (EIN/TIN, business
  email/phone, full street and mailing addresses) are excluded from all
  generated Markdown; committed fixtures are scrubbed of these values.
* Large official datasets (testing results: ~70 MB + ~105 MB) are streamed and
  never committed; only aggregate statistics and schema reports are committed.

## 6. Sources verified during this audit (pre-implementation discovery)

All official Massachusetts CCC endpoints were probed live (see
`data/massachusetts-ccc/source-catalog.json` for the full catalog):

* Data catalog: `https://masscannabiscontrol.com/open-data/data-catalog/`
* 15 downloadable datasets under
  `https://masscannabiscontrol.com/resource/<slug>.csv|.json`
* Advisories: `https://masscannabiscontrol.com/news/public-health-and-safety-advisories/`
  (3 published advisories as of 2026-08-05)
* Testing-data update notices, e.g.
  `https://masscannabiscontrol.com/2026/03/3-19-2026-testing-data-update/`

---

## Addendum — California commit discovery (2026-08-05, reconciliation pass)

The maintainer reported that current `main` contains the California DCC
ingestion commit `3628c641af3d262825b11b0baa4db7a304556356` and directed a
reconciliation rebase. Evidence gathered in this worktree:

1. Worktree `HEAD` and `origin/main` both resolve to `2ad7d56`; there are **no
   commits on `origin/main` beyond the worktree base**.
2. `git rev-list --all` contains **0** occurrences of `3628c641…`;
   `git cat-file -t 3628c641…` fails ("could not get object info").
3. All agent branches (`origin/agent-1` … `origin/agent-4`) point at
   `2ad7d56` — no California work in any reachable ref.
4. `git ls-remote origin` fails: `'…/thermalextractiondevices.com/.'
   does not appear to be a git repository`; the path is outside the sandbox
   ("Operation not permitted" on direct inspection). `git fetch origin` and
   direct SHA fetch fail identically.

**Conclusion**: the California-containing `main` is not obtainable from this
environment. No rebase was attempted on an unreachable commit, and no
California implementation was fabricated. All Massachusetts work is preserved
uncommitted (test-only); theme/navigation changes were reverted per boundary
instructions; fixture-derived public content and durable records were deleted;
and a hard guard now prevents fixture/synthetic records from generating
publishable content. The reconciliation steps that remain are listed in
`docs/ingest/implementation-report.md` §2.
