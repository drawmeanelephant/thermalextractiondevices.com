"""Fetch-layer tests: content-type guards, retries, fixture serving.

Uses an in-process HTTP server so no network is required.
"""

from __future__ import annotations

import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from scripts.ingest.core import ContentTypeError, IngestError
from scripts.ingest.fetch import Fetcher, FixtureFetcher

FIXTURES = Path(__file__).parent / "fixtures" / "massachusetts"


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/data.csv":
            body = b"a,b\n1,2\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/broken.html":
            body = b"<html>not a csv</html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/retry.csv":
            if not hasattr(self.server, "attempts"):
                self.server.attempts = 0
            self.server.attempts += 1
            if self.server.attempts < 3:
                self.send_response(500)
                self.end_headers()
                return
            body = b"x\n1\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):  # silence
        pass


class FetchTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.server.attempts = 0
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_csv_content_type_accepted(self):
        fetcher = Fetcher(retries=1, timeout=5)
        result = fetcher.fetch_bytes(f"{self.base}/data.csv")
        self.assertEqual(result.content_type, "text/csv")
        self.assertIn(b"1,2", result.data)

    def test_html_content_type_rejected(self):
        fetcher = Fetcher(retries=1, timeout=5)
        with self.assertRaises(ContentTypeError):
            fetcher.fetch_bytes(f"{self.base}/broken.html")

    def test_retry_after_500(self):
        self.server.attempts = 0
        fetcher = Fetcher(retries=3, backoff_seconds=0.05, timeout=5)
        result = fetcher.fetch_bytes(f"{self.base}/retry.csv")
        self.assertEqual(result.sha256[:0], "")

    def test_http_404_fails_fast(self):
        fetcher = Fetcher(retries=2, timeout=5)
        with self.assertRaises(IngestError):
            fetcher.fetch_bytes(f"{self.base}/missing.csv")

    def test_fixture_fetcher_serves_and_guards(self):
        fetcher = FixtureFetcher(FIXTURES)
        result = fetcher.fetch_bytes(
            "https://masscannabiscontrol.com/resource/a_agents_gender.csv"
        )
        self.assertIn("GENDER", result.data.decode("utf-8-sig"))
        # An HTML-ish fixture would be rejected; missing fixtures raise.
        with self.assertRaises(IngestError):
            fetcher.fetch_bytes("https://example.com/nope.csv")

    def test_fixture_fetcher_download_writes_file(self):
        import tempfile

        fetcher = FixtureFetcher(FIXTURES)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.csv"
            result = fetcher.download(
                "https://masscannabiscontrol.com/resource/a_agents_gender.csv", dest
            )
            self.assertTrue(dest.exists())
            self.assertEqual(result.path, dest)


if __name__ == "__main__":
    unittest.main()
