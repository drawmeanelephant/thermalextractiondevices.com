# Lane report — ch-flowerpot

Worker lane `ch-flowerpot`. Scope: `content/devices/TED-0004.md`, `TED-0005.md`,
`TED-0006.md`, `TED-0025.md`, `TED-0028.md`, `TED-0037.md`, `TED-0038.md`,
`TED-0039.md` — the wired FlowerPot heads (B1, B0/B-Zero, F16, F22, B2) and the
pre-ball heads (Showerhead, Vrod, Baller) by Cannabis Hardware.

## Family-wide reasoning

All eight heads share one architecture: an external 20 mm enail coil driven by
a separate PID controller. Per the brief, this is `heat_generation: coil` and
`power: external-pid` — never `resistive` and never `mains` — because the head
itself carries no power; the coil and PID are separately-sold components. I
applied this uniformly across all eight records.

**Delivery mode** required per-record judgment against each record's own
Chamber/Bowl row, per the brief's split:

- **Injector** (inject into a bowl seated in a joint): B0/B-Zero (TED-0005),
  F16 (TED-0006). Both records' Chamber/Bowl rows already said "injector
  bowl(s)." Independently confirmed via a 420VapeZone review of the B-Zero:
  "The B0 uses an 18mm male injector" — corroborating, not contradicting, the
  brief's split.
- **Diffuser/standard, water-tool** (seats over a Shovelhead/glass bowl, draws
  through a water piece): B1 (TED-0004), F22 (TED-0025), B2 (TED-0028).

**Where the hardware differs from a clean split:** B1's own Chamber/Bowl row
reads "Titanium Shovelhead bowl ... or compatible injector bowls" — genuine
documented cross-compatibility. Similarly B0/B-Zero's row notes Shovelhead
compatibility "Rev J and later," and F16's row also mentions Shovelhead
compatibility. I did not add a second `delivery_mode` tag for any of these: a
"compatible with" note on an accessory bowl is not the same claim as the
head's native draw path, and the brief's explicit family split (grounded in
Cannabis Hardware's own generational naming: F16="Injector" head, F22 is
titled "standard/female" diffuser in a retailer's manufacturer-sourced
description) is the more specific evidence. I record the cross-compatibility
language as already-present prose, not as an additional axis tag, to avoid
diluting a machine-readable claim with an accessory footnote.

