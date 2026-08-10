#!/usr/bin/env python3
"""Normalize and validate Thermal Extraction Devices form-based entity IDs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path


DEFAULT_PREFIX = {
    "affected-products": "TAFP",
    "botanicals": "TBOT",
    "cannabinoids": "TCBN",
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
    "cannabinoids": ("TCBN",),
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


def _canonical_json(data: dict) -> str:
    """Return the serialization used by state-map integrity digests."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _policy_root(policy_path: Path) -> Path:
    """Return the repository root represented by an id-policy path."""
    policy_path = Path(policy_path)
    if policy_path.parent.name == "metadata":
        return policy_path.parent.parent
    return policy_path.parent


def configured_state_maps(policy_path: Path) -> list[Path]:
    """Resolve state-map paths declared by the global identity policy."""
    try:
        policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MigrationError(f"could not read ID policy {policy_path}: {error}") from error

    root = _policy_root(Path(policy_path))
    paths: list[Path] = []
    for raw_path in policy.get("state_maps", []):
        path = Path(str(raw_path))
        paths.append(path if path.is_absolute() else root / path)
    for raw_pattern in policy.get("state_map_globs", []):
        pattern = Path(str(raw_pattern))
        if pattern.is_absolute():
            paths.extend(sorted(pattern.parent.glob(pattern.name)))
        else:
            paths.extend(sorted(root.glob(str(pattern))))

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def _state_map_claims(paths: list[Path]) -> list[tuple[Path, dict[str, str]]]:
    """Load and validate state-map claims without consulting current content."""
    claims: list[tuple[Path, dict[str, str]]] = []
    claimed_ids: dict[str, tuple[Path, str, str]] = {}
    claimed_keys: dict[tuple[str, str], tuple[Path, str]] = {}

    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise MigrationError(f"could not read state ID map {path}: {error}") from error
        if not isinstance(data, dict) or not isinstance(data.get("mappings"), list):
            raise MigrationError(f"{path}: state ID map must contain a mappings list")

        stored_digest = data.get("digest")
        if stored_digest:
            probe = {key: value for key, value in data.items() if key != "digest"}
            expected_digest = hashlib.sha256(
                _canonical_json(probe).encode("utf-8")
            ).hexdigest()
            if expected_digest != stored_digest:
                raise MigrationError(
                    f"{path}: state ID map integrity digest mismatch"
                )

        for index, raw_item in enumerate(data["mappings"]):
            if not isinstance(raw_item, dict):
                raise MigrationError(f"{path}: mapping {index} is not an object")
            entity_type = str(raw_item.get("entity_type", ""))
            natural_key = str(raw_item.get("natural_key", ""))
            entity_id = str(raw_item.get("entity_id", ""))
            collection = str(raw_item.get("collection", ""))
            if not entity_type or not natural_key or not entity_id:
                raise MigrationError(
                    f"{path}: mapping {index} must include entity_type, natural_key, and entity_id"
                )

            parts = entity_id.split("/", 1)
            if len(parts) != 2:
                raise MigrationError(f"{path}: malformed canonical ID {entity_id!r}")
            id_collection, form_id = parts
            if collection and collection != id_collection:
                raise MigrationError(
                    f"{path}: {entity_id!r} disagrees with collection {collection!r}"
                )
            collection = id_collection
            prefixes = FORM_PREFIXES.get(collection)
            if not prefixes:
                raise MigrationError(
                    f"{path}: state map uses unregistered collection {collection!r}"
                )
            if (
                not ID_PATTERN.fullmatch(form_id)
                or not re.search(r"(?:^|-)[0-9]{4}(?:-|$)", form_id)
                or not any(form_id == prefix or form_id.startswith(prefix + "-")
                           for prefix in prefixes)
            ):
                raise MigrationError(
                    f"{path}: state map ID {entity_id!r} does not match the global collection prefix"
                )

            key = (entity_type, natural_key)
            prior_key = claimed_keys.get(key)
            if prior_key is not None:
                prior_path, prior_id = prior_key
                raise MigrationError(
                    f"state natural key {key!r} is claimed by both {prior_path} ({prior_id}) "
                    f"and {path} ({entity_id})"
                )
            claimed_keys[key] = (path, entity_id)

            prior_claim = claimed_ids.get(entity_id)
            if prior_claim is not None:
                prior_path, prior_type, prior_natural_key = prior_claim
                raise MigrationError(
                    f"state ID collision {entity_id!r}: {prior_path} maps "
                    f"{prior_type}:{prior_natural_key!r}, {path} maps "
                    f"{entity_type}:{natural_key!r}"
                )
            claimed_ids[entity_id] = (path, entity_type, natural_key)
            claims.append((path, {
                "entity_type": entity_type,
                "natural_key": natural_key,
                "entity_id": entity_id,
                "collection": collection,
            }))
    return claims


def state_map_reservations(paths: list[Path]) -> dict[str, set[str]]:
    """Return canonical form IDs claimed by state maps, grouped by collection."""
    reservations: dict[str, set[str]] = {}
    for _path, item in _state_map_claims(paths):
        collection, form_id = item["entity_id"].split("/", 1)
        reservations.setdefault(collection, set()).add(form_id)
    return reservations


