#!/usr/bin/env python3
"""Normalize and validate Thermal Extraction Devices form-based entity IDs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


DEFAULT_PREFIX = {
    "affected-products": "TAFP",
    "botanicals": "TBOT",
    "changelog": "TCHG",
    "contaminants": "TCNT",
    "cultivars": "TCUL",
    "datasets": "TDTS",
    "devices": "TED",
    "guides": "TGDE",
    "jurisdictions": "TJUR",
    "lab-results": "TLAB",
    "law-and-use": "TLAW",
    "licenses": "TLIC",
    "manufacturers": "TMFR",
    "organizations": "TORG",
    "products": "TPRD",
    "recalls": "TRCL",
    "reference": "TREF",
    "releases": "TREL",
    "requirements": "TREQ",
    "safety": "TSAFE",
    "safety-advisories": "TSAD",
    "specs": "TSPEC",
    "terpenes": "TTRP",
    "testing-laboratories": "TSTL",
}

FORM_PREFIXES = {
    "affected-products": ("TAFP",),
    "botanicals": ("TBOT",),
    "changelog": ("TCHG",),
    "contaminants": ("TCNT",),
    "cultivars": ("TCUL",),
    "datasets": ("TDTS",),
    "devices": ("TED",),
    "guides": ("TGDE",),
    "jurisdictions": ("TJUR",),
    "lab-results": ("TLAB",),
    "law-and-use": ("TLAW",),
    "licenses": ("TLIC",),
    "manufacturers": ("TMFR",),
    "organizations": ("TORG",),
    "products": ("TPRD",),
    "recalls": ("TRCL",),
    "reference": ("TREF",),
    "releases": ("TREL",),
    "requirements": ("TREQ",),
    "safety": ("TSAFE",),
    "safety-advisories": ("TSAD",),
    "specs": ("TSPEC",),
    "terpenes": ("TTRP",),
    "testing-laboratories": ("TSTL",),
}

ID_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
NUMERIC_TOKEN = re.compile(r"^\d{1,4}$")
FIELD_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*?)(?:\r?\n)?$")


class MigrationError(Exception):
    """A source or ID policy failure."""


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def read_frontmatter(path: Path) -> tuple[str, int, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise MigrationError(f"{path}: missing Boris frontmatter opening fence")

    close = None
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            close = index
            break
    if close is None:
        raise MigrationError(f"{path}: unclosed frontmatter")

    fields: dict[str, str] = {}
    for line in lines[1:close]:
        if not line.strip():
            continue
        match = FIELD_LINE.match(line)
        if not match:
            raise MigrationError(f"{path}: unsupported frontmatter line: {line.rstrip()}")
        key, value = match.groups()
        if key in fields:
            raise MigrationError(f"{path}: duplicate frontmatter key {key!r}")
        fields[key] = parse_scalar(value)

    body_offset = sum(len(line) for line in lines[: close + 1])
    return text, body_offset, fields


def replace_id(text: str, new_id: str) -> str:
    lines = text.splitlines(keepends=True)
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            break
        if lines[index].startswith("id:"):
            ending = "\r\n" if lines[index].endswith("\r\n") else "\n"
            lines[index] = f"id: {new_id}{ending}"
            return "".join(lines)
    raise MigrationError("frontmatter has no id field")


def normalize_numeric_tokens(code: str) -> str | None:
    parts = code.upper().split("-")
    if not parts or any(not part for part in parts):
        return None
    numeric = [index for index, part in enumerate(parts) if NUMERIC_TOKEN.fullmatch(part)]
    if not numeric:
        return None
    for index in numeric:
        parts[index] = parts[index].zfill(4)
    candidate = "-".join(parts)
    if not ID_PATTERN.fullmatch(candidate):
        return None
    return candidate


def form_id_for(collection: str, stem: str) -> str | None:
    base = stem.split(".", 1)[0]
    upper = base.upper()

    for prefix in FORM_PREFIXES.get(collection, ()):
        if upper == prefix or upper.startswith(prefix + "-"):
            return normalize_numeric_tokens(upper)
    return None


def allocate_form_id(collection: str, used: set[str]) -> str:
    prefix = DEFAULT_PREFIX.get(collection, "TED")
    for number in range(1, 10000):
        candidate = f"{prefix}-{number:04d}"
        if candidate not in used:
            return candidate
    raise MigrationError(f"{collection}: exhausted four-digit {prefix} form IDs")


def content_pages(root: Path) -> list[Path]:
    pages = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if any(part in ("includes", "_includes") or part.startswith("_") for part in rel.parts[:-1]) or rel.name.startswith("_"):
            continue
        pages.append(path)
    return sorted(pages, key=lambda path: path.relative_to(root).as_posix())


def build_records(root: Path, legacy_by_source: dict[str, str] | None = None) -> list[dict[str, str | None]]:
    records: list[dict[str, str | None]] = []
    used_by_collection: dict[str, set[str]] = {}
    pending: list[dict[str, str | None]] = []

    for path in content_pages(root):
        rel = path.relative_to(root)
        parts = rel.parts
        collection = parts[0] if len(parts) > 1 else "_root"
        text, body_offset, fields = read_frontmatter(path)
        current_id = fields.get("id", "")
        old_id = (legacy_by_source or {}).get(rel.as_posix(), current_id)
        title = fields.get("title", "")
        parent = fields.get("parent") or None

        if collection == "_root":
            new_id = old_id or path.stem
            records.append({
                "source": rel.as_posix(),
                "legacy_id": old_id,
                "current_id": current_id,
                "id": new_id,
                "form_id": None,
                "collection": path.stem,
                "parent": parent,
                "title": title,
                "role": "trunk",
                "_text": text,
                "_body_offset": body_offset,
            })
            continue

        used = used_by_collection.setdefault(collection, set())
        candidate = form_id_for(collection, path.stem)
        record = {
            "source": rel.as_posix(),
            "legacy_id": old_id,
            "current_id": current_id,
            "id": None,
            "form_id": candidate,
            "collection": collection,
            "parent": collection,
            "title": title,
            "role": "satellite",
            "_text": text,
            "_body_offset": body_offset,
        }
        if candidate is None:
            pending.append(record)
        else:
            if candidate in used:
                raise MigrationError(f"{path}: form ID collision in {collection}: {candidate}")
            used.add(candidate)
            record["id"] = f"{collection}/{candidate}"
            records.append(record)

    for record in sorted(pending, key=lambda item: str(item["source"])):
        collection = str(record["collection"])
        used = used_by_collection.setdefault(collection, set())
        candidate = allocate_form_id(collection, used)
        used.add(candidate)
        record["form_id"] = candidate
        record["id"] = f"{collection}/{candidate}"
        records.append(record)

    records.sort(key=lambda item: str(item["source"]))
    return records


def validate_records(records: list[dict[str, str | None]], require_current_ids: bool = False) -> None:
    ids: dict[str, str] = {}
    roots = {str(record["id"]) for record in records if record["role"] == "trunk"}
    for record in records:
        source = str(record["source"])
        entity_id = str(record["id"])
        if entity_id in ids:
            raise MigrationError(f"duplicate entity ID {entity_id!r}: {ids[entity_id]} and {source}")
        ids[entity_id] = source
        if require_current_ids and str(record["current_id"]) != entity_id:
            raise MigrationError(
                f"{source}: current id {record['current_id']!r} does not match canonical {entity_id!r}"
            )
        if record["role"] == "trunk":
            if record["parent"]:
                raise MigrationError(f"{source}: trunk must not have parent")
            continue

        collection = str(record["collection"])
        parent = str(record["parent"])
        form_id = str(record["form_id"])
        if parent not in roots:
            raise MigrationError(f"{source}: parent {parent!r} is not a discovered trunk")
        if not entity_id.startswith(collection + "/"):
            raise MigrationError(f"{source}: entity ID is outside collection namespace: {entity_id}")
        if not ID_PATTERN.fullmatch(form_id) or not re.search(r"(?:^|-)[0-9]{4}(?:-|$)", form_id):
            raise MigrationError(f"{source}: form ID must contain a four-digit numeric segment: {form_id}")


def public_record(record: dict[str, str | None]) -> dict[str, str | None]:
    return {key: record[key] for key in (
        "source", "legacy_id", "id", "form_id", "collection", "parent", "title", "role"
    )}


def write_map(path: Path, records: list[dict[str, str | None]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(public_record(record), ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("content"))
    parser.add_argument("--map", dest="map_path", type=Path, default=Path("metadata/id-map.jsonl"))
    parser.add_argument("--write", action="store_true", help="rewrite satellite IDs and write the migration map")
    args = parser.parse_args()

    try:
        legacy_by_source: dict[str, str] = {}
        if args.map_path.exists():
            for line in args.map_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    legacy_by_source[str(item["source"])] = str(item["legacy_id"])

        records = build_records(args.root, legacy_by_source)
        if args.write:
            validate_records(records)
            write_map(args.map_path, records)
            print(f"normalized {len(records)} pages; wrote {args.map_path}")
        else:
            validate_records(records, require_current_ids=True)
            print(f"validated {len(records)} pages; no files changed")
    except (OSError, UnicodeError, MigrationError) as error:
        print(f"TED IDs: error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
