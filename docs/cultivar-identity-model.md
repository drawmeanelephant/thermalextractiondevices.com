# Cultivar Identity Model

This document defines the provenance-aware cultivar identity model for
Thermal Extraction Devices. It specifies how the archive represents breeder
claims, aliases, lineage claims, seed-bank listings, product labels, and
unresolved identity **without** pretending the cannabis naming ecosystem is
perfectly consistent.

**The core rule:** a source saying "this is Blue Dream" is a *claim*, not
automatically canonical truth. A seed bank selling something called "Blue
Dream" is evidence that the seller offers a cultivar under that name — it is
not automatically evidence that all Blue Dream has identical genetics or
chemistry, that the seller originated it, or that its stated lineage is
historically definitive. The archive models these distinctions explicitly and
preserves disagreement.

---

## 1. Entity semantics

The archive distinguishes several entity kinds that share names but are not
the same object:

| Entity | Definition | Canonical factual source |
| --- | --- | --- |
| **Cultivar entity** | Informational, canonical representation of a named genetic lineage; an index, not a chemical formula | First-party breeder documentation |
| **Product label** | A packaged commercial offering sold by a licensed producer | Licensee product registration / packaging |
| **Breeder claim** | A breeder's assertion about its own breeding or release | The breeder's own material |
| **Seed-bank listing** | A seed bank's catalog entry offering seeds under a name | The listing itself |
| **Batch identity** | The name a specific produced lot / submitted sample carried | Laboratory Certificate of Analysis header |
| **Measured chemistry** | Quantitative analyte results for a specific batch | Laboratory Certificate of Analysis values |

A cultivar entity is **not** a product label, a breeder claim, a seed-bank
listing, a batch, or a chemistry profile. A cultivar page may *link to* all of
those; it must never silently collapse them.

### Where entities live

* Content entities (cultivars, products, lab results, organizations) are
  Boris satellites with stable IDs such as `cultivars/TCUL-0001`
  (`metadata/id-policy.json`).
* Breeders and seed banks that are not yet content entities may appear as
  free-text claim objects. They are upgraded to entities when the archive
  creates pages for them; claims are then re-pointed at the entity ID.

---

## 2. Relation semantics

Relations exist in **two layers** that must stay in sync.

### Layer 1: the published Boris graph (`relations:` in frontmatter)

The pinned Boris compiler supports exactly four relation kinds:
`relates_to`, `implements`, `depends_on`, `supersedes`. The published graph
(`publish/ir/graph.json`) uses these edges for canonical, non-claim
connectivity — e.g. a cultivar page relating to its in-graph lineage parent,
or a product `depends_on` its batch report.

### Layer 2: the claim registry (`metadata/cultivar-claims.jsonl`)

Every nontrivial identity or lineage assertion lives as one JSON object per
line in the claim registry, carrying the full provenance envelope. The
registry is the source of truth for *who claimed what, when, and with what
status*. It is validated against the content tree
(`scripts/validate_cultivar_claims.py`) and exported to machine consumers by
`scripts/ted-publish.sh` as `publish/claims.jsonl`.

### Required relationship vocabulary

| Kind | Meaning | Provenance required |
| --- | --- | --- |
| `alias_of` | Evidence-backed identity: same genetic object | yes |
| `claimed_alias_of` | A source claims identity; archive does not merge on word alone | yes |
| `bred_by` | Evidence-backed origin | yes |
| `claimed_bred_by` | A source claims origin | yes |
| `lineage_parent` | Evidence-backed parent | yes |
| `claimed_lineage_parent` | A source claims a parent | yes |
| `sold_by` | Evidence-backed seller of subject | yes |
| `listed_by` | Evidence-backed catalog listing | yes |
| `seed_source` | Evidence-backed seed-stock origin | yes |
| `product_claims_cultivar` | Product label carries the cultivar name | yes |
| `batch_claims_cultivar` | Submitted sample carried the cultivar name | yes |
| `possibly_same_as` | Unresolved identity; do not merge | yes |
| `historically_associated_with` | Documented association, no identity claim | yes |
| `source_disagrees_with` | Two retained claims conflict. **`subject`/`object` are claim IDs, not content entities**: subject is one side of the dispute and object the other. Both claims remain in the registry | yes |

`claimed_*` kinds and `possibly_same_as` / `source_disagrees_with` are the
machinery of disagreement. Kinds without a `claimed_` prefix are reserved for
assertions the archive itself treats as evidence-backed; in practice nearly
everything in a naming ecosystem this noisy starts as `claimed_*` or
`possibly_same_as`.

### Claim record schema

