# Michigan COA Source Discovery

Research date: **2026-08-09**. This report records the result of a systematic
public-web review. It does not treat a laboratory marketing page or a product
claim as a laboratory report.

## Candidate systems

| Laboratory/vendor | Access mechanism | Public? | Identifier structure | Format | Enumeration | Ingestion suitability |
| --- | --- | --- | --- | --- | --- | --- |
| CRA / Metrc | Statewide monitoring system; CRA says COA results and pass/fail are entered in Metrc | No public read API found | Metrc plant/package/sample identifiers | private system | none without credentials | not ingestible from public web |
| PSI Labs | First-party services page; public contact/service information | Partly | license numbers SC-000005 / AU-SC-000100; no public report IDs located | marketing HTML; no public COA files located | none | laboratory identity only |
| ACT Laboratories — Michigan | First-party Michigan page and client workflow | Partly | AU-SC-000106 / SC-000018 named; no public report IDs located | marketing HTML; no public COA files located | none | laboratory identity only |
| Reassure Labs | First-party public site with customer login | No for reports | no public report identifiers | HTML + customer portal | not public | laboratory identity and claimed panel list only |
| Lab Link Testing | First-party laboratory site | No public reports located | no public report identifiers found in reviewed surface | HTML | none | candidate lab source; not ingested as an entity because current CRA license identity was not confirmed in the pass |
| Carbon Labs | First-party site with client portal | No public reports located | no public report identifiers found in reviewed surface | HTML + client portal | none | candidate lab source; not ingested |
| Producer / dispensary product pages | Product menus and brand pages reviewed for linked reports | Usually no | varies; often package/lot text without a public artifact | PDF/link if present | low and unstable | no real Michigan COA artifact survived the verification threshold |
| CRA recalls and enforcement documents | Public HTML/PDF notices sometimes mention COAs, invoices, Metrc IDs, or testing failures | Yes, event-specific | license/package/sample identifiers vary by notice | HTML/PDF | event-driven only | useful for recall/enforcement provenance, not a COA corpus |

## What was and was not obtainable

- No public Michigan regulator repository exposes downloadable batch-level COAs.
- No reviewed Michigan laboratory exposed a stable, public, enumeratable COA
  endpoint or a representative downloadable corpus.
- CRA enforcement documents prove that COAs exist in investigations and that
  COA/product identifiers can be compared with Metrc inventory, but they do not
  constitute a public normalized report corpus.
- The CRA FAQ advises consumers to check that a COA matches the product and
  stage of production, but does not link a statewide public verifier.

## Archival decision

No COA artifact was ingested. The project therefore has **0 real Michigan COAs,
0 Michigan batches, and 0 Michigan analyte-result rows**. This is an evidence
gap, not a zero-result chemistry finding. The shared COA model remains the
intended destination if a lab or producer publishes public reports later.

## Recheck queue

1. Recheck CRA Accela and the CRA bulletins page for a public report/export link.
2. Recheck PSI, ACT, Reassure, Lab Link, and Carbon for public report portals.
3. Search recall attachments and enforcement PDFs for public COA artifacts; if
   one is found, retain the original bytes, SHA-256, URL, retrieval timestamp,
   and parser confidence before normalization.
