# Phase `<N>` — `<slug>` — `<phase title>`

**SECRET IP · Brad M. Lindsey · Lindsey Lab**
**Project:** `<slug>`
**Phase:** `<N>` of 4
**Phase date:** `YYYY-MM-DD`
**Inherits:**
- `ace.phase4.freeze-1` = `9f9d28e5...fbb57` (mandatory replicator baseline)
- `<slug>_phase<N-1>_manifest.json` (if N > 1)

> This template is the canonical phase brief. The Principal signs the bottom before any phase work begins. The build agent receives a `BUILDER_PROMPT.md` rendered from this file plus `PROJECT_MANIFEST.json`.

---

## 1. Phase title and one-line scope

**Title:** `<short title, e.g. "4-physics solver + density carve">`
**Scope (one line):** `<one sentence>`

## 2. Phase position in the canonical WOQFEW partition

Mark which steps of the 12-step compiler partition this phase covers:

| Step | Description | In this phase? |
|---:|---|:---:|
| 1 | Parse intent | `[x|]` |
| 2 | Build grid | `[x|]` |
| 3 | Seed phase field | `[x|]` |
| 4 | Allen-Cahn step | `[x|]` |
| 5 | Non-linear Cauchy step | `[x|]` |
| 6 | NS predictor-corrector | `[x|]` |
| 7 | Strain-modulated Helmholtz | `[x|]` |
| 8 | Density carve | `[x|]` |
| 9 | Watertight STL emit + audit | `[x|]` |
| 10 | Cluster case emit | `[x|]` |
| 11 | Refit + RMSE ≤ 10⁻⁶ gate | `[x|]` |
| 12 | Cryptographic freeze | `[x|]` |

(For ACE / BRAD-class meta-builds, Phase 2 wraps steps 1–11 in a 5-branch batch; Phase 3 runs inversion + cascade + macro; Phase 4 seals.)

## 3. Modules to author

| # | Module | Purpose | Approximate LOC |
|---:|---|---|---:|
| 1 | `proto/<slug>_<role>.py` | `<one line>` | `<approx>` |
| 2 | `proto/<slug>_<role>.py` | `<one line>` | `<approx>` |

Total target LOC: `<approx>`.

## 4. Numerical guardrails enforced in this phase

For each invariant, name the module that owns it and the exception it raises on breach:

| Field | Envelope | Rule | Owning module | Exception |
|---|---|---|---|---|
| Ma | ≤ 0.30 | 28 | `proto/<slug>_field_solver.py:step_ns` | `InvariantViolation` |
| P_min | > P_sat | 30/38 | `proto/<slug>_field_solver.py:step_ns` | `InvariantViolation` |
| |E|∞ | ≤ 0.040 | 39 | `proto/<slug>_field_solver.py:step_cauchy` | `InvariantViolation` |
| σ_VM | ≤ 12 MPa | 13/21/35 | `proto/<slug>_field_solver.py:step_cauchy` | `InvariantViolation` |
| BFS drainage | ≥ 99% | 19/23/64 | `proto/<slug>_density_weaver.py` | `WaterTightnessViolation` |
| Vertex weld | ≥ 1 µm | 40/67 | `proto/<slug>_density_weaver.py` | `WaterTightnessViolation` |
| Refit RMSE | ≤ 10⁻⁶ | 75 | `proto/<slug>_cluster_refit.py` | `RefitConvergenceFailure` |
| Pearson r | ≥ 0.95 | 78 | `proto/<slug>_inversion.py` | `InversionWeakness` |
| Cascade leak | ≤ 10⁻⁶ | 79 | `proto/<slug>_cascade.py` | `CascadeLeakViolation` |
| Macro margin | ≥ 2.5× | 80 | `proto/<slug>_macro.py` | `MacroMarginViolation` |

(Strike rows that do not apply to this phase.)

## 5. Acceptance criteria (the audit grid)

Every row below must be PASS before the phase can be sealed. The `EVIDENCE_AUDIT_CHECKLIST.md` cross-checks each row to a specific on-disk artifact.

