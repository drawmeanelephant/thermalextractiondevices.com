# Git History Cleanup Plan (EXECUTED 2026-08-12 — EXPOSURE NOT CLOSED)

> **The rewrite ran and `main` is clean. The data is still downloadable.**
> 43 of 44 `refs/pull/N/head` refs on GitHub still point at pre-rewrite history,
> the repository is **public**, and an unauthenticated fetch of the purged
> commit still returns the full 20.4 MiB licensee payload. Closing this needs
> GitHub Support, not another local rewrite. See "What this does not fix".

## Outcome (verified 2026-08-13)

The rewrite removed the California DCC bulk payloads from every commit on `main`
that ever contained them. The originating commit `feat: California DCC ingestion
workflow` was rewritten from `3628c64` to `2fd1800`, dropping 59 files and
1,693,037 lines. Every SHA from that commit onward changed; `main` moved from
`6e693a8` — the pre-rewrite twin of the PR #44 merge — to `39a5589`.

| Deleted path | Size formerly in history | Reachable from `origin/main`? | Reachable from GitHub? |
| --- | --- | --- | --- |
| `data/dcc/license-registry/latest.json` | 20.4 MiB | no | **yes** |
| `data/dcc/license-registry/previous.json` | 19.4 MiB | no | **yes** |
| `data/dcc/license-registry/2026-08-04/raw.json` | 19.9 MiB | no | **yes** |
| `data/dcc/license-registry/2026-08-04/normalized.json` | 19.4 MiB | no | **yes** |

Four paths, 79.1 MiB total. `previous.json` and `2026-08-04/normalized.json` are
byte-identical, which is why earlier notes sometimes said "three payloads".

Why it mattered, and still does: `git show <commit>:data/dcc/license-registry/latest.json`
returns the full 20.4 MiB payload, carrying roughly 20,700 licensee records with
business emails, phones, owner names and premises addresses.

Evidence that `origin/main` is clean:

```
git rev-list --objects origin/main \
  | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $2>2000000'      # -> no output

git log --oneline origin/main -- data/dcc/license-registry/latest.json   # -> 0 commits
```

A fresh clone's `.git` directory is 3.2 MiB (`size-pack` 3.02 MiB; the checked-out
working tree is a further ~10 MiB), and CI (`CI & Graph Validation`, `Deploy to
Cloudflare Pages`) is green on the rewritten `39a5589`.

### What this does not fix

* **The payload is still anonymously downloadable from GitHub.** This is the open
  item, not a footnote. Pull-request refs were never rewritten, so the pre-rewrite
  history is still *reachable* — not merely uncollected garbage awaiting GC.
  Verified 2026-08-13 from an empty directory with no credentials:

  ```
  git ls-remote origin 'refs/pull/*'                     # -> 45 refs
  # 43 of 44 refs/pull/N/head still contain 3628c64

  git init -q . && git fetch -q --depth=1 \
    https://github.com/drawmeanelephant/thermalextractiondevices.com.git \
    3628c641af3d262825b11b0baa4db7a304556356               # -> exit 0
  git cat-file -s $(git rev-parse FETCH_HEAD:data/dcc/license-registry/latest.json)
  # -> 21416582   (20.4 MiB, 8,869 distinct email addresses)
  ```

  The repository is **public** (`gh repo view --json visibility` -> `public`), so
  the audience is everyone, not just collaborators.

  Remediation is not another `filter-repo` run — the objects are held by refs this
  repository does not control. It requires GitHub Support to drop the stale pull
  refs and expire the unreachable objects, and it should be paired with a decision
  about whether the affected licensees need notifying. Until that is done, treat
  this dataset as published.

* **Old clones still hold the data.** Any clone made before 2026-08-12 keeps the
  original objects. `LARGE-004` scans `git rev-list --all`, so a local clone with
  pre-rewrite branches or tags still reports the payloads — that part is a
  property of the stale clone. Delete the stale refs and run `git gc --prune=now`.

* **Branches created before the rewrite reintroduce the blobs if merged.** Rebase
  or recreate them onto the rewritten `main` before opening a pull request.

### Why the audits did not catch this at first

* `audit_sensitive_content.py` scans the **tracked working tree** plus commit
  *metadata* (author/committer/message). It never reads historical blob contents,
  so it reported the tree as clean.
* `audit_large_files.py` did detect the deleted-but-reachable blobs, but graded
  them `medium` — below the `high` fail threshold — so the gate passed.

`LARGE-004` still grades bulk data under `history_sensitive_paths` (default
`data/`) as `medium`, deliberately: the California licence registry is a public
state register, and grading public-record data as a blocking disclosure is how a
gate earns a reputation for crying wolf. Genuine category-4 material is caught by
`audit_sensitive_content.py`, which inspects content rather than path. See the
rationale comment in `scripts/audit_large_files.py`.

Neither audit can see the exposure that is still open. `LARGE-004` scans
`git rev-list --all` in the *local* clone, and a CI checkout has no
`refs/pull/*` refs, so the pull-ref exposure is structurally invisible to the
gate. A green CI run is evidence about `origin/main`, never about what GitHub
still serves. Check that with `git ls-remote origin 'refs/pull/*'` and an
unauthenticated fetch, by hand.

> **This is a history rewrite.** It changes every commit SHA from the first
> touched commit onward, requires a force-push to `main`, and invalidates every
> outstanding clone, branch and open pull request. Coordinate with all
> contributors before executing, and expect GitHub to retain unreachable objects
> afterwards — treat any exposed credential as compromised and rotate it.

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
