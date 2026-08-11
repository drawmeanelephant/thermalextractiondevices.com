"""Tests for the evidence-aware crosslinking layer (scripts/crosslinks.py)."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from scripts.crosslinks import (  # noqa: E402
    INDEX_PAGE_SIZE,
    MAX_ITEMS_PER_SECTION,
    MAX_LINKS_PER_PAGE,
    CrosslinkGraph,
    Edge,
    Entity,
    build_graph,
    export_json,
    generate_index_pages,
    index_page_count,
    index_page_path,
    inject_all,
    inject_html,
    load_coa_records,
    load_entities,
    render_sections_html,
    sections_for,
    validate_graph,
    validate_index_pages,
    validate_injected_html,
    validate_sections,
)
from scripts.cultivar_claims import load_claims  # noqa: E402
from scripts.coa_verify_example import record as verified_coa_record  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "crosslinks"

# The nine entities named by the mission's Definition of Done.
DOO_ENTITIES = [
    "lab-results/TLAB-0001",          # the report
    "products/TPRD-0001",             # the product
    "testing-laboratories/TSTL-0001", # the laboratory
    "cultivars/TCUL-0001",            # the cultivar
    "cannabinoids/TCBN-0007",         # THCA
    "cannabinoids/TCBN-0009",         # Δ9-THC
    "terpenes/TTRP-0005",             # β-myrcene
    "terpenes/TTRP-0007",             # limonene
]

DOO_COMPOUNDS = {"cannabinoids/TCBN-0007", "cannabinoids/TCBN-0009",
                 "terpenes/TTRP-0005", "terpenes/TTRP-0007"}


def build_fixture_graph() -> CrosslinkGraph:
    entities = load_entities(FIXTURES / "metadata" / "id-map.jsonl")
    claims = load_claims(FIXTURES / "metadata" / "cultivar-claims.jsonl")
    coa = load_coa_records(FIXTURES / "metadata" / "coa-records.jsonl")
    return build_graph(FIXTURES / "content", entities, claims, coa)


def section_map(entity_id: str, graph: CrosslinkGraph) -> dict[str, list[str]]:
    return {s.key: [item["id"] for item in s.items]
            for s in sections_for(entity_id, graph)}


class TestDefinitionOfDone(unittest.TestCase):
    """Adding ONE lab report (cultivar claim + lab + batch + THCA, Δ9-THC,
    β-myrcene, limonene) must improve navigation from all nine entities
    without manually editing the unrelated pages."""

    @classmethod
    def setUpClass(cls):
        cls.graph = build_fixture_graph()

    def test_report_page_navigation(self):
        sections = section_map("lab-results/TLAB-0001", self.graph)
        self.assertIn("testing-laboratories/TSTL-0001", sections["laboratory"])
        self.assertIn("products/TPRD-0001", sections["product"])
        self.assertIn("cultivars/TCUL-0001", sections["cultivar"])
        self.assertEqual(set(sections["compounds"]), DOO_COMPOUNDS)
        # The batch identifier is surfaced on the report page (no entity).
        batch = [s for s in sections_for("lab-results/TLAB-0001", self.graph)
                 if s.key == "batch"]
        self.assertEqual(len(batch), 1)
        self.assertIn("BR-BD-20260315-123", batch[0].items[0]["title"])

    def test_product_page_navigation(self):
        sections = section_map("products/TPRD-0001", self.graph)
        self.assertIn("cultivars/TCUL-0001", sections["cultivar_claims"])
        self.assertIn("lab-results/TLAB-0001", sections["reports"])
        self.assertEqual(set(sections["observed_compounds"]), DOO_COMPOUNDS)

    def test_laboratory_page_navigation(self):
        sections = section_map("testing-laboratories/TSTL-0001", self.graph)
        self.assertIn("lab-results/TLAB-0001", sections["reports"])

    def test_cultivar_page_navigation(self):
        sections = section_map("cultivars/TCUL-0001", self.graph)
        self.assertIn("products/TPRD-0001", sections["products"])
        self.assertIn("lab-results/TLAB-0001", sections["reports"])
        self.assertEqual(set(sections["observed_compounds"]), DOO_COMPOUNDS)

    def test_compound_pages_navigation(self):
        for compound in DOO_COMPOUNDS:
            with self.subTest(compound=compound):
                sections = section_map(compound, self.graph)
                self.assertIn("lab-results/TLAB-0001", sections["measured_reports"])
                self.assertIn("products/TPRD-0001", sections["products"])
                self.assertIn("cultivars/TCUL-0001", sections["observed_cultivars"])

    def test_no_manual_editing_required(self):
        # The report page's frontmatter only names the product; the compound
        # links, the laboratory link, and the cultivar link are all derived
        # from the structured COA record and claim registry — not authored.
        report_source = (FIXTURES / "content" / "lab-results"
                         / "example-producer-blue-dream-batch-123.md")
        text = report_source.read_text(encoding="utf-8")
        for compound in DOO_COMPOUNDS:
            self.assertNotIn(compound, text)
        self.assertNotIn("testing-laboratories/TSTL-0001", text)
        report_sections = section_map("lab-results/TLAB-0001", self.graph)
        self.assertEqual(set(report_sections["compounds"]), DOO_COMPOUNDS)
        self.assertIn("testing-laboratories/TSTL-0001", report_sections["laboratory"])


class TestEdgeClasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build_fixture_graph()

    def test_measurement_edges(self):
        kinds = {(e.from_id, e.to_id, e.kind) for e in self.graph.edges
                 if e.edge_class == "measurement"}
        self.assertIn(("lab-results/TLAB-0001", "testing-laboratories/TSTL-0001", "tested_by"), kinds)
        self.assertIn(("lab-results/TLAB-0001", "products/TPRD-0001", "product_of"), kinds)
        for compound in DOO_COMPOUNDS:
            self.assertIn(("lab-results/TLAB-0001", compound, "analyte_result"), kinds)

    def test_identity_claim_edges(self):
        kinds = {(e.from_id, e.to_id, e.kind) for e in self.graph.edges
                 if e.edge_class == "identity_claim"}
        self.assertIn(("products/TPRD-0001", "cultivars/TCUL-0001", "product_claims_cultivar"), kinds)
        self.assertIn(("lab-results/TLAB-0001", "cultivars/TCUL-0001", "batch_claims_cultivar"), kinds)

    def test_derived_edges_carry_traces(self):
        for edge in self.graph.edges:
            if edge.edge_class == "derived":
                self.assertTrue(edge.trace, f"derived edge without trace: {edge}")

    def test_derived_never_direct(self):
        for edge in self.graph.edges:
            if edge.edge_class == "direct":
                self.assertIn(edge.kind, ("relates_to", "implements", "depends_on", "supersedes"))
            else:
                self.assertNotEqual(edge.edge_class, "direct")

    def test_cultivar_compound_is_derived_not_factual(self):
        # Cultivar -> compound must be a derived navigation edge whose trace
        # names the report(s), never a direct factual assertion.
        matches = [e for e in self.graph.edges
                   if e.from_id == "cultivars/TCUL-0001"
                   and e.to_id == "terpenes/TTRP-0005"
                   and e.kind == "observed_in_reports"]
        self.assertEqual(len(matches), 1)
        edge = matches[0]
        self.assertEqual(edge.edge_class, "derived")
        self.assertIn("lab-results/TLAB-0001", edge.trace)


class TestReverseRelations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build_fixture_graph()

    def test_laboratory_reverse(self):
        issued = [e for e in self.graph.edges
                  if e.from_id == "testing-laboratories/TSTL-0001"
                  and e.kind == "issued"]
        self.assertEqual([e.to_id for e in issued], ["lab-results/TLAB-0001"])

    def test_compound_reverse(self):
        for compound in DOO_COMPOUNDS:
            measured = [e for e in self.graph.edges
                        if e.from_id == compound and e.kind == "measured_in"]
            self.assertEqual([e.to_id for e in measured], ["lab-results/TLAB-0001"])

    def test_cultivar_claims_reverse(self):
        # Derived reverse of product/batch cultivar claims: the cultivar page
        # navigates to the entities that carry its name.
        outgoing = [e for e in self.graph.edges
                    if e.from_id == "cultivars/TCUL-0001" and e.kind == "claims_cultivar"]
        self.assertEqual(
            {e.to_id for e in outgoing},
            {"products/TPRD-0001", "lab-results/TLAB-0001"},
        )
        for edge in outgoing:
            self.assertEqual(edge.edge_class, "derived")


class TestValidationRules(unittest.TestCase):
    def test_direct_cultivar_to_compound_relation_is_rejected(self):
        entities = {
            "cultivars/TCUL-0001": Entity(
                id="cultivars/TCUL-0001",
                title="Fixture Cultivar",
                source="cultivars/fixture.md",
                collection="cultivars",
                parent="cultivars",
                role="satellite",
            ),
            "terpenes/TTRP-0001": Entity(
                id="terpenes/TTRP-0001",
                title="Fixture Terpene",
                source="terpenes/fixture.md",
                collection="terpenes",
                parent="terpenes",
                role="satellite",
            ),
        }
        graph = CrosslinkGraph(
            entities=entities,
            edges=[
                Edge(
                    from_id="cultivars/TCUL-0001",
                    to_id="terpenes/TTRP-0001",
                    kind="relates_to",
                    edge_class="direct",
                )
            ],
        )

        problems = validate_graph(graph, FIXTURES / "content")
        self.assertTrue(
            any(
                "cannot connect a cultivar directly to a compound" in problem
                for problem in problems
            ),
            problems,
        )


class TestDeterminism(unittest.TestCase):
    def test_export_json_is_stable(self):
        graph = build_fixture_graph()
        first = json.dumps(export_json(graph), ensure_ascii=False, sort_keys=True)
        second = json.dumps(export_json(graph), ensure_ascii=False, sort_keys=True)
        self.assertEqual(first, second)

    def test_sections_stable(self):
        graph = build_fixture_graph()
        a = [s.to_dict() for s in sections_for("cultivars/TCUL-0001", graph)]
        b = [s.to_dict() for s in sections_for("cultivars/TCUL-0001", graph)]
        self.assertEqual(a, b)


class TestBounds(unittest.TestCase):
    def test_many_reports_stay_bounded(self):
        # 30 reports measuring one compound: count is full, list is capped.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            entities = {
                "terpenes/TTRP-0005": _entity("terpenes/TTRP-0005", "β-Myrcene",
                                              "terpenes/beta-myrcene.md", "terpenes"),
            }
            records = []
            for number in range(1, 31):
                report_id = f"lab-results/TLAB-{1000 + number:04d}"
                entities[report_id] = _entity(
                    report_id, f"Report {number}",
                    f"lab-results/report-{number}.md", "lab-results")
                records.append(_coa_json(report_id, number))
            coa_path = tmp / "coa-records.jsonl"
            coa_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            coa = load_coa_records(coa_path)
            graph = build_graph(tmp / "content", entities, [], coa)

            sections = {s.key: s for s in sections_for("terpenes/TTRP-0005", graph)}
            self.assertEqual(sections["measured_reports"].to_dict()["count"], 30)
            self.assertLessEqual(len(sections["measured_reports"].items), MAX_ITEMS_PER_SECTION)

            html = render_sections_html("terpenes/TTRP-0005", graph)
            self.assertLessEqual(html.count('href="'), MAX_LINKS_PER_PAGE)
            # High-degree sections link to a dedicated index page instead of
            # an unbounded in-page list or a bare "(+N more)" span.
            self.assertNotIn("(+22 more)", html)
            self.assertIn("View all 30", html)
            self.assertIn('href="TTRP-0005-measured_reports.html"', html)

            self.assertEqual(validate_sections(graph), [])


class TestValidation(unittest.TestCase):
    def test_fixture_graph_is_clean(self):
        graph = build_fixture_graph()
        self.assertEqual(validate_graph(graph, FIXTURES / "content"), [])
        self.assertEqual(validate_sections(graph), [])

    def test_broken_relation_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "content").mkdir(parents=True)
            entities = load_entities(FIXTURES / "metadata" / "id-map.jsonl")
            claims = [{
                "claim_id": "CLM-X", "kind": "batch_claims_cultivar",
                "subject": "lab-results/TLAB-0001", "object": "cultivars/TCUL-9999",
                "object_is_entity": True, "status": "claimed",
                "source": {"name": "Fixture", "type": "testing_laboratory"},
            }]
            graph = build_graph(tmp / "content", entities, claims, [])
            problems = validate_graph(graph, tmp / "content")
            self.assertTrue(any("CXL-02" in p and "TCUL-9999" in p for p in problems))

    def test_incorrect_relation_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "content").mkdir(parents=True)
            entities = load_entities(FIXTURES / "metadata" / "id-map.jsonl")
            claims = [{
                "claim_id": "CLM-Y", "kind": "product_claims_cultivar",
                "subject": "products/TPRD-0001", "object": "cannabinoids/TCBN-0007",
                "object_is_entity": True, "status": "claimed",
                "source": {"name": "Fixture", "type": "producer"},
            }]
            graph = build_graph(tmp / "content", entities, claims, [])
            problems = validate_graph(graph, tmp / "content")
            self.assertTrue(any("CXL-03" in p and "cultivar" in p for p in problems))

    def test_duplicate_edge(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "content").mkdir(parents=True)
            entities = load_entities(FIXTURES / "metadata" / "id-map.jsonl")
            claims = [
                {
                    "claim_id": "CLM-A", "kind": "product_claims_cultivar",
                    "subject": "products/TPRD-0001", "object": "cultivars/TCUL-0001",
                    "object_is_entity": True, "status": "claimed",
                    "source": {"name": "Fixture A", "type": "producer"},
                },
                {
                    "claim_id": "CLM-B", "kind": "product_claims_cultivar",
                    "subject": "products/TPRD-0001", "object": "cultivars/TCUL-0001",
                    "object_is_entity": True, "status": "claimed",
                    "source": {"name": "Fixture B", "type": "producer"},
                },
            ]
            graph = build_graph(tmp / "content", entities, claims, [])
            problems = validate_graph(graph, tmp / "content")
            self.assertTrue(any("CXL-04" in p for p in problems))

    def test_derived_without_trace_is_rejected(self):
        entities = load_entities(FIXTURES / "metadata" / "id-map.jsonl")
        graph = CrosslinkGraph(entities=entities)
        graph.add(Edge(
            from_id="lab-results/TLAB-0001", to_id="terpenes/TTRP-0005",
            kind="measured_in", edge_class="derived", trace=(),
        ))
        problems = validate_graph(graph, FIXTURES / "content")
        self.assertTrue(any("CXL-06" in p for p in problems))

    def test_fully_isolated_satellite_collection_is_rejected(self):
        entities = {
            "orphaned": Entity(
                id="orphaned", title="Orphaned", source="orphaned.md",
                collection="orphaned", parent=None, role="trunk",
            ),
            "orphaned/TO-0001": Entity(
                id="orphaned/TO-0001", title="Orphan One",
                source="orphaned/TO-0001.md", collection="orphaned",
                parent="orphaned", role="satellite",
            ),
            "orphaned/TO-0002": Entity(
                id="orphaned/TO-0002", title="Orphan Two",
                source="orphaned/TO-0002.md", collection="orphaned",
                parent="orphaned", role="satellite",
            ),
        }
        graph = CrosslinkGraph(entities=entities)

        problems = validate_graph(graph, FIXTURES / "content")

        self.assertEqual(len(problems), 1)
        self.assertIn("CXL-13", problems[0])
        self.assertIn("orphaned", problems[0])

    def test_partial_collection_and_trunks_are_not_rejected(self):
        entities = {
            "mixed": Entity(
                id="mixed", title="Mixed", source="mixed.md",
                collection="mixed", parent=None, role="trunk",
            ),
            "mixed/TM-0001": Entity(
                id="mixed/TM-0001", title="Connected",
                source="mixed/TM-0001.md", collection="mixed",
                parent="mixed", role="satellite",
            ),
            "mixed/TM-0002": Entity(
                id="mixed/TM-0002", title="Standalone",
                source="mixed/TM-0002.md", collection="mixed",
                parent="mixed", role="satellite",
            ),
            "trunks-only": Entity(
                id="trunks-only", title="Trunks Only", source="trunks-only.md",
                collection="trunks-only", parent=None, role="trunk",
            ),
        }
        graph = CrosslinkGraph(entities=entities)
        graph.add(Edge(
            from_id="mixed/TM-0001", to_id="mixed", kind="relates_to",
            edge_class="direct",
        ))

        self.assertEqual(validate_graph(graph, FIXTURES / "content"), [])

    def test_invalid_coa_record_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coa-records.jsonl"
            path.write_text(json.dumps({
                "schema_version": "1.0",
                "report": {"report_id": "lab-results/TLAB-0002", "revision": 1},
                "batch": {"batch_id": "B-2", "record_kind": "unverified"},
                "measurements": [{
                    "compound_id": "terpenes/TTRP-0005", "compound_name": "β-Myrcene",
                    "state": "numeric", "value": None,
                }],
            }) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_coa_records(path)


class TestHtmlInjection(unittest.TestCase):
    def _write_pages(self, html_root: Path, graph: CrosslinkGraph) -> None:
        for entity in graph.entities.values():
            path = html_root / entity.output_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "<!doctype html><html><head><title>x</title></head>"
                "<body><article><p>content</p></article></body></html>",
                encoding="utf-8",
            )

    def test_inject_and_idempotence(self):
        graph = build_fixture_graph()
        with tempfile.TemporaryDirectory() as tmp:
            html_root = Path(tmp) / "dist"
            self._write_pages(html_root, graph)
            first = inject_all(html_root, graph)
            self.assertGreaterEqual(first, 8)
            second = inject_all(html_root, graph)
            self.assertEqual(second, 0)  # idempotent
            self.assertEqual(validate_injected_html(html_root, graph), [])

    def test_injected_sections_are_labeled(self):
        graph = build_fixture_graph()
        block = render_sections_html("terpenes/TTRP-0005", graph)
        self.assertIn("data-edge-class=\"derived\"", block)
        self.assertIn("data-source-class=\"measurement\"", block)
        self.assertIn("Laboratory reports measuring this compound", block)
        self.assertIn("data-record-kind=\"demonstration\"", block)

    def test_inject_html_replaces_existing_block(self):
        graph = build_fixture_graph()
        block = render_sections_html("terpenes/TTRP-0005", graph)
        page = "<article>old</article>"
        once = inject_html(page, block)
        twice = inject_html(once, block)
        self.assertNotIn("<p>old</p>", twice)
        self.assertEqual(once, twice)
        self.assertEqual(twice.count('data-crosslinks="1"'), 1)

    def test_derived_links_resolve(self):
        graph = build_fixture_graph()
        with tempfile.TemporaryDirectory() as tmp:
            html_root = Path(tmp) / "dist"
            self._write_pages(html_root, graph)
            inject_all(html_root, graph)
            problems = validate_injected_html(html_root, graph)
            self.assertEqual(problems, [])


class TestIndexPages(unittest.TestCase):
    """Dedicated paginated index pages for high-degree sections."""

    SHELL = (
        "<!doctype html><html><head><title>{title}</title></head>"
        "<body><div class=\"breadcrumb-wrap\"><nav class=\"breadcrumb\">"
        "<ol><li>crumb</li></ol></nav></div>"
        "<main class=\"page-grid\" id=\"main-content\" data-boris-search-root>"
        "<article class=\"page article\" tabindex=\"-1\"><p>content</p></article>"
        "<aside class=\"page-rail\" aria-label=\"On this page\"><nav "
        "class=\"page-toc\"><ul><li>x</li></ul></nav></aside>"
        "</main></body></html>"
    )

    def _build(self, report_count: int):
        tmp = Path(tempfile.mkdtemp(prefix="crosslinks_index_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        entities = {
            "terpenes/TTRP-0005": _entity(
                "terpenes/TTRP-0005", "β-Myrcene",
                "terpenes/beta-myrcene.md", "terpenes"),
        }
        records = []
        for number in range(1, report_count + 1):
            report_id = f"lab-results/TLAB-{1000 + number:04d}"
            entities[report_id] = _entity(
                report_id, f"Report {number}",
                f"lab-results/report-{number}.md", "lab-results")
            records.append(_coa_json(report_id, number))
        coa_path = tmp / "coa-records.jsonl"
        coa_path.write_text("\n".join(records) + "\n", encoding="utf-8")
        coa = load_coa_records(coa_path)
        graph = build_graph(tmp / "content", entities, [], coa)
        html_root = tmp / "dist"
        for entity in graph.entities.values():
            path = html_root / entity.output_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.SHELL.format(title=entity.title), encoding="utf-8")
        return graph, html_root

    def test_paginated_index_pages_generated(self):
        graph, html_root = self._build(report_count=250)
        inject_all(html_root, graph)
        written = generate_index_pages(html_root, graph)
        self.assertEqual(written, 3)  # 100 + 100 + 50
        entity = graph.entities["terpenes/TTRP-0005"]
        for page in (1, 2, 3):
            rel = index_page_path(entity, "measured_reports", page)
            self.assertTrue((html_root / rel).exists(), rel)
            text = (html_root / rel).read_text(encoding="utf-8")
            self.assertIn(f'data-index-section="measured_reports"', text)
            items = len(__import__("re").findall(r"data-entity-id=", text))
            self.assertLessEqual(items, INDEX_PAGE_SIZE)
        # pagination: 250 = 100 + 100 + 50
        self.assertEqual(len(__import__("re").findall(
            r"data-entity-id=", (html_root / index_page_path(entity, "measured_reports", 1)).read_text(encoding="utf-8"))), 100)
        self.assertEqual(len(__import__("re").findall(
            r"data-entity-id=", (html_root / index_page_path(entity, "measured_reports", 3)).read_text(encoding="utf-8"))), 50)
        # pager on every page
        pager = (html_root / index_page_path(entity, "measured_reports", 1)).read_text(encoding="utf-8")
        self.assertIn('class="crosslinks__pager"', pager)
        self.assertIn("Next →", pager)
        self.assertIn('href="TTRP-0005-measured_reports-2.html"', pager)
        # entity page links to the index (crawlable)
        entity_html = (html_root / entity.output_path).read_text(encoding="utf-8")
        self.assertIn('href="TTRP-0005-measured_reports.html"', entity_html)
        self.assertIn("View all 250", entity_html)
        # validation is clean
        self.assertEqual(validate_injected_html(html_root, graph), [])
        self.assertEqual(validate_index_pages(html_root, graph), [])

    def test_export_carries_index_metadata(self):
        graph, html_root = self._build(report_count=120)
        payload = export_json(graph)
        for entity in payload["entities"]:
            if entity["id"] != "terpenes/TTRP-0005":
                continue
            section = next(s for s in entity["sections"] if s["key"] == "measured_reports")
            self.assertEqual(section["count"], 120)
            self.assertEqual(section["index"]["pages"], 2)
            self.assertEqual(section["index"]["url"],
                             "terpenes/TTRP-0005-measured_reports.html")
            return
        self.fail("compound entity missing from export")

    def test_small_section_needs_no_index(self):
        graph, html_root = self._build(report_count=5)
        written = generate_index_pages(html_root, graph)
        self.assertEqual(written, 0)
        entity = graph.entities["terpenes/TTRP-0005"]
        self.assertFalse((html_root / index_page_path(entity, "measured_reports")).exists())
        html = render_sections_html("terpenes/TTRP-0005", graph)
        self.assertNotIn("View all", html)

    def test_index_determinism(self):
        graph, html_root = self._build(report_count=250)
        inject_all(html_root, graph)
        generate_index_pages(html_root, graph)
        entity = graph.entities["terpenes/TTRP-0005"]
        first = (html_root / index_page_path(entity, "measured_reports", 1)).read_text(encoding="utf-8")
        generate_index_pages(html_root, graph)
        second = (html_root / index_page_path(entity, "measured_reports", 1)).read_text(encoding="utf-8")
        self.assertEqual(first, second)


class TestLiveRepository(unittest.TestCase):
    """The live repo's current structured state must validate cleanly."""

    def test_live_graph_validates(self):
        map_path = ROOT / "metadata" / "id-map.jsonl"
        claims_path = ROOT / "metadata" / "cultivar-claims.jsonl"
        coa_path = ROOT / "metadata" / "coa-records.jsonl"
        if not map_path.exists():
            self.skipTest("live metadata unavailable")
        entities = load_entities(map_path)
        claims = load_claims(claims_path) if claims_path.exists() else []
        coa = load_coa_records(coa_path)
        graph = build_graph(ROOT / "content", entities, claims, coa)
        problems = validate_graph(graph, ROOT / "content")
        problems.extend(validate_sections(graph))
        self.assertEqual(problems, [])

    def test_verified_coa_provenance_is_carried_into_measurement_edges(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coa-records.jsonl"
            path.write_text(
                json.dumps(verified_coa_record().to_dict(), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            loaded = load_coa_records(path)
            graph = build_graph(ROOT / "content", load_entities(ROOT / "metadata" / "id-map.jsonl"), [], loaded)
            edge = next(edge for edge in graph.edges if edge.kind == "tested_by")
            self.assertIn("coa:lab-results/TLAB-0002", edge.provenance)
            self.assertIn("record_kind:verified", edge.provenance)
            self.assertTrue(any(item.startswith("document_sha256:") for item in edge.provenance))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _entity(entity_id: str, title: str, source: str, collection: str):
    from scripts.crosslinks import Entity
    return Entity(id=entity_id, title=title, source=source,
                  collection=collection, parent=collection, role="satellite")


def _coa_json(report_id: str, number: int) -> str:
    return json.dumps({
        "schema_version": "1.0",
        "report": {
            "report_id": report_id, "revision": 1, "supersedes": None,
            "source_reference": f"fixture report {number}",
            "report_date": "2026-01-01", "test_date": "2026-01-01",
            "sample_date": None,
            "laboratory": {"name": "Fixture Lab", "lab_id": None,
                           "license_number": "", "jurisdiction": "XX"},
            "jurisdiction": "XX", "method": None,
        },
        "batch": {
            "batch_id": f"BATCH-{number}", "metrc_tag": "", "producer_id": None,
            "product_id": None, "cultivar_labels": [],
            "sample_type": "flower", "matrix_detail": "", "basis": "unknown",
            "decarb_convention": "native", "record_kind": "unverified",
            "jurisdiction": "XX", "harvest_date": None,
        },
        "measurements": [{
            "compound_id": "terpenes/TTRP-0005", "compound_name": "β-Myrcene",
            "compound_cas": None, "reported_value": "8.45",
            "reported_unit": "mg/g", "state": "numeric", "value": 8.45,
            "unit": "mg/g", "lod": None, "loq": None, "method": None,
            "test_date": "2026-01-01", "quantitation_note": None, "conversion": None,
        }],
    }, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
