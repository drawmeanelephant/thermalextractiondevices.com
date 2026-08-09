---
id: guides/TGDE-0006
title: "Cannabis Hardware Family Lineage"
parent: guides
status: published
tags: ["guide", "devices", "cannabis-hardware", "lineage", "ball-vape"]
relations: [relates_to=manufacturers/TMFR-0004, relates_to=reference/TREF-0004]
summary: Cross-page index of the Cannabis Hardware device lineage — FlowerPot, ZenLeaf, and Airstream families — mapping every modeled head and base station to its devices/TED-* record and component role, and recording the SKUs deliberately left unmodeled.
---

# Cannabis Hardware Family Lineage (TGDE-0006)

Cannabis Hardware's desktop catalog is organized into three architectures: **FlowerPot** (wired heads driven by a 20 mm coil + PID), **ZenLeaf** (cordless wireless heads and 25 mm axial-coil base stations), and **Airstream** (integrated all-in-one). This guide maps the full lineage and links every modeled device to its `devices/TED-*` record, using the component roles defined in the [Device Architecture Taxonomy (TREF-0004)](../reference/TREF-0004.md), for which it is the reference application.

> [!NOTE]
> Every product in the manufacturer's two live collections has been classified. Models are
> listed below with their record; SKUs that deliberately get no record are listed under
> [Deliberately not modeled](#deliberately-not-modeled) with the rule that excludes them.
> Dates are given as the manufacturer publishes them. Where the manufacturer publishes no
> date, the archive gives the earliest and latest observed listing instead of an invented
> release date, and says so.

## Lineage tree

```
Cannabis Hardware (2009–present; formerly NewVape)
│
├─ FlowerPot Family — wired heads (20 mm coil + PID)
│   ├─ Pre-ball heads
│   │   ├─ Showerhead — 19-hole titanium diffuser → TED-0037
│   │   └─ Vrod — titanium diffuser + 28 mm dish → TED-0038
│   ├─ B-rod Mod (c. 2021) — COMMUNITY mod (Vrod filled with rubies); not a CH product
│   ├─ Ball-vape generations
│   │   ├─ Baller (gen 1, 2021-08) — hollowed Vrod diffuser, ~58–60 × 4 mm balls → TED-0039
│   │   ├─ Screen Baller (gen 2, 2021-09) — screen-bottom diffuser (SKU 3408) → TED-0040
│   │   ├─ B2  (gen 3, by 2021-10, discontinued) — dual-use head + dish → TED-0028
│   │   ├─ B1  (gen 3, head listed 2021-10) — high-airflow flower head → TED-0004
│   │   ├─ B0 / B-Zero (gen 3, 2022) — budget single-piece injector → TED-0005
│   │   ├─ F16 (gen 4, 2023-06) — machined injector head → TED-0006
│   │   └─ F22 (gen 4, 2023-06) — machined diffuser head → TED-0025
│   └─ Cordless 20 mm-coil heads (2024-03, used with the Clampy coil post)
│       ├─ Pulse — 18 mm male flower head → TED-0042
│       └─ Swift — 14 mm male flower head → TED-0043
│
├─ ZenLeaf Family — cordless wireless (25 mm axial coil)
│   ├─ First-generation heads (c. 2022–2023, legacy)
│   │   ├─ Mary (standard/female diffuser) → TED-0026
│   │   └─ Jane (injector/male diffuser) → TED-0027
│   ├─ Second-generation base stations (2023-09; all now discontinued)
│   │   ├─ Whisper (BYO external PID, 2 pockets) → TED-0029
│   │   ├─ Nova (built-in PID, 4 pockets, heat shield) → TED-0007
│   │   ├─ Bliss (built-in PID + external XLR, 5 pockets) → TED-0030
│   │   └─ Fusion (dual PID, dual 25 mm coils) → TED-0031
│   ├─ Third generation (2024)
│   │   ├─ Zion (BYO PID; 20 mm or 25 mm coil) → TED-0041
│   │   ├─ MOAB (built-in PID; restyled "X Pattern" 2025-10) → TED-0032
│   │   └─ Mercury (second-generation female diffuser) → TED-0036
│   └─ Fourth-generation heads (2025-09)
│       ├─ VMAX (standard, quartz-lined) → TED-0034
│       └─ VMAX Injector (male, convection-focused) → TED-0035
│
└─ Airstream Family — integrated all-in-one wireless (2024-11)
    └─ Airstream (built-in coil + PID, integrated vapor path) → TED-0033
```

## FlowerPot family (wired, 20 mm coil + PID)

| Model | Gen | Release / listing evidence | Status | Component role | Record |
| --- | --- | --- | --- | --- | --- |
| Showerhead | Pre-ball | Not published; archived on newvape.com 2019-07 to 2019-12 | Discontinued | Heater head — pre-ball diffuser | [TED-0037](../devices/TED-0037.md) |
| Vrod | Pre-ball | Not published; archived 2019-08 to 2021-10 | Discontinued | Heater head — pre-ball diffuser + dish | [TED-0038](../devices/TED-0038.md) |
| B-rod Mod | — | c. 2021 | Community modification | Modified Vrod | — (not an entity) |
| Baller (FlowerPot Ball Vape) | 1 | "Introduced in Aug-2021" (manufacturer) | Superseded | Heater head — first ball-holding diffuser | [TED-0039](../devices/TED-0039.md) |
| Screen Baller | 2 | Not published; first archived listing 2021-09-27 | Branding retired; SKU 3408 continues as a component | Heater head — screen-bottom diffuser | [TED-0040](../devices/TED-0040.md) |
| B2 | 3 | Not published; documented as existing by 2021-10-20 | Discontinued (date not published) | Heater head — dual-use, concentrate dish | [TED-0028](../devices/TED-0028.md) |
| B1 | 3 | Head listed 2021-10-20; kit 2022-02-14 | Current | Heater head — high airflow, flower-only | [TED-0004](../devices/TED-0004.md) |
| B0 / B-Zero | 3 | 2022 | Current | Heater head — single-piece injector | [TED-0005](../devices/TED-0005.md) |
| F16 | 4 | 2023-06 | Current | Heater head — machined injector | [TED-0006](../devices/TED-0006.md) |
| F22 | 4 | 2023-06 | Current | Heater head — machined diffuser | [TED-0025](../devices/TED-0025.md) |
| Pulse | — | Listed 2024-03-06 | Current | Heater head — 18 mm male, 20 mm coil | [TED-0042](../devices/TED-0042.md) |
| Swift | — | Listed 2024-03-11 | Current | Heater head — 14 mm male, 20 mm coil | [TED-0043](../devices/TED-0043.md) |

### The 3408 continuity case

SKU **3408** is the clearest example of why this archive tracks part numbers, not just names. It was sold as the **Screen Baller** (generation 2, first archived 2021-09-27), relisted as the "22mm Baller Diffuser", and is sold today as the "22mm 'Standard' Diffuser" — the original URL still 301-redirects to the current listing. The archived B-2 assembly listing shows the same part shipping *inside* the B-2 as its "Screen Diffuser (3408)".

The archive therefore records 3408 in two roles across time, and says so plainly rather than choosing one: **as a model**, the Screen Baller is a named generation in the manufacturer's own lineage narrative and holds record [TED-0040](../devices/TED-0040.md); **as a current SKU**, 3408 is a diffuser component of later head assemblies and gets no separate record in that capacity. Neither statement contradicts the other — the part outlived the model.

## ZenLeaf family (cordless wireless, 25 mm axial coil)

| Model | Gen | Release / listing evidence | Status | Component role | Record |
| --- | --- | --- | --- | --- | --- |
| Mary | 1 | c. 2022 | Legacy — absent from the live catalog (2026-08-08) | Heater head — standard (female) diffuser | [TED-0026](../devices/TED-0026.md) |
| Jane | 1 | c. 2022 | Legacy — absent from the live catalog (2026-08-08) | Heater head — injector (male) diffuser | [TED-0027](../devices/TED-0027.md) |
| Whisper | 2 | 2023-09 | Discontinued — delisted, no model-specific notice | Complete system — BYO external PID | [TED-0029](../devices/TED-0029.md) |
| Nova | 2 | 2023-09 | Discontinued — manufacturer-stated | Complete system — built-in PID | [TED-0007](../devices/TED-0007.md) |
| Bliss | 2 | 2023-09 | Discontinued — delisted, no model-specific notice | Complete system — built-in PID + external XLR | [TED-0030](../devices/TED-0030.md) |
| Fusion | 2 | 2023-09 | Discontinued — manufacturer-stated | Complete system — dual PID / dual coils | [TED-0031](../devices/TED-0031.md) |
| Zion | 3 | Listed 2024-03-28 | Listed; all variants unavailable (2026-08-08) | Complete system — BYO PID, 20 mm or 25 mm coil | [TED-0041](../devices/TED-0041.md) |
| MOAB | 3 | 2024-04; "X Pattern" standalone listing 2025-10-08 | Current | Complete system — 25 mm axial coil + built-in PID | [TED-0032](../devices/TED-0032.md) |
| Mercury | 3 | Listed 2024-04-02 | Current | Heater head — second-generation female diffuser | [TED-0036](../devices/TED-0036.md) |
| VMAX | 4 | Listed 2025-09-23 | Current | Heater head — standard, quartz-lined | [TED-0034](../devices/TED-0034.md) |
| VMAX Injector | 4 | Listed 2025-09-23 | Current | Heater head — injector, convection-focused | [TED-0035](../devices/TED-0035.md) |

### Engineering revision: the Rev 2 heat-deflector plate

The manufacturer's ZenLeaf revision log records **Rev 2, dated 2023-11-29**: a snap-on aluminum plate complementing the heat shield by further reflecting radiant heat from the coil, retrofittable to existing units and factory-installed on new outgoing ones, with a manufacturer-claimed surface-temperature deflection of 200 °F ± compared with an un-updated unit. The identical note appears on all four second-generation station records ([Whisper](../devices/TED-0029.md), [Nova](../devices/TED-0007.md), [Bliss](../devices/TED-0030.md), [Fusion](../devices/TED-0031.md)) [^1].

### Contested "smallest" claim

The manufacturer has twice claimed a "smallest in the ZenLeaf series" title: the ZenLeaf blog gives it to the **Whisper** ("the smallest footprint in the ZenLeaf series"), and the **Zion** product page, listed 2024-03-28, gives it to the Zion ("the smallest and most affordable device in the ZenLeaf vaporizer series"). Both are dated manufacturer marketing claims about different-generation products; the archive records both [^1][^2].

## Airstream family (integrated)

| Model | Gen | Release | Status | Component role | Record |
| --- | --- | --- | --- | --- | --- |
| Airstream | 1 | 2024-11 | Current | Complete system — all-in-one (integrated coil + PID + vapor path) | [TED-0033](../devices/TED-0033.md) |

## Component roles at a glance

Per [TREF-0004](../reference/TREF-0004.md), a retailer bundle is never a model, and components stay spec-table rows unless they are substantive separately-purchasable platforms. The modeled catalog maps as follows:

- **Heater head entities (16):** Showerhead, Vrod, Baller, Screen Baller, B2, B1, B0/B-Zero, F16, F22, Pulse, Swift, Mary, Jane, Mercury, VMAX, VMAX Injector. Each names its coil, PID, and bowl in the spec table as sold-separately components.
- **Complete system entities (7):** ZenLeaf Whisper, Nova, Bliss, Fusion, Zion, MOAB, and the Airstream — each integrates a coil and stand (Whisper and Zion require a user-supplied external PID; Nova, Bliss, and MOAB carry a built-in PID, with Bliss adding an external XLR output; Fusion carries dual built-in PIDs and dual coils; the Airstream adds an integrated vapor path).
- **23 Cannabis Hardware records in total**, spanning 2019-era archived listings to the 2025 VMAX generation.
- **Cross-platform pairings** are recorded on both records where the manufacturer documents them: the Mercury names the MOAB and Airstream as supported systems, and the Airstream Essentials Kit bundles the VMAX by its correct part number (3574).

## Deliberately not modeled

Recorded so the omissions are decisions rather than gaps.

| SKU / item | Rule | Why |
| --- | --- | --- |
| B-rod Mod | Not a manufacturer product | A customer modification of the Vrod, documented on the [Vrod record](../devices/TED-0038.md) as prose context [^3] |
| Clampy — DIY Ball Vape Coil Post (3513) | `stand` component role | A 1/4-20 threaded coil post "sold as assembly only", shipped with no coil, head, or PID; the user completes it. Documented in the [Pulse](../devices/TED-0042.md) and [Swift](../devices/TED-0043.md) spec tables [^4] |
| Clampy Essentials Kit (8067) | TAX-05 | Retail bundle of the Clampy post, a Pulse head, a coil, a bowl, and an optional PID [^4] |
| B1 kit (8043/8044), B-Zero bundle (8068), MOAB Essentials Kit (8065), Airstream Essentials Kit (8072) | TAX-05 | Retail SKUs of models already recorded |
| Titanium Coil Cover (3585) | Accessory | Manufacturer states it "doesn't alter performance" — cosmetic cover over an existing coil |
| 22 mm "Standard" Diffuser (3408) in its current role | Component | The current-catalog identity of the Screen Baller SKU; see [The 3408 continuity case](#the-3408-continuity-case) |
| Coils, PID controllers, bowls, posts, screens, handles, sleeves, cases, bangers, ruby balls | Component roles | Recorded in the spec tables of the heads and stations that use them |

A sweep of the full ZenLeaf (34 products) and FlowerPot (43 products) collections on 2026-08-08 found no further substantive, separately-purchasable platform unmodeled.

## Relation conventions

- Every modeled device `relates_to` [Cannabis Hardware, LLC](../manufacturers/TMFR-0004.md).
- Sibling heads in the same family `relates_to` each other (B1 ↔ B0 ↔ F16 ↔ F22; Mary ↔ Jane; VMAX ↔ VMAX Injector ↔ Mercury); sibling base stations likewise (Whisper ↔ Nova ↔ Bliss ↔ Fusion).
- Generational succession uses `supersedes` on the newer record where a manufacturer source supports it: Baller → Screen Baller → B2, and Mary → Mercury. The Showerhead and Vrod are linked as siblings only, because no manufacturer source establishes which came first.
- Head ↔ base-station compatibility is expressed with `relates_to` plus explicit terminology in the spec table — no invented relation kinds.

## Sources

[^1]: Cannabis Hardware, "NEW ZenLeaf Series" (ZenLeaf architecture; Whisper/Nova/Bliss/Fusion; "Engineering Update (Revision Log)" Rev 2 dated 11/29/2023). https://www.cannabishardware.com/blogs/zenleaf/zenleaf
[^2]: Cannabis Hardware, Zion Wireless Enail Station product page ("the smallest and most affordable device in the ZenLeaf vaporizer series"; listed 2024-03-28). https://www.cannabishardware.com/products/zion-vaporizer
[^3]: Cannabis Hardware, "The Evolution of the FlowerPot Ball Vapes" (2021-10-20; B-rod Mod → FlowerPot Ball → Screen Baller → B2 → B1). https://www.cannabishardware.com/blogs/desktop-vaporizer/the-evolution-of-the-flowerpot-ball-vapes
[^4]: Cannabis Hardware, Clampy DIY Ball Vape Coil Post (3513) and Clampy Essentials Cordless Ball Vape Kit (8067) product pages. https://www.cannabishardware.com/products/clampy-diy-vape · https://www.cannabishardware.com/products/clampy-ball-vape-kit

## Related pages

- [Cannabis Hardware, LLC (TMFR-0004)](../manufacturers/TMFR-0004.md)
- [Device Architecture Taxonomy (TREF-0004)](../reference/TREF-0004.md) — the standard this guide applies
- [Thermal Extraction Devices Catalog](../devices.md)
