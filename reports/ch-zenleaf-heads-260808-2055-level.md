# Lane report: ch-zenleaf-heads — 2026-08-08

Files owned: `content/devices/TED-0026.md` (Mary), `TED-0027.md` (Jane), `TED-0036.md`
(Mercury), `TED-0044.md` (VMAX), `TED-0045.md` (VMAX Injector), `TED-0042.md` (Pulse),
`TED-0043.md` (Swift). No other file was touched.

## 1. Per-record axis table and evidence

| Record | heating_mechanism | heat_generation | delivery_mode | operating_mode | power | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| TED-0026 Mary | `hybrid` (already tagged) | `coil` (added) | `water-tool` (fixed — was `injector`) | `continuous-desktop` (already tagged) | `mains` (added) | Heating: record's own Heating Method row cites the manufacturer's "additional element of 'conduction'" language for Mary specifically (verified live against the source blog, quote confirmed: "It is also capable of creating an additional element of 'conduction' to the heating equation…" — distinct from Jane's "pure convection" framing). heat_generation: Heat Source row states "25 mm axial coil inside a ZenLeaf base station." delivery_mode: Component Role row identifies Mary as the standard/female (22 mm) diffuser that seats in a bowl — `injector` was a pre-existing tagging error I corrected to `water-tool` (see §4). power: Power row states "heated by a ZenLeaf base station (AC mains)." |
| TED-0027 Jane | `convection` (already tagged) | `coil` (added) | `injector` (already tagged, correct) | `continuous-desktop` (already tagged) | `mains` (added) | Heating: Heating Method row + manufacturer blog quote "minimal contact and therefore a more pure convection experience." heat_generation/power: same base-station Heat Source/Power rows as Mary. delivery_mode: Component Role names Jane the injector (18 mm male) diffuser. |
| TED-0036 Mercury | `convection` (already tagged) | `coil` (added) | `water-tool` (added — body already had the row, frontmatter tag was missing) | `continuous-desktop` (added) | `mains` (added) | All four newly-added tags were already stated in the record's own spec rows (Heat Source: "25 mm axial coil, via a ZenLeaf base station…"; Delivery Mode row: "water-tool"; Power row: "AC mains") — this record simply hadn't propagated its own prose into frontmatter tags. |
| TED-0044 VMAX | `hybrid` (already tagged) | `coil` (added) | `water-tool` (added — body already had the row) | `continuous-desktop` (added) | `mains` (added) | Heating Method row already quotes the manufacturer's explicit heat-soaking/conduction language ("layering even more intensity onto the convection experience") — this is the brief's documented hybrid exception, confirmed by the record's own citation [^1]. Other three tags mirror existing Heat Source/Delivery Mode/Power rows. |
| TED-0045 VMAX Injector | `convection` (already tagged) | `coil` (added) | `injector` (added) | `continuous-desktop` (added) | `mains` (added) | Heating Method row quotes the manufacturer's contrast with VMAX: "almost entirely convection-based." delivery_mode: I tagged `injector` only, not `injector`+`water-tool`, even though the record's own Delivery Mode row reads "water-tool + injector" — TREF-0004 defines `injector` as already including "draw through a water piece," and I kept this record's tagging consistent with Jane/Pulse/Swift (injector-joint heads tagged `injector` alone) rather than introducing an inconsistent double-tag on this one record. Noted here since it's a judgment call the integrator may want to revisit. |
| TED-0042 Pulse | `convection` (already tagged) | `coil` (added) | `injector` (added) | `continuous-desktop` (added) | `external-pid` (added) | heat_generation/delivery_mode from existing Heat Source ("20 mm exposed enail coil + external PID controller") and Joint Size rows. power: the brief explicitly directs `external-pid` (not `mains`) for Pulse/Swift because the coil and PID are separate purchasable components, not an integrated base station, matching TREF-0004's `external PID/controller` definition exactly (FlowerPot coil + CH/Auber PID). I reworded the existing Power row from "AC mains via coil + PID" to name the axis and tag explicitly, without deleting the underlying fact. |
| TED-0043 Swift | `convection` (already tagged) | `coil` (added) | `injector` (added) | `continuous-desktop` (added) | `external-pid` (added) | Same reasoning as Pulse — identical architecture, own Heat Source/Joint Size/Power rows. |

## 2. Part numbers

- **Mercury (3518), VMAX (3574), VMAX Injector (3580), Pulse (3516), Swift (3517)** — all
  already had correct Part Number rows citing the manufacturer's own live product pages,
  matching the numbers given in the brief. No change needed.
- **Mary (3483)** and **Jane (3484)** — neither record had a Part Number row, and both
  products are delisted (confirmed 404 live, 2026-08-08). I recovered both part numbers
  from Wayback Machine snapshots of the manufacturer's own now-dead product pages:
  - Mary: `https://web.archive.org/web/20240225074747/https://www.cannabishardware.com/products/mary_flower_diffuser` (2024-02-25) — page titled "Mary Female Flower Diffuser (3483)."
  - Jane: `https://web.archive.org/web/20240425070427/https://www.cannabishardware.com/products/jane_flower_diffuser` (2024-04-25) — page titled "Jane Male Flower Diffuser (3484)."
  Both snapshots are the manufacturer's own archived copy, not a retailer, so they count
  as primary-source citations for REC-03 as well as REC-02.
  - Bonus find: both snapshots directly state "Approximately 110-120 x 3mm rubies until
    full," which resolves the "Unverified"/derived-inference caveat previously sitting in
    both records' Thermal Media rows. I added this as a factual clarification alongside
    (not replacing) the existing derived-comparison text, per the "never delete an existing
    sourced claim" rule.

## 3. Warnings

- REC-04 (Safety) and REC-05 (Component Role) were already satisfied on all seven records
  before I touched them — no action needed.
- REC-06 (source-domain diversity): all seven records previously cited only
  `cannabishardware.com`. I cleared this warning on all seven by adding a second-domain
  citation:
  - Mary, Jane: the Wayback part-number citations above already introduce `web.archive.org`
    as a second domain (dual-purpose: satisfies REC-02/03 evidence and REC-06 in one move).
  - Mercury, Pulse, Swift: added a Wayback snapshot of each live product page
    (2025-10-09 for all three) as an archival-corroboration citation.
  - VMAX, VMAX Injector: **no Wayback snapshot exists yet** for either page (both checked
    directly via the Wayback Availability API — `no_archived_content_available`), consistent
    with their very recent publish date (2025-10-02). Instead I added a secondary-retailer
    citation to a French retailer (lacentralevapeur.com, SKUs `CH_3574`/`CH_3580`) that
    independently republishes the same specs (capacity, screens, heat-soak/convection
    framing), explicitly labeled as secondary/corroboration-only, not primary evidence.
  All seven now cite ≥2 distinct domains; `audit_record_completeness.py` confirms zero
  REC-06 findings for this lane.

## 4. Factual error found and corrected

- **TED-0026 (Mary) carried an incorrect `injector` delivery-mode tag.** Mary is the
  standard/female (22 mm) diffuser — per TREF-0004's own definition, `injector` describes
  a male head that injects into a joint, while a female/standard head that seats directly
  in a bowl is `water-tool`. Jane (the true injector counterpart, 18 mm male) correctly
  carried `injector`; Mary appears to have inherited the same tag by copy-paste when the
  pair was first created, before the delivery-mode axis existed as a distinct concept. I
  removed `injector` and added `water-tool` to Mary's frontmatter, and added an explicit
  Delivery Mode spec row to both Mary and Jane (mirroring the Mercury/VMAX/VMAX Injector
  convention) so the tag is now grounded in the record's own table rather than only in
  frontmatter.

## 5. Judgment call flagged for the integrator

- TED-0045 (VMAX Injector)'s own Delivery Mode row literally reads "water-tool + injector,"
  but I tagged only `injector` in frontmatter to stay consistent with how Jane/Pulse/Swift
  (the other three injector-joint heads) are tagged. If the integrator prefers evidence-literal
  double-tagging for VMAX Injector specifically, `water-tool` can be added without contradicting
  any TAX rule — I left it out for family-wide tagging consistency rather than per-record
  literalism, and want that call visible rather than silent.

## 6. Audit output

`python3 scripts/audit_record_completeness.py content --vocab metadata/device-taxonomy.json`
— zero REC-01/02/03/04/05/06 findings for TED-0026, TED-0027, TED-0036, TED-0042, TED-0043,
TED-0044, TED-0045 (verified by grep against the full run's output; other workers' files
still report findings, as expected — 40 error(s), 25 warning(s) across 65 finding(s) overall
at time of this report, none attributed to my seven files).

`python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json`
— `Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)` (exit 0), full
corpus, at time of this report.

`git status --porcelain` (full working tree — other lanes are working concurrently on the
same shared branch, so many non-owned files also show as modified/untracked; verified via
`git diff --stat` that my own changes are confined to exactly the seven files this lane owns):

```
 M content/devices/TED-0007.md
 M content/devices/TED-0008.md
 M content/devices/TED-0009.md
 M content/devices/TED-0012.md
 M content/devices/TED-0013.md
 M content/devices/TED-0014.md
 M content/devices/TED-0015.md
 M content/devices/TED-0016.md
 M content/devices/TED-0019.md
 M content/devices/TED-0020.md
 M content/devices/TED-0021.md
 M content/devices/TED-0022.md
 M content/devices/TED-0026.md
 M content/devices/TED-0027.md
 M content/devices/TED-0029.md
 M content/devices/TED-0030.md
 M content/devices/TED-0031.md
 M content/devices/TED-0034.md
 M content/devices/TED-0036.md
 M content/devices/TED-0042.md
 M content/devices/TED-0043.md
 M content/devices/TED-0044.md
 M content/devices/TED-0045.md
 M content/devices/dynavap-m7.md
?? reports/portables-b-260808-2055-level.md
```

`git diff --stat` restricted to this lane's seven owned files:

```
 content/devices/TED-0026.md | 7 +++++--
 content/devices/TED-0027.md | 7 +++++--
 content/devices/TED-0036.md | 4 +++-
 content/devices/TED-0042.md | 6 ++++--
 content/devices/TED-0043.md | 6 ++++--
 content/devices/TED-0044.md | 4 +++-
 content/devices/TED-0045.md | 4 +++-
 7 files changed, 27 insertions(+), 11 deletions(-)
```
