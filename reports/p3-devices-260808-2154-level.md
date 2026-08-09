# p3-devices lane — record-completeness leveling report

Lane: `p3-devices`. Files owned: `content/devices/TED-0046.md` through `TED-0053.md`.
Branch: `agent/record-completeness-floor` (not committed, not pushed — per instructions).

## Summary

All eight records now carry a tag on all five taxonomy axes, a `Part Number` row, and a
component-role/form-factor row. REC-04 (safety) was cleared honestly on five records that
lacked it (TED-0046, 0048, 0049, 0050, 0052) using real manufacturer/manual content; two
already had a safety section (TED-0047, 0051, 0053). REC-06 (single-sourced) was cleared on
all four flagged records (TED-0046, 0048, 0052, 0053) by adding a genuine second-domain
source. Zero REC errors and zero REC warnings remain on these eight files or anywhere in the
corpus (see audit output below — the whole corpus reports 0 findings, meaning the other five
lanes have also landed).

## Per-record axis table

| Record | heating_mechanism | heat_generation | delivery_mode | operating_mode | power | Basis |
| --- | --- | --- | --- | --- | --- | --- |
| **TED-0046** FLYTLAB CTRL 2.0 | `conduction` (pre-existing) | `resistive` | `direct-draw` | `on-demand` | `battery` | Spec table: "Conduction via the attached 510 cartridge atomizer"; "Inhale-activated (draw-activated)"; "Internal lithium-ion battery". **See judgement call below — this is a bare battery, not a complete device.** |
| **TED-0047** Tronian Milatron | `convection` (pre-existing) | `resistive` (inferred) | `direct-draw` | `session` (pre-existing) | `battery` | Manual: 160–240 °C range, OLED session control; battery row "2300 mAh lithium-ion". heat_generation is an inference — manual describes "dual heating mechanism" without naming element technology; see judgement-call note in record. |
| **TED-0048** Flowermate V5 Nano | `hybrid` (pre-existing) | `resistive` (inferred) | `direct-draw` | `session` (pre-existing) | `battery` | Spec table: black ceramic heating chamber; "borosilicate glass mouthpiece that stows into the device"; "User-swappable 18650". heat_generation follows this archive's own precedent (ceramic chamber → `resistive`, per TREF-0004's own E-Nano/VapeXhale examples). |
| **TED-0049** XMAX V3 Pro | `hybrid` (pre-existing) | `resistive` (inferred) | `direct-draw` | `on-demand` + `session` (pre-existing) | `battery` | Spec table: stainless-steel oven; "User-replaceable 18650 lithium-ion cell". heat_generation inferred by the same stainless-chamber precedent (TinyMight spiral → `resistive`). |
| **TED-0050** XVape Aria | `hybrid` + `conduction` (pre-existing) | `resistive` (inferred) | `direct-draw` | `session` (added — was missing despite the spec row already saying "Session") | `battery` | TopGreen product-detail page (fetched live): "Ceramic with embedded heating element", "full ceramic conduction oven chamber"; "18650 3.7V 2550mah". |
| **TED-0051** Mig Vapor Khan | `conduction` (pre-existing) | `resistive` (inferred) | `direct-draw` + `water-tool` | `session` (added — spec row said "Session" but had no tag) | `battery` | VaporFi retailer listings confirm the Khan ships with **both** a threaded glass mouthpiece (direct-draw) and a separate Pyrex bubbler attachment (water-tool) — this is a genuine dual-delivery device, not a single-mode one. |
| **TED-0052** Goboof Alfa | `conduction` (pre-existing) | `resistive` (already stated in spec row — just tagged) | `direct-draw` | `session` (added — spec row said "Session" but had no tag) | `battery` | Spec table already said "resistive heater embedded in a hard-anodized aluminum oven"; ManualsLib fetch confirms direct-draw mouthpiece, no water-tool attachment. |
| **TED-0053** Vaporfection viVape 2 | `convection` (added canonical value — record previously only had non-canonical `forced-air-convection` descriptor, which does not satisfy REC-01) | `resistive` (inferred) | `whip` + `balloon` | `session` + `continuous-desktop` | `mains` | Spec table: "Forced-air convection over an updated glass-on-glass heating element"; "Whip and balloon (dual-mode)"; "AC mains, dual-voltage 110/240V". operating_mode follows this archive's own Volcano precedent (TED-0034/TED-0035 carry both tags for the same class of mains whip/balloon desktop unit). |

## TED-0046 battery judgement — written out in full

The FLYTLAB CTRL 2.0 is a bare 510-thread battery. It supplies regulated voltage to a
user-supplied oil cartridge; it has no chamber, no heating element, and no mouthpiece of its
own — those all belong to whatever cartridge the buyer screws in. TREF-0004's five axes
describe a *complete device*, and this SKU is a component of one.

The record-completeness audit has no "not applicable" value — REC-01 requires a tag on every
axis unconditionally. Rather than leave the record failing a mechanical gate over a
philosophical point, I tagged the closest defensible value on each axis and wrote the
reasoning into the record itself (`## Usage Notes`, TED-0046.md) so a reader is not misled
into thinking these are manufacturer-documented facts about the battery itself:

- **heat_generation → `resistive`**: the cartridge the battery drives is a resistive coil;
  the battery's entire function is delivering current to that resistive load.
- **delivery_mode → `direct-draw`**: the assembled unit's only draw path is the cartridge's
  own mouthpiece — there is no whip, balloon, or water tool option for a 510 battery.
- **operating_mode → `on-demand`**: this one is not a stretch — "inhale-activated
  (draw-activated)" is a textbook match for the on-demand definition.
- **power → `battery`**: unambiguous.