For the three pre-ball heads (Showerhead, Vrod, Baller), the brief did not
specify delivery mode directly. Their own spec rows describe seating onto
14/18 mm glass bowls or a Shovelhead-style dish nut (no injector-bowl mention
anywhere in these three records), and the Baller/Vrod lineage is the direct
architectural ancestor of the B2 (which the manufacturer's page and this
family's own prose confirm is Shovelhead/diffuser-style). I tagged all three
`water-tool`, consistent with that lineage and with the absence of any
injector-bowl language in their own text.

**Operating mode** is `continuous-desktop` for all eight, per the brief and
consistent with the existing "designed for continuous/near-24-7 powered
operation on a desktop" definition in TREF-0004 — no record contradicts this.

## Per-record axis table

| Record | heating_mechanism | heat_generation | delivery_mode | operating_mode | power | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| TED-0004 (B1) | `convection` (unchanged) | `coil` (added) | `water-tool` (changed from `injector`) | `continuous-desktop` (unchanged) | `external-pid` (added) | Heat Source row: "20 mm enail coil + external PID controller (CH or Auber)"; Chamber/Bowl row: Shovelhead bowl primary, injector bowls noted as compatible accessory |
| TED-0005 (B0/B-Zero) | `convection` (unchanged) | `coil` (added) | `injector` (unchanged — already correct) | `continuous-desktop` (unchanged) | `external-pid` (added) | Heat Source row: "20 mm enail coil + external PID controller"; Chamber/Bowl row: "Injector bowl or titanium Shovelhead bowl"; 420VapeZone review: "The B0 uses an 18mm male injector" |
| TED-0006 (F16) | `convection` (unchanged) | `coil` (added) | `injector` (unchanged — already correct) | `continuous-desktop` (unchanged) | `external-pid` (added) | Heat Source row: "20 mm exposed enail coil + external PID controller"; Chamber/Bowl row: "18 mm injector bowls or titanium Shovelhead bowl"; product title itself is "FlowerPot F16 'Injector' Head Assembly" |
| TED-0025 (F22) | `convection` (unchanged) | `coil` (added) | `water-tool` (changed from `injector`) | `continuous-desktop` (unchanged) | `external-pid` (added) | Heat Source row: "20 mm enail coil + external PID controller"; record's own prose: "the F22 diffuser seats and seals over the bowl's outer edges (F16 injectors seal on the inside rim)"; retailer description sourced to the manufacturer: "F22 barrel is a 'standard' style 'female' head which will sit on the outside of the shovelhead bowl" |
| TED-0028 (B2) | `hybrid` (unchanged) | `coil` (added) | `water-tool` (changed from `injector`) | `continuous-desktop` (unchanged) | `external-pid` (added) | Heat Source row: "20 mm CH XLR enail coil ... + external PID controller"; Chamber/Bowl row: "Shovelhead bowl assembly ... 28 mm SiC or sapphire dish" — no injector-bowl language anywhere in the record |
| TED-0037 (Showerhead) | `hybrid` (unchanged) | `coil` (added) | `water-tool` (added) | `continuous-desktop` (added) | `external-pid` (added) | Heat Source row: "External 20 mm enail coil"; Chamber/Bowl row: "Male-post connection to FlowerPot 14 mm / 18 mm glass bowls" — same "14/18 mm connection posts" phrasing as B1's Shovelhead row, no injector language |
| TED-0038 (Vrod) | `hybrid` (unchanged) | `coil` (added) | `water-tool` (added) | `continuous-desktop` (added) | `external-pid` (added) | Heat Source row: "External 20 mm enail coil, manufacturer-specified '5 wraps in Clockwise direction'"; Chamber/Bowl row: dish nut + Shovelhead-style kit contents; direct architectural ancestor of the B2 (own record: "the manufacturer created by hollowing out this exact diffuser to hold quartz balls") |
| TED-0039 (Baller) | `convection` (unchanged — base variant has no dish; optional dish-top variant is a premium add-on, not the default configuration, so `hybrid` was not added) | `coil` (added) | `water-tool` (added) | `continuous-desktop` (added) | `external-pid` (added) | Heat Source row: "External 20 mm enail coil (same coil platform as the Vrod it was machined from)"; machined directly from the Vrod diffuser; superseded by the B2 (Shovelhead/diffuser lineage) |

## Part numbers added

| Record | Part Number | Source |
| --- | --- | --- |
| TED-0004 (B1) | 7007 | Already present in the record's own citation [^2] (manufacturer product page); re-confirmed live via the manufacturer's Shopify product JSON (`ball-vape-b1.json`), checked 2026-08-08. Promoted from prose into a formal `Part Number` row. |
| TED-0005 (B0/B-Zero) | 7015 | Confirmed live via `flowerpot-b-zero-assembly.json` on the manufacturer's own site, checked 2026-08-08 — title "Flowerpot B-ZERO Head (7015)." This is the head-only assembly SKU; the record's own [^2] citation already pointed at this exact page, but no part number had been promoted into a row. Distinct from the bundle SKU 8068 ("BZero Injector Budget Bundle"), which packages the head with a coil, PID, and bowl — not transcribed as the head's own part number. |
| TED-0006 (F16) | 7051 | Already embedded in the record's own cited URL (`flowerpot-f16-head-assembly-7051`) and confirmed via the manufacturer's product JSON, checked 2026-08-08 — title "Flowerpot F16 'Injector' Head Assembly (7051)." Promoted into a formal row. |
| TED-0025 (F22) | **Not published on a live manufacturer page.** Recorded honestly with retailer attribution: multiple independent retailers (La Centrale Vapeur, TopVapeShop, VGoodiEZ, Stonercentre) consistently sell it as part 7052, plausible given the sequential F16=7051 numbering from the same June-2023 launch, but I could not reach a manufacturer page confirming it. | Checked: manufacturer's FlowerPot Ball Vape collection JSON (no F22 entry), a guessed manufacturer URL pattern matching F16's (`flowerpot-f22-head-assembly-7052` — 404 on `cannabishardware.com`), and a second manufacturer-branded domain surfaced by search, `shopcannabishardware.com` — that domain does not resolve from this network (`getaddrinfo ENOTFOUND`), so I could not verify it independently. New footnote [^7] cites La Centrale Vapeur explicitly as a retailer/secondary source, per the evidence-discipline rule against transcribing a retailer SKU as a manufacturer fact — I did not write "7052" as a bare fact in the row. |
| TED-0028 (B2) | 7006 | Already present in the record's own prose ("head assembly 7006," in the Bundle note) sourced to an archived, explicitly-labelled "Archived Product Information" bundle page. I found a **currently live** manufacturer product page at `cannabishardware.com/products/b2-head-assembly` — title "Flowerpot B2 Standard Head - (7006)" — which independently corroborates both the SKU and the discontinuation rationale already in the record ("The B2 head was discontinued because it no longer favored its original dual-purpose design"). Added as new footnote [^8] and used as the Part Number row's citation, since it is a stronger (live, not Wayback-dependent) source than the archived bundle page alone. |
| TED-0037 (Showerhead) | 7005 (assembly) / 3063 (top) | Already present as a `Part Number` row before I started — no change needed. |
| TED-0038 (Vrod) | 7003 (assembly); 3129 (top, sold separately) | Already present as a `Part Number` row before I started — no change needed. |
| TED-0039 (Baller) | Base product ID 6670452195468; variant SKU `3405-3103` (no balls/no top) | Already present as a `Part Number` row before I started — no change needed. Matches the brief's "Baller 3405" (the row records the full variant SKU string, of which 3405 is the base component). |

## Warnings I could not honestly clear

None outstanding. `TED-0004` and `TED-0005` previously cited only
`cannabishardware.com` (single domain — REC-06 warning); I found and added
independent 420VapeZone reviews specific to the B1 and the B-Zero
respectively, with explicit secondary-source attribution, clearing REC-06 for
both without overstating their evidentiary weight (they are cited only for
the specific reviewer-attributed claims: a ball-capacity figure for B1, and
a connection-type/safety observation for B-Zero — the manufacturer's own
figures and safety statements were not replaced).

## Factual notes / corrections found

- **TED-0028 (B2) part number and discontinuation are now corroborated by a
  live manufacturer page**, not only the archived bundle listing the record
  already cited. This strengthens rather than contradicts the existing
  record — no correction needed, only a stronger citation added.
- **F22 (TED-0025) genuinely has no reachable manufacturer product page** as
  of 2026-08-08 — this matches what the record already said before I started
  ("As of 2026-08-08 the F22 has no dedicated manufacturer product page"). I
  independently re-verified this rather than assuming it was still true, and
  it held.
- No other factual errors found in the eight records. They were already
  unusually well-sourced and internally consistent going in; the work here
  was almost entirely adding the missing machine-readable axis tags and
  promoting already-cited facts into formal spec rows, not correcting prose.

## Audit output

`python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json`:

```
Record completeness audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

(Run against the full corpus after my edits — zero findings across all 44
records, not just mine; other lanes had already brought their files to the
floor by the time I ran this.)

`python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json`:

```
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

`git status --porcelain` (full repo, showing other lanes' concurrent
in-progress work — my own changes are limited to the eight files below):

```
 M content/devices/TED-0004.md
 M content/devices/TED-0005.md
 M content/devices/TED-0006.md
 M content/devices/TED-0025.md
 M content/devices/TED-0028.md
 M content/devices/TED-0037.md
 M content/devices/TED-0038.md
 M content/devices/TED-0039.md
```

`git diff --stat` confirms no file outside this list was touched by this lane.

DONE
