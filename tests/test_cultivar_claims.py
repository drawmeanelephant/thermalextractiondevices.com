"""Cultivar identity claim vocabulary, normalization, and registry tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.cultivar_claims import (
    CLAIM_KINDS,
    SOURCE_TYPES,
    STATUSES,
    load_claims,
    normalize_name,
    render_claim_context,
    validate_claims,
)
from scripts.ingest.validation import collect_entity_ids

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_REGISTRY = REPO_ROOT / "metadata" / "cultivar-claims.jsonl"
REAL_CONTENT = REPO_ROOT / "content"

#: The required relationship vocabulary from the cultivar identity mission.
REQUIRED_KINDS = {
    "alias_of",
    "claimed_alias_of",
    "bred_by",
    "claimed_bred_by",
    "lineage_parent",
    "claimed_lineage_parent",
    "sold_by",
    "listed_by",
    "seed_source",
    "product_claims_cultivar",
    "batch_claims_cultivar",
    "possibly_same_as",
    "historically_associated_with",
    "source_disagrees_with",
}

ENTITIES = {
    "cultivars/TCUL-0001",
    "cultivars/TCUL-0002",
    "products/TPRD-0001",
    "lab-results/TLAB-0001",
    "organizations/TORG-0001",
}


def _claim(**overrides: object) -> dict:
    base = {
        "claim_id": "CLM-9001",
        "kind": "claimed_bred_by",
        "subject": "cultivars/TCUL-0001",
        "object": "Sensi Seeds",
        "object_is_entity": False,
        "status": "claimed",
        "source": {"name": "Archive page", "type": "archive", "retrieved": "2026-08-09"},
    }
    base.update(overrides)
    return base


class VocabularyTestCase(unittest.TestCase):
    def test_required_relationship_vocabulary_present(self):
        missing = REQUIRED_KINDS - set(CLAIM_KINDS)
        self.assertEqual(missing, set(), f"missing claim kinds: {missing}")

    def test_claim_kinds_have_definitions(self):
        for kind, definition in CLAIM_KINDS.items():
            self.assertTrue(definition, f"{kind} lacks a definition")

    def test_source_roles_include_all_mission_roles(self):
        for role in ("breeder", "seed_bank", "producer", "testing_laboratory",
                     "regulator", "community", "database", "forum"):
            self.assertIn(role, SOURCE_TYPES)

    def test_statuses_are_human_readable(self):
        self.assertEqual(
            STATUSES,
            {"verified", "well_supported", "claimed", "conflicting",
             "tentative", "unresolved", "historical"},
        )


class NormalizationTestCase(unittest.TestCase):
    def test_case_and_whitespace_folding(self):
        self.assertEqual(normalize_name("  Blue   Dream "), "blue dream")
        self.assertEqual(normalize_name("BLUE DREAM"), "blue dream")

    def test_unicode_normalization(self):
        # Decomposed (e + U+0301) and precomposed (\u00e9) forms are equal.
        self.assertEqual(normalize_name("Cafe\u0301 Dream"), "caf\u00e9 dream")
        self.assertEqual(normalize_name("Caf\u00e9 Dream"), "caf\u00e9 dream")

    def test_punctuation_variants_fold(self):
        self.assertEqual(normalize_name("Gorilla Glue #4"), "gorilla glue 4")
        self.assertEqual(normalize_name("Gorilla Glue # 4"), "gorilla glue 4")
        self.assertEqual(normalize_name("Skunk #1"), "skunk 1")
        self.assertEqual(normalize_name("Mazar-i-Sharif"), "mazar i sharif")

    def test_meaningful_tokens_preserved(self):
        # Numbers, hash numbers, phenotype markers, and breeder prefixes are
        # never stripped by normalization.
        self.assertEqual(normalize_name("GG4"), "gg4")
        self.assertEqual(normalize_name("Original Glue F1"), "original glue f1")
        self.assertEqual(normalize_name("Blue Dream Auto"), "blue dream auto")
        self.assertEqual(normalize_name("Sensi Skunk #1 BX2"), "sensi skunk 1 bx2")

    def test_alias_requires_evidence_not_string_similarity(self):
        # Abbreviations must NOT silently resolve through normalization.
        self.assertNotEqual(normalize_name("GG4"), normalize_name("Gorilla Glue #4"))
        self.assertNotEqual(normalize_name("GG4"), normalize_name("Original Glue"))


class ValidationTestCase(unittest.TestCase):
    def test_valid_claim_passes(self):
        self.assertEqual(validate_claims([_claim()], ENTITIES), [])

    def test_unknown_kind_detected(self):
        problems = validate_claims([_claim(kind="is_definitely")], ENTITIES)
        self.assertTrue(any("unknown kind" in p for p in problems))

    def test_missing_subject_entity_detected(self):
        problems = validate_claims(
            [_claim(subject="cultivars/TCUL-9999")], ENTITIES
        )
        self.assertTrue(any("subject" in p and "not a content entity" in p for p in problems))

    def test_entity_object_must_exist(self):
        problems = validate_claims(
            [_claim(object="cultivars/TCUL-9999", object_is_entity=True)], ENTITIES
        )
        self.assertTrue(any("object" in p and "not a content entity" in p for p in problems))

    def test_free_text_object_allowed(self):
        claim = _claim(object="Sensi Seeds", object_is_entity=False)
        self.assertEqual(validate_claims([claim], ENTITIES), [])

    def test_self_referential_claim_detected(self):
        claim = _claim(
            subject="cultivars/TCUL-0001", object="cultivars/TCUL-0001",
            object_is_entity=True,
        )
        problems = validate_claims([claim], ENTITIES)
        self.assertTrue(any("self-referential" in p for p in problems))

    def test_unknown_status_detected(self):
        problems = validate_claims([_claim(status="95% sure")], ENTITIES)
        self.assertTrue(any("unknown status" in p for p in problems))

    def test_missing_source_detected(self):
        claim = _claim()
        del claim["source"]
        problems = validate_claims([claim], ENTITIES)
        self.assertTrue(any("missing source" in p for p in problems))

    def test_unknown_source_type_detected(self):
        problems = validate_claims(
            [_claim(source={"name": "x", "type": "marketing"})], ENTITIES
        )
        self.assertTrue(any("unknown source.type" in p for p in problems))

    def test_bad_retrieval_date_detected(self):
        problems = validate_claims(
            [_claim(source={"name": "x", "type": "archive", "retrieved": "yesterday"})],
            ENTITIES,
        )
        self.assertTrue(any("retrieved" in p for p in problems))

    def test_duplicate_claim_id_detected(self):
        problems = validate_claims([_claim(), _claim()], ENTITIES)
        self.assertTrue(any("duplicate claim_id" in p for p in problems))

    def test_disagreement_references_claim_ids(self):
        # source_disagrees_with subject/object are claim IDs, not entities.
        claim_a = _claim(claim_id="CLM-9001")
        claim_b = _claim(claim_id="CLM-9002")
        dispute = _claim(
            claim_id="CLM-9003", kind="source_disagrees_with",
            subject="CLM-9001", object="CLM-9002", status="conflicting",
        )
        self.assertEqual(validate_claims([claim_a, claim_b, dispute], ENTITIES), [])

    def test_disagreement_rejects_entity_references(self):
        dispute = _claim(
            claim_id="CLM-9003", kind="source_disagrees_with",
            subject="cultivars/TCUL-0001", object="cultivars/TCUL-0002",
            object_is_entity=True,
        )
        problems = validate_claims([dispute], ENTITIES)
        self.assertTrue(any("not a known claim ID" in p for p in problems))
        self.assertTrue(any("object_is_entity must not be true" in p for p in problems))

    def test_disagreement_rejects_missing_claim(self):
        dispute = _claim(
            claim_id="CLM-9003", kind="source_disagrees_with",
            subject="CLM-9001", object="CLM-9999",
        )
        problems = validate_claims([dispute], ENTITIES)
        self.assertTrue(any("CLM-9999" in p for p in problems))

    def test_disagreement_rejects_self_reference(self):
        dispute = _claim(
            claim_id="CLM-9003", kind="source_disagrees_with",
            subject="CLM-9001", object="CLM-9001",
        )
        problems = validate_claims([dispute], ENTITIES)
        self.assertTrue(any("self-referential" in p for p in problems))


class RenderingTestCase(unittest.TestCase):
    def test_claimed_kind_keeps_epistemic_language(self):
        text = render_claim_context(_claim())
        self.assertIn("is claimed to have been bred by", text)
        self.assertIn("Per Archive page (archive, retrieved 2026-08-09)", text)
        self.assertIn("Status: claimed", text)

    def test_product_claim_renders_label_relationship(self):
        claim = _claim(
            kind="product_claims_cultivar",
            subject="products/TPRD-0001",
            object="cultivars/TCUL-0001",
            object_is_entity=True,
            wording="Cultivar Lineage: Blue Dream",
        )
        text = render_claim_context(claim)
        self.assertIn("product record products/TPRD-0001 is labeled as", text)
        self.assertIn("Wording", text)

    def test_evidence_backed_kind_uses_states(self):
        claim = _claim(kind="bred_by")
        text = render_claim_context(claim)
        self.assertIn("was bred by", text)
        self.assertNotIn("is claimed to", text)

    def test_disagreement_renders_both_sides(self):
        claim_a = _claim(claim_id="CLM-9001", object="Kyle Kushman / Dutch Passion")
        claim_b = _claim(claim_id="CLM-9002", object="Jeff Cavanagh")
        dispute = _claim(
            claim_id="CLM-9003", kind="source_disagrees_with",
            subject="CLM-9001", object="CLM-9002", status="conflicting",
        )
        text = render_claim_context(
            dispute, claims_by_id={"CLM-9001": claim_a, "CLM-9002": claim_b}
        )
        self.assertIn("attribution of cultivars/TCUL-0001 is disputed", text)
        self.assertIn("CLM-9001 (Kyle Kushman / Dutch Passion)", text)
        self.assertIn("CLM-9002 (Jeff Cavanagh)", text)
        self.assertIn("Status: conflicting", text)

    def test_disagreement_falls_back_without_lookup(self):
        dispute = _claim(
            claim_id="CLM-9003", kind="source_disagrees_with",
            subject="CLM-9001", object="CLM-9002",
        )
        text = render_claim_context(dispute)
        self.assertIn("claim CLM-9001 disagrees with claim CLM-9002", text)


class RealRegistryTestCase(unittest.TestCase):
    def test_real_registry_validates_against_real_content(self):
        self.assertTrue(REAL_REGISTRY.is_file(), "registry missing")
        claims = load_claims(REAL_REGISTRY)
        entity_ids = collect_entity_ids(REAL_CONTENT)
        self.assertEqual(
            validate_claims(claims, entity_ids), [],
            "real registry must validate clean against the content tree",
        )
        self.assertGreaterEqual(len(claims), 1)

    def test_real_registry_covers_product_and_batch_claims(self):
        claims = load_claims(REAL_REGISTRY)
        kinds = {claim["kind"] for claim in claims}
        self.assertIn("product_claims_cultivar", kinds)
        self.assertIn("batch_claims_cultivar", kinds)

    def test_no_fabricated_seed_listings(self):
        # The repository has no seed-bank listing evidence yet; the registry
        # must not invent any.
        claims = load_claims(REAL_REGISTRY)
        for claim in claims:
            self.assertNotIn(
                claim["kind"], {"sold_by", "listed_by", "seed_source"},
                f"{claim['claim_id']} fabricates a seed-bank listing",
            )

    def test_well_supported_claims_carry_source_urls(self):
        # Upgrade invariant: a claim cannot be well-supported without an
        # attached primary-source URL (see model doc §4 rule 6).
        claims = load_claims(REAL_REGISTRY)
        for claim in claims:
            if claim["status"] == "well_supported":
                self.assertTrue(
                    claim["source"].get("url", "").startswith("http"),
                    f"{claim['claim_id']} is well_supported but has no source URL",
                )

    def test_dispute_pair_is_first_class(self):
        claims = load_claims(REAL_REGISTRY)
        by_id = {claim["claim_id"]: claim for claim in claims}
        disputes = [c for c in claims if c["kind"] == "source_disagrees_with"]
        self.assertEqual(len(disputes), 1)
        dispute = disputes[0]
        self.assertIn(dispute["subject"], by_id)
        self.assertIn(dispute["object"], by_id)
        self.assertEqual(dispute["status"], "conflicting")
        self.assertEqual(by_id[dispute["subject"]]["subject"], "cultivars/TCUL-0008")
        self.assertEqual(by_id[dispute["object"]]["subject"], "cultivars/TCUL-0008")

    def test_registry_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.jsonl"
            claims = load_claims(REAL_REGISTRY)
            with path.open("w", encoding="utf-8") as handle:
                for claim in claims:
                    import json
                    handle.write(json.dumps(claim, ensure_ascii=False) + "\n")
            self.assertEqual(load_claims(path), claims)


if __name__ == "__main__":
    unittest.main()
