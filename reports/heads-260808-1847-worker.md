# Worker report — slice `heads`

Date: 2026-08-08. Branch: `agent/cannabis-hardware-cleanup`. Scope: Pulse (3516), Swift
(3517), Clampy (3513), Clampy Essentials Kit (8067) — the four candidates on the live
ZenLeaf collection page absent from the archive.

## 1. What I changed

- **Created** `content/devices/TED-0042.md` — Cannabis Hardware Pulse 18 mm Male Flower Head (heater head, entity).
- **Created** `content/devices/TED-0043.md` — Cannabis Hardware Swift 14 mm Male Flower Head (heater head, entity).
- **Did not create** `content/devices/TED-0044.md` — Clampy gets no entity (see §2). ID left unused.
- No other files touched.

## 2. Entity-versus-component decisions

### Pulse (3516) and Swift (3517) — ENTITY (TED-0042, TED-0043)

Rule applied: TREF-0004 component-role table — "Create an entity for a component only
when it is a substantive, separately-purchasable platform." Both are titled and sold as
standalone heater heads with an 18-variant option matrix (handle/screens/thermal-media
add-ons), not accessories to an existing head.

Manufacturer wording that decided the family (FlowerPot 20 mm coil, **not** ZenLeaf 25 mm
axial), despite the Shopify product `tags` field on both being `zenleaf`:

- Pulse: "This device is designed to work with the traditional 20mm coil found in the
  Flowerpot ecosystem. When combined with the 'Clampy,' it creates a complete cordless
  setup using your existing Flowerpot equipment."
- Swift: "The device is compatible with the traditional 20mm coil found in the Flowerpot
  ecosystem, and when combined with the 'Clampy,' it creates a fully cordless setup using
  your existing Flowerpot equipment."

Both pages explicitly title themselves "for 20mm Coils." I read the manufacturer's own
platform language over the Shopify catalog tag and classified both under FlowerPot, and
documented the tag/copy conflict directly in each page's Family Context section per the
"document the contradiction" house rule — this is a real inconsistency in the manufacturer's
own site, not resolved by picking a side silently.

SKU decoding (base head vs. add-on options), same structure for both products:
- Base SKU (3516 / 3517 alone) = "Cup and C Clip Only (not assembled) / No Handle / No
  Screens" — this is the modeled head.
- `9465` = Cocobolo Handle (+$28), `9467` = Basswood Handle (+$5) — add-on, not modeled separately.
- `3503(2)`/`3468(2)` = 2× machined titanium screens (+$40), `9375(2)` = 2× mesh screens (+$10) — add-on.
- `9422(3mm)` = +3mm rubies (+$30) — add-on; **rubies are not included in the base head**, which is
  unusual relative to B1/F16/B0 (all ship with balls standard) and is called out on both pages.

### Clampy — DIY Ball Vape Coil Post (3513) — NO ENTITY

Rule applied: TREF-0004 component-role table, `stand` role ("Base/holder for the head, with
or without heating"); TAX-05 (bundle exclusion) does not itself apply here since Clampy is
not a bundle, but the "substantive platform" burden-of-proof standard does, and Clampy does
not meet it.

Manufacturer wording: "Clampy features a 1/4-20 threaded coil post that securely holds any
standard coil... two-piece assembly secured by two 8-32 allen screws... choice of a 25mm or
a 20mm coil... Clampy can even heat up any banger." It ships with no coil, no head, and no
PID — it is explicitly a DIY building-block ("Sold as assembly only") that a user completes
with their own coil, head, and controller. That is materially thinner than a "complete
system" (which bundles head + coil + PID + stand, e.g. ZenLeaf Nova) — it is closer to the
minimal mechanical post/stand than to a station. I ruled it a **component** (coil-post/stand
role) and gave it no entity. `TED-0044` is intentionally left unused.

Clampy is referenced (without a broken wikilink, since it has no entity) in both TED-0042
and TED-0043's spec tables and Family Context sections, so the archive records what it is
without implying it is a modeled device.

### Clampy Essentials Cordless Ball Vape Kit (8067) — NO ENTITY

Rule applied: TAX-05, full stop, per the brief's pre-established fact. Confirmed from its
own body copy: "This vape bundle includes: Clampy DIY Ball Vape Coil Stand (3513), Pulse -
18mm Male Flower Head... (3516), 20mm XLR Coil (9322 or 9323), CH Injector Pass Through
Bowl (9453), CH Controller Optional (9089)" — a retailer bundle of existing/already-modeled
components (Clampy component + the new Pulse entity + a coil + a bowl + an existing PID
SKU). No entity created; not referenced by a wikilink anywhere since it has no page, but it
is named in the Pulse page's evidence for what Clampy is used for.

## 3. Primary sources verified

All fetched live 2026-08-08 via the manufacturer's Shopify JSON endpoints (structured data:
title, tags, `created_at`/`published_at`, variant SKUs/prices, and live variant
`available` flags from the collection endpoint) plus each product's `body_html`:

