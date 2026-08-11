#!/usr/bin/env python3
"""Create a resolved copy of Boris's working RAG export.

The input directory is treated as immutable provenance. Only the derived
output directory is replaced, and it must be a sibling of the input directory
so an accidental broad path cannot be recursively removed. The output keeps
the Boris working-pack layout while adding explicit derivation and hash
metadata to its manifest.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
from typing import Any

# Allow the publish wrapper to invoke this file as ``python3 scripts/...`` as
# well as allowing the test suite to import it as ``scripts....``.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.rag_includes import (
    IncludeResolver,
    audit_content_includes,
    format_include_issues,
    iter_include_markers,
)


WORKING_PACK_RE = re.compile(r"working-[0-9]+\.md\Z")


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_manifest_path(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"manifest {field} must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"manifest {field} escapes its input directory: {value!r}")
    return path.as_posix()


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _remove_generated_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _validate_sibling_output(input_dir: Path, output_dir: Path) -> None:
    if input_dir == output_dir:
        raise ValueError("resolved RAG output must differ from the raw input")
    if input_dir.parent != output_dir.parent:
        raise ValueError("resolved RAG output must be a sibling of the raw input")
    if output_dir.exists() and output_dir.is_symlink():
        raise ValueError("resolved RAG output may not be a symlink")


def _manifest(input_dir: Path) -> tuple[dict[str, Any], bytes]:
    path = input_dir / "manifest.json"
    if not path.is_file():
        raise ValueError(f"Boris working manifest is missing: {path}")
    raw = path.read_bytes()
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read Boris working manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("Boris working manifest must be a JSON object")
    if manifest.get("mode") != "working":
        raise ValueError("resolved RAG input requires a Boris working-mode manifest")
    if not isinstance(manifest.get("upload_files"), list) or not manifest["upload_files"]:
        raise ValueError("working manifest has no upload_files")
    if not isinstance(manifest.get("documents"), list):
        raise ValueError("working manifest has no documents list")
    return manifest, raw


def create_resolved_export(
    input_dir: Path,
    output_dir: Path,
    content_root: Path,
    *,
    include_dir: str = "includes",
) -> dict[str, Any]:
    """Resolve a Boris working export and return its derived manifest."""

    raw_dir = input_dir.resolve(strict=True)
    if not raw_dir.is_dir():
        raise ValueError(f"RAG input is not a directory: {input_dir}")
    resolved_dir = output_dir.resolve(strict=False)
    _validate_sibling_output(raw_dir, resolved_dir)
    content = content_root.resolve(strict=True)
    if not content.is_dir():
        raise ValueError(f"content root is not a directory: {content_root}")

    source_audit = audit_content_includes(content, include_dir=include_dir)
    if source_audit.issues:
        raise ValueError(
            "content include audit failed:\n" + format_include_issues(source_audit.issues)
        )

    manifest, raw_manifest_bytes = _manifest(raw_dir)
    upload_files = manifest["upload_files"]
    documents = manifest["documents"]
    resolver = IncludeResolver(
        content / include_dir,
        include_prefix=include_dir,
    )
    resolved_packs: list[tuple[dict[str, Any], bytes, bytes, str]] = []
    raw_reference_count = 0
    raw_references: set[str] = set()

    for raw_entry in upload_files:
        if not isinstance(raw_entry, dict):
            raise ValueError("working manifest upload_files must be objects")
        relative = _safe_manifest_path(raw_entry.get("path"), field="upload_files.path")
        if not WORKING_PACK_RE.fullmatch(PurePosixPath(relative).name) or "/" in relative:
            raise ValueError(f"unexpected Boris working pack path: {relative!r}")
        source_path = raw_dir / relative
        if not source_path.is_file():
            raise ValueError(f"Boris working pack is missing: {source_path}")
        raw_bytes = source_path.read_bytes()
        try:
            raw_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Boris working pack is not UTF-8: {source_path}") from exc
        markers = list(iter_include_markers(raw_text))
        raw_reference_count += len(markers)
        raw_references.update(
            marker.reference for marker in markers if marker.reference is not None
        )
        resolved_text = resolver.resolve_text(raw_text, source=relative)
        resolved_bytes = resolved_text.encode("utf-8")
        if list(iter_include_markers(resolved_text)):
            raise ValueError(f"resolved working pack still contains an include: {relative}")
        resolved_packs.append((raw_entry, raw_bytes, resolved_bytes, relative))

    resolved_manifest = copy.deepcopy(manifest)
    resolved_manifest["surface"] = "resolved-working"
    resolved_manifest["representation"] = "boris-working-with-includes-expanded"
    resolved_manifest["resolved_from"] = {
        "surface": "boris-working",
        "manifest": "manifest.json",
        "manifest_sha256": _sha256(raw_manifest_bytes),
    }
    resolved_manifest["include_resolution"] = {
        "include_root": f"content/{include_dir.strip('/')}",
        "source_files_scanned": source_audit.files_scanned,
        "source_references": source_audit.reference_count,
        "raw_pack_references": raw_reference_count,
        "unique_include_files": sorted(raw_references),
        "unresolved_markers": 0,
    }

    resolved_upload_files: list[dict[str, Any]] = []
    for raw_entry, raw_bytes, resolved_bytes, _relative in resolved_packs:
        entry = dict(raw_entry)
        entry["raw_bytes"] = len(raw_bytes)
        entry["raw_sha256"] = _sha256(raw_bytes)
        entry["bytes"] = len(resolved_bytes)
        entry["sha256"] = _sha256(resolved_bytes)
        resolved_upload_files.append(entry)
    resolved_manifest["upload_files"] = resolved_upload_files

    resolved_documents: list[dict[str, Any]] = []
    source_cache: dict[str, bytes] = {}
    for raw_document in documents:
        if not isinstance(raw_document, dict):
            raise ValueError("working manifest documents must be objects")
        source = _safe_manifest_path(raw_document.get("source"), field="document.source")
        source_path = content / Path(*PurePosixPath(source).parts)
        source_resolved = source_path.resolve(strict=False)
        if not _is_within(source_resolved, content) or not source_resolved.is_file():
            raise ValueError(f"manifest document source is unavailable: {source!r}")
        if source not in source_cache:
            source_raw = source_resolved.read_bytes()
            source_text = source_raw.decode("utf-8")
            source_cache[source] = resolver.resolve_text(source_text, source=source)
        resolved_source_bytes = source_cache[source].encode("utf-8")
        document = dict(raw_document)
        if "bytes" in raw_document:
            document["raw_bytes"] = raw_document["bytes"]
        document["bytes"] = len(resolved_source_bytes)
        document["resolved_source_sha256"] = _sha256(resolved_source_bytes)
        resolved_documents.append(document)
    resolved_manifest["documents"] = resolved_documents

    resolved_dir.parent.mkdir(parents=True, exist_ok=True)
    stage_dir = resolved_dir.parent / f".{resolved_dir.name}.stage"
    if stage_dir.exists() or stage_dir.is_symlink():
        _remove_generated_path(stage_dir)
    stage_dir.mkdir()
    try:
        for _raw_entry, _raw_bytes, resolved_bytes, relative in resolved_packs:
            (stage_dir / relative).write_bytes(resolved_bytes)
        _write_json(stage_dir / "manifest.json", resolved_manifest)
        if resolved_dir.exists() or resolved_dir.is_symlink():
            _remove_generated_path(resolved_dir)
        stage_dir.replace(resolved_dir)
    except Exception:
        if stage_dir.exists() or stage_dir.is_symlink():
            _remove_generated_path(stage_dir)
        raise

    return resolved_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a resolved copy of a Boris working RAG export."
    )
    parser.add_argument("--input", required=True, type=Path, help="raw Boris working RAG directory")
    parser.add_argument("--output", required=True, type=Path, help="derived resolved RAG directory")
    parser.add_argument("--content", required=True, type=Path, help="canonical content root")
    parser.add_argument(
        "--include-dir",
        default="includes",
        help="include directory below --content (default: includes)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = create_resolved_export(
            args.input,
            args.output,
            args.content,
            include_dir=args.include_dir,
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: cannot resolve RAG includes: {exc}", file=sys.stderr)
        return 2
    pack_count = len(manifest["upload_files"])
    print(
        f"✅ Resolved {pack_count} Boris RAG working pack(s) in {args.output}; "
        "raw input preserved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
