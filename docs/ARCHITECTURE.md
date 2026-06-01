# Architecture

Quick technical reference for how `lindsey-provenance` is structured internally.

## Package layout

```
lindsey_provenance/
├── __init__.py
├── config.py              # identity (replicator baseline + SHA + principal)
├── _root.py               # locate project root + subdirectories
├── new_project.py         # CLI: scaffold a project from INTAKE.md
├── proof_state.py         # CLI: six-state classifier + append-only ledger
├── freeze_manifest.py     # CLI: per-phase cryptographic freeze
├── audit.py               # CLI: 5-gate audit (core / inheritance / ledger / IP / chains)
├── ip_extract.py          # CLI: extract IP-CLAIM markers to draft journal
├── sign_ip.py             # CLI: flip DRAFT IP rows to SIGNED
├── status.py              # CLI: cross-project snapshot
├── purge_selftest.py      # CLI: clean self-test residue
├── assimilate_brief.py    # CLI: 7-phase multi-modal brief intake
└── run_phase.py           # CLI: end-to-end phase execution
```

## Project layout (what `lindsey-provenance init` creates)

```
<project-root>/
├── .lindsey_provenance/
│   └── config.json                 # replicator_baseline, replicator_sha256, principal
├── operator/
│   ├── projects/
│   │   ├── REGISTRY.md
│   │   └── <slug>/
│   │       ├── INTAKE.md
│   │       ├── PROJECT_MANIFEST.json
│   │       ├── phases/PHASE_<N>.md
│   │       ├── proto/<modules>.py
│   │       ├── artifacts/...
│   │       ├── docs/...
│   │       └── notebooks/...
│   ├── briefs/
│   │   ├── BRIEF_LOG.md
│   │   └── <date>_<slug>.<ext>     # archived briefs
│   ├── proof_state_ledger/
│   │   └── LEDGER.jsonl            # append-only NDJSON
│   ├── ip_journal/
│   │   ├── JOURNAL.md
│   │   └── <slug>_IP_<date>.md
│   ├── sealed_core_audit/
│   │   ├── ALERTS.log
│   │   └── AUDIT_<YYYY-MM-DD>.md
│   └── templates/                  # copies of the lindsey-provenance templates
├── core/                           # YOUR sealed engine modules (optional)
└── docs/
    └── internal_record/            # triage docs, attestations
```

## The five audit gates

`lindsey-provenance audit` runs 5 independent checks:

| Gate | Check |
|---|---|
| `sealed_core` | SHA-256 of every file under `core/` matches the recorded baseline. Detects drift. |
| `inheritance` | Every project's `PROJECT_MANIFEST.json` declares the same `replicator_sha256` as `.lindsey_provenance/config.json`. |
| `ledger` | `proof_state_ledger/LEDGER.jsonl` is monotonic (no retrograde transitions) and every recorded SHA still matches the file on disk. |
| `ip_completeness` | Count of `# IP-CLAIM:` markers across `proto/` ≥ count of corresponding rows in the IP journal. |
| `phase_chains` | Each phase manifest's `inherits` SHA matches the actual prior phase manifest's `top_digest`. |

All 5 must return `ok: true` for `all_pass: true`.

## The six-state proof ledger

Transition allowed if and only if:

```
allowed = (
    (current == "idea"                 and next == "planned") or
    (current == "planned"              and next == "implemented") or
    (current == "implemented"          and next == "simulated") or
    (current == "simulated"            and next == "artifact-generated") or
    (current == "artifact-generated"   and next == "physically-validated")
)
```

Retrograde transitions are rejected with `ProofStateError`. To "rework" a
prior state, append a new `idea` row that references the artifact you're
reworking; this is detectable downstream.

The ledger is a single append-only NDJSON file. Each row carries:

- `ts`: ISO-8601 UTC timestamp
- `project`: slug
- `artifact`: relative path
- `from_state`, `to_state`
- `evidence_sha256`: SHA of the file at transition time
- `operator`: name from config
- `witness_operator`, `instrument_id`: required only for `physically-validated`
- `note`: free-text

## Phase-chain inheritance

The `freeze` command writes a manifest like:

```json
{
  "slug": "my-project",
  "phase": 2,
  "frozen_utc": "2026-05-20T05:15:00Z",
  "inherits": {
    "baseline": "my-engine.v1.freeze-1",
    "baseline_sha256": "abc...",
    "additional_projects": [
      ["my-project.phase1.freeze-1", "def..."]
    ]
  },
  "sources": [{"path": "proto/x.py", "sha256": "..."}, ...],
  "artifacts": [{"path": "artifacts/x.json", "sha256": "..."}, ...],
  "top_digest": "<sha256 over the sorted body bytes>"
}
```

`top_digest` is computed over the canonical-sort serialization of the
manifest body. Re-running `freeze` produces an identical `top_digest`
*only if every source and artifact file is byte-identical*. This makes
unintended drift trivially detectable: re-freeze, diff the digest.

## Config resolution

`lindsey_provenance.config` reads identity from (highest priority first):

1. `.lindsey_provenance/config.json` walking upward from cwd
2. Environment variables: `LINDSEY_PROVENANCE_REPLICATOR_BASELINE`, `LINDSEY_PROVENANCE_REPLICATOR_SHA256`, `LINDSEY_PROVENANCE_PRINCIPAL`, `LINDSEY_PROVENANCE_INSTITUTION`
3. Defaults (placeholder SHA = all zeros; tools warn if you haven't overridden)

## Adding a new tool

A new CLI tool should:

1. Live as a module in `lindsey_provenance/`.
2. Import path helpers from `lindsey_provenance._root`.
3. Import identity constants from `lindsey_provenance.config`.
4. Expose a `main()` returning an exit-code-style dict, plus `argparse` CLI.
5. Have a corresponding entry point in `pyproject.toml` under `[project.scripts]`.

Follow the existing modules as templates.
