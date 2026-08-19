# Publication Hardening Checklist

The repository and site are already public. Run every item before calling the
publication surface fully hardened. Items marked **[BLOCKER]** remain release
gates. The public-release audit (`scripts/audit_public_release.py`) automates
the mechanical parts, but human sign-off is required on judgment items.

## 0. Blockers — resolve before anything else

- [ ] **[BLOCKER] Purge the licensee registry from GitHub's pull refs.**
      Verified open 2026-08-13. The 2026-08-12 history rewrite cleaned `main`,
      but pull-request refs were never rewritten, so the pre-rewrite history is
      still reachable and the California DCC licensee registry can still be
      fetched from this public repository by an unauthenticated client. Roughly
      20,700 licensee records. Reproduction steps and the affected object id are
      held with the maintainers, not in this tracked file — publishing a runnable
      recipe next to the finding would widen the exposure. Note that there is
      nowhere private to file them yet; see the private-reporting blocker below. No local change fixes it; it needs a GitHub Support request to
      drop the stale pull refs and expire the objects. Pair it with a decision on
      notifying the affected licensees. Until then this dataset is published, and
      every other item on this list is downstream of it. See
      `docs/history-cleanup-plan.md`.
- [x] **[BLOCKER] Licensing decision recorded.** `LICENSE.md` records an
      all-rights-reserved notice and the limited GitHub viewing/forking context.
      Maintainers should confirm that proprietary terms remain intentional
      before any release announcement.
- [ ] **[BLOCKER] Private security reporting is enabled and tested.** Verified
      **not enabled** on 2026-08-13: `gh api
      repos/drawmeanelephant/thermalextractiondevices.com/private-vulnerability-reporting`
      returns `enabled: false`, so the flow `SECURITY.md` directs reporters to does
      not exist. This is no longer hypothetical — a real finding (the pull-ref
      exposure above) had nowhere private to go. Requires repository admin;
      `SECURITY.md` intentionally does not invent a mailbox or response SLA.
- [x] **[BLOCKER] No category-4 data in the in-scope publication tree.** Run
      `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json`
      and disposition findings. Verified 2026-08-13: 35 active findings, none
      above `low`, and Massachusetts contributes zero. The Massachusetts lane is
      no longer an exclusion — see `docs/status/states/massachusetts.md`. This
      item covers the tracked tree only; the pull-ref exposure above is
      separate and still open.
- [ ] **[BLOCKER] Human review of flagged records.** Review every `REV-001`
      finding (producer/manufacturer/lab content, draft research queue) and
      confirm each record is accurate, evidenced, and safe to publish under
      `PRIVACY.md` categories.
## 1. Automated audits (all must pass)

- [ ] `python3 scripts/audit_public_release.py --config docs/audit-config.json`
      → exit 0. Verified 2026-08-13 on the tracked tree: 75 findings, 35 active,
      nothing at medium or above. Note the structural limit — this scans
      `git rev-list --all` in the local clone, so it can see neither GitHub's
      pull refs nor another machine's stale branches. A pass here is not
      evidence about what GitHub serves.
- [ ] `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json`
      → exit 0 for the in-scope tree. Massachusetts is no longer excluded.
- [ ] `python3 scripts/audit_large_files.py --config docs/audit-config.json`
      → no giant tracked files, no duplicate dataset blobs, no
      external-storage candidates that should not exist
- [ ] `python3 scripts/audit_markdown_links.py content` → all links resolve
- [ ] `python3 scripts/audit_html_ids.py dist/cantilever` → no duplicate IDs
- [ ] `./bin/validate_graph.sh` → IDs, graph, and publication checks pass
- [ ] CI pipeline green on the release commit (`.github/workflows/ci.yml`,
      including the audit step)

## 2. Git & history

- [ ] Working tree clean; no `dist/`, `publish/`, `.tools/`, `bin/boris*`,
      or `.env` files tracked.
