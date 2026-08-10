#!/usr/bin/env python3
"""Deterministic evidence-aware crosslinking layer for Thermal Extraction Devices.

Relationships are data; links are presentation. This module is the derived
navigation layer on top of the existing content graph (Boris): it consumes the
same structured relationship sources the site already publishes and derives
bounded, labeled, deterministic navigation sections. It deliberately does not
reimplement the graph engine — Boris owns discovery, parent/nav validation,
and rendering. This layer only adds *presentation edges* (navigation) derived
from already-validated structured data.

Structured relationship sources
-------------------------------

1. **Frontmatter semantic relations** (``content/**`` ``relations:`` fields)
   — author-declared, Boris-validated, closed vocabulary
   (``relates_to`` / ``implements`` / ``depends_on`` / ``supersedes``).
2. **Cultivar identity claim registry** (``metadata/cultivar-claims.jsonl``)
   — typed identity/claim edges (``product_claims_cultivar``,
   ``batch_claims_cultivar``, ``claimed_lineage_parent``,
   ``claimed_bred_by``, …) with provenance.
3. **Durable COA records** (``metadata/coa-records.jsonl``, one
   ``CoaRecord`` per line per ``metadata/coa-measurement.schema.json``) —
   measurement edges: report -> laboratory, report -> batch,
   batch -> product, batch cultivar labels, report -> compound.

Edge classes
------------

Every generated link carries exactly one edge class (never mixed):

* ``direct`` — author-declared semantic relation (frontmatter ``relations``).
* ``source`` — provenance/attribution to a named non-entity (e.g. a breeder
  without an archive page), kept as text, never a link.
* ``measurement`` — a measurement edge from a COA record (tested_by,
  analyte_result, batch product, …).
* ``identity_claim`` — a claim-registry edge with an entity object.
* ``derived`` — reverse navigation or multi-hop projection with an evidence
  trace. Derived edges are presentation only: they never create a permanent
  factual assertion (e.g. "Cultivar contains Compound" is never emitted; the
  UI shows "Observed in associated reports" instead).

Determinism
-----------

All output is sorted (entities by id, sections by rule order, items by
evidence-count then id). No timestamps or host fields are emitted, so
regenerating over the same inputs produces byte-identical artifacts.

Scale
-----

Adjacency indexes are built once (O(E)); per-entity sections are O(1) lookups
plus bounded truncation. No page ever renders more than
``MAX_LINKS_PER_PAGE`` links; every section is capped at
``MAX_ITEMS_PER_SECTION`` with the full count reported, so hundreds of
thousands of measurements never explode a single HTML page.

Usage
-----

::

    # Build the machine-readable crosslink export only
    python3 scripts/crosslinks.py --out exports/crosslinks.json

    # Validate the derived graph (no HTML required)
    python3 scripts/crosslinks.py --check

    # Generate + inject labeled navigation into a rendered Boris site
    python3 scripts/crosslinks.py --html-dir dist/cantilever --inject

    # Emit the deterministic RAG companion document
    python3 scripts/crosslinks.py --rag exports/crosslinks-rag.md
"""

from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cultivar_claims import load_claims  # noqa: E402
from scripts.coa_model import (  # noqa: E402
    AnalyteMeasurement,
    Batch,
    CoaRecord,
    Laboratory,
    RecordKind,
    Report,
    ReportingBasis,
    ResultState,
    coa_problems,
)
from scripts.ingest.validation import collect_entity_ids  # noqa: E402

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

# Boris's closed semantic-relation vocabulary (frontmatter `relations:`).
DIRECT_RELATION_KINDS = frozenset({"relates_to", "implements", "depends_on", "supersedes"})

# Claim kinds that form entity-to-entity edges in the derived navigation.
CLAIM_ENTITY_KINDS = frozenset({
    "alias_of", "claimed_alias_of", "bred_by", "claimed_bred_by",
    "lineage_parent", "claimed_lineage_parent", "sold_by", "listed_by",
    "seed_source", "product_claims_cultivar", "batch_claims_cultivar",
    "possibly_same_as", "historically_associated_with",
})

# Five edge classes (the mission's minimum distinction set).
EDGE_CLASSES = ("direct", "source", "measurement", "identity_claim", "derived")

# Entity collections that hold compounds (analytes).
COMPOUND_COLLECTIONS = frozenset({"terpenes", "cannabinoids", "contaminants", "botanicals"})

# Entity collection -> semantic role used for relation-type validation.
COLLECTION_ROLE = {
    "affected-products": "affected_product",
    "botanicals": "compound",
    "cannabinoids": "compound",
    "changelog": "changelog",
    "contaminants": "compound",
    "cultivars": "cultivar",
    "datasets": "dataset",
    "devices": "device",
    "guides": "guide",
    "jurisdictions": "jurisdiction",
    "lab-results": "report",
    "law-and-use": "law",
    "licenses": "license",
    "manufacturers": "manufacturer",
    "organizations": "organization",
    "products": "product",
    "recalls": "recall",
    "reference": "reference",
    "releases": "release",
    "requirements": "requirement",
    "safety": "safety",
    "safety-advisories": "safety_advisory",
    "specs": "spec",
    "terpenes": "compound",
    "testing-laboratories": "laboratory",
}

# Rendering bounds (mission: no unbounded page expansion).
MAX_ITEMS_PER_SECTION = 8
MAX_LINKS_PER_PAGE = 48
MAX_TRACE_ITEMS = 3
# High-degree relationships (sections that exceed the display cap) get
# dedicated paginated index pages instead of an unbounded in-page list.
INDEX_PAGE_SIZE = 100

# Section labels: "Observed in associated reports" wording that must never be
# read as a universal cultivar-chemistry assertion.
OBSERVED_COMPOUNDS_LABEL = "Compounds observed in associated reports"
OBSERVED_CULTIVARS_LABEL = "Cultivars observed in associated reports"
OBSERVED_COMPOUNDS_NOTE = (
    "These observations are batch- and report-attached; they do not assert "
    "that a cultivar name implies a fixed chemistry."
)

FRONTMATTER_RELATION_RE = re.compile(r"^relations:\s*\[(.*)\]$", flags=re.M)
RELATION_ENTRY_RE = re.compile(r"^\s*([A-Za-z_]+)\s*=\s*([^\s,\]]+)\s*$")

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Entity:
    """One content entity (page) from the ID registry."""

    id: str
    title: str
    source: str
    collection: str
    parent: Optional[str]
    role: str

    @property
    def output_path(self) -> str:
        """Rendered HTML path under the dist root.

        Boris publishes pages by entity id, not source filename: satellites
        render to ``<collection>/<FORM-ID>.html`` and trunks to
        ``<id>.html`` (``index.html`` for the root page). Verified against a
        full build: the id-based set exactly equals the emitted HTML tree.
        """
        if "/" in self.id:
            form = self.id.split("/", 1)[1]
            return f"{self.collection}/{form}.html"
        return f"{self.id}.html"


@dataclass(frozen=True)
class Edge:
    """One typed, classified edge in the derived navigation graph."""

    from_id: str
    to_id: str
    kind: str
    edge_class: str
    provenance: tuple[str, ...] = ()
    trace: tuple[str, ...] = ()
    record_kinds: tuple[str, ...] = ()
    note: str = ""


@dataclass
class Section:
    """A derived navigation section for one entity page.

    ``count`` is the full reproducible count from the graph data; ``items``
    is the bounded display list, so a page never renders 20,000 backlinks
    while still reporting the honest total. ``all_items`` is the full rule
    result, used only to materialize dedicated index pages (paginated) when
    ``count`` exceeds the display cap; it is never serialized.
    """

    key: str
    label: str
    edge_class: str
    source_class: str
    count: int = 0
    items: list[dict[str, Any]] = field(default_factory=list)
    all_items: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "edgeClass": self.edge_class,
            "sourceClass": self.source_class,
            "count": self.count,
            "items": self.items,
        }


