# Lane report — erigs-butane

Records owned: TED-0015 (Dr. Dabber Switch²), TED-0016 (Dr. Dabber Boost EVO),
TED-0021 (IOLITE Original), TED-0022 (IOLITE WISPR 2), TED-0023 (VapeXhale Cloud Gen 1),
TED-0024 (VapeXhale Cloud EVO).

## 1. Axis tags assigned, with evidence

### TED-0015 — Dr. Dabber Switch²

| Axis | Tag | Evidence |
| --- | --- | --- |
| heating_mechanism | `conduction` | Already-cited product page (`https://drdabber.com/products/switch2`): "Omni Directional Induction Heating," concentrate/herb sits directly in the quartz cup — heat reaches the load by contact with the heated cup, not circulating air. Spec table's Heating Method row updated to state this explicitly. |
| heat_generation | `induction` | Already present in frontmatter tags; spec table row "Electromagnetic induction coupled to a 20 mm quartz induction cup" [^1][^2]. Matches TREF-0004's own worked example ("Dr. Dabber Switch² quartz induction cup"). |
| delivery_mode | `water-tool` | Already present in tags; per brief instruction and existing e-rig/water-piece design. |
| operating_mode | `session` | Already present in tags; closed-loop temperature hold across 5 presets/app control. |
| power | `battery` | Spec table: "Battery — Fixed internal 3000 mAh INR pack." |

### TED-0016 — Dr. Dabber Boost EVO

| Axis | Tag | Evidence |
| --- | --- | --- |
| heating_mechanism | `conduction` | Already present; magnetic quartz eChamber, contact heating. |
| heat_generation | `resistive` | New footnote [^3]: manufacturer's own Quartz eChamber product page (`https://drdabber.com/products/boost-evo-quartz-e-chamber`) — the "IntelliTEMP" heating element is an electrical resistive element embedded in/isolated from the chamber, matching TREF-0004's `resistive` definition ("electrical current through a resistance element"). |
| delivery_mode | `water-tool` | Already present. |
| operating_mode | `session` | Already present. |
| power | `battery` | Spec table: "Battery — Internal 3400 mAh." |

### TED-0021 — IOLITE Original

| Axis | Tag | Evidence |
| --- | --- | --- |
| heating_mechanism | `conduction` | Already present; stainless heater pin contacts the load. |
| heat_generation | `indirect-flame` | Per brief instruction, confirmed independently via US20080149118A1 ("Device for Vaporising Vaporisable Matter," Oglesby and Butler Research and Development Ltd): "a gas catalytic combustion element…for transfer of heat…to the vaporising chamber…for preventing exhaust gases entering the vaporising chamber" — combustion heat crosses a heat exchanger, no flame/exhaust contacts the load path. Matches TREF-0004's own `indirect-flame` example ("IOLITE/WISPR catalytic butane heat exchanger"). |
| delivery_mode | `direct-draw` | Already present. |
| operating_mode | `session` | Already present. |
| power | `torch` | Per brief instruction: a self-contained butane tank counts as `torch` on the power axis. Spec table already states "Power Source — Refillable butane tank." |

### TED-0022 — IOLITE WISPR 2

