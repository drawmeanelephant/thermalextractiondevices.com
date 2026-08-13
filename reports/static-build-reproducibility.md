# Static Build Reproducibility Baseline

Status: **reproducible**

Verified: 2026-08-13

TED source commit: `0d8094b70dbd63cfe8365681578b8775c312b50c`
(`worktree_dirty: false` at build time, per `dist/reproducibility/report.json`;
this paragraph was written afterwards)

Boris pin: `d703fadb62b7451f354c0c83904737db4868b0b0`
(binary SHA-256 `b466e729c1e8777240e6956d38a5eab640e6df3bebfafbee926526417b4853d8`,
Zig 0.16.0)

Two production builds were generated independently with `BORIS_JOBS=1` and
the pinned local Boris binary. The comparison included every relative file
path and exact file byte, including Boris proof/cache files, crosslink-injected
HTML, the sitemap, assets, and `_headers`.

| Build | Files | Bytes | Aggregate SHA-256 |
| --- | ---: | ---: | --- |
| First | 494 | 10,149,589 | `d19089d96c9fde1aa72bef97224bc8227830bdfbe362ecd36669186342a7f0c5` |
| Second | 494 | 10,149,589 | `d19089d96c9fde1aa72bef97224bc8227830bdfbe362ecd36669186342a7f0c5` |

No missing, extra, or changed files were found. No nondeterministic timestamp,
ordering, absolute-path, or random-ID difference was observed in the static
artifact.

## Change from the 2026-08-09 baseline

The previous baseline was 496 files / 10,133,239 bytes / aggregate SHA-256
`9a909f8c5656b8e300331427f98f0daafe63ad6b618278788535795bbc6ebb9b`, taken at
TED commit `e10f5dc` — a pre-rewrite SHA that no longer resolves after the
2026-08-12 history rewrite. Its post-rewrite equivalent is `188f0c2`.

The output shrank by two files while the corpus grew by one entity. The
*file-list* delta is accounted for exactly, by building `188f0c2` with the same
pinned binary and diffing the two lists of paths:

```
+ jurisdictions/TJUR-0076.html              (Denmark, PR #40)
- lab-results/TLAB-0002-related.html        (crosslink overflow page)
- terpenes/TTRP-0004-backlinks.html         (crosslink overflow page)
- terpenes/TTRP-0005-backlinks.html         (crosslink overflow page)
```

The three overflow pages disappeared because PR #44 added a `CXL-03` rule
rejecting a direct `cultivar --relates_to--> compound` edge — cultivar
chemistry must be derived from reports, not asserted in frontmatter — and
removed 27 cultivar → terpene relations from nine cultivar records. The
crosslink graph went from 444 entities / 1,664 edges to 445 entities /
1,614 edges, which dropped those three sections back under the
`MAX_ITEMS_PER_SECTION` pagination threshold. No entity page was lost: all 445
content IDs still have a corresponding HTML file in `dist/cantilever`.

Two things this comparison does **not** account for, stated so the next reader
does not over-read it:

* **File contents.** Only the path lists were diffed. Hundreds of pages changed
  content between the baselines — every page carrying injected navigation, at
  minimum — and the +16,350-byte total is not attributed to any specific cause.
* **The toolchain moved too.** The 2026-08-09 baseline was built with Boris
  `9505ec6`; this one uses `d703fad`. Rebuilding `188f0c2` with the *new* binary
  isolates the content-driven part of the file-list delta, which is why that
  comparison is trustworthy for paths — but a byte total spanning both a content
  change and a compiler change cannot be attributed to either from this evidence.

Both baselines are internally reproducible, which is what this report certifies.

The reusable check is:

```sh
python3 scripts/check_reproducible_build.py
```

It writes machine-readable evidence to
`dist/reproducibility/report.json`, keeps logs alongside the report, and
removes the two bulky output trees after a successful comparison unless
`--keep-builds` is supplied. The scheduled/manual workflow in
`.github/workflows/reproducibility.yml` preserves the report and logs as a CI
artifact.
