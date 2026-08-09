# Worker report — lane `portables-a`

Raised `content/devices/TED-0008.md`, `TED-0009.md`, `TED-0010.md`, `TED-0011.md`,
`TED-0017.md`, `TED-0018.md` to the record-completeness floor defined in `common.md` /
`TREF-0004`. All research was live web verification against manufacturer pages, not the
brief's orientation paragraph — see the deviation note below.

## 1. Per-record axis table

| Record | heating_mechanism | heat_generation | delivery_mode | operating_mode | power | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| TED-0008 TinyMight 2 | `convection` (pre-existing) | `resistive` (added) | `stem` (pre-existing) | `on-demand`, `session` (pre-existing) | `battery` (added) | Spec table: "stainless steel spiral heater, 70 W" → resistive (TREF-0004 names "TinyMight stainless spiral" as its own resistive example). "Single user-replaceable 18650" → battery. Delivery: confirmed live via `tinymightvape.com/tinymight-2` and `tinymightvape.eu/tinymight-2-guide` — the draw path is a removable glass tube/stem that is also the load chamber ("One 55 mm glass tube… Additional glass tubes"), not a fixed body mouthpiece, so `stem` (already tagged) is correct. |
| TED-0009 TinyMight OG | `convection` (pre-existing) | `resistive` (added) | `stem` (pre-existing) | `on-demand` (pre-existing) | `battery` (added) | Spec table: "ceramic heating element" → resistive (same category as TREF-0004's "E-Nano ceramic rod" example). "Single user-replaceable 18650" → battery. |
| TED-0010 E-Nano NXT | `convection` (pre-existing) | `cartridge-heater` (added) | `stem` (pre-existing) | `continuous-desktop` (pre-existing) | `mains` (added) | Spec table: "custom ceramic heating rod" + log/heat-block form factor → cartridge-heater (TREF-0004 names "E-Nano" directly as its own cartridge-heater example: "Log-vape heater cores (E-Nano, Woodscents)"). "120 V AC, ~15 W max" → mains. |
| TED-0011 E-Nano OG | `convection` (pre-existing) | `cartridge-heater` (added) | `stem` (pre-existing) | `continuous-desktop` (pre-existing) | `mains` (added) | Same as NXT: "custom ceramic heating rod" → cartridge-heater; "120 V AC, ~15 W max" → mains. |
| TED-0017 G Pen Elite II | `hybrid` (pre-existing) | `resistive` (added, inferred) | `direct-draw` (pre-existing) | `session` (pre-existing) | `battery` (added) | Spec table already hybrid conduction+convection, ceramic chamber. `resistive` is inferred, not manufacturer-stated verbatim — see uncertainty note below. "2100 mAh Li-ion… USB-C" → battery. |
| TED-0018 G Pen Dash+ | `hybrid` (pre-existing) | `resistive` (added) | `direct-draw` (pre-existing) | `session` (pre-existing) | `battery` (added) | Official FAQ (`gpen.com/pages/dash-plus-faq`, checked 2026-08-08): "conduction (vaporization via **direct contact with a heating element**)" — explicit "heating element" language, battery/USB-C powered, no flame/induction/halogen documented → resistive. "1800 mAh Li-ion… USB-C" → battery. |

**Deviation from the brief's orientation paragraph:** the brief states the TinyMights carry
"`direct-draw` delivery." I checked this live against `tinymightvape.com` and
`tinymightvape.eu` rather than taking it as given (as instructed) and found the opposite:
the draw path is a removable glass tube that doubles as the load chamber — this is TREF-0004's
own definition of `stem`, not `direct-draw` (which the standard defines by example as a
*fixed* "cooling unit mouthpiece," e.g. the Mighty+). The pre-existing `stem` tag on both
TinyMight records was already correct; I left it as-is and did not reclassify it.

## 2. Part numbers added

| Record | Part Number row | Source |
| --- | --- | --- |
| TED-0008 TinyMight 2 | Not published as a distinct identifier — the site's "Product Code" field just echoes the product name ("tinymight 2") | `tinymightvape.com/tinymight-2`, checked 2026-08-08 |
| TED-0009 TinyMight OG | Not published — no OG product page is live anymore; the storefront now lists only the TM2 | `tinymightvape.com`, checked 2026-08-08 |
| TED-0010 E-Nano NXT | `NXT-Wal_std` / `NXT-Maple_std` / `NXT-Cherry_std` (wood-specific Shopify variant SKUs) | `epicvape.com/products/e-nano-kit-nxt` (variant JSON), checked 2026-08-08 |
| TED-0011 E-Nano OG | Not published as a general model SKU — only discontinued, sold-out per-unit numeric listings (e.g. `2010029`, `211009`) | `epicvape.com/collections/the-original-e-nano`, checked 2026-08-08 |
| TED-0017 G Pen Elite II | Not published as a retail SKU — the dedicated product URL now redirects to the Dash+ listing; only regulatory IDs exist (ARTG Entry 526764, HC MDL 113029) | `gpen.com/products/g-pen-elite-ii-vaporizer` (redirects), `gpen.com/collections/g-pen-elite-ii`, `gpen.com/pages/elite-ii-faq`, `grencomedical.com`, checked 2026-08-08 |
| TED-0018 G Pen Dash+ | `GPD-001-AMZZ` — the manufacturer's own Shopify variant SKU | `gpen.com/products/g-pen-dash-plus-vaporizer.json`, checked 2026-08-08 |

Note on `GPD-001-AMZZ`: the `-AMZZ` suffix looks like an Amazon-channel naming convention, but
the value is embedded in Grenco's own `gpen.com` Shopify product JSON (their own store, not a
retailer page), so I treated it as the manufacturer's own SKU rather than a transcribed
third-party identifier. Flagging the naming pattern here so the integrator can override if
they know otherwise.

