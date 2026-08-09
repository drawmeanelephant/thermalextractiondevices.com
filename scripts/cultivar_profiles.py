"""Normalized cultivar batch analyte profiles.

Minimal primitives for the cultivar/chemotype graph model (see
docs/graph/cultivar-chemotype-model.md). This module deliberately does NOT
build an analysis engine; it provides the unit-of-truth representation,
censoring discipline, and validation needed before any batch data lands.

Key rules enforced here:

* ``censoring`` is mandatory and one of: numeric, nd, below_lod, below_loq,
  not_tested.
* A numeric ``value`` is required if and only if ``censoring == numeric``.
* Missing/censored values are NEVER silently imputed as zero. Zero-replacement
  is a data-product decision and is intentionally deferred to the future
  analysis engine; no substitution routine exists in this module.
* Batch identity and report identity are distinct. ``batch_id`` is the
  producer/operator batch identifier (a natural key that stays stable across
  retests); ``lab_report_id`` is the canonical archive record for the
  laboratory report (``lab-results/TLAB-XXXX``). One batch may have retests,
  corrected reports, multiple panels, or reports from different laboratories.
* Analyte measurements carry their own units, and a batch may legitimately
  contain mixed units (e.g. % w/w cannabinoids, mg/g terpenes, ppm
  pesticides, ug/g heavy metals). Measurements are only compared or composed
  after explicit normalization into a compatible analyte subset (common unit
  and basis), never rejected wholesale because a batch spans units.
* Derived statistics include only ``record_kind == verified`` profiles;
  demonstration and unverified records are never analysis data.
* No scientific thresholds are hard-coded anywhere in this module.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
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


LAB_REPORT_ID_PATTERN = re.compile(r"^lab-results/TLAB-[0-9]{4}$")
PRODUCER_ID_PATTERN = re.compile(r"^organizations/TORG-[0-9]{4}$")
PRODUCT_ID_PATTERN = re.compile(r"^products/TPRD-[0-9]{4}$")


@dataclass(frozen=True)
class AnalyteMeasurement:
    """One compound measurement in one laboratory report.

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


def soft_measurement_warnings(m: AnalyteMeasurement) -> list[str]:
    """Non-fatal notes for one measurement (e.g. ``nd`` without an ``lod``).

    These never raise; they are surfaced by ``validate_measurement`` and
    ``profile_warnings`` so detection-capability gaps stay visible without
    blocking construction. Real COAs commonly omit LOD on ``nd`` results.
    """
    warnings: list[str] = []
    if m.censoring == Censoring.ND and m.lod is None:
        warnings.append("nd should carry an lod so detection capability is recorded")
    return warnings


def validate_measurement(m: AnalyteMeasurement) -> list[str]:
    """Return ALL validation issues for one measurement: hard problems plus
    soft warnings. Hard problems raise at construction; soft warnings are
    surfaced here and by ``profile_warnings``."""
    return measurement_problems(m) + soft_measurement_warnings(m)


@dataclass(frozen=True)
class BatchProfile:
    """Normalized unit of truth for one laboratory report of one batch.

    ``batch_id`` is the producer/operator batch identifier (a natural key that
    stays stable across retests and corrected reports); ``lab_report_id`` is
    the canonical archive record for the report (``lab-results/TLAB-XXXX``).
    The two identities are deliberately distinct: a single commercial batch
    may be covered by several reports.
    """

    batch_id: str
    lab_report_id: str
    producer_id: Optional[str]
    product_id: Optional[str]
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
    """Return HARD validation problems for a batch profile (empty = valid).

    Soft warnings (e.g. ``nd`` without an ``lod``) are deliberately NOT
    included here, so constructing a profile never fails on them; use
    ``profile_warnings`` to surface those separately. The one hard contract
    for censoring values lives on ``AnalyteMeasurement`` itself.
    """
    problems: list[str] = []
    if not p.batch_id:
        problems.append("batch_id is required")
    if not p.lab_report_id or not LAB_REPORT_ID_PATTERN.fullmatch(p.lab_report_id):
        problems.append("lab_report_id must be a canonical lab-results/TLAB-XXXX record id")
    if p.producer_id is not None and not PRODUCER_ID_PATTERN.fullmatch(p.producer_id):
        problems.append("producer_id must be a canonical organizations/TORG-XXXX id or null")
    if p.product_id is not None and not PRODUCT_ID_PATTERN.fullmatch(p.product_id):
        problems.append("product_id must be a canonical products/TPRD-XXXX id or null")
    if not p.cultivar_labels:
        problems.append("at least one cultivar label is required")
    if not p.analytes:
        problems.append("at least one analyte measurement is required")
    seen: set[str] = set()
    for m in p.analytes:
        problems.extend(measurement_problems(m))
        if m.compound_id in seen:
            problems.append(f"duplicate analyte measurement for {m.compound_id}")
        seen.add(m.compound_id)
    return problems


def profile_warnings(p: BatchProfile) -> list[str]:
    """Soft, non-fatal validation notes for a batch profile.

    Warnings never block construction; they exist so detection-capability gaps
    (e.g. ``nd`` without an ``lod``) stay visible to ingest pipelines and
    editors without contradicting the soft-warning contract.
    """
    warnings: list[str] = []
    for m in p.analytes:
        warnings.extend(soft_measurement_warnings(m))
    return warnings


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
    function never imputes; zero-replacement is a data-product decision that
    is deferred to the future analysis engine and is not implemented here.
    """
    if m.censoring == Censoring.NUMERIC:
        return m.value
    return None


def clr_transform(values: list[float]) -> list[float]:
    """Centered log-ratio transform of strictly positive values.

    Raises on non-positive values: zero/negative handling must be decided
    upstream as an explicit, documented data-product decision, never silently
    here.
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
    """Build a report × compound matrix of fully quantified values.

    Censored values appear as None (never 0). Rows are ``lab_report_id``s —
    one row per laboratory report, so retests/corrected reports of the same
    batch appear as separate rows sharing a ``batch_id`` — and columns are
    compound_ids in the order given. Only ``record_kind == verified`` profiles
    are included: demonstration and unverified records are never analysis
    data. Censored entries are None, and callers must apply an explicit zero
    strategy before any compositional transform.
    """
    rows: list[BatchProfile] = []
    matrix: dict[str, dict[str, Optional[float]]] = {}
    for profile in profiles:
        if profile.record_kind != RecordKind.VERIFIED:
            continue  # only verified COAs are analysis data
        rows.append(profile)
        by_id = {m.compound_id: m for m in profile.analytes}
        row: dict[str, Optional[float]] = {}
        for cid in compounds:
            m = by_id.get(cid)
            row[cid] = numeric_value(m) if m else None
        matrix[profile.lab_report_id] = row
    return rows, matrix
