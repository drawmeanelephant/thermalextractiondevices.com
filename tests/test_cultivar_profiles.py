"""Tests for the normalized cultivar batch-profile model (scripts/cultivar_profiles.py)."""

from __future__ import annotations

import unittest

from scripts.cultivar_profiles import (
    AnalyteMeasurement,
    BatchProfile,
    Basis,
    Censoring,
    DecarbConvention,
    RecordKind,
    aitchison_distance,
    censorship_summary,
    clr_transform,
    numeric_value,
    profile_matrix,
    profile_warnings,
    reporting_rate,
    validate_profile,
)


def measurement(
    compound_id: str = "cannabinoids/TCBN-0002",
    censoring: Censoring = Censoring.NUMERIC,
    value: float | None = 5.0,
    lod: float | None = None,
    loq: float | None = None,
    unit: str = "mg/g",
) -> AnalyteMeasurement:
    return AnalyteMeasurement(
        compound_id=compound_id,
        compound_name="CBD",
        unit=unit,
        censoring=censoring,
        method="HPLC-UV",
        value=value,
        lod=lod,
        loq=loq,
    )


def profile(
    analytes: tuple[AnalyteMeasurement, ...],
    record_kind: RecordKind = RecordKind.VERIFIED,
    batch_id: str = "BR-BD-20260315-123",
    lab_report_id: str = "lab-results/TLAB-0101",
) -> BatchProfile:
    return BatchProfile(
        batch_id=batch_id,
        lab_report_id=lab_report_id,
        producer_id="organizations/TORG-0001",
        product_id="products/TPRD-0001",
        cultivar_labels=("Blue Dream",),
        sample_type="flower",
        basis=Basis.DRY_WEIGHT,
        decarb_convention=DecarbConvention.TOTAL_POTENTIAL,
        record_kind=record_kind,
        analytes=analytes,
        jurisdiction="CA",
    )


class MeasurementValidationTests(unittest.TestCase):
    def test_numeric_requires_value(self):
        with self.assertRaises(ValueError):
            measurement(censoring=Censoring.NUMERIC, value=None)

    def test_censored_must_not_carry_value(self):
        with self.assertRaises(ValueError):
            measurement(censoring=Censoring.ND, value=0.0)

    def test_below_lod_requires_lod(self):
        with self.assertRaises(ValueError):
            measurement(censoring=Censoring.BELOW_LOD, value=None, lod=None)

    def test_below_loq_requires_loq(self):
        with self.assertRaises(ValueError):
            measurement(censoring=Censoring.BELOW_LOQ, value=None, loq=None)

    def test_nd_should_record_lod(self):
        # Enforced as a soft rule: nd without lod is a warning, not an error.
        from scripts.cultivar_profiles import validate_measurement

        self.assertTrue(validate_measurement(measurement(censoring=Censoring.ND, value=None)))
        self.assertFalse(
            validate_measurement(measurement(censoring=Censoring.ND, value=None, lod=0.01))
        )


class CensoringTests(unittest.TestCase):
    def test_numeric_value_never_imputes(self):
        m = measurement(censoring=Censoring.BELOW_LOQ, value=None, loq=1.0)
        self.assertIsNone(numeric_value(m))
        m2 = measurement(censoring=Censoring.ND, value=None, lod=0.05)
        self.assertIsNone(numeric_value(m2))
        self.assertEqual(numeric_value(measurement()), 5.0)

    def test_censorship_summary_counts(self):
        p = profile(
            (
                measurement(compound_id="a"),
                measurement(compound_id="b", censoring=Censoring.ND, value=None, lod=0.01),
                measurement(
                    compound_id="c", censoring=Censoring.BELOW_LOQ, value=None, loq=0.1
                ),
                measurement(
                    compound_id="d", censoring=Censoring.NOT_TESTED, value=None
                ),
            )
        )
        summary = censorship_summary(p)
        self.assertEqual(summary["numeric"], 1)
        self.assertEqual(summary["nd"], 1)
        self.assertEqual(summary["below_loq"], 1)
        self.assertEqual(summary["not_tested"], 1)

    def test_reporting_rate(self):
        p = profile(
            (
                measurement(compound_id="a"),
                measurement(compound_id="b", censoring=Censoring.ND, value=None, lod=0.01),
                measurement(compound_id="c", censoring=Censoring.NOT_TESTED, value=None),
            )
        )
        self.assertEqual(reporting_rate(p), 0.5)
        untested = profile((measurement(compound_id="a", censoring=Censoring.NOT_TESTED, value=None),))
        self.assertIsNone(reporting_rate(untested))


