# lindsey-provenance — Status

**As of:** 2026-05-26
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

- ✅ Domain registered: `lindseyprovenance.com` (Cloudflare, 2026-05-26). Note: .com chosen over the originally-targeted .dev per DEC-005 Addendum 2026-05-26.
- ✅ Clean-venv smoke test passed on local Windows 2026-05-26 — `pip install -e .` succeeded; `lindsey-provenance --help` printed the 11-subcommand banner correctly. Yesterday's flagged Brad-side action is complete.
- ✅ Private GitHub repo initialized + pushed 2026-05-26 — `github.com/bradmlindsey/lindsey-provenance` (private). Initial commit `26e5690`, 29 files, 4,856 lines. SSH-auth via ed25519 key on this Windows machine.
- Companion arXiv preprint v0.1 → v0.2 — depends on PT-1 case study measurement (still pending; SLA print + USB mic not yet ordered).
- Public GitHub push (flip Private → Public) — gated on coordinated drop with arXiv preprint going up the same day.
- ✅ ORCID iD claimed 2026-05-26: **`0009-0004-6392-2720`** (`https://orcid.org/0009-0004-6392-2720`). Both registered emails verified + profile fields populated (Employment / Education / Keywords / Websites / Biography). Ready for arXiv submission author byline.

## Next concrete move

1. Claim ORCID iD (Task C in `02_methodology/public_presence/EXECUTION_STEP2_domain_email_orcid_2026-05-22.md`).
2. Order the PT-1 phononic SLA print + $50 USB mic so the physical-validation case study can land in the preprint.
3. Polish the repo with `.gitattributes` + .gitignore comment fix (queued as follow-up commit).
4. Build out `tests/` to cover the assimilate-brief pipeline more thoroughly before public push (defer to v0.2 if time-constrained).

## Open questions

- Should `tes