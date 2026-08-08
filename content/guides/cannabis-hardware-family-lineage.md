---
id: guides/TGDE-0006
title: "Cannabis Hardware Family Lineage"
parent: guides
status: published
tags: ["guide", "devices", "cannabis-hardware", "lineage", "ball-vape"]
relations: [relates_to=manufacturers/TMFR-0004, relates_to=reference/TREF-0004]
summary: Cross-page index of the Cannabis Hardware device lineage — FlowerPot, ZenLeaf, and Airstream families — mapping every modeled head and base station to its devices/TED-* record and component role.
---

# Cannabis Hardware Family Lineage (TGDE-0006)

Cannabis Hardware's desktop catalog is organized into three architectures: **FlowerPot** (wired ball-vape heads driven by a 20 mm coil + PID), **ZenLeaf** (cordless wireless heads and 25 mm axial-coil base stations), and **Airstream** (integrated all-in-one). This guide maps the full lineage and links every modeled device to its `devices/TED-*` record, using the component roles defined in the [Device Architecture Taxonomy (TREF-0004)](../reference/TREF-0004.md).

> [!NOTE]
> Records marked **not yet modeled** are documented on the [Cannabis Hardware manufacturer page](../manufacturers/TMFR-0004.md) but have no `devices/TED-*` entity yet. Dates for legacy and discontinued models are approximate (research dossier); the manufacturer publishes release/discontinuation dates only for current-generation products.

## Lineage tree

```
Cannabis Hardware (2009–present)
│
├─ FlowerPot Family — wired ball vapes (20 mm coil + PID)
│   ├─ Legacy (pre-ball, not yet modeled)
│   │   ├─ Showerhead (c. 2009–2018) — ceramic/metal block heat mass
│   │   ├─ Vrod (c. 2010–2020) — titanium diffuser; predecessor to the ball-vape line
│   │   ├─ B-rod Mod (c. 2020) — COMMUNITY mod (Vrod filled with rubies); not a CH product
│   │   ├─ FlowerPot Ball Vape (gen 1, c. 2021) — hollowed diffuser, ~60 × 4 mm quartz balls
│   │   └─ Screen Baller (gen 2, c. 2021) — screen-bottom diffuser
│   ├─ Third generation (gen 3, 2021–2022)
│   │   ├─ B2  (2021, discontinued c. 2024) — dual-use head + concentrate dish → TED-0028
│   │   ├─ B1  (2022 – present) — high-airflow flower head → TED-0004
│   │   └─ B0 / B-Zero (2022 – present) — budget single-piece injector → TED-0005
│   └─ Fourth generation (gen 4, 2023-06)
│       ├─ F16 (injector head) → TED-0006
│       └─ F22 (diffuser head) → TED-0025
│
├─ ZenLeaf Family — cordless wireless (25 mm axial-coil base stations)
│   ├─ First-generation heads (c. 2022–2023, legacy)
│   │   ├─ Mary (standard/female diffuser) → TED-0026
│   │   └─ Jane (injector/male diffuser) → TED-0027
│   ├─ Second-generation base stations (2023-09 – present)
│   │   ├─ Whisper (BYO external PID, 2 pockets) — not yet modeled
│   │   ├─ Nova (built-in PID, 4 pockets, heat shield) → TED-0007
│   │   ├─ Bliss (built-in PID + external XLR, 5 pockets) — not yet modeled
│   │   └─ Fusion (dual PID, dual 25 mm coils) — not yet modeled
│   ├─ Third generation (2024-04)
│   │   └─ MOAB (compact kit, 16 mm coil + Mercury diffuser) — not yet modeled
│   └─ Current diffuser heads (successors to Mary/Jane): Vmax, Vmax Injector, Mercury — not yet modeled
│
└─ Airstream Family — integrated all-in-one wireless (2024-11)
    └─ Airstream (built-in coil + PID, integrated vapor path) — not yet modeled
```

## FlowerPot family (wired, 20 mm coil + PID)

| Model | Gen | Release | Status | Component role | Record |
| --- | --- | --- | --- | --- | --- |
| Showerhead | Legacy | c. 2009 | Discontinued | Legacy heat-mass block | — (not yet modeled) |
| Vrod | Legacy | c. 2010 | Discontinued | Legacy titanium diffuser (pre-ball) | — (not yet modeled) |
| B-rod Mod | — | c. 2020 | Community mod | Community-modified Vrod | — (not an entity) |
| FlowerPot Ball Vape | 1 | c. 2021 | Superseded | Heater head (ruby-filled diffuser) | — (not yet modeled) |
| Screen Baller | 2 | c. 2021 | Superseded | Heater head (screen-bottom diffuser) | — (not yet modeled) |
| B2 | 3 | 2021 | Discontinued (c. 2024) | Heater head — dual-use, concentrate dish | [TED-0028](../devices/TED-0028.md) |
| B1 | 3 | 2022 | Current | Heater head — high airflow, flower-only | [TED-0004](../devices/TED-0004.md) |
| B0 / B-Zero | 3 | 2022 | Current | Heater head — single-piece injector | [TED-0005](../devices/TED-0005.md) |
| F16 | 4 | 2023-06 | Current | Heater head — machined injector | [TED-0006](../devices/TED-0006.md) |
| F22 | 4 | 2023-06 | Current | Heater head — machined diffuser | [TED-0025](../devices/TED-0025.md) |

