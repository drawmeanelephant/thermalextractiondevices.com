# Worker report — lane `ch-zenleaf-stations`

Lane: ZenLeaf cordless base stations (Nova, Whisper, Bliss, Fusion, MOAB, Zion) + Airstream.
Files owned: `content/devices/TED-0007.md`, `TED-0029.md`, `TED-0030.md`, `TED-0031.md`,
`TED-0032.md`, `TED-0033.md`, `TED-0041.md`.

## 1. Per-record axis table

All seven are `complete-system` (base station or integrated all-in-one). Heating mechanism is
`convection` and heat-generation is `coil` for all seven per the brief — every record's own
spec table already documented "cordless ball-assisted convection" heat supplied by a 25 mm
(or, for Zion, 20/25 mm) coil, so these two tags were simply promoted from prose that was
already there.

| Record | heating_mechanism | heat_generation | delivery_mode | operating_mode | power | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| TED-0007 Nova | `convection` | `coil` | `water-tool` (kept; `injector` removed) | `continuous-desktop` (already present) | `mains` (added) | Spec row "Heating Method: Cordless ball-assisted convection; heat supplied by a 25 mm axial coil"; spec row "Power \| AC mains (base station)"; Component Role row already states built-in PID |
| TED-0029 Whisper | `convection` | `coil` | `water-tool` (kept; `injector` removed) | `continuous-desktop` (already present) | `external-pid` (added, replacing absent power tag) | Spec row "Power \| AC mains via user-supplied external PID" and Component Role "requires a user-supplied external PID controller (XLR), not included" — taxonomy's own `external-pid` definition already folds in "mains-powered external controller," so a bare `mains` tag would double-count the same fact |
| TED-0030 Bliss | `convection` | `coil` | `water-tool` (kept; `injector` removed) | `continuous-desktop` (already present) | `mains` (added) | Spec row "Power \| AC mains (base station)". Re-read the "external XLR output with its own temperature controller" line per the brief's instruction to check what the hardware does: grammatically this is a *second built-in controller* dedicated to the XLR output, not a user-supplied PID — nothing in the record says the user must supply their own controller for that output, unlike Whisper/Zion which say so explicitly. Reworded the Temperature Control spec row to make that reading explicit rather than leaving it ambiguous for the next reader. |
| TED-0031 Fusion | `convection` | `coil` | `water-tool` (kept; `injector` removed) | `continuous-desktop` (already present) | `mains` (added) | Spec row "Power \| AC mains (base station)"; Component Role: "dual built-in PID controllers" |
| TED-0032 MOAB | `convection` | `coil` | `water-tool` (kept; `injector` removed) | `continuous-desktop` (already present) | `mains` (added) | Spec row "Power \| AC mains (base station; no external PID required)" |
| TED-0033 Airstream | `convection` | `coil` | `injector`, `water-tool`, `whip` (all three kept, none removed) | `continuous-desktop` (already present) | `mains` (added) | Spec row "Power \| AC mains (integrated; power cord included)". Checked the record per the brief's flag: the built-in vapor path seats 18.8 mm bowls (Shovelhead, Matrix) at a joint and draws through a water piece — that is the taxonomy's own injector definition ("heater head injects into a bowl seated in a 14/18 mm joint; draw through a water piece"), distinct from the plain "ZenLeaf head + water piece" pattern the other six stations use. Compatible-accessories row also documents whips explicitly. All three delivery tags were already present and are correct; no change made. |
| TED-0041 Zion | `convection` | `coil` | `water-tool` (added — was entirely missing) | `continuous-desktop` (added — was entirely missing) | `external-pid` (added — was entirely missing) | Spec row "Power \| AC mains via user-supplied external PID"; Component Role: "requires a user-supplied external PID controller via a standard XLR plug"; "banger use is paired with a shovelhead bowl and water piece" |

### `injector` tag removal — factual correction

