# Client / Architect Brief Triage — `<brief-basename>`

**Brad M. Lindsey · Lindsey Lab**
**Inherits:** `my-engine.v1.freeze-1` = `9f9d28e5bfbcbc8c66c9c9e167ae20b6389493fef28e3caec59cdb47c00fbb57`
**Triage date:** `YYYY-MM-DD`
**Triage operator:** `<name / agent>`
**Source brief path:** `operator/briefs/<YYYY-MM-DD>_<short-slug>.<ext>`
**Source brief SHA-256:** `<64-hex>`

> Reusable template for the seven-phase brief-assimilation workflow (run via `lindsey-provenance assimilate`). Fill in every section. Where empty, write `N/A` rather than leaving blank. The Principal signs Section 9 to authorise routing.

---

## 1. Phase 1 — Receive

- **Original brief format:** `<docx / pdf / md / inline-message>`
- **Word count (extracted):** `<int>`
- **Brief shape** (per workflow §3): `<sparse / single-page / multi-section / multi-document>`
- **Stored byte-identical at:** `operator/briefs/<filename>`
- **SHA-256 verified:** `<yes/no>` — recorded in `operator/briefs/BRIEF_LOG.md`

## 2. Phase 2 — Extract

- **Extracted text path:** `operator/briefs/<basename>.extracted.txt`
- **Paragraph count:** `<int>`
- **Tables / figures:** `<int tables, int figures>` — content summarised inline with `[TABLE N]` / `[FIGURE N]` markers
- **Numerical-claim spot-check (3 samples):**
  - Brief line `<N>`: "<verbatim quote>" — matches original ✓ / ✗
  - Brief line `<N>`: "<verbatim quote>" — matches original ✓ / ✗
  - Brief line `<N>`: "<verbatim quote>" — matches original ✓ / ✗

## 3. Phase 3 — Decompose

### 3.1 Six-section pre-mapping

| Section | Brief content (line refs) | Value extracted |
|---|---|---|
| `structural` | `<line refs>` | `<material card, scale, feature size, walls, ε>` |
| `environmental_fields` | `<line refs>` | `<load, temp, pressure>` |
| `acoustic_carriers` | `<line refs>` | `<f₀, sweep, Q, LC corner>` |
| `fluidic_transport` | `<line refs>` | `<viscosity, Mach, v_in, P_sat>` |
| `invariants` | `<line refs>` | `<zero_telemetry, BFS, laminar>` |
| `process_gates` | `<line refs>` | `<RMSE, MPI, Pearson, leak, drainage>` |

### 3.2 Proposed section extensions (7th / 8th sections beyond canonical six)

| Extension name | Brief content (line refs) | Parameters | Existing precedent? |
|---|---|---|---|
| `<e.g. magnetic_carriers>` | `<line refs>` | `<B-field, J, χ, ferrofluid card>` | `xt-1-ace-mhd` ✓ / new ✗ |

### 3.3 Domain-vector tags (paragraph histogram)

| Tag | Paragraph count | Sample line refs |
|---|---:|---|
| MHD      | `<n>` | `<refs>` |
| VISCO    | `<n>` | `<refs>` |
| THERMAL  | `<n>` | `<refs>` |
| STRUCT   | `<n>` | `<refs>` |
| ACOUSTIC | `<n>` | `<refs>` |
| FLUID    | `<n>` | `<refs>` |
| PHASE    | `<n>` | `<refs>` |
| FAB      | `<n>` | `<refs>` |
| METRO    | `<n>` | `<refs>` |
| MATH     | `<n>` | `<refs>` |
| INV      | `<n>` | `<refs>` |
| ADMIN    | `<n>` | `<refs>` |

