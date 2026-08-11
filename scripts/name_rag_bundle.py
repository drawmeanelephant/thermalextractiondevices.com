#!/usr/bin/env python3
"""Create a semantically named upload copy of a Boris working RAG export.

Boris deliberately keeps working-pack filenames generic (``working-N.md``)
so its own export is stable across products. TED's upload handoff needs the
same deterministic bytes with filenames that identify the corpus and the
content range. This helper copies pack bytes unchanged and rewrites only the
manifest paths and pack references.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any


WORKING_PACK_RE = re.compile(r"working-[0-9]+\.md\Z")


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def slugify(value: str) -> str:
    """Return a stable lower-case filename component."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("bundle name must contain at least one letter or digit")
    return slug


def _safe_relpath(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"manifest {field} must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"manifest {field} escapes the RAG input directory: {value!r}")
    return path.as_posix()


def _collection_name(source: str) -> str:
    parts = PurePosixPath(source).parts
    if len(parts) > 1:
        return slugify(parts[0])
    return slugify(PurePosixPath(source).stem)


def _semantic_range(documents: list[dict[str, Any]]) -> str:
    labels: list[str] = []
    for document in documents:
        source = document.get("source")
        if not isinstance(source, str) or not source:
            raise ValueError("manifest documents must include a non-empty source")
        label = _collection_name(source)
        if not labels or labels[-1] != label:
            labels.append(label)

    if not labels:
        return "corpus"
    unique_labels = list(dict.fromkeys(labels))
    if len(unique_labels) == 1:
        return unique_labels[0]
    if labels[0] == labels[-1]:
        return f"{labels[0]}-mixed"
    return f"{labels[0]}-to-{labels[-1]}"


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_named_bundle(
    input_dir: Path,
    output_dir: Path,
    bundle_name: str,
) -> list[str]:
    """Copy and rename a Boris working export, returning upload filenames."""

    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()
    if input_dir == output_dir:
        raise ValueError("RAG input and named output directories must differ")
    if _is_within(output_dir, input_dir) or _is_within(input_dir, output_dir):
        raise ValueError("RAG input and named output directories must be siblings, not nested")

    manifest_path = input_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"Boris working manifest is missing: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read Boris working manifest: {exc}") from exc

    if manifest.get("mode") != "working":
        raise ValueError("named upload bundles require a Boris working-mode manifest")
    upload_files = manifest.get("upload_files")
    documents = manifest.get("documents")
    if not isinstance(upload_files, list) or not upload_files:
        raise ValueError("working manifest has no upload_files")
    if not isinstance(documents, list):
        raise ValueError("working manifest has no documents list")

    documents_by_pack: dict[str, list[dict[str, Any]]] = {}
    for raw_document in documents:
        if not isinstance(raw_document, dict):
            raise ValueError("working manifest documents must be objects")
        pack = _safe_relpath(raw_document.get("pack"), field="document.pack")
        documents_by_pack.setdefault(pack, []).append(raw_document)

    name_slug = slugify(bundle_name)
    total = len(upload_files)
    width = max(2, len(str(total)))
    path_map: dict[str, str] = {}
    named_upload_files: list[dict[str, Any]] = []
    staged_files: list[tuple[Path, Path]] = []
    used_names: set[str] = set()

    for index, raw_entry in enumerate(upload_files, start=1):
        if not isinstance(raw_entry, dict):
            raise ValueError("working manifest upload_files must be objects")
        old_path = _safe_relpath(raw_entry.get("path"), field="upload_files.path")
        if not WORKING_PACK_RE.fullmatch(PurePosixPath(old_path).name) or "/" in old_path:
            raise ValueError(f"unexpected Boris working pack path: {old_path!r}")
        source_path = input_dir / old_path
        if not source_path.is_file():
            raise ValueError(f"Boris working pack is missing: {source_path}")

        label = _semantic_range(documents_by_pack.get(old_path, []))
        ordinal = str(index).zfill(width)
        final_ordinal = str(total).zfill(width)
        new_path = (
            f"{name_slug}-working-context-{ordinal}-of-"
            f"{final_ordinal}-{label}.md"
        )
        if new_path in used_names:
            raise ValueError(f"semantic filename collision: {new_path}")
        used_names.add(new_path)
        path_map[old_path] = new_path

        named_entry = dict(raw_entry)
        named_entry["path"] = new_path
        named_upload_files.append(named_entry)
        staged_files.append((source_path, Path(new_path)))

    for raw_document in documents:
        old_pack = _safe_relpath(raw_document.get("pack"), field="document.pack")
        if old_pack not in path_map:
            raise ValueError(f"document refers to an unlisted pack: {old_pack!r}")
        raw_document["pack"] = path_map[old_pack]
    manifest["upload_files"] = named_upload_files

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage_dir = output_dir.parent / f".{output_dir.name}.stage"
    if stage_dir.exists() or stage_dir.is_symlink():
        if stage_dir.is_dir() and not stage_dir.is_symlink():
            shutil.rmtree(stage_dir)
        else:
            stage_dir.unlink()
    stage_dir.mkdir()
    try:
        for source_path, relative_path in staged_files:
            shutil.copyfile(source_path, stage_dir / relative_path)
        _write_json(stage_dir / "manifest.json", manifest)

        if output_dir.exists() or output_dir.is_symlink():
            if output_dir.is_dir() and not output_dir.is_symlink():
                shutil.rmtree(output_dir)
            else:
                output_dir.unlink()
        stage_dir.replace(output_dir)
    except Exception:
        if stage_dir.exists() or stage_dir.is_symlink():
            if stage_dir.is_dir() and not stage_dir.is_symlink():
                shutil.rmtree(stage_dir)
            else:
                stage_dir.unlink()
        raise

    return [entry["path"] for entry in named_upload_files]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a semantically named upload copy of a Boris working RAG export."
    )
    parser.add_argument("--input", required=True, type=Path, help="Boris working RAG directory")
    parser.add_argument("--output", required=True, type=Path, help="named upload directory")
    parser.add_argument(
        "--name",
        default="thermal-extraction-devices",
        help="semantic corpus name used in upload filenames",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        filenames = create_named_bundle(args.input, args.output, args.name)
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot create named RAG bundle: {exc}", file=sys.stderr)
        return 2
    print(
        f"✅ Named {len(filenames)} RAG upload pack(s) in {args.output}: "
        f"{filenames[0]} … {filenames[-1]}"
    )
    print("   manifest.json is a sidecar; upload the named .md packs only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
