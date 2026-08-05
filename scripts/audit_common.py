#!/usr/bin/env python3
"""Shared helpers for the Thermal Extraction Devices public-release audits.

Provides the finding model, default configuration with allowlists and
suppressions, configuration loading, and small scanning utilities used by:

* ``audit_public_release.py``   (orchestrator)
* ``audit_sensitive_content.py`` (secrets / PII / personal paths)
* ``audit_large_files.py``      (giant files / history blobs / duplicates)

All three scripts accept ``--config`` pointing at a JSON file that deep-merges
over these defaults, so allowlists and suppressions stay explicit and
reviewable instead of being silently baked into code.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

# Extensions scanned for sensitive content in the working tree.
DEFAULT_SCAN_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".py", ".sh", ".bash", ".yml", ".yaml",
    ".json", ".jsonc", ".jsonl", ".toml", ".cfg", ".conf", ".ini", ".env",
    ".html", ".css", ".js", ".xml", ".csv", ".tsv",
}

# File names that always warrant a secret/credential review when tracked.
CREDENTIAL_FILE_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    ".pypirc", ".netrc", ".npmrc", ".htpasswd",
    "id_rsa", "id_ed25519", "id_dsa", "id_ecdsa",
    "credentials", "credentials.json", "secrets", "secrets.json",
    "service-account.json", "client-secret.json",
}
CREDENTIAL_FILE_SUFFIXES = {
    ".pem", ".key", ".p12", ".pfx", ".keystore", ".jks", ".ppk",
    ".pgp", ".gpg", ".asc",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "thresholds": {
        # Files/blobs at or above this many bytes are "giant tracked files".
        "large_file_bytes": 5_000_000,
        # Files at or above this size are surfaced for human review.
        "review_file_bytes": 1_000_000,
        # How many entries to print in large-file / blob reports.
        "report_limit": 25,
    },
    # Field names whose mere presence is a sensitive-data signal (PII-007).
    # Config-driven: extend in docs/audit-config.json, never by editing code.
    "prohibited_fields": [],
    "allowlist": {
        # Substrings that make an otherwise-suspicious email acceptable.
        "emails": ["@users.noreply.github.com", "@example.com", "@example.org"],
        # Regexes; a secret match inside any of these is ignored.
        "secrets": [
            r"\$\{\{\s*secrets\.[A-Za-z0-9_]+\s*\}\}",   # GitHub Actions
            r"\$\{\{\s*env\.[A-Za-z0-9_]+\s*\}\}",
            r"BORIS_[A-Z_]+",                            # documented build vars
            r"CLOUDFLARE_API_TOKEN|CLOUDFLARE_ACCOUNT_ID",
        ],
        # Personal-path substrings to ignore (e.g. inside test fixtures).
        "personal_paths": [],
        "phones": [],
        "addresses": [],
        "coordinates": [],
        "tax_ids": [],
        # Paths (repo-relative) excluded from size findings.
        "large_files": [],
        # SHA-256 prefixes of blobs ignored by the duplicate-blob report.
        "duplicate_blobs": [],
        # Paths excluded from the human-review report.
        "human_review": [],
        # Paths that may legitimately look like generated artifacts.
        "generated_artifacts": ["metadata/id-map.jsonl"],
    },
    # Finding codes ("SEC-001") or exact "CODE:path" pairs to suppress.
    "suppressions": [],
    # Findings at or above this severity fail the audit (exit code 1).
    "fail_threshold": "high",
    # Root-relative required policy documents. Any missing item is POL-001.
    "required_policy_documents": [
        "README.md",
        "LICENSE.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "DATA_SOURCES.md",
        "PRIVACY.md",
        "docs/pre-publication-checklist.md",
        "docs/artifact-storage.md",
    ],
    # Paths that host third-party or regulated data and therefore need
    # explicit human sign-off before public release (REV-001 findings).
    "human_review_paths": [
        "content/lab-results/",
        "content/products/",
        "content/law-and-use/",
        "content/manufacturers/",
        "content/guides/manufacturer-research-queue.md",
    ],
    # Recommended response headers, with the severity of their absence.
    "recommended_headers": {
        "Content-Security-Policy": "critical",
        "X-Content-Type-Options": "high",
        "Referrer-Policy": "medium",
        "Permissions-Policy": "medium",
        "Cross-Origin-Opener-Policy": "medium",
        "X-Frame-Options": "high",
    },
    # Patterns that mark a committed path as a generated artifact.
    "generated_artifact_patterns": [
        r"(^|/)dist/", r"(^|/)publish/", r"(^|/)site/", r"(^|/)exports/",
        r"(^|/)\.tools/", r"(^|/)__pycache__/", r"\.pyc$",
        r"(^|/)node_modules/", r"(^|/)\.wrangler/", r"bin/boris$",
        r"bin/boris\.json$", r"(^|/)\.zig-cache/", r"(^|/)zig-out/",
    ],
    # Entries that must be present in .gitignore.
    "required_gitignore_entries": [
        "dist/", "publish/", "site/", "exports/", ".tools/", "node_modules/",
        "__pycache__/", "*.pyc", "bin/boris*", ".wrangler/", ".DS_Store",
        ".env", ".env.*",
    ],
}


@dataclass
class Finding:
    """A single audit finding with a stable, suppressible identity."""

    code: str
    severity: str
    message: str
    path: str = ""
    line: Optional[int] = None
    detail: str = ""

    @property
    def id(self) -> str:
        return self.code

    def key(self) -> str:
        """Stable identity used for suppressions: CODE or CODE:path."""
        return self.code if not self.path else "{}:{}".format(self.code, self.path)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "path": self.path,
            "line": self.line,
            "detail": self.detail,
            "id": self.key(),
        }


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``override`` into ``base`` (returning a new dict)."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    """Load and deep-merge an optional JSON config over the defaults."""
    config = deep_merge({}, DEFAULT_CONFIG)
    if path is not None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        config = deep_merge(config, data)
    return config


def is_suppressed(finding: Finding, config: Dict[str, Any]) -> bool:
    """True when the finding matches a configured suppression."""
    suppress = config.get("suppressions", [])
    if finding.key() in suppress or finding.code in suppress:
        return True
    for entry in suppress:
        if isinstance(entry, str) and entry.startswith(finding.code + ":"):
            if entry == finding.key():
                return True
    return False


def severity_rank(severity: str) -> int:
    return SEVERITY_RANK.get(severity, 0)


def is_blocking(finding: Finding, config: Dict[str, Any]) -> bool:
    """True when the finding meets the configured fail threshold."""
    threshold = severity_rank(str(config.get("fail_threshold", "high")))
    return severity_rank(finding.severity) >= threshold


def list_tracked_files(root: Path) -> List[str]:
    """Repo-relative paths of all files tracked by git (empty if not a repo)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, text=True, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    return [p for p in proc.stdout.split("\0") if p]


def is_generated_artifact(rel_path: str, config: Dict[str, Any]) -> bool:
    allowed = set(config.get("allowlist", {}).get("generated_artifacts", []))
    if rel_path in allowed:
        return False
    patterns = config.get("generated_artifact_patterns", [])
    return any(re.search(pattern, rel_path) for pattern in patterns)


def human_path(path: str) -> str:
    """Normalize a repo-relative path for display."""
    return path.replace("\\", "/")
