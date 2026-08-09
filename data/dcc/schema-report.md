# California DCC Schema Report

- Schema version: 1.0
- Generated: 2026-08-04T23:21:57Z

## Collections introduced

| Collection | ID prefix | Entity type |
| --- | --- | --- |
| jurisdictions | TJUR | Jurisdictions |
| licenses | TLIC | Licenses |
| organizations | TORG | Organizations |
| testing-laboratories | TSTL | Testing Laboratories |
| recalls | TRCL | Recalls |
| contaminants | TCNT | Contaminants |
| datasets | TDTS | Datasets |
| requirements | TREQ | Requirements |


## Taxonomy deviation (deliberate)

The project brief suggested nested content layouts such as
`datasets/california-dcc/` and `licenses/california/`. Boris and ted_ids derive
the collection from the FIRST path segment of a source file, so nested satellite
dirs would mislabel entity identities. Content collections are therefore flat
(`datasets/TDTS-0001.md`, `licenses/TLIC-0001.md`, `recalls/TRCL-0001.md`, ...).
Source payloads are retained in private, unpublished storage; no raw archive
layout is present in the public repository.

## Normalized license fields (schema 1.0)

license_number, license_status, license_term, license_type, license_designation,
issue_date, expiration_date, authority_id, authority, business_legal_name,
business_dba, business_structure, activity, premise_city, premise_state,
premise_county, data_refreshed_at.

## Redacted source fields

The ingestion boundary removes or keeps private the following licensee-entered
fields before any normalized record is written to a tracked path: owner identity,
street address, postal code, email, phone, parcel/cadastral identifiers, and
latitude/longitude coordinates. The public site retains only the coarse
regulatory facts needed for source-attributed aggregate and entity pages.

## Enum drift tracking

License statuses are validated against a fixed allowlist (Active, Canceled,
Expired, Revoked, Suspended, Surrendered, Limited Operations); unexpected
statuses fail the run before publication.
