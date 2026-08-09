# Worker report — slice `legacy` (pre-ball FlowerPot lineage)

Branch: `agent/cannabis-hardware-cleanup`. No build, validation gate, or state-changing git
command was run. Only files in my assigned ownership were modified.

## 1. What I changed

- **Created** `content/devices/TED-0037.md` — Cannabis Hardware FlowerPot Showerhead (pre-ball head).
- **Created** `content/devices/TED-0038.md` — Cannabis Hardware FlowerPot Vrod (pre-ball head).
- **Created** `content/devices/TED-0039.md` — Cannabis Hardware FlowerPot Baller Head Assembly (FlowerPot Ball Vape, Generation 1).
- **Created** `content/devices/TED-0040.md` — Cannabis Hardware FlowerPot Screen Baller (Generation 2).
- **Created** `reports/legacy-260808-1847-worker.md` — this report.
- All four reserved IDs were used, in the order specified in my brief. No ID was skipped.

## 2. Entities and relations created

| ID | Title | Component role | Relations |
| --- | --- | --- | --- |
| `devices/TED-0037` | FlowerPot Showerhead | Heater head, pre-ball | `relates_to=manufacturers/TMFR-0004`, `relates_to=devices/TED-0038` |
| `devices/TED-0038` | FlowerPot Vrod | Heater head, pre-ball | `relates_to=manufacturers/TMFR-0004`, `relates_to=devices/TED-0037` |
| `devices/TED-0039` | FlowerPot Baller Head Assembly (Ball Vape gen 1) | Heater head, first ball-holding generation | `relates_to=manufacturers/TMFR-0004`, `supersedes=devices/TED-0038` |
| `devices/TED-0040` | FlowerPot Screen Baller (gen 2) | Heater head, second ball-holding generation | `relates_to=manufacturers/TMFR-0004`, `supersedes=devices/TED-0039`, `relates_to=devices/TED-0028` |

**Deliberate departure from the brief's assumed lineage:** my brief states the lineage is
"Showerhead → Vrod → [B-rod Mod] → FlowerPot Ball Vape → Screen Baller → B2 → B1, per the
2021-10-20 evolution blog." I fetched and read that blog's full text directly (see §3). It
does **not** mention the Showerhead at all — it opens at the B-rod Mod, built from the Vrod,
and never establishes a Showerhead→Vrod order. I could not find any other primary source
establishing which of the two came first (see §4). I therefore linked Showerhead↔Vrod as
siblings (`relates_to` only, both directions) rather than asserting a `supersedes` edge in
either direction. The rest of the chain (Ball Vape gen 1 supersedes Vrod; Screen Baller
supersedes Ball Vape gen 1) **is** directly confirmed by the blog and is modeled with
`supersedes` as instructed.

**Missing back-link to report:** `devices/TED-0028` (FlowerPot B2, owned by another worker)
does not yet carry a `supersedes=devices/TED-0040` edge. Per the evolution blog, the B2 is
the manufacturer's next step after the Screen Baller ("The Screen Baller performed so well
that we wanted to make it more than just an upgraded diffuser... the B-2 was born"). TED-0040
adds its side of the link (`relates_to=devices/TED-0028`); the integrator should add the
reciprocal `supersedes=devices/TED-0040` to TED-0028 if that record's owner agrees with this
reading. I did not touch TED-0028.

## 3. Primary sources verified (URL + snapshot + what it establishes)

All fetched via direct HTTP retrieval of Wayback Machine snapshots (`web.archive.org/web/<ts>/<url>`,
`curl` + local HTML→text extraction) after both `WebFetch` and the `crawl4ai` MCP tool returned
errors against `web.archive.org` specifically (WebFetch: "unable to fetch from web.archive.org";
crawl4ai: HTTP 500 on every wayback URL tried). `crawl4ai` worked fine against the **live**
`cannabishardware.com` site and was used for all live-site checks below. CDX inventory queries
used the raw `http://web.archive.org/cdx/search/cdx` API via `curl`.

- **Showerhead Assembly** (SKU 7005), newvape.com, snapshot 2019-12-15:
  https://web.archive.org/web/20191215215537/https://www.newvape.com/showerhead-assembly
  → full assembly contents, price ($100), "19 intake air holes," Grade 2 titanium, "twax" dual-use description.
