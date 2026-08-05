#!/usr/bin/env python3
"""Serve a built site locally WITH the committed _headers security headers.

`python3 -m http.server` cannot send custom headers, so Cloudflare-specific
headers (Content-Security-Policy, etc.) are invisible in local previews.
This tiny server parses the `_headers` manifest from the build output and
applies matching rules, so maintainers can verify headers and check the
browser console for CSP violations before deploying.

Usage:

    ./scripts/ted-build.sh                 # builds dist/cantilever (+ _headers)
    python3 scripts/serve-headers.py       # serves dist/cantilever on :8000
    python3 scripts/serve-headers.py dist/cantilever 8080

Only the `/*` global section and exact/wildcard path rules are honored;
`/*` is applied to everything, and longer explicit rules override it.
"""

from __future__ import annotations

import argparse
import fnmatch
import http.server
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def parse_headers(text: str) -> List[Tuple[str, Dict[str, str]]]:
    rules: List[Tuple[str, Dict[str, str]]] = []
    current_path: str | None = None
    current_headers: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            if current_path is not None:
                rules.append((current_path, dict(current_headers)))
            current_path = line.strip()
            current_headers = {}
        else:
            if ":" in line:
                name, value = line.strip().split(":", 1)
                current_headers[name.strip()] = value.strip()
    if current_path is not None:
        rules.append((current_path, dict(current_headers)))
    return rules


def match_rule(rule_path: str, request_path: str) -> bool:
    if rule_path == "/*":
        return True
    if "*" in rule_path:
        return fnmatch.fnmatch(request_path, rule_path.lstrip("/"))
    return request_path == rule_path


class HeaderHandler(http.server.SimpleHTTPRequestHandler):
    rules: List[Tuple[str, Dict[str, str]]] = []

    def end_headers(self) -> None:
        for rule_path, headers in self.rules:
            if match_rule(rule_path, self.path.split("?", 1)[0]):
                for name, value in headers.items():
                    self.send_header(name, value)
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[serve-headers] %s\n" % (fmt % args))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist/cantilever"),
                        help="built site directory (must contain _headers)")
    parser.add_argument("port", nargs="?", type=int, default=8000)
    args = parser.parse_args()

    headers_path = args.directory / "_headers"
    if not headers_path.is_file():
        print("serve-headers: no {} found; run ./scripts/ted-build.sh first".format(headers_path),
              file=sys.stderr)
        return 2

    HeaderHandler.rules = parse_headers(headers_path.read_text(encoding="utf-8"))
    handler = lambda *a, **kw: HeaderHandler(*a, directory=str(args.directory), **kw)  # noqa: E731
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print("serve-headers: http://127.0.0.1:{} ({} rules from {})".format(
        args.port, len(HeaderHandler.rules), headers_path))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