def validate_state_maps(paths: list[Path]) -> None:
    """Fail closed when state maps claim a canonical ID more than once.

    State maps may retain historical reservations whose page is no longer in
    the current content tree, so this check intentionally does not require
    every state-map ID to have a current Markdown page. The global allocator
    still treats every such ID as reserved.
    """
    # Historical state reservations are valid even when their page is no
    # longer present in the current tree.
    _state_map_claims(paths)


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


def allocate_form_id(
    collection: str,
    used: set[str],
    reserved: set[str] | None = None,
) -> str:
    prefix = DEFAULT_PREFIX.get(collection, "TED")
    reserved = reserved or set()
    for number in range(1, 10000):
        candidate = f"{prefix}-{number:04d}"
        if candidate not in used and candidate not in reserved:
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


def build_records(
    root: Path,
    legacy_by_source: dict[str, str] | None = None,
    reserved_form_ids: dict[str, set[str]] | None = None,
) -> list[dict[str, str | None]]:
    records: list[dict[str, str | None]] = []
    used_by_collection: dict[str, set[str]] = {}
    pending: list[dict[str, str | None]] = []
    reserved_form_ids = reserved_form_ids or {}

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
            current_entity_id = str(current_id or "")
            if candidate in used:
                raise MigrationError(f"{path}: form ID collision in {collection}: {candidate}")
            if candidate in reserved_form_ids.get(collection, set()) and current_entity_id != f"{collection}/{candidate}":
                raise MigrationError(
                    f"{path}: form ID {collection}/{candidate} is reserved by a state ID map"
                )
            used.add(candidate)
            record["id"] = f"{collection}/{candidate}"
            records.append(record)

    # Preserve existing canonical IDs (id-policy immutability): a pending
    # satellite whose current entity ID is already a valid form ID in this
    # collection keeps it (the map's legacy_id is the *prior* identity, not the
    # canonical one). Reservation happens in a first pass over ALL pending
    # records so that a newly allocated ID can never steal a number that an
    # existing satellite already holds (which would renumber it), regardless
    # of file sort order.
    reserved_forms: dict[str, dict[str, str]] = {}  # collection -> form -> source
    for record in sorted(pending, key=lambda item: str(item["source"])):
        collection = str(record["collection"])
        used = used_by_collection.setdefault(collection, set())
        existing = str(record["current_id"] or "")
        if existing.startswith(collection + "/"):
            existing_form = existing[len(collection) + 1:]
            if (
                ID_PATTERN.fullmatch(existing_form)
                and re.search(r"(?:^|-)[0-9]{4}(?:-|$)", existing_form)
            ):
                if existing_form in used:
                    raise MigrationError(
                        f"{record['source']}: existing canonical ID collision in {collection}: {existing_form}"
                    )
                used.add(existing_form)
                reserved_forms.setdefault(collection, {})[existing_form] = str(record["source"])

    for record in sorted(pending, key=lambda item: str(item["source"])):
        collection = str(record["collection"])
        used = used_by_collection.setdefault(collection, set())
        existing = str(record["current_id"] or "")
        kept_form = None
        if existing.startswith(collection + "/"):
            candidate_form = existing[len(collection) + 1:]
            if (
                ID_PATTERN.fullmatch(candidate_form)
                and re.search(r"(?:^|-)[0-9]{4}(?:-|$)", candidate_form)
                and reserved_forms.get(collection, {}).get(candidate_form) == str(record["source"])
            ):
                kept_form = candidate_form
        if kept_form is not None:
            record["form_id"] = kept_form
            record["id"] = f"{collection}/{kept_form}"
            records.append(record)
            continue
        candidate = allocate_form_id(
            collection,
            used,
            reserved_form_ids.get(collection, set()),
        )
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
    parser.add_argument(
        "--policy", dest="policy_path", type=Path,
        default=Path("metadata/id-policy.json"),
        help="global ID policy used to resolve --all-state-maps",
    )
    parser.add_argument(
        "--state-map", dest="state_maps", action="append", type=Path, default=[],
        help="state natural-key map to validate and reserve (repeatable)",
    )
    parser.add_argument(
        "--all-state-maps", action="store_true",
        help="validate and reserve every state map declared by the ID policy",
    )
    parser.add_argument("--write", action="store_true", help="rewrite satellite IDs and write the migration map")
    args = parser.parse_args()

    try:
        state_map_paths = list(args.state_maps)
        if args.all_state_maps:
            state_map_paths.extend(configured_state_maps(args.policy_path))
        unique_state_map_paths: list[Path] = []
        seen_state_map_paths: set[Path] = set()
        for path in state_map_paths:
            resolved = path.resolve()
            if resolved not in seen_state_map_paths:
                seen_state_map_paths.add(resolved)
                unique_state_map_paths.append(resolved)
        state_map_paths = unique_state_map_paths

        reserved_form_ids = state_map_reservations(state_map_paths) if state_map_paths else {}
        legacy_by_source: dict[str, str] = {}
        if args.map_path.exists():
            for line in args.map_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    legacy_by_source[str(item["source"])] = str(item["legacy_id"])

        records = build_records(args.root, legacy_by_source, reserved_form_ids)
        if state_map_paths:
            validate_state_maps(state_map_paths)
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
