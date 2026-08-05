"""Optional live-source smoke test.

Normal unit tests must not require network access. Set ``INGEST_LIVE=1`` to
run this against the official Massachusetts CCC endpoints:

    INGEST_LIVE=1 python3 -m unittest tests.test_live_smoke -v
"""

from __future__ import annotations

import os
import unittest

import scripts.ingest.states.massachusetts as ma
from scripts.ingest.fetch import Fetcher

LIVE = os.environ.get("INGEST_LIVE") == "1"


@unittest.skipUnless(LIVE, "set INGEST_LIVE=1 to run live smoke tests")
class LiveSmokeTestCase(unittest.TestCase):
    def test_data_catalog_reachable(self):
        fetcher = Fetcher(timeout=30)
        result = fetcher.fetch_bytes(ma.REGULATOR["data_catalog"])
        self.assertIn("masscannabiscontrol", result.url)

    def test_advisories_page_lists_posts(self):
        fetcher = Fetcher(timeout=30)
        urls = ma.discover_advisory_urls(fetcher)
        self.assertGreaterEqual(len(urls), 1)
        for url in urls:
            html = fetcher.fetch_text(url)
            self.assertIn("Public Health and Safety Advisory", html)

    def test_small_dataset_fetches_as_csv(self):
        fetcher = Fetcher(timeout=60)
        spec = ma.DATASETS["price_per_gram"]
        result = fetcher.fetch_bytes(spec.csv_url)
        self.assertEqual(result.content_type, "text/csv")
        self.assertGreater(result.size_bytes, 500)


if __name__ == "__main__":
    unittest.main()
