# lindsey-provenance — Status

**As of:** 2026-05-23
**Proof-state (per six-state ledger):** `implemented` — full CLI + Python package; smoke-tested; not yet `simulated` end-to-end in a third-party operator's hands.
**Position in portfolio:** Active product #1 — top priority (per DEC-001 + DEC-004 + DEC-005).
**Owner:** Brad M. Lindsey.

---

## What works today

- The full CLI (`lindsey-provenance init`, `new-project`, `proof-state`, `freeze`, `audit`, `ip-extract`, `sign-ip`, `status`, `purge-selftest`, `assimilate`, `run-phase`) runs end-to-end on a stock Python 3.10+ environment with numpy.
- Hello-world example exercises every CLI tool in under sixty seconds.
- Python package: `brad_lite` → `lomoto` (DEC-004, 2026-05-20) → `lindsey-provenance` (DEC-005, 2026-05-22). All imports, entry points, and egg-info updated; folder renamed to `01_active/lindsey_provenance/` on 2026-05-23.
- README rewritten in Brad's voice (no LLM-tells; mentions Master Electrician + HVAC background; cites the forthcoming preprint).
- All templates in `templates/` de-personalized for public release (operator-neutral placeholders).
- MIT licensed; no external dependencies beyond `numpy`.

## What is blocked or in progress

- ✅ Domain registered: `lindseyprovenance.com` (Cloudflare, 2026-05-23). Note: .com chosen over the originally-targeted .dev per DEC-005 Addendum 2026-05-23.
- Private GitHub repo initialization — pending (`git init` + first commit + push to `Brad-Lindsey/lindsey-provenance`).
- Companion arXiv preprint v0.1 → v0.2 — depends on PT-1 case study measurement.
- Public GitHub push — gated on coordinated drop with arXiv preprint going up the same day.

## Next concrete move

1. Register `lindseyprovenance.dev` on Namecheap or Cloudflare Registrar.
2. `cd 01_active/lindsey_provenance && git init && git add . && git commit -m "Initial commit: lindsey-provenance v0.1.0"` — push to private GitHub.
3. Smoke-test the install path on a clean Python venv to catch any rename leftovers.

## Open questions

- Should `tests/` be expanded to cover the assimilate-brief pipeline more thoroughly before public push?
- The proof-state ledger pattern would benefit from a worked example in `examples/` beyond hello-world — defer to v0.2.

## See also

- Public README: `README.md` (this folder)
- Methodology long-form: `docs/METHODOLOGY.md`
- Architecture: `docs/ARCHITECTURE.md`
- The decision chain: `../../00_Journal/decisions/DEC-004_rename_brad_lite_to_lomoto_and_lab_to_lindsey_lab.md` and `../../00_Journal/decisions/DEC-005_rename_lomoto_to_lindsey_provenance_discipline.md`
- Preprint draft: `../../02_methodology/preprint_draft/preprint_v0.1.md`
