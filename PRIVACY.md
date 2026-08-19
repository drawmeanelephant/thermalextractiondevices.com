# Privacy Policy & Data Classification

Thermal Extraction Devices (`thermalextractiondevices.com`) is a static
archive of engineering, regulatory, and product data. It does **not**
operate accounts, forms that store data, cookies, or client-side analytics.
This document states how data in the repository is classified and what may
or may not become public.

## What the site does not collect

* No visitor accounts, logins, or stored user data.
* No analytics/tracking scripts, cookies, or fingerprinting.
* The only client-side request is the site's own local search index
  (`connect-src 'self'` in the Content-Security-Policy).
* Requests pass through Cloudflare Pages; refer to Cloudflare's privacy
  policy for edge-level request logs.

## Data classification categories

All data in this repository falls into exactly one category below. Before
any record is published, a maintainer must confirm its category.

### 1. Safe to publish

Public engineering and general reference data:

* Device specifications, thermal/engineering parameters, safety procedures.
* Terpene and botanical chemistry reference data (public scientific data).
* Statutory/regulatory summaries citing published law.
* General cultivar knowledge attributable to public breeder documentation.
* Repository documentation, policies, and this archive's own content.

### 2. Publish only for licensed premises

Data tied to regulated cannabis operations in a specific state. Publicly
released COAs and product records fall here and must carry evidence
warnings:

* Batch Certificates of Analysis (producer + testing laboratory + batch id).
* Producer product listings with identifiers and pack sizes.
* State-specific regulatory detail referencing operating rules.

These records are published **only with the evidence include attached**, and
only when the producer/lab identifiers are already public commercial facts.
Batch data must not be extrapolated across batches, and no patient, customer,
or premises-location data may be included.

### 3. Retain only in local raw artifacts

Raw source material that exists locally or in external artifact storage but
is **never committed to git** and **never published**:

* Unprocessed lab certificates, scans, or producer communications.
* Large raw datasets and archives (see `docs/artifact-storage.md`).
* Internal research notes and editorial backlogs (draft status in git is
  acceptable for the backlog itself, but the raw sources stay local).
* California DCC raw and normalized source payloads. The public repository
  retains only the redacted `data/dcc/manifest.json`,
  `data/dcc/schema-report.md`, and sync reports; source payloads belong in
  private, unpublished storage.

### 4. Never publish

Absolute prohibitions, whether or not the government publishes them:

* Personal email addresses, phone numbers, physical addresses, or geocoordinates of individuals or private premises.
* Tax identifiers (SSN, EIN), parcel numbers, license numbers tied to individuals.
* Patient, customer, or registered-user data.
* Credentials, tokens, API keys, private keys, internal server paths.
* Private communications and anything under legal privilege.
* Data that a third party asked not to republish, even if "public" elsewhere.

### 5. Requires human review

Published-but-sensitive content that needs explicit maintainer sign-off per
record before release (the audit flags these as `REV-001`):

* Content naming identifiable businesses (producers, manufacturers, labs).
* Draft editorial material naming candidates for future coverage.
* Any record where the provenance category is disputed.

## Handling

* **Committed content** must satisfy category 1 or 2 (with evidence
  warnings) or 5 (after review). Never commit categories 3 or 4.
* **Corrections and takedowns** follow `DATA_SOURCES.md`; category-4 data
  discovered in the current tree is removed and the disposition is recorded
  in the publication-hardening report.
* **Deletion does not erase history, and a history rewrite does not erase
  GitHub.** Prohibited data in a commit stays reachable until the plan in
  `docs/history-cleanup-plan.md` is executed — and even then, GitHub keeps
  serving the pre-rewrite commits through `refs/pull/*`, which a local rewrite
  cannot touch. Closing that requires a GitHub Support request. Rotate any
  exposed credential regardless. This is not hypothetical: it is the current
  state of the California DCC licence registry in this repository.
* **Automated enforcement:** `scripts/audit_public_release.py` and
  `scripts/audit_sensitive_content.py` scan the tracked working tree for
  category-4 patterns (emails, phones, addresses, coordinates, tax IDs,
  personal paths, secrets). New allowlist entries require a PR review of
  `docs/audit-config.json`.
* **What the audits do not scan.** `audit_sensitive_content.py` reads the
  tracked tree plus commit *metadata* — author, committer, message — and never
  reads a historical blob's contents. `audit_large_files.py` sees deleted-but-
  reachable blobs by path and size only, and only within the local clone's own
  refs. No audit can see what GitHub serves from pull refs. Do not read a green
  gate as an assurance about history.

## Contact

Privacy or takedown requests: use the process in `DATA_SOURCES.md`; contact
details are in `SECURITY.md`.