Flagged to the integrator: if the corpus later gains a `component`/`not-applicable` value
for cases like this, TED-0046 (and any other bare-battery or bare-cartridge record) should
be revisited rather than carrying tags that describe a cartridge the record doesn't actually
model.

## Part numbers

None of the eight manufacturers publish a distinct SKU/part number separate from the model
name. Each record's Part Number row states this explicitly with the URL(s) checked:

| Record | Row content | URL(s) checked |
| --- | --- | --- |
| TED-0046 | Not published; product page + `/products/ctrl-2-0.json` (404, not a live Shopify endpoint) | https://www.flytlab.com/product/ctrl-2-0/ |
| TED-0047 | Not published; manual filename embeds `82775600325` but the manual doesn't label it a part/model number, so it is not recorded as one | https://tronian.com/tronian-milatron.html, manual PDF |
| TED-0048 | Not published; product page + `/products/v5-nano.json` (404) | https://flowermate.com/product/v5-nano/ |
| TED-0049 | Not published as a distinct SKU — listings identify it only by model name "XMAX V3 PRO" | official listing, support hub |
| TED-0050 | Not published as a distinct SKU — listings identify it only by model name + colorway | official listing, support hub |
| TED-0051 | Not published; brand defunct, checked EcigGuide, Get-Vape, VaporFi, and the Khan manual | see record footnotes |
| TED-0052 | Not published; checked the 9-page ManualsLib-hosted manual and current retailer listings | https://www.manualslib.com/manual/991462/Goboof-Alfa.html |
| TED-0053 | Not published; brand dormant since ~2016–2017, vaporfection.com no longer resolves as the original site | Medical Jane, Dab Dude |

## Warnings that could not be fully/honestly cleared

None outstanding. REC-04, REC-05, and REC-06 are clear on all eight files as of this audit
run (see raw output below). Two records (TED-0047, TED-0051) already had a Safety section
before this lane started; the rest gained one from real sourced content — none is padded
with invented cautions.

## Factual issues found in existing records (not corrected, flagged instead)

1. **TED-0048 heating-ratio disagreement.** The manufacturer calls the V5 Nano's heating
   system "Hybrid" without a stated ratio; an independent 2024 Planet of the Vapes review
   instead characterizes its practical behavior as conduction-dominant. Both are now
   reproduced in the record's Usage Notes rather than reconciled — no manufacturer-published
   ratio exists to arbitrate between them.
2. **TED-0051 battery-capacity discrepancy.** The record's primary sources (EcigGuide,
   Get-Vape) state 2500 mAh; a Buy eCig Kits retailer listing titles the same kit "2200 mAh".
   Recorded as an unresolved discrepancy in Usage Notes, not corrected either direction.
3. **TED-0053 weight/dimension discrepancy.** Medical Jane's review states 7.75×5.25×2.5 in
   and 1.75 lb; a Dab Dude listing states 12×8×10 in and 3.65 lb for the same unit. Recorded
   as an unresolved discrepancy in Usage Notes.

None of these are corrected in either direction — both values are preserved with attribution,
per the evidence-discipline rule against deleting an existing sourced claim.

## Tooling note

`WebFetch` in this environment cannot reach `web.archive.org` (hard error: "Claude Code is
unable to fetch from web.archive.org"). This blocked a planned Wayback-snapshot check for
Vaporfection's original site. I substituted live secondary sources (Medical Jane, Dab Dude)
instead and noted the gap in TED-0053's Part Number row rather than silently omitting the
check.

## Audit output

### `python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json`

```
Record completeness audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

(Whole corpus — all 52 records, not just this lane's 8 — reports zero REC findings at the
time this report was written.)

### `python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json`

```
  [WARNING] VOCAB: TED-0046.md: tag '510' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0046.md: tag 'oil-cartridge' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0046.md: tag 'flytlab' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0047.md: tag 'digital' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0047.md: tag 'tronian' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0048.md: tag 'flowermate' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0048.md: tag 'smiss' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0048.md: tag '18650' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0049.md: tag 'xmax' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0049.md: tag 'topgreen' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0049.md: tag '18650' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0050.md: tag 'wax' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0050.md: tag 'xvape' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0050.md: tag 'topgreen' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0051.md: tag 'mig-vapor' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0051.md: tag 'defunct' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0051.md: tag 'bubbler' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0052.md: tag 'goboof' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0052.md: tag 'ireland' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0052.md: tag 'dial' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0053.md: tag 'forced-air-convection' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0053.md: tag 'glass-path' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0053.md: tag 'vaporfection' is not in the device taxonomy vocabulary
  [WARNING] VOCAB: TED-0053.md: tag 'defunct' is not in the device taxonomy vocabulary
Device taxonomy audit: 0 error(s), 24 warning(s) across 24 finding(s)
```

All 24 VOCAB warnings are on **pre-existing** descriptive tags (`510`, `flytlab`, `18650`,
`defunct`, `dial`, etc.) that were already in these records before this lane started. VOCAB
is a warning-severity, non-blocking rule (not part of REC-01…06, not a contradiction rule);
per the hard rules I did not add any new tag outside `metadata/device-taxonomy.json`, and I
did not remove these pre-existing descriptive tags since the brief scopes this lane to the
record-completeness floor, not a tag cleanup pass. Zero TAX-01…05 contradiction errors and
zero ADV errors on any of these eight files.

### `git status --porcelain`

```
 M content/devices/TED-0046.md
 M content/devices/TED-0047.md
 M content/devices/TED-0048.md
 M content/devices/TED-0049.md
 M content/devices/TED-0050.md
 M content/devices/TED-0051.md
 M content/devices/TED-0052.md
 M content/devices/TED-0053.md
```

Only the eight owned files plus this report were touched. No build, test suite, or
state-changing git command was run.
