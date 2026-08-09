"""Durable batch and laboratory measurement model (COA layer).

This module is the durable data model for laboratory reports and analyte
measurements: producer -> product -> batch/lot/package -> laboratory ->
report -> analyte measurements (see docs/graph/coa-lab-data-model.md). It is
the measurement-level extension of the cultivar batch-profile model
(``scripts/cultivar_profiles.py``); batch profiles remain the derived
normalized representation for cultivar chemistry, while this module owns the
archive-facing record: the report document, its batch, and every analyte
measurement with full censoring, unit, method, and comparability metadata.

Key rules enforced here:

* **Result states are never collapsed.** ``nd`` (not detected), ``below_lod``,
  ``below_loq``, ``zero`` (explicit zero, flagged for review), ``missing``
  (blank), ``not_tested`` (absent from the panel), and ``invalid`` (present but
  unparseable, preserved verbatim) are seven distinct states with distinct
  allowed uses. A ``0.0`` printed by a laboratory is recorded as ``zero``,
  never silently converted to ``nd`` or ``missing``.
* **Reported values are preserved verbatim.** ``reported_value`` /
  ``reported_unit`` keep the exact printed string and unit; ``value`` / ``unit``
  carry the normalized representation. Nothing is rounded during ingestion;
  rounding happens only at display time via ``round_to_sigfigs``.
* **Conversions are audited.** Every unit or basis conversion produces a
  ``ConversionAudit`` (formula, parameters, added uncertainty). Mass/volume
  conversions require a verified density; dry-weight <-> as-received requires
  a moisture fraction. Conversions never happen silently.
* **Batch identity and report identity are distinct.** ``batch_id`` is the
  producer/operator batch identifier (stable across retests); ``report_id`` is
  the archive record (``lab-results/TLAB-XXXX``). One batch may have retests,
  corrected reports, multiple panels, or reports from different laboratories.
* **Cultivar claims are claims, not measurements.** ``CultivarClaim`` records
  the printed label plus an explicit ``resolution`` (resolved / tentative /
  ambiguous / unresolved) and an optional canonical ``cultivars/TCUL-XXXX``
  target. Resolution is never forced: an unknown label stays unresolved with
  ``cultivar_id = None``, and chemistry is never attached to a cultivar name.
* **Provenance is required for verified records.** ``SourceProvenance`` ties a
  report to its source (URL, document hash, retrieval date, upstream record
  id, parser version); a verified record without at least one of
  ``source_url`` / ``document_hash`` / ``upstream_record_id`` is rejected so
  no measurement floats without a traceable source.
* **Comparability is graded, never assumed.** ``comparability_grade`` returns
  A (directly comparable) through F (incomparable/invalid) with explicit
  reason codes, following the laboratory-comparability research report
  (research/cannabis/laboratory-comparability/). Measurements that lack method
  or moisture metadata cannot be Grade A or B; that is a feature, not a bug.
* **No fabricated identities.** ``compound_id`` is set only when a canonical
  archive record exists (e.g. ``cannabinoids/TCBN-0007`` for THCA,
  ``contaminants/TCNT-0007`` for Lead). Unknown compounds keep their parsed
  name and are left unmapped.
* **Derived statistics use only ``record_kind == verified``.** Demonstration
  and unverified records are never analysis data.

The module deliberately does not build an analysis engine (clustering,
censored-data estimators, uncertainty propagation for summaries are deferred
until real verified batch data exists, mirroring the cultivar chemotype
model).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ResultState(str, Enum):
    """Distinct result states; never conflated (see docs §5)."""

    NUMERIC = "numeric"          # fully quantified
    ND = "nd"                    # tested, not detected above detection capability
    BELOW_LOD = "below_lod"      # detected signal below the limit of detection
    BELOW_LOQ = "below_loq"      # quantified but below the reliable quantitation limit
    ZERO = "zero"                # explicit zero as printed; flagged for review
    MISSING = "missing"          # source record exists but the result field is blank
    NOT_TESTED = "not_tested"    # analyte absent from the panel
    INVALID = "invalid"          # result string present but unparseable/unusable


class CultivarClaimResolution(str, Enum):
    """How confidently a printed label resolves to a canonical cultivar.

    A claim is never forced to resolve: ``resolved`` (confidently one
    cultivar), ``tentative`` (leaning toward one cultivar), ``ambiguous``
    (matches several possibilities), or ``unresolved`` (no canonical target).
    """

    RESOLVED = "resolved"
    TENTATIVE = "tentative"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class ReportingBasis(str, Enum):
    DRY_WEIGHT = "dry-weight"
    AS_RECEIVED = "as-received"
    UNKNOWN = "unknown"


class InstrumentTechnique(str, Enum):
    HPLC_DAD = "HPLC-DAD"
    UHPLC_DAD = "UHPLC-DAD"
    UPLC_DAD = "UPLC-DAD"
    LC_MS = "LC-MS"
    LC_MS_MS = "LC-MS/MS"
    GC_FID = "GC-FID"
    GC_MS = "GC-MS"
    GC_MS_MS = "GC-MS/MS"
    HS_GC_MS = "HS-GC-MS"
    HS_GC_FID = "HS-GC-FID"
    ICP_MS = "ICP-MS"      # heavy-metal panels
    ICP_OES = "ICP-OES"    # heavy-metal panels
    PCR = "PCR"            # microbial panels (qPCR/real-time PCR)
    ELISA = "ELISA"        # mycotoxin immunoassay panels
    OTHER = "other"
    UNKNOWN = "unknown"


class CalibrationType(str, Enum):
    MATRIX_MATCHED = "matrix-matched"
    SOLVENT = "solvent"
    UNKNOWN = "unknown"


class RoundingRule(str, Enum):
    HALF_EVEN = "round-half-even"
    HALF_UP = "round-half-up"
    TRUNCATE = "truncate"
    UNKNOWN = "unknown"


class UncertaintyMethod(str, Enum):
    TOP_DOWN = "top-down"
    BOTTOM_UP = "bottom-up"
    AOAC_SMPR = "AOAC-SMPR"
    UNKNOWN = "unknown"


class MoistureMethod(str, Enum):
    VACUUM_OVEN = "vacuum-oven"
    KARL_FISCHER = "karl-fischer"
    LOSS_ON_DRYING = "loss-on-drying"
    UNKNOWN = "unknown"


class ComparabilityGrade(str, Enum):
    A = "A"  # directly comparable
    B = "B"  # comparable with documented conversion
    C = "C"  # conditionally comparable
    D = "D"  # not comparable
    F = "F"  # incomparable / invalid


class RecordKind(str, Enum):
    VERIFIED = "verified"
    DEMONSTRATION = "demonstration"
    UNVERIFIED = "unverified"


# ---------------------------------------------------------------------------
# Canonical identity patterns
# ---------------------------------------------------------------------------

REPORT_ID_PATTERN = re.compile(r"^lab-results/TLAB-[0-9]{4}$")
BATCH_PRODUCER_ID_PATTERN = re.compile(r"^organizations/TORG-[0-9]{4}$")
BATCH_PRODUCT_ID_PATTERN = re.compile(r"^products/TPRD-[0-9]{4}$")
LAB_ID_PATTERN = re.compile(r"^testing-laboratories/TSTL-[0-9]{4}$")
CULTIVAR_ID_PATTERN = re.compile(r"^cultivars/TCUL-[0-9]{4}$")
LICENSE_ID_PATTERN = re.compile(r"^licenses/TLIC-[0-9]{4}$")

# Vocabulary of test panels a report may declare. Unknown panels are a soft
# warning, never a hard error: jurisdictions legitimately name panels
# differently and the model must not reject legitimate historical data.
TEST_PANEL_VOCABULARY = frozenset({
    "cannabinoid", "terpene", "pesticide", "heavy-metal", "microbial",
    "mycotoxin", "residual-solvent", "foreign-material", "water-activity",
    "moisture", "other",
})
COMPOUND_ID_PATTERN = re.compile(
    r"^(cannabinoids/TCBN|terpenes/TTRP|contaminants/TCNT|botanicals/TBOT)-[0-9]{4}$"
)

# Acidic cannabinoids whose GC-vs-LC behavior differs (underivatized GC
# underestimates acidic forms; laboratory-comparability report §1.1).
ACIDIC_CANNABINOIDS = frozenset({
    "THCA", "CBDA", "CBCA", "CBGA", "THCVA",
})

# Terpenes are identified by the terpenes/TTRP-* collection prefix.
TERPENE_ID_PREFIX = "terpenes/TTRP"


class CoaModelError(ValueError):
    """Base error for model construction / normalization failures."""


class DensityRequiredError(CoaModelError):
    """A mass/volume conversion requires a verified density."""


class UnitConversionError(CoaModelError):
    """The requested unit conversion is not defined."""


class MoistureRequiredError(CoaModelError):
    """A dry-weight / as-received basis conversion requires moisture."""


# ---------------------------------------------------------------------------
# Unit normalization
# ---------------------------------------------------------------------------

# Canonical mass/mass units and their factor to ug/g (1 ug/g == 1 ppm m/m).
_MASS_TO_UG_PER_G: dict[str, float] = {
    "% w/w": 10_000.0,
    "mg/g": 1_000.0,
    "ug/g": 1.0,
    "ppm": 1.0,
    "ppb": 0.001,
}

# Mass/volume units (canonical); conversion to mass/mass requires density.
MASS_PER_VOLUME_UNITS = frozenset({"mg/mL", "ug/mL"})

# Count units; interconvertible only with a density (volume basis).
COUNT_UNITS = frozenset({"CFU/g", "CFU/mL"})

CANONICAL_UNITS = (
    frozenset(_MASS_TO_UG_PER_G) | MASS_PER_VOLUME_UNITS | COUNT_UNITS
    | {"other"}
)

# A conservative relative uncertainty (fraction) added by basis conversion
# when the moisture method uncertainty is not reported (lab-comparability
# report §7.2 suggests u_moisture >= 0.5% absolute).
_DEFAULT_MOISTURE_U = 0.005


@dataclass(frozen=True)
class ConversionAudit:
    """Audit trail for one unit or basis conversion.

    ``added_uncertainty`` is the relative uncertainty (fraction, e.g. 0.05 =
    5%) contributed by the conversion parameters, for propagation by the
    future analysis engine. It is informational here; nothing is propagated in
    this module.
    """

    from_unit: str
    to_unit: str
    factor: float
    formula: str
    params: tuple[str, ...] = ()
    added_uncertainty: Optional[float] = None
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "from_unit": self.from_unit,
            "to_unit": self.to_unit,
            "factor": self.factor,
            "formula": self.formula,
            "params": list(self.params),
            "added_uncertainty": self.added_uncertainty,
            "note": self.note,
        }


def _identity_audit(unit: str) -> ConversionAudit:
    return ConversionAudit(
        from_unit=unit, to_unit=unit, factor=1.0,
        formula="identity", note="unit already canonical",
    )


def _require_density(from_u: str, to_u: str, density_g_per_ml: Optional[float]) -> float:
    if density_g_per_ml is None or density_g_per_ml <= 0:
        raise DensityRequiredError(
            f"conversion {from_u} -> {to_u} requires a verified density "
            "(g/mL) at measurement temperature; mass/volume and mass/mass "
            "values are never converted without it"
        )
    return density_g_per_ml


def convert_unit(
    value: float,
    from_unit: str,
    to_unit: str,
    *,
    density_g_per_ml: Optional[float] = None,
) -> tuple[float, ConversionAudit]:
    """Convert ``value`` from ``from_unit`` to ``to_unit`` with an audit.

    Mass/mass units convert by exact factors. Mass/volume (``mg/mL``,
    ``ug/mL``) conversions require ``density_g_per_ml``; without it a
    :class:`DensityRequiredError` is raised (flower bulk density is never a
    valid conversion factor). Count units (``CFU/g`` <-> ``CFU/mL``) likewise
    require a density. ``other`` and unknown units raise
    :class:`UnitConversionError` — the model refuses silent guesses.

    Nothing is rounded here; precision is preserved for display-time rounding.
    """
    from_u = (from_unit or "").strip()
    to_u = (to_unit or "").strip()
    if from_u == to_u:
        return value, _identity_audit(from_u)

    mass_side = from_u in _MASS_TO_UG_PER_G or from_u in MASS_PER_VOLUME_UNITS
    if mass_side and (to_u in _MASS_TO_UG_PER_G or to_u in MASS_PER_VOLUME_UNITS):
        density: Optional[float] = None
        if from_u in MASS_PER_VOLUME_UNITS or to_u in MASS_PER_VOLUME_UNITS:
            density = _require_density(from_u, to_u, density_g_per_ml)
        # Normalize both sides to ug/g (mass/mass equivalent), then divide.
        ug = _to_ug_per_g(value, from_u, density)
        out = _from_ug_per_g(ug, to_u, density)
        factor = out / value if value else 0.0
        params = (f"density_g_per_ml={density:g}",) if density is not None else ()
        audit = ConversionAudit(
            from_unit=from_u, to_unit=to_u, factor=factor,
            formula=f"value via ug/g mass/mass equivalent"
            + (f" / density_g_per_ml={density:g}" if density is not None else ""),
            params=params,
            added_uncertainty=0.02 if density is not None else None,
            note=(
                "mass/volume conversion; density uncertainty must be recorded"
                " by the ingest pipeline"
                if density is not None
                else "exact mass/mass conversion"
            ),
        )
        return out, audit

    if from_u in COUNT_UNITS and to_u in COUNT_UNITS:
        if from_u == to_u:
            return value, _identity_audit(from_u)
        density = _require_density(from_u, to_u, density_g_per_ml)
        factor = 1.0 / density if from_u == "CFU/mL" else density
        audit = ConversionAudit(
            from_unit=from_u, to_unit=to_u, factor=factor,
            formula=f"value * density_g_per_ml={density:g}",
            params=(f"density_g_per_ml={density:g}",),
            added_uncertainty=0.02,
            note="count-per-volume conversion; density uncertainty must be"
            " recorded by the ingest pipeline",
        )
        return value * factor, audit

    raise UnitConversionError(f"no defined conversion {from_u!r} -> {to_u!r}")


def _to_ug_per_g(value: float, unit: str, density: Optional[float]) -> float:
    """Convert a mass-based value to ug/g (mass/mass equivalent)."""
    if unit in _MASS_TO_UG_PER_G:
        return value * _MASS_TO_UG_PER_G[unit]
    if unit == "mg/mL":
        return value * 1000.0 / density   # mg/mL -> ug/mL -> ug/g
    if unit == "ug/mL":
        return value / density
    raise UnitConversionError(f"unit {unit!r} is not mass-based")


def _from_ug_per_g(ug: float, unit: str, density: Optional[float]) -> float:
    """Convert a ug/g (mass/mass equivalent) value into ``unit``."""
    if unit in _MASS_TO_UG_PER_G:
        return ug / _MASS_TO_UG_PER_G[unit]
    if unit == "mg/mL":
        return ug * density / 1000.0   # ug/g -> ug/mL -> mg/mL
    if unit == "ug/mL":
        return ug * density
    raise UnitConversionError(f"unit {unit!r} is not mass-based")


def convert_basis(
    value: float,
    basis_from: ReportingBasis,
    basis_to: ReportingBasis,
    moisture_fraction: Optional[float],
) -> tuple[float, ConversionAudit]:
    """Convert a value between dry-weight and as-received reporting bases.

    dry -> as-received: ``value * (1 - moisture)``
    as-received -> dry: ``value / (1 - moisture)``

    ``moisture_fraction`` is the fractional moisture content (0.10 = 10%) and
    must be in [0, 1). A missing or invalid moisture raises
    :class:`MoistureRequiredError`; the model never converts bases without it.
    """
    if basis_from == basis_to:
        return value, _identity_audit(basis_from.value)
    if moisture_fraction is None or not (0.0 <= moisture_fraction < 1.0):
        raise MoistureRequiredError(
            "basis conversion requires moisture_fraction in [0, 1); "
            "dry-weight and as-received results are never compared or "
            "converted without it"
        )
    if basis_from == ReportingBasis.DRY_WEIGHT:
        factor = 1.0 - moisture_fraction
        formula = f"value * (1 - {moisture_fraction:g})"
    else:
        factor = 1.0 / (1.0 - moisture_fraction)
        formula = f"value / (1 - {moisture_fraction:g})"
    audit = ConversionAudit(
        from_unit=basis_from.value, to_unit=basis_to.value, factor=factor,
        formula=formula, params=(f"moisture_fraction={moisture_fraction:g}",),
        added_uncertainty=_DEFAULT_MOISTURE_U,
        note="basis conversion; moisture-method uncertainty (>=0.5% absolute"
        " per lab-comparability report) should be propagated downstream",
    )
    return value * factor, audit


def round_to_sigfigs(
    value: float,
    sig_figs: int,
    rule: RoundingRule = RoundingRule.HALF_EVEN,
) -> float:
    """Round a value to ``sig_figs`` significant figures (display only).

    The model never rounds during ingestion; this helper exists so export and
    display code can apply the laboratory's stated rounding convention
    (measured = half-even, calculated = half-up per the Mississippi hybrid
    convention and NIST; see lab-comparability report §1.5).
    """
    if sig_figs < 1:
        raise ValueError("sig_figs must be >= 1")
    if value == 0.0 or not math.isfinite(value):
        return value
    if not math.isfinite(sig_figs):
        raise ValueError("sig_figs must be finite")
    digits = math.floor(math.log10(abs(value)))
    scale = 10.0 ** (sig_figs - 1 - digits)
    scaled = value * scale
    if rule == RoundingRule.HALF_UP:
        rounded = math.floor(scaled + 0.5) if scaled >= 0 else math.ceil(scaled - 0.5)
    elif rule == RoundingRule.TRUNCATE:
        rounded = math.trunc(scaled)
    else:  # half-even (banker's rounding, NIST)
        lower = math.floor(scaled)
        diff = scaled - lower
        if diff > 0.5:
            rounded = lower + 1
        elif diff < 0.5:
            rounded = lower
        else:
            rounded = lower if lower % 2 == 0 else lower + 1
    return rounded / scale


# ---------------------------------------------------------------------------
# Result decoding (reported string -> structured state)
# ---------------------------------------------------------------------------

_ND_TOKENS = {"nd", "n.d.", "n/d", "not detected", "none detected", "n.d"}
_NOT_TESTED_TOKENS = {"not tested", "not tested for", "nt", "not run", "n/t"}


def decode_result(raw: Optional[str]) -> tuple[ResultState, Optional[float], Optional[str]]:
    """Decode a reported result string into (state, value, note).

    ``value`` is set only for ``numeric`` and ``zero`` states. Explicit zeros
    are returned as ``zero`` with a review flag — never conflated with ``nd``
    or ``missing``. Unrecognized non-blank strings are returned as ``invalid``
    with the original text in ``note`` so nothing is lost; ``invalid`` is
    distinct from ``missing`` (blank field) and never conflated with ``nd`` or
    ``zero``.
    """
    text = (raw or "").strip()
    if not text:
        return ResultState.MISSING, None, "blank result field"

    lowered = text.lower()
    if lowered in _ND_TOKENS:
        return ResultState.ND, None, None
    if lowered in _NOT_TESTED_TOKENS:
        return ResultState.NOT_TESTED, None, None
    if lowered in ("<lod", "< lod", "below lod", "bdl"):
        return ResultState.BELOW_LOD, None, None
    if lowered in ("<loq", "< loq", "below loq"):
        return ResultState.BELOW_LOQ, None, None
    if lowered.startswith("<"):
        # e.g. "<0.05": censored below a printed threshold. The threshold is
        # the quantitation limit unless the method states otherwise; the note
        # keeps that assumption visible.
        try:
            limit = float(text[1:].strip())
        except ValueError:
            return ResultState.MISSING, None, f"unrecognized censored string {text!r}"
        return ResultState.BELOW_LOQ, None, (
            f"censored below printed threshold {limit:g}; confirm against "
            "the method LOQ"
        )

    try:
        value = float(text)
    except ValueError:
        return ResultState.INVALID, None, (
            f"unrecognized result string {text!r} preserved verbatim; "
            "state=invalid, never conflated with missing/nd/zero"
        )
    if value == 0.0:
        return ResultState.ZERO, 0.0, (
            "explicit zero as printed; flagged for review — chemically "
            "implausible for cannabinoids in cannabis, but a common ND "
            "reporting convention for contaminants"
        )
    return ResultState.NUMERIC, value, None


# ---------------------------------------------------------------------------
# Method / laboratory / report / batch / measurement records
# ---------------------------------------------------------------------------


def _claim_problems(claim: "CultivarClaim") -> list[str]:
    problems: list[str] = []
    if not claim.label.strip():
        problems.append("cultivar claim label is required")
    if claim.cultivar_id is not None and not CULTIVAR_ID_PATTERN.fullmatch(claim.cultivar_id):
        problems.append(
            f"claim cultivar_id {claim.cultivar_id!r} is not a canonical cultivars/TCUL-XXXX id"
        )
    for candidate in claim.candidate_ids:
        if not CULTIVAR_ID_PATTERN.fullmatch(candidate):
            problems.append(
                f"claim candidate id {candidate!r} is not a canonical cultivars/TCUL-XXXX id"
            )
    if claim.resolution == CultivarClaimResolution.RESOLVED and claim.cultivar_id is None:
        problems.append("resolved cultivar claims require a cultivar_id")
    return problems


def _claim_warnings(claim: "CultivarClaim") -> list[str]:
    warnings: list[str] = []
    if claim.resolution == CultivarClaimResolution.AMBIGUOUS and not claim.candidate_ids:
        warnings.append(
            f"claim {claim.label!r} is ambiguous but lists no candidate ids"
        )
    if claim.resolution == CultivarClaimResolution.TENTATIVE and claim.cultivar_id is None:
        warnings.append(
            f"claim {claim.label!r} is tentative but names no leaning cultivar_id"
        )
    return warnings


@dataclass(frozen=True)
class CultivarClaim:
    """A cultivar name/label as claimed for a product or batch.

    The claim is the *printed identity*, never a measurement: resolving it to a
    canonical ``cultivars/TCUL-XXXX`` record is a separate, optional act with an
    explicit ``resolution`` grade. ``candidate_ids`` lists the several
    possibilities when the label is ambiguous. Unknown labels stay
    ``resolution = unresolved`` with ``cultivar_id = None`` — resolution is
    never forced.
    """

    label: str
    resolution: CultivarClaimResolution = CultivarClaimResolution.UNRESOLVED
    cultivar_id: Optional[str] = None
    candidate_ids: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        problems = _claim_problems(self)
        if problems:
            raise ValueError("; ".join(problems))

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "resolution": self.resolution.value,
            "cultivar_id": self.cultivar_id,
            "candidate_ids": list(self.candidate_ids),
            "note": self.note,
        }


@dataclass(frozen=True)
class SourceProvenance:
    """Retrieval metadata tying a report to its source document/endpoint.

    Every real observation must trace to a source: this object records the
    official URL, a document hash, when the archive retrieved it, the upstream
    record id, and the parser/import version that produced the record. All
    fields are optional so incomplete historical data stays representable;
    verified records require at least one of ``source_url`` /
    ``document_hash`` / ``upstream_record_id`` (see ``coa_problems``).
    """

    source_url: str = ""
    document_hash: str = ""           # sha256 hex of the source artifact
    retrieval_date: Optional[str] = None
    upstream_record_id: str = ""
    parser_version: str = ""
    retrieval_note: str = ""

    def to_dict(self) -> dict:
        return {
            "source_url": self.source_url,
            "document_hash": self.document_hash,
            "retrieval_date": self.retrieval_date,
            "upstream_record_id": self.upstream_record_id,
            "parser_version": self.parser_version,
            "retrieval_note": self.retrieval_note,
        }


@dataclass(frozen=True)
class MethodMetadata:
    """Optional analytical method metadata (report- or measurement-level).

    Fields mirror the minimum-viable-comparability metadata from the
    laboratory-comparability report §3. Unknowns are explicit; absence of this
    object entirely means the report carries no method section and cannot
    grade above D.
    """

    instrument_technique: InstrumentTechnique = InstrumentTechnique.UNKNOWN
    derivatization: Optional[bool] = None      # GC cannabinoids: acids derivatized?
    extraction_method: str = ""                # e.g. "headspace", "liquid-injection"
    extraction_solvent: str = ""
    homogenization_method: str = ""
    internal_standard: str = ""
    calibration_type: CalibrationType = CalibrationType.UNKNOWN
    calibration_range: str = ""
    matrix_matched_calibration: Optional[bool] = None
    crm_vendor: str = ""
    crm_lot: str = ""
    moisture_method: MoistureMethod = MoistureMethod.UNKNOWN
    moisture_content_pct: Optional[float] = None
    rounding_rule: RoundingRule = RoundingRule.UNKNOWN
    significant_figures: Optional[int] = None
    measurement_uncertainty: Optional[float] = None  # expanded k=2, relative fraction
    uncertainty_method: UncertaintyMethod = UncertaintyMethod.UNKNOWN
    accreditation_body: str = ""
    pt_provider: str = ""
    pt_z_score: Optional[float] = None

    def to_dict(self) -> dict:
        out = {k: getattr(self, k) for k in self.__dataclass_fields__}
        for key in (
            "instrument_technique", "calibration_type", "moisture_method",
            "rounding_rule", "uncertainty_method",
        ):
            out[key] = out[key].value
        return out


@dataclass(frozen=True)
class Laboratory:
    """Testing laboratory. ``lab_id`` is the archive record when one exists."""

    name: str
    lab_id: Optional[str] = None
    license_number: str = ""
    jurisdiction: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lab_id": self.lab_id,
            "license_number": self.license_number,
            "jurisdiction": self.jurisdiction,
        }


@dataclass(frozen=True)
class Report:
    """One laboratory report (COA) document.

    ``report_id`` is the archive record id (``lab-results/TLAB-XXXX``).
    ``revision`` increments when a corrected report supersedes an earlier one;
    ``supersedes`` names the prior report id. ``source_reference`` points at
    the original document (COA number, PDF id, or dataset row key) so every
    value traces to the printed artifact; ``provenance`` carries the retrieval
    metadata (URL, hash, retrieval date, upstream id, parser version).
    ``sample_id`` is the laboratory's own sample identifier when printed.
    ``license_references`` names regulator licenses (``licenses/TLIC-XXXX``
    canonical ids when records exist, else natural license numbers as
    printed). ``test_panels`` declares the panels the report covers
    (``cannabinoid``, ``terpene``, ``pesticide``, ``heavy-metal``, ...).
    """

    report_id: str
    revision: int = 1
    supersedes: Optional[str] = None
    source_reference: str = ""
    report_date: Optional[str] = None
    test_date: Optional[str] = None
    sample_date: Optional[str] = None
    sample_id: str = ""
    laboratory: Optional[Laboratory] = None
    jurisdiction: str = ""
    license_references: tuple[str, ...] = ()
    test_panels: tuple[str, ...] = ()
    provenance: Optional[SourceProvenance] = None
    method: Optional[MethodMetadata] = None

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "revision": self.revision,
            "supersedes": self.supersedes,
            "source_reference": self.source_reference,
            "report_date": self.report_date,
            "test_date": self.test_date,
            "sample_date": self.sample_date,
            "sample_id": self.sample_id,
            "laboratory": self.laboratory.to_dict() if self.laboratory else None,
            "jurisdiction": self.jurisdiction,
            "license_references": list(self.license_references),
            "test_panels": list(self.test_panels),
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "method": self.method.to_dict() if self.method else None,
        }


@dataclass(frozen=True)
class Batch:
    """The commercial batch/lot/package a report's sample came from.

    ``batch_id`` is the producer/operator batch identifier (a natural key
    stable across retests and reports). ``metrc_tag`` carries the state
    traceability package tag when the source system provides one (e.g. the
    CCC testing files' METRC SOURCE TAG). ``lot_number``, ``harvest_date``,
    ``production_date``, and ``package_date`` are optional identifiers/dates
    that legitimately vary by jurisdiction and are never required.
    ``cultivar_labels`` keeps the raw printed labels; ``cultivar_claims``
    carries the interpreted claims (resolution, canonical target) when an
    editor or ingest step has attempted resolution — claims may be absent and
    resolution is never forced.
    """

    batch_id: str
    metrc_tag: str = ""
    lot_number: str = ""
    producer_id: Optional[str] = None
    product_id: Optional[str] = None
    cultivar_labels: tuple[str, ...] = ()
    cultivar_claims: tuple[CultivarClaim, ...] = ()
    sample_type: str = "unknown"
    matrix_detail: str = ""
    basis: ReportingBasis = ReportingBasis.UNKNOWN
    decarb_convention: str = "unknown"      # native | total-potential | not-applicable | unknown
    record_kind: RecordKind = RecordKind.UNVERIFIED
    jurisdiction: str = ""
    harvest_date: Optional[str] = None
    production_date: Optional[str] = None
    package_date: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "metrc_tag": self.metrc_tag,
            "lot_number": self.lot_number,
            "producer_id": self.producer_id,
            "product_id": self.product_id,
            "cultivar_labels": list(self.cultivar_labels),
            "cultivar_claims": [c.to_dict() for c in self.cultivar_claims],
            "sample_type": self.sample_type,
            "matrix_detail": self.matrix_detail,
            "basis": self.basis.value,
            "decarb_convention": self.decarb_convention,
            "record_kind": self.record_kind.value,
            "jurisdiction": self.jurisdiction,
            "harvest_date": self.harvest_date,
            "production_date": self.production_date,
            "package_date": self.package_date,
        }


@dataclass(frozen=True)
class AnalyteMeasurement:
    """One analyte measurement in one laboratory report.

    ``reported_value`` / ``reported_unit`` preserve the printed string and
    unit exactly; ``value`` / ``unit`` carry the normalized representation
    (converted, never rounded). ``state`` discriminates numeric / nd /
    below_lod / below_loq / zero / missing / not_tested; each state has its
    own allowed value contract (see :func:`measurement_problems`).
    """

    compound_name: str
    state: ResultState
    compound_id: Optional[str] = None
    compound_cas: Optional[str] = None
    reported_value: str = ""
    reported_unit: str = ""
    value: Optional[float] = None
    unit: str = ""
    lod: Optional[float] = None
    loq: Optional[float] = None
    method: Optional[MethodMetadata] = None
    test_date: Optional[str] = None
    quantitation_note: Optional[str] = None
    conversion: Optional[ConversionAudit] = None
    calculation_formula: Optional[str] = None  # set => report-derived calculated quantity

    def __post_init__(self) -> None:
        problems = measurement_problems(self)
        if problems:
            raise ValueError("; ".join(problems))

    def to_dict(self) -> dict:
        return {
            "compound_id": self.compound_id,
            "compound_name": self.compound_name,
            "compound_cas": self.compound_cas,
            "reported_value": self.reported_value,
            "reported_unit": self.reported_unit,
            "state": self.state.value,
            "value": self.value,
            "unit": self.unit,
            "lod": self.lod,
            "loq": self.loq,
            "method": self.method.to_dict() if self.method else None,
            "test_date": self.test_date,
            "quantitation_note": self.quantitation_note,
            "conversion": self.conversion.to_dict() if self.conversion else None,
            "calculation_formula": self.calculation_formula,
        }


def measurement_problems(m: AnalyteMeasurement) -> list[str]:
    """Hard contract violations that make a measurement unusable (raise)."""
    problems: list[str] = []
    if not m.compound_name.strip():
        problems.append("compound_name is required")
    if m.compound_id is not None and not COMPOUND_ID_PATTERN.fullmatch(m.compound_id):
        problems.append(f"compound_id {m.compound_id!r} is not a canonical entity id")
    if m.state in (ResultState.NUMERIC, ResultState.ZERO):
        if m.value is None or not math.isfinite(m.value):
            problems.append(f"state={m.state.value} requires a finite value")
    else:
        if m.value is not None:
            problems.append(f"state={m.state.value} must not carry a value")
    if m.state == ResultState.ZERO and m.value != 0.0:
        problems.append("state=zero requires value == 0.0")
    if m.state == ResultState.BELOW_LOD and m.lod is None:
        problems.append("below_lod requires an lod")
    if m.state == ResultState.BELOW_LOQ and m.loq is None:
        problems.append("below_loq requires an loq")
    if m.state == ResultState.NUMERIC and not m.reported_value:
        problems.append("numeric measurement requires a reported value")
    return problems


def soft_measurement_warnings(m: AnalyteMeasurement) -> list[str]:
    """Non-fatal notes surfaced by ``coa_warnings`` (never raise)."""
    warnings: list[str] = []
    if m.state == ResultState.ND and m.lod is None:
        warnings.append(f"{m.compound_name}: nd should carry an lod so detection capability is recorded")
    if m.state in (ResultState.ZERO, ResultState.NUMERIC) and m.unit and m.unit not in CANONICAL_UNITS:
        warnings.append(f"{m.compound_name}: unit {m.unit!r} is not canonical")
    if m.state == ResultState.ZERO:
        warnings.append(f"{m.compound_name}: explicit zero flagged for review (never treated as nd/missing)")
    if m.state == ResultState.INVALID:
        warnings.append(
            f"{m.compound_name}: reported result string is present but unparseable "
            "(state=invalid); preserved verbatim for review"
        )
    if m.calculation_formula is not None:
        if m.compound_id is not None:
            warnings.append(
                f"{m.compound_name}: calculated quantity carries compound_id; "
                "report-derived totals are not independent chemical compounds"
            )
        if m.state != ResultState.NUMERIC:
            warnings.append(
                f"{m.compound_name}: calculated quantity has state={m.state.value}; "
                "calculated rows are expected to be numeric"
            )
    if m.test_date is not None and len(m.test_date) > 10:
        warnings.append(f"{m.compound_name}: test_date is not an ISO date")
    return warnings


# ---------------------------------------------------------------------------
# Top-level record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoaRecord:
    """Durable unit of publication: one report document + batch + measurements.

    ``record_kind`` mirrors the cultivar-profile model: ``verified`` only for
    real, provenance-verified COAs; ``demonstration`` and ``unverified``
    records are never analysis data. For ``verified`` records the report id
    must be a canonical ``lab-results/TLAB-XXXX``; provisional natural keys
    (e.g. ``ma-ccc:<metrc tag>``) are tolerated only for non-verified records
    and surface as warnings.
    """

    report: Report
    batch: Batch
    measurements: tuple[AnalyteMeasurement, ...]

    def __post_init__(self) -> None:
        problems = coa_problems(self)
        if problems:
            raise ValueError("; ".join(problems))

    def to_dict(self) -> dict:
        return {
            "schema_version": "1.0",
            "report": self.report.to_dict(),
            "batch": self.batch.to_dict(),
            "measurements": [m.to_dict() for m in self.measurements],
        }


def coa_problems(record: CoaRecord) -> list[str]:
    """HARD validation problems for a CoaRecord (empty = valid)."""
    problems: list[str] = []
    if not record.report.report_id:
        problems.append("report_id is required")
    if not record.batch.batch_id:
        problems.append("batch_id is required")
    if record.batch.producer_id is not None and not BATCH_PRODUCER_ID_PATTERN.fullmatch(record.batch.producer_id):
        problems.append("producer_id must be a canonical organizations/TORG-XXXX id or null")
    if record.batch.product_id is not None and not BATCH_PRODUCT_ID_PATTERN.fullmatch(record.batch.product_id):
        problems.append("product_id must be a canonical products/TPRD-XXXX id or null")
    if record.report.laboratory is not None and record.report.laboratory.lab_id is not None \
            and not LAB_ID_PATTERN.fullmatch(record.report.laboratory.lab_id):
        problems.append("laboratory.lab_id must be a canonical testing-laboratories/TSTL-XXXX id or null")
    if record.report.revision < 1:
        problems.append("report revision must be >= 1")
    for claim in record.batch.cultivar_claims:
        problems.extend(_claim_problems(claim))
    if not record.measurements:
        problems.append("at least one analyte measurement is required")
    seen: set[str] = set()
    for m in record.measurements:
        problems.extend(measurement_problems(m))
        key = m.compound_id or m.compound_name
        if key in seen:
            problems.append(f"duplicate analyte measurement for {key}")
        seen.add(key)
    if record.batch.record_kind == RecordKind.VERIFIED:
        if not REPORT_ID_PATTERN.fullmatch(record.report.report_id):
            problems.append(
                "verified records require a canonical lab-results/TLAB-XXXX report id"
            )
        if record.report.report_date is None:
            problems.append("verified records require a report_date")
        provenance = record.report.provenance
        has_provenance = provenance is not None and bool(
            provenance.source_url.strip()
            or provenance.document_hash.strip()
            or provenance.upstream_record_id.strip()
        )
        if not has_provenance:
            problems.append(
                "verified records require provenance (source_url, document_hash, "
                "or upstream_record_id) so every measurement traces to a source"
            )
    return problems


def coa_warnings(record: CoaRecord) -> list[str]:
    """SOFT, non-fatal validation notes for a CoaRecord."""
    warnings: list[str] = []
    if record.batch.record_kind != RecordKind.VERIFIED \
            and not REPORT_ID_PATTERN.fullmatch(record.report.report_id):
        warnings.append(
            f"provisional report id {record.report.report_id!r}; allocate a "
            "canonical lab-results/TLAB-XXXX id before verification"
        )
    if record.report.laboratory is None:
        warnings.append("no laboratory recorded; results cannot be lab-stratified")
    if record.report.method is None:
        for m in record.measurements:
            if m.method is None:
                warnings.append(
                    f"{m.compound_name}: no method metadata (report or "
                    "measurement level); cross-lab comparability is limited"
                )
                break
    if record.batch.basis == ReportingBasis.UNKNOWN:
        warnings.append(
            "reporting basis unknown; dry-weight and as-received results are "
            "never compared without a basis"
        )
    for claim in record.batch.cultivar_claims:
        warnings.extend(_claim_warnings(claim))
    for reference in record.report.license_references:
        if not LICENSE_ID_PATTERN.fullmatch(reference):
            warnings.append(
                f"license reference {reference!r} is not a canonical licenses/TLIC-XXXX "
                "id; natural license numbers are preserved verbatim until a record exists"
            )
    for panel in record.report.test_panels:
        if panel not in TEST_PANEL_VOCABULARY:
            warnings.append(
                f"test panel {panel!r} is not in the known vocabulary; preserved verbatim"
            )
    if record.report.provenance is not None:
        prov = record.report.provenance
        if prov.retrieval_date is not None and len(prov.retrieval_date) > 10:
            warnings.append("provenance.retrieval_date is not an ISO date")
        if prov.document_hash and not re.fullmatch(r"[0-9a-fA-F]{64}", prov.document_hash):
            warnings.append("provenance.document_hash is not a 64-char hex sha256")
    for label, date_value in (
        ("production_date", record.batch.production_date),
        ("package_date", record.batch.package_date),
        ("harvest_date", record.batch.harvest_date),
    ):
        if date_value is not None and len(date_value) > 10:
            warnings.append(f"batch.{label} is not an ISO date")
    for m in record.measurements:
        warnings.extend(soft_measurement_warnings(m))
    return warnings


def censorship_summary(record: CoaRecord) -> dict[str, int]:
    """Count measurements per result state."""
    counts = {state.value: 0 for state in ResultState}
    for m in record.measurements:
        counts[m.state.value] += 1
    return counts


# ---------------------------------------------------------------------------
# Cross-lab comparability grading
# ---------------------------------------------------------------------------

# Grade-D reasons (lab-comparability report §6.2): any one forces grade D.
_CRITICAL_REASONS = frozenset({
    "gc_underivatized_vs_lc_acidic",
    "lab_a_pt_unsatisfactory",
    "lab_b_pt_unsatisfactory",
    "moisture_unknown_for_conversion",
    "calibration_type_mismatch",
    "terpene_panel_overlap_lt_50",
})

# ISO 13528: |z| >= 3 is unsatisfactory performance in proficiency testing.
PT_UNSATISFACTORY_Z = 3.0


@dataclass(frozen=True)
class ComparabilityView:
    """The subset of two records needed to grade their comparability."""

    compound_name: str
    compound_id: Optional[str] = None
    matrix_class: str = "unknown"                 # flower | concentrate | edible | ...
    instrument_technique: InstrumentTechnique = InstrumentTechnique.UNKNOWN
    derivatization: Optional[bool] = None
    basis: ReportingBasis = ReportingBasis.UNKNOWN
    moisture_content_pct: Optional[float] = None
    pt_z_score: Optional[float] = None
    measurement_uncertainty: Optional[float] = None
    matrix_matched_calibration: Optional[bool] = None
    terpene_panel: frozenset = frozenset()

    @classmethod
    def from_measurement(
        cls,
        m: AnalyteMeasurement,
        *,
        basis: ReportingBasis = ReportingBasis.UNKNOWN,
        matrix_class: str = "unknown",
        jurisdiction: str = "",
    ) -> "ComparabilityView":
        method = m.method
        return cls(
            compound_name=m.compound_name,
            compound_id=m.compound_id,
            matrix_class=matrix_class,
            instrument_technique=(
                method.instrument_technique if method else InstrumentTechnique.UNKNOWN
            ),
            derivatization=method.derivatization if method else None,
            basis=basis,
            moisture_content_pct=(
                method.moisture_content_pct if method else None
            ),
            pt_z_score=method.pt_z_score if method else None,
            measurement_uncertainty=(
                method.measurement_uncertainty if method else None
            ),
            matrix_matched_calibration=(
                method.matrix_matched_calibration if method else None
            ),
        )


def _is_acidic_cannabinoid(name: str) -> bool:
    token = name.upper().replace(" ", "").replace("-", "").replace("Δ", "D")
    return any(acid in token for acid in ACIDIC_CANNABINOIDS)


def comparability_grade(
    a: ComparabilityView,
    b: ComparabilityView,
) -> tuple[ComparabilityGrade, list[str]]:
    """Pairwise comparability grade A-F with reason codes.

    Implements the grading algorithm from the laboratory-comparability
    research report §6.2 (which follows ISO 13528 z-score conventions):

    * F — different analyte or different matrix class (never comparable).
    * D — any critical mismatch: underivatized GC vs LC on acidic
      cannabinoids, |z| >= 3 for either lab, moisture unknown for a basis
      conversion, calibration-type mismatch, or <50% terpene panel overlap.
    * A — no reasons at all (same technique, basis, calibration, PT, MU,
      rounding, matrix).
    * B — exactly one non-critical difference (e.g. basis differs but moisture
      is known).
    * C — more than one non-critical difference.

    The result is a *pairwise, per-analyte* judgement; it never makes a
    measurement interchangeable with another, it only says how directly they
    can be compared.
    """
    reasons: list[str] = []
    if a.compound_name != b.compound_name or (
        a.compound_id and b.compound_id and a.compound_id != b.compound_id
    ):
        return ComparabilityGrade.F, ["different_analyte"]
    if a.matrix_class != b.matrix_class:
        return ComparabilityGrade.F, ["different_matrix_class"]

    techs = {a.instrument_technique, b.instrument_technique}
    acidic = _is_acidic_cannabinoid(a.compound_name)
    if acidic and {InstrumentTechnique.GC_FID, InstrumentTechnique.GC_MS} & techs \
            and (InstrumentTechnique.LC_MS in techs or InstrumentTechnique.LC_MS_MS in techs
                 or InstrumentTechnique.HPLC_DAD in techs or InstrumentTechnique.UPLC_DAD in techs):
        if not (a.derivatization and b.derivatization):
            reasons.append("gc_underivatized_vs_lc_acidic")

    if a.basis != b.basis:
        if a.moisture_content_pct is None or b.moisture_content_pct is None:
            reasons.append("moisture_unknown_for_conversion")
        else:
            reasons.append("basis_converted_with_moisture")

    for label, z in (("lab_a", a.pt_z_score), ("lab_b", b.pt_z_score)):
        if z is not None and abs(z) >= PT_UNSATISFACTORY_Z:
            reasons.append(f"{label}_pt_unsatisfactory")

    if a.measurement_uncertainty is None or b.measurement_uncertainty is None:
        reasons.append("missing_MU")

    if a.matrix_matched_calibration != b.matrix_matched_calibration:
        reasons.append("calibration_type_mismatch")

    if a.compound_id and a.compound_id.startswith(TERPENE_ID_PREFIX):
        if a.terpene_panel and b.terpene_panel:
            overlap = len(a.terpene_panel & b.terpene_panel)
            union = len(a.terpene_panel | b.terpene_panel)
            if union and overlap / union < 0.5:
                reasons.append("terpene_panel_overlap_lt_50")

    if not reasons:
        return ComparabilityGrade.A, ["all_criteria_met"]
    if any(r in _CRITICAL_REASONS for r in reasons):
        return ComparabilityGrade.D, reasons
    if len(reasons) <= 1:
        return ComparabilityGrade.B, reasons
    return ComparabilityGrade.C, reasons


# ---------------------------------------------------------------------------
# Massachusetts CCC adapter (real-data mapping)
# ---------------------------------------------------------------------------

# Canonical compound records that exist in the archive today (metadata/id-map.jsonl).
_CANONICAL_ANALYTE_IDS = {
    "THCA": "cannabinoids/TCBN-0007",
    "Lead": "contaminants/TCNT-0007",
}

# Analyte unit as printed inside the CCC analyte name -> canonical unit.
_MA_UNIT_MAP = {
    "%": "% w/w",
    "ppm": "ppm",
    "ppb": "ppb",
    "mg/g": "mg/g",
    "ug/g": "ug/g",
    "CFU/g": "CFU/g",
    "CFU/mL": "CFU/mL",
}

MA_DECARB_DEFAULT = "native"      # CCC testing files list THC and THCA as
# separate native rows; no total-potential column


def massachusetts_canonical_unit(reported_unit: str) -> str:
    """Map a CCC analyte unit (e.g. ``%``, ``ppm``, ``CFU/g``) to canonical."""
    key = (reported_unit or "").strip()
    if not key:
        return "other"
    return _MA_UNIT_MAP.get(key, key if key in CANONICAL_UNITS else "other")


def from_massachusetts_normalized(row: dict) -> AnalyteMeasurement:
    """Map one normalized CCC testing row to an :class:`AnalyteMeasurement`.

    Consumes the row shape produced by
    ``scripts.ingest.states.massachusetts.normalize_testing_common`` (date,
    metrc_id, analyte_id, result, result_numeric, test_passed, lab, notes,
    strain, product_category, test_category, quantity, unit_of_measure,
    test_id, analyte, analyte_unit, matrix). The CCC open-data CSVs carry no
    method, LOD/LOQ, or basis fields; those are recorded as unknown and
    surfaced as soft warnings so the missing metadata stays visible.
    """
    analyte = (row.get("analyte") or row.get("analyte_id") or "").strip()
    reported_value = row.get("result")
    state, value, note = decode_result(reported_value)

    reported_unit = (row.get("analyte_unit") or "").strip() or (row.get("unit_of_measure") or "").strip()
    unit = massachusetts_canonical_unit(reported_unit)

    conversion = None
    if value is not None and unit and unit not in ("other",):
        try:
            _, conversion = convert_unit(value, unit, unit)
        except (UnitConversionError, DensityRequiredError):
            conversion = None

    compound_id = _CANONICAL_ANALYTE_IDS.get(analyte)
    if compound_id is None:
        # Match contaminant records by normalized name (e.g. "Lead").
        lowered = analyte.lower()
        if lowered in ("lead", "lead (pb)"):
            compound_id = "contaminants/TCNT-0007"

    matrix = (row.get("matrix") or "").strip() or "Raw Plant Material"
    return AnalyteMeasurement(
        compound_id=compound_id,
        compound_name=analyte,
        reported_value="" if reported_value is None else str(reported_value).strip(),
        reported_unit=reported_unit,
        state=state,
        value=value,
        unit=unit,
        test_date=row.get("date") or None,
        conversion=conversion,
        quantitation_note=note,
    )


def massachusetts_rows_to_record(
    rows: Iterable[dict],
    *,
    metrc_tag: Optional[str] = None,
    jurisdiction: str = "MA",
    record_kind: RecordKind = RecordKind.UNVERIFIED,
    sample_type: str = "flower",
) -> CoaRecord:
    """Group normalized CCC testing rows into one provisional :class:`CoaRecord`.

    Rows are grouped by the Metrc package tag (the CCC files' ``METRC SOURCE
    TAG``) when present, else by ``METRC ID``. The resulting record uses a
    provisional natural-key ``report_id`` (``ma-ccc:<tag>``) which is legal
    for non-verified records and must be replaced by a canonical
    ``lab-results/TLAB-XXXX`` id (allocated via the ingest pipeline's
    NaturalKeyRegistry) before the record can be verified. See
    docs/graph/coa-migration.md.
    """
    rows = list(rows)
    if not rows:
        raise ValueError("massachusetts_rows_to_record requires at least one row")

    first = rows[0]
    source_tag = (first.get("METRC SOURCE TAG") or first.get("METRC source tag") or "").strip()
    tag = (
        (metrc_tag or "").strip()
        or source_tag
        or (first.get("metrc_id") or "").strip()
    )
    if not tag:
        raise ValueError("a metrc package tag (or metrc_id) is required to group rows")

    measurements = tuple(from_massachusetts_normalized(r) for r in rows)
    cultivar_labels = tuple(
        sorted({r.get("strain") for r in rows if (r.get("strain") or "").strip()})
    )
    has_potency = any(
        m.compound_name in ("THC", "THCA") for m in measurements
    )
    laboratory_name = (first.get("lab") or "").strip()
    laboratory = (
        Laboratory(name=laboratory_name, jurisdiction=jurisdiction)
        if laboratory_name else None
    )

    report = Report(
        report_id=f"ma-ccc:{tag}",
        source_reference=f"CCC testing CSV row group (metrc tag {tag})",
        test_date=first.get("date") or None,
        laboratory=laboratory,
        jurisdiction=jurisdiction,
    )
    batch = Batch(
        batch_id=tag,
        metrc_tag=tag,
        cultivar_labels=cultivar_labels,
        sample_type=sample_type,
        matrix_detail=(first.get("matrix") or "").strip() or "Raw Plant Material",
        basis=ReportingBasis.UNKNOWN,
        decarb_convention="native" if has_potency else "not-applicable",
        record_kind=record_kind,
        jurisdiction=jurisdiction,
    )
    return CoaRecord(report=report, batch=batch, measurements=measurements)