- **ShowerHead for 20mm Coil** (SKU 3063, top-only), newvape.com, snapshot 2019-07-21:
  https://web.archive.org/web/20190721133724/https://www.newvape.com/showerhead-flowerpot-20mm
  → price ($60), dimensions, thread spec, "top only, no other parts included."
- **Vrod Head Assembly (7003)**, newvape.com, snapshot 2020-08-13:
  https://web.archive.org/web/20200813133058/https://www.newvape.com/products/flowerpot-vrod-head-assembly
  → SKU 7003, $115.00, full kit contents, "5 wraps clockwise" coil spec.
- **Vrod Head Assembly (7003)**, cannabishardware.com, snapshot 2021-04-18:
  https://web.archive.org/web/20210418230144/https://www.cannabishardware.com/products/flowerpot-vrod-head-assembly
  → same SKU/kit/description, price risen to $140.00 — used to establish the NewVape→Cannabis Hardware price change.
- **Baller Head Assembly**, cannabishardware.com, snapshot 2021-09-27:
  https://web.archive.org/web/20210927061719/https://www.cannabishardware.com/products/baller-head-assembly
  → "Introduced in Aug-2021," "58 Quartz 4 mm spheres," full variant/price ladder, product ID 6670452195468.
- **Screen Baller (3408)**, cannabishardware.com, snapshot 2021-09-27:
  https://web.archive.org/web/20210927060236/https://www.cannabishardware.com/products/screen-baller-3408
  → SKU 3408, $66.00, "3mm pearls" fix description, product ID 6677849505932.
- **22mm Baller Diffuser (3408)**, cannabishardware.com, snapshot 2021-12-28:
  https://web.archive.org/web/20211228153158/https://www.cannabishardware.com/products/22mm-baller-diffuser
  → same SKU 3408 under a renamed listing, description updated to reference the B2 — evidence the "Screen Baller" identity was renamed, not discontinued outright.
  Interesting incidental find (not used as fact, informational only): 6 customer reviews on this
  snapshot describe the diffuser as a direct performance upgrade over "the regular baller" and
  "the old Vrod," independently corroborating the Vrod→Baller→Screen Baller succession from the
  buyer side. Flagged as **community-reported**, not manufacturer fact, and not relied on for any
  CONFIRMED claim in the device pages.
- **"Baller Head Assembly" blog** (release announcement), cannabishardware.com, snapshot 2023-09-28:
  https://web.archive.org/web/20230928101659/https://www.cannabishardware.com/blogs/ch/baller-head-assembly
  → dated August 31, 2021; names Troy/420 VapeZone and the community/Discord as the B-rod Mod origin; "can only be used with the Vrod top, not the Weedeater."
- **"The Evolution of the Flowerpot Baller" / "...FlowerPot Ball Vapes"**, cannabishardware.com, snapshot 2021-11-08 (of the pre-rename URL):
  https://web.archive.org/web/20211108122509/https://www.cannabishardware.com/blogs/newvape-blog/the-evolution-of-the-flowerpot-baller
  → confirmed full text matches the common brief's summary verbatim, dated 2021-10-20, and confirmed it does **not** mention the Showerhead.
- **"Vrod or WeedEater?" blog**, cannabishardware.com, snapshot 2021-04-13:
  https://web.archive.org/web/20210413202136/https://www.cannabishardware.com/blogs/newvape-blog/flowerpot-vrod-or-weedeater
  → dated October 6, 2020; describes the Weedeater as a flower-only, dish-less Vrod variant. No standalone Weedeater product page was located (see §4) — not modeled as an entity, mentioned only as prose context on the Vrod page.
- **28mm Vrod SiC Dish**, newvape.com, snapshot 2020-08-13:
  https://web.archive.org/web/20200813151116/https://www.newvape.com/products/28mm-vrod-sic-dish — confirms the dish is also sold standalone.
- **28mm Vrod Sapphire Dish (9265)**, cannabishardware.com, snapshot 2021-06-15:
  https://web.archive.org/web/20210615002905/https://www.cannabishardware.com/products/28mm-vrod-sapphire-dish-9265
