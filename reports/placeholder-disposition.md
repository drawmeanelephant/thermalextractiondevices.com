# Placeholder Disposition Report

Scope: locate and address industrial-process placeholder content (closed-loop recovery, vacuum condensers, cryogenic quenching, Modbus, CAN bus, firmware/industrial PID loops, overpressure systems, generic condenser units) that is unrelated to thermal extraction devices (*vaporizers / hand-held and desktop dry-herb and concentrate extractors*).

## Disposition rule applied

Because `status: draft` still renders pages into the published HTML site (verified: the pre-existing `guides/TGDE-0004` draft page is emitted to `dist/`), "quarantine as draft" is not a viable way to stop placeholder pages from being published. The in-repo ways to stop publication are **deletion** or **replacement with in-scope content**.

**ID-allocation constraint discovered during execution:** `scripts/ted_ids.py` anchors each collection's canonical sequence on its prefix-matched anchor file (e.g., `guides/TGDE-0001.md`, `reference/TREF-0001.md`, `devices/TED-0001.md`). Deleting an anchor file silently renumbers the collection's remaining satellites. For collections with prefix-matched satellites still present, the anchor was therefore **replaced with genuine in-scope content** rather than deleted. Collections whose only satellite was the anchor (specs, safety) deleted cleanly with no renumbering.

Each item was checked for incoming references before modification.

## Deleted records (collections with no remaining prefix-matched satellites)

| Collection | Former ID | Former subject | Rationale | Incoming references |
| --- | --- | --- | --- | --- |
| specs | `specs/TSPEC-0001` | "Condenser Thermal Profile" — 14.2 kg, Tri-Clamp flange, 4.5 kW duty | Industrial condenser spec for the deleted TED-0001 | TED-0001 (replaced; no longer referenced) |
| safety | `safety/TSAFE-0001` | "Overpressure & Thermal Runaway Protocol" — pneumatic ESV valves, cryo-quench, N2 flush | Industrial closed-loop overpressure/cryo procedure; out of scope for consumer vaporizer safety | None (auto collection child only) |

## Replaced records (in-scope replacement kept the anchor to avoid sibling renumbering)

| Collection | Former ID | Former subject | Replacement content |
| --- | --- | --- | --- |
| devices | `devices/TED-0001` | "Thermal Condenser Unit" — dual-stage condenser, `10^-3 Torr`, Modbus RTU / CAN bus telemetry | **Arizer Solo III** — verified portable thermal extraction device record with sourced specs |
| guides | `guides/TGDE-0001` | "System Commissioning & Leak Testing" — vacuum decay on extraction loops | **Vaporizer Heating Architectures** — conduction/convection/hybrid reference guide |
| reference | `reference/TREF-0001` | "Solvation & Thermal Constant Tables" — enthalpy of vaporization across operating fluids | **Physical Property Data Standards** — how the archive reports pressure-referenced boiling points and source tiers |

## Trunk link cleanup

- `content/guides.md`: replaced the old industrial `[[guides/TGDE-0001|…]]` link with the new `[[guides/TGDE-0001|Vaporizer Heating Architectures]]`.
- `content/reference.md`: replaced the old industrial `[[reference/TREF-0001|…]]` link with `[[reference/TREF-0001|Physical Property Data Standards]]`.
- `content/devices.md`, `content/specs.md`, `content/safety.md`: trunk descriptions updated from industrial-caption language to accurate, current collection descriptions.

## ID allocation note

Deleting `TSPEC-0001` and `TSAFE-0001` leaves numeric gaps in those sequences (safe per `metadata/id-policy.json` — gaps are acceptable; never silently renumber). The replaced `TED-0001`, `TGDE-0001`, and `TREF-0001` retain their original IDs, so no sibling renumbering occurred in devices, guides, or reference. `metadata/id-map.jsonl` was regenerated via `ted_ids.py --write` (58 rows) after rebalancing.

## Disposition of remaining `status: draft` pages

- `guides/TGDE-0004` (Manufacturer Research Queue): retained — it is a genuine, in-scope editorial backlog item, not an industrial placeholder, and is explicitly labeled as a draft/backlog page.

## Not deleted (in-scope placeholders replaced with sourced content)

No in-scope thermal-extraction content needed industrial-placeholder replacement; instead the demo/sample product and COA records (`products/TPRD-0001`, `lab-results/TLAB-0001`) were relabeled as demonstrations (see `unresolved-claims.md` and the content edits).