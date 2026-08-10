"""Tests for the condition-aware cannabinoid thermal-property audit."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.audit_cannabinoid_thermal import audit_file


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "cannabinoid_thermal"


def findings(name: str):
    return audit_file(FIXTURE_DIR / name)


class CannabinoidThermalAuditTest(unittest.TestCase):
    def test_conditioned_fixture_is_clean(self):
        self.assertEqual(findings("clean.md"), [])

    def test_unconditioned_boiling_point_fails(self):
        self.assertIn("THERM-001", {code for _, code, _ in findings("unconditioned-boiling.md")})

    def test_unconditioned_vapor_pressure_fails(self):
        self.assertIn("THERM-002", {code for _, code, _ in findings("unconditioned-vapor-pressure.md")})

    def test_unconditioned_decomposition_fails(self):
        self.assertIn("THERM-003", {code for _, code, _ in findings("unconditioned-decomposition.md")})

    def test_missing_setpoint_sample_distinction_fails(self):
        self.assertIn("THERM-004", {code for _, code, _ in findings("missing-temperature-distinction.md")})


if __name__ == "__main__":
    unittest.main()
