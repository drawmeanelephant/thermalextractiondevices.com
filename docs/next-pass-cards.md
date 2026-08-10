# Next-Pass Cards: Archive Integrity and Scaling

**Status:** Ready-to-dispatch planning runbook  
**Prepared:** 2026-08-09  
**Source:** fresh audit follow-up recommendations, repository inspection, and
current local validation

This document turns the recent audit recommendations into bounded agent cards.
It is a dispatch plan, not a replacement for `docs/roadmap.md` or
`docs/status.md`. Update the relevant status lane when a card lands; do not use
this document as a daily task log.

The recurring instruction for every card is:

> Audit first. Preserve working semantics. Make the smallest coherent change.
> Add validation so the bug cannot quietly return.

## Current evidence snapshot

Re-check these values at dispatch time. They are a baseline for the checkout
used to prepare this document, not permanent facts:

| Surface | Observed baseline | Consequence |
| --- | ---: | --- |
| Checkout | `codex/publish-bundled-rag` at `8c9dee6` | Audit reports must name the exact source SHA they inspect |
| Canonical pages | 417 | The previous audit's 442-page baseline is not this checkout |
| HTML/TED crosslink edges | 1,404 | Derived navigation is richer than Boris-native export |
| Durable COA records | 0 | `metadata/coa-records.jsonl` is empty despite `TLAB-0002` being published |
| Device taxonomy warnings | 24 | Warnings need classification, not vocabulary inflation |
| Fresh RAG export | 417 pages / 697 Boris relations | Current export is structurally fresh but not semantically equivalent to HTML |
| Tests discovered | 301 | CI currently does not invoke the test suite; local sandbox blocked one socket test |
| Historical DCC blobs | Reachable | The documented history-cleanup plan is not executed |

The current working tree is expected to remain clean before dispatch. Generated
`dist/`, `publish/`, compiler binaries, caches, and local reports are not card
deliverables unless a card explicitly asks for a report that belongs in git.

## Global dispatch contract

Every agent card must follow these rules:

1. Start with `git status --short --branch` and record the exact branch, source
   SHA, and relevant remote refs.
2. Read the nearby content, metadata, tests, and governing documentation before
   editing. Preserve unrelated work in progress.
3. Keep Boris as the compiler. Do not introduce Astro, Node, React, another
   static-site generator, or a replacement graph architecture.
4. Use only the supported content frontmatter fields: `id`, `title`, `parent`,
   `status`, `tags`, and `relations`. Put additional machine data in an
   existing or deliberately documented metadata format; do not smuggle new
   fields into records.
5. Never silently rename, renumber, reuse, or hand-edit canonical IDs. Use the
   approved ID tooling and migration map.
6. Do not commit generated output, raw/private source snapshots, credentials,
   local paths, or compiler binaries.
7. Do not force-push or rewrite shared history from a normal implementation
   branch. Card P01 is an operations-controlled exception with a separate
   backup, approval, and collaborator-recovery procedure.
8. Add or update tests/validators for every new machine-decidable rule. Do not
   weaken a test or hide a finding solely to obtain green CI.
9. Run the proportional checks for the card and finish with
   `./bin/validate_graph.sh`. If an unrelated pre-existing release gate fails,
   report it separately with the exact output and exit status.
10. Deliver a short receipt: files changed, commands run, results, unresolved
    evidence gaps, and whether the next card is unblocked.

## Wave plan

Do not launch all cards simultaneously. The same seams recur in multiple cards,
and simultaneous edits would produce avoidable merge conflicts or inconsistent
models.

