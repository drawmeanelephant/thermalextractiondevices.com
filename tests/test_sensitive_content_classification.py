"""Unit tests for business-contact classification in scripts/audit_sensitive_content.py.

PRIVACY.md category 4 prohibits "personal email addresses, phone numbers, physical
addresses ... of individuals or private premises". Category 5 covers "content naming
identifiable businesses (producers, manufacturers, labs)" and is flagged REV-001 for
maintainer sign-off.

These tests pin that distinction. The negative controls matter more than the positive
ones: a rule that downgrades business contacts must never downgrade a personal address,
and must never touch the raw ingest payloads under data/.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# audit_sensitive_content imports its shared helpers as a bare `audit_common`
# module, so scripts/ must be importable directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_sensitive_content import _scan_text  # noqa: E402


def scan(text: str, rel_path: str):
    findings: list = []
    _scan_text(text, rel_path, {"allowlist": {}}, findings)
    return findings


def codes(findings) -> set[str]:
    return {f.code for f in findings}


def by_code(findings, code: str):
    return [f for f in findings if f.code == code]


class BusinessContactClassification(unittest.TestCase):
    # --- role mailboxes on published content are category 5 -----------------

    def test_role_mailbox_on_content_is_review_not_blocker(self):
        f = scan("| Contact | support@example.com |", "content/manufacturers/TMFR-0001.md")
        self.assertIn("REV-001", codes(f))
        self.assertNotIn("PII-001", codes(f))
        self.assertEqual(by_code(f, "REV-001")[0].severity, "medium")

    def test_recall_contact_is_not_blocked(self):
        """A product-safety recall contact is exactly what this archive should publish."""
        line = "contact Arizer for a free replacement: recall@arizer.com or 888-291-0521."
        f = scan(line, "content/devices/TED-0001.md")
        self.assertNotIn("PII-001", codes(f))
        self.assertNotIn("PII-002", codes(f))
        self.assertEqual(len(by_code(f, "REV-001")), 2)  # the email and its phone

    def test_phone_on_same_line_as_role_mailbox_is_review(self):
        f = scan("| Contact | support@x.com \u00b7 561-529-9001 |", "content/manufacturers/TMFR-0004.md")
        self.assertNotIn("PII-002", codes(f))
        self.assertEqual(len(by_code(f, "REV-001")), 2)

    def test_manufacturer_business_address_is_review(self):
        f = scan("| HQ | 5016 Schuster St |", "content/manufacturers/TMFR-0009.md")
        self.assertIn("REV-001", codes(f))
        self.assertNotIn("PII-003", codes(f))

    # --- negative controls: the rule must not over-reach --------------------

    def test_personal_email_on_content_still_blocks(self):
        f = scan("reach john.smith@gmail.com directly", "content/manufacturers/TMFR-0001.md")
        self.assertIn("PII-001", codes(f))
        self.assertNotIn("REV-001", codes(f))

    def test_role_mailbox_in_data_still_blocks(self):
        """Raw ingest payloads stay category 4 — 96.5% of those emails are personal."""
        f = scan('{"email":"info@licensee.com"}', "data/dcc/license-registry/latest.json")
        self.assertIn("PII-001", codes(f))
        self.assertNotIn("REV-001", codes(f))

    def test_phone_in_data_still_blocks(self):
        f = scan('{"phone":"561-529-9001"}', "data/dcc/license-registry/latest.json")
        self.assertIn("PII-002", codes(f))

    def test_bare_phone_on_content_without_role_mailbox_still_blocks(self):
        """Only a phone sharing a line with a functional mailbox is a business line."""
        f = scan("call 415-555-0142 for the grower", "content/manufacturers/TMFR-0001.md")
        self.assertIn("PII-002", codes(f))
        self.assertNotIn("REV-001", codes(f))

    def test_address_outside_manufacturer_records_still_blocks(self):
        f = scan("premises at 742 Evergreen Terrace Drive", "content/licenses/TLIC-0001.md")
        self.assertIn("PII-003", codes(f))

    def test_personal_email_in_data_still_blocks(self):
        f = scan('{"email":"grower.jane@gmail.com"}', "data/dcc/license-registry/latest.json")
        self.assertIn("PII-001", codes(f))

    # --- the detector still detects ----------------------------------------

    def test_secrets_and_coordinates_unaffected(self):
        f = scan("lat 37.774900, -122.419400", "content/manufacturers/TMFR-0001.md")
        self.assertIn("PII-004", codes(f))


if __name__ == "__main__":
    unittest.main()
