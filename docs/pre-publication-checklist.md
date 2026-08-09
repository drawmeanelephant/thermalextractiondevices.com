# Publication Hardening Checklist

The repository and site are already public. Run every item before calling the
publication surface fully hardened. Items marked **[BLOCKER]** remain release
gates. The public-release audit (`scripts/audit_public_release.py`) automates
the mechanical parts, but human sign-off is required on judgment items.

## 0. Blockers — resolve before anything else

- [ ] **[BLOCKER] Licensing decision made.** Choose and commit a real license
      (see `LICENSE.md`). The repository is currently unlicensed (all rights
      reserved by default).
- [ ] **[BLOCKER] Private security reporting is enabled and tested.** Confirm
      the repository's GitHub Security-tab private advisory flow is available;
      `SECURITY.md` intentionally does not invent a mailbox or response SLA.
- [ ] **[BLOCKER] No category-4 data in the in-scope publication tree.** Run
      `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json`
      and disposition findings. The Massachusetts implementation lane is
      explicitly excluded from this pass and remains a reported blocker until
      its owner handles it.
- [ ] **[BLOCKER] Human review of flagged records.** Review every `REV-001`
      finding (producer/manufacturer/lab content, draft research queue) and
      confirm each record is accurate, evidenced, and safe to publish under
      `PRIVACY.md` categories.
- [ ] **[BLOCKER] Category-4 data removed from git *history*, not just the tree.**
      Verified 2026-08-09: the DCC registry payloads were untracked in `6d740f4`
      but **no history rewrite was performed**, so ~79 MiB across four blobs is
      still reachable — `git show <commit-before-6d740f4>:data/dcc/license-registry/latest.json`
      returns the full payload, from which **20,697 email addresses** were
      recovered during verification. `LARGE-004` grades this `high`, and the
      three findings are currently **suppressed by explicit, dated acknowledgement**
      in `docs/audit-config.json` on the sole grounds that this repository is
      private. **Making the repository public without first executing
      `docs/history-cleanup-plan.md` and deleting those three suppression entries
      publishes the data.** Removing the suppressions is part of this item, not
      optional cleanup.

## 1. Automated audits (all must pass)

- [ ] `python3 scripts/audit_public_release.py --config docs/audit-config.json`
      → exit 0 — current-tree California DCC payloads were removed; history
      and excluded Massachusetts findings still require disposition.
- [ ] `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json`
      → exit 0 for the in-scope tree; report excluded Massachusetts findings
      separately rather than modifying that lane here.
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
- [ ] No blob above the 5 MiB threshold reachable from any ref
      (`python3 scripts/audit_large_files.py`) — historical DCC blobs remain
      until the separate history-cleanup plan is executed.
- [x] Duplicate current-tree DCC payload copies removed; private cache state
      is ignored and not a publication artifact.
- [ ] History cleanup decided (`docs/history-cleanup-plan.md`) — only if
      `data/` PII is to be removed from history.
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