| Wave | Cards | Purpose | Dispatch rule |
| --- | --- | --- | --- |
| 0 | Coordination preflight | Pin the audit baseline and claim ownership | Run before every card; no implementation yet |
| 1 | P01, P02, P03, P06, P07, P08 | Publication truth, privacy, and basic gates | P01 execution requires maintainer approval; P03 is fact-finding before P04 |
| 2 | P04, P05, P11, P15 | Temporal and canonical identity controls | P15 is the gate before new state-ingest allocation; do not migrate IDs by string matching |
| 3 | P09, P10, P14, P17 | Determinism, machine exports, ingest boundaries, provenance | P10 consumes the settled COA/graph semantics; P14 consumes the allocator decision |
| 4 | P12, P13, P16, P18, P19 | Editorial, device, source-health, cultivar, and production cleanup | Prefer independent branches; network-heavy P16/P19 should not block local content work |
| 5 | P20 | Permanent integrity gate | Run after preceding cards land and their intentional findings are dispositioned |

### Safe parallel sets

These can normally run in parallel if each agent owns a separate branch and
avoids shared files:

- P02 thermal claims, P03 jurisdiction fact-finding, P07 test-CI inventory,
  P08 Boris pin audit, and P13 device-warning classification.
- P06 COA materialization and P15 allocator analysis, provided neither agent
  changes chemical IDs or global allocation rules without coordination.
- P12 trunk copy, P16 source-health design, and P19 production discovery audit
  after their reports are based on the same source SHA.

Do not run these implementation pairs independently:

- P03 with P04 on the same jurisdiction files.
- P05 with P06 on compound mappings or COA-derived relations.
- P07 with P08 on the same workflow files without one integrator.
- P11 with P14/P15 on organization or ID allocation semantics.
- P10 with P20 before the export contract is settled.

## Card index

| Card | Title | Wave | Type | Primary dependency |
| --- | --- | ---: | --- | --- |
| P01 | Finish Git-history privacy cleanup | 1 | Operations / history | Maintainer sign-off and full backup |
| P02 | Correct cannabinoid thermal-property claims | 1 | Content + validator | None |
| P03 | Verify current law across jurisdictions | 1 | Evidence sweep | Authoritative sources and network access |
| P04 | Add effective-date semantics | 2 | Model + validator | P03 findings |
| P05 | Canonicalize chemical/analyte identity | 2 | Identity migration | P15 allocation rules; coordinate with P06 |
| P06 | Materialize the verified COA | 1 | Data model + graph | Existing COA model |
| P07 | Put the unit tests in CI | 1 | CI | Test inventory |
| P08 | Pin Boris identically everywhere | 1 | Toolchain + CI | `metadata/boris-version.json` |
| P09 | Prove reproducible static builds | 3 | Build verification | P08 |
| P10 | Make RAG exports semantically equivalent | 3 | Machine export | P06, P08, and crosslink semantics |
| P11 | Canonicalize organizations | 2 | Identity resolution | P15; source evidence |
| P12 | Correct stale collection-trunk prose | 4 | Editorial / light automation | P02/P03/P06 content state |
| P13 | Resolve device-taxonomy warnings | 4 | Vocabulary + content | Existing taxonomy audit |
| P14 | Define the state-ingest publication contract | 3 | Ingest architecture | P01/P15 privacy and ID boundaries |
| P15 | Reconcile global and state ID allocation | 2 | Allocation control | Current ID-map inventory |
| P16 | Add external source-health auditing | 4 | Scheduled audit | URL inventory and HTTP policy |
| P17 | Strengthen provenance grading | 3 | Evidence model | Existing labels plus P02/P03 findings |
| P18 | Prevent cultivar chemotype overclaiming | 4 | Content + validator | P06 and provenance semantics |
| P19 | Clean production discovery and legacy URLs | 4 | Deployment audit | Direct origin access |
| P20 | Turn the audit into a permanent gate | 5 | Consolidated CI | Preceding validators and dispositions |

---

## Wave 1 — Publication truth and hardening

### P01 — Finish the Git-history privacy cleanup

**Type:** operations-controlled history task  
**Status:** ready for preflight; execution requires maintainer approval  
**Scope:** `data/dcc/**` history, release audits, privacy documentation, and
possibly author-attribution history

