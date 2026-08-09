# Publication Hardening Report

Status: **NEEDS HARDENING**

This report records the publication-hardening pass on branch
`agent/publication-hardening`, based on `origin/main` at commit `2195db4`,
verified 2026-08-09. The current tree is materially safer to publish, but
the repository is not yet a clean public-release candidate because history
cleanup, the excluded Massachusetts lane, licensing, and security-process
confirmation remain open.

## Executive result

The pass removed the California DCC raw and normalized payloads from the
tracked tree, moved the ingestion boundary to private and unpublished
storage, removed direct contact and premise details from the in-scope
published records, tightened the site identity, retired fixture content,
corrected the demo COA wording, removed unsupported operating advice, and
made release audits fail closed.

The public-release decision remains **NEEDS HARDENING**. The current audit
still reports 77 blocking findings at the configured `high` threshold. These
are not current California payload findings: they are reachable historical
blobs and commit metadata, the unchanged Massachusetts implementation and
fixtures, shared synthetic validation fixtures, and unresolved human-review
items. No history rewrite was performed.

## Blockers fixed in this pass

- Removed tracked California DCC raw, normalized, and duplicate snapshot
  payloads. Only the manifest, schema report, and sync reports remain in the
  public repository.
- Changed `scripts/dcc_ingest.py` and `scripts/dcc_sync.py` so sensitive
  source fields are not written to tracked or published payloads. The
  ingestion result retains source checksums and coarse regulatory facts, with
  private storage declared explicitly.
- Removed in-scope manufacturer street addresses, direct phone numbers, and
  direct email addresses from published records. Broad location context is
  retained where it is useful and non-sensitive.
- Removed the fake firmware release fixture `TREL-0001` and the internal
  manufacturer research queue. Retired identifiers remain documented rather
  than being silently reused.
- Reframed the site as an evidence-aware archive of thermal extraction and
  vaporization hardware, lineage, chemistry, products, batches, laboratories,
  jurisdictions, requirements, recalls, and safety. The public identity no
  longer implies closed-loop industrial control, firmware telemetry,
  schematics, calibration services, or pressure guarantees.
- Corrected the demo COA row to **Total Potential THC (calculated)** and
  stated that `THCA × 0.877` is not total cannabinoids and is not a direct
  measurement. Demo material remains labeled synthetic and non-evidence.
- Removed the specimen-page recommendation that prescribed a 180–200 °C
  airflow range for terpene preservation. No operating recommendation is
  asserted where the page lacks an appropriate source.
- Removed all 60 internal `research/...` citations from the published
  content tree across 53 pages. Every disposition is recorded in
  `reports/published-provenance-gap.md`; no replacement URL was invented.
- Removed the release-audit bypass from CI, deploy, Cloudflare build, local
  build, and publishing paths. Audit tool failures and blocking findings now
  stop release workflows.

## Remaining blockers

1. **Reachable history.** Three former DCC license-registry blobs remain
   reachable in Git history, along with four duplicate historical DCC blobs.
   The audit also finds 70 historical commit-metadata email findings. The
   cleanup plan is documented in `docs/history-cleanup-plan.md`, but no
   history rewrite or force-push is authorized in this pass.
2. **Massachusetts lane.** The current Massachusetts adapter, its fixtures,
   Massachusetts tests, and its state status document were explicitly out of
   scope and were not modified. The public and sensitive audits still detect
   synthetic addresses, phone data, and identifiers there. A separate owner
   must review that lane before a clean release decision.
3. **Shared validation fixtures.** The generic ingestion validation guard
   contains synthetic identifier examples and prohibited-name patterns. The
   audit reports these as active findings because they are shared code, not
   California DCC data. They require a maintainer decision or a narrowly
   documented audit disposition.
4. **Human review.** The public-release audit reports 13 `REV-001` review
   paths covering regulated, product, laboratory, manufacturer, jurisdiction,
   and data records. They remain review gates, not silently waived findings.
5. **Licensing.** `LICENSE.md` still states an all-rights-reserved posture and
   does not grant an open-source license. The maintainer must choose and
   publish the intended license before inviting reuse.
6. **Security process.** `SECURITY.md` now points to GitHub's private
   vulnerability-reporting flow and deliberately invents neither a mailbox
   nor a response-time promise. Maintainers still need to confirm that the
   repository's Security-tab flow is enabled and usable.

## Privacy disposition

| Data class | Before this pass | Current tree | Publication decision | Disposition |
| --- | --- | --- | --- | --- |
| California DCC owner identity and direct contact details | Tracked in raw and normalized snapshots | Not tracked | Never publish | Removed from current payloads; ingestion omits them |
| California DCC premise addresses, postal details, parcel identifiers, and coordinates | Tracked in raw and normalized snapshots | Not tracked | Never publish | Removed from current payloads; only coarse regulatory context remains |
| California DCC business, license, status, county, and city facts | Tracked in snapshots and derived pages | Redacted/aggregate forms remain | Publish with source caveat | Retained in manifest-backed records without premise or contact detail |
| California DCC source payloads | Tracked | Private/unpublished storage only | Never publish | `.gitignore`, ingest, sync, and documentation now enforce the boundary; hashes remain as provenance |
| In-scope manufacturer direct contact and street-address details | Present in several content records | Removed | Never publish | Records retain identity and broad location only where appropriate |
| Synthetic demo COA | Present as a demonstration | Present and explicitly labeled synthetic | Publish as demonstration only | Formula and potential-THC wording corrected; no verified batch claim |
| Massachusetts adapter, fixtures, tests, and status | Existing implementation | Unchanged | Separate review lane | Explicitly excluded; reported, not modified |
| Historical DCC blobs and commit metadata | Reachable in Git history | Still reachable | Block release pending decision | Follow `docs/history-cleanup-plan.md`; no rewrite performed |

