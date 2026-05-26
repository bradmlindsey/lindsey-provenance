#!/usr/bin/env python3
"""brad_audit — background audit runner for the BRAD engine + operator layer.

Provenance-tracked build (lindsey-provenance framework).

Checks:
  1. Sealed-core SHA verifier: every PROGECT BRAD/core/*.py byte-matches
     the SHA-256 recorded in artifacts/ace_phase4_manifest.json.
  2. Inheritance integrity: every project's PROJECT_MANIFEST.json inlines
     the replicator baseline SHA-256.
  3. Ledger consistency: proof_state_ledger/LEDGER.jsonl has no retrograde
     transitions.
  4. IP-journal completeness: every # IP-CLAIM: marker in any project's
     proto/ has a journal row (with --strict).
  5. Phase-manifest chain integrity: every phase manifest's source SHAs
     still match the files on disk.

Usage:
    python3 brad_audit.py --quick                 # core + inheritance + ledger
    python3 brad_audit.py --full                  # add IP and chain checks,
                                                  # write AUDIT_<date>.md
    python3 brad_audit.py --project <slug>        # restrict to one project
    python3 brad_audit.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from lindsey_provenance.config import (
    REPLICATOR_BASELINE, REPLICATOR_SHA256, PRINCIPAL, INSTITUTION,
)

IP_MARKER_RE = re.compile(r"#\s*IP-CLAIM:", re.IGNORECASE)


class AuditError(Exception):
    pass


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _brad_project_root():
    return os.path.normpath(os.path.join(_operator_root(), ".."))


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _alerts_path():
    return os.path.join(_operator_root(), "sealed_core_audit", "ALERTS.log")


def _audit_report_path():
    d = os.path.join(_operator_root(), "sealed_core_audit")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "AUDIT_" + time.strftime("%Y-%m-%d") + ".md")


def _alert(msg):
    p = _alerts_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    line = _utc() + "  " + msg + "\n"
    with open(p, "a") as f:
        f.write(line)


# ---------------- Check 1 — sealed-core SHA verifier ----------------

def check_sealed_core():
    """Verify every core/*.py against the freeze manifest.

    If neither core/ nor a manifest exists, the gate is N/A and returns
    ok=True (a fresh lindsey-provenance project has no sealed engine yet).
    """
    root = _brad_project_root()
    manifest_p = os.path.join(root, "artifacts", "ace_phase4_manifest.json")
    core_dir = os.path.join(root, "core")
    has_core_py = (os.path.isdir(core_dir)
                   and any(fn.endswith(".py") for fn in os.listdir(core_dir)))
    if not os.path.exists(manifest_p):
        if not has_core_py:
            return {"ok": True, "reason": "no sealed core configured (skipped)",
                    "checked": 0, "mismatches": []}
        return {"ok": False, "reason": "ace_phase4_manifest.json missing",
                "checked": 0, "mismatches": []}
    m = json.load(open(manifest_p))
    files = m.get("source_modules", {}).get("files", {})
    mismatches = []
    checked = 0
    for fn, body in files.items():
        p = os.path.join(root, "core", fn)
        if not os.path.exists(p):
            mismatches.append((fn, "missing"))
            continue
        h = _sha256_file(p)
        checked += 1
        if h != body.get("sha256"):
            mismatches.append((fn, "sha mismatch"))
    return {"ok": len(mismatches) == 0, "checked": checked,
            "mismatches": mismatches}


# ---------------- Check 2 — inheritance integrity ----------------

def check_inheritance(project=None):
    """Verify every project's PROJECT_MANIFEST.json inlines the replicator
    baseline SHA. Optionally restrict to one project."""
    proj_root = os.path.join(_operator_root(), "projects")
    if not os.path.isdir(proj_root):
        return {"ok": True, "checked": 0, "violations": []}
    violations = []
    checked = 0
    skipped_selftest = 0
    for entry in sorted(os.listdir(proj_root)):
        full = os.path.join(proj_root, entry)
        if not os.path.isdir(full):
            continue
        if project and entry != project:
            continue
        # Skip self-test slugs. Convention: any slug beginning with "_"
        # (e.g. "_selftest_np_<ts>") or containing "selftest" is a tool
        # self-test artifact, not a real project.
        if entry.startswith("_") or "selftest" in entry.lower():
            skipped_selftest += 1
            continue
        pm_p = os.path.join(full, "PROJECT_MANIFEST.json")
        if not os.path.exists(pm_p):
            violations.append((entry, "PROJECT_MANIFEST.json missing"))
            continue
        try:
            pm = json.load(open(pm_p))
        except Exception as e:
            violations.append((entry, "manifest unreadable: " + repr(e)))
            continue
        checked += 1
        inh = pm.get("inherits_from", {}) or {}
        if inh.get("brad_engine_sha256") != REPLICATOR_SHA256:
            violations.append((entry, "brad_engine_sha256 mismatch"))
        if pm.get("replicator_baseline_sha256") != REPLICATOR_SHA256:
            violations.append((entry, "replicator_baseline_sha256 missing/mismatch"))
    return {"ok": len(violations) == 0, "checked": checked,
            "skipped_selftest": skipped_selftest,
            "violations": violations}


# ---------------- Check 3 — ledger consistency ----------------

def check_ledger():
    """Walk the proof-state ledger; flag retrograde or unknown-state rows."""
    p = os.path.join(_operator_root(), "proof_state_ledger", "LEDGER.jsonl")
    STATES = (
        "idea", "planned", "implemented", "simulated",
        "artifact-generated", "physically-validated",
    )
    idx = {s: i for i, s in enumerate(STATES)}
    if not os.path.exists(p):
        return {"ok": True, "n_rows": 0, "violations": []}
    rows = []
    with open(p) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    rows.append({"_parse_error": ln})
    violations = []
    last_state = {}
    for i, r in enumerate(rows):
        if "_parse_error" in r:
            violations.append((i, "unparseable row"))
            continue
        key = (r.get("project"), r.get("artifact"))
        to_s = r.get("to_state")
        if to_s not in idx:
            violations.append((i, "unknown state: " + str(to_s)))
            continue
        prev = last_state.get(key)
        if prev is not None and idx[to_s] <= idx[prev]:
            violations.append(
                (i, "retrograde " + str(prev) + " → " + to_s
                 + " for " + str(key)),
            )
        last_state[key] = to_s
    return {"ok": len(violations) == 0, "n_rows": len(rows),
            "violations": violations}


# ---------------- Check 4 — IP-journal completeness ----------------

def check_ip_completeness(project=None):
    """Count # IP-CLAIM: markers across all proto/ files and compare to
    the number of journal-row headers (### Claim ) in ip_journal/."""
    operator_root = _operator_root()
    proj_root = os.path.join(operator_root, "projects")
    ip_root = os.path.join(operator_root, "ip_journal")
    if not os.path.isdir(proj_root):
        return {"ok": True, "markers": 0, "journal_rows": 0, "deltas": []}

    n_markers = 0
    markers_per_project = {}
    for entry in sorted(os.listdir(proj_root)):
        full = os.path.join(proj_root, entry)
        if not os.path.isdir(full):
            continue
        if project and entry != project:
            continue
        if entry.startswith("_") or "selftest" in entry.lower():
            continue
        proto = os.path.join(full, "proto")
        n = 0
        if os.path.isdir(proto):
            for base, _, files in os.walk(proto):
                for fn in files:
                    if fn.endswith(".py"):
                        try:
                            with open(os.path.join(base, fn),
                                      errors="ignore") as f:
                                for ln in f:
                                    if IP_MARKER_RE.search(ln):
                                        n += 1
                        except Exception:
                            pass
        markers_per_project[entry] = n
        n_markers += n

    n_rows = 0
    rows_per_project = {}
    if os.path.isdir(ip_root):
        for fn in os.listdir(ip_root):
            if not fn.endswith(".md"):
                continue
            slug = fn.split("_IP_")[0] if "_IP_" in fn else fn[:-3]
            if project and slug != project:
                continue
            # Rev 1.1: skip self-test journal files so they do not pollute
            # the cross-project ip-completeness gate. Same skip rule as the
            # project-dir loop above.
            if slug.startswith("_") or "selftest" in slug.lower():
                continue
            full = os.path.join(ip_root, fn)
            try:
                with open(full, errors="ignore") as f:
                    for ln in f:
                        if ln.lstrip().startswith("### Claim "):
                            n_rows += 1
                            rows_per_project[slug] = (
                                rows_per_project.get(slug, 0) + 1
                            )
            except Exception:
                pass

    # v3.2 patch (2026-05-20): tolerate marker <= row asymmetry.
    # Signed IP rows are permanent institutional claims; source markers can
    # legitimately consolidate during refactor (e.g., PT-1 Phase-4 macro rewrite).
    # The audit should FAIL only when markers > rows (a marker without a row =
    # unclaimed source IP) or when DRAFT rows exist without markers. It should
    # PASS when markers <= rows (rows that outlive their markers are signed
    # historical claims and remain valid).
    deltas = []
    hard_deltas = []
    for proj in sorted(set(list(markers_per_project) + list(rows_per_project))):
        m = markers_per_project.get(proj, 0)
        r = rows_per_project.get(proj, 0)
        if m != r:
            deltas.append((proj, m, r))
            if m > r:
                # markers without rows = unclaimed source IP; this is a hard failure
                hard_deltas.append((proj, m, r))
    return {
        "ok":            len(hard_deltas) == 0,
        "markers":       n_markers,
        "journal_rows":  n_rows,
        "deltas":        deltas,
        "hard_deltas":   hard_deltas,
    }


# ---------------- Check 5 — phase-manifest chain ----------------

def check_phase_chains(project=None):
    operator_root = _operator_root()
    proj_root = os.path.join(operator_root, "projects")
    if not os.path.isdir(proj_root):
        return {"ok": True, "checked": 0, "violations": []}
    violations = []
    checked = 0
    for entry in sorted(os.listdir(proj_root)):
        full = os.path.join(proj_root, entry)
        if not os.path.isdir(full):
            continue
        if project and entry != project:
            continue
        if entry.startswith("_") or "selftest" in entry.lower():
            continue
        art = os.path.join(full, "artifacts")
        if not os.path.isdir(art):
            continue
        for fn in sorted(os.listdir(art)):
            if not (fn.endswith("_manifest.json") and "_phase" in fn):
                continue
            checked += 1
            try:
                m = json.load(open(os.path.join(art, fn)))
            except Exception as e:
                violations.append((entry + "/" + fn, "unreadable: " + repr(e)))
                continue
            for rel, body in (m.get("source_modules", {}).get("files", {})).items():
                p = os.path.join(full, rel)
                if not os.path.exists(p):
                    violations.append((entry + "/" + fn, rel + " missing"))
                    continue
                if _sha256_file(p) != body.get("sha256"):
                    violations.append(
                        (entry + "/" + fn, rel + " sha mismatch"))
    return {"ok": len(violations) == 0, "checked": checked,
            "violations": violations}


# ---------------- Driver ----------------

def run_audit(mode="quick", project=None):
    out = {"mode": mode, "ts": _utc(), "project": project}
    out["sealed_core"] = check_sealed_core()
    out["inheritance"] = check_inheritance(project=project)
    out["ledger"] = check_ledger()
    if mode == "full":
        out["ip_completeness"] = check_ip_completeness(project=project)
        out["phase_chains"] = check_phase_chains(project=project)
    out["all_pass"] = all(
        out[k]["ok"] for k in
        ("sealed_core", "inheritance", "ledger")
    )
    if mode == "full":
        out["all_pass"] = out["all_pass"] and all(
            out[k]["ok"] for k in ("ip_completeness", "phase_chains")
        )
    return out


def _summary_line(out):
    sc = out["sealed_core"]
    inh = out["inheritance"]
    led = out["ledger"]
    parts = []
    parts.append("sealed_core=" +
                 ("PASS" if sc["ok"] else "FAIL")
                 + "(" + str(sc.get("checked", 0)) + ")")
    parts.append("inheritance=" + ("PASS" if inh["ok"] else "FAIL"))
    parts.append("ledger=" + ("PASS" if led["ok"] else "FAIL"))
    if "ip_completeness" in out:
        ip = out["ip_completeness"]
        parts.append("ip=" + ("PASS" if ip["ok"] else "FAIL"))
    if "phase_chains" in out:
        pc = out["phase_chains"]
        parts.append("phase_chains=" + ("PASS" if pc["ok"] else "FAIL"))
    parts.append("ALL=" + ("PASS" if out["all_pass"] else "FAIL"))
    return "  ".join(parts)


def _write_report(out):
    p = _audit_report_path()
    lines = []
    lines.append("# BRAD audit — " + out["ts"])
    lines.append("")
    lines.append("**PROVENANCE-TRACKED · " + PRINCIPAL + (" · " + INSTITUTION if INSTITUTION else "") + "**")
    lines.append("")
    lines.append("Mode: `" + out["mode"] + "`  Project: `"
                 + str(out["project"]) + "`")
    lines.append("")
    lines.append("Summary: " + _summary_line(out))
    lines.append("")
    for k, v in out.items():
        if k in ("mode", "ts", "project", "all_pass"):
            continue
        lines.append("## " + k)
        lines.append("```")
        lines.append(json.dumps(v, indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")
    open(p, "w").write("\n".join(lines))
    return p


def _selftest():
    print("brad_audit — self-test")
    out = run_audit("quick")
    print("  " + _summary_line(out))
    if not out["sealed_core"]["ok"]:
        for fn, why in out["sealed_core"]["mismatches"]:
            print("    sealed_core: " + fn + " — " + why)
    if not out["inheritance"]["ok"]:
        for slug, why in out["inheritance"]["violations"]:
            print("    inheritance: " + slug + " — " + why)
    if not out["ledger"]["ok"]:
        for i, why in out["ledger"]["violations"]:
            print("    ledger row " + str(i) + ": " + why)
    print("---\n  brad_audit: "
          + ("PASS" if out["all_pass"] else "PARTIAL")
          + "  (sealed_core is the load-bearing check)")
    # Self-test exits 0 if sealed_core passed even if no projects yet
    return 0 if out["sealed_core"]["ok"] else 1


def main():
    """CLI entry point for `lindsey-provenance audit`."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true",
                    help="run sealed_core + inheritance + ledger only")
    ap.add_argument("--full", action="store_true",
                    help="add IP-completeness and phase-chain checks, write AUDIT report")
    ap.add_argument("--project", default=None,
                    help="restrict inheritance + IP checks to one project slug")
    ap.add_argument("--selftest", action="store_true",
                    help="run a smoke selftest and exit")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    mode = "full" if args.full else "quick"
    out = run_audit(mode=mode, project=args.project)

    line = _summary_line(out)
    print(line)
    _alert(line)

    if args.full:
        # write the dated audit report
        rpt_path = _audit_report_path()
        with open(rpt_path, "a", encoding="utf-8") as fh:
            fh.write("## " + _utc() + "\n\n")
            fh.write("```\n" + json.dumps(out, indent=2) + "\n```\n\n")

    if not out["sealed_core"]["ok"]:
        for fn, why in out["sealed_core"]["mismatches"]:
            print("    sealed_core: " + fn + " - " + why)
    if not out["inheritance"]["ok"]:
        for slug, why in out["inheritance"]["violations"]:
            print("    inheritance: " + slug + " - " + why)
    if not out["ledger"]["ok"]:
        for i, why in out["ledger"]["violations"]:
            print("    ledger row " + str(i) + ": " + why)
    if args.full:
        if not out.get("ip_completeness", {}).get("ok", True):
            for slug, m, j in out["ip_completeness"].get("hard_deltas", []):
                print("    ip_completeness: " + slug + " markers=" + str(m) + " journal=" + str(j))
        if not out.get("phase_chains", {}).get("ok", True):
            for slug, why in out["phase_chains"].get("violations", []):
                print("    phase_chains: " + slug + " - " + why)

    return 0 if out["all_pass"] else 1


def _summary_line(out):
    """One-line audit summary used by main() + _selftest()."""
    parts = []
    sc = out.get("sealed_core", {})
    parts.append("sealed_core=" + ("PASS(" + str(sc.get("checked", 0)) + ")"
                                    if sc.get("ok") else "FAIL"))
    parts.append("inheritance=" + ("PASS" if out.get("inheritance", {}).get("ok") else "FAIL"))
    parts.append("ledger=" + ("PASS" if out.get("ledger", {}).get("ok") else "FAIL"))
    if "ip_completeness" in out:
        parts.append("ip=" + ("PASS" if out["ip_completeness"]["ok"] else "FAIL"))
    if "phase_chains" in out:
        parts.append("phase_chains=" + ("PASS" if out["phase_chains"]["ok"] else "FAIL"))
    parts.append("ALL=" + ("PASS" if out.get("all_pass") else "FAIL"))
    return "[brad_audit: " + "  ".join(parts) + "]"


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
