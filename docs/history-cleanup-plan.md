# Git History Cleanup Plan (NOT executed)

Current state (re-audited against the California `main` base, 2026-08-09):

* 8 commits; every author/committer identity is the repository owner's
  GitHub noreply address.
* **64.2 MiB of unique blobs** reachable from `main` (264 blobs), dominated
  by the DCC license-registry datasets:
  * `data/dcc/license-registry/latest.json` — 21.4 MiB
  * `data/dcc/license-registry/2026-08-04/raw.json` — 20.9 MiB
  * `data/dcc/license-registry/2026-08-04/normalized.json` — 20.3 MiB
  (byte-identical to `previous.json`; git stores it once).
* The pre-hardening base tracked ~87.6 MiB across four registry copies
  (`raw.json`, `normalized.json`, `latest.json`, `previous.json`). This
  hardening branch removes those current-tree copies and leaves only bounded
  provenance metadata; it does not rewrite history.
* **No path has ever been deleted** from the real history (the provisioning
  scripts seen in some local snapshots never existed on `main`).
* The datasets contain personal/regulated data (business emails, phones,
  owner names, parcel numbers, premises addresses and coordinates) — see
  the public-release audit report. Removing the data from history, if
  decided, is exactly what this plan is for.

This plan has **not** been executed and must not be run without maintainer
sign-off and a full backup. It applies if category-4 data from `PRIVACY.md`
(owner contact details, premises coordinates) is committed in `data/` and
maintainers later decide those datasets must not be part of the public
repository.

---

## When to execute this plan

1. `scripts/audit_public_release.py` or `scripts/audit_sensitive_content.py`
   reports a finding in `<history>` (not just the current tree), **or**
2. a commit containing prohibited data is removed but the blob remains
   reachable from earlier commits.

Blobs deleted from the current tree remain in history forever unless a
rewrite is performed; GitHub may retain unreachable objects after a rewrite,
so treat any exposed credential as compromised and rotate it regardless.

---

## Step 0 — Backup (mandatory)

```bash
# Full mirror backup — do not skip.
git clone --mirror <repository-url> /tmp/thermalextractiondevices-backup.git
git bundle create /tmp/thermalextractiondevices-backup.bundle --all
# Verify the backup opens:
git bundle verify /tmp/thermalextractiondevices-backup.bundle
```

## Step 1 — Install the rewrite tool

```bash
# git-filter-repo is the maintained successor to filter-branch.
pip install git-filter-repo        # or: brew install git-filter-repo
git filter-repo --version
```

## Step 2 — Fresh clone (filter-repo refuses dirty/incomplete clones)

```bash
git clone --no-local <repository-url> /tmp/clean-work
cd /tmp/clean-work
git filter-repo --analyze   # optional: preview what the tool sees
```

## Step 3 — Remove the offending paths / blobs from all history

Examples (choose the relevant one; never run all blindly):

```bash
# Remove a whole generated directory from history:
git filter-repo --path dist/ --path publish/ --path .tools/ --invert-paths

# Remove a specific large or sensitive file wherever it appeared:
git filter-repo --path metadata/secret-dataset.csv --invert-paths

# Remove blobs above a size across all history (dangerous for fonts!):
# git filter-repo --strip-blobs-bigger-than 50M

# (Optional) scrub a real author email from history:
# git filter-repo --mailmap <(echo 'Old Name <old@email> New Name <new@noreply>')
```

`--invert-paths` keeps everything except the listed paths. Review the
rewritten log before pushing:

```bash
git log --all --oneline
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3>5000000 {print}'        # expect: no giant blobs
git rev-list --objects --all | grep -i secret     # expect: no matches
```

## Step 4 — Verification

* Re-run every audit in the fresh clone:
  `python3 scripts/audit_public_release.py --config docs/audit-config.json`.
* Confirm the current tree is byte-identical to the pre-rewrite HEAD
  (`git diff` against the backup).
* Confirm IDs and the build still pass: `./bin/validate_graph.sh`.
* Confirm the removed content is gone from `git log --all --name-only`.

## Step 5 — Force-push (irreversible; requires coordination)

```bash
git push --force --all origin
git push --force --tags origin
# Delete any stale remote branches that no longer exist locally:
git push origin --delete <stale-branch>
```

## Implications (document before executing)

* **Force-push rewrites shared history.** Every collaborator, CI cache, and
  fork must re-clone from the rewritten refs. Old clones keep the old
  history — and the removed blobs — locally.
* **Forks and caches survive.** GitHub may keep unreachable objects until
  garbage collection; for truly sensitive data, contact GitHub Support to
  scrub objects and consider rotating any exposed secrets.
* **All open PRs/branches must be rebased** onto the rewritten `main`, or
  they will reintroduce the removed blobs.
* **Mirror-clone backups are the only safety net**; keep them off the
  machine that will be force-pushed.
* After the rewrite, set the branch protection / push settings to prevent
  accidental force-pushes, and consider a one-time re-creation of the
  repository if the dataset is exceptionally sensitive.

## Do NOT

* Do not run `git filter-branch` without a backup.
* Do not force-push from the mirror backup clone.
* Do not rewrite shared history or destroy the only source copy. Current-tree
  publication cleanup may remove tracked payloads when a private source copy
  and manifest disposition are documented; preserve any retained source in
  private external storage (`docs/artifact-storage.md`).
