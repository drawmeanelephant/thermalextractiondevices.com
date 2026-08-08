"""Normalized cultivar batch analyte profiles.

Minimal primitives for the cultivar/chemotype graph model (see
docs/graph/cultivar-chemotype-model.md). This module deliberately does NOT
build an analysis engine; it provides the unit-of-truth representation,
censoring discipline, and validation needed before any batch data lands.

Key rules enforced here:

* ``censoring`` is mandatory and one of: numeric, nd, below_lod, below_loq,
  not_tested.
* A numeric ``value`` is required if and only if ``censoring == numeric``.
* Missing/censored values are NEVER silently imputed as zero. Any function
  that needs a zero-substitution requires an explicit ``zero_strategy``.
* No scientific thresholds are hard-coded anywhere in this module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional


class Censoring(str, Enum):
    NUMERIC = "numeric"
    ND = "nd"
    BELOW_LOD = "below_lod"
    BELOW_LOQ = "below_loq"
    NOT_TESTED = "not_tested"


class Basis(str, Enum):
    DRY_WEIGHT = "dry-weight"
    AS_RECEIVED = "as-received"
    UNKNOWN = "unknown"


class DecarbConvention(str, Enum):
    NATIVE = "native"
    TOTAL_POTENTIAL = "total-potential"
    NOT_APPLICABLE = "not-applicable"
    UNKNOWN = "unknown"


class RecordKind(str, Enum):
    VERIFIED = "verified"
    DEMONSTRATION = "demonstration"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class AnalyteMeasurement:
    """One compound measurement in one batch.

    ``value`` is required (and numeric) iff ``censoring == numeric``.
    ``lod`` is required iff ``censoring == below_lod``; ``loq`` iff
    ``censoring == below_loq``.
    """

    compound_id: str
    compound_name: str
    unit: str
    censoring: Censoring
    method: str
    value: Optional[float] = None
    lod: Optional[float] = None
    loq: Optional[float] = None
    quantitation_note: Optional[str] = None

    def __post_init__(self) -> None:
        problems = measurement_problems(self)
        if problems:
            raise ValueError("; ".join(problems))


def measurement_problems(m: AnalyteMeasurement) -> list[str]:
    """Hard contract violations that make a measurement unusable (raise on build)."""
    problems: list[str] = []
    if m.censoring == Censoring.NUMERIC:
        if m.value is None:
            problems.append("numeric measurement requires a value")
        elif not math.isfinite(m.value):
            problems.append("numeric measurement value must be finite")
    else:
        if m.value is not None:
            problems.append(f"censoring={m.censoring.value} must not carry a value")
    if m.censoring == Censoring.BELOW_LOD and m.lod is None:
        problems.append("below_lod requires an lod")
    if m.censoring == Censoring.BELOW_LOQ and m.loq is None:
        problems.append("below_loq requires an loq")
    return problems


def validate_measurement(m: AnalyteMeasurement) -> list[str]:
    """Return ALL validation issues for one measurement: hard problems plus
    soft warnings (e.g. ``nd`` without an ``lod``, which is common on real
    COAs). Hard problems raise at construction; soft warnings are surfaced
    here and by ``validate_profile``."""
    problems = measurement_problems(m)
    if m.censoring == Censoring.ND and m.lod is None:
        problems.append("nd should carry an lod so detection capability is recorded")
    return problems


@dataclass(frozen=True)
class BatchProfile:
    """Normalized unit of truth for one batch's laboratory measurements."""

    batch_id: str
    lab_report_id: str
    producer_id: str
    product_id: str
    cultivar_labels: tuple[str, ...]
    sample_type: str
    basis: Basis
    decarb_convention: DecarbConvention
    record_kind: RecordKind
    analytes: tuple[AnalyteMeasurement, ...]
    jurisdiction: Optional[str] = None
    harvest_date: Optional[str] = None
    report_date: Optional[str] = None

    def __post_init__(self) -> None:
        problems = validate_profile(self)
        if problems:
            raise ValueError("; ".join(problems))


def validate_profile(p: BatchProfile) -> list[str]:
    """Return a list of validation problems for a batch profile (empty = valid)."""
    problems: list[str] = []
    if not p.batch_id:
        problems.append("batch_id is required")
    if not p.cultivar_labels:
        problems.append("at least one cultivar label is required")
    if not p.analytes:
        problems.append("at least one analyte measurement is required")
    units = {m.unit for m in p.analytes}
    if len(units) > 1:
        problems.append(f"mixed units within a batch are not comparable: {sorted(units)}")
    seen: set[str] = set()
    for m in p.analytes:
        problems.extend(validate_measurement(m))
        if m.compound_id in seen:
            problems.append(f"duplicate analyte measurement for {m.compound_id}")
        seen.add(m.compound_id)
    return problems