Nova, Whisper, Bliss, Fusion, and MOAB all carried a pre-existing `injector` tag alongside
`water-tool`. Per the brief's own framing ("these stations heat a diffuser or a banger that
the user then takes to a water piece — `water-tool`") and TREF-0004's own worked example
— `water-tool`'s canonical archive example is literally **"ZenLeaf head + water piece"** —
`injector` does not describe how these six stations work: the diffuser/banger sits directly
in the station's own coil, not injected into a separate joint-seated bowl by a heater head.
I removed `injector` from all five records that had it (kept it only on Airstream, whose own
built-in vapor path genuinely does seat bowls at a joint — see table above). This is the one
"factual error found in an existing record" for this lane (report item 4).

## 2. Part numbers added

| Record | Part number | Source |
| --- | --- | --- |
| TED-0007 Nova | 3482 (SKUs 3482-110v / 3482-220v) | Live manufacturer product JSON, observed 2026-08-08, + Wayback snapshot 2024-01-06 corroborating the same SKUs while still actively sold — https://www.cannabishardware.com/products/nova.json ; http://web.archive.org/web/20240106084523/https://www.cannabishardware.com/products/nova |
| TED-0029 Whisper | 3489 (SKUs 3489-110v / 3489-220v, $322) | Wayback snapshot 2024-02-22 of the manufacturer's product page (live page now 404) — http://web.archive.org/web/20240222113920/https://www.cannabishardware.com/products/whisper |
| TED-0030 Bliss | 3486 (SKUs 3486-110v / 3486-220V, $553) | Wayback snapshot 2024-04-25 of the manufacturer's product page (live page now 404) — http://web.archive.org/web/20240425095348/https://www.cannabishardware.com/products/bliss |
| TED-0031 Fusion | 3488 (SKUs 3488-110v / 3488-220v, $748) | Live manufacturer product JSON, observed 2026-08-08, + Wayback snapshot 2025-12-10 — https://www.cannabishardware.com/products/fusion.json ; http://web.archive.org/web/20251210011857/https://www.cannabishardware.com/products/fusion |
| TED-0032 MOAB | 3506 (standalone listing 3583) | Already present pre-leveling; added Wayback snapshot 2025-09-14 of the Essentials Kit page as a second-domain corroboration — http://web.archive.org/web/20250914175545/https://www.cannabishardware.com/products/moab-ball-vape-kit |
| TED-0033 Airstream | 3556 (base station) | Was only stated inline in the Component Role prose, no dedicated Part Number row — added the row, citing the existing product-page footnote plus a new Wayback snapshot 2025-09-14 — http://web.archive.org/web/20250914183540/https://www.cannabishardware.com/products/airstream-vaporizer |
| TED-0041 Zion | 3540 + five variant SKUs | Already present pre-leveling; added Wayback snapshot 2025-12-10 as a second-domain corroboration — http://web.archive.org/web/20251210014808/https://www.cannabishardware.com/products/zion-vaporizer |

