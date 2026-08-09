# Lane report: storz-arizer

Worker lane covering the four best-documented records in the archive: Storz & Bickel
Volcano Classic (TED-0034), Volcano Hybrid (TED-0035), Mighty+ (`mighty-plus.md`,
id TED-0003), and Arizer Solo III (TED-0001). Goal: bring all four to the record-completeness
floor (REC-01…06) with primary-source evidence, per `/tmp/lvl/brief-storz-arizer.md` and
`/tmp/lvl/common.md`.

## Per-record axis table

### TED-0034 — Storz & Bickel Volcano Classic

| Axis | Tag(s) added/kept | Evidence |
| --- | --- | --- |
| heating_mechanism | `convection` (kept) | Product page: "due to its pure convection heating..." and manual: "hot air generator." https://www.storz-bickel.com/en-us/volcanoclassic |
| heat_generation | `cartridge-heater` (**new**) | Official Instructions for Use repeatedly names the element a "heating block" ("the heating block will automatically heat up"; "the temperature is measured at the heating block"), matching the taxonomy's own cartridge-heater definition ("resistance heater embedded in a heat block"). Corroborated by retailer copy naming a "high-performance heating cartridge" in a "food-safe aluminum heating block" (secondary, explicitly attributed) |
| delivery_mode | `balloon` (kept) | EASY VALVE balloon system, per product page and manual |
| operating_mode | `session`, `continuous-desktop` (kept) | Existing tags, consistent with "unlimited sessions" marketing and always-on analog design |
| power | `mains` (**new**) | Spec row: "AC mains (220–240 V / 50–60 Hz or 110–120 V / 50–60 Hz...)", official IFU |

### TED-0035 — Storz & Bickel Volcano Hybrid