**Objective:** Remove prohibited historical California DCC registry blobs from
all intended public refs, while preserving the current tree and useful history
as far as practical.

**Agent work:**

- Inspect all refs and reachable blobs from a clean/mirror-capable checkout.
- Identify exact DCC payloads and sensitive fields; do not rely on an earlier
  count or commit boundary.
- Prepare a rewrite plan using
  [`docs/history-cleanup-plan.md`](history-cleanup-plan.md).
- Separately disposition the `beau@boorman.tech` history-email findings: either
  document that public author attribution is allowed or prepare a separate
  mailmap/history decision. Do not silently combine unrelated rewrites.
- Update the checklist only after the final state is proven.

**Non-goals:** deleting current-tree files again, changing audit suppressions to
make the report green, or force-pushing from an ordinary agent branch.

**Definition of done:**

- Full mirror/bundle backup exists and is verified.
- Intended public refs no longer reach the prohibited DCC blobs.
- Current-tree content is unchanged except explicitly approved documentation.
- `LARGE-004` and historical sensitive-content findings are absent without
  suppressions.
- The post-rewrite build and graph validation pass.
- A maintainer receives exact ref changes, recovery instructions, and residual
  GitHub/fork/cache risks before any force-update.

**Required receipt:** exact refs inspected, blob IDs/paths removed, backup
locations, verification commands, and collaborator instructions. This card is
not complete merely because the working tree is clean.

### P02 — Correct cannabinoid thermal-property claims

**Type:** scientific content audit plus regression validator  
**Status:** ready  
**Scope:** `content/cannabinoids/`, relevant shared includes, thermal-property
validators/tests

**Objective:** Correct Δ9-THC and audit every cannabinoid claim involving
boiling point, vapor pressure, evaporation, decomposition, decarboxylation, or
thermal stability.

**Agent work:**

- Inventory every thermal-property statement before editing.
- Inspect the cited primary literature or authoritative database for each
  number, including pressure and measurement conditions.
- Label values as measured, extrapolated, predicted, secondary, or unsupported.
- Correct `content/cannabinoids/d9-thc.md` without replacing one unqualified
  number with another.
- Preserve the rule that device setpoint, sample temperature, and thermodynamic
  boiling point are different quantities.
- Put reusable caveats in shared includes when that improves consistency.

**Non-goals:** expanding into unrelated medical/biological claims or treating
marketing temperature charts as thermodynamic data.

**Definition of done:**

- Every changed value has condition-aware provenance.
- No atmospheric boiling claim is left without pressure/source qualification.
- An automated audit flags suspicious unconditioned atmospheric claims.
- Known failure cases have tests/fixtures.
- A report lists weak or intentionally unresolved constants.

**Checks:** targeted content audit, unit tests for the validator, Markdown link
audit, and `./bin/validate_graph.sh`.

### P03 — Verify current law across all jurisdiction profiles

**Type:** authoritative evidence sweep  
**Status:** ready; network-heavy  
**Scope:** `content/jurisdictions/*.md`, jurisdiction source metadata, findings
report

**Objective:** Audit every jurisdiction profile for current factual accuracy
before designing a new temporal model.

**Priority claims:** possession, medical status, home cultivation, retail
operation, licensing, regulator identity, future-effective changes, testing
regimes, and public data availability.

**Agent work:**

- Treat NJ, Virginia, and Washington as leads, not assumed answers.
- Prefer regulator, statute, regulation, or official dataset sources.
- Separate current law from enacted-but-not-effective, proposed, pending, and
  repealed material.
- Correct only claims actually checked; do not bulk-refresh retrieval dates.
- Produce a severity-grouped report: blocking factual error, material
  uncertainty, stale source, or editorial improvement.

**Non-goals:** redesigning IDs, adding a temporal schema in the same pass, or
pretending a profile is fully verified when the public source is unclear.

**Definition of done:**

