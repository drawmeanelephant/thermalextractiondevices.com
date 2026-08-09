# Device Taxonomy — Migration Recommendations

**Status:** Plan — ball-vape component-role recommendations applied 2026-08-08 · delivery-mode tags applied 2026-08-08 · operating-mode tags applied 2026-08-08 · Cannabis Hardware corpus completed 2026-08-08 · **Standard:** `content/reference/TREF-0004.md` (Device Architecture Taxonomy) · **Scope:** all existing `content/devices/*.md` records (44 pages; TED-0001…TED-0045 with TED-0040 retired and never to be reused) and the `devices` trunk.

This document audits the current device corpus against the five orthogonal axes and the ball-vape component model, and recommends concrete changes. It complements `metadata/device-taxonomy.json` and `scripts/audit_device_taxonomy.py`.

---

## 1. Baseline: what already conforms

The corpus was built before this taxonomy existed, but it is largely consistent with it:

- **Tag vocabulary is already clean.** Every tag in use on device pages is either a recognized descriptor (`portable`, `desktop`, `ball-vape`, `log-vape`, `erig`, `cordless`, `analog`, `catalytic`, `conduction`, `convection`, `hybrid`, `induction`, `butane`, `manual`, `battery`, `on-demand`, `dry-herb`, `concentrates`, `glass-airpath`) or a manufacturer slug. `scripts/audit_device_taxonomy.py` reports **0 errors / 0 warnings** on the current corpus.
- **Spec tables already separate heating from power** on most pages (e.g., FlowerPot pages list "Heating Method" and "Heat Source: 20 mm enail coil + external PID controller" as distinct rows).
- **No contradiction rules currently fire.** No page tags `conduction`+`convection` without `hybrid`, `battery`+`mains`, `direct-flame`+`indirect-flame`, `manual`+`session`, or `bundle` as a model.

## 2. Per-axis audit of current pages

| Record | Heating mechanism | Heat generation | Delivery | Operating mode | Power |
| --- | --- | --- | --- | --- | --- |
| TED-0001 Solo III | hybrid | resistive (ceramic) | stem | session + on-demand | battery |
| TED-0002 M7 | conduction-dominant | direct flame / induction (external) | direct draw | manual thermal cycle | torch / induction heater |
| TED-0003 Mighty+ | hybrid | resistive | direct draw | session | battery |
| TED-0004 B1 | convection | coil + PID | injector | continuous desktop | mains + external PID |
| TED-0005 B0 | convection | coil + PID | injector | continuous desktop | mains + external PID |
| TED-0006 F16 | convection | coil + PID | injector | continuous desktop | mains + external PID |
| TED-0007 ZenLeaf Nova | convection | coil (axial) + PID | water-tool / injector | continuous desktop | mains + external PID (built-in) |
| TED-0008 TinyMight 2 | convection | resistive | stem | on-demand (+ session) | battery |
| TED-0009 TinyMight OG | convection | resistive | stem | on-demand | battery |
| TED-0010 E-Nano NXT | convection | cartridge heater | stem | continuous desktop | mains |
| TED-0011 E-Nano OG | convection | cartridge heater | stem | continuous desktop | mains |
| TED-0012 Vapman Click | hybrid (conduction/convection/radiant) | direct flame | direct draw | manual thermal cycle | torch |
| TED-0013 Vapman 2.0 | hybrid (conduction/convection/radiant) | direct flame | direct draw | manual thermal cycle | torch |
| TED-0014 Lotus | convection | direct flame | direct draw / water-tool | manual thermal cycle | torch |
| TED-0015 Switch² | conduction (induction cup) | induction | water-tool | session | battery |
| TED-0016 Boost EVO | conduction | resistive | water-tool | session | battery |
| TED-0017 G Pen Elite II | hybrid | resistive | direct draw | session | battery |
| TED-0018 G Pen Dash+ | hybrid | resistive | direct draw | session | battery |
| TED-0019 Launch Box | conduction (+ radiant) | resistive | direct draw / stem | on-demand | battery |
| TED-0020 MD Dab Box | conduction | resistive | whip | on-demand | battery |
| TED-0021 IOLITE | conduction | indirect flame (catalytic) | direct draw | session | torch (butane tank) |
| TED-0022 WISPR 2 | conduction | indirect flame (catalytic) | direct draw | session | torch (butane tank) |
| TED-0023 Cloud Gen 1 | convection | resistive | whip / water-tool | session | mains |
| TED-0024 Cloud EVO | convection | resistive | whip / water-tool | session | mains |
| TED-0025 F22 | convection | coil + PID | injector | continuous desktop | mains + external PID |
| TED-0026 Mary | hybrid | coil (axial) + PID (station) | injector | continuous desktop | mains + external PID |
| TED-0027 Jane | convection | coil (axial) + PID (station) | injector | continuous desktop | mains + external PID |
| TED-0028 B2 | hybrid | coil (CH XLR) + PID | injector | continuous desktop | mains + external PID |
| TED-0029 ZenLeaf Whisper | convection | coil (axial) + external PID | injector / water-tool | continuous desktop | mains + external PID |
| TED-0030 ZenLeaf Bliss | convection | coil (axial) + PID | injector / water-tool | continuous desktop | mains |
| TED-0031 ZenLeaf Fusion | convection | coil (axial) + PID | injector / water-tool | continuous desktop | mains |
| TED-0032 ZenLeaf MOAB | convection | coil (axial) + PID | injector / water-tool | continuous desktop | mains |
| TED-0033 Airstream | convection | coil (built-in) + PID | injector / water-tool / whip | continuous desktop | mains |

