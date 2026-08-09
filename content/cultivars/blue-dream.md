---
id: cultivars/TCUL-0001
title: "Blue Dream Cultivar Overview"
parent: cultivars
status: published
tags: ["cultivar", "hybrid", "genetics"]
relations: [relates_to=cultivars/TCUL-0002, relates_to=terpenes/TTRP-0005, relates_to=terpenes/TTRP-0007, relates_to=terpenes/TTRP-0003, relates_to=terpenes/TTRP-0004, relates_to=reference/TREF-0002, relates_to=products/TPRD-0001]
summary: Overview index for the Blue Dream genetic lineage and an illustrative sample batch laboratory record (demonstration).
---

# Blue Dream

{{include includes/cultivar-identity-warning.md}}

{{include includes/first-party-provenance-warning.md}}

## Identity & Lineage Claims

The statements below are **claims**, not independently verified genetic facts.
A source saying "this is Blue Dream" is a claim; this archive preserves the
claim and its provenance rather than treating it as canonical truth. Each
statement maps to a machine-readable record in `metadata/cultivar-claims.jsonl`
(see `docs/cultivar-identity-model.md`).

| Claim | Status | Source |
| --- | --- | --- |
| **Lineage**: Blueberry × Haze (`CLM-0003`) | well_supported | First-party: [DJ Short Seeds — Azure Haze](https://www.djgenetics.com/strains/azure-haze/) states the Azure Haze cross "create[s] the same cross as the Blue Dream" (Silver Haze mother × famous Blueberry male; retrieved 2026-08-09). Corroborated by the [DNA Genetics — Blue Dream](https://dnagenetics.com/product/blue-dream-feminized/) seed-bank listing ("Genetics: Blueberry x Haze #1"). Only the [Blueberry](blueberry.md) parent resolves to an archive entity; the Haze parent has no page. |
| **Classification**: Hybrid | claimed | Archive cultivar page (morphology descriptor; does not predict chemistry) |
| **Known aliases** | none documented in this archive | Unresolved alias terms are not merged; alias resolution requires repository evidence. |
| **Breeder / origin** | not attributed | No page for the name "Blue Dream" itself exists on a first-party breeder site; the Santa Cruz, California origin is a secondary-account claim. |

> [!NOTE] Chemistry firewall
> Batch-level chemistry linked below describes the **specific batch and
> product label**, not "Blue Dream" as a genetic object. This archive does not
> assert that a cultivar name implies any fixed cannabinoid or terpene
> profile. See [Cultivar Name, Product Name, and Chemovar](../reference/cultivar-name-vs-chemovar.md).

## Products Carrying This Name

- [Buckeye Relief Blue Dream Flower (sample record)](../products/example-producer-blue-dream.md) — product label claims the cultivar name (`CLM-0001`)

## Laboratory Reports Associated With This Name

- [Sample Batch 123 COA (demonstration)](../lab-results/example-producer-blue-dream-batch-123.md) — submitted sample carried the name Blue Dream (`CLM-0002`)

> [!IMPORTANT]
> The batch record linked above is a **demonstration / sample record**, not a verified Certificate of Analysis. Its batch identifier and numeric values are illustrative placeholders and must not be cited as verified laboratory evidence for this cultivar.

## Common Terpene Nodes

- [β-Myrcene](../terpenes/beta-myrcene.md)
- [D-Limonene](../terpenes/d-limonene.md)
- [α-Pinene](../terpenes/alpha-pinene.md)
- [β-Caryophyllene](../terpenes/beta-caryophyllene.md)

## Provenance & Sources

The lineage details above (Blueberry × Haze) are widely reported across secondary and community references and are consistent with DJ Short's own description of his "Azure Haze" cross as "the same cross as the Blue Dream"; they are not independently verified genetics. Per the archive's [cultivar identity framework](../reference/cultivar-name-vs-chemovar.md), cultivar names do not fix chemical composition, and breeder-attributed pedigrees are claims that can conflict across sources.

- DJ Short Seeds (djgenetics.com), "Azure Haze": describes a Silver Haze mother clone crossed with the "famous Blueberry male" to create "the same cross as the Blue Dream." https://www.djgenetics.com/strains/azure-haze/ (accessed 2026-08-09)
- DNA Genetics, "Blue Dream Feminized Cannabis Seeds": "Genetics: Blueberry x Haze #1." https://dnagenetics.com/product/blue-dream-feminized/ (accessed 2026-08-09)
- No single first-party breeder page for the "Blue Dream" name itself was located for this archive; the Santa Cruz, California origin is a secondary-account claim.

## Claim Registry

Machine-readable claim records for this page live in `metadata/cultivar-claims.jsonl` (`CLM-0001`–`CLM-0003`), per `docs/cultivar-identity-model.md`:

- `CLM-0001` — product label claim (`product_claims_cultivar`); demonstration placeholder source
- `CLM-0002` — batch label claim (`batch_claims_cultivar`); demonstration placeholder source
- `CLM-0003` — lineage claim (`claimed_lineage_parent`, status `well_supported`); source DJ Short Seeds "Azure Haze", corroborated by the DNA Genetics listing