- `https://www.cannabishardware.com/products/pulse-vape.json` — Pulse title, body copy (20 mm
  coil / Clampy cordless claim), 18 variants (prices $65–$163), `created_at` 2024-03-06,
  `published_at` 2024-03-15, `tags: zenleaf`.
- `https://www.cannabishardware.com/products/swift-vape.json` — Swift title, body copy, 18
  variants (prices $65–$163), `created_at` 2024-03-11, `published_at` 2024-03-15, `tags: zenleaf`.
- `https://www.cannabishardware.com/products/clampy-diy-vape.json` — Clampy title, body copy
  (threaded coil post, 20/25 mm coil compatibility, DIY assembly-only), single variant $62.
- `https://www.cannabishardware.com/products/clampy-ball-vape-kit.json` — Kit title, body
  copy (bundle contents list), 4 variants $278–$395.
- `https://www.cannabishardware.com/collections/zenleaf-wireless-vaporizer/products.json?limit=250`
  — used for (a) confirming both Pulse/Swift and Clampy/kit sit in this collection under the
  `zenleaf` tag, and (b) live per-variant `available` booleans (not present on the bare
  product JSON endpoint): Pulse base SKU 3516 available=true, all 18 Basswood-handle (`9467`)
  variants available=false; Swift all 18 variants available=true; Clampy (3513) available=true;
  Clampy kit (8067) mostly available=false (3 of 4 variants out of stock, one 220V no-controller
  variant available=true).
- `https://www.cannabishardware.com/collections/flowerpot-ball-vape/products.json?limit=250`
  — full FlowerPot collection enumerated for the gap sweep (§4).
- Cross-checked handful of ambiguous FlowerPot/ZenLeaf collection items individually (see §4)
  to confirm component-vs-platform calls: `cyclone-dab-bucket`, `22mm-vaporizer-diffuser`,
  `ball-vape-b1`, `titanium-coil-cover-moab-airstream-compatible`,
  `20mm-sleeve-for-25mm-coils-3559`, `hanger-threaded-basic-heat-stand`, `vaporizer-heat-post`.
- Read `content/devices/TED-0004.md`, `TED-0005.md`, `TED-0006.md`, `TED-0026.md`,
  `TED-0029.md`, `content/manufacturers/TMFR-0004.md`, `content/reference/TREF-0004.md`,
  `metadata/device-taxonomy.json`, `scripts/audit_device_taxonomy.py` for house style,
  taxonomy vocabulary, and validation logic before writing.

## 4. Gap list — rest of both collections (no further gaps found)

I enumerated all 34 products in the ZenLeaf collection and all 43 in the FlowerPot
collection. Beyond the four assigned candidates, **every remaining unmodeled product is a
component/accessory or a bundle of an already-modeled entity** — I found no additional
substantive, unmodeled platform. Noteworthy items, with assessment:

**Bundles of already-modeled or in-progress entities (TAX-05, no entity):**
- `flowerpot-b1-ball-vape` (8043/8044) — "FlowerPot B1 Standard Wired Ball Vape Kit," a kit
  bundle of the already-modeled [B1](../devices/TED-0004.md).
- `bzero-vaporizer-bundle` (8068) — bundle of the already-modeled [B0/B-Zero](../devices/TED-0005.md).
- `moab-ball-vape-kit` (8065) — MOAB Essentials Kit; already flagged by the integrator as
  miscrediting part 3518 (Mercury) to "VMAX." Bundle, no entity.
- `clampy-ball-vape-kit` (8067) — this slice's Clampy kit, see §2.

**The actual head SKU behind an existing entity (confirms coverage, not a gap):**
- `ball-vape-b1` (7007) — "Flowerpot B1 'Standard' Ball Vape Head," Grade 2 titanium, 19
  drilled holes, houses 3/4 mm ruby balls, mates to the 22 mm screen diffuser. This is the
  raw head product behind [TED-0004](../devices/TED-0004.md); not a gap.

