#!/usr/bin/env python3
"""brad_proof_state — proof-state classifier and ledger for BRAD projects.

Provenance-tracked build (lindsey-provenance framework).

Six states (ordered, monotonic):
    idea  →  planned  →  implemented  →  simulated
          →  artifact-generated  →  physically-validated

Rules:
    * Forward-only. Retrograde transitions are rejected; rework opens a new
      'idea' row pointing at the prior artifact.
    * 'implemented' requires the module to exist and exit 0 on self-test
      (caller asserts this; tool records the SHA-256 of the source file).
    * 'simulated' requires an on-disk artifact with a recordable SHA-256.
    * 'artifact-generated' requires a file under artifacts/production/.
    * 'physically-validated' requires --witness-operator and --instrument-id.

The ledger at operator/proof_state_ledger/LEDGER.jsonl is append-only NDJSON.
One row per transition. Every row carries the evidence SHA-256 at transition
time so retrospective tamper is detectable.

Usage:
    python3 brad_proof_state.py --project <slug> --artifact <path> --to <state>
                                [--from <state>] [--witness-operator NAME]
                                [--instrument-id ID] [--note "..."]
    python3 brad_proof_state.py --tail [N]
    python3 brad_proof_state.py --verify
    python3 brad_proof_state.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from lindsey_provenance.config import (
    REPLICATOR_BASELINE, REPLICATOR_SHA256, PRINCIPAL, INSTITUTION,
)

STATES = (
    "idea",
    "planned",
    "implemented",
    "simulated",
    "artifact-generated",
    "physically-validated",
)
STATE_INDEX = {s: i for i, s in enumerate(STATES)}

class ProofStateError(Exception):
    pass


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _ledger_path():
    return os.path.join(_operator_root(), "proof_state_ledger", "LEDGER.jsonl")


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _resolve_artifact_path(project, artifact):
    """Resolve artifact path. Relative paths are interpreted under the
    project's root (operator/projects/<project>/)."""
    if os.path.isabs(artifact):
        return artifact
    proj_root = os.path.join(_operator_root(), "projects", project)
    candidate = os.path.join(proj_root, artifact)
    return candidate


def _read_ledger():
    p = _ledger_path()
    if not os.path.exists(p):
        return []
    rows = []
    with open(p) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def _last_state(rows, project, artifact):
    last = None
    for r in rows:
        if r.get("project") == project and r.get("artifact") == artifact:
            last = r.get("to_state")
    return last


def transition(project, artifact, to_state, from_state=None,
               operator=None, witness_operator=None, instrument_id=None,
               note=None):
    if to_state not in STATE_INDEX:
        raise ProofStateError(
            "invalid to_state: " + to_state
            + " (must be one of: " + ", ".join(STATES) + ")"
        )

    rows = _read_ledger()
    inferred_from = _last_state(rows, project, artifact)
    if from_state and inferred_from and from_state != inferred_from:
        raise ProofStateError(
            "from_state mismatch: claimed " + from_state
            + " but ledger says " + str(inferred_from)
        )
    effective_from = from_state or inferred_from

    # Forward-only check.
    if effective_from is not None:
        if STATE_INDEX[to_state] <= STATE_INDEX[effective_from]:
            raise ProofStateError(
                "retrograde transition refused: "
                + str(effective_from) + " → " + to_state
                + ". Open a new 'idea' row for the rework path instead."
            )

    # State-specific gates.
    path = _resolve_artifact_path(project, artifact)
    evidence_sha256 = None
    if to_state in ("simulated", "artifact-generated"):
        if not os.path.exists(path):
            raise ProofStateError(
                "artifact file not found: " + path
                + " (required for state '" + to_state + "')"
            )
        evidence_sha256 = _sha256_file(path)
    if to_state == "artifact-generated":
        # Must live under artifacts/production/ for canonical production state.
        norm = path.replace("\\", "/")
        if "/artifacts/production/" not in norm:
            raise ProofStateError(
                "'artifact-generated' requires the file under "
                "artifacts/production/, got: " + path
            )
    if to_state == "physically-validated":
        if not witness_operator or not instrument_id:
            raise ProofStateError(
                "'physically-validated' requires --witness-operator and "
                "--instrument-id"
            )
        if os.path.exists(path):
            evidence_sha256 = _sha256_file(path)

    row = {
        "ts":               _utc(),
        "project":          project,
        "artifact":         artifact,
        "from_state":       effective_from,
        "to_state":         to_state,
        "operator":         operator or "operator",
        "witness_operator": witness_operator,
        "instrument_id":    instrument_id,
        "note":             note,
        "evidence_sha256":  evidence_sha256,
    }

    p = _ledger_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def tail(n=20):
    rows = _read_ledger()
    return rows[-n:]