- Every jurisdiction has a review disposition.
- Each changed claim has an authoritative source and retrieval date.
- Partially verified profiles are explicitly listed.
- The next model card, P04, has concrete examples and impossible-state cases
  to encode.

### P06 — Materialize the verified COA as a machine record

**Type:** data-model and graph integration  
**Status:** ready  
**Scope:** `metadata/coa-records.jsonl`, `scripts/coa_model.py`,
`scripts/crosslinks.py`, COA validators/tests, `TLAB-0002`

**Objective:** Close the gap between the published verified Dragonberry COA
page and the durable registry that drives typed measurement edges.

**Agent work:**

- Inspect the existing model and schema before choosing a serialization path.
- Convert the verified report into a canonical durable record.
- Preserve exact printed values/units and all result states: ND, below LOD,
  below LOQ, missing, not tested, numeric, and calculated quantities.
- Resolve only legitimate canonical compounds; retain source-native names when
  identity is not safely resolved.
- Keep `TLAB-0001` synthetic/demo data out of real-data derivations.
- Add a parity validator: every published verified TLAB page has one durable
  record, and every durable verified record resolves to one page.

**Non-goals:** redesigning the COA model, inferring omitted measurements, or
attaching chemistry directly to a cultivar.

**Definition of done:**

- `metadata/coa-records.jsonl` contains the verified record(s) in schema-valid
  form.
- Crosslink output includes measurement, laboratory, product, and analyte
  edges with evidence traces.
- Parity and synthetic-data exclusion tests pass.
- The documented path can scale to the next 100/10,000 records.

**Coordination:** If P05 later migrates a compound identity, it must include a
COA-record mapping update rather than silently invalidating this card.

### P07 — Put the unit tests in CI for real

**Type:** CI gate  
**Status:** ready; coordinate with P08 on workflow files  
**Scope:** `.github/workflows/ci.yml`, test commands, contributor docs

**Objective:** Make the actual repository test suite a required CI gate.

**Agent work:**

- Inventory unittest/pytest/integration tests and current skips.
- Add the appropriate command(s) to blocking CI; ensure nonzero exit codes fail
  the job.
- Separate fast tests from build/integration checks if that reduces duplication.
- Investigate the local socket-test failure as an environment issue; do not
  weaken its assertions merely to get green.
- Report discovered, executed, passed, failed, and skipped counts.

**Definition of done:**

- CI executes the suite on the release/PR path.
- A deliberately failing test is demonstrably capable of failing CI, or the
  workflow configuration makes that mechanically obvious.
- Local instructions match the CI command.
- New validators from later cards have a designated test location.

### P08 — Pin Boris identically everywhere

**Type:** toolchain and workflow determinism  
**Status:** ready; coordinate with P07 on workflow files  
**Scope:** `metadata/boris-version.json`, `scripts/ensure-boris.sh`, CI/deploy
workflows, `SECURITY.md`, build documentation

**Objective:** Make local, CI, and deploy builds use the exact same Boris
commit, not a moving `afterparty` branch.

**Agent work:**

- Establish `metadata/boris-version.json` as the single source of truth.
- Make workflows fetch/checkout that commit and fail loudly if it cannot be
  resolved.
- Preserve Zig version/checksum verification.
- Record the compiler commit in build/proof metadata where practical.
- Add a drift check that catches workflows returning to floating branches.
- Correct SECURITY/documentation contradictions.

**Non-goals:** upgrading Boris or changing compiler behavior.

**Definition of done:**

- CI and deploy consume the configured commit SHA.
- No workflow depends on a moving Boris branch for build selection.
- Local provisioning and CI agree on repository, SHA, and Zig version.
- The drift test fails on a deliberately floating configuration.

---

## Wave 2 — Temporal and canonical identity controls

### P15 — Reconcile global and state-specific ID allocation

