# Oliver renderer readiness (TED side)

Status: **prepared, blocked on one upstream defect**
Verified: 2026-08-13
TED pin at time of writing: Boris `d703fadb62b7451f354c0c83904737db4868b0b0` (ApexMarkdown)
Tested against: Boris `afterparty` tip `78c0745`, Oliver `872b002`

On 2026-08-13 Boris replaced its Markdown renderer: ApexMarkdown Unified was
removed (PR #371) and [Oliver](https://github.com/drawmeanelephant/oliver) —
a freestanding Zig markup library — was integrated as the only render seam
(PR #370). Boris's own account of the change is
`docs/contracts/oliver-renderer.md` in that repository, including a
compatibility wall enumerating the intended output deltas.

This document records what that costs TED, what has already been fixed, and
what still blocks the pin bump.

## Blocker: Oliver emits duplicate footnote-reference ids

**This is the only thing preventing adoption.** It is an upstream defect, not a
TED policy quirk, and both TED's audit and Boris's own publication checks reject
it independently.

When a page references the same footnote more than once, Oliver gives every
reference the same `id`:

```html
<sup class="footnote-ref"><a href="#fn-1" id="fnref-1" data-footnote-ref>1</a></sup>
...
<sup class="footnote-ref"><a href="#fn-1" id="fnref-1" data-footnote-ref>1</a></sup>
```

ApexMarkdown disambiguated repeat references, which is what GFM does:

```html
id="fnref-1"     first reference
id="fnref-1-2"   second reference
id="fnref-2-11"  eleventh reference to footnote 2
```

Measured on the current corpus, built with `afterparty` `78c0745`:

| Measure | Apex (`d703fad`) | Oliver (`78c0745`) |
| --- | ---: | ---: |
| Pages with duplicate `id` attributes | 0 | 77 |
| Duplicate `id` occurrences | 0 | 1,078 |
| Boris `HTML_DUPLICATE_ID` findings | 0 | 216 |

Every duplicate is a `fnref-*` id; no other id collides. 110 content files use
footnotes, and reusing one reference is normal in a sourced archive, so there is
no content-side workaround that does not amount to deleting citations.

Consequences today:

- `bin/validate_graph.sh` fails its HTML-ID audit.
- Boris fails its own publication checks and refuses to derive the Touch Atlas,
  so `scripts/ted-build.sh` aborts with `PublicationTouchesFailed`.
- Duplicate `id` is invalid HTML: it breaks `getElementById`, in-page fragment
  navigation, and accessibility tooling.

The fix belongs in Oliver's footnote renderer — suffix repeat references the way
GFM does. Do not add a TED-side HTML post-processor for it; per `AGENTS.md` §6,
a project-local workaround for a missing upstream primitive is exactly what
should not be built here.

## Already fixed on the TED side (renderer-independent)

All four items below were resolved by content and theme changes that work under
**both** renderers, so they are already merged rather than waiting on the pin.
Confirmed zero occurrences in an Oliver build.

### Callouts → Boris `<Aside>` (60 uses, 45 files)

`> [!NOTE]`-style callouts were an Apex extension. Under Oliver the marker leaks
as visible literal text (`<p>[!NOTE]`). They now use Boris's native `<Aside>`
component, which Boris tokenizes itself outside the render seam:

```md
<Aside kind="warning">

**DCC data caveat**

Source data are entered by licensees and may later be corrected.

</Aside>
```

Kind mapping preserves all five severities that were in use —
`NOTE`→`note`, `TIP`→`tip`, `IMPORTANT`→`info`, `WARNING`→`warning`,
`CAUTION`→`danger`. Where a callout carried a custom title on the marker line
(18 of the 60), the title became a bold lead-in paragraph, because `<Aside>`
derives its title from `kind`. An `Aside` `title` attribute would restore the
original presentation exactly; worth requesting upstream if it matters.

The theme followed: `.callout*` rules were replaced with `.admonition*` rules
matching Boris's `<aside class="admonition admonition--KIND" aria-label="Kind">`
output. The new markup is a semantic `<aside>` with an accurate ARIA label,
which the Apex `<div>` soup was not.

### Approximation tildes → `≈` and `c.` (188 occurrences, 65 files)

This one was a **live rendering defect**, not a migration cost. Content wrote
`~80 %` for "approximately 80 %", and Apex paired unrelated tildes into
subscript spans, so the published site rendered
`Hybrid <sub>80</sub> % convection / <sub>20</sub> % conduction`. There were
170 such bogus `<sub>` spans across 56 published pages.

Numeric approximations now use `≈`, and approximate dates use `c.`. The 7
remaining `<sub>` spans in the build are deliberate chemical formulas
(`C21H30O2`, `C22H30O4`, `CO2`).

### Task lists → status prefixes (24 lines, 4 files)

Apex rendered `- [x]` as a disabled checkbox; Oliver leaves `[x]` literal. These
were coverage and sync-status lists, so they now say what they mean —
`**Covered** —`, `**Done** —`, `**Blocked** —`, `**Not republished here** —`.
More precise than a checkbox, and it needs no renderer feature.

### Math → code spans and `<sub>` (2 guides)

`$…$` / `$$…$$` was an Apex extension. The two affected guides now write
`` `Total Active THC = Δ⁹-THC + (THCA × 0.877)` `` and use `<sub>` for
molecular formulas. If TED ever needs real math, ask for an Oliver extension
rather than reintroducing a renderer-specific dialect.

## Accepted behaviour change: no smart typography

Apex applied Unified's smart-typography default, converting `"` to `“ ”` and
`'` to `’`. Oliver keeps author bytes literal, which affects 324 lines of
rendered output. Nothing in TED's contracts required curly quotes, and the
change is invisible to the graph, audits, and tests.

Two options when the pin moves, both fine:

1. Accept straight quotes. Zero work, slightly plainer typography.
2. Convert the affected content to typographic quotes deliberately, so the
   bytes say what is published.

This is a presentation decision and is not tracked as a blocker.

## Also worth knowing

- **Fenced code**: Apex emitted `<pre lang="bash">`, Oliver emits
  `<pre><code class="language-bash">`. TED had a `pre[lang]::before` rule that
  drew a language badge; it was already dead — the current corpus produces
  exactly one `<pre>` and it carries no language — so the rule was removed
  rather than ported.
- **Footnote numbering** also changes: Oliver numbers by first-reference order,
  so a given footnote may take a different number than under Apex. That is
  internally consistent and no content links to `#fn-N` directly (verified: 0
  hardcoded fragment references), so it is harmless.
- **`content/guides/cultivar-page-apex-specimen.md`** (`guides/TGDE-0002`) was
  written as an ApexMarkdown feature specimen. Its Apex-only constructs are
  rewritten, but the page still needs a deliberate pass to exercise Oliver's
  feature set instead. The canonical ID is unchanged; ask the integrator before
  renaming the file.
- Boris's `afterparty` is 70 commits ahead of TED's pin, and `main` is 50 ahead
  and does **not** yet contain the Oliver swap. TED pins the `afterparty`
  branch, so it meets this change first.

## Upgrade procedure once the footnote defect is fixed

1. Update `metadata/boris-version.json` to the Boris commit containing the fix.
2. `./scripts/ensure-boris.sh --provision`
3. `./bin/validate_graph.sh` — expect the HTML-ID audit to pass and Boris's
   publication checks to report zero `HTML_DUPLICATE_ID`.
4. `python3 scripts/check_reproducible_build.py` and record a fresh baseline in
   `reports/static-build-reproducibility.md`. The existing 494-path /
   10,149,589-byte baseline is pin-scoped and will not survive a renderer
   change.
5. Decide the smart-quote question above, then diff the rendered output against
   the pre-bump baseline and classify anything not listed in this document or in
   Boris's compatibility wall.
