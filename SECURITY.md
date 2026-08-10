# Security Policy

## Reporting a vulnerability

This repository is public. Use GitHub's private vulnerability-reporting flow
from the repository's **Security** tab when it is available. Do not include
secrets or sensitive exploit details in a public issue.

| Channel | Address / route |
| --- | --- |
| Private security report | repository → Security → *Report a vulnerability* |

Please do **not** open a public issue for a security defect. Provide:

1. A short summary and severity estimate.
2. The affected file(s)/commit(s) and reproduction steps.
3. Any suggested fix.

There is no published response-time SLA. Non-security issues belong in the
issue tracker; if private reporting is unavailable, contact the repository
owner through an authenticated GitHub channel before disclosing details.

## Supported versions

* The site is compiled with **Boris**, pinned by repository and full commit SHA
  in `metadata/boris-version.json` (checked out exactly; never selected by a
  floating branch).
* The Zig toolchain version and SHA-256 checksums for each platform are
  pinned in the same file and verified before download.
* Only the current production build is supported; there are no long-term
  support branches.

## Security posture (already in place)

* No secrets, API keys, or credentials are committed. The only credential
  material in CI are GitHub Actions secrets referenced by name
  (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`).
* CI and deploy build Boris from the Zig version in
  `metadata/boris-version.json` (`mlugg/setup-zig`) and fetch the exact Boris
  repository and commit recorded there. The workflows verify both the remote
  URL and checked-out `HEAD`; a moving branch is never used to select source.
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