class ProfileValidationTests(unittest.TestCase):
    def test_mixed_units_allowed(self):
        # Real COAs mix units (% w/w cannabinoids, mg/g terpenes, ppm
        # pesticides). Comparison/composition requires explicit normalization
        # into a compatible analyte subset, not wholesale rejection.
        other = AnalyteMeasurement(
            compound_id="terpenes/TTRP-0005",
            compound_name="β-Myrcene",
            unit="% w/w",
            censoring=Censoring.NUMERIC,
            method="GC-FID",
            value=0.5,
        )
        p = profile((measurement(), other))
        self.assertEqual(len(p.analytes), 2)
        self.assertEqual(validate_profile(p), [])

    def test_duplicate_analyte_rejected(self):
        with self.assertRaises(ValueError):
            profile((measurement(compound_id="a"), measurement(compound_id="a")))

    def test_empty_analytes_rejected(self):
        with self.assertRaises(ValueError):
            profile(())

    def test_producer_product_id_accept_real_null(self):
        p = BatchProfile(
            batch_id="BR-BD-20260315-123",
            lab_report_id="lab-results/TLAB-0101",
            producer_id=None,
            product_id=None,
            cultivar_labels=("Blue Dream",),
            sample_type="flower",
            basis=Basis.DRY_WEIGHT,
            decarb_convention=DecarbConvention.TOTAL_POTENTIAL,
            record_kind=RecordKind.VERIFIED,
            analytes=(measurement(),),
        )
        self.assertIsNone(p.producer_id)
        self.assertIsNone(p.product_id)
        self.assertEqual(validate_profile(p), [])

    def test_literal_null_string_rejected(self):
        # The old schema permitted the literal string "null"; only real JSON
        # null is acceptable.
        with self.assertRaises(ValueError):
            BatchProfile(
                batch_id="BR-BD-20260315-123",
                lab_report_id="lab-results/TLAB-0101",
                producer_id="null",
                product_id="products/TPRD-0001",
                cultivar_labels=("Blue Dream",),
                sample_type="flower",
                basis=Basis.DRY_WEIGHT,
                decarb_convention=DecarbConvention.TOTAL_POTENTIAL,
                record_kind=RecordKind.VERIFIED,
                analytes=(measurement(),),
            )

    def test_report_identity_distinct_from_batch_identity(self):
        # One commercial batch may have retests/corrected reports: several
        # lab_report_ids share one batch_id and remain distinct entities.
        first = profile((measurement(),), lab_report_id="lab-results/TLAB-0101")
        retest = profile((measurement(),), lab_report_id="lab-results/TLAB-0102")
        self.assertEqual(first.batch_id, retest.batch_id)
        self.assertNotEqual(first.lab_report_id, retest.lab_report_id)

    def test_lab_report_id_must_be_canonical(self):
        # Report identity is a canonical lab-results/TLAB-XXXX record id, not
        # a free-form COA string.
        with self.assertRaises(ValueError):
            BatchProfile(
                batch_id="BR-BD-20260315-123",
                lab_report_id="COA-101",
                producer_id="organizations/TORG-0001",
                product_id="products/TPRD-0001",
                cultivar_labels=("Blue Dream",),
                sample_type="flower",
                basis=Basis.DRY_WEIGHT,
                decarb_convention=DecarbConvention.TOTAL_POTENTIAL,
                record_kind=RecordKind.VERIFIED,
                analytes=(measurement(),),
            )


class SoftWarningTests(unittest.TestCase):
    def test_nd_without_lod_is_soft_not_hard(self):
        # The documented soft warning must not become a hard error at
        # BatchProfile construction.
        p = profile(
            (measurement(compound_id="a", censoring=Censoring.ND, value=None),)
        )
        self.assertEqual(validate_profile(p), [])
        self.assertTrue(any("lod" in w for w in profile_warnings(p)))

    def test_nd_with_lod_has_no_warning(self):
        p = profile(
            (measurement(compound_id="a", censoring=Censoring.ND, value=None, lod=0.01),)
        )
        self.assertEqual(profile_warnings(p), [])


class CompositionalTests(unittest.TestCase):
    def test_clr_requires_positive(self):
        with self.assertRaises(ValueError):
            clr_transform([0.0, 1.0])
        with self.assertRaises(ValueError):
            clr_transform([-1.0, 1.0])

    def test_clr_constant_vector_is_zero(self):
        self.assertEqual(clr_transform([1.0, 1.0, 1.0]), [0.0, 0.0, 0.0])

    def test_aitchison_distance_scale_invariant(self):
        self.assertAlmostEqual(aitchison_distance([1, 1, 1], [2, 2, 2]), 0.0, places=9)
        d = aitchison_distance([0.5, 0.25, 0.25], [0.25, 0.25, 0.5])
        self.assertGreater(d, 0.0)

    def test_aitchison_distance_length_mismatch(self):
        with self.assertRaises(ValueError):
            aitchison_distance([1.0, 1.0], [1.0, 1.0, 1.0])


class ProfileMatrixTests(unittest.TestCase):
    def test_matrix_excludes_non_verified_records(self):
        verified = profile(
            (measurement(compound_id="cannabinoids/TCBN-0002"),), record_kind=RecordKind.VERIFIED
        )
        demo = profile(
            (measurement(compound_id="cannabinoids/TCBN-0002"),), record_kind=RecordKind.DEMONSTRATION
        )
        unverified = profile(
            (measurement(compound_id="cannabinoids/TCBN-0002"),), record_kind=RecordKind.UNVERIFIED
        )
        rows, matrix = profile_matrix([verified, demo, unverified], ["cannabinoids/TCBN-0002"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(matrix), ["lab-results/TLAB-0101"])

    def test_matrix_rows_keyed_by_report_id(self):
        # Retests of the same batch are separate rows (one per report).
        first = profile((measurement(),), lab_report_id="lab-results/TLAB-0101")
        retest = profile((measurement(),), lab_report_id="lab-results/TLAB-0102")
        rows, matrix = profile_matrix([first, retest], ["cannabinoids/TCBN-0002"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(list(matrix), ["lab-results/TLAB-0101", "lab-results/TLAB-0102"])

    def test_matrix_keeps_censored_as_none(self):
        p = profile(
            (
                measurement(compound_id="a", value=5.0),
                measurement(compound_id="b", censoring=Censoring.ND, value=None, lod=0.01),
            )
        )
        _, matrix = profile_matrix([p], ["a", "b"])
        self.assertEqual(matrix[p.lab_report_id]["a"], 5.0)
        self.assertIsNone(matrix[p.lab_report_id]["b"])


if __name__ == "__main__":
    unittest.main()