**Type:** allocation/process control  
**Status:** gate for new state ingestion; analysis ready  
**Scope:** `scripts/ted_ids.py`, `metadata/id-map.jsonl`, state-specific maps,
`metadata/id-policy.json`, ingestion operator guidance, collision tests

**Objective:** Establish one authoritative canonical allocator while preserving
source-native and provisional state IDs.

**Agent work:**

- Map every current allocation mechanism and its authority.
- Classify IDs as source-native, provisional, or canonical archive IDs.
- Design the smallest deterministic reservation/collision mechanism for
  parallel state agents.
- Preserve all existing canonical IDs and source identifiers.
- Add collision tests that simulate concurrent state allocations.
- Update operator guidance with the exact allocation procedure.

**Non-goals:** renumbering existing entities for cosmetic consistency or
hand-editing `metadata/id-map.jsonl`.

**Definition of done:**

- Two state agents cannot silently allocate the same canonical ID.
- The migration map remains authoritative and valid.
- New ingestion work has a documented preflight gate.
- P05 and P11 can perform migrations without inventing competing IDs.

### P04 — Add effective-date semantics to law and regulation records

**Type:** compatible model and validator  
**Status:** blocked on P03 findings; design may begin  
**Scope:** jurisdiction/law/requirement metadata, render helpers, validators,
authoring guidance, tests

**Objective:** Represent current, future, proposed, pending, repealed, and
unknown regulatory states without turning future law into present tense.

**Agent work:**

- Inspect existing source metadata and legal/evidence patterns first.
- Reuse existing fields/patterns where possible. Do not add arbitrary content
  frontmatter keys merely because they are convenient.
- Support state, effective date where known, source date, and retrieval date in
  a documented compatible layer.
- Define impossible combinations and stale-state behavior.
- Migrate only records where temporal state changes interpretation.

**Definition of done:**

- P03’s NJ/Virginia-style examples render correctly.
- Validation catches a future state whose effective date is past unless marked
  stale/reviewed.
- Existing IDs and URLs remain stable.
- Authoring guidance tells future agents how to distinguish law states.

### P05 — Canonicalize chemical and analyte identity

**Type:** identity audit and migration  
**Status:** analysis ready; implementation follows P15 and COA coordination  
**Scope:** chemical/analyte content, ingest mappings, `metadata/id-map.jsonl`,
crosslinks, aliases/migration metadata, tests

**Objective:** Keep one canonical chemical identity while representing
jurisdiction-specific testing roles separately.

**Agent work:**

- Inventory cannabinoids, terpenes, contaminants, botanicals, and analyte
  records.
- Compare names, CAS, PubChem IDs, synonyms, stereochemistry, isomers, and
  acid/neutral state.
- Distinguish real duplicates from legitimate near-names.
- Design role/context representation for required analyte, potency analyte,
  contaminant-panel member, and action-limit subject.
- Preserve source labels and create aliases/redirects before deprecating any
  public ID.
- Add uniqueness validation and tests for THC, THCA, Lead, and a legitimate
  nonduplicate.

**Non-goals:** collapsing genuine isomers, stereoisomers, acid/neutral forms,
or chemically distinct homologues.

**Definition of done:** duplicate report, migration map, repaired relations,
COA/source mapping updates, no broken public URLs, and a validator preventing
the same chemical from being minted twice without an explicit exception.

### P11 — Canonicalize organizations before more states arrive

**Type:** identity resolution  
**Status:** blocked on P15 for migrations; candidate inventory ready  
**Scope:** organizations, manufacturers, testing labs, licenses, source names,
alias/equivalence metadata, duplicate-candidate audit, tests

**Objective:** Separate canonical organizations from locations, licenses, DBAs,
and source-specific spellings.

**Agent work:**

- Inventory likely variants such as Holistic Industries, Enlite, ARL Healthcare,
  and 6 Bricks, treating them as candidates rather than known duplicates.
- Match using official identifiers, license numbers, jurisdiction, DBA names,
  and permitted internal matching fields.
