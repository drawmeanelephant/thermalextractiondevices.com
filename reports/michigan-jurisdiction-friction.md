# Michigan Jurisdiction Friction

Research and implementation date: **2026-08-09**. This is a first-class
engineering record, not a list of excuses.

| Class | What happened / evidence | Affected files or entities | Workaround / code avoided | Severity | State #4 likely? | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| SOURCE FRICTION | CRA license verification is an interactive Accela search; periodic licensing reports are DOC/DOCX aggregates, not bulk rows. | `data/michigan-cra/licenses.json`, `TDTS-0025` | Preserved three notice-connected licenses separately and marked coverage partial. No scraper or guessed API added. | high | yes | CRA/public-data architecture |
| SOURCE FRICTION | CRA does not expose a public statewide COA repository; lab pages generally use client portals. | `reports/michigan-coa-source-discovery.md`, `TDTS-0027` | Recorded a negative result and kept the shared COA schema unused rather than manufacturing records. | high | likely | CRA / labs |
| SCHEMA FRICTION | Existing collections separate California `recalls` from Massachusetts `safety-advisories`; Michigan uses both voluntary/mandatory recall and consumer-advisory terminology. | `content/recalls.md`, `TRCL-0007..0009` | Used existing `recalls` records while preserving Michigan event type; documented that the collection is not jurisdiction-neutral. | medium | yes | shared jurisdiction model |
| SCHEMA FRICTION | License, legal entity, DBA, brand, premises, and product are distinct in notices but the human surface has no dedicated brand/premises collections. | licenses, organizations, products | Kept fields separate inside records and relations; no new brand collection. | medium | yes | shared entity model |
| INGESTION FRICTION | Shared Massachusetts adapter assumes a stable CSV/JSON catalog and a live state adapter. Michigan's strongest sources are HTML/PDF/DOCX. | `scripts/state_ingest.py`, Michigan data artifacts | Used compact source-specific normalized artifacts; did not retrofit the MA adapter for document scraping. | medium | yes | shared ingest package/Boris boundary |
| ENTITY-RESOLUTION FRICTION | First-party lab pages name historical/current-looking license identifiers, but do not establish current CRA status or parent-company ownership. | `TSTL-0029..0031`, `TORG-0066..0068` | Retained first-party identity and explicit unresolved status; no ownership inference. | medium | yes | entity resolution layer |
| BORIS FRICTION | Boris frontmatter has a closed relation vocabulary and page-level relation cap; rich confidence/provenance remains in data/reports. | all Michigan pages | Used `relates_to` only and kept confidence/limitations in evidence records and prose. No Boris patch. | medium | yes | Boris |
| DOCUMENTATION FRICTION | CRA labels the current guidance link as v5.1 in one page surface while the fetched PDF is revised 2024-09-23 v5.2. | source manifest, `TREQ-0003` | Recorded the PDF title/version and page-level caveat instead of silently normalizing the label. | low | likely | CRA documentation |
| PROJECT-SPECIFIC | Michigan recalls name MCT oil and CRA guidance names MCT as a target analyte; this is more specific than a generic contamination node. | `TCNT-0017`, `TRCL-0008..0009` | Added one contaminant/target-analyte entity because identity is explicit. | low | state-specific | Michigan adapter |
| AGENT TEMPTATION | The absence of a bulk registry strongly invites a bespoke Accela/Metrc scraper. | not added | Deliberately did not create a second crawler architecture; left the source limitation visible. | high | yes | project maintainers |

## Architectural conclusion

Michigan did not justify a new generic ingestion framework. It did justify
keeping the shared evidence model, source manifests, provenance conventions,
stable IDs, privacy boundaries, and raw-vs-normalized COA semantics. The next
shared improvement should be a documented document-source adapter contract,
not another one-off Michigan crawler.
