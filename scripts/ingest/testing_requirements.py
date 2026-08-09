"""Normalized jurisdiction testing-requirements model.

Structured capture of what a jurisdiction *requires* laboratories to test,
with exact primary citations. The canonical data lives in
``data/testing-requirements/<state>.json``; this module validates it and
renders the human-readable requirement records under ``content/requirements/``.

Design rules (see docs/jurisdiction-evidence-model.md):

* Jurisdiction-specific language is preserved verbatim in ``notes`` /
  ``governing_document`` even when a shared normalized ``category`` is applied.
* A numeric limit is only recorded with a citation. Where a primary source
  states a limit in prose but the authoritative table is image-only in the
  source document, ``value_status`` is ``pending-transcription`` and the
  exact location is named — the ambiguity is recorded, not silently resolved.
* ``effective_date`` / ``superseded_date`` are recorded where known so a
  state's limit history is not flattened into "current".
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .core import IngestError

# Controlled vocabularies -----------------------------------------------------

PANEL_CATEGORIES = [
    "cannabinoid", "terpene", "pesticide", "heavy-metal", "microbial",
    "mycotoxin", "residual-solvent", "moisture", "water-activity",
    "foreign-material", "homogeneity", "process", "other",
]

MATRICES = [
    "all", "inhalable", "non-inhalable", "dried-flower", "flower-pre-rolls",
    "solid-edible", "cannabis-product", "concentrate-resin", "vape-product",
    "final-plant-material", "all-uses", "ingestion-only", "cannabis-oil",
    "tincture", "topical", "other",
]

VALUE_STATUSES = ["verified", "pending-transcription", "reported-by-source", "unknown"]

# Qualitative requirements ("not detected", "prohibited") are verified limits
# whose stated value IS the qualitative state, not a number. Numeric operators
# (≤, <, =) always require a numeric limit + unit.
QUALITATIVE_COMPARISONS = {
    "not-detected", "absent", "prohibited", "reported", "negative", "not-required",
}


@dataclass
class LegalReference:
    """A statute, regulation, or guidance document citation."""

    title: str                      # human-readable name
    citation: str                   # e.g. "4 CCR § 15719" | "935 CMR 500.160(2)"
    url: str = ""
    kind: str = "regulation"        # statute | regulation | guidance | advisory | other
    retrieved_at: str = ""
    notes: str = ""

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.title.strip():
            problems.append("legal reference title is required")
        if not self.citation.strip():
            problems.append(f"{self.title}: citation is required")
        if self.url and not self.url.startswith(("http://", "https://")):
            problems.append(f"{self.title}: url must be http(s)")
        return problems


@dataclass
class PanelRequirement:
    """One mandatory test category on the jurisdiction panel."""

    category: str                   # PANEL_CATEGORIES
    required: bool = True
    citation: str = ""
    citation_url: str = ""
    notes: str = ""                 # jurisdiction-specific language

    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.category not in PANEL_CATEGORIES:
            problems.append(f"unknown panel category {self.category!r}")
        if self.required and not self.citation.strip():
            problems.append(f"{self.category}: required panel needs a citation")
        return problems


@dataclass
class LimitRecord:
    """One analyte/action-limit row with provenance."""

    analyte: str
    category: str                   # PANEL_CATEGORIES
    citation: str
    matrix: str = "all"             # MATRICES
    cas: str = ""
    limit: str = ""                 # numeric value as stated, e.g. "0.2"
    unit: str = ""                  # µg/g, µg/kg, ppb, %, Aw, CFU/g, mg/g ...
    comparison: str = "≤"           # ≤ | < | = | not-detected | absent
    effective_date: str = ""
    superseded_date: str = ""
    value_status: str = "verified"  # VALUE_STATUSES
    citation_url: str = ""
    notes: str = ""

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.analyte.strip():
            problems.append("limit analyte is required")
        if self.category not in PANEL_CATEGORIES:
            problems.append(f"{self.analyte}: unknown category {self.category!r}")
        if not self.citation.strip():
            problems.append(f"{self.analyte}: limit needs a citation")
        if self.matrix not in MATRICES:
            problems.append(f"{self.analyte}: unknown matrix {self.matrix!r}")
        if self.value_status not in VALUE_STATUSES:
            problems.append(f"{self.analyte}: unknown value_status {self.value_status!r}")
        if self.value_status == "verified" and not (self.limit and self.unit):
            if self.comparison not in QUALITATIVE_COMPARISONS:
                problems.append(
                    f"{self.analyte}: verified limit needs both limit and unit "
                    f"(or a qualitative comparison like 'not-detected')"
                )
        if self.value_status == "verified" and self.comparison in QUALITATIVE_COMPARISONS and self.limit:
            problems.append(
                f"{self.analyte}: qualitative comparison {self.comparison!r} should not carry a numeric limit"
            )
        if self.value_status == "pending-transcription" and self.limit:
            problems.append(
                f"{self.analyte}: pending-transcription limit must leave limit blank"
            )
        if self.cas:
            # Mixtures legitimately carry several CAS numbers (e.g. spinosad
            # A+D, aflatoxin totals); each part must still be a valid CAS.
            parts = re.split(r"[;,]\s*", self.cas)
            if any(not part.replace("-", "").isdigit() for part in parts):
                problems.append(f"{self.analyte}: malformed CAS {self.cas!r}")
        return problems


@dataclass
class ProcessRule:
    """A non-numeric requirement: remediation, retesting, retention, COA, ..."""

    topic: str
    rule: str                       # jurisdiction-specific language
    citation: str = ""
    citation_url: str = ""
    notes: str = ""

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.topic.strip():
            problems.append("process rule topic is required")
        if not self.rule.strip():
            problems.append(f"{self.topic}: rule text is required")
        return problems


@dataclass
class SourceRef:
    """A source consulted while building this requirement set."""

    name: str
    url: str
    retrieved_at: str = ""
    kind: str = "primary"           # primary | secondary
    notes: str = ""

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.name.strip():
            problems.append("source name is required")
        if not self.url.startswith(("http://", "https://")):
            problems.append(f"{self.name}: url must be http(s)")
        return problems


@dataclass
class JurisdictionRequirements:
    """The full requirement set for one jurisdiction."""

    jurisdiction: str               # lowercase state key, e.g. "california"
    jurisdiction_label: str
    research_status: str
    updated_date: str
    regulator: str = ""
    regulator_url: str = ""
    governing_document: str = ""    # what sets the limits (reg title / protocol)
    legal_framework: list[LegalReference] = field(default_factory=list)
    panel: list[PanelRequirement] = field(default_factory=list)
    limits: list[LimitRecord] = field(default_factory=list)
    process_rules: list[ProcessRule] = field(default_factory=list)
    sources: list[SourceRef] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.jurisdiction.strip():
            problems.append("jurisdiction is required")
        if not self.updated_date:
            problems.append(f"{self.jurisdiction}: missing updated_date")
        for ref in self.legal_framework:
            problems.extend(ref.validate())
        for panel in self.panel:
            problems.extend(panel.validate())
        for limit in self.limits:
            problems.extend(limit.validate())
        for rule in self.process_rules:
            problems.extend(rule.validate())
        for source in self.sources:
            problems.extend(source.validate())
        return problems

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "jurisdiction": self.jurisdiction,
            "jurisdiction_label": self.jurisdiction_label,
            "research_status": self.research_status,
            "updated_date": self.updated_date,
            "regulator": self.regulator,
            "regulator_url": self.regulator_url,
            "governing_document": self.governing_document,
            "legal_framework": [r.__dict__ for r in self.legal_framework],
            "panel": [p.__dict__ for p in self.panel],
            "limits": [l.__dict__ for l in self.limits],
            "process_rules": [r.__dict__ for r in self.process_rules],
            "sources": [s.__dict__ for s in self.sources],
            "gaps": list(self.gaps),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JurisdictionRequirements":
        def _ref(item: dict) -> LegalReference:
            return LegalReference(**{k: item.get(k, "") for k in (
                "title", "citation", "url", "kind", "retrieved_at", "notes")})

        def _panel(item: dict) -> PanelRequirement:
            return PanelRequirement(**{k: item.get(k, "") for k in (
                "category", "required", "citation", "citation_url", "notes")})

        def _limit(item: dict) -> LimitRecord:
            return LimitRecord(**{k: item.get(k, "") for k in (
                "analyte", "category", "citation", "matrix", "cas", "limit",
                "unit", "comparison", "effective_date", "superseded_date",
                "value_status", "citation_url", "notes")})

        def _rule(item: dict) -> ProcessRule:
            return ProcessRule(**{k: item.get(k, "") for k in (
                "topic", "rule", "citation", "citation_url", "notes")})

        def _source(item: dict) -> SourceRef:
            return SourceRef(**{k: item.get(k, "") for k in (
                "name", "url", "retrieved_at", "kind", "notes")})

        return cls(
            jurisdiction=data.get("jurisdiction", ""),
            jurisdiction_label=data.get("jurisdiction_label", ""),
            research_status=data.get("research_status", ""),
            updated_date=data.get("updated_date", ""),
            regulator=data.get("regulator", ""),
            regulator_url=data.get("regulator_url", ""),
            governing_document=data.get("governing_document", ""),
            legal_framework=[_ref(i) for i in data.get("legal_framework", [])],
            panel=[_panel(i) for i in data.get("panel", [])],
            limits=[_limit(i) for i in data.get("limits", [])],
            process_rules=[_rule(i) for i in data.get("process_rules", [])],
            sources=[_source(i) for i in data.get("sources", [])],
            gaps=list(data.get("gaps", [])),
        )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def read_requirements(path: Path) -> JurisdictionRequirements:
    return JurisdictionRequirements.from_dict(
        json.loads(Path(path).read_text(encoding="utf-8"))
    )


def validate_requirements_file(path: Path) -> list[str]:
    return read_requirements(path).validate()


def today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_requirements_markdown(req: JurisdictionRequirements) -> str:
    """Human-readable requirement record body (no frontmatter)."""
    lines: list[str] = []
    lines.append(f"# {req.jurisdiction_label} Testing Requirements")
    lines.append("")
    lines.append(f"- Regulator: {_cell(req.regulator)}")
    lines.append(f"- Research status: {_cell(req.research_status)}")
    lines.append(f"- Updated: {req.updated_date}")
    if req.governing_document:
        lines.append(f"- Governing document: {_cell(req.governing_document)}")
    lines.append("")

    if req.legal_framework:
        lines.append("## Legal Framework")
        lines.append("")
        lines.append("| Document | Citation | Type | Source |")
        lines.append("| --- | --- | --- | --- |")
        for ref in sorted(req.legal_framework, key=lambda r: (r.kind, r.citation)):
            url = f"<{ref.url}>" if ref.url else "—"
            lines.append(
                f"| {_cell(ref.title)} | {_cell(ref.citation)} "
                f"| {ref.kind} | {url} |"
            )
        lines.append("")

    if req.panel:
        lines.append("## Required Testing Panel")
        lines.append("")
        lines.append("| Category | Required | Citation | Notes |")
        lines.append("| --- | --- | --- | --- |")
        for panel in req.panel:
            lines.append(
                f"| {panel.category} | {'yes' if panel.required else 'no'} "
                f"| {_cell(panel.citation)} | {_cell(panel.notes)} |"
            )
        lines.append("")

    categories = {}
    for limit in req.limits:
        categories.setdefault(limit.category, []).append(limit)

    for category in PANEL_CATEGORIES:
        limits = categories.get(category)
        if not limits:
            continue
        lines.append(f"## {category.replace('-', ' ').title()} Limits")
        lines.append("")
        lines.append(
            "| Analyte | CAS | Matrix | Limit | Unit | Comparison | "
            "Citation | Effective | Superseded | Status | Notes |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for limit in sorted(limits, key=lambda l: (l.analyte.lower(), l.matrix)):
            lines.append(
                f"| {_cell(limit.analyte)} | {limit.cas or '—'} "
                f"| {_cell(limit.matrix)} | {limit.limit or '—'} "
                f"| {limit.unit or '—'} | {limit.comparison} "
                f"| {_cell(limit.citation)} | {limit.effective_date or '—'} "
                f"| {limit.superseded_date or '—'} | {limit.value_status} "
                f"| {_cell(limit.notes)} |"
            )
        lines.append("")

    if req.process_rules:
        lines.append("## Process Requirements")
        lines.append("")
        lines.append("| Topic | Rule | Citation | Notes |")
        lines.append("| --- | --- | --- | --- |")
        for rule in req.process_rules:
            lines.append(
                f"| {_cell(rule.topic)} | {_cell(rule.rule)} "
                f"| {_cell(rule.citation)} | {_cell(rule.notes)} |"
            )
        lines.append("")

    if req.sources:
        lines.append("## Sources Consulted")
        lines.append("")
        lines.append("| Source | Kind | Retrieved | URL | Notes |")
        lines.append("| --- | --- | --- | --- | --- |")
        for source in req.sources:
            lines.append(
                f"| {_cell(source.name)} | {source.kind} "
                f"| {source.retrieved_at or '—'} | <{source.url}> | {_cell(source.notes)} |"
            )
        lines.append("")

    if req.gaps:
        lines.append("## Evidence Gaps")
        lines.append("")
        for gap in req.gaps:
            lines.append(f"- {gap}")
        lines.append("")

    return "\n".join(lines) + "\n"


__all__ = [
    "PANEL_CATEGORIES", "MATRICES", "VALUE_STATUSES",
    "LegalReference", "PanelRequirement", "LimitRecord", "ProcessRule",
    "SourceRef", "JurisdictionRequirements", "read_requirements",
    "validate_requirements_file", "render_requirements_markdown", "today_iso",
]
