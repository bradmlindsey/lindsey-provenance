#!/usr/bin/env python3
"""purge_selftest - remove leftover self-test residue from operator state.

Provenance-tracked build (lindsey-provenance framework).

Removes self-test residue from:
    operator/projects/_*_selftest_*/, operator/projects/selftest-*/
    operator/projects/REGISTRY.md  (rows for self-test slugs)
    operator/proof_state_ledger/LEDGER.jsonl  (rows for self-test slugs)
    operator/ip_journal/_*selftest*_IP_*.md, selftest*_IP_*.md

Default: --dry-run (lists what would be removed, makes NO changes).
Use --execute on a real workstation where the filesystem permits deletes.
Every action is logged to operator/sealed_core_audit/PURGE_<UTC>.log
"""
from __future__ import annotations

import argparse
import os
import shutil
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


def _is_selftest_slug(slug):
    return slug.startswith("_") or "selftest" in slug.lower()


def _scan_projects():
    proj_root = os.path.join(_operator_root(), "projects")
    if not os.path.isdir(proj_root):
        return []
    found = []
    for entry in sorted(os.listdir(proj_root)):
        full = os.path.join(proj_root, entry)
        if os.path.isdir(full) and _is_selftest_slug(entry):
            found.append(full)
    return found


def _scan_ip_journals():
    ip_root = os.path.join(_operator_root(), "ip_journal")
    if not os.path.isdir(ip_root):
        return []
    found = []
    for fn in sorted(os.listdir(ip_root)):
        if not fn.endswith(".md"):
            continue
        slug = fn.split("_IP_")[0] if "_IP_" in fn else fn[:-3]
        if _is_selftest_slug(slug):
            found.append(os.path.join(ip_root, fn))
    return found


def _registry_purge_lines():
    p = os.path.join(_operator_root(), "projects", "REGISTRY.md")
    if not os.path.exists(p):
        return p, []
    keep_rows = []
    drop_rows = []
    for ln in open(p):
        stripped = ln.strip()
        if stripped.startswith("| `") and stripped.endswith(" |"):
            slug = stripped.split("`")[1] if "`" in stripped else ""
            if _is_selftest_slug(slug):
                drop_rows.append(ln.rstrip())
                continue
        keep_rows.append(ln)
    return p, drop_rows, keep_rows


def _ledger_purge_rows():
    p = os.path.join(_operator_root(), "proof_state_ledger", "LEDGER.jsonl")
    if not os.path.exists(p):
        return p, [], []
    keep = []
    drop = []
    import json
    for ln in open(p):
        s = ln.strip()
        if not s:
            continue
        try:
            row = json.loads(s)
        except Exception:
            keep.append(ln)
            continue
        proj = row.get("project", "")
        if _is_selftest_slug(proj):
            drop.append(s[:120] + ("..." if len(s) > 120 else ""))
        else:
            keep.append(ln)
    return p, drop, keep


def _log_action(msg, log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(_utc() + "  " + msg + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true",
                    help="actually delete (default is dry-run)")
    args = ap.parse_args()

    dry = not args.execute
    log_path = os.path.join(_operator_root(), "sealed_core_audit",
                             "PURGE_" + time.strftime("%Y-%m-%dT%H-%M-%SZ") + ".log")
    print("purge_selftest (" + ("dry-run" if dry else "EXECUTE") + ")")
    print("audit log: " + log_path)
    if not dry:
        _log_action("BEGIN purge (execute)", log_path)

    # Projects
    proj_dirs = _scan_projects()
    print("\nSelf-test project directories: " + str(len(proj_dirs)))
    for d in proj_dirs:
        print("  " + ("would rmtree " if dry else "rmtree ") + d)
        if not dry:
            try:
                shutil.rmtree(d)
                _log_action("rmtree OK: " + d, log_path)
            except Exception as e:
                _log_action("rmtree FAIL: " + d + " " + repr(e), log_path)

    # IP journal files
    ip_files = _scan_ip_journals()
    print("\nSelf-test IP-journal files: " + str(len(ip_files)))
    for f in ip_files:
        print("  " + ("would remove " if dry else "remove ") + f)
        if not dry:
            try:
                os.remove(f)
                _log_action("remove OK: " + f, log_path)
            except Exception as e:
                _log_action("remove FAIL: " + f + " " + repr(e), log_path)

    # Registry
    reg_result = _registry_purge_lines()
    if len(reg_result) == 3:
        reg_p, reg_drop, reg_keep = reg_result
        print("\nRegistry rows to purge: " + str(len(reg_drop)))
        for ln in reg_drop:
            print("  " + ln)
        if not dry and reg_drop:
            try:
                open(reg_p, "w").write("".join(reg_keep))
                _log_action("registry purged: " + str(len(reg_drop)) + " rows", log_path)
            except Exception as e:
                _log_action("registry FAIL: " + repr(e), log_path)

    # Ledger
    led_p, led_drop, led_keep = _ledger_purge_rows()
    print("\nLedger rows to purge: " + str(len(led_drop)))
    for s in led_drop[:5]:
        print("  " + s)
    if len(led_drop) > 5:
        print("  ... and " + str(len(led_drop) - 5) + " more")
    if not dry and led_drop:
        try:
            open(led_p, "w").write("".join(led_keep))
            _log_action("ledger purged: " + str(len(led_drop)) + " rows", log_path)
        except Exception as e:
            _log_action("ledger FAIL: " + repr(e), log_path)

    print("\n" + ("DRY-RUN complete (use --execute to apply)" if dry else "PURGE complete"))


if __name__ == "__main__":
    main()