**Domain spine** (the dominant non-ADMIN tag, candidate as the project's primary physics): `<e.g. MHD>`

## 4. Phase 4 — Cross-check

### 4.1 Redundancy ledger

| Domain tag | Existing coverage | Project / phase | Verdict |
|---|---|---|---|
| `<tag>` | `<project slug>` | `<phase freeze>` | `FULLY COVERED / PARTIAL / GAP` |

### 4.2 Invariant-conflict ledger

| Brief claim (line ref + verbatim) | Conflicts with | Proposed resolution |
|---|---|---|
| `<line N: "...">` | `Rule <#> (<scope>)` | `<re-route / decline / re-scope>` |

### 4.3 Tool-and-extension catalog

| Tool / extension named in brief | Catalog status | Action |
|---|---|---|
| `<solver name / kernel>` | `existing in core / existing in proto / new` | `none / extend proto / new module` |
| `<physical tool>` | `in BoM / not in BoM` | `none / add to BoM` |

### 4.4 IP cross-check

| Brief claim | Matches SIGNED IP row | Notes |
|---|---|---|
| `<line N: "...">` | `<journal id or "new candidate">` | `<details>` |

## 5. Phase 5 — Routing verdict

Select exactly **one**:

- [ ] **NO-OP** — all proposed work is shipped; reply with sealed manifest + IP citations
- [ ] **EXTEND-EXISTING** — Phase-N+1 trigger for `<slug>`; open `PHASE_N+1.md`
- [ ] **NEW-PROJECT** — coherent new downstream project; slug `<proposed slug>`
- [ ] **SPLIT** — multiple coherent new projects; slugs `<list>`
- [ ] **DECLINE** — conflicts with non-negotiable invariants; reply with citation

**Reasoning** (cite §4.1, §4.2, §4.3 evidence):

```
<free text - the route must be derivable from the four cross-check ledgers above>
```

**Single-physics-spine test** (only required if NEW-PROJECT selected):

- Section extension count beyond canonical six: `<int>` (must be ≤ 2)
- Distinct physics introduced: `<list>` (must be ≤ 1 new physics class for a single project; if > 1 → re-route to SPLIT)
- Verdict: `PASS / FAIL`

## 6. Phase 6 — Authoring plan

Depending on the verdict in §5:

### 6.1 If NEW-PROJECT or SPLIT
- Target intake path(s): `operator/projects/<slug>/INTAKE.md`
- Inferred / default fields (need explicit Principal sign-off per field):
  - `<field>: <inferred value>` — basis: `<inheritance from prior project / template default>`
- Open phase: `PHASE_1.md`

### 6.2 If EXTEND-EXISTING
- Target phase path: `operator/projects/<existing-slug>/PHASE_<N+1>.md`
- New scope (delta over Phase N): `<bullets>`
- Inherited deliverables preserved: `<bullets>`

### 6.3 If NO-OP or DECLINE
- Response path: `operator/briefs/<basename>.RESPONSE.md`
- Key citations to include: `<list>`

## 7. Out-of-scope appendix

Paragraphs tagged `ADMIN` (rhetoric, branding, schedule, signoff) recorded here for completeness, not carried into intake:

| Brief line ref | Content type | Disposition |
|---|---|---|
| `<refs>` | `<branding / rhetoric / schedule>` | `noted, not actioned` |

## 8. Triage author signoff

- **Triage operator:** `<name>`
- **Date / time UTC:** `<YYYY-MM-DDThh:mm:ssZ>`
- **Attestation:** "I have verified that every numerical claim in §3 traces to a brief line ref, every conflict in §4.2 cites a rule by number, and the verdict in §5 is supported by the evidence ledgers above."

## 9. Principal signoff

- **Principal:** Brad M. Lindsey
- **Date / time UTC:** `<YYYY-MM-DDThh:mm:ssZ>`
- **Verdict ratified:** `<NO-OP / EXTEND-EXISTING / NEW-PROJECT / SPLIT / DECLINE>`
- **Per-field inferred-default acknowledgements** (only if NEW-PROJECT/SPLIT and §6.1 lists inferred fields):
  - `<field>: <inferred value>` — `ACK ✓ / OVERRIDE: <override value>`
- **Authorisation:** "I authorise the operator to execute the routing verdict above and consider this triage the canonical record of how the brief was assimilated."

— Triage template version 1.0 · assimilation workflow rev 1.0 · 2026-05-19
