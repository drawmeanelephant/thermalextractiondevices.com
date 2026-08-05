"""Source revision comparison between normalized snapshots.

Distinguishes changed status labels from changed numerical measurements so a
sync report can say *which kind* of change occurred.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .schema import looks_numeric

STATUS_LIKE = {
    "status", "license_status", "license_status_category", "testpassed",
    "commence_ops", "commence_operations", "approved_license_stage", "db", "dbe",
}


@dataclass
class DiffResult:
    """Row-level comparison between a prior and a current snapshot."""

    added: int = 0
    removed: int = 0
    changed: int = 0
    changed_status_only: int = 0
    changed_numeric: int = 0
    sample_changes: list = field(default_factory=list)
    summary: str = "no change"

    def merge(self, other: "DiffResult") -> "DiffResult":
        return DiffResult(
            added=self.added + other.added,
            removed=self.removed + other.removed,
            changed=self.changed + other.changed,
            changed_status_only=self.changed_status_only + other.changed_status_only,
            changed_numeric=self.changed_numeric + other.changed_numeric,
            sample_changes=(self.sample_changes + other.sample_changes)[:12],
        )

    def finalize(self) -> "DiffResult":
        parts = []
        if self.added:
            parts.append(f"+{self.added} rows added")
        if self.removed:
            parts.append(f"-{self.removed} rows removed")
        if self.changed:
            parts.append(f"{self.changed} rows changed "
                         f"({self.changed_status_only} status, {self.changed_numeric} numeric)")
        if not parts:
            parts.append("no change")
        self.summary = ", ".join(parts)
        return self


def _row_key(row: dict, key_columns: list[str]) -> tuple:
    if not key_columns:
        return tuple(sorted(row.items()))
    return tuple(str(row.get(col, "") or "").strip() for col in key_columns)


def compare_snapshots(
    prior_rows: list[dict],
    current_rows: list[dict],
    key_columns: list[str],
    *,
    status_columns: Optional[list[str]] = None,
    numeric_columns: Optional[list[str]] = None,
    sample_limit: int = 8,
) -> DiffResult:
    """Compare two normalized row sets by identity key and values."""
    result = DiffResult()
    status_columns = status_columns or []
    numeric_columns = numeric_columns or []

    prior_map = {_row_key(row, key_columns): row for row in prior_rows}
    current_map = {_row_key(row, key_columns): row for row in current_rows}

    for key, prior_row in prior_map.items():
        if key not in current_map:
            result.removed += 1
            continue
        current_row = current_map[key]
        diffs = _value_diffs(prior_row, current_row, status_columns, numeric_columns)
        if diffs:
            result.changed += 1
            if all(kind == "status" for _, _, _, kind in diffs):
                result.changed_status_only += 1
            if any(kind == "numeric" for _, _, _, kind in diffs):
                result.changed_numeric += 1
            if len(result.sample_changes) < sample_limit:
                result.sample_changes.append(
                    {"key": key, "diffs": diffs[:6]}
                )

    result.added = sum(1 for key in current_map if key not in prior_map)
    return result.finalize()


def _value_diffs(
    prior: dict, current: dict, status_columns: list[str], numeric_columns: list[str]
) -> list[tuple[str, object, object, str]]:
    diffs = []
    columns = set(prior.keys()) | set(current.keys())
    for column in sorted(columns):
        old = prior.get(column)
        new = current.get(column)
        if old == new:
            continue
        if str(old or "").strip() == str(new or "").strip():
            continue
        lowered = column.lower().strip()
        if column in status_columns or lowered in STATUS_LIKE:
            kind = "status"
        elif column in numeric_columns or (looks_numeric(old) and looks_numeric(new)):
            kind = "numeric"
        else:
            kind = "other"
        diffs.append((column, old, new, kind))
    return diffs


def checksum_changed(prior_sha: Optional[str], current_sha: str) -> bool:
    return prior_sha is not None and prior_sha != current_sha