- **Live site checks (2026-08-08)**, via `crawl4ai-mcp-md` and direct `curl` HTTP-status checks:
  - `cannabishardware.com/products/showerhead-assembly` → 404
  - `cannabishardware.com/products/flowerpot-vrod-head-assembly` → 404
  - `cannabishardware.com/products/baller-head-assembly` → 404
  - `cannabishardware.com/products/flowerpot-vrod-head-top-3129` → 301 → `.../dab-rig-b2-top` (which itself 404s live — a dead redirect target, noted but not built on)
  - `cannabishardware.com/products/screen-baller-3408` → 301 → `.../22mm-vaporizer-diffuser`, which is a **live, current** product page: "22mm 'Standard' Diffuser (3408)," $71.00, "Rev C machined to accept both mesh and machined screens, started shipping 7/9/23" — same SKU 3408 as the Screen Baller, still sold today.
  - `cannabishardware.com/products/ball-vape-b1` (current B1 listing) → confirms the current B1 head is "perfectly optimized to work seamlessly with the 22mm Screen Diffuser," i.e. SKU 3408's current descendant is still a load-bearing part of the current catalog.

## 4. Claims deliberately left labelled unverified, and why

- **Showerhead vs. Vrod ordering.** Not asserted either direction. Evidence considered:
  Wayback image-cache assets tagged "showerhead" first appear 2017-10-16; the earliest
  Vrod-specific asset found is 2019-01-30. That gap is suggestive of Showerhead predating
  Vrod but is not conclusive (Wayback crawl depth varies independently of true release
  order, and neither date is a manufacturer-stated release date). Documented as an open
  question on both pages rather than resolved by inference.
- **Ball count discrepancy for the FlowerPot Ball Vape (gen 1):** manufacturer product page
  (2021-09-27) says "58 Quartz 4 mm spheres"; manufacturer evolution blog (2021-10-20) says
  "about 60 4mm quartz balls." Both are manufacturer-published; recorded as a disagreement on
  TED-0039 rather than silently picking one number, per my brief's explicit instruction to
  verify and flag disagreement.
- **Temperature ranges** for all four models: not manufacturer-published for these specific,
  discontinued listings. I deliberately did **not** cite the current FlowerPot FAQ's 550–800°F
  range for them, since that FAQ page postdates these listings, doesn't name them, and may
  reflect a different (later) coil/head platform — citing it would have been inference
  dressed as fact.
- **Warranty terms** for all four: not separately published on the archived listings. I did
  not backdate the current 1-year/30-day warranty terms onto these discontinued products.
- **Weedeater** (mentioned only in prose on the Vrod page, per the NewVape blog): no
  standalone archived product page was found in this search pass, so it is explicitly **not**
  modeled as an entity. If a later worker or the integrator locates one, it would need its
  own ID.

## 5. Anything I could not do / files outside my ownership that need a change

- **TED-0028 (FlowerPot B2)** should eventually carry `supersedes=devices/TED-0040` for the
  Screen Baller → B2 edge described in the evolution blog. Not my file to edit; flagged above
  in §2 and here for the integrator.
- No other blockers. All four reserved IDs were used; no ID was left unused.

## 6. Search-coverage section (URL patterns and CDX queries tried)

CDX base: `http://web.archive.org/cdx/search/cdx` (all queries run 2026-08-08).

1. `url=cannabishardware.com/products/*&output=text&fl=original,timestamp&collapse=urlkey&limit=5000`
   → 1,221 unique URLs. Grepped case-insensitively for `vrod`, `shower`, `ball`, `baller`, `screen`, `flowerpot`.