def censorship_summary(p: BatchProfile) -> dict[str, int]:
    """Count measurements per censoring state for a batch profile."""
    counts = {state.value: 0 for state in Censoring}
    for m in p.analytes:
        counts[m.censoring.value] += 1
    return counts


def reporting_rate(p: BatchProfile) -> Optional[float]:
    """Fraction of tested analytes that were fully quantified, or None if none tested."""
    tested = [m for m in p.analytes if m.censoring != Censoring.NOT_TESTED]
    if not tested:
        return None
    quantified = sum(1 for m in tested if m.censoring == Censoring.NUMERIC)
    return quantified / len(tested)


def numeric_value(m: AnalyteMeasurement) -> Optional[float]:
    """Return the numeric value only for fully quantified measurements.

    Censored measurements (nd / below_lod / below_loq) return None. This
    function never imputes; callers that require substitution must request an
    explicit strategy via ``substitute_zeros``.
    """
    if m.censoring == Censoring.NUMERIC:
        return m.value
    return None


_ZERO_STRATEGY_PREFIX = "multiplicative_replacement_"


def substitute_zeros(
    measurements: Iterable[AnalyteMeasurement],
    zero_strategy: str,
) -> list[float]:
    """Map measurements to numeric values with an EXPLICIT zero strategy.

    ``zero_strategy`` must be ``"multiplicative_replacement_<delta>"``
    (delta in (0, 1)), which replaces censored/undetected values with
    ``delta * (smallest positive quantified value)`` and renormalizes —
    the standard Aitchison-style multiplicative replacement. Any other value
    raises, so no implicit imputation is possible.

    ``not_tested`` measurements are dropped (they carry no information), and
    the caller sees exactly which rows were substituted via the returned
    ``(values, substituted_indices)``? No — keep the API minimal: this
    function returns values only; use ``censorship_summary`` for the counts.
    """
    measurements = list(measurements)
    if not zero_strategy.startswith(_ZERO_STRATEGY_PREFIX):
        raise ValueError(
            "no implicit zero-substitution: pass an explicit zero_strategy, "
            "e.g. 'multiplicative_replacement_0.65'"
        )
    try:
        delta = float(zero_strategy[len(_ZERO_STRATEGY_PREFIX):])
    except ValueError:
        raise ValueError(f"invalid zero_strategy: {zero_strategy!r}") from None
    if not 0.0 < delta < 1.0:
        raise ValueError("delta must be in (0, 1)")

    quantified = [m.value for m in measurements if m.censoring == Censoring.NUMERIC and m.value]
    if not quantified:
        raise ValueError("no fully quantified values to anchor replacement")
    detection_floor = delta * min(quantified)

    out: list[float] = []
    for m in measurements:
        if m.censoring == Censoring.NOT_TESTED:
            continue
        if m.censoring == Censoring.NUMERIC:
            out.append(float(m.value))  # type: ignore[arg-type]
        else:
            out.append(detection_floor)
    return out


def clr_transform(values: list[float]) -> list[float]:
    """Centered log-ratio transform of strictly positive values.

    Raises on non-positive values: zero/negative handling must be decided
    upstream via an explicit zero strategy, never silently here.
    """
    if not values:
        return []
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError("CLR requires strictly positive values; apply an explicit zero strategy first")
    total = sum(values)
    geometric_mean = math.exp(sum(math.log(v) for v in values) / len(values))
    return [math.log(v / geometric_mean) for v in values]


def aitchison_distance(a: list[float], b: list[float]) -> float:
    """Aitchison distance between two positive composition vectors (same length)."""
    if len(a) != len(b):
        raise ValueError("composition vectors must have equal length")
    ca = clr_transform(a)
    cb = clr_transform(b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(ca, cb)))


def profile_matrix(
    profiles: Iterable[BatchProfile],
    compounds: Iterable[str],
) -> tuple[list[BatchProfile], dict[str, dict[str, Optional[float]]]]:
    """Build a batch × compound matrix of fully quantified values.

    Censored values appear as None (never 0). Rows are batch_ids, columns are
    compound_ids in the order given. ``not_tested`` and censored entries are
    None, and callers must apply an explicit zero strategy before any
    compositional transform.
    """
    rows: list[BatchProfile] = []
    matrix: dict[str, dict[str, Optional[float]]] = {}
    for profile in profiles:
        if profile.record_kind == RecordKind.DEMONSTRATION:
            continue  # demonstration/placeholder records are never analysis data
        rows.append(profile)
        by_id = {m.compound_id: m for m in profile.analytes}
        row: dict[str, Optional[float]] = {}
        for cid in compounds:
            m = by_id.get(cid)
            row[cid] = numeric_value(m) if m else None
        matrix[profile.batch_id] = row
    return rows, matrix
