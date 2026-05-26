#!/usr/bin/env python3
"""brad_status - single-command operator dashboard (v2/rev 1.1).

Provenance-tracked build (lindsey-provenance framework).

Reports: sealed engine SHA, active projects, ledger summary, audit state,
IP-draft counts. The dashboard tool every operator runs at session start.
"""
from __future__ import annotations

import json
import os
import sys
import time
from lindsey_provenance.config import (
    REPLICATOR_BASELINE, REPLICATOR_SHA256, PRINCIPAL, INSTITUTION,
)

def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def status():
    op = _operator_root()
    out = dict()
    out["ts"] = _utc()
    out["replicator_baseline"] = REPLICATOR_BASELINE
    out["replicator_baseline_sha256"] = REPLICATOR_SHA256
    out["principal"] = PRINCIPAL

    # Projects
    proj_dir = os.path.join(op, "projects")
    projects_real = []
    projects_selftest = []
    if os.path.isdir(proj_dir):
        for entry in sorted(os.listdir(proj_dir)):
            full = os.path.join(proj_dir, entry)
            if not os.path.isdir(full):
                continue
            if entry.startswith("_") or "selftest" in entry.lower():
                projects_selftest.append(entry)
            else:
                projects_real.append(entry)
    out["projects_real_n"] = len(projects_real)
    out["projects_real"] = projects_real
    out["projects_selftest_residue_n"] = len(projects_selftest)

    # Ledger summary
    led_p = os.path.join(op, "proof_state_ledger", "LEDGER.jsonl")
    n_rows = 0
    by_state = dict()
    if os.path.exists(led_p):
        for ln in open(led_p):
            ln = ln.strip()
            if not ln:
                continue
            try:
                row = json.loads(ln)
            except Exception:
                continue
            n_rows += 1
            ts = row.get("to_state")
            if ts:
                by_state[ts] = by_state.get(ts, 0) + 1
    out["ledger_rows"] = n_rows
    out["ledger_by_state"] = by_state

    # IP journal
    ip_dir = os.path.join(op, "ip_journal")
    ip_draft = 0
    ip_signed = 0
    ip_files = 0
    if os.path.isdir(ip_dir):
        for fn in os.listdir(ip_dir):
            if not fn.endswith(".md"):
                continue
            slug = fn.split("_IP_")[0] if "_IP_" in fn else fn[:-3]
            if slug.startswith("_") or "selftest" in slug.lower():
                continue
            ip_files += 1
            try:
                txt = open(os.path.join(ip_dir, fn), errors="ignore").read()
            except Exception:
                continue
            ip_draft += txt.count("Status:` `DRAFT`")
            ip_draft += txt.count("Status:** `DRAFT`")
            ip_signed += txt.count("Status:** `SIGNED`")
            ip_signed += txt.count("Status:` `SIGNED`")
    out["ip_journal_files"] = ip_files
    out["ip_rows_draft"] = ip_draft
    out["ip_rows_signed"] = ip_signed

    # Latest audit log line
    alerts_p = os.path.join(op, "sealed_core_audit", "ALERTS.log")
    last_alert = None
    if os.path.exists(alerts_p):
        for ln in open(alerts_p):
            ln = ln.strip()
            if ln:
                last_alert = ln
    out["last_audit_alert"] = last_alert
    return out


def main():
    s = status()
    print("=" * 60)
    print(" BRAD OPERATOR STATUS - " + s["ts"])
    print("=" * 60)
    print("Replicator baseline    : " + s["replicator_baseline"])
    print("Replicator SHA-256     : " + s["replicator_baseline_sha256"])
    print("Principal              : " + s["principal"])
    print("")
    print("Active projects        : " + str(s["projects_real_n"]))
    for proj in s["projects_real"]:
        print("    - " + proj)
    if s["projects_selftest_residue_n"]:
        print("Self-test residue dirs : " + str(s["projects_selftest_residue_n"]))
    print("")
    print("Ledger rows total      : " + str(s["ledger_rows"]))
    for state, n in sorted(s["ledger_by_state"].items()):
        print("    " + state.ljust(22) + ": " + str(n))
    print("")
    print("IP journal files       : " + str(s["ip_journal_files"]))
    print("    DRAFT rows         : " + str(s["ip_rows_draft"]))
    print("    SIGNED rows        : " + str(s["ip_rows_signed"]))
    print("")
    if s["last_audit_alert"]:
        print("Last audit alert       :")
        print("    " + s["last_audit_alert"])
    else:
        print("Last audit alert       : (none)")
    print("=" * 60)


if __name__ == "__main__":
    main()