- [ ] `git log --all` shows only intended history; no commit message or
      author/committer email leaks a personal address (noreply identities
      are acceptable).
- [x] **[BLOCKER] Current-tree disposition of `data/dcc/**` recorded** — raw
      and normalized payloads are removed from tracked paths; the manifest,
      schema note, and sync report remain; ingest code uses private/unpublished
      storage and redacts sensitive fields.
- [x] No blob above the 5 MiB threshold reachable from any ref in `origin/main`.
      Verified 2026-08-13 on a fresh clone: the largest blob is a 327 KiB Inter
      font, and `.git` is 3.2 MiB. Note that `audit_large_files.py` scans
      `git rev-list --all` locally, so a stale clone reports otherwise; that is
      the clone, not the repository.
- [x] Duplicate current-tree DCC payload copies removed; private cache state
      is ignored and not a publication artifact.
- [x] **Bulk payloads removed from `main`'s git history.** Executed
      2026-08-12T18:04:56Z; four paths totalling 79.1 MiB are gone from
      `origin/main`. This item is superseded by the pull-ref blocker in
      section 0 — the same payload is still reachable through GitHub's
      `refs/pull/*`. See `docs/history-cleanup-plan.md`.

      **On severity.** The payload is the California DCC licence register,
      fetched from `search.cannabis.ca.gov` — a public register the state
      operates so that licensed cannabis businesses can be looked up by anyone.
      Cal. Civ. Code § 1798.82(i) excludes information lawfully made public in
      government records from the definition of personal information, and
      `PRIVACY.md` places records naming identifiable businesses in category 5
      (human review), not category 4 (never publish). That is why the audit
      grades it `medium` rather than blocking.

      It is still a blocker for publication, for two reasons that do not depend
      on the disclosure question: it violates `docs/artifact-storage.md` rule 4
      (raw and normalized payloads are not committed), and republishing a
      20.4 MiB bulk extract of 20,700 licensee contact records is a different
      act from operating a per-record lookup, whatever the source register's
      status. Decide it deliberately rather than by leaving pull refs in place.

- [x] Repository visibility is public; this checklist does not change
      visibility.

## 3. Content & provenance

- [ ] Every third-party claim carries its evidence/provenance warning
      include (`content/includes/`); claim grammar per
      `content/reference/evidence-labels-and-claim-grammar.md`.
- [ ] No PII, addresses, coordinates, or tax identifiers in any content.
- [ ] `metadata/id-map.jsonl` current; IDs immutable.
- [ ] Correction/takedown process documented and a maintainer assigned
      (`DATA_SOURCES.md`).

## 4. Site security

- [ ] `_headers` is committed at the repo root **and** copied into the build
      output by `scripts/ted-build.sh` (verify in the built `dist/`).
- [ ] Headers verified on a deployed preview: `Content-Security-Policy`,
      `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`,
      `Cross-Origin-Opener-Policy`, `X-Frame-Options`. Check the browser
      console for CSP violations after deploying (search and styling must
      still work).
- [ ] Cloudflare Pages project is served over HTTPS with a valid certificate
      and no mixed content.
- [ ] No analytics/tracking scripts added inadvertently.

## 5. Storage & dependencies

- [ ] Large raw datasets live in external artifact storage, not git
      (`docs/artifact-storage.md`).
- [ ] Boris compiler source pinned to a commit (not a moving branch) and
      Zig 0.16.0 pinned in `.github/workflows/ci.yml`.

## 6. Final sign-off

- [ ] Maintainer records the license choice, the security contact, and the
      date in this checklist.
- [ ] Announcement/README accurate: links, commands, and repository layout
      match the current tree.
- [ ] A post-publication follow-up scheduled: re-run audits after 30 days and
      after any content ingest.

---

*When every remaining blocker is checked, record the maintainer sign-off and
date here. This checklist does not authorize history rewriting, force-pushes,
or changes to the excluded Massachusetts lane.*