- Preserve source names exactly as reported.
- Require evidence for merges; fuzzy spelling alone is insufficient.
- Add a future-ingest duplicate-candidate audit and known positive/negative
  tests.

**Definition of done:** canonicalization decisions, explicit ambiguous cases,
aliases/evidence, repaired relations, preserved stable URLs, and no silent
organization merge.

---

## Wave 3 — Determinism, machine exports, ingest boundaries, provenance

### P09 — Prove reproducible static builds

**Type:** build verification  
**Status:** complete — verified 2026-08-09; see
`reports/static-build-reproducibility.md`

**Scope:** reproducibility script/test, build reports, optional scheduled CI

**Objective:** Demonstrate whether two clean builds from the same source and
pinned toolchain produce identical artifacts.

**Procedure:** clean checkout, provision pinned toolchain, build, hash every
file and aggregate output, remove generated outputs, rebuild, compare, and
classify differences such as timestamps, ordering, absolute paths, or random
IDs.

**Definition of done:**

- First/second hash results are recorded.
- Nondeterministic fields are fixed or explicitly isolated.
- A periodic/manual reproducibility check exists without doubling every PR
  build unnecessarily.
- Content is not modified merely to cheat the comparison.

### P10 — Make RAG/context exports semantically equivalent to the site

**Type:** machine-export contract  
**Status:** blocked on P06/P08; coordinate with P20  
**Scope:** `scripts/ted-publish.sh`, Boris RAG/context/IR output,
`scripts/crosslinks.py`, export tests, manifests, consumer documentation

**Objective:** Ensure machine consumers receive the same entity identity,
relationship meaning, and caveats as the human publication.

**Agent work:**

- Regenerate exports from the current source SHA and pinned compiler.
- Compare canonical entity counts with source and HTML.
- Preserve direct, identity-claim, measurement, and derived edge semantics.
- Resolve or make retrieval-resolvable all include/disclaimer content.
- Do not collapse meaningful `related` data into generic part pointers.
- Include source SHA, compiler SHA, artifact hashes, and generation metadata.
- Document which artifact is for context uploads, retrieval, or crawler
  discovery.

**Non-goals:** dumping the whole site into every chunk or making artifacts
byte-for-byte identical when semantic parity is sufficient.

**Definition of done:**

- Every canonical entity is represented exactly as intended; no invented entity
  exists.
- Expected relation counts/types are tested against source/HTML semantics.
- Caveats are present or resolvable in the consumer's retrieval path.
- Freshness and provenance are visible in manifests.
- CI uploads current machine artifacts and runs parity checks.

### P14 — Build a state-ingest publication contract

**Type:** ingest architecture and boundary validation  
**Status:** blocked on P15; privacy review should include P01 outcomes  
**Scope:** state adapters, `docs/ingest/`, source manifests, normalization and
publication validators, reusable importer scaffold

**Objective:** Prevent source-specific raw structures from leaking directly into
canonical public semantics as the archive expands.

**Contract layers:** source discovery → private/raw retrieval → normalization →
source manifest → identity resolution → canonical entity generation → human and
machine publication.

**Definition of done:**

- Each boundary has explicit allowed/prohibited fields and failure behavior.
- PII/raw payload rules are documented and machine-checked.
- Source-native IDs remain provenance, not accidental global IDs.
- Schema drift and missing-source behavior are explicit.
- CA, MA, and MI differences are documented without forcing identical source
  schemas.
- A new state adapter can use a reusable scaffold and canonical publication
  contract.

### P17 — Strengthen provenance grading

**Type:** evidence model and targeted migration  
**Status:** design ready; implementation follows P02/P03 evidence findings  
**Scope:** existing evidence labels/includes, source metadata, claim-level
validators, representative content, authoring guidance

**Objective:** Make the existing evidence discipline machine-checkable without
reducing every claim to a misleading single score.

**Agent work:**

- Inventory existing evidence labels, warning includes, claim registries, and
  source metadata.
