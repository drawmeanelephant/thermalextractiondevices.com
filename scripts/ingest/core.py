"""Core primitives shared across the ingestion pipeline.

Everything in this module is regulator-agnostic.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class IngestError(Exception):
    """Base class for all ingestion failures."""


class ContentTypeError(IngestError):
    """An endpoint returned unexpected content (e.g. HTML for a CSV URL)."""


class SchemaDriftError(IngestError):
    """Required columns disappeared or column types changed unexpectedly."""


class RowCollapseError(IngestError):
    """Row count collapsed beyond the configured threshold."""


class DateRegressionError(IngestError):
    """Reported dates moved backward without a recognized source correction."""


class EmptyOutputError(IngestError):
    """Normalized output was empty when a non-empty result was required."""


class DuplicateKeyError(IngestError):
    """Primary keys were duplicated in a normalized dataset."""


class IdCollisionError(IngestError):
    """Two natural keys resolved to the same entity ID."""


class IdMappingChangedError(IngestError):
    """A persisted natural-key mapping changed unexpectedly."""


class PrivacyViolationError(IngestError):
    """Excluded fields or sensitive values appeared in generated Markdown."""


class ValidationError(IngestError):
    """Boris graph, link, or publication validation failed."""


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

DATE_FORMATS = (
    "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S", "%Y%m%d", "%d-%b-%y", "%b %d, %Y",
    "%B %d, %Y", "%Y/%m/%d",
)


def parse_date(value: Any) -> Optional[_dt.date]:
    """Parse a source date string into a ``datetime.date``.

    Returns ``None`` when the value is empty or unparseable; callers decide
    whether that is acceptable.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    # ISO timestamps with fractional seconds / T separator
    if "T" in text:
        text = text.split("T", 1)[0]
    text = text.replace("/", "-")
    try:
        return _dt.date.fromisoformat(text)
    except ValueError:
        pass
    for fmt in DATE_FORMATS:
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # Fall back to natural language "Month Day, Year"
    match = re.match(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", text)
    if match:
        month = _MONTHS.get(match.group(1).lower())
        if month:
            try:
                return _dt.date(int(match.group(3)), month, int(match.group(2)))
            except ValueError:
                return None
    return None


def parse_date_range(text: str) -> Optional[tuple[_dt.date, _dt.date]]:
    """Parse a human range such as ``May 31, 2024 and January 23, 2025``.

    Accepts ``X and Y``, ``X through Y``, ``X - Y``, ``X to Y`` separators.
    Returns ``(start, end)`` or ``None``.
    """
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip()
    separators = (r"\s+and\s+", r"\s+through\s+", r"\s+to\s+", r"\s*-\s*", r"\s*–\s*")
    for sep in separators:
        parts = re.split(sep, cleaned, maxsplit=1)
        if len(parts) == 2:
            start = parse_date(parts[0])
            end = parse_date(parts[1])
            if start and end:
                return (start, end)
    return None


def parse_month(value: Any) -> Optional[tuple[int, int]]:
    """Parse a ``YYYY-MM`` value into ``(year, month)``."""
    if value is None:
        return None
    text = str(value).strip()
    match = re.fullmatch(r"(\d{4})[-/](\d{1,2})", text)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Change reporting
# ---------------------------------------------------------------------------


@dataclass
class ChangeReport:
    """Human-readable, machine-serializable record of one sync run."""

    state: str
    run_id: str
    started_at: str
    completed_at: Optional[str] = None
    datasets: dict = field(default_factory=dict)          # slug -> DatasetRun
    pages_generated: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "datasets": self.datasets,
            "pages_generated": self.pages_generated,
            "warnings": self.warnings,
            "errors": self.errors,
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Sync Report: {self.state}",
            "",
            f"- Run ID: `{self.run_id}`",
            f"- Started: {self.started_at}",
            f"- Completed: {self.completed_at or 'incomplete'}",
            "",
            "## Datasets",
            "",
            "| Dataset | Status | Rows | Raw SHA-256 | Change |",
            "| --- | --- | ---: | --- | --- |",
        ]
        for slug, run in sorted(self.datasets.items()):
            lines.append(
                f"| {slug} | {run.get('status', 'unknown')} | "
                f"{run.get('row_count', '-')} | "
                f"{_short_sha(run.get('raw_sha256'))} | "
                f"{run.get('change', 'no change')} |"
            )
        if self.warnings:
            lines += ["", "## Warnings", ""]
            lines += [f"- ⚠️ {w}" for w in self.warnings]
        if self.errors:
            lines += ["", "## Errors", ""]
            lines += [f"- ❌ {e}" for e in self.errors]
        if self.pages_generated:
            lines += ["", "## Pages Generated", ""]
            lines += [f"- {p}" for p in sorted(self.pages_generated)]
        lines.append("")
        return "\n".join(lines)


def _short_sha(sha: Optional[str]) -> str:
    if not sha:
        return "-"
    return sha[:12]


@dataclass
class DatasetRun:
    """Outcome record for one dataset during a sync."""

    slug: str
    status: str = "skipped"            # fetched | unchanged | error
    row_count: Optional[int] = None
    raw_sha256: Optional[str] = None
    normalized_sha256: Optional[str] = None
    change: str = "no change"
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "status": self.status,
            "row_count": self.row_count,
            "raw_sha256": self.raw_sha256,
            "normalized_sha256": self.normalized_sha256,
            "change": self.change,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------


def read_json(path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data, indent=2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=indent, ensure_ascii=False)
        handle.write("\n")


def iter_records(rows: Iterable[dict]) -> Iterable[dict]:
    """Normalize CSV row values: strip whitespace, empty-string -> None."""
    for row in rows:
        out = {}
        for key, value in row.items():
            if value is None:
                out[key] = value
                continue
            text = str(value).strip()
            out[key] = text if text else None
        yield out


def summarize_counts(counter, limit: int = 12) -> str:
    """Render a Counter as ``"A: 10, B: 4, ..."`` for report prose."""
    return ", ".join(f"{k}: {v}" for k, v in counter.most_common(limit)) or "none"