2. `url=newvape.com/products/*&output=text&fl=original,timestamp&collapse=urlkey&limit=5000` → 334 URLs, same greps.
3. `url=newvape.com*&output=text&fl=original,timestamp&collapse=urlkey&limit=5000` → 4,555 URLs (whole-domain sweep, not just `/products/`, to catch the older Magento-era non-`/products/` URL scheme). Same greps, plus a manual scan of the full "screen/ball/vrod/shower" result set.
4. `url=cannabishardware.com/collections/*&output=text&fl=original,timestamp&collapse=urlkey&limit=5000` → 1,157 URLs; filtered to `collections/flowerpot(-ball-vape)?/products/` and `collections/all/products/` to find first/last-seen listing windows for the four handles.
5. `url=cannabishardware.com/blogs/*&output=text&fl=original,timestamp&collapse=urlkey&limit=2000` → 201 URLs; grepped for `vrod|shower|ball|baller|screen|evolution` — found both the evolution blog and the separate "Baller Head Assembly" release blog (Aug 31, 2021).
6. `url=cannabishardware.com/sitemap.xml` (bare, no filters) → confirmed sitemap snapshots exist from 2022-06 onward; did not deep-crawl child sitemaps once the `/blogs/*` and `/products/*` sweeps above had already surfaced every relevant handle.
7. `url=cannabishardware.com/products/*.json&output=text...` → **0 results.** No archived Shopify JSON snapshots exist for any product on this domain; all product-level facts in the four pages therefore come from parsed HTML product pages, not JSON, with the exact snapshot cited per claim.
8. Per-handle timestamp+statuscode CDX queries (`fl=timestamp,statuscode`) run individually for: `newvape.com/showerhead-assembly`, `newvape.com/showerhead-flowerpot-20mm`, `cannabishardware.com/products/showerhead-assembly`, `newvape.com/products/flowerpot-vrod-head-assembly`, `newvape.com/flowerpot-vrod-head-assembly`, `cannabishardware.com/products/flowerpot-vrod-head-assembly`, `cannabishardware.com/products/flowerpot-vrod-head-top-3129`, `cannabishardware.com/products/baller-head-assembly`, `newvape.com/products/baller-head-assembly` (0 results — this handle only ever existed on the cannabishardware.com domain), `cannabishardware.com/products/screen-baller-3408`, `newvape.com/products/screen-baller-3408` (0 results). The Internet Archive's CDX endpoint returned intermittent 503/504 errors during this pass; queries were retried until a clean result was obtained, except where noted as "0 results" (a genuine empty result, not a retry failure).
9. Live-site HTTP status + redirect-target checks (2026-08-08, `curl -o /dev/null -w '%{http_code}'` and `%{redirect_url}`, plus `crawl4ai-mcp-md` for content) for all four product handles and their current redirect targets — see §3.
10. Not tried: deep crawl of `newvape.com` pre-2017 Magento numeric-ID URLs (e.g. `/2648-bottom-screen`-style paths) beyond the domain-wide sweep in query 3, since that sweep already surfaced all `vrod`/`shower`/`ball`/`screen` hits back to 2015 and none predate the 2017-10 Showerhead image-cache assets already cited. Not tried: searching non-Wayback secondary sources (forums, retailer archives) for a Showerhead/Vrod ordering claim, since my brief and the common brief both restrict ordering claims to primary manufacturer sources.

## 7. Exact commands run and actual output

**Taxonomy audit (final, on the full working tree):**

```
$ python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json
Device taxonomy audit: 0 error(s), 0 warning(s) across 0 finding(s)
```

**Git status of my owned files (only):**

```
$ git status --porcelain -- content/devices/TED-0037.md content/devices/TED-0038.md content/devices/TED-0039.md content/devices/TED-0040.md reports/
?? content/devices/TED-0037.md
?? content/devices/TED-0038.md
?? content/devices/TED-0039.md
?? content/devices/TED-0040.md
?? reports/ballcounts-260808-1847-worker.md      (another worker's file, not mine)
?? reports/heads-260808-1847-worker.md           (another worker's file, not mine)
?? reports/rev2-260808-1847-worker.md            (another worker's file, not mine)
?? reports/vmax-260808-1847-worker.md            (another worker's file, not mine)
?? reports/zion-260808-1847-worker.md            (another worker's file, not mine)
```

`git diff --stat` against the four files I created returns empty (they are new/untracked,
never previously existed), confirming I made no modification to any pre-existing file. The
full repo `git status --porcelain` also shows modifications to `TED-0004/0005/0006/0007/0025/
0026/0027/0028/0029/0030/0031/0032` and `reference/TREF-0004.md`, and new files
`TED-0034/0035/0036/0041/0042/0043` — all of these are other workers' in-progress changes on
this shared branch, not mine; I did not touch any of them.

**Live HTTP status checks (2026-08-08):**

```
404  https://www.cannabishardware.com/products/showerhead-assembly
404  https://www.cannabishardware.com/products/flowerpot-vrod-head-assembly
301  https://www.cannabishardware.com/products/flowerpot-vrod-head-top-3129
404  https://www.cannabishardware.com/products/baller-head-assembly
301  https://www.cannabishardware.com/products/screen-baller-3408
301  https://www.newvape.com/products/flowerpot-vrod-head-assembly

Redirect targets:
flowerpot-vrod-head-top-3129 -> https://www.cannabishardware.com/products/dab-rig-b2-top (itself 404s live)
screen-baller-3408           -> https://www.cannabishardware.com/products/22mm-vaporizer-diffuser (live, current listing)
```


Status: DONE