None of the four "discontinued and delisted" stations required a "not published" fallback —
every one recovered a real manufacturer part number, either from the still-live product JSON
(Nova, Fusion — both pages are live and carry the manufacturer's own discontinuation note) or
from a Wayback snapshot (Whisper, Bliss — both genuinely 404 on the live site, confirmed by a
direct fetch during this pass).

## 3. Warnings

**None outstanding.** `audit_record_completeness.py` reports zero findings (errors or
warnings) for all seven files — REC-04 (Safety Notes) and REC-05 (Component Role row) were
already satisfied on every record before this pass; REC-06 (source-domain diversity) was a
warning on all seven going in (every citation was `www.cannabishardware.com`). I cleared it
on all seven by adding a genuine second primary-source domain — a Wayback Machine snapshot of
the same manufacturer page — per common.md's explicit inclusion of "Wayback snapshots of
[primary sources]" as valid evidence. No warning needed an unclearable explanation.

## 4. Factual errors / notable findings

- **`injector` mistagging** on Nova, Whisper, Bliss, Fusion, MOAB — see §1. Corrected.
- **Unresolved discrepancy on Nova (not corrected, flagged in-record):** the manufacturer's
  current live product JSON for the Nova (`https://www.cannabishardware.com/products/nova.json`,
  observed 2026-08-08) lists **"PID controller not included"** in its Important Notes. This
  contradicts the built-in-PID characterization used throughout the archive for the Nova —
  sourced from the ZenLeaf Engineering Update ("first ZenLeaf station with integrated PID")
  and TREF-0004's own canonical complete-system example ("ZenLeaf Nova base station (integrated
  PID)"). I did **not** change the `mains`/built-in-PID classification, because it's
  corroborated by multiple independent primary-source statements across the family and the
  brief itself directs Nova to `mains`; I recorded the live page's contradicting line as an
  explicit, cited discrepancy in TED-0007's Family Context section (new bullet + footnote 5)
  for the integrator to adjudicate — this is exactly the kind of new evidence a completeness
  pass shouldn't silently paper over, but also isn't mine to unilaterally resolve against three
  corroborating sources. Flagging this prominently: **integrator should decide whether this
  needs a fuller correction to the Nova record.**
- **Bliss's "external XLR output with its own temperature controller"** — re-read per the
  brief's explicit instruction to check what the hardware does. Concluded this describes a
  second built-in controller (not a user-supplied external PID), because nothing in the
  record says the user must supply their own controller for that output — unlike Whisper and
  Zion, which say so explicitly ("requires a user-supplied external PID controller"). Tagged
  `mains` only. Reworded the Temperature Control spec row for clarity rather than leaving the
  ambiguity for the next reader to re-derive.

## 5. Audit output

### `python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json`

Overall: `25 error(s), 14 warning(s) across 39 finding(s)` (other workers' files — expected,
per common.md, since other lanes were still in progress at the time of this run).

Filtered to this lane's seven files: **zero findings of any kind** (confirmed by grepping the
full output for each of TED-0007, TED-0029, TED-0030, TED-0031, TED-0032, TED-0033, TED-0041 —
no matches).

### `python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json`

```
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

Zero findings corpus-wide (not just for this lane) at the time of this run.

### `git status --porcelain`

```
 M content/devices/TED-0007.md
 M content/devices/TED-0008.md
 M content/devices/TED-0009.md
 M content/devices/TED-0010.md
 M content/devices/TED-0012.md
 M content/devices/TED-0013.md
 M content/devices/TED-0014.md
 M content/devices/TED-0015.md
 M content/devices/TED-0016.md
 M content/devices/TED-0019.md
 M content/devices/TED-0020.md
 M content/devices/TED-0021.md
 M content/devices/TED-0022.md
 M content/devices/TED-0023.md
 M content/devices/TED-0024.md
 M content/devices/TED-0026.md
 M content/devices/TED-0027.md
 M content/devices/TED-0029.md
 M content/devices/TED-0030.md
 M content/devices/TED-0031.md
 M content/devices/TED-0032.md
 M content/devices/TED-0033.md
 M content/devices/TED-0034.md
 M content/devices/TED-0035.md
 M content/devices/TED-0036.md
 M content/devices/TED-0041.md
 M content/devices/TED-0042.md
 M content/devices/TED-0043.md
 M content/devices/TED-0044.md
 M content/devices/TED-0045.md
 M content/devices/dynavap-m7.md
 M content/devices/mighty-plus.md
?? reports/ch-zenleaf-heads-260808-2055-level.md
?? reports/portables-b-260808-2055-level.md
```

This is a shared branch with six other concurrent lane workers, so the full status necessarily
shows everyone's in-flight edits. **My own edits are exactly and only**: `TED-0007.md`,
`TED-0029.md`, `TED-0030.md`, `TED-0031.md`, `TED-0032.md`, `TED-0033.md`, `TED-0041.md` (all
in my brief's file list) plus this report file. I did not touch any other file in the working
tree; the remaining modified/untracked entries belong to other lanes' workers.

DONE
