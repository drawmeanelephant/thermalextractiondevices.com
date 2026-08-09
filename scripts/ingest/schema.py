"""Schema validation and streaming CSV/JSON readers.

Guards implemented here:

* required columns disappear            -> :class:`SchemaDriftError`
* column types change unexpectedly      -> warnings, hard failure for numbers
* source file truncated                 -> :class:`IngestError`
* decompression/decoding fails          -> :class:`IngestError`
* normalized output empty               -> :class:`EmptyOutputError`
* primary keys duplicated               -> :class:`DuplicateKeyError`
* row count collapses beyond threshold  -> :class:`RowCollapseError`
"""

from __future__ import annotations

import csv
import datetime as _dt
import email.utils
import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from .core import (
    DateRegressionError,
    DuplicateKeyError,
    EmptyOutputError,
    IngestError,
    RowCollapseError,
    SchemaDriftError,
)

NUMBER_RE = re.compile(r"^[-+]?(\d+(\.\d*)?|\.\d+)$")


def looks_numeric(value: Any) -> bool:
    if value is None:
        return False
    return bool(NUMBER_RE.match(str(value).strip()))


@dataclass
class SchemaSpec:
    """Declared expectations for one dataset.

    ``column_types`` maps column name to ``"date" | "number" | "bool" | "text"``.
    Type checks on ``text`` columns are skipped.
    """

    name: str
    required: list[str] = field(default_factory=list)
    column_types: dict = field(default_factory=dict)
    row_collapse_threshold: float = 0.5       # fail if rows < threshold * prior
    min_rows: int = 1                         # fail if normalized output smaller
    key_columns: list[str] = field(default_factory=list)   # natural-key columns
    duplicate_key_policy: str = "fail"        # "fail" raises; "warn" reports

    def check_headers(self, headers: list[str]) -> None:
        missing = [col for col in self.required if col not in headers]
        if missing:
            raise SchemaDriftError(
                f"{self.name}: required columns disappeared: {missing}"
            )

    def check_types(self, rows: Iterable[dict]) -> list[str]:
        """Return warnings for type drift; hard-fail on numeric->non-numeric."""
        warnings: list[str] = []
        for row in rows:
            for column, kind in self.column_types.items():
                value = row.get(column)
                if value is None or value == "":
                    continue
                if kind == "number":
                    if not looks_numeric(value):
                        raise SchemaDriftError(
                            f"{self.name}: column {column!r} expected numeric, "
                            f"got {value!r}"
                        )
                elif kind == "date":
                    from .core import parse_date

                    if parse_date(value) is None:
                        warnings.append(
                            f"{self.name}: column {column!r} has unparseable date {value!r}"
                        )
                elif kind == "bool":
                    if str(value).strip().lower() not in ("true", "false", "yes", "no", "1", "0"):
                        warnings.append(
                            f"{self.name}: column {column!r} value {value!r} "
                            f"not obviously boolean"
                        )
        return warnings


def read_csv_rows(path: Path, *, limit: Optional[int] = None) -> tuple[list[str], list[dict]]:
    """Read a whole CSV (small/medium files) returning headers + rows.

    Raises :class:`IngestError` on decode failure or a truncated tail.
    """
    try:
        data = path.read_bytes()
    except OSError as error:
        raise IngestError(f"cannot read {path}: {error}") from error
    return parse_csv_bytes(data, limit=limit)


def parse_csv_bytes(data: bytes, *, limit: Optional[int] = None) -> tuple[list[str], list[dict]]:
    """Parse CSV from bytes (tolerating a UTF-8 BOM)."""
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise IngestError(f"CSV decoding failed: {error}") from error
    stream = io.StringIO(text)
    reader = csv.DictReader(stream)
    if reader.fieldnames is None:
        raise EmptyOutputError("CSV has no header row")
    headers = [h.strip() for h in reader.fieldnames if h is not None]
    if not headers:
        raise EmptyOutputError("CSV header row is empty")
    rows: list[dict] = []
    for number, raw in enumerate(reader, start=2):
        if limit is not None and len(rows) >= limit:
            break
        row = {k.strip(): v for k, v in raw.items()}
        rows.append(row)
    # Truncation guard: a payload with rows that does not terminate in a
    # newline is treated as truncated (official sources always end files with
    # a newline). A header-only payload is left for the empty-output guard.
    if rows and not (text.endswith("\n") or text.endswith("\r")):
        raise IngestError("CSV appears truncated (missing trailing newline)")
    return headers, rows


def stream_csv(path: Path, *, encoding: str = "utf-8-sig", limit: Optional[int] = None):
    """Yield normalized row dicts one at a time (large files)."""
    try:
        handle = open(path, "r", encoding=encoding, newline="")
    except OSError as error:
        raise IngestError(f"cannot open {path}: {error}") from error
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise EmptyOutputError(f"{path}: CSV has no header row")
        headers = [h.strip() for h in reader.fieldnames if h is not None]
        if not headers:
            raise EmptyOutputError(f"{path}: CSV header row is empty")
        for number, raw in enumerate(reader):
            if limit is not None and number >= limit:
                break
            row = {}
            for key, value in raw.items():
                col = key.strip() if key is not None else ""
                if value is None:
                    row[col] = None
                else:
                    text = value.strip()
                    row[col] = text if text else None
            yield row


