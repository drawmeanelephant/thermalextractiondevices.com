#!/usr/bin/env python3
"""Audit large tracked files and reachable git history blobs.

Reports:

* the largest tracked files in the current tree
* the largest blobs reachable from any ref (i.e. everything that would
  remain visible if the repository were made public)
* duplicate blobs (identical content tracked under more than one path),
  which is the signature of duplicated raw/normalized/latest/previous
  datasets
* committed generated artifacts (``dist/``, ``publish/``, ``.tools/``, ...)
* candidates for external artifact storage (blobs above a size threshold)

With ``--plan`` it also prints the recommended, non-executed history-cleanup
command plan (backup, ``git filter-repo``, verification, force-push
implications). The authoritative version of that plan lives in
``docs/history-cleanup-plan.md``.

Exit codes: 0 = no findings above threshold, 1 = findings, 2 = tool error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from audit_common import (
    Finding,
    human_path,
    is_generated_artifact,
    is_suppressed,
    load_config,
    severity_rank,
)

CLEANUP_PLAN = """\
Recommended history-cleanup plan (NOT executed by this tool; see docs/history-cleanup-plan.md):

  # 0. Preconditions
  #   - Coordinate with all clone holders and CI; a rewrite invalidates every fork and clone.
  #   - Create a full backup before any rewrite.
  git clone --mirror <url> /tmp/thermalextractiondevices-backup.git
  git bundle create /tmp/thermalextractiondevices-backup.bundle --all

  # 1. Install the standard history-rewrite tool
  pip install git-filter-repo   # or: brew install git-filter-repo

  # 2. Fresh clone (filter-repo refuses to run on a non-fresh clone)
  git clone --no-local <url> /tmp/clean-work
  cd /tmp/clean-work

  # 3. Strip the offending paths/blobs from all history (example for dist/):
  git filter-repo --path dist/ --path publish/ --path .tools/ --invert-paths

  # 4. Verify before pushing
  git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize)' | awk '$1=="blob" && $2>5000000 {print}'   # expect: no giants
  git log --all --oneline | head                    # expect: rewritten history reads correctly

  # 5. Force-push to every remote branch and delete stale remote refs
  git push --force --all origin
  git push --force --tags origin

  # 6. Implications (documented for maintainers)
  #   - Force-push rewrites history: everyone must re-clone; stale forks remain.
  #   - Anybody who cloned the old history retains the removed blobs locally.
  #   - GitHub may retain unreachable objects until GC; consider GitHub Support scrub
  #     or rotating secrets, since deleted blobs can survive in forks and caches.
  #   - The GitHub noreply author identity is unaffected; no author rewriting needed.