## ZenLeaf family (cordless wireless, 25 mm axial coil)

| Model | Gen | Release | Status | Component role | Record |
| --- | --- | --- | --- | --- | --- |
| Mary | 1 | c. 2022 | Legacy | Heater head — standard (female) diffuser | [TED-0026](../devices/TED-0026.md) |
| Jane | 1 | c. 2022 | Legacy | Heater head — injector (male) diffuser | [TED-0027](../devices/TED-0027.md) |
| Whisper | 2 | 2023-09 | Current | Complete system — base station, BYO external PID | — (not yet modeled) |
| Nova | 2 | 2023-09 | Current | Complete system — base station, built-in PID | [TED-0007](../devices/TED-0007.md) |
| Bliss | 2 | 2023-09 | Current | Complete system — base station, built-in PID + external XLR | — (not yet modeled) |
| Fusion | 2 | 2023-09 | Current | Complete system — base station, dual PID / dual coils | — (not yet modeled) |
| MOAB | 3 | 2024-04 | Current | Complete system — kit (16 mm coil + Mercury diffuser) | — (not yet modeled) |
| Vmax / Vmax Injector / Mercury | 3+ | 2024–present | Current | Heater head — current cordless diffusers (successors to Mary/Jane) | — (not yet modeled) |

## Airstream family (integrated)

| Model | Gen | Release | Status | Component role | Record |
| --- | --- | --- | --- | --- | --- |
| Airstream | 1 | 2024-11 | Current | Complete system — all-in-one (integrated coil + PID + vapor path) | — (not yet modeled) |

## Component roles at a glance

Per [TREF-0004](../reference/TREF-0004.md), a retailer bundle is never a model, and components stay spec-table rows unless they are substantive separately-purchasable platforms. The modeled CH catalog maps as follows:

- **Heater head entities (8):** B2, B1, B0/B-Zero, F16, F22, Mary, Jane. Each names its coil/PID/bowl in the spec table as sold-separately components.
- **Complete system entities (1):** ZenLeaf Nova — the base station integrates the 25 mm axial coil, built-in PID, and stand; compatible diffuser/banger heads are separate components.
- **Bundle rule applied:** the "FlowerPot B2 Standard Essentials Bundle" and "B-Zero bundle" are retail SKUs of the B2 / B0 models — referenced as source notes on their pages, never separate entities (rule TAX-05).
- **Not yet modeled:** legacy pre-ball heads (Showerhead, Vrod, FlowerPot Ball, Screen Baller), the community B-rod mod, ZenLeaf base stations Whisper/Bliss/Fusion, the MOAB kit, the Airstream, and the current Vmax/Mercury diffuser heads.

## Relation conventions

- Every modeled device `relates_to` [Cannabis Hardware, LLC](../manufacturers/TMFR-0004.md).
- Sibling heads in the same family `relates_to` each other (e.g., B1 ↔ B0 ↔ F16 ↔ F22; Mary ↔ Jane).
- Head ↔ base-station compatibility is expressed with `relates_to` plus explicit terminology in the spec table (e.g., Mary/Jane `relates_to` the Nova as compatible heads) — no invented relation kinds.

## Sources

[^1]: Cannabis Hardware, "The Evolution of the FlowerPot Ball Vapes" (Vrod → B-rod Mod → FlowerPot Ball → Screen Baller → B2 → B1 lineage). https://www.cannabishardware.com/blogs/desktop-vaporizer/the-evolution-of-the-flowerpot-ball-vapes
[^2]: Cannabis Hardware, "NEW ZenLeaf Series" (Mary/Jane diffusers; Whisper/Nova/Bliss/Fusion base stations). https://www.cannabishardware.com/blogs/zenleaf/zenleaf
[^3]: Cannabis Hardware, FlowerPot Ball Vape collection page (current wired lineup). https://www.cannabishardware.com/collections/flowerpot-ball-vape
[^4]: Cannabis Hardware, ZenLeaf Wireless Dry Herb Ball Vape Stations collection (MOAB, Vmax, Mercury, current lineup). https://www.cannabishardware.com/collections/zenleaf-wireless-vaporizer
[^5]: Cannabis Hardware research dossier (internal provenance: `research/devices/manufacturers/cannabis-hardware/artifact.md`) — legacy models (Showerhead, Vrod), approximate dates, and discontinuation notes not published by the manufacturer.

## Related pages

- [Cannabis Hardware, LLC (TMFR-0004)](../manufacturers/TMFR-0004.md)
- [Device Architecture Taxonomy (TREF-0004)](../reference/TREF-0004.md)
- [Thermal Extraction Devices Catalog](../devices.md)