Notes and judgment calls:

- **TED-0015 Switch² carries both `desktop` and `portable` tags.** That is legitimate — the unit is a portable battery e-rig marketed for desktop-style use — and the taxonomy's form-factor descriptors are not mutually exclusive. Keep both tags; do not "fix" this into a contradiction.
- **TED-0012/0013 (Vapman):** pages describe heating as "hybrid conduction/convection/radiant" and now tag `hybrid` (heating mechanism). `radiant` is not required as a separate tag since hybrid covers the combination; the spec row already names radiant explicitly.
- **TED-0002 (M7):** power row names "butane torch or electromagnetic induction heater" — that is the `torch` + `induction heater` dual-power case the taxonomy documents. The page now tags `torch`; the `induction-heater` power tag remains optional.
- **TED-0021/0022 (IOLITE/WISPR):** the butane tank is a self-contained fuel source (catalytic), not an open torch. The taxonomy classifies this as power `torch` with heat-generation `indirect flame`; the pages already use `butane` + `catalytic` tags, which map cleanly.

### Delivery-mode coverage (applied 2026-08-08)

Delivery-mode tags were added to every device page per axis 3 of TREF-0004, closing the wave-1 gap that left the delivery axis unpopulated:

- **Injector heads** (`injector`): TED-0004 (B1), TED-0005 (B0), TED-0006 (F16), TED-0025 (F22), TED-0026 (Mary), TED-0027 (Jane), TED-0028 (B2) — heads inject/diffuse into a bowl seated in a 14/18 mm joint.
- **Complete systems** (`injector` + `water-tool`): TED-0007 (Nova), TED-0029 (Whisper), TED-0030 (Bliss), TED-0031 (Fusion), TED-0032 (MOAB); TED-0033 (Airstream) additionally tags `whip` (whips listed as a compatible accessory; MOAB's product page states a water piece is required).
- **E-rigs** (`water-tool`): TED-0015 (Switch²), TED-0016 (Boost EVO).
- **Glass-stem portables** (`stem`): TED-0001 (Solo III), TED-0008 (TinyMight 2), TED-0009 (TinyMight OG), TED-0010 (E-Nano NXT), TED-0011 (E-Nano OG) — the removable glass stem is the draw path and load carrier.
- **Whip / water-tool desktops**: TED-0023 (Cloud Gen 1), TED-0024 (Cloud EVO) tag `whip` + `water-tool` (per TREF-0004's VapeXhale examples).
- **Manufacturer-required whip**: TED-0020 (MD Dab Box) tags `whip` — the included silicone drawing whip is required for vapor cooling at ~900 °F.
- **Direct-draw portables** (`direct-draw`): TED-0002 (M7), TED-0003 (Mighty+), TED-0012 (Vapman Click), TED-0013 (Vapman 2.0), TED-0017 (Elite II), TED-0018 (Dash+), TED-0021 (IOLITE), TED-0022 (WISPR 2).
- **Multiple modes**: TED-0014 (Lotus) tags `direct-draw` + `water-tool` (Gen 1 shipped with a steel water-pipe adapter); TED-0019 (Launch Box) tags `direct-draw` + `stem` (drawn natively or via the included stem).

Two corrections vs. the audit table above: TinyMight 2/OG are `stem` (removable glass stem that serves as draw path and load carrier — matching the taxonomy's `stem` definition, not `direct draw`), and the MD Dab Box is `whip` rather than `direct draw` (the manufacturer requires the included silicone drawing whip). `balloon` remains defined but unused — no Volcano-family page exists in the corpus yet.

### Operating-mode coverage (applied 2026-08-08)

Operating-mode tags were added to every device page per axis 4 of TREF-0004, completing the axis population started with the delivery pass:

- **`session`**: TED-0003 (Mighty+), TED-0015 (Switch²), TED-0016 (Boost EVO), TED-0017 (Elite II), TED-0018 (Dash+), TED-0021 (IOLITE), TED-0022 (WISPR 2), TED-0023 (Cloud Gen 1), TED-0024 (Cloud EVO).
- **`session` + `on-demand`**: TED-0001 (Solo III — Session and On Demand modes), TED-0008 (TinyMight 2 — session mode capped at 230 °C).
- **`on-demand`**: TED-0009 (TinyMight OG), TED-0019 (Launch Box), TED-0020 (MD Dab Box).
- **`manual` (alias for `manual-thermal-cycle`)**: TED-0002 (M7 — DynaVap click cap), TED-0012 (Vapman Click), TED-0013 (Vapman 2.0), TED-0014 (Lotus). The Vapman/Lotus pages already carried `manual`; the M7 gained it in this pass. The retained `analog` tags (M7, Launch Box, MD Dab Box) describe the control interface, not the operating mode — per TREF-0004's terminology rule.
- **`continuous-desktop`**: TED-0004 (B1), TED-0005 (B0), TED-0006 (F16), TED-0025 (F22), TED-0026 (Mary), TED-0027 (Jane), TED-0028 (B2), TED-0007 (Nova), TED-0029 (Whisper), TED-0030 (Bliss), TED-0031 (Fusion), TED-0032 (MOAB), TED-0033 (Airstream), TED-0010 (E-Nano NXT), TED-0011 (E-Nano OG) — log vapes and PID-driven ball-vape stations are designed for continuous powered desktop operation.

No page violates TAX-03 (`manual` + `session` on one record); torch-driven manual-thermal-cycle devices and session devices remain disjoint. The `manual-thermal-cycle` axis value is expressed on pages as the `manual` tag (the alias defined in `metadata/device-taxonomy.json`), matching the audit's TAX-03 rule, which keys on `manual`.

## 3. Ball-vape component roles (recommended)

| Record | Current framing | Component role |
| --- | --- | --- |
| TED-0004 B1 | "Wired, high-airflow ball-assisted convection head" | `heater head` |
| TED-0028 B2 | "Dual-use (flower + concentrates) head with concentrate dish" | `heater head` (entity created 2026-08-08; discontinued c. 2024) |
| TED-0005 B0 / B-Zero | "single-piece injector ball-vape head" | `heater head` |
| TED-0006 F16 | "Machined injector ball-vape head" | `heater head` |
| TED-0025 F22 | "Machined diffuser ball-vape head" | `heater head` (entity created 2026-08-08) |
| TED-0026 Mary | "Cordless standard (22 mm female) diffuser head" | `heater head` (entity created 2026-08-08) |
| TED-0027 Jane | "Cordless injector (18 mm male) diffuser head" | `heater head` (entity created 2026-08-08) |
| TED-0007 ZenLeaf Nova | "Cordless wireless ball-vape base station with built-in PID" | `complete system` (base station = stand + coil + PID) |
| TED-0029 ZenLeaf Whisper | "Smallest cordless base station, BYO external PID" | `complete system` (entity created 2026-08-08; base station = stand + coil, PID user-supplied) |
| TED-0030 ZenLeaf Bliss | "Base station with built-in PID plus external XLR output" | `complete system` (entity created 2026-08-08) |
| TED-0031 ZenLeaf Fusion | "Largest base station, dual PID, dual 25 mm coils" | `complete system` (entity created 2026-08-08) |
| TED-0032 ZenLeaf MOAB | "Compact third-gen station, 25 mm axial coil + built-in PID" | `complete system` (entity created 2026-08-08) |
| TED-0033 Airstream | "Integrated all-in-one with built-in vapor path" | `complete system` (entity created 2026-08-08) |

Recommendations:

1. **Add an explicit "Component Role" spec row** to each ball-vape page naming `heater head` or `complete system` (this also clears advisory ADV-01). The pages already state role in their summaries; make it a table row for consistency. **✅ Applied 2026-08-08**: Component Role rows added to TED-0004/0005/0006 (`heater head`) and TED-0007 (`complete system`), with matching `heater-head` / `complete-system` tags and explicit "heater head" / "complete system" language in each summary and family row.
2. **Do not create new entities for CH coils, PIDs, bowls, or stands.** The 20 mm coil, CH/Auber PID, Shovelhead bowl, and injector bowls are components; they stay spec-table rows on the head pages. Only the Nova is a separate platform entity (a complete system).

   **✅ Applied 2026-08-08**: substantive, separately-purchasable heads that previously existed only as manufacturer-page rows were promoted to entities per the model — F22 (TED-0025), Mary (TED-0026), Jane (TED-0027) — each with a Component Role row, `heater-head` tag, and explicit role language. No coil/PID/bowl/stand entities were created, and no bundle was promoted to a model.
3. **Never promote retailer bundles to models.** Bundles referenced on existing pages (e.g., the B-Zero bundle, B2 bundle) are source notes for the model they repackage; keep them as citations, not entities.

   **✅ Completed 2026-08-08 (Cannabis Hardware corpus)**: the remaining substantive, separately-purchasable platforms were promoted to entities — the current ZenLeaf diffuser heads VMAX (TED-0044), VMAX Injector (TED-0045), and Mercury (TED-0036); the pre-ball FlowerPot heads Showerhead (TED-0037) and Vrod (TED-0038); the generation-1 Baller head assembly (TED-0039); the Zion base station (TED-0041); and the cordless 20 mm-coil heads Pulse (TED-0042) and Swift (TED-0043). A sweep of the manufacturer's full ZenLeaf (34 products) and FlowerPot (43 products) collections found no further unmodeled platform. The exclusions are recorded in `content/guides/cannabis-hardware-family-lineage.md` under "Deliberately not modeled".

   **Part 3408 — a component that briefly had a name (rule TAX-06, added 2026-08-08).** The Screen Baller was first modeled as a device (TED-0040) and then **retired the same day** as a misclassification. Its listing sold only the diffuser plus a screen — no top, nothing that forms a working head — and the same part is sold today as the "22mm 'Standard' Diffuser", shipping inside the B1 and B2 heads. A device record for it double-counted a part that is already a spec-table row on the heads that contain it. The generation-1 Baller (part 3405) keeps its record because its listing sold top-with-dish variants and could be bought as a complete head: **the discriminator is what the listing sold, not what it was called.** An earlier revision of this document recommended recording such a part in "two roles across time"; that guidance was wrong and is withdrawn — classify once, and narrate the former name as a lineage stage. **`TED-0040` is retired and must never be reused.**

   **Source-attribution hazard.** Cannabis Hardware renames and repurposes Shopify listings, so an archived page's title and its body copy can describe different products. The 2021-10-22 snapshot titled "B-2 Head Assembly" carries the *Baller's* description and the Baller/Vrod ball figures; both were initially adopted as B-2 specifications and were corrected on 2026-08-08. Verify that an archived page's body copy actually describes the product named in its title before citing it.

   **Boris caps `relations` at 16 per page (`max_relation_count`, boris/0.8.1).** The manufacturer record used to carry a reciprocal `relates_to` for every device; at 23 Cannabis Hardware records that list exceeded the cap and failed the build with `EFRONTMATTER: relations exceeds maximum relation count`. The reciprocal list was redundant — every device already carries `relates_to=manufacturers/TMFR-XXXX` — so `TMFR-0004` now relates only to the family lineage guide and the taxonomy standard, and the device links live in its prose tables (validated by `scripts/audit_markdown_links.py`). **Do not re-add a per-device relation list to a manufacturer page**; it does not scale past 16 devices and adds no graph information.

## 4. Recommended tag changes (small, optional)

| Record | Change |
| --- | --- |
| TED-0002 M7 | add `torch` (power) tag | **✅ applied 2026-08-08** |
| TED-0012, TED-0013 | add `hybrid` (heating mechanism) tag | **✅ applied 2026-08-08** |
| TED-0004, TED-0005, TED-0006 | add `heater-head` component tag | **✅ applied 2026-08-08** |
| TED-0007 | add `complete-system` component tag | **✅ applied 2026-08-08** |

These are **recommendations only**; none are required for the audit to pass. Apply them opportunistically when a page is next edited for content reasons, to avoid churning stable pages. **All rows in the table above are now applied (2026-08-08).**

## 5. Rules that must never be violated (enforced)

Enforced as **errors** by `scripts/audit_device_taxonomy.py`:

- TAX-01: `conduction` + `convection` tags without `hybrid`.
- TAX-02: `direct-flame` + `indirect-flame` together.
- TAX-03: `manual` + `session` together.
- TAX-04: `battery` + `mains` together (unless dual power is documented in the spec table).
- TAX-05: `bundle` tagged as a device model.

Enforced as **warnings**:

- ADV-01: ball-vape page without a component role statement.
- ADV-02: device page with no heating-mechanism declaration (tag or "Heating Method" row).
- VOCAB: any tag outside the taxonomy vocabulary (new terms must be added to `metadata/device-taxonomy.json` first).

## 6. Process for new device pages

1. Classify the record on all five axes before drafting prose.
2. Add the applicable tags from `metadata/device-taxonomy.json`.
3. For ball vapes, name the component role (complete system / heater head) and keep coil/PID/bowl/stand as spec rows or components — never as new models.
4. State the relation to its manufacturer (`relates_to=manufacturers/TMFR-XXXX`) and any successor (`supersedes=devices/TED-XXXX`).
5. Run `python3 scripts/audit_device_taxonomy.py content` and clear all errors before commit.

## 7. Out of scope

- Reformatting existing pages or rewriting spec tables that already conform.
- Creating `specs/TSPEC-*` records (the `specs` collection remains empty; device pages stay the record of record per `content/specs.md`).
- Renaming manufacturer slugs or device IDs.

---

*Companion: `content/reference/TREF-0004.md`, `metadata/device-taxonomy.json`, `scripts/audit_device_taxonomy.py`, `tests/test_device_taxonomy.py`.*