- Define a lightweight claim-specific tier vocabulary: official/primary,
  primary scientific measurement, manufacturer claim, secondary literature,
  archived/unpublished note, unresolved/unsupported.
- Flag weak support on high-impact claims: thermal constants, current law,
  safety, and product specifications.
- Render uncertainty clearly and migrate representative records first.

**Non-goals:** retroactively making every page appear equally authoritative or
replacing the archive's uncertainty language with a numeric confidence score.

**Definition of done:** model, validators, sample migrations, weakest-claim
report, tests, and authoring rules are documented.

---

## Wave 4 — Editorial, source-health, cultivar, and production cleanup

### P12 — Fix collection trunks that lie about corpus state

**Type:** editorial audit with light automation  
**Status:** ready after P03/P06 content changes  
**Scope:** top-level collection Markdown pages and optional count/state helper

**Objective:** Remove stale statements such as “current sample is synthetic,”
“contains only,” old counts, and California-only descriptions after multistate
expansion.

**Definition of done:**

- Every trunk is reviewed, including products, lab-results, testing labs,
  jurisdictions, licenses, organizations, datasets, recalls, and placeholders.
- False current-state statements are corrected.
- Counts/state labels are generated only where the source of truth is stable.
- Empty or placeholder trunks remain honestly labeled.
- Editorial prose remains useful rather than becoming a giant generated dump.

### P13 — Repair the device-taxonomy warning backlog

**Type:** controlled vocabulary and content cleanup  
**Status:** ready  
**Scope:** `metadata/device-taxonomy.json`, affected device records, taxonomy
tests and documentation

**Objective:** Resolve the 24 current warnings without weakening the component,
system, head, controller, heater, bundle, and family-lineage model.

**Agent work:** classify each warning as missing reusable vocabulary, incorrect
tag, ambiguous architecture, or deliberate exception. Extend vocabulary only
for reusable concepts; correct content when the tag is wrong; document any
intentional remaining warning.

**Definition of done:** warning before/after count, vocabulary additions,
content corrections, tests, and a disposition for every remaining warning.

### P16 — Add external-link and source-health auditing

**Type:** scheduled/network audit  
**Status:** design ready; should not block ordinary local builds  
**Scope:** URL inventory, source-health script/report, cache, mocked tests,
scheduled workflow recommendation

**Objective:** Detect dead, redirected, changed, or disappearing evidence URLs
without treating transient rate limits as content failures.

**Definition of done:**

- External URLs are categorized by source type.
- A polite, cache-aware checker reports status, redirects, domain changes, and
  obvious dead pages.
- 429/403/transient failures are classified separately from confirmed death.
- Last-success metadata and remediation workflow are documented.
- Mocked HTTP tests cover redirects, timeouts, and failure policy.

### P18 — Prevent cultivar pages from implying fixed chemotypes

**Type:** content audit and validator  
**Status:** follows P06/P17; analysis may begin earlier  
**Scope:** `content/cultivars/`, claims registry, COA-derived summaries,
`COA-04`-style validators, tests, authoring guidance

**Objective:** Keep chemistry attached to reports/batches, not intrinsically to
cultivar names.

**Agent work:**

- Flag “dominant terpene,” “typical THC,” “common primary terpenes,” and
  “expected potency” unless explicitly sourced or statistically derived.
- Distinguish breeder claims, market descriptors, observed reports, and derived
  statistics.
- Prefer “observed in N reports carrying this label” only when actual reports
  support it.
- Preserve conflicting lineage claims and uncertainty.

**Definition of done:** every cultivar is audited; numeric chemistry leakage is
flagged automatically; affected wording is corrected; no chemistry is invented;
future COA-derived summaries have an evidence rule.

### P19 — Clean production discovery and legacy URLs

**Type:** deployment/discovery audit  
**Status:** requires direct production access; do after core export/content work  
**Scope:** deployed custom domain, Pages deployment, sitemap, robots,
canonical metadata, redirects, Cloudflare-side settings

