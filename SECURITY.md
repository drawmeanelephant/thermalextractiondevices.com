# Security Policy

## Reporting a vulnerability

**Pre-publication note:** this repository is not yet public. Until it is,
route reports through the repository owner's private channel. The contact
address below is a **placeholder** — it must be replaced with a real,
monitored mailbox before public release (blocker in the pre-publication
checklist).

| Channel | Address / route |
| --- | --- |
| Private security mailbox (placeholder — REPLACE) | `security@example.com` |
| GitHub private advisory (once public) | repository → Security → *Report a vulnerability* |

Please do **not** open a public issue for a security defect. Provide:

1. A short summary and severity estimate.
2. The affected file(s)/commit(s) and reproduction steps.
3. Any suggested fix.

Reports are acknowledged within 5 business days. Non-security issues belong
in the issue tracker.

## Supported versions

* The site is compiled with **Boris**, pinned by commit in
  `metadata/boris-version.json` (checked out exactly; never floating).
* The Zig toolchain version and SHA-256 checksums for each platform are
  pinned in the same file and verified before download.
* Only the current production build is supported; there are no long-term
  support branches.

## Security posture (already in place)

* No secrets, API keys, or credentials are committed. The only credential
  material in CI are GitHub Actions secrets referenced by name
  (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`).
* The build toolchain is reproducible-ish: CI builds Boris from a pinned
  Zig 0.16.0 toolchain (`mlugg/setup-zig`) and clones the Boris source from
  the `afterparty` branch (`.github/workflows/ci.yml`). Improvement
  opportunity before public release: pin the Boris commit SHA instead of a
  moving branch.
* CI uses least-privilege workflow permissions (`contents: read`).
* The deployed site sets security headers — including
  `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`,
  `Permissions-Policy`, `Cross-Origin-Opener-Policy`, and
  `X-Frame-Options` — via the committed `_headers` manifest (see
  `docs/pre-publication-checklist.md`).
* Public-release audits run in CI (`scripts/audit_public_release.py`),
  scanning for secrets, PII, personal paths, giant files, generated
  artifacts, missing policy documents, and absent headers.

## Supply-chain notes

* Dependencies are minimized: one pinned compiler (Boris) and the pinned Zig
  toolchain used to build it. There is no package-manager dependency tree to
  audit beyond that.
* Before a release, re-verify the pinned Boris commit is the intended one
  and re-run `scripts/audit_public_release.py --config docs/audit-config.json`.

## Reporting a data-correction or takedown

Content-related requests (inaccurate data, takedown of records about a
person or business) are governed by the correction process in
`DATA_SOURCES.md` and `PRIVACY.md`; they are handled separately from
security reports.
