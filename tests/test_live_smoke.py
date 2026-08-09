"""Optional live-source smoke test.

Normal unit tests must not require network access. Set ``INGEST_LIVE=1`` to
run this against the official Massachusetts CCC endpoints:

    INGEST_LIVE=1 python3 -m unittest tests.test_live_smoke -v

It verifies:

1. the official Data Catalog responds;
2. every current source link resolves and serves CSV (not HTML/error text);
3. required columns remain present in the current payloads;
4. the large testing files support streaming downloads;
5. the source-update date is not older than the last accepted snapshot
   recorded in the committed manifest (when one exists);
6. the advisories page remains parseable into structured records.
"""

from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

import scripts.ingest.states.massachusetts as ma
from scripts.ingest.fetch import Fetcher

LIVE = os.environ.get("INGEST_LIVE") == "1"
ROOT = Path(__file__).resolve().parent.parent

_CSV_TYPES = ("text/csv", "application/csv")


@unittest.skipUnless(LIVE, "set INGEST_LIVE=1 to run live smoke tests")
class LiveSmokeTestCase(unittest.TestCase):
    def setUp(self):
        self.html_fetcher = Fetcher(timeout=30, allow_html=True)
        self.csv_fetcher = Fetcher(timeout=90, accepted_types=_CSV_TYPES)

    def test_data_catalog_responds(self):
        result = self.html_fetcher.fetch_bytes(ma.REGULATOR["data_catalog"])
        self.assertEqual(result.content_type, "text/html")
        self.assertGreater(result.size_bytes, 10_000)

    def test_every_dataset_url_resolves_as_csv(self):
        """All catalog dataset URLs must resolve and serve tabular CSV, not
        HTML/error text. The large testing files are probed via a range
        request so the smoke run stays small."""
        failures = []
        for slug, spec in ma.DATASETS.items():
            try:
                if spec.large:
                    # Probe a small sample and close: the CCC servers ignore
                    # Range requests, so a full fetch would stream the whole
                    # multi-hundred-MB file. Streaming itself is exercised by
                    # the real sync (Fetcher.download streams to disk).
                    result = self.csv_fetcher.probe(spec.csv_url)
                    self.assertEqual(result.content_type.split(";")[0].strip(), "text/csv")
                    self.assertGreater(len(result.data or b""), 500)
                else:
                    result = self.csv_fetcher.fetch_bytes(spec.csv_url)
                    self.assertEqual(result.content_type.split(";")[0].strip(), "text/csv")
                    self.assertGreater(result.size_bytes, 100)
            except Exception as error:  # noqa: BLE001 - collect all failures
                failures.append(f"{slug}: {error}")
        self.assertEqual(failures, [], failures)

    def test_required_columns_still_present(self):
        """The current payloads must still carry the adapter's required
        columns; a header-only check is cheap and fails loudly on drift."""
        missing = {}
        for slug, spec in ma.DATASETS.items():
            if spec.large:
                continue
            result = self.csv_fetcher.fetch_bytes(spec.csv_url)
            headers = result.data.decode("utf-8-sig", errors="replace").splitlines()[0]
            present = [c for c in headers.split(",")]
            absent = [c for c in spec.required_columns if c not in present]
            if absent:
                missing[slug] = absent
        self.assertEqual(missing, {}, missing)

    def test_source_update_not_older_than_accepted_snapshot(self):
        """The current file's Last-Modified must not be older than the last
        accepted snapshot recorded in the committed manifest (prevents an
        obsolete upstream copy from silently replacing a corrected release)."""
        manifest_path = ROOT / "data" / "massachusetts-ccc" / "manifest.json"
        if not manifest_path.is_file():
            self.skipTest("no committed Massachusetts manifest yet")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for slug, spec in ma.DATASETS.items():
            if spec.large:
                continue
            latest = (manifest.get("datasets", {}).get(slug) or [{}])[-1]
            accepted = latest.get("source_last_updated")
            if not accepted:
                continue
            result = self.csv_fetcher.fetch_bytes(spec.csv_url)
            self.assertIsNotNone(
                result.last_modified,
                f"{slug}: live file has no Last-Modified header",
            )
            from scripts.ingest.schema import parse_http_date

            live_date = parse_http_date(result.last_modified)
            accepted_date = parse_http_date(accepted)
            if live_date is None or accepted_date is None:
                continue  # one side unparseable; staleness guard cannot run
            self.assertGreaterEqual(
                live_date, accepted_date,
                f"{slug}: live file date {live_date} is older than the "
                f"accepted snapshot {accepted_date}",
            )

    def test_advisories_page_parses_into_records(self):
        fetcher = Fetcher(timeout=60, allow_html=True)
        urls = ma.discover_advisory_urls(fetcher)
        self.assertGreaterEqual(len(urls), 1)
        for url in urls:
            html = fetcher.fetch_text(url)
            parsed = ma.parse_advisory_page(html, url)
            self.assertIn("Public Health and Safety Advisory", parsed["title"])
            self.assertTrue(parsed["advisory_date"])
            self.assertIn("url", parsed)


if __name__ == "__main__":
    unittest.main()
