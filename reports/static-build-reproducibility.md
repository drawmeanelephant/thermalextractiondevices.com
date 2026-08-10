# Static Build Reproducibility Baseline

Status: **reproducible**

Verified: 2026-08-09

TED source commit: `e10f5dc552758a5da1b4ed28c449a1553005a342`

Boris source commit: `9505ec610364e25f12bc4ec13e69275051f143fa`

Two production builds were generated independently with `BORIS_JOBS=1` and
the pinned local Boris binary. The comparison included every relative file
path and exact file byte, including Boris proof/cache files, crosslink-injected
HTML, the sitemap, assets, and `_headers`.

| Build | Files | Bytes | Aggregate SHA-256 |
| --- | ---: | ---: | --- |
| First | 496 | 10,133,239 | `9a909f8c5656b8e300331427f98f0daafe63ad6b618278788535795bbc6ebb9b` |
| Second | 496 | 10,133,239 | `9a909f8c5656b8e300331427f98f0daafe63ad6b618278788535795bbc6ebb9b` |

No missing, extra, or changed files were found. No nondeterministic timestamp,
ordering, absolute-path, or random-ID difference was observed in the static
artifact.

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
