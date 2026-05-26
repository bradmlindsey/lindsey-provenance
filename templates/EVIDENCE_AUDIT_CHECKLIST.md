# Evidence-Audit Checklist

**SECRET IP · Brad M. Lindsey · Lindsey Lab**
**For project:** `<slug>` · **Phase:** `<N>` · **Audit date:** `YYYY-MM-DD`
**Auditor (operator):** `<name>`
**Replicator baseline:** `ace.phase4.freeze-1` = `9f9d28e5...fbb57`

> This checklist is the operator's hard gate. Every row must be PASS before `brad_freeze_manifest.py` is permitted to seal. Each row's verdict is paired with an on-disk evidence path. An incomplete checklist halts the seal.

---

## A. Inheritance integrity

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| A.1 | Sealed-core SHA verifier passes | All 14 modules byte-match | `sealed_core_audit/AUDIT_<date>.md` | ⬜ |
| A.2 | Project manifest inlines BRAD SHA | `replicator_baseline_sha256 == 9f9d28e5…fbb57` | `projects/<slug>/PROJECT_MANIFEST.json` | ⬜ |
| A.3 | Prior phase manifests present (if N>1) | All N-1 manifests exist with valid SHA | `projects/<slug>/artifacts/` | ⬜ |
| A.4 | No source under `core/` modified | git diff or SHA cmp clean | `sealed_core_audit/AUDIT_<date>.md` | ⬜ |

## B. Source-level audits

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| B.1 | All modules compile | All `python3 -B proto/*.py` exit 0 | session stdout / lab-notebook entry | ⬜ |
| B.2 | All modules carry SECRET-IP docstring | Header on every `.py` | `proto/` grep | ⬜ |
| B.3 | No forbidden imports | grep returns empty for torch/tf/keras/jax | `proto/` grep | ⬜ |
| B.4 | No forbidden language in docstrings | grep returns empty for sentient/cognitive/etc. | `proto/` grep | ⬜ |
| B.5 | All modules end with `_selftest()` | grep returns 1 per module | `proto/` grep | ⬜ |

## C. Per-step solver audits (Phase 1 + every phase that runs the solver)

| # | Field | Envelope | Rule | Pass criterion | Evidence path | Verdict |
|---:|---|---|---:|---|---|:---:|
| C.1 | Ma | ≤ 0.30 | 28 | 0 raises across run | `<slug>_phase<N>_field_audit.json` | ⬜ |
| C.2 | P_min | > P_sat | 30/38 | 0 raises across run | same | ⬜ |
| C.3 | \|E\|∞ | ≤ 0.040 | 39 | 0 raises across run | same | ⬜ |
| C.4 | σ_VM | ≤ 12 MPa | 13/21/35 | 0 raises across run | same | ⬜ |

## D. Geometry audits

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| D.1 | Non-manifold edges | 0 NME on every emitted STL | `<slug>_phase<N>_production_manifest.json:branches[*].non_manifold_edges` | ⬜ |
| D.2 | Vertex weld | ≥ 1 µm everywhere | weaver self-test | ⬜ |
| D.3 | BFS drainage | ≥ 99 % on every branch | `<slug>_phase<N>_sla_preflight.json:per_branch[*].drainage_pct` | ⬜ |
| D.4 | Min feature | ≥ 300 µm | same | ⬜ |
| D.5 | Min wall | ≥ 600 µm | same | ⬜ |
| D.6 | Span | ≤ 1.0 m | same | ⬜ |

## E. Numerical-method audits

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| E.1 | Refit RMSE | ≤ 1.0 × 10⁻⁶ (Rule 75) | `<slug>_phase<N>_refit.json:rmse` | ⬜ |
| E.2 | Pearson r per branch (Phase 3) | ≥ 0.95 (Rule 78) | `<slug>_phase<N>_inversion.json:per_branch[*].pearson_r` | ⬜ |
| E.3 | Cascade leak per branch (Phase 3) | ≤ 1.0 × 10⁻⁶ (Rule 79) | `<slug>_phase<N>_cascade.json:per_branch[*].post_match_leak` | ⬜ |
| E.4 | Macro margin per branch (Phase 3) | ≥ 2.5× (Rule 80) | `<slug>_phase<N>_macro.json:per_branch[*].safety_margin` | ⬜ |
| E.5 | MPI per case (cluster phases) | = 64 (Rule 76) | `<slug>_phase<N>_cluster_schedule.json:mpi_per_case` | ⬜ |
| E.6 | Scheduler concurrent (Rule 77) | true | same | ⬜ |
| E.7 | Theory-branch count (Rule 76) | 1 ≤ n ≤ 5 | `<slug>_phase<N>_multi_domain_manifest.json:n_branches` | ⬜ |

