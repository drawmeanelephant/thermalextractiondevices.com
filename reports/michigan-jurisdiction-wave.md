# Michigan Jurisdiction Wave

Implementation date: **2026-08-09**. Michigan is the project's third deeply
implemented U.S. jurisdiction after California and Massachusetts.

## What Was Added

- Expanded Michigan source manifest with 12 authoritative or first-party source
  surfaces and explicit machine-readability/archival limitations.
- Replaced the Michigan stub with a connected jurisdiction index page.
- Added normalized compact evidence for 3 CRA notice-connected licenses, 3
  laboratory discovery records, 3 recall events, 11 testing requirements, and
  28 action-limit rows.
- Added 3 license pages, 3 organization pages, 3 laboratory pages, 3 product
  pages, 3 recall pages, and 1 explicit MCT target-analyte page.
- Added Michigan testing requirements data, source manifests, evidence manifest,
  recall/license/laboratory normalized records, and a sync report.
- Added the required COA discovery report; no public Michigan COA was counted.
- Added friction and three-state comparison reports.

## Official Sources Located

CRA homepage/program sections; CRA laws/rules page; MRTMA; MMFLA; adult-use and
medical verification pages; licensing and statistical reports; Metrc/enforcement
page; Sampling and Testing Technical Guidance v5.2; CRA bulletins and news
releases; disciplinary guidelines; laboratory inspection checklist surface; and
first-party PSI Labs, ACT Laboratories, and Reassure Labs pages. Full metadata
is in `data/source-manifests/stubs/michigan.json`.

## Data Ingested

| Entity/data | Count | Qualification |
| --- | ---: | --- |
| Licenses | 3 | source-connected adult-use processor sample; not complete registry |
| Legal entities | 6 | 3 notice-connected processors + 3 lab entities |
| Laboratories | 3 | first-party discovery sample; no complete official list |
| Recalls | 3 | representative CRA voluntary recall sample |
| Regulatory requirements | 11 | normalized from CRA v5.2 |
| Numeric/qualitative limit rows | 28 | analyte, matrix, limit, unit, source section retained |
| Products | 3 | recall-linked; not COA-backed |
| Batches | 0 | no public Michigan COA corpus |
| COAs | 0 | no public artifact passed verification threshold |
| Analyte results | 0 | no chemistry result is inferred from recall notices |

## What Michigan Taught Us

Michigan validates the generalized evidence architecture more than it validates
the assumption that every state will yield a bulk dataset. The same state can
provide deep testing rules and recall detail while withholding the public
license/COA joins needed for a full batch graph. A negative COA result must be a
dataset state, not an empty page or fabricated zero.

## Shared Infrastructure Reused

Stable Boris IDs and closed frontmatter; shared collection trunks; source
manifest schema; provenance conventions; shared jurisdiction evidence model;
license/entity/laboratory/product/recall collections; contamination/analyte
identity discipline; privacy exclusions; and the COA model's raw/normalized
semantics. No change to Boris was required.

## Shared Infrastructure Changed

No generic infrastructure was changed. The existing Massachusetts adapter is
correctly optimized for structured CCC datasets, while Michigan's sources are
document/search/portal oriented. Adding Michigan-specific scraping to the
Massachusetts adapter would create a second architecture and hide the source
friction.

## Michigan-Specific Code Added

No Michigan-specific Python parser or generic helper was added. The normalized
artifacts are deliberately compact, reviewable JSON assembled from the
source-specific evidence reviewed in this pass. A future live adapter should be
added only after CRA exposes a stable bulk source or the project agrees on a
shared document-source contract.

## Things You Deliberately Did NOT Scaffold Around

- No Accela/Metrc credentialed crawler.
- No guessed or reverse-engineered bulk registry API.
- No lab-performance ranking or misconduct inference.
- No public COA enumeration through client portals.
- No synthetic or demonstration Michigan COA records.
- No national MSO map or broad corporate-resolution database.

## COA Availability

The CRA states that pass/fail results are reported in Metrc and on COAs, and
enforcement documents may reference COAs, invoices, and Metrc inventory. That is
evidence that reports exist, not public access to the reports. The systematic
discovery record is `reports/michigan-coa-source-discovery.md`; the normalized
count remains zero.

## Entity Resolution Status

License → legal entity → municipality is direct for the three CRA notices.
DBAs/brands remain attributes. PSI, ACT, and Reassure are first-party lab
identities, but current CRA status, full license history, accreditation scope,
and parent-company relationships remain unresolved unless explicitly stated by
the source. Commercial cultivar labels in recall notices remain raw labels only.

## Build/Test Status

The validation gate completed with the following results:

- `python3 -m unittest discover -s tests`: 307 tests, with the existing
  loopback-dependent fetch setup requiring the approved escalated rerun; no
  Michigan assertion failures.
- `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl`:
  442 pages validated; no files changed after the ID map refresh.
- `python3 scripts/audit_markdown_links.py content`: all local Markdown links
  resolve.
- `python3 scripts/crosslinks.py --check`: 442 entities, 1,592 edges, 0 COA
  records; graph valid.
- `./bin/validate_graph.sh`: graph, crosslinks, content audits, and Boris
  compilation completed; Boris retained its known baseline diagnostics. The
  command remains nonzero at the final public-release audit because the
  repository reports 44 blocking findings, including historical email metadata
  and pre-existing artifact/history findings. The Michigan changes introduced
  no graph, link, COA, or content-audit errors; the initial Boris output-root
  link error was removed before this final run.

The primary commands were:

```sh
python3 -m unittest discover -s tests
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl
python3 scripts/audit_markdown_links.py content
./bin/validate_graph.sh
```

## Remaining Michigan Gaps

Complete license registry extraction; official complete lab list; accreditation
scope and disciplinary history joins; historical recall corpus; public product/
batch/package identifiers; real COA artifacts; producer/lab public portals; and
current rule-version diffing when CRA replaces v5.2.

## State #4 Readiness

Yes, conditionally. State #4 is easier when it has a stable structured dataset:
the shared source-manifest, identity, provenance, privacy, and COA boundaries
are now tested across three states. Michigan also makes the failure mode
explicit: if State #4 is portal/document-heavy, it will repeat Michigan's
friction until the project adds a shared document-source contract. The next
state should therefore be chosen for structured public data, not because it
looks similar on paper; Nevada is a strong next candidate because its CCB lab
library and public data surface can test the shared COA/lab path.