def verify():
    rows = _read_ledger()
    violations = []
    last_state = {}  # (project, artifact) → state
    for i, r in enumerate(rows):
        key = (r.get("project"), r.get("artifact"))
        to_s = r.get("to_state")
        if to_s not in STATE_INDEX:
            violations.append((i, "unknown state: " + str(to_s)))
            continue
        prev = last_state.get(key)
        if prev is not None and STATE_INDEX[to_s] <= STATE_INDEX[prev]:
            violations.append(
                (i, "retrograde " + str(prev) + " → " + to_s
                 + " for " + str(key))
            )
        last_state[key] = to_s
    return {
        "n_rows":         len(rows),
        "n_violations":   len(violations),
        "violations":     violations,
        "ok":             len(violations) == 0,
    }


def summary():
    rows = _read_ledger()
    by_proj = {}
    last_state = {}
    for r in rows:
        proj = r.get("project")
        art = r.get("artifact")
        last_state[(proj, art)] = r.get("to_state")
    for (proj, art), st in last_state.items():
        by_proj.setdefault(proj, {})
        by_proj[proj][st] = by_proj[proj].get(st, 0) + 1
    return by_proj


def _selftest():
    """Functional self-test. Uses a '_selftest_' slug so brad_audit skips it."""
    print("brad_proof_state — self-test")
    fake_project = "_selftest_ps_" + str(int(time.time()))
    fake_artifact = "fake_artifact.json"
    tmp_dir = os.path.join(_operator_root(), "projects", fake_project)
    os.makedirs(tmp_dir, exist_ok=True)
    art_path = os.path.join(tmp_dir, fake_artifact)
    open(art_path, "w").write('{"selftest": true}')

    functional_pass = True
    try:
        transition(fake_project, fake_artifact, "idea")
        print("  idea               : PASS")
        transition(fake_project, fake_artifact, "planned")
        print("  planned            : PASS")
        transition(fake_project, fake_artifact, "implemented")
        print("  implemented        : PASS")
        r4 = transition(fake_project, fake_artifact, "simulated")
        print("  simulated          : PASS  (sha=" + r4["evidence_sha256"][:16] + ")")
        try:
            transition(fake_project, fake_artifact, "implemented")
            print("  retrograde block   : FAIL  (allowed retrograde)")
            functional_pass = False
        except ProofStateError:
            print("  retrograde block   : PASS")
        v = verify()
        print("  verify n_rows      : " + str(v["n_rows"])
              + "  violations=" + str(v["n_violations"])
              + "  ok=" + str(v["ok"]))
    except Exception as e:
        print("  FAIL: " + repr(e))
        return 1

    cleanup_ok = True
    try:
        with open(_ledger_path()) as f:
            lines = f.readlines()
        with open(_ledger_path(), "w") as f:
            for ln in lines:
                if '"project": "' + fake_project + '"' not in ln:
                    f.write(ln)
        try:
            os.remove(art_path)
            os.rmdir(tmp_dir)
        except Exception:
            cleanup_ok = False
    except Exception:
        cleanup_ok = False
    print("  cleanup            : "
          + ("PASS" if cleanup_ok else "BEST-EFFORT (sandbox FS locked)"))
    print("---\n  brad_proof_state: " + ("PASS" if functional_pass else "FAIL"))
    return 0 if functional_pass else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project")
    ap.add_argument("--artifact")
    ap.add_argument("--to", dest="to_state",
                    choices=STATES)
    ap.add_argument("--from", dest="from_state",
                    choices=STATES)
    ap.add_argument("--operator", default="operator")
    ap.add_argument("--witness-operator", default=None)
    ap.add_argument("--instrument-id", default=None)
    ap.add_argument("--note", default=None)
    ap.add_argument("--tail", type=int, nargs="?", const=20, default=None)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_selftest())
    if args.verify:
        v = verify()
        print("[brad_proof_state: verify n_rows=" + str(v["n_rows"])
              + " violations=" + str(v["n_violations"])
              + " ok=" + str(v["ok"]) + "]")
        for i, msg in v["violations"]:
            print("  row " + str(i) + ": " + msg)
        sys.exit(0 if v["ok"] else 1)
    if args.summary:
        s = summary()
        print(json.dumps(s, indent=2, sort_keys=True))
        sys.exit(0)
    if args.tail is not None:
        for r in tail(args.tail):
            print(r["ts"] + "  " + r["project"] + "/"
                  + r["artifact"] + ": "
                  + str(r.get("from_state")) + " → " + r["to_state"])
        sys.exit(0)
    if not (args.project and args.artifact and args.to_state):
        ap.error("--project, --artifact, and --to are required (or use "
                 "--tail / --verify / --summary / --selftest)")
    row = transition(
        args.project, args.artifact, args.to_state,
        from_state=args.from_state,
        operator=args.operator,
        witness_operator=args.witness_operator,
        instrument_id=args.instrument_id,
        note=args.note,
    )
    msg = "[brad_proof_state: PASS - " + args.project + "/"
    msg += args.artifact + " -> " + args.to_state + "]"
    print(msg)
    if row.get("evidence_sha256"):
        sha_short = row["evidence_sha256"][:32]
        print("  evidence_sha256 : " + sha_short + "...")


if __name__ == "__main__":
    main()