## CI and release-gate changes

- `.github/workflows/ci.yml` now runs the public, sensitive-content, and
  large-file audits as hard gates and exits on any failure.
- `.github/workflows/deploy.yml` and `scripts/cloudflare-build.sh` no longer
  set a release-audit skip flag.
- `scripts/ted-build.sh` treats both blocking findings and audit-tool errors as
  build failures.
- `scripts/ted-publish.sh` runs all three release audits after generating the
  HTML, IR, RAG, context, sitemap, and `llms.txt` artifacts.
- `docs/audit-config.json` no longer names the deleted research-queue page as
  a human-review path. Existing suppressions remain narrowly scoped to the
  audit implementation's own pattern definitions.

## Site identity and trust language

The collection roots and homepage now describe what the archive actually
contains: thermal extraction and vaporization hardware, manufacturer and
lineage records, chemistry references, products and batches, laboratory
results, jurisdictional requirements, recalls, and safety material. Claims
about certification, calibration, telemetry, schematics, industrial closed
loops, and pressure performance are either explicitly bounded or reserved for
future evidence-backed records.

Manufacturer and laboratory pages distinguish source-attributed information
from independent certification. The synthetic COA remains useful as a schema
example but is not presented as a real producer, laboratory, or batch result.

## Fixture and demo cleanup

- `content/releases/TREL-0001.md` was deleted as a fake firmware fixture.
- `TGDE-0004` and `TREL-0001` are retained only in retirement and migration
  notes; neither is an active published record.
- The manufacturer research queue was removed from the published content
  tree.
- The COA example is clearly synthetic and uses potential-THC terminology.
- The specimen guide no longer gives a temperature/airflow optimization
  prescription.

## Published-provenance corrections

The pre-cleanup scan found 60 `research/...` references across 53 published
pages. Those internal paths were not reachable publication evidence. They were
removed from `content/` and classified in
`reports/published-provenance-gap.md` as either partial support, where a
reachable source supports only part of a claim, or a high provenance gap,
where the claim remains explicitly approximate or unverified until a primary
source is added.

The published rule is now: internal research may guide discovery, but a public
record must name a reachable primary or otherwise authoritative source and
separate measured, reported, approximate, and unresolved values.

## Documentation consistency

The pass aligned `README.md`, `SECURITY.md`, `PRIVACY.md`, `DATA_SOURCES.md`,
`docs/pre-publication-checklist.md`, `docs/artifact-storage.md`,
`docs/history-cleanup-plan.md`, `docs/status.md`, and the California state
status page with the current public-repository posture. The documents no
longer use placeholder security contact details or fabricated response-time
commitments. The history limitation and Massachusetts exclusion are stated
where release decisions are discussed.

## Machine-discovery and generated-artifact review

The publish step is required to inspect all generated surfaces: HTML, sitemap,
IR, RAG, context, and `llms.txt`. The final artifact scan must confirm that
retired fixture IDs, internal research paths, raw DCC payload paths, fake
firmware claims, internal editorial queues, and unqualified demo-evidence
language do not leak into those outputs. Any remaining occurrence must be
classified as a truthful caveat or fixed before release.

## Validation results

The following results are from the hardened current tree before the final
commit:

| Command | Result |
| --- | --- |
| `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl` | Pass: 222 pages validated |
| `python3 scripts/audit_markdown_links.py content` | Pass: all local Markdown links resolve |
| `python3 scripts/audit_public_release.py --config docs/audit-config.json` | Expected fail: 77 blocking findings; 136 total, 116 active |
| `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json` | Expected fail: 77 blocking findings; 116 total |
| `python3 scripts/audit_large_files.py --config docs/audit-config.json` | Pass at high threshold: 7 historical findings, none above high |
| `git diff --cached --check` | Pass |

The final artifact and gate results are:

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | Pass: 167 tests, 4 skipped |
| `BORIS_BIN=./bin/boris ./scripts/ted-publish.sh` | Exported HTML, IR, RAG, context, sitemap, and `llms.txt`; stopped at the public-release gate with exit 1 because 77 blocking findings remain |
| `./bin/validate_graph.sh` | Exit 1 at the hardened public-release gate; IDs, Markdown links, Boris parent-edge diagnostics, HTML generation, and release checks ran first. Taxonomy: 0 errors / 24 warnings. Completeness: 0 errors / 0 warnings. |
| `python3 scripts/audit_html_ids.py publish/site` | Pass: 0 duplicate IDs |
| `python3 scripts/audit_html_ids.py dist/cantilever` | Pass: 0 duplicate IDs |
| Generated machine-artifact scan | Pass: no retired fixture IDs, internal research paths, raw DCC filenames, stale evidence labels, or prohibited field names in generated surfaces |

A nonzero result from the hardened release gates is expected until the
remaining blockers above are resolved; the failure is now visible and stops
the release instead of being bypassed.

## History cleanup still required

`docs/history-cleanup-plan.md` is the handoff for any future history work. A
maintainer must decide whether to make private backups, coordinate a scrub of
the reachable DCC blobs and sensitive metadata, rotate any exposed secrets if
found, and force-push only through an explicitly approved repository
maintenance window. This pass intentionally did none of those operations.

## Recommended next actions

1. Approve or reject a coordinated history-cleanup window and update all
   clones after the scrub.
2. Give the Massachusetts lane a separate privacy and fixture review.
3. Decide how synthetic shared validation examples should be represented in
   the release audit without hiding real data.
4. Confirm GitHub private vulnerability reporting and choose the repository
   license.
5. Complete the `REV-001` record review, then rerun every required gate before
   publishing.
