# Pre-Publication Checklist

Run every item before making this repository public. Items marked **[BLOCKER]**
must be resolved first. This checklist is the authoritative gate; the
public-release audit (`scripts/audit_public_release.py`) automates the
mechanical parts, but human sign-off is required on the judgment items.

## 0. Blockers — resolve before anything else

- [ ] **[BLOCKER] Licensing decision made.** Choose and commit a real license
      (see `LICENSE.md`). The repository is currently unlicensed (all rights
      reserved by default).
- [ ] **[BLOCKER] Security contact is real.** Replace the placeholder
      `security@example.com` in `SECURITY.md` with a monitored mailbox, and
      enable GitHub private security advisories.
- [ ] **[BLOCKER] No category-4 data anywhere.** Run
      `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json`
      — must report zero findings in both the tree and history.
- [ ] **[BLOCKER] Human review of flagged records.** Review every `REV-001`
      finding (producer/manufacturer/lab content, draft research queue) and
      confirm each record is accurate, evidenced, and safe to publish under
      `PRIVACY.md` categories.

## 1. Automated audits (all must pass)

- [ ] `python3 scripts/audit_public_release.py --config docs/audit-config.json`
      → exit 0 — **currently exits 1**: 172,562 blocking findings (PII in
      `data/dcc/**`). Resolve the `data/` disposition first.
- [ ] `python3 scripts/audit_sensitive_content.py --config docs/audit-config.json`
      → exit 0 — currently fails for the same reason.
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
- [ ] **[BLOCKER] Decide the disposition of `data/dcc/**`** — the tracked
      registry datasets (≈88 MiB on disk, 64 MiB in history) contain
      business emails, phones, owner names, parcel numbers, and premises
      coordinates. Options: move raw/normalized payloads to private
      external artifact storage and keep only manifests in git, strip PII
      at ingest, or obtain consent for republication. Do not make the
      repository public while this is unresolved.
- [ ] No blob above the 5 MiB threshold reachable from any ref
      (`python3 scripts/audit_large_files.py`) — currently FALSE: three
      license-registry blobs exceed it.
- [ ] No duplicate dataset copies (`previous.json` ≡ dated `normalized.json`
      for license-registry, recalls-index, and testing-labs) — currently
      FALSE; deduplicate or point `previous` at the dated file.
- [ ] History cleanup decided (`docs/history-cleanup-plan.md`) — only if
      `data/` PII is to be removed from history.
- [ ] Repository visibility is still **private** (this checklist does not
      change visibility).

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

*When every box is checked, remove the repository's private visibility
setting per the owner's process. This repository has not been made public.*
