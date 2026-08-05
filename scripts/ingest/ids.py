"""Stable mapping from source natural keys to Boris entity IDs.

A :class:`NaturalKeyRegistry` persists ``(entity_type, natural_key) ->
Boris entity ID`` in ``data/<state>-ccc/id-map.json``. IDs are allocated
deterministically from the collection prefix, and reused across runs.

Guards:

* IDs never collide across entity types.
* A persisted mapping that changed unexpectedly raises
  :class:`IdMappingChangedError` (tamper / drift detection).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Optional

from .core import IdCollisionError, IdMappingChangedError, write_json

_NUMERIC_SEGMENT = re.compile(r"-(\d{4})$")


def _canonical(data: dict) -> str:
    """Deterministic serialization used for the integrity digest."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class NaturalKeyRegistry:
    """Allocates and persists stable Boris IDs for source natural keys."""

    def __init__(
        self,
        path: Path,
        prefixes: dict,
        collections: dict,
    ):
        """
        Args:
            path: durable ``id-map.json`` location.
            prefixes: entity_type -> form prefix (e.g. ``"advisory" -> "TSAD"``).
            collections: entity_type -> collection dir (e.g. ``"advisory" -> "safety-advisories"``).
        """
        self.path = Path(path)
        self.prefixes = dict(prefixes)
        self.collections = dict(collections)
        self._entries: dict[tuple[str, str], str] = {}
        self._labels: dict[tuple[str, str], str] = {}
        self._allocated: dict[str, int] = {}
        if self.path.is_file():
            self._load()

    # ------------------------------------------------------------------ load
    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        stored_digest = data.get("digest")
        if stored_digest:
            probe = {k: v for k, v in data.items() if k != "digest"}
            if hashlib.sha256(_canonical(probe).encode("utf-8")).hexdigest() != stored_digest:
                raise IdMappingChangedError(
                    "persisted id-map integrity digest mismatch "
                    "(file edited outside the importer or corrupted)"
                )
        for item in data.get("mappings", []):
            entity_type = item.get("entity_type")
            natural_key = item.get("natural_key")
            entity_id = item.get("entity_id", "")
            collection = item.get("collection")
            key = (entity_type, natural_key)
            previous = self._entries.get(key)
            if previous is not None and previous != entity_id:
                raise IdMappingChangedError(
                    f"persisted mapping for {key} changed {previous} -> {entity_id}"
                )
            # Tamper/drift guard: the persisted ID must match the registered
            # prefix and collection scheme for its entity type.
            expected = self._expected_id(entity_type, entity_id)
            if expected is None:
                raise IdMappingChangedError(
                    f"persisted mapping for {key} uses unexpected ID {entity_id!r} "
                    f"(expected collection/prefix pattern for {entity_type!r})"
                )
            if collection and self.collections.get(entity_type) != collection:
                raise IdMappingChangedError(
                    f"persisted mapping for {key} has unexpected collection {collection!r}"
                )
            self._entries[key] = expected
            self._labels[key] = item.get("label", "")
            number = _parse_number(expected)
            if number is not None:
                self._allocated[entity_type] = max(
                    self._allocated.get(entity_type, 0), number
                )

    def _expected_id(self, entity_type: str, entity_id: str) -> Optional[str]:
        """Return the canonical full entity ID if ``entity_id`` matches the scheme."""
        prefix = self.prefixes.get(entity_type)
        collection = self.collections.get(entity_type)
        if not prefix or not collection:
            return None
        number = _parse_number(entity_id)
        if number is None:
            return None
        expected_form = f"{prefix}-{number:04d}"
        if entity_id == expected_form:
            return f"{collection}/{expected_form}"
        if entity_id == f"{collection}/{expected_form}":
            return entity_id
        return None

    # ------------------------------------------------------------- allocation
    def id_for(self, entity_type: str, natural_key: str, *, label: str = "") -> str:
        """Return the stable full entity ID for a natural key, allocating if new.

        Entity IDs use the Boris form ``<collection>/<PREFIX>-NNNN``.
        """
        prefix = self.prefixes.get(entity_type)
        collection = self.collections.get(entity_type)
        if not prefix or not collection:
            raise KeyError(f"no prefix registered for entity type {entity_type!r}")
        key = (entity_type, str(natural_key))
        if key in self._entries:
            return self._entries[key]
        number = self._allocated.get(entity_type, 0) + 1
        self._allocated[entity_type] = number
        entity_id = f"{collection}/{prefix}-{number:04d}"
        if self._collides(entity_type, entity_id):
            raise IdCollisionError(f"allocated ID {entity_id} collides with an existing entity")
        self._entries[key] = entity_id
        self._labels[key] = label
        return entity_id

    def _collides(self, entity_type: str, entity_id: str) -> bool:
        for (other_type, _), other_id in self._entries.items():
            if other_type == entity_type and other_id == entity_id:
                return True
        return False

    # ----------------------------------------------------------------- save
    def save(self) -> None:
        mappings = []
        for (entity_type, natural_key), entity_id in sorted(self._entries.items()):
            mappings.append({
                "entity_type": entity_type,
                "natural_key": natural_key,
                "entity_id": entity_id,
                "label": self._labels.get((entity_type, natural_key), ""),
                "collection": self.collections.get(entity_type),
            })
        payload = {"version": 1, "state": None, "mappings": mappings}
        payload["digest"] = hashlib.sha256(
            _canonical(payload).encode("utf-8")
        ).hexdigest()
        write_json(self.path, payload)

    # ------------------------------------------------------------------ query
    def entity_id(self, entity_type: str, natural_key: str) -> Optional[str]:
        return self._entries.get((entity_type, str(natural_key)))

    def all_ids(self) -> set[str]:
        return set(self._entries.values())

    def label_for(self, entity_type: str, natural_key: str) -> str:
        return self._labels.get((entity_type, str(natural_key)), "")


def _parse_number(entity_id: str) -> Optional[int]:
    match = _NUMERIC_SEGMENT.search(entity_id)
    return int(match.group(1)) if match else None
