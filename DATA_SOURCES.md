# Data Sources & Provenance Policy

This document defines where the archive's data comes from, how it is
attributed, and how errors and omissions are corrected. It is the source of
record for provenance expectations across all content collections.

## Data categories and sources

| Category | Typical source | Attribution requirement |
| --- | --- | --- |
| Device specifications | Manufacturer documentation (DynaVap, Storz & Bickel, Arizer, ...) | Cite the manufacturer record; do not claim independent testing |
| Cultivar lineage & morphology | First-party breeder/seed-company documentation (e.g. Sensi Seeds, Dutch Passion) | Use the first-party provenance warning include; distinguish origin claims from chemistry/effects |
| Lab results (COAs) | Licensed testing-laboratory certificates for a named producer batch | Keep the batch/lot identifier and test-date; attach the evidence warning; do not extrapolate to other batches |
| Legal/regulatory rules | Published statutes and administrative codes (e.g. ORC / OAC) | Cite the specific rule number and effective date |
| Product listings | Producer packaging and labels | Record the exact product identifier and pack size |

Every record that makes a claim about a third party must carry the matching
evidence/provenance warning include from `content/includes/`. If a claim has
no citable source, the record stays `status: draft` or the claim is removed.

## Evidence labels

`content/reference/evidence-labels-and-claim-grammar.md` defines the label
grammar (verified / documented / asserted / draft). All content must use it.
The short version:

* **Verified** — independently confirmed by a primary source we hold.
* **Documented** — attributable to a named first-party source.
* **Asserted** — claimed by a source, not independently confirmed.
* **Draft** — unverified editorial material (research queue, notes).

## Correction & takedown process

The archive publishes information about identifiable businesses (producers,
manufacturers, testing laboratories). When a subject believes a record is
inaccurate, outdated, or should not be published:

1. **Submit a correction request** through the repository issue tracker or
   the contact channel in `SECURITY.md`. Requests must identify the record
   (collection + entity ID), the specific claim, and the correct information
   with a source.
2. **Acknowledge** within 5 business days.
3. **Verify** the claim against the primary source; where conflicting,
   prefer the primary source and record the discrepancy on the page.
4. **Act within 10 business days**: correct, annotate, or remove the claim.
   Content is corrected in a new commit (history is never rewritten).
5. **Takedown requests** for entire records about a person or business are
   reviewed under `PRIVACY.md` category rules; removal is logged in the
   changelog.

Record every correction in `content/changelog/` (TCHG entities) so the
archive's editorial history stays auditable.

## What is never published

See `PRIVACY.md` for the full categorization. At minimum, never commit:
personal email addresses, phone numbers, full street addresses, geocoordinates
for non-public premises, tax identifiers, parcel numbers, patient or
customer data, access credentials, or internal communications.

## Keeping this policy current

Changes to this policy are themselves editorial changes and belong in the
changelog. The public-release audit (`scripts/audit_public_release.py`)
flags missing provenance structures; keep `metadata/id-map.jsonl` current via
`scripts/ted_ids.py --write`.