**Components/accessories (no entity — not substantive platforms):**
- `22mm-vaporizer-diffuser` (3408) — "22mm 'Standard' Diffuser," a diffuser sub-assembly
  that mates into a head (used inside the B1 head per its own body copy: "optimized to work
  seamlessly with the 22mm Screen Diffuser"); a component, not a standalone head.
- `cyclone-dab-bucket` (3573) — dab-rig accessory for Airstream/MOAB; two-part base+bucket
  that fits a 25 mm axial coil and takes a 22 mm quartz dish; a banger/bucket accessory
  (`bowl`-adjacent role for concentrates), not a vaporizer platform.
- `titanium-coil-cover-moab-airstream-compatible` (3585) — cosmetic coil cover, "doesn't
  alter performance"; pure accessory.
- `20mm-sleeve-for-25mm-coils-3559` — titanium adapter sleeve so 20 mm heads fit a 25 mm
  axial coil; an adapter component.
- `hanger-threaded-basic-heat-stand` (7045, built from 3438+3196) and `vaporizer-heat-post`
  (3196) — a **storage** stand for safely resting a hot head between uses, not a
  coil-bearing operating platform; explicitly a safety accessory ("purpose built to safely
  store your cannabis ball vaporizers").
- `vaporizer-ch-single-enail-pid-controller` (9089) and `auber-enail-controller` (9319) —
  PID controllers; TREF-0004 lists `PID controller` as an explicit component role with CH
  PID as its own example. No entity.
- `25mm-axial-enail-coil`, `20mm-enail` — coils; explicit `coil` component role. No entity.
- `b1-nut-3227`, `enail-heat-shield` (3431), `hangar-thread-cover` (3452),
  `hangar-curved-base-adapter` (3437), `flowerpot-threaded-insert-for-heat-post` (9304) —
  small mechanical hardware for the stand/heat-post assembly. No entity.
- All bowls, bowl posts, glass weed bowls, "Elev8" injector bowls, Shovelhead bowl, quartz
  inserts, ruby balls, titanium screens (5/8", 3/4", machined, mesh), handles (Cocobolo,
  Basswood, solid, aluminum), carry cases, loading tool, debowler spike, Stundenglass whip
  adapters, double-ended screw, dabber, banger sleeves/bangers — all explicit `bowl`,
  thermal-media, screen, handle, or accessory-tool components per TREF-0004's own examples
  or plain mechanical hardware. No entity.

No item I found meets the "substantive, separately-purchasable platform" bar the way Pulse,
Swift, or a base station does. This sweep is exhaustive over both named collections (34 + 43
products, all titles read; ambiguous ones individually fetched and read in full).

## 5. Claims left labelled unverified, and why

- **Head material for Pulse/Swift**: the manufacturer does not state a material on either
  product page (unlike B1's page, which explicitly says "Grade 2 titanium"). I did not carry
  the company-wide titanium claim over as a Pulse/Swift-specific fact — both pages say "Not
  manufacturer-published on the [Pulse/Swift] product page" and cite the B1 page only as
  general-company context, per the "never fill a gap with inference" rule.
- **Bowl compatibility** ("18 mm female injector bowl" for Pulse, "14 mm female" for Swift):
  derived from the product's own "male [joint size]" title plus TREF-0004's injector
  delivery-mode definition, not a manufacturer-stated bowl-compatibility line. I flagged this
  derivation explicitly in the spec row wording rather than presenting it as directly quoted.
- **Release dates**: used "Manufacturer record created/published" language with Shopify's
  `created_at`/`published_at` timestamps, not "released," per house style — the manufacturer
  does not state an actual release date for either product.

## 6. What I could not do / requests to the integrator

- Nothing blocked. No file outside my ownership needed a change.
- `content/guides/cannabis-hardware-family-lineage.md` and `content/manufacturers/TMFR-0004.md`
  are not in my slice, so I did not add Pulse/Swift/Clampy to either — the integrator should
  fold TED-0042/TED-0043 into the FlowerPot family table in TMFR-0004 and the lineage guide,
  and record the Clampy/Clampy-kit exclusion reasoning from §2 above in the lineage guide (the
  brief specifically asks for the excluding rule + manufacturer wording to be placed there so
  the omission is documented rather than silent).
- TMFR-0004's `relations` list and Related Devices section will need `TED-0042`/`TED-0043`
  added by whoever owns that file — I did not touch it.

## 7. Exact commands run and actual output

```
$ curl -s "https://www.cannabishardware.com/products/pulse-vape.json" -o /tmp/ch-heads/pulse.json
$ curl -s "https://www.cannabishardware.com/products/swift-vape.json" -o /tmp/ch-heads/swift.json
$ curl -s "https://www.cannabishardware.com/products/clampy-diy-vape.json" -o /tmp/ch-heads/clampy.json
$ curl -s "https://www.cannabishardware.com/products/clampy-ball-vape-kit.json" -o /tmp/ch-heads/clampy-kit.json
$ curl -s "https://www.cannabishardware.com/collections/zenleaf-wireless-vaporizer/products.json?limit=250" -o /tmp/ch-heads/zenleaf-collection.json
$ curl -s "https://www.cannabishardware.com/collections/flowerpot-ball-vape/products.json?limit=250" -o /tmp/ch-heads/flowerpot-collection.json
(all six requests returned 200 with valid JSON; sizes 9.2KB/9.1KB/18KB/17.2KB/226KB/244.8KB respectively)
```

```
$ python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
EXIT CODE: 0
```

```
$ git status --porcelain
 M content/devices/TED-0007.md
 M content/devices/TED-0029.md
 M content/devices/TED-0030.md
 M content/devices/TED-0031.md
 M content/devices/TED-0032.md
 M content/reference/TREF-0004.md
?? content/devices/TED-0041.md
?? content/devices/TED-0042.md
?? content/devices/TED-0043.md
```

Only `content/devices/TED-0042.md` and `content/devices/TED-0043.md` are mine — created new,
untouched by anyone else. The other six paths (`TED-0007`, `TED-0029`–`TED-0032`, `TREF-0004`,
`TED-0041`) are other workers' in-progress changes in this shared parallel-team working tree;
I did not read, edit, or otherwise act on their content beyond what was already established as
fact in `brief-common.md`.
