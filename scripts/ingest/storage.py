"""Storage abstraction for raw snapshots, normalized artifacts, and manifests.

Policy (per the Massachusetts task):

* Large raw and normalized files live under a git-ignored working directory
  (``var/ingest/<state>-ccc/`` by default, overridable with ``--artifacts-dir``).
* Only small durable records are committed: ``data/<state>-ccc/manifest.json``,
  ``source-catalog.json``, ``schema-report.md``, ``sync-reports/``, ``id-map.json``.
* Raw snapshots are immutable: a new checksum always produces a new path, and
  the manifest never overwrites the only earlier snapshot record.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .core import IngestError, utc_now, write_json

MANIFEST_VERSION = 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class ArtifactStore:
    """Owns the durable committed directory and the ignored working directory."""

    state: str                            # e.g. "massachusetts"
    working_root: Path                    # var/ingest/<state>-ccc/ by default
    durable_root: Path                    # data/<state>-ccc/ by default
    importer_version: str = "state_ingest-0.1"
    schema_version: str = "1"

    # ------------------------------------------------------------------ dirs
    @property
    def raw_dir(self) -> Path:
        return self.working_root / "raw"

    @property
    def normalized_dir(self) -> Path:
        return self.working_root / "normalized"

    @property
    def reports_dir(self) -> Path:
        return self.working_root / "reports"

    @property
    def sync_reports_dir(self) -> Path:
        return self.durable_root / "sync-reports"

    @property
    def manifest_path(self) -> Path:
        return self.durable_root / "manifest.json"

    # ------------------------------------------------------------ raw snapshot
    def raw_snapshot_path(self, slug: str, sha256: str, ext: str = ".csv") -> Path:
        """Immutable snapshot path: ``raw/<slug>/<sha256><ext>``."""
        return self.raw_dir / slug / f"{sha256}{ext}"

    def portable_artifact_location(self, path: Path) -> str:
        """Return a stable, non-machine-specific artifact location.

        Durable manifests are committed and may be inspected from any
        checkout.  Never serialize the local working directory into them;
        expose the documented default artifact namespace instead.
        """
        relative = Path(path).relative_to(self.working_root)
        return (Path("var") / "ingest" / f"{self.state}-ccc" / relative).as_posix()

    def snapshot_exists(self, slug: str, sha256: str, ext: str = ".csv") -> bool:
        return self.raw_snapshot_path(slug, sha256, ext).is_file()

    def record_snapshot(
        self,
        slug: str,
        source_url: str,
        *,
        raw_sha256: str,
        raw_path: Path,
        content_type: str,
        size_bytes: int,
        retrieved_at: str,
        reporting_period: Optional[str] = None,
        source_last_updated: Optional[str] = None,
        disclaimer: Optional[str] = None,
        clarification: Optional[str] = None,
        row_count: Optional[int] = None,
        columns: Optional[list[str]] = None,
        normalized_sha256: Optional[str] = None,
        normalized_path: Optional[Path] = None,
        max_reported_date: Optional[str] = None,
    ) -> dict:
        """Append a durable manifest record for one dataset snapshot."""
        manifest = self.read_manifest()
        entries = manifest.setdefault("datasets", {}).setdefault(slug, [])
        prior = entries[-1] if entries else None
        record = {
            "slug": slug,
            "official_source_url": source_url,
            "retrieval_timestamp": retrieved_at,
            "reporting_period": reporting_period,
            "source_last_updated": source_last_updated,
            "http_content_type": content_type,
            "file_size_bytes": size_bytes,
            "raw_sha256": raw_sha256,
            "normalized_sha256": normalized_sha256,
            "row_count": row_count,
            "column_schema": columns or [],
            "importer_version": self.importer_version,
            "normalization_schema_version": self.schema_version,
            "artifact_location": self.portable_artifact_location(raw_path),
            "source_disclaimer": disclaimer,
            "source_clarification_or_correction": clarification,
            "prior_snapshot_checksum": (prior or {}).get("raw_sha256"),
            "max_reported_date": max_reported_date,
        }
        entries.append(record)
        manifest["version"] = MANIFEST_VERSION
        manifest["updated_at"] = utc_now()
        manifest["state"] = self.state
        write_json(self.manifest_path, manifest)
        return record

    def read_manifest(self) -> dict:
        if not self.manifest_path.is_file():
            return {"version": MANIFEST_VERSION, "state": self.state, "datasets": {}}
        import json

        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def latest_snapshot(self, slug: str) -> Optional[dict]:
        entries = self.read_manifest().get("datasets", {}).get(slug, [])
        return entries[-1] if entries else None

    # ------------------------------------------------------------- normalized
    def normalized_path(self, slug: str, sha256: str, ext: str = ".csv") -> Path:
        return self.normalized_dir / slug / f"{sha256}{ext}"

    def write_normalized(self, slug: str, sha256: str, rows: list[dict]) -> Path:
        """Write normalized machine records (immutable by checksum)."""
        import csv as _csv

        path = self.normalized_path(slug, sha256)
        path.parent.mkdir(parents=True, exist_ok=True)
        columns = list(rows[0].keys()) if rows else []
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = _csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        return path

    def write_report(self, filename: str, content: str) -> Path:
        self.sync_reports_dir.mkdir(parents=True, exist_ok=True)
        path = self.sync_reports_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def write_durable_json(self, filename: str, data: Any) -> Path:
        path = self.durable_root / filename
        write_json(path, data)
        return path

    def write_durable_markdown(self, filename: str, content: str) -> Path:
        path = self.durable_root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    # ---------------------------------------------------------------- helpers
    def all_snapshot_records(self) -> dict[str, list[dict]]:
        return self.read_manifest().get("datasets", {})

    def dataset_freshness(self, slug: str) -> Optional[dict]:
        latest = self.latest_snapshot(slug)
        if not latest:
            return None
        return {
            "slug": slug,
            "retrieval_timestamp": latest.get("retrieval_timestamp"),
            "raw_sha256": latest.get("raw_sha256"),
            "row_count": latest.get("row_count"),
            "reporting_period": latest.get("reporting_period"),
        }