## F. Proof-state ledger consistency

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| F.1 | Every emitted artifact has a ledger row | `n_artifacts == n_ledger_rows_for_this_project` | `proof_state_ledger/LEDGER.jsonl` | ⬜ |
| F.2 | No illegal state transitions | No retrograde transitions | `brad_proof_state.py --verify` | ⬜ |
| F.3 | Every `implemented` artifact's module exits 0 | re-run check | session stdout | ⬜ |
| F.4 | Every `simulated` artifact's SHA-256 recorded | non-empty `sha256` field | ledger row | ⬜ |
| F.5 | No `physically-validated` rows without witness | every PV row has `witness_operator` and `instrument_id` | ledger row | ⬜ |

## G. IP-journal completeness

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| G.1 | Every `# IP-CLAIM:` marker has a journal row | counts match | `brad_ip_extract.py --verify` | ⬜ |
| G.2 | Every claim has evidence path filled | `evidence_path` non-empty | `ip_journal/<slug>_IP_<date>.md` | ⬜ |
| G.3 | Every claim has filing recommendation | one of trade-secret/provisional/defensive/pending | same | ⬜ |
| G.4 | Every claim has Principal signature line | line present (signature itself optional pre-seal) | same | ⬜ |

## H. Lab-notebook entries

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| H.1 | At least one entry exists for this phase | n ≥ 1 | `lab_notebooks/<slug>_LN_*` | ⬜ |
| H.2 | Every entry is signed (operator) | every entry has operator signature line | each file | ⬜ |
| H.3 | Page numbers are sequential, no gaps | monotonic per project | grep `^Page: ` | ⬜ |
| H.4 | No erasures, only strike-throughs with initial | inspect any edits | manual review | ⬜ |
| H.5 | Every entry has a witness line | line present (witness signature optional pre-seal) | each file | ⬜ |

## I. Reports

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| I.1 | Phase report exists | file present | `projects/<slug>/docs/<slug>_PHASE<N>_REPORT.md` | ⬜ |
| I.2 | Phase report carries SECRET IP attribution | header line present | same | ⬜ |
| I.3 | Phase report cites the phase manifest SHA | line present | same | ⬜ |

## J. Cryptographic-freeze readiness

| # | Check | Pass criterion | Evidence path | Verdict |
|---:|---|---|---|:---:|
| J.1 | `brad_freeze_manifest.py --dry-run` passes | exit 0; no diffs | session stdout | ⬜ |
| J.2 | All A–I rows above are PASS | no `❌` | this file | ⬜ |
| J.3 | Principal authorisation present on phase template | §10 signed | `projects/<slug>/phases/PHASE_<N>.md` | ⬜ |

---

## Auditor sign-off

> *I, the operator named above, attest that I have audited every row of this checklist against the corresponding on-disk evidence, that every row is PASS, and that this phase is cleared for cryptographic seal under the BRAD engine.*

- **Auditor (operator) signature:** `_______________________`
- **Audit complete UTC:** `YYYY-MM-DDThh:mm:ssZ`

## Principal sign-off (seal authorisation)

> *I, Brad M. Lindsey, authorise the cryptographic seal of Phase `<N>` of project `<slug>` under the BRAD engine. All output remains SECRET IP at the institutional level.*

- **Principal signature:** Brad M. Lindsey
- **Seal authorised UTC:** `YYYY-MM-DDThh:mm:ssZ`

---

— Evidence-audit checklist · Brad M. Lindsey · Lindsey Lab