def parse_json_bytes(data: bytes) -> list[dict]:
    """Parse a JSON array payload (tolerating a BOM)."""
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IngestError(f"JSON parsing failed: {error}") from error
    if not isinstance(payload, list):
        raise IngestError(f"expected JSON array, got {type(payload).__name__}")
    return payload


def check_duplicate_keys(
    rows: Iterable[dict], key_columns: list[str], label: str, *, policy: str = "fail"
) -> list[str]:
    """Detect duplicate natural keys.

    With ``policy="fail"`` (default) a duplicate raises
    :class:`DuplicateKeyError`. With ``policy="warn"`` the count is returned
    as a warning instead — used for large source datasets whose columns are
    not a true primary key (e.g. testing results where the same package,
    analyte, and value legitimately recur).
    """
    if not key_columns:
        return []
    seen = set()
    duplicate_keys = set()
    for row in rows:
        key = tuple(str(row.get(col, "") or "") for col in key_columns)
        if key in seen:
            duplicate_keys.add(key)
        seen.add(key)
    if not duplicate_keys:
        return []
    message = (
        f"{label}: {len(duplicate_keys)} duplicate key(s) across {key_columns} "
        f"(e.g. {next(iter(duplicate_keys))}); verify against the source — "
        "these columns are not a true primary key in the source data"
    )
    if policy == "warn":
        return [message]
    raise DuplicateKeyError(message)


def check_fully_duplicate_rows(rows: Iterable[dict], label: str) -> list[str]:
    """Fail closed when a source repeats an entire row.

    Used for large datasets whose columns are not a true primary key: partial
    duplicates are legitimate, but an exact repeat of every column indicates
    corruption or a mangled export.
    """
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(sorted((k, str(v or "")) for k, v in row.items()))
        if key in seen:
            duplicates += 1
        seen.add(key)
    if duplicates:
        raise DuplicateKeyError(
            f"{label}: {duplicates} fully duplicate row(s) in source payload"
        )
    return []


def check_row_collapse(spec: SchemaSpec, current: int, prior: Optional[int]) -> list[str]:
    """Warn/fail when the row count collapses below the configured threshold."""
    warnings: list[str] = []
    if prior is None:
        if current < spec.min_rows:
            raise EmptyOutputError(
                f"{spec.name}: normalized output empty (0 < min_rows {spec.min_rows})"
            )
        return warnings
    if current < spec.min_rows:
        raise EmptyOutputError(
            f"{spec.name}: normalized output below minimum ({current} < {spec.min_rows})"
        )
    if prior > 0 and current < prior * spec.row_collapse_threshold:
        raise RowCollapseError(
            f"{spec.name}: row count collapsed from {prior} to {current} "
            f"(threshold {spec.row_collapse_threshold:.0%})"
        )
    # A decrease above the collapse line is a non-blocking warning; exactly at
    # the threshold boundary the drop is treated as an expected source change.
    if current < prior and current > prior * spec.row_collapse_threshold:
        warnings.append(
            f"{spec.name}: row count decreased {prior} -> {current} "
            "(verify against source corrections)"
        )
    return warnings


def check_date_regression(
    prior_max: Optional[str],
    new_max: Optional[str],
    *,
    tolerance_days: int = 30,
    has_clarification: bool = False,
) -> list[str]:
    """Warn/fail when the newest reported date moves backward.

    A backward move beyond ``tolerance_days`` hard-fails unless the dataset
    carries a recognized source clarification/correction; smaller backward
    moves produce a non-blocking warning in the sync report.
    """
    warnings: list[str] = []
    if not prior_max or not new_max:
        return warnings
    try:
        prior = _dt.date.fromisoformat(prior_max)
        new = _dt.date.fromisoformat(new_max)
    except ValueError:
        return warnings
    if new < prior:
        days = (prior - new).days
        if days > tolerance_days and not has_clarification:
            raise DateRegressionError(
                f"reported dates moved backward {days} days "
                f"({prior} -> {new}) without a source clarification"
            )
        warnings.append(
            f"reported dates moved backward {days} days ({prior} -> {new})"
        )
    return warnings


def parse_http_date(value: Optional[str]) -> Optional[_dt.date]:
    """Parse an HTTP ``Last-Modified`` value (e.g. ``Fri, 10 Apr 2026 …``)."""
    if not value:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(str(value).strip())
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    return parsed.date()


def check_source_staleness(
    prior_source_updated: Optional[str],
    new_source_updated: Optional[str],
    *,
    tolerance_days: int = 30,
    has_clarification: bool = False,
) -> list[str]:
    """Guard against an older upstream copy replacing a newer verified snapshot.

    Compares the source file's own update date (e.g. HTTP ``Last-Modified``)
    with the previously accepted snapshot's recorded update date. When the
    incoming payload claims to be older than the accepted snapshot by more
    than ``tolerance_days`` the sync fails closed (so an obsolete
    pre-correction release of a corrected dataset cannot silently become the
    latest record) unless the dataset carries a recognized source
    clarification/correction notice.
    """
    warnings: list[str] = []
    prior = parse_http_date(prior_source_updated)
    new = parse_http_date(new_source_updated)
    if not prior or not new:
        return warnings
    if new < prior:
        days = (prior - new).days
        if days > tolerance_days and not has_clarification:
            raise DateRegressionError(
                f"source file date moved backward {days} days "
                f"({prior} -> {new}); refusing to replace a newer verified "
                "snapshot with an older upstream copy"
            )
        warnings.append(
            f"source file date moved backward {days} days ({prior} -> {new})"
        )
    return warnings
