# Contributing to Thermal Extraction Devices

Thanks for helping improve the Thermal Extraction Devices archive. This is a
production static site compiled with [Boris](https://github.com/drawmeanelephant/boris);
please read `README.md`, `rules.md`, and `AGENTS.md` before starting.

## Workflow

1. **Discuss first.** For anything beyond a typo fix, open an issue or
   discussion to agree on scope before writing content.
2. **Branch.** Create a branch off `main`; never commit directly to `main`.
3. **Make focused changes.** One logical change per commit. Do not run
   repository-wide formatting or touch unrelated files.
4. **Validate locally.** Run every gate below.
5. **Open a pull request** describing what changed, what evidence the
   content relies on, and which validation commands you ran.

## Required validation (all must pass)

```sh
./bin/validate_graph.sh                          # IDs, graph, build, HTML IDs
python3 scripts/audit_public_release.py --config docs/audit-config.json
python3 scripts/audit_markdown_links.py content
python3 scripts/audit_html_ids.py dist/cantilever   # after a build
```

CI runs these on every push and pull request.

## Content rules

* **Frontmatter is a closed schema.** Only `id`, `title`, `parent`, `status`,
  `tags`, `relations` are allowed. Unknown keys break the build.
* **IDs are immutable.** Never rename, renumber, or reuse canonical IDs.
  Run `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl`
  to validate; allocate new IDs from the next unused prefix.
* **Evidence over assertion.** Follow the claim grammar in
  `content/reference/evidence-labels-and-claim-grammar.md`. Attribute
  cultivar lineage and morphology to first-party breeder sources; never
  claim that breeder marketing predicts batch chemistry or effects.
* **Provenance warnings.** Records describing commercial products, cultivar
  lineages, or lab results must carry the relevant evidence/provenance
  warning include (see `content/includes/`).
* **Draft vs published.** Unverified research material stays `status: draft`
  (for example `content/guides/manufacturer-research-queue.md`).
* **No PII.** Do not add personal email addresses, phone numbers, full
  addresses, coordinates, or tax identifiers to content. See `PRIVACY.md`.

## History policy

* Never rewrite, rebase, or force-push shared history.
* Never commit build output (`dist/`, `publish/`, `site/`, `bin/boris*`,
  `.tools/`).
* `metadata/id-map.jsonl` is a generated file but is deliberately tracked as
  the migration record; update it via `ted_ids.py --write`, not by hand.

## Licensing

The repository is currently unlicensed (all rights reserved). Do not assume
that contributed content is reusable elsewhere. See `LICENSE.md`.