**Objective:** Determine whether legacy Rocket/Grav-era search results reflect
stale indexing, bad routing, or a live production problem.

**Agent work:**

- Check custom domain and pages.dev origin directly.
- Compare HTTP/HTTPS, www/non-www, sitemap, robots, canonicals, and known legacy
  URLs.
- Decide route-by-route between 301, 410, intentional availability, or no
  action.
- Add versioned redirects/configuration where possible and document Cloudflare
  settings that are not represented in git.
- Provide search-index cleanup/resubmission guidance.

**Non-goals:** fake replacement pages for SEO or treating a search snippet as
proof of current-origin failure.

**Definition of done:** production routing report, versioned redirect/removal
changes if needed, canonical/sitemap verification, and a separate list of
external-index lag that cannot be fixed in the repository.

---

## Wave 5 — Permanent integrity gate

### P20 — Turn the audit into a permanent regression gate

**Type:** consolidated audit runner and CI integration  
**Status:** blocked until the preceding validators and intentional findings are
known  
**Scope:** existing specialized audits, new validators, JSON/terminal report,
CI, tests, documentation

**Objective:** Compose the existing checks into one understandable integrity
gate without replacing the specialized scripts.

**Coverage:** canonical IDs; chemical and organization duplicate candidates;
COA page/record parity; future-law semantics; thermal-property conditioning;
cultivar chemistry leakage; stale trunk assertions; Boris pin drift; machine
export parity; current-tree and historical privacy checks; links; HTML IDs;
graph validity; taxonomy; provenance; policy documents; unit tests; build
success.

**Requirements:**

- Clearly separate blocking errors, warnings, and human-review findings.
- Fail only on genuinely machine-decidable blockers.
- Preserve visible findings; use narrow, reviewable suppressions only.
- Produce readable terminal output and structured JSON.
- Test the audit itself.
- Wire it into CI only after its failure policy is agreed.

**Definition of done:** one documented runner, tests, CI integration, current
before/after integrity report, and an explicit list of intentionally
nonblocking findings. A green result must mean “the configured gates passed,”
not “all possible editorial work is finished.”

---

## Agent handoff template

Copy this block into a new task when dispatching a card:

```text
CARD: P__ — <title>
REPOSITORY: thermalextractiondevices.com
SOURCE SHA: <exact commit>
SCOPE: <owned files/directories>
DEPENDENCIES: <cards or decisions>

Before editing:
1. Run git status --short --branch.
2. Read AGENTS.md-equivalent instructions, README.md, rules.md,
   metadata/id-policy.json, and the card's nearby project docs.
3. Re-run the card's baseline audit and record counts/findings.

Constraints:
- Preserve Boris and the Trunk/Satellite model.
- Do not add arbitrary frontmatter keys.
- Do not rename, renumber, reuse, or hand-edit canonical IDs.
- Do not commit generated output, raw/private data, or local paths.
- Do not change unrelated seams owned by another card.

Deliver:
- smallest coherent implementation or evidence report
- tests/validator coverage for the failure mode
- exact commands and exit statuses
- before/after counts or hashes where applicable
- unresolved evidence gaps and next-card status

Finish with:
./bin/validate_graph.sh
```

## Exit criteria for the next pass

The next pass is complete when:

- P01 has an explicit privacy/history decision and, if approved, a verified
  rewrite—not merely a cleaned working tree.
- the known scientific and legal factual defects are corrected or explicitly
  marked unresolved with evidence;
- the verified COA exists in the durable model;
- tests and the Boris pin are enforced in CI;
- machine exports carry the same semantic graph and caveats as the site;
- identity and allocation rules are safe for additional state ingestion; and
- P20 can report blocking errors separately from warnings and human review.

Until then, prioritize truth-control and synchronization over adding more
collections, more state dumps, or another framework.