| # | Criterion | Threshold | Evidence file |
|---:|---|---|---|
| 1 | Module compiles + exits 0 on self-test | exit 0 | stdout of `python3 -B proto/<module>.py` |
| 2 | Per-step invariant audit returns no exception | 0 raises | `<slug>_phase<N>_field_audit.json` |
| 3 | STL emit watertight | 0 NME | `<slug>_phase<N>_production_manifest.json` |
| 4 | Drainage clearance | ≥ 99% | same |
| 5 | Refit converges | RMSE ≤ 10⁻⁶ | `<slug>_phase<N>_refit.json` |
| 6 | Pearson r (if Phase 3) | ≥ 0.95 | `<slug>_phase<N>_inversion.json` |
| 7 | Cascade leak (if Phase 3) | ≤ 10⁻⁶ | `<slug>_phase<N>_cascade.json` |
| 8 | Macro margin (if Phase 3) | ≥ 2.5× | `<slug>_phase<N>_macro.json` |
| 9 | Freeze manifest emitted | exists | `<slug>_phase<N>_manifest.json` |
| 10 | Inheritance assertion | inlines BRAD SHA | same |

## 6. IP claims expected in this phase

Pre-allocate IP claim slots. The operator opens an `ip_journal/<slug>_IP_<date>.md` row for each claim *at synthesis time*.

| Slot | Tentative claim | Filing recommendation |
|---:|---|---|
| 1 | `<one-line claim>` | `<trade-secret|provisional|defensive>` |
| 2 | `<one-line claim>` | `<...>` |

## 7. Lab-notebook entries expected

Approximate number of GLP-grade entries this phase will produce: `<n>`. Each entry uses `LAB_NOTEBOOK_TEMPLATE.md`.

## 8. Cluster envelope (if cluster cases are emitted)

| Quantity | Value |
|---|---|
| MPI per case | 64 (Rule 76 floor) |
| Cases per branch | 18 (Rule 49/68 cardinality) |
| Theory branches | `<1-5>` (Rule 76 cap = 5) |
| Total cases | `<1*18 ... 5*18>` |
| Serial-equivalent core-hours | `<n * 256>` |
| Concurrent wallclock target | `<h>` |

## 9. Outputs this phase will produce

- Source modules: `<list>` under `proto/`.
- Artifacts: `<list>` under `artifacts/`.
- Reports: `<slug>_PHASE<N>_REPORT.md` under `docs/`.
- Lab-notebook entries: at `operator/lab_notebooks/<slug>_LN_<date>.md`.
- IP-journal rows: at `operator/ip_journal/<slug>_IP_<date>.md`.
- Proof-state ledger entries: appended to `operator/proof_state_ledger/LEDGER.jsonl`.
- Phase freeze manifest: `<slug>_phase<N>_manifest.json`.

## 10. Phase dispatch authorisation

> *I, Brad M. Lindsey, authorise Phase `<N>` of project `<slug>` to proceed under the BRAD engine, with all output reserved as SECRET IP at the institutional level. The build agent is dispatched per `BUILDER_PROMPT_TEMPLATE.md`. Acceptance is per §5 above.*

- **Signed by:** Brad M. Lindsey
- **Signed UTC:** `YYYY-MM-DDThh:mm:ssZ`
- **Note:** `<optional>`

## 10b. Honest design deferrals (v2 — driven by XT-1/XT-2 lessons)

A deferral is something planned in this phase that is honestly moved to a later phase because evidence in flight showed it could not be cleanly delivered now. Deferrals are NOT failures — they are disciplined recognition that the right place for the work is downstream.

Every deferral entered below must include the *trigger* (what evidence forced the move), the *target phase* for the work, and the *impact on Phase-N's deliverables and gates*. Empty if no deferrals.

| # | Original item | Trigger (evidence) | Deferred to | Impact on Phase-N gates |
|---:|---|---|---|---|
| 1 | _e.g. log-spiral void grid_ | _e.g. 4 attempts at voxel-mask mesher all produced non-manifold edges_ | Phase 2 | _e.g. Rule 83 attenuation target moves to Phase 3_ |

After populating: write the deferral list verbatim into the Phase-N report §10 (Honest caveats). Phase-N+1 brief MUST address every row.

## 11. Phase closure (filled at seal)

- **Sealed UTC:** `YYYY-MM-DDThh:mm:ssZ`
- **Phase manifest SHA-256:** `<filled by brad_freeze_manifest.py>`
- **Inherits asserted:** ✅ ace.phase4.freeze-1 + ✅ prior phase (if N > 1)
- **Audit checklist:** ✅ all rows PASS / ❌ failures (list)
- **IP-journal rows opened:** `<n>`
- **IP-journal rows signed:** `<n>`
- **Lab-notebook entries:** `<n>`
- **Principal closeout signature:** Brad M. Lindsey
- **Closeout UTC:** `YYYY-MM-DDThh:mm:ssZ`

---

— Phase template · Brad M. Lindsey · Lindsey Lab