| Axis | Tag(s) added/kept | Evidence |
| --- | --- | --- |
| heating_mechanism | `convection` (kept) | Product page/manual: "hot air generator"; manufacturer states the "Hybrid" name refers to dual balloon+tube delivery, not to hybrid heating |
| heat_generation | `cartridge-heater` (**new**) | Official IFU: "the temperature is measured at the heat exchanger"; "the heat exchanger has finished warming up." Same reasoning as the Classic (electrically heated block/exchanger assembly), corroborated only by secondary retailer language for the sibling Classic/Digit (explicitly flagged as not confirmed against the Hybrid's own manual) |
| delivery_mode | `balloon`, `whip` (kept) | "1 device, 2 systems" — EASY VALVE balloon and Tube Kit, per product page |
| operating_mode | `session` (kept) | Existing tag |
| power | `mains` (**new**) | Spec row: AC mains, per IFU and live Technical Overview article |

### TED-0003 — Storz & Bickel Mighty+ (`mighty-plus.md`)

| Axis | Tag(s) added/kept | Evidence |
| --- | --- | --- |
| heating_mechanism | `hybrid` (kept) | Manufacturer's cross-device explainer: "a patented combination of hot air convection and additional conduction heating," chamber itself heated in addition to pre-heated air. https://support.storz-bickel.com/hc/en-us/articles/35886728106257-All-Devices |
| heat_generation | `resistive` (**new**) | No specific sub-type (rod/coil/cartridge) is published by Storz & Bickel for the Mighty+ specifically. `resistive` is the general, honest value for an electric resistance heater; recorded the uncertainty directly in the spec row rather than guessing `cartridge-heater` |
| delivery_mode | `direct-draw` (kept) | Cooling-unit mouthpiece, matches TREF-0004's own example for this exact product |
| operating_mode | `session` (kept) | Existing tag, spec row "Operation Mode: Session" |
| power | `battery` (**new**) | Two internal Li-ion cells, per support Technical Overview |

**TAX-04 (dual power) — explicitly NOT applied.** The Mighty+ genuinely supports pass-through
charging ("with a power supply that provides enough current, the batteries are bridged... the
display confirms this function with a 'dct' signal," per official support). I confirmed the
device does **not** run on mains power with no batteries fitted — it is a battery device that
can be topped up while in use, not a dual-power unit. I did **not** tag `mains` alongside
`battery`. Separately: `scripts/audit_device_taxonomy.py`'s TAX-04 check
(`audit_device_taxonomy.py:102-104`) has **no exception for documented dual power** despite
`metadata/device-taxonomy.json`'s own rule text and TREF-0004 both saying dual power is an
allowed exception — the code hard-fails on `battery`+`mains` co-occurring, full stop. Flagging
this for the integrator: even a genuinely dual-power device (if one exists elsewhere in the
corpus) cannot currently pass the audit. I avoided the conflict entirely here because the
underlying fact (no direct mains operation without batteries) supports `battery`-only anyway,
but another lane's device may not be so lucky.

### TED-0001 — Arizer Solo III

| Axis | Tag(s) added/kept | Evidence |
| --- | --- | --- |
| heating_mechanism | `hybrid` (kept) | Manufacturer: "hybrid heat ratio of 80% Convection, 20% Conduction," "Instant Heating Ceramic Convection Technology." https://arizer.com/solo3/ |
| heat_generation | `resistive` (**new**) | Manufacturer names it a "ceramic" heating element but never uses "resistive"/"coil"/"cartridge." TREF-0004's own axis-2 table lists ceramic heating elements (E-Nano ceramic rod, VapeXhale ceramic element) under `resistive`, so I applied the same equivalence rather than inventing a value |
| delivery_mode | `stem` (kept) | Glass Aroma Tube system |
| operating_mode | `session`, `on-demand` (kept) | Existing tags, "Session Mode and On Demand Mode" |
| power | `battery` (**new**) | Internal lithium-ion battery, not user-replaceable, per product page |

`mains` was **not** added despite "Use While Charging" support, for the same reasoning as the
Mighty+: charging while in use is not mains-direct operation.

## Part numbers added

| Record | Part Number | Source |
| --- | --- | --- |
| TED-0034 (Volcano Classic) | `01 00 C-1` | Storz & Bickel's own product page (article number shown on-page). https://www.storz-bickel.com/en-us/volcanoclassic |
| TED-0035 (Volcano Hybrid) | `01 00 H-1` | Storz & Bickel's own product page. https://www.storz-bickel.com/en-us/volcanohybrid |
| TED-0003 (Mighty+) | `01 01 MY` | Storz & Bickel's own product page; corroborated by the official manual's own filename slug ("01-01-my-mighty-plus-vaporizer-manual"). https://www.storz-bickel.com/en/mighty-plus |
| TED-0001 (Solo III) | **Not published** as a discrete SKU/part code on Arizer's own site (checked the product page, the support/warranty page, and the owner's manual — none carry one; Arizer's WooCommerce product page exposes no visible SKU field). Stated explicitly in the record, plus the one genuinely manufacturer-adjacent identifier I could verify: UPC `628078802274` for the Intergalactic (Black) colorway, disclosed in the CPSC recall notice (26-565) | https://arizer.com/solo3/, https://www.cpsc.gov/Recalls/2026/... |

I deliberately did **not** use a "AR-3815-656675"-style SKU surfaced by a web search — it was
attributed by the search tool to "official Arizer retail listings" without ever quoting a page
that actually shows it, and I could not independently verify it traces to Arizer itself rather
than a third-party retailer's internal SKU. Per the evidence rule, a wrong tag/identifier is
worse than an honest gap, so I left it out rather than transcribe an unverified number.

## Certification / temperature-accuracy data added

Folded into existing spec rows only (no new row types invented, per brief):

- **Volcano Classic** — Temperature Control row: official IFU states actual air temperature
  fluctuates **± 5 °C (± 9 °F)** around the set point during the heating block's cycle.
- **Volcano Hybrid** — Power row: **Protection Class II (double insulated)**; TÜV SÜD-tested to
  **EN 60335-1, UL 499, CAN/CSA-22.2 No. 64-M91**; complies with EU LVD 2014/35/EU and EMC
  2014/30/EU. Sourced from both the official IFU and the live `support.storz-bickel.com`
  Technical Overview article (independently confirms Protection Class II).
- **Mighty+** — Charging row: max. power consumption **≈45 W**, rated operating temperature
  **5 °C–35 °C**, compliance **IEC 60335, EN 55011** (consumer standards, explicitly
  distinguished from the medical-device MDR certification already documented in the record).
- **Solo III** — No additional certification data found beyond the existing warranty terms;
  Arizer's support page only claims vague "international safety certifications" with no
  standard named, so I did not add an unverifiable claim.

## Warnings not honestly clearable

None. All four records already had, or now have, a Safety section, a form-factor row, and
more than one source domain:

- TED-0034: already had "Safety & Use Notes" and 5 source domains — no changes needed there.
- TED-0035: already had "Safety & Use Notes" and 6 source domains — no changes needed there.
- TED-0003 (Mighty+): **added** a new "## Safety Notes" section (it had none before — this
  would have been a REC-04 warning) sourced from the official support "Operation" article's
  pre-use safety instructions; added `Part Number` and `Form Factor` rows for REC-02/05; already
  had 3 source domains for REC-06.
- TED-0001: already had "Safety & Recall Notice" and 4 source domains — no changes needed there.

## Factual issues found and fixed

1. **Broken citation URL, Mighty+ [^5].** The existing footnote pointed at
   `.../articles/36136284918585-Technical-Overview`, which now 404s. The correct current URL is
   `.../articles/36136284925585-Technical-Overview` (verified live). Fixed in place; noted the
   correction in the footnote text itself.
2. **Ambiguous heating-mechanism claim, both Volcanos — flagged, not changed.** Storz & Bickel's
   cross-product support FAQ ("All Devices" — "How Is The Vapor Created?") states *all* S&B
   devices, without exception, use "a patented combination of hot air convection and additional
   conduction heating," which read literally could argue for `hybrid` on the Volcanos too. I did
   **not** apply this: the brief explicitly frames the Volcanos as "desktop mains convection
   units," and the model-specific product pages and Instructions for Use for both Classic and
   Hybrid consistently and repeatedly describe pure forced-air convection with no
   electrically-heated integral chamber (unlike the Mighty+/Crafty+, whose filling chamber *is*
   the heated body). I judged the generic FAQ blurb less precise than the model-specific
   documentation and left `heating_mechanism` as `convection`. Recording this here in case the
   integrator or a future pass wants to revisit it with the FAQ as a lead.
3. **Mighty+ had no heat_generation tag, no Part Number row, no Safety section, and no power
   axis tag at all** before this pass — the record looked complete (rich cleaning/accessories
   sections) but was actually missing 3 of 5 required axes. Now complete.

## Audit output

```
$ python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json
... (18 findings total, all for TED-0004, TED-0005, TED-0006, TED-0018, TED-0025, TED-0028,
     TED-0037, TED-0038, TED-0039 — none of which are in this lane's file list)
Record completeness audit: 14 error(s), 4 warning(s) across 18 finding(s)
```

Zero REC-01/02/03 errors and zero REC-04/05/06 warnings reference TED-0034.md, TED-0035.md,
mighty-plus.md, or TED-0001.md — confirmed by grepping the full output for those four filenames
(no matches).

```
$ python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

Zero errors/warnings overall — acceptance criterion met.

```
$ git status --porcelain
```

Shows my four owned files (`TED-0034.md`, `TED-0035.md`, `mighty-plus.md`, `TED-0001.md`) as
modified, plus a large number of other workers' concurrent changes across the rest of
`content/devices/` and other `reports/*.md` files from this same seven-agent run — none of
which I touched. I did not run any build, test suite, or state-changing git command.

DONE