@dataclass
class CrosslinkGraph:
    """Indexes built once, then queried per entity."""

    entities: dict[str, Entity] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    outgoing: dict[str, list[Edge]] = field(default_factory=dict)
    incoming: dict[str, list[Edge]] = field(default_factory=dict)
    # Batch ids per report (non-entity provenance for report pages).
    report_batches: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Non-entity attributions (source class): subject id -> notes. These are
    # provenance, never links, so they never create a navigation edge.
    source_notes: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def add(self, edge: Edge) -> None:
        self.edges.append(edge)
        self.outgoing.setdefault(edge.from_id, []).append(edge)
        self.incoming.setdefault(edge.to_id, []).append(edge)

    def add_source_note(self, subject: str, note: dict[str, Any]) -> None:
        self.source_notes.setdefault(subject, []).append(note)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_entities(map_path: Path) -> dict[str, Entity]:
    """Load the entity registry (``metadata/id-map.jsonl``)."""
    entities: dict[str, Entity] = {}
    if not map_path.exists():
        return entities
    for line_no, line in enumerate(map_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{map_path}:{line_no}: invalid JSON: {error}") from error
        entity_id = item.get("id")
        if not entity_id:
            continue
        collection = str(item.get("collection") or "")
        if "/" in str(entity_id):
            parts = str(entity_id).split("/", 1)
            collection = collection or parts[0]
        entities[str(entity_id)] = Entity(
            id=str(entity_id),
            title=str(item.get("title") or entity_id),
            source=str(item.get("source") or ""),
            collection=collection,
            parent=item.get("parent"),
            role=str(item.get("role") or "satellite"),
        )
    return entities


def parse_frontmatter_relations(text: str, source: str) -> list[tuple[str, str, str]]:
    """Parse a Boris ``relations:`` line into (from, to, kind) triples.

    Follows the documented Boris grammar: a single ``relations`` key whose
    value is ``[kind=target, ...]`` with the closed kind vocabulary. The
    entity id (``from``) is read from the same frontmatter.
    """
    id_match = re.search(r"^id:\s*(.+)$", text, flags=re.M)
    if not id_match:
        return []
    from_id = id_match.group(1).strip().strip('"')
    match = FRONTMATTER_RELATION_RE.search(text)
    if not match:
        return []
    relations: list[tuple[str, str, str]] = []
    for raw in match.group(1).split(","):
        entry = RELATION_ENTRY_RE.match(raw)
        if not entry:
            if not raw.strip():
                continue  # empty list ("relations: []") is valid
            raise ValueError(
                f"{source}: malformed relations entry {raw.strip()!r}; "
                "expected kind=entity-id"
            )
        kind, target = entry.groups()
        if kind not in DIRECT_RELATION_KINDS:
            raise ValueError(
                f"{source}: unknown relation kind {kind!r}; allowed: "
                + ", ".join(sorted(DIRECT_RELATION_KINDS))
            )
        relations.append((from_id, target, kind))
    return relations


def load_direct_edges(content_root: Path) -> list[Edge]:
    """Load author-declared semantic relations as ``direct`` edges."""
    edges: list[Edge] = []
    for path in sorted(content_root.rglob("*.md")):
        rel = path.relative_to(content_root)
        parts = rel.parts
        if not parts:
            continue
        if parts[0] in ("includes", "_includes") or path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for from_id, to_id, kind in parse_frontmatter_relations(text, rel.as_posix()):
            edges.append(Edge(
                from_id=from_id, to_id=to_id, kind=kind,
                edge_class="direct", provenance=(rel.as_posix(),),
            ))
    return edges


def coa_record_from_dict(data: dict[str, Any]) -> CoaRecord:
    """Reconstruct a validated :class:`CoaRecord` from a JSON dict.

    Raises ``ValueError`` with the model's hard-validation problems when the
    record violates ``scripts/coa_model.coa_problems``.
    """
    report_data = data.get("report") or {}
    lab_data = report_data.get("laboratory")
    laboratory = (
        Laboratory(
            name=str(lab_data.get("name") or ""),
            lab_id=lab_data.get("lab_id"),
            license_number=str(lab_data.get("license_number") or ""),
            jurisdiction=str(lab_data.get("jurisdiction") or ""),
        )
        if lab_data is not None
        else None
    )
    report = Report(
        report_id=str(report_data.get("report_id") or ""),
        revision=int(report_data.get("revision") or 1),
        supersedes=report_data.get("supersedes"),
        source_reference=str(report_data.get("source_reference") or ""),
        report_date=report_data.get("report_date"),
        test_date=report_data.get("test_date"),
        sample_date=report_data.get("sample_date"),
        laboratory=laboratory,
        jurisdiction=str(report_data.get("jurisdiction") or ""),
    )
    batch_data = data.get("batch") or {}
    def _enum(member: Any, values: Any, fallback: Any) -> Any:
        if isinstance(member, values):
            return member
        try:
            return values(member)
        except ValueError:
            return fallback

    batch = Batch(
        batch_id=str(batch_data.get("batch_id") or ""),
        metrc_tag=str(batch_data.get("metrc_tag") or ""),
        producer_id=batch_data.get("producer_id"),
        product_id=batch_data.get("product_id"),
        cultivar_labels=tuple(batch_data.get("cultivar_labels") or ()),
        sample_type=str(batch_data.get("sample_type") or "unknown"),
        matrix_detail=str(batch_data.get("matrix_detail") or ""),
        basis=_enum(batch_data.get("basis"), ReportingBasis, ReportingBasis.UNKNOWN),
        record_kind=_enum(batch_data.get("record_kind"), RecordKind, RecordKind.UNVERIFIED),
        jurisdiction=str(batch_data.get("jurisdiction") or ""),
        harvest_date=batch_data.get("harvest_date"),
    )
    measurements: list[AnalyteMeasurement] = []
    for measurement in data.get("measurements") or ():
        measurements.append(AnalyteMeasurement(
            compound_id=measurement.get("compound_id"),
            compound_name=str(measurement.get("compound_name") or ""),
            compound_cas=measurement.get("compound_cas"),
            reported_value=str(measurement.get("reported_value") or ""),
            reported_unit=str(measurement.get("reported_unit") or ""),
            state=_enum(measurement.get("state"), ResultState, ResultState.MISSING),
            value=measurement.get("value"),
            unit=str(measurement.get("unit") or ""),
            lod=measurement.get("lod"),
            loq=measurement.get("loq"),
            test_date=measurement.get("test_date"),
            quantitation_note=measurement.get("quantitation_note"),
        ))
    record = CoaRecord(report=report, batch=batch, measurements=tuple(measurements))
    problems = coa_problems(record)
    if problems:
        raise ValueError(
            f"COA record {report.report_id!r} is invalid: " + "; ".join(problems)
        )
    return record


def load_coa_records(coa_path: Path) -> list[CoaRecord]:
    """Load and validate durable COA records (empty file == no records)."""
    records: list[CoaRecord] = []
    if not coa_path.exists():
        return records
    for line_no, line in enumerate(coa_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{coa_path}:{line_no}: invalid JSON: {error}") from error
        records.append(coa_record_from_dict(data))
    return records


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def _entity_collection(entity_id: str, entities: dict[str, Entity]) -> str:
    entity = entities.get(entity_id)
    if entity is not None:
        return entity.collection
    return entity_id.split("/", 1)[0] if "/" in entity_id else entity_id


def build_graph(
    content_root: Path,
    entities: dict[str, Entity],
    claims: Iterable[dict[str, Any]],
    coa_records: Iterable[CoaRecord],
) -> CrosslinkGraph:
    """Build the typed, classified navigation graph.

    Forward edges carry their real class (direct / identity_claim /
    measurement / source). Reverse and multi-hop navigation edges are always
    class ``derived`` and carry the evidence trace that justifies them, so a
    derived link can never be mistaken for a primary factual assertion.
    """
    graph = CrosslinkGraph(entities=entities)

    for edge in load_direct_edges(content_root):
        graph.add(edge)

    # --- claim registry edges ---------------------------------------------
    claim_edges: list[Edge] = []
    for claim in claims:
        kind = claim.get("kind")
        subject = claim.get("subject")
        obj = claim.get("object")
        object_is_entity = claim.get("object_is_entity") is True
        if not subject or not obj:
            continue
        if kind == "source_disagrees_with":
            continue
        provenance = (
            f"claim:{claim.get('claim_id', '')}",
            f"status:{claim.get('status', '')}",
            f"source:{str((claim.get('source') or {}).get('name') or '')}",
        )
        if object_is_entity:
            edge = Edge(
                from_id=str(subject), to_id=str(obj), kind=str(kind),
                edge_class="identity_claim", provenance=provenance,
            )
            graph.add(edge)
            claim_edges.append(edge)
        else:
            # Non-entity attribution: kept as a source-class note so the
            # derived navigation can name e.g. a breeder without inventing a
            # link to a nonexistent page. Never a navigation edge.
            graph.add_source_note(str(subject), {
                "kind": str(kind),
                "object": str(obj),
                "claim_id": claim.get("claim_id"),
                "status": claim.get("status"),
                "source": (claim.get("source") or {}).get("name") or "",
            })

    # --- COA measurement edges --------------------------------------------
    compound_edges: list[Edge] = []       # report -> compound
    report_lab_edges: list[Edge] = []     # report -> laboratory
    report_product_edges: list[Edge] = []  # report -> product (via batch)
    for record in coa_records:
        record_kind = record.batch.record_kind.value
        report_id = record.report.report_id
        provenance = (f"coa:{report_id}", f"record_kind:{record_kind}")
        graph.report_batches[report_id] = {
            "batch_id": record.batch.batch_id,
            "metrc_tag": record.batch.metrc_tag,
            "cultivar_labels": list(record.batch.cultivar_labels),
            "record_kind": record_kind,
        }

        if record.report.laboratory is not None and record.report.laboratory.lab_id:
            lab_id = record.report.laboratory.lab_id
            graph.add(Edge(
                from_id=report_id, to_id=lab_id, kind="tested_by",
                edge_class="measurement", provenance=provenance,
                record_kinds=(record_kind,),
            ))
            report_lab_edges.append(Edge(
                from_id=report_id, to_id=lab_id, kind="tested_by",
                edge_class="measurement", provenance=provenance,
                record_kinds=(record_kind,),
            ))

        if record.batch.product_id:
            graph.add(Edge(
                from_id=report_id, to_id=record.batch.product_id,
                kind="product_of", edge_class="measurement",
                provenance=provenance, record_kinds=(record_kind,),
            ))
            report_product_edges.append(Edge(
                from_id=report_id, to_id=record.batch.product_id,
                kind="product_of", edge_class="measurement",
                provenance=provenance, record_kinds=(record_kind,),
            ))

        for measurement in record.measurements:
            compound_id = measurement.compound_id
            if not compound_id:
                continue
            edge = Edge(
                from_id=report_id, to_id=compound_id, kind="analyte_result",
                edge_class="measurement", provenance=provenance,
                record_kinds=(record_kind,),
                note=measurement.compound_name,
            )
            graph.add(edge)
            compound_edges.append(edge)

    # --- derived: reverse navigation -------------------------------------
    # Reverse of every forward edge is navigation-only (class derived). The
    # record kinds ride along so demo/unverified records stay visibly labeled.
    for edge in list(graph.edges):
        if edge.from_id == edge.to_id:
            continue
        reverse_kind = _reverse_kind(edge.kind)
        if edge.edge_class in ("direct", "identity_claim", "measurement"):
            graph.add(Edge(
                from_id=edge.to_id, to_id=edge.from_id,
                kind=reverse_kind, edge_class="derived",
                provenance=edge.provenance, trace=(edge.from_id,),
                record_kinds=edge.record_kinds,
            ))

    # --- derived: multi-hop projections with traces ------------------------
    # Cultivar -> compounds / compound -> cultivars, via reports. The trace is
    # the set of reports that measured the compound in a batch carrying the
    # cultivar label; the derived edge is *never* emitted as a factual claim.
    cultivar_reports: dict[str, set[str]] = {}
    for edge in claim_edges:
        if edge.kind == "batch_claims_cultivar" and _entity_collection(edge.to_id, entities) == "cultivars":
            cultivar_reports.setdefault(edge.to_id, set()).add(edge.from_id)

    compound_reports: dict[str, set[str]] = {}
    for edge in compound_edges:
        compound_reports.setdefault(edge.to_id, set()).add(edge.from_id)

    product_reports: dict[str, set[str]] = {}
    for edge in report_product_edges:
        product_reports.setdefault(edge.to_id, set()).add(edge.from_id)

    cultivar_compounds: dict[str, set[str]] = {}
    for cultivar, reports in cultivar_reports.items():
        for report in reports:
            for edge in compound_edges:
                if edge.from_id == report:
                    cultivar_compounds.setdefault(cultivar, set()).add(edge.to_id)
    for cultivar, compounds in sorted(cultivar_compounds.items()):
        for compound in sorted(compounds):
            reports = sorted(
                report for report in cultivar_reports[cultivar]
                if any(e.from_id == report and e.to_id == compound for e in compound_edges)
            )
            record_kinds = _record_kinds_for_reports(reports, compound_edges)
            graph.add(Edge(
                from_id=cultivar, to_id=compound, kind="observed_in_reports",
                edge_class="derived", trace=tuple(reports),
                record_kinds=record_kinds,
            ))
            graph.add(Edge(
                from_id=compound, to_id=cultivar, kind="reported_in_cultivars",
                edge_class="derived", trace=tuple(reports),
                record_kinds=record_kinds,
            ))

    # Product -> compounds (via reports), and the reverse for compound pages.
    product_compounds: dict[str, set[str]] = {}
    for product, reports in product_reports.items():
        for report in reports:
            for edge in compound_edges:
                if edge.from_id == report:
                    product_compounds.setdefault(product, set()).add(edge.to_id)
    for product, compounds in sorted(product_compounds.items()):
        for compound in sorted(compounds):
            reports = sorted(
                report for report in product_reports[product]
                if any(e.from_id == report and e.to_id == compound for e in compound_edges)
            )
            record_kinds = _record_kinds_for_reports(reports, compound_edges)
            graph.add(Edge(
                from_id=product, to_id=compound, kind="observed_in_reports",
                edge_class="derived", trace=tuple(reports),
                record_kinds=record_kinds,
            ))
            graph.add(Edge(
                from_id=compound, to_id=product, kind="reported_in_products",
                edge_class="derived", trace=tuple(reports),
                record_kinds=record_kinds,
            ))

    return graph


def _record_kinds_for_reports(reports: Iterable[str], compound_edges: list[Edge]) -> tuple[str, ...]:
    """Union of record kinds across the reports that justify a projection."""
    kinds: list[str] = []
    for edge in compound_edges:
        if edge.from_id in set(reports):
            for kind in edge.record_kinds:
                if kind not in kinds:
                    kinds.append(kind)
    return tuple(sorted(kinds))


def _reverse_kind(kind: str) -> str:
    """Deterministic reverse-edge kind name (navigation only)."""
    return {
        "relates_to": "related_to",
        "implements": "implemented_by",
        "depends_on": "dependency_of",
        "supersedes": "superseded_by",
        "tested_by": "issued",
        "analyte_result": "measured_in",
        "product_of": "reported_in",
        "product_claims_cultivar": "claims_cultivar",
        "batch_claims_cultivar": "claims_cultivar",
        "claimed_lineage_parent": "parent_of",
        "claimed_bred_by": "bred",
        "listed_by": "listed",
        "sold_by": "sold",
    }.get(kind, f"reverse_{kind}")


# ---------------------------------------------------------------------------
# Section derivation (context-appropriate rendering rules)
# ---------------------------------------------------------------------------


def _role(entity_id: str, graph: CrosslinkGraph) -> str:
    collection = _entity_collection(entity_id, graph.entities)
    return COLLECTION_ROLE.get(collection, collection)


def _collect_items(
    edges: Iterable[Edge],
    graph: CrosslinkGraph,
    *,
    incoming: bool = False,
    kinds: Optional[Iterable[str]] = None,
    classes: Optional[Iterable[str]] = None,
) -> list[dict[str, Any]]:
    """Materialize edge endpoints as deterministic section items.

    ``incoming`` selects the *other* endpoint (the page that links here) as
    the item. ``kinds`` / ``classes`` filter edges *before* deduplication so
    the strongest class wins for an entity that is both measured and related.
    Items are sorted by evidence weight (trace length) then entity id, so the
    ordering is stable and reproducible from graph data alone.
    """
    kinds = set(kinds) if kinds is not None else None
    classes = set(classes) if classes is not None else None
    seen: dict[str, dict[str, Any]] = {}
    for edge in edges:
        if kinds is not None and edge.kind not in kinds:
            continue
        if classes is not None and edge.edge_class not in classes:
            continue
        entity_id = edge.from_id if incoming else edge.to_id
        entity = graph.entities.get(entity_id)
        if entity is None:
            continue
        item = seen.setdefault(entity_id, {
            "id": entity_id,
            "title": entity.title,
            "trace": [],
            "recordKinds": [],
            "kind": edge.kind,
            "edgeClass": edge.edge_class,
        })
        item["trace"] = sorted(set(list(item["trace"]) + list(edge.trace)))[:MAX_TRACE_ITEMS]
        for kind in edge.record_kinds:
            if kind not in item["recordKinds"]:
                item["recordKinds"].append(kind)
    return sorted(seen.values(), key=lambda item: (-len(item["trace"]), item["id"]))


def _backlink_items(entity_id: str, graph: CrosslinkGraph) -> list[dict[str, Any]]:
    """Incoming direct relations, reversed into full navigation items."""
    return _collect_items(
        graph.incoming.get(entity_id, []), graph,
        incoming=True, classes=("direct",),
    )


def _outgoing_direct_items(entity_id: str, graph: CrosslinkGraph) -> list[dict[str, Any]]:
    """Author-declared direct relation targets, as full navigation items."""
    return _collect_items(
        graph.outgoing.get(entity_id, []), graph, classes=("direct",),
    )


def _append_source_notes(
    items: list[dict[str, Any]],
    graph: CrosslinkGraph,
    entity_id: str,
    kinds: Iterable[str],
) -> None:
    """Append non-entity attributions (source class) as text-only items."""
    wanted = set(kinds)
    seen = {item["id"] for item in items}
    for note in graph.source_notes.get(entity_id, []):
        if note.get("kind") not in wanted:
            continue
        item_id = f"source:{note.get('claim_id') or note.get('object')}"
        if item_id in seen:
            continue
        seen.add(item_id)
        items.append({
            "id": item_id,
            "title": note.get("object") or "",
            "kind": note.get("kind") or "",
            "edgeClass": "source",
            "trace": [],
            "recordKinds": [],
            "note": note.get("source") or "",
        })


def sections_for(entity_id: str, graph: CrosslinkGraph) -> list[Section]:
    """Compute the ordered, context-appropriate sections for one entity page.

    Items are claimed by the first matching rule so a page never shows the
    same target twice. ``related`` / ``backlinks`` catch the remainder.
    """
    role = _role(entity_id, graph)
    claimed: set[str] = set()

    def claim(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        fresh = [item for item in items if item["id"] not in claimed]
        for item in fresh:
            claimed.add(item["id"])
        return fresh

    sections: list[Section] = []

    def add_section(key: str, label: str, edge_class: str, source_class: str,
                    full: list[dict[str, Any]]) -> None:
        """Register one section from its full rule result.

        Role filters (if any) are applied by the caller to ``full`` before
        this point so the count always matches the shown + indexed set. The
        display list is the top ``MAX_ITEMS_PER_SECTION`` items after the
        cross-section dedupe; ``all_items`` retains the full set for index
        pages.
        """
        display = claim(full[:MAX_ITEMS_PER_SECTION])
        if display:
            sections.append(Section(
                key=key, label=label, edge_class=edge_class,
                source_class=source_class,
                count=len(full), items=display, all_items=full,
            ))

    def rule_items(edges: Iterable[Edge], *, incoming: bool = False,
                   kinds: Optional[Iterable[str]] = None,
                   classes: Optional[Iterable[str]] = None,
                   role_filter: Optional[Callable[[str], bool]] = None,
                   ) -> list[dict[str, Any]]:
        """Full (unbounded) rule result for one section rule."""
        full = _collect_items(
            edges, graph, incoming=incoming, kinds=kinds, classes=classes,
        )
        if role_filter is not None:
            full = [item for item in full if role_filter(item["id"])]
        return full

    incoming = graph.incoming.get(entity_id, [])
    outgoing = graph.outgoing.get(entity_id, [])
    is_product = lambda item_id: _role(item_id, graph) == "product"  # noqa: E731
    is_cultivar = lambda item_id: _role(item_id, graph) == "cultivar"  # noqa: E731
    is_report = lambda item_id: _role(item_id, graph) == "report"  # noqa: E731

    if role == "compound":
        # compound -> report (reverse of report --analyte_result--> compound)
        add_section("measured_reports",
                    "Laboratory reports measuring this compound",
                    "derived", "measurement",
                    rule_items(outgoing, kinds=("measured_in",)))
        # compound <- product / cultivar (multi-hop projection)
        add_section("products", "Products with measurements",
                    "derived", "measurement",
                    rule_items(incoming, incoming=True,
                               kinds=("observed_in_reports",), role_filter=is_product))
        add_section("observed_cultivars", OBSERVED_CULTIVARS_LABEL,
                    "derived", "measurement",
                    rule_items(incoming, incoming=True,
                               kinds=("observed_in_reports",), role_filter=is_cultivar))
        botanical = rule_items(
            outgoing, classes=("direct",),
            role_filter=lambda item_id: (
                _entity_collection(item_id, graph.entities) == "botanicals"
            ),
        )
        add_section("botanical_occurrence", "Botanical occurrence",
                    "direct", "direct", botanical)

    elif role == "cultivar":
        add_section("lineage", "Lineage", "identity_claim", "identity_claim",
                    rule_items(outgoing, kinds=("claimed_lineage_parent", "lineage_parent")))
        breeders = rule_items(outgoing, kinds=("claimed_bred_by", "bred_by", "seed_source"))
        _append_source_notes(breeders, graph, entity_id,
                             ("claimed_bred_by", "bred_by", "seed_source"))
        add_section("breeders", "Breeder / origin claims",
                    "identity_claim", "identity_claim", breeders)
        listings = rule_items(outgoing, kinds=("listed_by", "sold_by"))
        _append_source_notes(listings, graph, entity_id, ("listed_by", "sold_by"))
        add_section("seed_listings", "Seed / catalog listings",
                    "identity_claim", "identity_claim", listings)
        add_section("aliases", "Aliases & identity",
                    "identity_claim", "identity_claim",
                    rule_items(outgoing, kinds=("alias_of", "claimed_alias_of", "possibly_same_as")))
        add_section("products", "Products carrying this name",
                    "derived", "identity_claim",
                    rule_items(outgoing, kinds=("claims_cultivar",), role_filter=is_product))
        add_section("reports", "Batch-associated laboratory reports",
                    "derived", "identity_claim",
                    rule_items(outgoing, kinds=("claims_cultivar",), role_filter=is_report))
        add_section("observed_compounds", OBSERVED_COMPOUNDS_LABEL,
                    "derived", "measurement",
                    rule_items(outgoing, kinds=("observed_in_reports",)))

    elif role == "product":
        add_section("cultivar_claims", "Cultivar claim",
                    "identity_claim", "identity_claim",
                    rule_items(outgoing, kinds=("product_claims_cultivar", "batch_claims_cultivar")))
        add_section("reports", "Laboratory reports",
                    "derived", "measurement",
                    rule_items(outgoing, kinds=("reported_in",)))
        add_section("observed_compounds", OBSERVED_COMPOUNDS_LABEL,
                    "derived", "measurement",
                    rule_items(outgoing, kinds=("observed_in_reports",)))

    elif role == "laboratory":
        add_section("reports", "Reports issued",
                    "derived", "measurement",
                    rule_items(outgoing, kinds=("issued",)))

    elif role == "report":
        add_section("laboratory", "Testing laboratory",
                    "measurement", "measurement",
                    rule_items(outgoing, kinds=("tested_by",)))
        batch_info = graph.report_batches.get(entity_id)
        if batch_info is not None:
            add_section("batch", "Batch", "measurement", "measurement", [{
                "id": f"batch:{batch_info['batch_id']}",
                "title": batch_info["batch_id"],
                "kind": "batch",
                "edgeClass": "measurement",
                "trace": [],
                "recordKinds": [batch_info["record_kind"]],
                "metrcTag": batch_info.get("metrc_tag") or "",
                "cultivarLabels": batch_info.get("cultivar_labels") or [],
            }])
        add_section("product", "Product", "measurement", "measurement",
                    rule_items(outgoing, kinds=("product_of",)))
        add_section("cultivar", "Cultivar claim",
                    "identity_claim", "identity_claim",
                    rule_items(outgoing, kinds=("batch_claims_cultivar",)))
        add_section("compounds", "Measured compounds",
                    "measurement", "measurement",
                    rule_items(outgoing, kinds=("analyte_result",)))

    related = _outgoing_direct_items(entity_id, graph)
    add_section("related", "Related", "direct", "direct", related)
    backlinks = _backlink_items(entity_id, graph)
    add_section("backlinks", "Pages that link here",
                "derived", "direct", backlinks)

    return sections


# ---------------------------------------------------------------------------
# Machine export
# ---------------------------------------------------------------------------


def export_json(graph: CrosslinkGraph) -> dict[str, Any]:
    """Deterministic machine representation of the derived navigation.

    Every section and item carries its edge class, its source class, and the
    evidence trace, so RAG / IR consumers can distinguish direct facts, source
    claims, measured observations, and derived associations without re-deriving
    anything.
    """
    entities_out: list[dict[str, Any]] = []
    for entity_id in sorted(graph.entities):
        entity = graph.entities[entity_id]
        sections_out: list[dict[str, Any]] = []
        for section in sections_for(entity_id, graph):
            data = section.to_dict()
            if section.count > MAX_ITEMS_PER_SECTION:
                data["index"] = {
                    "url": index_page_path(entity, section.key),
                    "pages": index_page_count(section.count),
                }
            sections_out.append(data)
        if not sections_out:
            continue
        entities_out.append({
            "id": entity_id,
            "title": entity.title,
            "collection": entity.collection,
            "role": entity.role,
            "sections": sections_out,
        })

    edge_class_counts: dict[str, int] = {}
    for edge in graph.edges:
        edge_class_counts[edge.edge_class] = edge_class_counts.get(edge.edge_class, 0) + 1

    return {
        "schemaVersion": "1.0",
        "description": (
            "Deterministic evidence-aware crosslinks derived from structured "
            "relationships (frontmatter relations, cultivar-claim registry, "
            "durable COA records). Derived edges are navigation only."
        ),
        "edgeClassCounts": dict(sorted(edge_class_counts.items())),
        "entityCount": len(entities_out),
        "entities": entities_out,
    }


def render_rag_document(graph: CrosslinkGraph) -> str:
    """Deterministic RAG companion: derived associations with epistemic wording.

    Generated sentences never strengthen uncertain relations: a cultivar page
    does not say "Blue Dream contains myrcene"; it says the compound "appears
    in laboratory reports associated with products labeled Blue Dream".
    """
    lines = [
        "# Crosslink & derived-navigation guide (RAG companion)",
        "",
        "Machine consumers should prefer `exports/crosslinks.json`; this file "
        "is the human-readable wording of the same derived edges. Every "
        "statement below is a **derived navigation association**, not a "
        "primary factual assertion. Five edge classes exist: `direct` "
        "(author-declared relation), `source` (attribution to a named "
        "non-entity), `measurement` (COA measurement edge), `identity_claim` "
        "(claim registry with an entity object), `derived` (reverse or "
        "multi-hop navigation with an evidence trace).",
        "",
    ]
    for entity_id in sorted(graph.entities):
        sections = sections_for(entity_id, graph)
        if not sections:
            continue
        entity = graph.entities[entity_id]
        lines.append(f"## {entity.title} (`{entity_id}`)")
        for section in sections:
            lines.append(f"### {section.label} (edge class: {section.edge_class})")
            for item in section.items:
                trace = ", ".join(item["trace"]) or "no trace"
                lines.append(
                    f"- [{item['title']}]({item['id']}) — derived from: {trace}"
                )
            if section.count > MAX_ITEMS_PER_SECTION:
                lines.append(
                    f"- Full list ({section.count} items, "
                    f"{index_page_count(section.count)} page(s)): "
                    f"`{index_page_path(entity, section.key)}`"
                )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# HTML injection
# ---------------------------------------------------------------------------


def _relative_link(from_path: str, to_path: str) -> str:
    """Relative URL from one rendered page to another (POSIX)."""
    return posixpath.relpath(to_path, posixpath.dirname(from_path))


def _escape(text: Any) -> str:
    return html.escape(str(text), quote=True)


def _item_html(item: dict[str, Any], from_output: str, graph: CrosslinkGraph,
               limit: int = MAX_ITEMS_PER_SECTION) -> str:
    target = graph.entities.get(item["id"])
    if target is None:
        # Non-entity item (e.g. a batch identifier): render as labeled text.
        badges = "".join(
            f' <span class="crosslinks__badge" data-record-kind="{_escape(kind)}">{_escape(kind)}</span>'
            for kind in item.get("recordKinds", [])
        )
        labels = "".join(
            f' <span class="crosslinks__badge">{_escape(label)}</span>'
            for label in item.get("cultivarLabels", [])
        )
        return (
            f'<li data-entity-id="{_escape(item["id"])}" '
            f'data-edge-class="{_escape(item["edgeClass"])}">'
            f'<span class="crosslinks__nonentity">{_escape(item["title"])}</span>'
            f'{labels}{badges}</li>'
        )
    href = _relative_link(from_output, target.output_path)
    badges = "".join(
        f' <span class="crosslinks__badge" data-record-kind="{_escape(kind)}">{_escape(kind)}</span>'
        for kind in item.get("recordKinds", [])
    )
    trace = item.get("trace") or []
    trace_html = ""
    if trace:
        trace_ids = ", ".join(_escape(t) for t in trace)
        trace_html = (
            f' <span class="crosslinks__trace" title="Evidence: {trace_ids}">'
            f"via {_escape(len(trace))} record(s)</span>"
        )
    return (
        f'<li data-entity-id="{_escape(item["id"])}" '
        f'data-edge-class="{_escape(item["edgeClass"])}">'
        f'<a href="{_escape(href)}">{_escape(item["title"])}</a>{badges}{trace_html}</li>'
    )


def render_sections_html(entity_id: str, graph: CrosslinkGraph) -> str:
    """Render the labeled, bounded crosslink section block for one page."""
    entity = graph.entities[entity_id]
    from_output = entity.output_path
    sections = sections_for(entity_id, graph)
    if not sections:
        return ""

    blocks = [f'<section class="crosslinks" data-crosslinks="1" aria-label="Related navigation">']
    blocks.append(
        '<p class="crosslinks__note">Derived navigation generated from structured '
        'relationships. Links are labeled by edge class and evidence trace; '
        'derived links are navigation, not primary assertions.</p>'
    )
    link_count = 0
    for section in sections:
        shown = section.items[:MAX_ITEMS_PER_SECTION]
        link_count += len(shown)
        if link_count > MAX_LINKS_PER_PAGE:
            shown = shown[: max(0, MAX_LINKS_PER_PAGE - (link_count - len(shown)))]
        total = section.count
        # High-degree sections link to a dedicated paginated index page
        # instead of dumping every item (or a bare "+N more") on this page.
        if total > MAX_ITEMS_PER_SECTION:
            index_rel = index_page_path(entity, section.key)
            more = (
                f' <a class="crosslinks__more" '
                f'href="{_escape(_relative_link(from_output, index_rel))}">'
                f'View all {total}</a>'
            )
        else:
            more = ""
        note = ""
        if section.key == "observed_compounds":
            note = f' <span class="crosslinks__note">{_escape(OBSERVED_COMPOUNDS_NOTE)}</span>'
        blocks.append(
            f'<section class="crosslinks__section" '
            f'data-section="{_escape(section.key)}" '
            f'data-edge-class="{_escape(section.edge_class)}" '
            f'data-source-class="{_escape(section.source_class)}">'
            f'<h3>{_escape(section.label)} '
            f'<span class="crosslinks__count">({total})</span>{more}</h3>'
            f'{note}'
            f'<ul>{"" .join(_item_html(item, from_output, graph) for item in shown)}</ul>'
            f'</section>'
        )
    blocks.append("</section>")
    return "\n".join(blocks)


def inject_html(html_text: str, block: str) -> str:
    """Insert (or replace) the crosslink block before ``</article>``.

    Idempotent: an existing ``data-crosslinks`` section is replaced, so
    re-running injection over an already-injected page is safe.
    """
    # The block's closing </section> is the one immediately followed by
    # </article> / </main> / end-of-file — never an inner section's close tag.
    pattern = re.compile(
        r'<section class="crosslinks" data-crosslinks="1".*?</section>\s*'
        r'(?=</article>|</main>|\Z)',
        flags=re.S,
    )
    if pattern.search(html_text):
        html_text = pattern.sub("", html_text, count=1)
    marker = "</article>"
    if marker in html_text:
        return html_text.replace(marker, block + "\n" + marker, 1)
    marker = "</main>"
    if marker in html_text:
        return html_text.replace(marker, block + "\n" + marker, 1)
    return html_text + "\n" + block


def inject_all(html_root: Path, graph: CrosslinkGraph) -> int:
    """Inject derived navigation into every rendered entity page.

    Returns the number of pages modified. Skips non-entity pages and the
    Boris system directory (``_boris``).
    """
    output_to_entity: dict[str, str] = {}
    for candidate_id, entity in graph.entities.items():
        output_to_entity.setdefault(entity.output_path, candidate_id)
    modified = 0
    for path in sorted(html_root.rglob("*.html")):
        rel = path.relative_to(html_root)
        if rel.parts and rel.parts[0] == "_boris":
            continue
        entity_id = output_to_entity.get(rel.as_posix())
        if entity_id is None:
            continue
        block = render_sections_html(entity_id, graph)
        if not block:
            continue
        original = path.read_text(encoding="utf-8")
        updated = inject_html(original, block)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            modified += 1
    return modified


# ---------------------------------------------------------------------------
# Dedicated paginated index pages
# ---------------------------------------------------------------------------


def index_page_path(entity: Entity, section_key: str, page: int = 1) -> str:
    """Dist-relative path of a section's index page.

    Index pages live next to the entity page (same collection directory, so
    relative asset and item links are identical in depth). Page 1 has no
    suffix; later pages append ``-N``. The ``<FORM>-<section>`` stem cannot
    collide with entity ids, which require a four-digit numeric segment.
    """
    form = entity.id.split("/", 1)[1] if "/" in entity.id else entity.id
    base = f"{form}-{section_key}"
    if page <= 1:
        return f"{entity.collection}/{base}.html"
    return f"{entity.collection}/{base}-{page}.html"


def index_page_count(total: int) -> int:
    """Number of index pages needed for ``total`` items."""
    if total <= 0:
        return 0
    return (total + INDEX_PAGE_SIZE - 1) // INDEX_PAGE_SIZE


def _index_shell_article(
    entity: Entity,
    section: Section,
    page: int,
    items: list[dict[str, Any]],
    total_pages: int,
    graph: CrosslinkGraph,
) -> str:
    """Article content for one paginated index page."""
    from_output = index_page_path(entity, section.key, page)
    back = _relative_link(from_output, entity.output_path)
    blocks = [
        f'<article class="page article" tabindex="-1" '
        f'data-crosslinks-index="1" data-index-for="{_escape(entity.id)}" '
        f'data-index-section="{_escape(section.key)}">',
        f'<h1>All {_escape(section.label)}</h1>',
        f'<p class="crosslinks__note">Full list for the “{_escape(section.label)}” '
        f'section of <a href="{_escape(back)}">{_escape(entity.title)}</a>. '
        'Generated from structured relationships; links are labeled by edge '
        'class and evidence trace. Derived links are navigation, not primary '
        'assertions.</p>',
        f'<section class="crosslinks__section" '
        f'data-section="{_escape(section.key)}" '
        f'data-edge-class="{_escape(section.edge_class)}" '
        f'data-source-class="{_escape(section.source_class)}">'
        f'<h2>{_escape(section.label)} '
        f'<span class="crosslinks__count">({section.count})</span></h2>'
        f'<ul>{"".join(_item_html(item, from_output, graph) for item in items)}</ul>'
        f'</section>',
    ]
    if total_pages > 1:
        blocks.append(_pager_html(entity, section.key, page, total_pages))
    blocks.append(
        f'<p><a href="{_escape(back)}">← Back to {_escape(entity.title)}</a></p>'
    )
    blocks.append("</article>")
    return "\n".join(blocks)


def _pager_html(entity: Entity, section_key: str, page: int, total_pages: int) -> str:
    """Prev / page / next navigation between index pages (deterministic)."""
    links: list[str] = []
    if page > 1:
        prev = index_page_path(entity, section_key, page - 1)
        links.append(
            f'<a class="crosslinks__pager-link" rel="prev" '
            f'href="{_escape(_relative_link(index_page_path(entity, section_key, page), prev))}">'
            "← Prev</a>"
        )
    for number in range(1, total_pages + 1):
        target = index_page_path(entity, section_key, number)
        if number == page:
            links.append(
                f'<span class="crosslinks__pager-link" aria-current="page">'
                f'{number}</span>'
            )
        else:
            href = _relative_link(index_page_path(entity, section_key, page), target)
            links.append(
                f'<a class="crosslinks__pager-link" href="{_escape(href)}">'
                f'{number}</a>'
            )
    if page < total_pages:
        nxt = index_page_path(entity, section_key, page + 1)
        links.append(
            f'<a class="crosslinks__pager-link" rel="next" '
            f'href="{_escape(_relative_link(index_page_path(entity, section_key, page), nxt))}">'
            "Next →</a>"
        )
    return f'<nav class="crosslinks__pager" aria-label="Pages">{" ".join(links)}</nav>'


def _splice_index_shell(
    shell: str,
    entity: Entity,
    section: Section,
    page: int,
    items: list[dict[str, Any]],
    total_pages: int,
    graph: CrosslinkGraph,
) -> str:
    """Splice index content into a copy of the entity page's layout shell.

    The index page lives in the same collection directory as the entity page,
    so the copied shell's relative asset/script paths stay correct. Only the
    title, breadcrumb, rail (emptied), and article body are replaced.
    """
    title = f"All {_escape(section.label)} — {_escape(entity.title)} · Thermal Extraction Devices"
    back = _relative_link(index_page_path(entity, section.key, page), entity.output_path)
    breadcrumb = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>'
        f'<li><a href="{_escape(back)}">{_escape(entity.title)}</a></li>'
        f'<li aria-current="page">All {_escape(section.label)}</li>'
        f'</ol></nav>'
    )
    article = _index_shell_article(entity, section, page, items, total_pages, graph)
    html = re.sub(
        r"<title>.*?</title>", f"<title>{title}</title>", shell, count=1, flags=re.S
    )
    html = re.sub(
        r"<article[^>]*>.*?</article>", article, html, count=1, flags=re.S
    )
    html = re.sub(
        r'<div class="breadcrumb-wrap">.*?</div>',
        f'<div class="breadcrumb-wrap">{breadcrumb}</div>',
        html, count=1, flags=re.S,
    )
    html = re.sub(
        r'<aside class="page-rail"[^>]*>.*?</aside>',
        '<aside class="page-rail" aria-label="On this page"></aside>',
        html, count=1, flags=re.S,
    )
    return html


def generate_index_pages(html_root: Path, graph: CrosslinkGraph) -> int:
    """Write dedicated paginated index pages for high-degree sections.

    A section whose count exceeds the in-page display cap gets one index page
    per ``INDEX_PAGE_SIZE`` items, linked from the entity page. Returns the
    number of index pages written. Deterministic and idempotent (overwrites
    with identical bytes on every build).
    """
    written = 0
    for entity_id in sorted(graph.entities):
        entity = graph.entities[entity_id]
        shell_path = html_root / entity.output_path
        if not shell_path.exists():
            continue
        shell = shell_path.read_text(encoding="utf-8")
        for section in sections_for(entity_id, graph):
            if section.count <= MAX_ITEMS_PER_SECTION:
                continue
            total_pages = index_page_count(section.count)
            for page in range(1, total_pages + 1):
                start = (page - 1) * INDEX_PAGE_SIZE
                items = section.all_items[start:start + INDEX_PAGE_SIZE]
                html = _splice_index_shell(
                    shell, entity, section, page, items, total_pages, graph
                )
                out_path = html_root / index_page_path(entity, section.key, page)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(html, encoding="utf-8")
                written += 1
    return written


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_graph(graph: CrosslinkGraph, content_root: Path) -> list[str]:
    """Structural validation of the derived navigation graph.

    Returns human-readable problems (empty == clean). Checks:

    * CXL-02 relation targets exist (all edge endpoints are known entities);
    * CXL-03 relation types are valid for the target collection;
    * CXL-04 no duplicate ``(from, kind, to, class)`` edges;
    * CXL-05 no derived edge is ever emitted as ``direct``;
    * CXL-06 derived edges carry an evidence trace;
    * CXL-13 every collection with satellites has at least one connected
      satellite (trunks are navigation roots and are not counted).
    """
    problems: list[str] = []

    for edge in graph.edges:
        if edge.from_id not in graph.entities:
            problems.append(
                f"CXL-02: edge source {edge.from_id!r} (kind {edge.kind}) is not "
                "a content entity"
            )
        if edge.to_id not in graph.entities:
            problems.append(
                f"CXL-02: edge target {edge.to_id!r} (kind {edge.kind}, from "
                f"{edge.from_id}) is not a content entity"
            )

    for edge in graph.edges:
        problem = _validate_edge_type(edge, graph)
        if problem:
            problems.append(problem)

    seen: set[tuple[str, str, str, str]] = set()
    for edge in graph.edges:
        key = (edge.from_id, edge.kind, edge.to_id, edge.edge_class)
        if key in seen:
            problems.append(
                f"CXL-04: duplicate edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} ({edge.edge_class})"
            )
        seen.add(key)

    for edge in graph.edges:
        if edge.edge_class == "direct" and edge.kind not in DIRECT_RELATION_KINDS:
            problems.append(
                f"CXL-05: edge {edge.from_id} --{edge.kind}--> {edge.to_id} is "
                "classified direct but is not a frontmatter relation kind"
            )
        if edge.edge_class == "derived" and not edge.trace:
            problems.append(
                f"CXL-06: derived edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} has no evidence trace"
            )

    # CXL-07: frontmatter relation targets must exist (Boris's own check,
    # mirrored here so graph-only validation never needs a Boris run).
    entity_ids = set(graph.entities)
    for edge in graph.edges:
        if edge.edge_class == "direct" and edge.to_id not in entity_ids:
            problems.append(
                f"CXL-07: relation {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} targets a nonexistent entity"
            )

    problems.extend(validate_satellite_connectivity(graph))

    return problems


def validate_satellite_connectivity(graph: CrosslinkGraph) -> list[str]:
    """Reject a collection whose satellites have no semantic graph edges.

    Parentage connects a satellite to its collection trunk structurally, but
    it is not a semantic relation in this graph. A collection may therefore
    contain intentionally standalone records, while a collection made up
    entirely of standalone satellites is likely an authoring omission.
    """
    satellites_by_collection: dict[str, list[str]] = {}
    for entity in graph.entities.values():
        if entity.role != "satellite":
            continue
        satellites_by_collection.setdefault(entity.collection, []).append(entity.id)

    problems: list[str] = []
    for collection, satellite_ids in sorted(satellites_by_collection.items()):
        if all(
            not graph.outgoing.get(entity_id) and not graph.incoming.get(entity_id)
            for entity_id in satellite_ids
        ):
            problems.append(
                f"CXL-13: satellite collection {collection!r} is fully isolated "
                f"({len(satellite_ids)} satellite(s) have no semantic relations)"
            )
    return problems


def _validate_edge_type(edge: Edge, graph: CrosslinkGraph) -> Optional[str]:
    """One relation-type rule: the target collection must fit the edge kind.

    Only forward edges (direct / identity_claim / measurement) are checked;
    derived edges are projections of already-validated forward edges.
    """
    if edge.edge_class == "derived":
        return None
    from_role = _role(edge.from_id, graph)
    to_role = _role(edge.to_id, graph)

    if edge.kind in ("analyte_result", "measured_in"):
        if to_role != "compound":
            return (
                f"CXL-03: analyte edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must target a compound entity"
            )
        return None
    if edge.kind == "observed_in_reports":
        if to_role != "compound" or from_role not in ("product", "cultivar"):
            return (
                f"CXL-03: observed-in-reports edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must run product/cultivar -> compound"
            )
        return None
    if edge.kind in ("reported_in_cultivars", "reported_in_products"):
        if from_role != "compound":
            return (
                f"CXL-03: projection edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must originate at a compound entity"
            )
        return None
    if edge.kind in ("tested_by", "issued"):
        if to_role != "laboratory":
            return (
                f"CXL-03: laboratory edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must target a testing-laboratories entity"
            )
        return None
    if edge.kind in ("product_of", "reported_in"):
        if to_role != "product":
            return (
                f"CXL-03: product edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must target a products entity"
            )
        return None
    if edge.kind in ("product_claims_cultivar", "batch_claims_cultivar",
                     "claims_cultivar"):
        if to_role != "cultivar":
            return (
                f"CXL-03: cultivar-claim edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must target a cultivars entity"
            )
        return None
    if edge.kind in ("claimed_lineage_parent", "lineage_parent", "parent_of"):
        if from_role != "cultivar" or to_role != "cultivar":
            return (
                f"CXL-03: lineage edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must connect cultivar entities"
            )
        return None
    if edge.kind in ("claimed_bred_by", "bred_by", "bred", "seed_source"):
        if from_role != "cultivar":
            return (
                f"CXL-03: breeder edge {edge.from_id} --{edge.kind}--> "
                f"{edge.to_id} must originate at a cultivars entity"
            )
        return None
    return None


def validate_sections(graph: CrosslinkGraph) -> list[str]:
    """Rendering-bounds validation over the derived sections.

    * CXL-08 per-section cap respected (item lists are bounded);
    * CXL-09 no duplicate target ids within one section;
    * CXL-10 derived sections are labeled (edge class carried in data attrs).
    """
    problems: list[str] = []
    for entity_id in sorted(graph.entities):
        for section in sections_for(entity_id, graph):
            if len(section.items) > MAX_ITEMS_PER_SECTION:
                problems.append(
                    f"CXL-08: section {entity_id}#{section.key} exceeds "
                    f"{MAX_ITEMS_PER_SECTION} items ({len(section.items)})"
                )
            ids = [item["id"] for item in section.items]
            if len(ids) != len(set(ids)):
                problems.append(
                    f"CXL-09: section {entity_id}#{section.key} contains "
                    "duplicate target ids"
                )
            if section.edge_class not in EDGE_CLASSES:
                problems.append(
                    f"CXL-10: section {entity_id}#{section.key} has unknown "
                    f"edge class {section.edge_class!r}"
                )
    return problems


def validate_injected_html(html_root: Path, graph: CrosslinkGraph) -> list[str]:
    """Check every generated crosslink in the rendered HTML resolves."""
    problems: list[str] = []
    for path in sorted(html_root.rglob("*.html")):
        rel = path.relative_to(html_root)
        if rel.parts and rel.parts[0] == "_boris":
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r'<section class="crosslinks" data-crosslinks="1">(.*?)</section>', text, flags=re.S):
            for link in re.finditer(r'href="([^"]+)"', match.group(1)):
                href = link.group(1)
                if href.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                resolved = (path.parent / href).resolve()
                if not resolved.exists():
                    problems.append(
                        f"CXL-01: broken generated link {href!r} in {rel}"
                    )
    return problems


def validate_index_pages(html_root: Path, graph: CrosslinkGraph) -> list[str]:
    """Validate dedicated paginated index pages for high-degree sections.

    * CXL-11 every section over the display cap has its index page(s), marked
      for the right section, with at most ``INDEX_PAGE_SIZE`` items each;
    * CXL-12 the entity page links to the index (crawlable, not orphaned).
    """
    problems: list[str] = []
    for entity_id in sorted(graph.entities):
        entity = graph.entities[entity_id]
        for section in sections_for(entity_id, graph):
            if section.count <= MAX_ITEMS_PER_SECTION:
                continue
            total_pages = index_page_count(section.count)
            for page in range(1, total_pages + 1):
                rel = index_page_path(entity, section.key, page)
                path = html_root / rel
                if not path.exists():
                    problems.append(
                        f"CXL-11: missing index page {rel} for "
                        f"{entity_id}#{section.key}"
                    )
                    continue
                text = path.read_text(encoding="utf-8")
                if f'data-index-section="{section.key}"' not in text:
                    problems.append(
                        f"CXL-11: index page {rel} is not marked for section "
                        f"{section.key}"
                    )
                item_count = len(re.findall(r'data-entity-id=', text))
                if item_count > INDEX_PAGE_SIZE:
                    problems.append(
                        f"CXL-11: index page {rel} exceeds {INDEX_PAGE_SIZE} "
                        f"items ({item_count})"
                    )
            entity_html = html_root / entity.output_path
            if entity_html.exists():
                text = entity_html.read_text(encoding="utf-8")
                first = index_page_path(entity, section.key)
                if _relative_link(entity.output_path, first) not in text:
                    problems.append(
                        f"CXL-12: entity page {entity.output_path} does not "
                        f"link to index {first}"
                    )
    return problems


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "content")
    parser.add_argument("--map", type=Path, default=ROOT / "metadata" / "id-map.jsonl")
    parser.add_argument("--claims", type=Path, default=ROOT / "metadata" / "cultivar-claims.jsonl")
    parser.add_argument("--coa", type=Path, default=ROOT / "metadata" / "coa-records.jsonl")
    parser.add_argument("--out", type=Path, default=None, help="write exports/crosslinks.json")
    parser.add_argument("--rag", type=Path, default=None, help="write the RAG companion markdown")
    parser.add_argument("--html-dir", type=Path, default=None,
                        help="rendered Boris HTML directory to inject into")
    parser.add_argument("--inject", action="store_true",
                        help="inject derived navigation into --html-dir pages")
    parser.add_argument("--check", action="store_true",
                        help="validate the derived graph and exit (no writes)")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args(argv)

    try:
        entities = load_entities(args.map)
        claims = load_claims(args.claims) if args.claims.exists() else []
        coa_records = load_coa_records(args.coa)
        graph = build_graph(args.root, entities, claims, coa_records)
        problems = validate_graph(graph, args.root)
        problems.extend(validate_sections(graph))
    except (OSError, ValueError, KeyError) as error:
        print(f"Crosslinks: error: {error}", file=sys.stderr)
        return 2

    if args.check:
        if problems:
            print(
                f"Crosslinks: {len(problems)} problem(s):",
                file=sys.stderr,
            )
            for problem in problems:
                print(f"  {problem}", file=sys.stderr)
            return 1
        print(
            f"Crosslinks: graph valid — {len(graph.entities)} entities, "
            f"{len(graph.edges)} edges, {len(coa_records)} COA record(s)"
        )
        return 0

    if problems:
        print(
            f"Crosslinks: {len(problems)} problem(s); refusing to emit:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    payload = export_json(graph)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.rag:
        args.rag.parent.mkdir(parents=True, exist_ok=True)
        args.rag.write_text(render_rag_document(graph), encoding="utf-8")

    modified = 0
    index_written = 0
    if args.inject:
        if args.html_dir is None:
            print(
                "Crosslinks: error: --inject requires --html-dir",
                file=sys.stderr,
            )
            return 2
        if not args.html_dir.exists():
            print(
                f"Crosslinks: error: --html-dir {args.html_dir} does not exist "
                "(run the Boris build first)",
                file=sys.stderr,
            )
            return 2
        modified = inject_all(args.html_dir, graph)
        index_written = generate_index_pages(args.html_dir, graph)
        html_problems = validate_injected_html(args.html_dir, graph)
        html_problems.extend(validate_index_pages(args.html_dir, graph))
        if html_problems:
            print(
                f"Crosslinks: {len(html_problems)} generated-HTML problem(s):",
                file=sys.stderr,
            )
            for problem in html_problems:
                print(f"  {problem}", file=sys.stderr)
            return 1

    index_total = sum(
        index_page_count(section.count)
        for entity_id in graph.entities
        for section in sections_for(entity_id, graph)
        if section.count > MAX_ITEMS_PER_SECTION
    )
    print(
        f"Crosslinks: {len(payload['entities'])} entity page(s) with derived "
        f"navigation; {len(graph.edges)} edges; {modified} HTML page(s) updated; "
        f"{index_total} index page(s) ({index_written} written)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
