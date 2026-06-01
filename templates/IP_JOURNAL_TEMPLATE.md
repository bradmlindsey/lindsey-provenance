# IP Extraction Journal — `<slug>`

**Brad M. Lindsey · Lindsey Lab**
**Replicator baseline:** `my-engine.v1.freeze-1` = `9f9d28e5...fbb57`
**Journal file:** `ip_journal/<slug>_IP_<YYYY-MM-DD>.md`
**Master index:** `ip_journal/JOURNAL.md`

> Every IP claim is captured in real time, at synthesis, not retroactively. Each claim is one row of the table below. Rows are append-only. Rows draft until the Principal signs.

> The build agent surfaces candidates via `# IP-CLAIM:` markers in source. The operator's `ip_extract.py` runner pre-populates rows. The operator enriches. The Principal signs.

---

## How a claim is born

1. The build agent writes a piece of source containing a *novel combination*: a new rule, a new closed-form identity, a new architectural pattern, a new material card, a new cryptographic-inheritance pattern.
2. The build agent annotates the line with `# IP-CLAIM: <one-line description>` and (optionally) `# NOVEL: <reason>`.
3. The operator runs `python3 operator/tools/ip_extract.py --project <slug>`. The tool appends one draft row per marker to this journal.
4. The operator enriches the draft row: evidence path, prior-art-search status, filing recommendation.
5. The Principal signs the row. Until signed, the row is `DRAFT` and is **excluded** from any licensing kit.
6. The signed row is summarised into `ip_journal/JOURNAL.md` (one line per signed claim across all projects).

---

## Per-claim row format

Each row in this file uses the structure below. Append new rows at the bottom (oldest at top).

### Claim `<NNN>` — `<one-line title>`

- **Claim ID:** `<slug>-IP-<NNN>` (e.g. `radiator-IP-001`)
- **Surfaced UTC:** `YYYY-MM-DDThh:mm:ssZ`
- **Synthesised in module:** `proto/<file>.py` lines `<L1>–<L2>`
- **Source marker:** `# IP-CLAIM: <verbatim text>`
- **Phase:** `<N>`

**Claim statement (paragraph, ≤ 6 lines):**
> `<the claim, articulated by the operator — what is the novel combination?>`

**Evidence on disk:**
- Source file: `proto/<file>.py` SHA-256 = `<...>`
- Artifact: `artifacts/<file>` SHA-256 = `<...>` *(if applicable)*
- Lab-notebook entry: `lab_notebooks/<slug>_LN_<date>.md` page `<NN>`
- Phase manifest: `<slug>_phase<N>_manifest.json` SHA-256 = `<...>`

**Novelty argument (paragraph, ≤ 6 lines):**
> `<why is this novel? what is the closest prior art the operator is aware of?
>  what is the inventive step?>`

**Prior-art search status:**
- [ ] Not yet searched.
- [ ] Cursory search performed (search terms: `<...>` · date: `<...>` · operator: `<...>`).
- [ ] Comprehensive search performed (patent counsel involved · date: `<...>`).
- [ ] No relevant prior art found.
- [ ] Relevant prior art found (citation: `<...>` · disposition: `<narrow|abandon|amend>`).

**Filing recommendation (operator's view):**
- [ ] Trade secret (retain as the operator's reserve).
- [ ] Provisional patent (file within 12 months).
- [ ] Defensive publication (publish to block third-party filing).
- [ ] Pending decision.

**Licensing posture (operator's view):**
- [ ] Excluded from any external license.
- [ ] Eligible for license.
- [ ] Eligible under public-safe summary.

**Inheritance attestation:**
- The claim is wholly composed on top of `<sealed-baseline-name>` and the inherited prior baselines. The claim does not modify any sealed-core source.

**Principal sign-off:**

> *I, `<your name>`, attest that the foregoing claim originated in `<project name>` under my direction, is my original intellectual work, and is reserved at my discretion.*

- **Status:** `DRAFT` → `SIGNED` (toggle on signature)
- **Signed by:** `<your name>`
- **Signed UTC:** `YYYY-MM-DDThh:mm:ssZ`
- **Note:** `<optional>`

---

## Filed master-index line (auto-appended to `JOURNAL.md` on signature)

```
| <slug>-IP-<NNN> | <one-line title> | <phase> | <filing rec> | <signed UTC> |
```

---

## Bulk operator notes (free-form scratchpad)

Below the per-row section, the operator may keep an unstructured scratchpad of observations, links between claims, and questions for patent counsel. Anything important is promoted into a new claim row.

```
<free-form notes>
```

---

— IP extraction journal · Brad M. Lindsey · Lindsey Lab