## 3. Warnings not honestly clearable

None outstanding. All six records now carry a Safety & Use Notes section, a Form Factor row,
and cite ≥2 distinct source domains (all six already had ≥2 domains before I touched them, or
gained a second when I added a new footnote — verified per-file below):

- TED-0008: `tinymightvape.com`, `tinymightvape.eu`, `youtube.com` (3)
- TED-0009: `tinymightvape.com`, `tinymightvape.eu` (2)
- TED-0010: `epicvape.com`, `manuals.plus` (2)
- TED-0011: `epicvape.com`, `manuals.plus` (2)
- TED-0017: `gpen.com`, `grencomedical.com` (2)
- TED-0018: `gpen.com`, `prnewswire.com` (2)

## 4. Factual/citation errors found

- **TED-0010 (E-Nano NXT), pre-existing:** the Safety & Use Notes section cited the alcohol/
  citrus-cleaner and 24/7-operation claims to `[^2][^4]` (the general "Info" page and the
  Returns/Warranty policy). I fetched both pages directly and neither contains that text. The
  actual source is a separate live page, the **E-Nano Quick Start Guide**
  (`epicvape.com/pages/e-nano-quick-start-guide`), which also adds two safety items the
  original note omitted (never leave a glass stem on a hot heater port; black spots indicate
  combustion). I added it as `[^7]` and repointed the safety bullet to it, and reused the same
  source for the new TED-0011 (OG) safety section. I did not delete the original claims — I
  corrected their citation and left the warranty-serial-number detail explicitly marked as
  carried from research-corpus notes rather than reconfirmed live, since I could not find a
  reachable page stating the serial's printed location.
- **TED-0011 (E-Nano OG):** the "Original E-Nano" storefront collection currently shows every
  listing as sold out, each under a one-off numeric handle (`2010029`, `211009`, etc.) rather
  than a stable model SKU — worth noting for whoever eventually audits EpicVape's broader
  catalog, since this pattern (per-unit listings instead of a model SKU) likely also affects
  other EpicVape records outside this lane.
- **TED-0017 (G Pen Elite II):** the manufacturer's dedicated product page
  (`gpen.com/products/g-pen-elite-ii-vaporizer`) now 301-redirects to the Dash+ listing, and
  the Elite II is absent from both `gpen.com/collections/dry-herb-vaporizers` and the general
  Elite II collection (which lists accessories only). The FAQ and regulatory pages are still
  live. This suggests the Elite II unit itself may be currently out of stock or discontinued
  on the manufacturer's own store — the record doesn't currently say this and I did not add an
  unverified discontinuation claim; flagging it for the integrator/manufacturer-page owner to
  confirm independently before stating it as fact.

## 5. Uncertainty flagged for integrator review

- **TED-0017 heat_generation (`resistive`):** unlike TED-0018, I could not find manufacturer
  text on the Elite II using the word "heating element" or equivalent. I inferred `resistive`
  from the power architecture (battery/USB-C, hybrid conduction+convection, no flame/induction/
  halogen documented anywhere) rather than a verbatim manufacturer statement, per common.md's
  "closest honest value" guidance. I added an explicit spec-table note saying this is inferred,
  not quoted. Confidence is high (no plausible alternative mechanism fits a USB-C dry-herb
  pen), but it is not a direct citation the way TED-0018's is.

## 6. Audit output

```
$ python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json
Record completeness audit: 13 error(s), 2 warning(s) across 15 finding(s)
```
None of the 15 findings reference TED-0008, TED-0009, TED-0010, TED-0011, TED-0017, or
TED-0018 (confirmed by grep against the six IDs — zero matches). All findings belong to other
workers' files (TED-0004/0005/0006/0025/0028/0037/0038/0039).

```
$ python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

```
$ git status --porcelain
```
Shows my six files as modified (`TED-0008.md` … `TED-0018.md`), plus a large number of other
`content/devices/*.md` files and `reports/*-level.md` files that belong to the other six
workers on this team, editing concurrently in the same working tree. I verified with
`git diff --stat` restricted to my six paths that my edits touch only those six files (51
insertions / 12 deletions total, no other file appears in that diff).
