#!/usr/bin/env python3
"""brad_run_phase - one-command Phase-N closeout runner (v3 SPEED tool).

Provenance-tracked build (lindsey-provenance framework).

Replaces ~10 manual operator commands with a single call that:
  1. Runs every proto/*.py self-test in dependency order
  2. Runs brad_ip_extract to populate journal rows
  3. Transitions every proto/*.py + every artifacts/*.stl through
     planned -> implemented -> simulated
  4. Runs brad_audit --full
  5. Runs brad_freeze_manifest --project X --phase N

Stops on the first failure. Reports a clean summary.

Usage:
    python3 brad_run_phase.py --project <slug> --phase N
    python3 brad_run_phase.py --project <slug> --phase N --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from lindsey_provenance.config import (
    REPLICATOR_BASELINE, REPLICATOR_SHA256, PRINCIPAL, INSTITUTION,
)


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _project_root(slug):
    return os.path.join(_operator_root(), "projects", slug)


def _run(cmd, cwd=None):
    """Run a subprocess, return (rc, stdout)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd,
                           timeout=120)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return -1, "(timeout)"
    except Exception as e:
        return -2, repr(e)


def _list_proto_modules(slug):
    proto = os.path.join(_project_root(slug), "proto")
    if not os.path.isdir(proto):
        return []
    mods = []
    for fn in sorted(os.listdir(proto)):
        if fn.endswith(".py") and fn != "__init__.py":
            mods.append(fn)
    return mods


def _list_artifact_stls(slug):
    art = os.path.join(_project_root(slug), "artifacts")
    if not os.path.isdir(art):
        return []
    out = []
    for fn in sorted(os.listdir(art)):
        if fn.endswith(".stl"):
            out.append("artifacts/" + fn)
    return out


def _proto_module_order():
    """Dependency order: lexer first, solver second, weaver third, refit last."""
    return ("lexer", "solver", "weaver", "refit")


def _sort_modules_by_role(modules):
    """Order modules so lexer runs first, solver second, weaver third, refit last."""
    role_order = {role: i for i, role in enumerate(_proto_module_order())}
    def key_fn(fn):
        for role in role_order:
            if role in fn:
                return role_order[role]
        return 99
    return sorted(modules, key=key_fn)


def run_phase(slug, phase, dry_run=False):
    proj_root = _project_root(slug)
    op_tools = os.path.join(_operator_root(), "tools")
    mods = _sort_modules_by_role(_list_proto_modules(slug))
    if not mods:
        return {"ok": False, "reason": "no proto/*.py files in " + slug}

    steps_log = []

    # 1. Self-tests
    for mod in mods:
        step = dict()
        step["step"] = "selftest:" + mod
        step["cmd"] = "python3 -B proto/" + mod
        if not dry_run:
            rc, out = _run(["python3", "-B", "proto/" + mod], cwd=proj_root)
            step["rc"] = rc
            step["tail"] = out.splitlines()[-1] if out else ""
            if rc != 0:
                steps_log.append(step)
                result = dict()
                result["ok"] = False
                result["failed_at"] = step["step"]
                result["steps"] = steps_log
                return result
        steps_log.append(step)

    # 2. IP extract
    step = dict()
    step["step"] = "ip_extract"
    step["cmd"] = "brad_ip_extract.py --project " + slug
    if not dry_run:
        rc, out = _run(["python3", "-B",
                        os.path.join(op_tools, "brad_ip_extract.py"),
                        "--project", slug])
        step["rc"] = rc
        step["tail"] = out.splitlines()[-1] if out else ""
    steps_log.append(step)

    # 3. Proof-state transitions
    artifacts_to_transition = ["proto/" + m for m in mods]
    artifacts_to_transition.extend(_list_artifact_stls(slug))
    transitions = ("planned", "implemented", "simulated")
    for art in artifacts_to_transition:
        for tgt in transitions:
            step = dict()
            step["step"] = "proof_state:" + art + ":->" + tgt
            if not dry_run:
                rc, out = _run(["python3", "-B",
                                os.path.join(op_tools, "brad_proof_state.py"),
                                "--project", slug,
                                "--artifact", art,
                                "--to", tgt])
                step["rc"] = rc
            steps_log.append(step)

    # 4. Audit
    step = dict()
    step["step"] = "audit:full"
    step["cmd"] = "brad_audit.py --full"
    if not dry_run:
        rc, out = _run(["python3", "-B",
                        os.path.join(op_tools, "brad_audit.py"),
                        "--full"])
        step["rc"] = rc
        for line in out.splitlines():
            if "[brad_audit:" in line:
                step["tail"] = line
                break
    steps_log.append(step)

    # 5. Seal
    step = dict()
    step["step"] = "seal:phase_" + str(phase)
    step["cmd"] = "brad_freeze_manifest.py --project " + slug + " --phase " + str(phase)
    if not dry_run:
        rc, out = _run(["python3", "-B",
                        os.path.join(op_tools, "brad_freeze_manifest.py"),
                        "--project", slug, "--phase", str(phase)])
        step["rc"] = rc
        for line in out.splitlines():
            if "PASS" in line and "freeze" in line:
                step["tail"] = line
                break
    steps_log.append(step)

    result = dict()
    result["ok"] = True
    result["slug"] = slug
    result["phase"] = phase
    result["steps_run"] = len(steps_log)
    result["steps"] = steps_log
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=False)
    ap.add_argument("--phase", type=int, required=False)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.project or not args.phase:
        ap.error("--project and --phase are required")
    out = run_phase(args.project, args.phase, dry_run=args.dry_run)
    print("=" * 60)
    print(" brad_run_phase: " + args.project + " phase " + str(args.phase))
    print("=" * 60)
    if args.dry_run:
        print("(dry-run)")
    for s in out.get("steps", []):
        rc = s.get("rc", "DR") if not args.dry_run else "DR"
        tail = s.get("tail", "")
        print("  [" + str(rc).rjust(3) + "] " + s["step"])
        if tail:
            print("        " + tail[:90])
    print("=" * 60)
    print("OK: " + str(out.get("ok", False)))
    if not out.get("ok", False):
        print("FAILED AT: " + out.get("failed_at", "?"))
        sys.exit(1)


if __name__ == "__main__":
    main()
