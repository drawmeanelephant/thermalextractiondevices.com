#!/usr/bin/env python3
"""Refresh the tracked legacy URL map from current content and Git renames."""

from __future__ import annotations

import argparse
from pathlib import Path

from finalize_site import SiteFinalizationError, write_redirect_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", type=Path, default=Path("content"))
    parser.add_argument("--git-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("metadata/legacy-paths.json"),
    )
    args = parser.parse_args()
    try:
        count = write_redirect_manifest(args.content, args.git_root, args.output)
    except SiteFinalizationError as exc:
        parser.error(str(exc))
    print(f"update_legacy_paths: wrote {count} legacy paths to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
