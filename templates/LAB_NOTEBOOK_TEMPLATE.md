# Lab Notebook Entry — `<slug>`

**SECRET IP · Brad M. Lindsey · Lindsey Lab**
**Notebook format:** GLP-compatible (sequential pages · no erasures · witness line)

> Industry-standard lab-notebook entries are sequentially paginated, never erased (only strike-through with operator initials), signed by the operator, and witnessed for high-consequence runs. One **session = one page**. Each entry below uses a fresh page number from the running ledger at `lab_notebooks/<slug>_PAGE_LEDGER.txt`.

---

**Page:** `<NN>` (sequential, never reused)
**Project slug:** `<slug>`
**Phase:** `<N>`
**Date (local):** `YYYY-MM-DD`
**Session start UTC:** `YYYY-MM-DDThh:mm:ssZ`
**Session end UTC:** `YYYY-MM-DDThh:mm:ssZ`
**Operator:** `<full name>`
**Build agent:** `<Claude | Gemini | other>`
**Build-agent version:** `<exact model string if known>`
**Workstation:** `<hostname | platform>`

---

## 1. Purpose of this session

`<one short paragraph stating the scientific or engineering question that this session addresses>`

## 2. Materials, instruments, software

| Item | Description | Identifier / version | Calibration date |
|---|---|---|---|
| Python | runtime | `3.10.x` | n/a |
| numpy | library | `<version>` | n/a |
| Workstation | hardware | `<spec>` | n/a |
| Sealed BRAD core | reference baseline | `ace.phase4.freeze-1 = 9f9d28e5…fbb57` | 2026-05-18 |
| Project source | proto/ at session start | git SHA / mtime / SHA-256 list | session start |
| `<instrument>` | `<purpose>` | `<id>` | `<date>` |

## 3. Parameters

```
<paste the intent block or the parameter set used for this session,
 verbatim — no abbreviation>
```

## 4. Procedure (numbered, atomic steps)

1. `<step>`
2. `<step>`
3. `<step>`

If a step was modified mid-session, **strike through with initial** and append the corrected step beneath, e.g.:

> ~~3. ran `python3 -B foo.py` with `seed=7`~~ — *<initial>*
> 3b. ran `python3 -B foo.py` with `seed=11` (corrected to canonical session seed)

## 5. Observations (raw data)

`<paste stdout, key numerical readings, error messages, exit codes>`

Numeric observations:

| Quantity | Value | Units | Source |
|---|---:|---|---|
| `<e.g. refit RMSE>` | `<e.g. 2.72e-07>` | (dim-less) | `<slug>_phase<N>_refit.json` |
| `<e.g. macro margin>` | `<e.g. 2.59>` | × | `<slug>_phase<N>_macro.json` |

## 6. Interpretation

`<one short paragraph interpreting the observations: did the audits clear?
 what does this tell us about the model? any unexpected behaviour?>`

## 7. Artifacts produced this session

| Artifact path | SHA-256 (16) | Proof state at end of session |
|---|---|---|
| `<path/file.json>` | `<sha>` | `<idea|planned|implemented|simulated|artifact-generated|physically-validated>` |
| `<path/file.stl>` | `<sha>` | `<...>` |

## 8. Proof-state transitions logged

| Artifact | From | To | Ledger row UTC |
|---|---|---|---|
| `<path>` | `<state>` | `<state>` | `<UTC>` |

(Cross-reference: `proof_state_ledger/LEDGER.jsonl`.)

## 9. IP claims surfaced this session

| Marker line in source | Filed in journal? | Filing recommendation |
|---|:---:|---|
| `# IP-CLAIM: <text>` | ⬜ | `<trade-secret|provisional|defensive|pending>` |

(Cross-reference: `ip_journal/<slug>_IP_<date>.md`.)

## 10. Issues / failures (full disclosure)

`<list any audit that did not clear, any unexpected exception, any
 mid-session correction. Honesty requirement — do not omit.>`

## 11. Next session

`<one-line plan for the next session under this project>`

## 12. Operator signature

> *I attest that the above is a complete and unmodified record of this session, and that no observation has been altered after the session-end UTC.*

- **Operator signature:** `_______________________`
- **Signed UTC:** `YYYY-MM-DDThh:mm:ssZ`

## 13. Witness signature (required for high-consequence sessions)

A session is **high-consequence** if it is a Phase-3 inversion, a Phase-4 seal, or any wet-bench measurement.

> *I witnessed this session and attest that the observations recorded above are consistent with what occurred.*

- **Witness signature:** `_______________________`
- **Witness name:** `<full name>`
- **Witness UTC:** `YYYY-MM-DDThh:mm:ssZ`

---

## Page ledger record (also append to `<slug>_PAGE_LEDGER.txt`)

```
<NN>  <YYYY-MM-DD>  <operator>  <phase>  <one-line purpose>
```

---

— Lab notebook entry · GLP-compatible format · Brad M. Lindsey · Lindsey Lab