"""


def _git(root: Path, args: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root)] + args,
            capture_output=True, text=True, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return proc.returncode, proc.stdout


def reachable_blobs(root: Path) -> List[Tuple[str, int, str]]:
    """Return (sha, size, path) for every blob reachable from any ref.

    Path multiplicity is preserved: when the same blob is reachable under
    two paths (the signature of duplicated datasets), both entries appear.
    """
    rc, out = _git(root, ["rev-list", "--objects", "--all"])
    if rc != 0 or not out:
        return []
    # Preserve (sha, path) pairs WITHOUT collapsing by sha, so identical
    # content under multiple paths is visible to the duplicate check.
    pairs: List[Tuple[str, str]] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2:
            pairs.append((parts[0], parts[1]))
    if not pairs:
        return []
    batch = "\n".join(sha for sha, _ in pairs) + "\n"
    proc = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch-check=%(objecttype) %(objectname) %(objectsize)"],
        input=batch, capture_output=True, text=True, check=False,
    )
    sizes: Dict[str, int] = {}
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[0] == "blob":
                sizes[parts[1]] = int(parts[2])
    blobs = []
    for sha, path in pairs:
        if sha in sizes:
            blobs.append((sha, sizes[sha], path))
    return blobs


def duplicate_entries(root: Path) -> List[Tuple[str, List[str]]]:
    """Return (sha, paths) for every blob whose identical content appears
    under two or more distinct paths anywhere in reachable history.

    Uses `git ls-tree -r` (git's own object store already deduplicates
    blobs by content, so path multiplicity only shows up at the tree
    level; `git rev-list --objects` collapses it).
    """
    rc, commits = _git(root, ["rev-list", "--all"])
    if rc != 0 or not commits:
        return []
    paths_by_sha: Dict[str, set] = defaultdict(set)
    for commit in commits.splitlines():
        rc, out = _git(root, ["ls-tree", "-r", "--full-tree", commit])
        if rc != 0:
            continue
        for line in out.splitlines():
            meta, _, path = line.partition("\t")
            fields = meta.split()
            if len(fields) == 3 and fields[1] == "blob":
                paths_by_sha[fields[2]].add(path)
    return [(sha, sorted(paths)) for sha, paths in paths_by_sha.items() if len(paths) > 1]


def deleted_but_reachable(root: Path) -> List[Tuple[str, int]]:
    """Paths deleted at some point but whose blobs remain reachable in
    history (i.e. they would still be visible if the repo went public).

    Returns (path, last-known blob size) pairs, most recent deletion first.
    """
    rc, out = _git(root, ["log", "--all", "--pretty=format:", "--name-only", "--diff-filter=D"])
    if rc != 0:
        return []
    paths = []
    for line in out.splitlines():
        line = line.strip()
        if line and line not in paths:
            paths.append(line)
    # Map each deleted path to the size of its last blob.
    result = []
    if paths:
        rc, objects = _git(root, ["rev-list", "--objects", "--all"])
        sha_for_path: Dict[str, str] = {}
        for line in objects.splitlines():
            parts = line.split()
            if len(parts) == 2:
                sha_for_path[parts[1]] = parts[0]
        batch = "\n".join(sha_for_path[p] for p in paths if p in sha_for_path) + "\n"
        if batch.strip():
            proc = subprocess.run(
                ["git", "-C", str(root), "cat-file", "--batch-check=%(objecttype) %(objectname) %(objectsize)"],
                input=batch, capture_output=True, text=True, check=False,
            )
            sizes = {}
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    parts = line.split()
                    if len(parts) == 3 and parts[0] == "blob":
                        sizes[parts[1]] = int(parts[2])
            for path in paths:
                sha = sha_for_path.get(path)
                result.append((path, sizes.get(sha, 0)))
    return result


def tracked_sizes(root: Path) -> List[Tuple[str, int]]:
    """Repo-relative path and byte size of every tracked file."""
    rc, out = _git(root, ["ls-files", "-z"])
    if rc != 0 or not out:
        return []
    sizes = []
    for rel in out.split("\0"):
        if not rel:
            continue
        path = root / rel
        try:
            sizes.append((rel, path.stat().st_size))
        except OSError:
            continue
    return sizes


def audit(root: Path, config: Dict[str, Any]) -> Tuple[List[Finding], Dict[str, Any]]:
    findings: List[Finding] = []
    report: Dict[str, Any] = {"total_tracked_bytes": 0, "total_reachable_blob_bytes": 0}

    large_bytes = int(config.get("thresholds", {}).get("large_file_bytes", 5_000_000))
    review_bytes = int(config.get("thresholds", {}).get("review_file_bytes", 1_000_000))
    limit = int(config.get("thresholds", {}).get("report_limit", 25))
    allow_large = set(config.get("allowlist", {}).get("large_files", []))
    allow_dup = set(config.get("allowlist", {}).get("duplicate_blobs", []))

    # --- tracked tree -----------------------------------------------------
    sizes = tracked_sizes(root)
    report["total_tracked_bytes"] = sum(size for _, size in sizes)
    report["largest_tracked_files"] = [
        {"path": p, "bytes": s}
        for p, s in sorted(sizes, key=lambda item: item[1], reverse=True)[:limit]
    ]
    for rel, size in sizes:
        if size >= large_bytes and rel not in allow_large:
            findings.append(Finding(
                code="LARGE-001", severity="medium",
                message="giant tracked file ({} MiB)".format(round(size / 1048576, 1)),
                path=human_path(rel),
            ))
        if size >= review_bytes and rel not in allow_large:
            findings.append(Finding(
                code="REV-002", severity="low",
                message="large tracked file for human review ({} MiB)".format(round(size / 1048576, 1)),
                path=human_path(rel),
            ))
        if is_generated_artifact(rel, config):
            findings.append(Finding(
                code="GEN-001", severity="high",
                message="generated artifact is committed",
                path=human_path(rel), detail="{} bytes".format(size),
            ))

    # --- reachable history blobs ------------------------------------------
    blobs = reachable_blobs(root)
    report["total_reachable_blob_bytes"] = sum(size for _, size, _ in blobs)
    report["largest_reachable_blobs"] = [
        {"sha": sha[:12], "bytes": size, "path": path}
        for sha, size, path in sorted(blobs, key=lambda item: item[1], reverse=True)[:limit]
    ]
    report["blobs_visible_if_public"] = len(blobs)

    # External-storage candidates: blobs above the large threshold.
    candidates = sorted((b for b in blobs if b[1] >= large_bytes),
                        key=lambda item: item[1], reverse=True)
    report["external_storage_candidates"] = [
        {"sha": sha[:12], "bytes": size, "path": path}
        for sha, size, path in candidates
    ]
    for sha, size, path in candidates:
        findings.append(Finding(
            code="LARGE-002", severity="low",
            message="blob is a candidate for external artifact storage",
            path=human_path(path) if path else "<no-path>",
            detail="{} bytes (sha {})".format(size, sha[:12]),
        ))

    # --- duplicate blobs ---------------------------------------------------
    sizes_by_sha = {sha: size for sha, size, _ in blobs}
    duplicates = []
    for sha, paths in duplicate_entries(root):
        if any(sha.startswith(prefix) for prefix in allow_dup):
            continue
        duplicates.append({"sha": sha[:12], "bytes": sizes_by_sha.get(sha, 0), "paths": paths})
        findings.append(Finding(
            code="LARGE-003", severity="medium",
            message="duplicate blob (identical content under {} paths)".format(len(paths)),
            path=human_path(paths[0]), detail="; ".join(paths[:6]),
        ))
    report["duplicate_blobs"] = duplicates

    # --- deleted-but-still-reachable ---------------------------------------
    deleted = deleted_but_reachable(root)
    report["deleted_but_reachable"] = [
        {"path": path, "bytes": size} for path, size in deleted
    ]
    # A deleted file that is still reachable is only an efficiency problem for
    # ordinary build output — but for paths carrying PRIVACY.md category-4 data it
    # is a live disclosure: `git show <old-commit>:<path>` returns the payload in
    # full. Removing it from the working tree does not remove it from any clone.
    # Those paths block; everything else informs.
    sensitive_prefixes = tuple(config.get("history_sensitive_paths", ["data/"]))
    for path, size in deleted:
        if size >= large_bytes:
            human = human_path(path)
            if human.startswith(sensitive_prefixes):
                findings.append(Finding(
                    code="LARGE-004", severity="high",
                    message=(
                        "deleted file remains reachable in git history ({} MiB) under a path "
                        "carrying regulated data — still recoverable from any clone; see "
                        "docs/history-cleanup-plan.md".format(round(size / 1048576, 1))
                    ),
                    path=human,
                ))
            else:
                findings.append(Finding(
                    code="LARGE-004", severity="medium",
                    message="deleted file remains reachable in history ({} MiB)".format(round(size / 1048576, 1)),
                    path=human,
                ))

    return findings, report


def render(findings: List[Finding], config: Dict[str, Any], report: Dict[str, Any]) -> str:
    limit = int(config.get("thresholds", {}).get("report_limit", 25))
    lines = ["Large-file & history audit: {} finding(s)".format(len(findings))]
    if report.get("largest_tracked_files"):
        lines.append("\nLargest tracked files (top {}):".format(min(limit, len(report["largest_tracked_files"]))))
        for item in report["largest_tracked_files"]:
            lines.append("  {:>10,} bytes  {}".format(item["bytes"], item["path"]))
    if report.get("largest_reachable_blobs"):
        lines.append("\nLargest reachable git blobs (top {}, visible if public):".format(min(limit, len(report["largest_reachable_blobs"]))))
        for item in report["largest_reachable_blobs"]:
            lines.append("  {:>10,} bytes  {}  {}".format(item["bytes"], item["path"] or "<no path>", item["sha"]))
    if report.get("duplicate_blobs"):
        lines.append("\nDuplicate blobs ({}):".format(len(report["duplicate_blobs"])))
        for item in report["duplicate_blobs"]:
            lines.append("  {} ({} bytes): {}".format(item["sha"], item["bytes"], ", ".join(item["paths"][:4])))
    if report.get("external_storage_candidates"):
        lines.append("\nExternal-storage candidates ({}):".format(len(report["external_storage_candidates"])))
        for item in report["external_storage_candidates"]:
            lines.append("  {}  {}".format(item["path"] or item["sha"], item["bytes"]))
    if report.get("deleted_but_reachable"):
        lines.append("\nDeleted but still reachable in history ({}):".format(len(report["deleted_but_reachable"])))
        for item in report["deleted_but_reachable"][:limit]:
            lines.append("  {}  {} bytes".format(item["path"], item["bytes"]))
    lines.append("\nTotals: tracked {:,} bytes; reachable history {:,} bytes; {} blobs visible if public".format(
        report.get("total_tracked_bytes", 0), report.get("total_reachable_blob_bytes", 0),
        report.get("blobs_visible_if_public", 0)))
    for finding in findings:
        if is_suppressed(finding, config):
            continue
        lines.append("[{}] {:>8} {} {}".format(finding.code, finding.severity.upper(), finding.path, finding.message))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--plan", action="store_true",
                        help="print the non-executed history-cleanup command plan")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    if args.plan:
        print(CLEANUP_PLAN)
        return 0

    root = args.root.resolve()
    try:
        config = load_config(args.config)
        findings, report = audit(root, config)
    except Exception as error:  # tool error => exit 2, never misread as findings
        print("large-file audit: error: {}".format(error), file=sys.stderr)
        return 2

    try:
        if args.as_json or args.report is not None:
            payload = {"findings": [f.to_dict() for f in findings], "report": report}
            if args.as_json:
                print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            if args.report is not None:
                args.report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if not args.as_json:
            print(render(findings, config, report))
        active = [f for f in findings if not is_suppressed(f, config)]
        blocking = [f for f in active if severity_rank(f.severity) >= severity_rank(str(config.get("fail_threshold", "high")))]
        if blocking:
            print("large-file audit: {} blocking finding(s); see above".format(len(blocking)), file=sys.stderr)
            return 1
        print("large-file audit: no findings above fail threshold ({})".format(config.get("fail_threshold", "high")))
        return 0
    except Exception as error:
        print("large-file audit: error while rendering: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