Same five tags/evidence pattern as TED-0021 (same platform, confirmed by the manual's 210 °C thermostat row and the same patent's catalytic/heat-exchanger architecture, which the record's own Revision Notes already describe as shared lineage with the Original).

### TED-0023 — VapeXhale Cloud (Gen 1)

| Axis | Tag | Evidence |
| --- | --- | --- |
| heating_mechanism | `convection` | Already present in tags. |
| heat_generation | `resistive` | Existing Heating Method row already said "ceramic heating element"; TREF-0004 lists "VapeXhale ceramic element" as its own worked example under `resistive`. Independently confirmed via a new citation, Medical Jane's review of the original Cloud [^4]: "the air never passes over a heating source" — an electrically heated ceramic element by contact/radiant proximity to the glass, not a flame or induction source. |
| delivery_mode | `whip`, `water-tool` | Already present in tags; both are documented (Medical Jane review confirms 18.8 mm water-pipe/HydraTube fitting on Gen 1 too [^4]). |
| operating_mode | `session` | Already present. |
| power | `mains` | Spec table: "Power — AC mains only (110 V NA / 220 V EU)." |

### TED-0024 — VapeXhale Cloud EVO

Same heat_generation/power reasoning as TED-0023 (identical PerpetuHeat ceramic-element architecture, spec table already states "AC mains only"). `heating_mechanism=convection`, `delivery_mode=whip,water-tool`, `operating_mode=session` were already present and unchanged.

## 2. Part numbers

| Record | Result | Source checked |
| --- | --- | --- |
| TED-0015 | **A4001** (Shopify product ID 7295923028041) | `https://drdabber.com/products/switch2.json` — manufacturer's own storefront data, checked 2026-08-08. |
| TED-0016 | **Not published** for the standalone unit | Checked `https://drdabber.com/products/boost-evo` and `https://www.drdabber.com/products/boost-evo` (both 404) and the storefront search-suggest endpoint (`https://drdabber.com/search/suggest.json?q=boost%20evo`), which returns only accessory SKUs (e.g. Quartz eChamber = 130102). The base Boost EVO unit appears delisted from the current storefront; its component SKU is documented but is not the unit's own part number, so it is not substituted. |
| TED-0021 | **Not published** | ManualsLib mirror of the Operation Manual lists no model/part number. No live official manufacturer page exists to check further — `https://www.oandbltd.com` (the URL named in the brief) does not resolve (`getaddrinfo ENOTFOUND`, checked 2026-08-08), and IOLITE is reported to have ceased production in 2023 (Intrade, the agency that built its e-commerce site). See §4 for the discrepancy this raises. |
| TED-0022 | **Not published** | Same as TED-0021. Retailer catalog codes exist (e.g. Canatura's per-colorway product codes) but are retailer SKUs, not manufacturer part numbers, and are explicitly excluded per the brief's rule against transcribing them. |
| TED-0023 | **Not published** | VapeXhale/Hanu Labs is defunct; no live official page. Checked the Medical Jane Gen-1 review and the TotheCloudVaporStore closure announcement — neither cites a manufacturer part number. |
| TED-0024 | **Not published** | Vapor Warehouse's retailer listing states "Part no 9415-Evo" — confirmed by direct fetch, but that is a retailer catalog code (Vapor Warehouse's own inventory number), not a manufacturer part number, so it is not transcribed as one. |

## 3. Warnings

All REC-04/05/06 warnings clear for all six records after the edits (verified by audit run below). None left unaddressed.

- TED-0023 previously had no Safety section (REC-04); added one derived from the record's own already-cited AC-mains/fixed-cord spec (not from new manufacturer safety documentation, which does not appear to survive the company's 2025 closure for the Gen-1 unit specifically — noted honestly in the section text itself).
- REC-06 (source-domain diversity) for TED-0021/TED-0022 was fixed with a real, independently verified primary source: US patent US20080149118A1, assigned to Oglesby and Butler Research and Development Ltd, describing the exact catalytic-combustion/heat-exchanger mechanism the records already claim. This is a stronger fix than the brief anticipated (a Wayback snapshot), since `web.archive.org` is not fetchable from this environment (tool error: "Claude Code is unable to fetch from web.archive.org") — flagging this as an environment limitation, not a research shortcut: I could not verify Wayback content directly and did not cite anything from it.
- REC-06 for TED-0016 fixed via the manufacturer's own eChamber accessory page (`drdabber.com`), a different domain from the previously-sole `drdabber.helpscoutdocs.com`.
- REC-06 for TED-0023 fixed via the Medical Jane Gen-1 review (secondary, explicitly attributed as a review).

## 4. Factual issues found in existing records (not silently resolved)

