# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- Renamed the manifest inheritance fields `brad_engine` / `brad_engine_sha256`
  to `baseline` / `baseline_sha256` across writers, readers, the intake schema,
  and the architecture docs (the audit inheritance gate reads the new names).
- Replaced retired internal vocabulary with neutral public terms throughout the
  source, templates, and docs (e.g. "BRAD engine" → "sealed baseline"; dropped
  the `brad_` prefix from tool display names so command output reads cleanly).
- Corrected the dependency claim everywhere to **standard library only** (the
  package imports no third-party libraries and declares zero dependencies).
- Fixed the README Quickstart to use the real subcommand flags
  (`new-project --slug`, `freeze --project … --phase …`).
- README CLI-tools heading corrected from "ten" to "eleven".

### Added
- `examples/hello-world/` — a tested, end-to-end CLI tour (`run.sh` + README).
- `SECURITY.md`, `CONTRIBUTING.md`, and this `CHANGELOG.md`.
- `keys/brad_authorship.pub` — the Ed25519 **public** key, so anyone can verify
  the authorship signatures (the private key is never committed).

### Removed
- The IP-classification vocabulary (`secret_ip` flag, `ip_classification`
  field, and the `SECRET_IP_*` enum) from the public schema, templates, and
  manifest writers. Classification is an internal concern, not part of the
  open-source framework.

### Security
- `.gitignore` now blocks `*.key` so private keys can never be committed.

## [0.1.0]
- Initial public release of the `lindsey-provenance` framework.