```json
{
  "claim_id": "CLM-0001",
  "kind": "product_claims_cultivar",
  "subject": "products/TPRD-0001",
  "object": "cultivars/TCUL-0001",
  "object_is_entity": true,
  "status": "claimed",
  "wording": "Cultivar Lineage: Blue Dream",
  "source": {
    "name": "Buckeye Relief (sample placeholder)",
    "type": "producer",
    "retrieved": "2026-08-09",
    "url": "https://…"
  },
  "notes": "…"
}
```

* `subject` — always a content entity ID (validated to exist).
* `object` — a content entity ID (`object_is_entity: true`) or a free-text
  name (e.g. a breeder without a page yet).
* `source` — name, `type` (role), optional `retrieved` (ISO date) and `url`.
* `status` — human-readable (see §4). No fabricated numeric confidence.

---

## 3. Source-role model

Different sources are authoritative for different things. The role is recorded
per claim and is never flattened into one credibility bucket:

| Role | Strong evidence for | Weak evidence for |
| --- | --- | --- |
| `breeder` | its own breeding / release claims | anyone else's claims |
| `seed_bank` | that it listed/sold a cultivar under a name | genetics or origin |
| `producer` | the label it put on its own product | chemistry of other batches |
| `testing_laboratory` | what the submitted sample/report was called | genetics |
| `regulator` | licensed product/report metadata in its system | breeding history |
| `community` / `database` / `forum` | discovery and historical context | identity authority |

`archive` is a special role: the repository's own curated page as the source
of a claim. Archive-sourced claims inherit the page's stated provenance
(first-party breeder documentation, per `content/includes/first-party-provenance-warning.md`)
and stay `claimed` until a first-party source URL is attached.

---

## 4. Uncertainty model

Statuses are human-readable; the archive does not fabricate numeric
confidence scores (it has no principled scoring model).

