# Methodology

This document describes the four disciplines that make up `lindsey-provenance`. They
are independent — you can adopt any one without the others — but they
compose into a single coherent practice.

## 1. Closed-form re-route at intake

**Problem.** When an LLM generates a brief proposing how to implement a
feature, it will almost always reach for the most general-purpose tool it
knows. For numerical or ML-adjacent work, that means `torch`, `tensorflow`,
`scikit-learn`, etc. After three or four such briefs, your codebase has
inherited several heavy dependencies you did not consciously decide on.

**Discipline.** Every incoming brief is triaged *before any code is
written* against a list of architectural invariants — both positive
(things the codebase must have) and negative (things it must not have).
When a negative invariant is hit, the brief is **declined categorically**
at intake and **re-routed** to a substitute that preserves the algorithmic
intent.

**Example.** A brief proposing `nn.TransformerDecoder` + beam search for
token decoding gets declined under the "no ML libraries" invariant and
re-routed to: a deterministic signature bank seeded by SHA-256 of token
names, plus closed-form softmax + argmax. The token-emission semantics
are identical; the dependency footprint is reduced from torch to the standard library.

**Why this is novel.** Most LLM-collaboration patterns are *generative* —
the human accepts what the LLM produces and refactors later. Closed-form
re-route is *invariant-preserving* — the human declines at the gate and
specifies the substitute. The LLM then implements *the substitute*, not the
original. This keeps the codebase auditable end-to-end.

**How lindsey-provenance supports it.** The `assimilate` command runs the 7-phase
intake pipeline. The `templates/CLIENT_BRIEF_TRIAGE_TEMPLATE.md` provides
the structure for documenting each decline + re-route decision. The pattern
forms a permanent record in `docs/internal_record/`.

## 2. Phase-chain freeze with SHA-256 inheritance

**Problem.** A research codebase that evolves over weeks of LLM-assisted
work accumulates many incompatible versions. "What version of the
calibration module produced the figure in my July report?" is unanswerable.

**Discipline.** Each project advances through numbered phases. At the end
of every phase, `freeze` walks the project's `proto/` and `artifacts/`
directories, computes a SHA-256 over each file, and emits a manifest at
`artifacts/<slug>_phase<N>_manifest.json`. The manifest inherits — by SHA
reference — the prior phase's manifest, *and* the sealed engine baseline
SHA from `.lindsey_provenance/config.json`. This forms a Merkle-style chain anchored
to a single sealed root.

Verification is one command: `lindsey-provenance audit` walks every project's chain
and confirms each per-file SHA still matches the recorded value.

**Why this is novel.** Build systems (Nix, Bazel) do this for software
inputs. Git does it for commits. `lindsey-provenance` does it for *project phases* —
groups of source files + artifacts that represent a coherent state of a
research demonstration. The chain is human-meaningful (each phase has a
narrative + report) and machine-verifiable (each phase has a SHA + audit).

**How lindsey-provenance supports it.** `freeze_manifest.py` builds manifests;
`audit.py` verifies them; the `phase_chains` audit gate confirms inheritance
SHAs across every project in the repo.

## 3. Six-state proof-state ledger

**Problem.** "We've implemented the optimization module" can mean six
different things: an idea, a planned spec, code that exists, code that
runs, code that emits an artifact, or code whose artifact has been
physically measured. Conflating these is how research overclaims happen.

**Discipline.** Every meaningful artifact in the codebase moves through
exactly six monotonic proof states:

| State | Meaning |
|---|---|
| `idea` | Mentioned somewhere; nothing committed |
| `planned` | Phase brief written; not yet built |
| `implemented` | Source exists, self-test exit 0, SHA-256 recorded |
| `simulated` | On-disk artifact emitted, SHA-256 recorded |
| `artifact-generated` | File under `artifacts/production/` |
| `physically-validated` | Real instrument measurement with named witness |

Transitions are append-only, monotonic (no retrograde), and recorded with
the source/artifact SHA at transition time, so retrospective tamper is
detectable. The `proof_state` tool refuses to skip steps and refuses to
move backward.

**Why this is novel.** Most project trackers (Jira, Linear) track *task
status*. `lindsey-provenance` tracks *epistemic status* — what you can honestly
claim about a piece of code based on the evidence on disk.

**How lindsey-provenance supports it.** `proof_state.py` enforces the state
machine; `proof_state_ledger/LEDGER.jsonl` is the append-only log;
`audit.py` cross-checks ledger rows against on-disk SHAs.

## 4. Multi-modal brief assimilation

**Problem.** When you collaborate with an LLM you receive briefs in many
formats: chat messages, exported `.docx`, `.eml`, photos of whiteboards,
hand-written notes. These need a single uniform intake pipeline so they
can all be triaged the same way.

**Discipline.** Every brief, regardless of modality, goes through 7 phases:

1. **Archive** — copy the raw brief into `operator/briefs/<date>_<slug>.<ext>`
2. **Extract** — convert to plain text (docx → txt, eml → txt, image → OCR transcription)
3. **Tag** — count keyword occurrences across a fixed domain vocabulary; produce a histogram
4. **Cross-check** — compare extracted intent against rules registry, pattern signature, prior briefs
5. **Verdict** — NO-OP / NEW-PROJECT / EXTEND-EXISTING / DECLINE
6. **Triage document** — write `docs/internal_record/CLIENT_BRIEF_TRIAGE_<slug>.md`
7. **Brief log update** — append a row to `operator/briefs/BRIEF_LOG.md`

**Why this is novel.** Most ingestion pipelines handle one modality at
a time. `lindsey-provenance` treats modality as a transcription detail and unifies
the triage layer. The handwriting/photo path includes a small "ingestion
control" sub-experiment that measures the engine's transcription fidelity
across handwriting samples — a calibration step nobody else seems to
formalize.

**How lindsey-provenance supports it.** `assimilate_brief.py` runs the full
pipeline. Templates for the triage document and brief log live in
`templates/`.

## Composition: how the four work together

A typical day looks like this:

1. You receive an LLM-generated brief in some modality.
2. `lindsey-provenance assimilate brief.eml` runs the 7-phase intake.
3. The triage doc is reviewed; declines and re-routes are documented.
4. If the verdict is NEW-PROJECT or EXTEND-EXISTING, you write `PHASE_<N>.md`
   from the triage.
5. Build the modules. Self-test. `lindsey-provenance proof-state` records `implemented`.
6. Run the modules. Emit artifacts. `lindsey-provenance proof-state` records `simulated`.
7. `lindsey-provenance ip-extract` surfaces IP-CLAIM comments. Review and `sign-ip` them.
8. `lindsey-provenance audit` verifies everything cross-references.
9. `lindsey-provenance freeze --phase N` seals the phase with a SHA-256 manifest.
10. The chain has grown by one phase. The audit will catch any future drift.

The methodology is the product. The CLI tools are the runtime that enforces it.
