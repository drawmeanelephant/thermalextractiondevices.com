#!/usr/bin/env python3
"""Build the TED site twice and prove path-and-byte reproducibility.

The checker deliberately uses the production ``scripts/ted-build.sh`` wrapper
so ID, link, graph, crosslink, HTML, and release gates are part of both builds.
Generated working files stay under ``dist/`` because Boris rejects output that
escapes the repository workspace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class FileRecord:
    size: int
    sha256: str


@dataclass(frozen=True)
class TreeInventory:
    file_count: int
    total_bytes: int
    tree_sha256: str
    files: Mapping[str, FileRecord]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory_tree(root: Path) -> TreeInventory:
    """Inventory every regular file using its relative path and exact bytes."""
    if not root.is_dir():
        raise ValueError(f"build output is not a directory: {root}")

    aggregate = hashlib.sha256()
    records: dict[str, FileRecord] = {}
    total_bytes = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"build output contains an unsupported symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        relative_bytes = relative.encode("utf-8")
        payload = path.read_bytes()
        aggregate.update(len(relative_bytes).to_bytes(8, "big"))
        aggregate.update(relative_bytes)
        aggregate.update(len(payload).to_bytes(8, "big"))
        aggregate.update(payload)
        records[relative] = FileRecord(
            size=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
        )
        total_bytes += len(payload)

    return TreeInventory(
        file_count=len(records),
        total_bytes=total_bytes,
        tree_sha256=aggregate.hexdigest(),
        files=records,
    )


def compare_inventories(first: TreeInventory, second: TreeInventory) -> dict[str, list[str]]:
    first_paths = set(first.files)
    second_paths = set(second.files)
    return {
        "only_in_first": sorted(first_paths - second_paths),
        "only_in_second": sorted(second_paths - first_paths),
        "changed": sorted(
            path for path in first_paths & second_paths
            if first.files[path] != second.files[path]
        ),
    }


def safe_work_dir(root: Path, requested: Path) -> Path:
    """Resolve an isolated child of ``dist/`` and refuse broad delete targets."""
    root = root.resolve()
    dist_root = (root / "dist").resolve()
    candidate = requested if requested.is_absolute() else root / requested
    candidate = candidate.resolve(strict=False)
    if candidate == dist_root or dist_root not in candidate.parents:
        raise ValueError(
            f"work directory must be a child of {dist_root}, not {candidate}"
        )
    return candidate


def git_value(root: Path, *args: str, default: str = "unknown") -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else default


def resolve_boris(root: Path, explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        return (root / path).resolve() if not path.is_absolute() else path.resolve()
    result = subprocess.run(
        [str(root / "scripts" / "ensure-boris.sh")],
        cwd=root, text=True, stdout=subprocess.PIPE, check=True,
    )
    return Path(result.stdout.strip()).resolve()


def run_build(root: Path, build_script: Path, boris_bin: Path,
              output: Path, log_path: Path) -> None:
    environment = os.environ.copy()
    environment.update({
        "BORIS_BIN": str(boris_bin),
        "BORIS_JOBS": "1",
        "DIST_DIR": output.relative_to(root).as_posix(),
    })
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(
            [str(build_script)], cwd=root, env=environment,
            stdout=log, stderr=subprocess.STDOUT, text=True, check=False,
        )
    if result.returncode:
        tail = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-30:]
        print(f"reproducibility: build failed ({result.returncode}); log: {log_path}",
              file=sys.stderr)
        for line in tail:
            print(line, file=sys.stderr)
        raise RuntimeError(f"build failed with exit code {result.returncode}")


def report_inventory(inventory: TreeInventory) -> dict[str, object]:
    return {
        "file_count": inventory.file_count,
        "total_bytes": inventory.total_bytes,
        "tree_sha256": inventory.tree_sha256,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository root (default: script parent repository)")
    parser.add_argument("--boris-bin",
                        help="pinned Boris binary (default: resolve with ensure-boris.sh)")
    parser.add_argument("--work-dir", type=Path, default=Path("dist/reproducibility"),
                        help="isolated child of dist/ for builds, logs, and report")
    parser.add_argument("--keep-builds", action="store_true",
                        help="retain first/ and second/ output trees after comparison")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()
    try:
        work_dir = safe_work_dir(root, args.work_dir)
    except ValueError as error:
        print(f"reproducibility: {error}", file=sys.stderr)
        return 2

    build_script = root / "scripts" / "ted-build.sh"
    try:
        boris_bin = resolve_boris(root, args.boris_bin)
    except (OSError, subprocess.SubprocessError) as error:
        print(f"reproducibility: cannot resolve Boris: {error}", file=sys.stderr)
        return 2
    if not boris_bin.is_file() or not os.access(boris_bin, os.X_OK):
        print(f"reproducibility: Boris is not executable: {boris_bin}", file=sys.stderr)
        return 2

    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)
    first_dir = work_dir / "first"
    second_dir = work_dir / "second"

    source_commit = git_value(root, "rev-parse", "HEAD")
    source_status = git_value(root, "status", "--porcelain", "--untracked-files=all", default="")
    try:
        run_build(root, build_script, boris_bin, first_dir, work_dir / "first.log")
        first = inventory_tree(first_dir)
        run_build(root, build_script, boris_bin, second_dir, work_dir / "second.log")
        second = inventory_tree(second_dir)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"reproducibility: {error}", file=sys.stderr)
        return 2

    differences = compare_inventories(first, second)
    reproducible = not any(differences.values()) and first.tree_sha256 == second.tree_sha256
    boris_metadata = json.loads((root / "metadata" / "boris-version.json").read_text(
        encoding="utf-8"
    ))
    report = {
        "schema_version": 1,
        "reproducible": reproducible,
        "source": {
            "commit": source_commit,
            "worktree_dirty": bool(source_status),
        },
        "toolchain": {
            "repository": boris_metadata["repository"],
            "commit": boris_metadata["commit"],
            "zig_version": boris_metadata["zig_version"],
            "binary_sha256": sha256_file(boris_bin),
        },
        "build": {
            "command": "scripts/ted-build.sh",
            "boris_jobs": 1,
            "first": report_inventory(first),
            "second": report_inventory(second),
            "differences": differences,
        },
    }
    report_path = work_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")

    if reproducible:
        print(
            "reproducibility: PASS "
            f"files={first.file_count} bytes={first.total_bytes} "
            f"sha256={first.tree_sha256} report={report_path.relative_to(root)}"
        )
    else:
        print(
            "reproducibility: FAIL "
            f"only_first={len(differences['only_in_first'])} "
            f"only_second={len(differences['only_in_second'])} "
            f"changed={len(differences['changed'])} report={report_path.relative_to(root)}",
            file=sys.stderr,
        )

    if reproducible and not args.keep_builds:
        shutil.rmtree(first_dir)
        shutil.rmtree(second_dir)
    return 0 if reproducible else 1


if __name__ == "__main__":
    raise SystemExit(main())