| Status | Meaning |
| --- | --- |
| `verified` | Archive treats the assertion as established fact |
| `well_supported` | Multiple independent, compatible sources, **or** a directly attached first-party primary source that confirms the claim (e.g., the breeder's own strain page asserting its release) |
| `claimed` | Asserted by a source whose role is not strong for this claim type (e.g., a seed-bank listing for a genetics claim); not independently confirmed |
| `conflicting` | Sources assert incompatible things; all retained |
| `tentative` | Plausible but weakly sourced |
| `unresolved` | Identity/lineage cannot be settled from current evidence |
| `historical` | Documented in historical sources; not a current claim |

Rules:

1. Never upgrade a `claimed_*` claim to evidence-backed status without
   attaching the evidence.
2. Never resolve an alias from model memory; require repository evidence.
3. Conflicting claims are stored side by side. Resolving the conflict is a
   decision recorded with its own provenance, never a silent merge.
4. Unknown lineage is a first-class state: a cultivar may have zero, one, two,
   or many documented parents — or none documented at all.
5. **Kind and status are orthogonal.** The kind (`claimed_bred_by`,
   `claimed_lineage_parent`, …) records the claim's structure and never
   changes when confidence rises; the status carries the confidence.
6. **Upgrade convention.** When a claim is upgraded, the `source` object is
   repointed at the primary source that confirms it (name, role, URL,
   retrieval date) and `notes` preserve the claim's history (e.g. "previously
   recorded from the archive page"). A source upgrade without a role-appropriate
   URL is not an upgrade: per the source-role model, a seed-bank page is
   strong evidence for its listing but weak for genetics or origin.

---

## 5. Alias rules

Aliases (e.g. GG4 ↔ Gorilla Glue #4 ↔ Original Glue) are resolved **only**
through registry records (`alias_of` / `claimed_alias_of`) backed by
repository evidence. String similarity is never sufficient.

* `scripts/cultivar_claims.normalize_name()` performs surface-level
  normalization for matching and discovery only: case folding, Unicode NFC,
  whitespace collapsing, and punctuation-variant folding.
* Normalization **preserves** meaningful tokens: numbers, phenotype markers,
  hash numbers, breeder prefixes, `BX`, `F1`, `F2`, `Auto`, `Fast`. Canonical
  display names are never rewritten.
* Normalization does **not** connect abbreviations: `gg4` and
  `gorilla glue 4` normalize to different keys on purpose.
* Unresolved alias terms stay findable without silently merging: a search
  for an unclaimed term surfaces the term, any `possibly_same_as` records,
  and a note that identity is unresolved.

---

## 6. Lineage rules

* A cultivar may have zero, one, two, or more claimed parents; lineage is
  not forced into exactly two parents.
* Complex backcross claims (`BX`, `F1`, `F2`) are preserved verbatim in
  `wording` and are never stripped by normalization.
* Each lineage assertion is a claim with provenance: who stated it, in what
  role, when retrieved, and with what status.
* Multiple conflicting lineage claims coexist as separate registry records.
* Parents may be in-graph entities or free-text names. A claim whose parent
  is out of graph is recorded with `object_is_entity: false`; the wording
  carries the full lineage string (e.g. "Blueberry × Haze").

---

## 7. Seed-listing rules

Seed-bank links are supported without turning the site into an affiliate
directory.

* Each listing record preserves, where possible: organization, cultivar /
  listing name, URL, breeder claimed by seller, lineage claimed by seller,
  seed type if stated, availability status if known, retrieved date.
* No affiliate parameters. No fabricated purchase links.
* Availability is a point-in-time observation: the archive does not promise
  that availability remains current unless actively refreshed.
* Seed-bank listings map to `listed_by` / `sold_by` / `seed_source` claim
  kinds. A listing is evidence of *what the seller offers under a name*,
  never of genetics, origin, or chemistry.

The repository currently contains **no** seed-bank listing evidence; the
registry must not invent any (enforced by tests). Importer requirements for
adding listings live in §10.

---

## 8. Chemistry firewall

Cultivar identity pages may **link** to laboratory observations; they must
never automatically inherit analyte measurements.

* Acceptable: "Reports associated with products labeled Blue Dream."
* Forbidden: "Blue Dream contains 23% THC" — unless the statement is
  explicitly tied to a particular report or a legitimate aggregated study.
* Batch chemistry describes the *batch and the label it carried*
  (`batch_claims_cultivar`), not the genetic object.
* Measured values live in lab-result records (`content/lab-results/`), which
  are the factual source of record; cultivar pages are indexes into them.

This firewall is mandatory and is restated on cultivar pages (see
`content/cultivars/blue-dream.md`).

---

## 9. Machine retrieval behavior

Machine consumers (RAG, exports) must be able to distinguish *"Seed Bank X
claims Y"* from *"Y is definitively true."*

* `scripts/cultivar_claims.render_claim_context()` renders each claim with
  epistemic language: who said it, in what role, when retrieved, the claim
  statement, and its status (e.g. `claimed` vs `verified`). When given the
  registry (`claims_by_id`), `source_disagrees_with` records render as
  "the attribution of <entity> is disputed between claim A (X) and claim
  B (Y)" so retrieval context names both sides.
* `scripts/ted-publish.sh` copies the registry to `publish/claims.jsonl`,
  alongside the Boris IR graph (`publish/ir/`), RAG corpus
  (`publish/rag/`), and context bundle (`publish/context/`).
* Retrieval prompts must render claims through `render_claim_context` rather
  than quoting `object` fields bare.
* Content pages carry the same epistemic framing in prose, so the Boris RAG
  corpus (generated from content) is consistent with the registry.

---

## 10. Future importer requirements

Any automated importer that adds identity, lineage, alias, or listing data
must:

1. Write one record per claim to `metadata/cultivar-claims.jsonl` with the
   full provenance envelope; never mutate a claim in place without a new
   claim record or an explicit, sourced revision.
2. Reference existing content entity IDs; allocate new entity IDs through
   `scripts/ted_ids.py --write` before referencing them.
3. Use only the vocabulary in §2 (or extend it here first).
4. Never fabricate: no affiliate links, no availability promises, no
   chemistry assertions, no alias resolution without evidence.
5. Keep the published graph (`relations:` in frontmatter) limited to the four
   Boris kinds; rich semantics live in the registry.
6. Preserve epistemic language in every generated string (see §9).
7. Add or extend tests in `tests/test_cultivar_claims.py` so the registry
   validates clean against the content tree.

---

## 11. Worked example (definition of done)

The model must be able to represent the following scenario without falsely
asserting that all four references describe the exact same genetic object:

> Laboratory report R tested batch B whose producer labeled the product
> "Blue Dream"; Seed Bank S also sells a cultivar called "Blue Dream";
> Breeder X claims one lineage while Source Y claims another.

Representation:

* `batch_claims_cultivar`: R → the cultivar entity, status `claimed`
  (the report is evidence of what the sample was called).
* `product_claims_cultivar`: the producer's product → the cultivar entity,
  status `claimed`.
* `listed_by` / `sold_by`: S's listing → the cultivar entity, status
  `claimed`, with the listing URL and retrieval date.
* `claimed_lineage_parent` (source X) and `claimed_lineage_parent` (source Y)
  as separate records; if they conflict, both are marked `claimed` and a
  `source_disagrees_with` record documents the conflict. That record's
  `subject`/`object` reference the two conflicting claim IDs (e.g.
  `CLM-0013` vs `CLM-0014`), not the cultivar entity, so the dispute link
  survives machine export without losing either side.
* If the archive cannot establish identity between the lab's "Blue Dream",
  the seed bank's "Blue Dream", and the cultivar page's "Blue Dream",
  `possibly_same_as` records carry that unresolved status.

All four references remain distinguishable. That ambiguity is a feature:
**do not merge.**
