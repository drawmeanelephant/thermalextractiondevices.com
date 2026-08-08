# Planning Prompt — Cannabis Hardware Cleanup

Use this brief to continue the Cannabis Hardware device modeling. It is written to be handed to an agent as a self-contained prompt.

---

**You are working on the Cannabis Hardware device lineage cleanup.** The taxonomy and the first modeling wave are complete; your job is to finish the remaining items below against the organized research corpus under `research/`, following the established standards.

## Context (already done — read these first)

- `content/reference/TREF-0004.md` — Device Architecture Taxonomy: five orthogonal axes + ball-vape component model (complete system / heater head / coil / PID controller / bowl / stand / bundle). **A retailer bundle is never a model (TAX-05).**
- `content/guides/cannabis-hardware-family-lineage.md` (TGDE-0006) — cross-page lineage index. Its **"not yet modeled"** list is your work queue.
- `docs/device-taxonomy-migration.md` — migration state of all device pages.
- Modeled entities: TED-0004/0005/0006 (B1, B0, F16), TED-0025–0028 (F22, Mary, Jane, B2), TED-0007 + TED-0029–0033 (Nova, Whisper, Bliss, Fusion, MOAB, Airstream).
- `content/manufacturers/TMFR-0004.md` — manufacturer record with the product-family tables (kept in sync as entities are added).

## Common rules (from `research/README.md`)

1. Read `research/README.md` and `research/_index/manifest.jsonl` before working; record branch, HEAD, and `git status --short`.
2. Never treat a Perplexity research report as primary evidence — follow its source ledger back to authoritative sources (manufacturer pages, archived official pages, blogs, FAQ, warranty, primary literature).
3. Prefer manufacturer documentation; label uncertainty rather than filling gaps; never infer a device spec from a retailer description when primary documentation contradicts it.
4. Never promote a bundle to a model; never create entities for coils/PIDs/bowls/stands unless they are substantive separately-purchasable platforms.
5. Preserve Boris frontmatter and graph conventions (`relates_to`, `supersedes`, `depends_on`, `implements`; device → manufacturer; siblings relate to each other).
6. Validate before committing; produce one focused commit per work item; work on the assigned branch/worktree only; never push to `main` directly.

## Work items (in suggested order)

### 1. Vmax / Vmax Injector / Mercury cordless diffuser heads
The current ZenLeaf diffuser generation (successors to Mary/Jane), visible on the live ZenLeaf collection page and referenced in the MOAB kit page (Vmax head with 3 mm rubies + Cocobolo handle, part 3518/3574).
- Grounding: live product pages (VMAX Ball Vape, VMAX Injector, Mercury Female Flower Diffuser), the ZenLeaf collection page, and the MOAB kit parts list.
- Model as **heater-head** entities with Component Role rows and `heater-head` tags. Note the part-number overlap between "VMAX" and "Mercury" listings (3518 appears as both) — resolve via product pages or label it unresolved.
- Update TGDE-0006, TMFR-0004 (ZenLeaf table + relations), and the migration doc.

### 2. Legacy pre-ball FlowerPot models
Showerhead, Vrod, FlowerPot Ball, Screen Baller — plus the community B-rod mod.
- Grounding: the manufacturer evolution blog ("Brod Mod → FlowerPot Ball → Screen Baller → B2 → B1"), archived product pages, and the dossier's source ledger. Most specs (release dates, ball counts, dimensions) are **unconfirmed** per the dossier — label uncertainty on the page.
- Decide entity vs manufacturer-page-only per model. The **B-rod mod is a community mod, not a CH product — do not create an entity for it.**
- These are pre-ball heads, not ball vapes: component role `heater head` still applies (they are heads), but confirm terminology against TREF-0004 before tagging.

### 3. Zion Wireless Enail Station (3540)
Appears on the current ZenLeaf collection page; not yet in the dossier or the lineage guide.
- Verify against its live product page before deciding entity vs table row. Add to TGDE-0006 either way.

### 4. Verify F16/F22 (and B2/Mary/Jane) ruby ball counts
Currently flagged unverified (e.g., TED-0025 "Thermal Media" row; the F22 review does not state ball counts).
- Try archived manufacturer parts listings and the FlowerPot FAQ; if no primary source exists, keep the "unverified" label.

### 5. Document the ZenLeaf Rev 2 heat-deflector plate (2023-11-29)
The ZenLeaf blog's "Engineering Update (Revision Log)" documents a snap-on aluminum heat-deflector plate (retrofit or factory) with ~200 °F surface-temperature deflection.
- Add a consistent engineering note to the four gen-2 station pages (TED-0007, TED-0029–0031) and a line in TGDE-0006 — one shared wording, not three variants.

### 6. Cross-link TREF-0004 and the lineage guide
- Add a "Family" section to `content/reference/TREF-0004.md` linking TGDE-0006, and ensure the guide links back to the standard.

### 7. Current-availability verification
- Whisper/Nova/Bliss/Fusion status: the live ZenLeaf collection page paginates; confirm whether the gen-2 stations are still listed (the manufacturer page currently marks them Current).
- Mary/Jane discontinuation timing: keep the "c. 2022 – c. 2023 (legacy)" framing unless a primary source pins it down.

### 8. Known uncertain specs — resolve or keep labeled
B2 release/discontinuation dates (manufacturer publishes neither), F22 ~610 °F set point (community-reported), head-specific warranty terms, certifications (CE/FCC/UL). None of these may be stated as fact without a primary source.

## Validation gate (run before each commit)

```bash
python3 scripts/audit_device_taxonomy.py content
python3 -m unittest discover -s tests
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl --write
python3 scripts/audit_markdown_links.py content
SKIP_RELEASE_AUDIT=1 ./bin/validate_graph.sh
```

Every new entity needs an id-map row (via `ted_ids.py --write`) and must build in the Boris gate.

## Deliverables

- New/modified `content/devices/TED-*` pages and relations as needed
- Updated `content/guides/cannabis-hardware-family-lineage.md` (retire completed items from "not yet modeled")
- Updated `content/manufacturers/TMFR-0004.md` and `docs/device-taxonomy-migration.md`
- One focused commit per work item, message style matching `git log` (e.g., `feat: add ...`, `docs: ...`)
- Final summary listing files added/modified, entities and relations created, primary sources verified, uncertain claims left unresolved, validation results, and corpus records consumed