1. **TED-0021/TED-0022 — brief's suggested manufacturer URL does not resolve.** The brief states Oglesby & Butler's site is `https://www.oandbltd.com`. Both `http://` and `https://`, with and without `www`, return `getaddrinfo ENOTFOUND` — the domain does not resolve at all (not merely a dead page). I could not find a working "oandbltd" domain of any kind via search. The company's actual public web presence for its *industrial tool* business (soldering irons, gas torches, under the "Portasol" brand) is `https://portasol.com` — a live, different site with no IOLITE/WISPR content. IOLITE appears to have been a separate consumer sub-brand with its own now-defunct e-commerce site (built by Intrade, a Kilkenny web agency, per their own portfolio page), not hosted at oandbltd.com or portasol.com.
2. **IOLITE brand ceased production in 2023**, per Intrade's own portfolio page describing the client relationship ("IOLITE ceased production in 2023"). This is a single, non-manufacturer-first-party source (Intrade is the manufacturer's contracted web agency, not the manufacturer itself), so I've added it to Revision Notes as reported/single-source rather than upgrading it to stated fact.
3. **Discrepancy this raises in TED-0022:** the existing Revision Notes already state "the WISPR E (2024/25) shifted to a battery-powered design (reported)" — i.e., a 2024/25 product launch, which postdates the 2023 production-cessation claim above by a year or more. I did not resolve this (neither claim is well-enough sourced to override the other) — I added an explicit "Unresolved conflict, flagged rather than silently resolved" note in Revision Notes per the archive's evidence discipline, rather than deleting either claim.
4. **TED-0024, footnote [^4] citation-precision gap:** the existing footnote claimed the Medical Jane Cloud EVO review's "specs table" was the source for the Dimensions/Weight spec-table rows. On re-checking the cited review page (`https://www.medicaljane.com/review/vapexhale-cloud-evo-stationary-vaporizer-with-an-all-glass-vapor-path/`) on 2026-08-08, its visible specs table does not include dimensions or weight (it lists Released/Manufactured By/Manufactured In/Designed In/Designed For only). I did not alter or remove the Dimensions/Weight spec rows themselves — I don't have positive evidence they're wrong, only that I can't currently confirm them at the cited URL (possibly a JS-rendered table section my fetch didn't capture, or the dossier sourced them from a different medicaljane page). Flagged in the footnote text as an unresolved citation-precision gap rather than silently re-confirmed or deleted.
5. **TED-0024 footnote [^5] (VaporWarehouse) previously had no URL** and asserted "UL-certified heating element" — I found and added the real URL, which confirms the part-number and 110V-only claims verbatim but does **not** mention UL certification anywhere on the page. I left the UL claim in place (not disproven, just unconfirmed on re-check) per the rule against deleting existing sourced claims, but flagged it as unconfirmed in the footnote.

## 5. Files outside my ownership

None needed. All fixes were achievable within `content/devices/TED-0015.md`, `TED-0016.md`, `TED-0021.md`, `TED-0022.md`, `TED-0023.md`, `TED-0024.md`.

## 6. Audit output

### `python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json`

Full run (other lanes' files still show errors — not in scope):

```
Record completeness audit: 18 error(s), 7 warning(s) across 25 finding(s)
```

Filtered to this lane's six files — **zero findings of any kind** (confirmed via `grep -E "TED-0015|TED-0016|TED-0021|TED-0022|TED-0023|TED-0024"` against the full run's output, which returned no matching lines).

### `python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json`

```
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

Zero findings archive-wide (no contradictions, no unrecognized tags) after this lane's edits.

### `git status --porcelain`

Only `content/devices/TED-0015.md`, `TED-0016.md`, `TED-0021.md`, `TED-0022.md`, `TED-0023.md`, `TED-0024.md` are modified by this lane (plus this new report file). Other `M`/`??` entries in the working tree belong to concurrently-running sibling lanes, not this one.

No build, test suite, or state-changing git command was run.
