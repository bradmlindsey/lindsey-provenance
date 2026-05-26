#!/usr/bin/env python3
"""brad_sign_ip - Principal-signing tool for IP-journal rows.

Provenance-tracked build (lindsey-provenance framework).

Flips DRAFT IP-journal rows to SIGNED, records the Principal's signature UTC,
and appends a one-line index entry to operator/ip_journal/JOURNAL.md.

Usage:
    brad_sign_ip.py --list                     # show pending DRAFT rows
    brad_sign_ip.py --sign <claim-id>          # sign one claim
    brad_sign_ip.py --sign-all                 # sign every pending DRAFT row
    brad_sign_ip.py --project <slug>           # restrict to one project
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from lindsey_provenance.config import (
    REPLICATOR_BASELINE, REPLICATOR_SHA256, PRINCIPAL, INSTITUTION,
)


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _ip_dir():
    return os.path.join(_operator_root(), "ip_journal")


def _master_path():
    return os.path.join(_ip_dir(), "JOURNAL.md")


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


CLAIM_HDR_RE = re.compile(r"^### Claim `(?P<cid>[a-z0-9-]+IP-\d+)`")
STATUS_LINE_RE = re.compile(r"^(\*\*Status:\*\*\s*`?)(DRAFT|SIGNED)(`?)")


def _scan_journals(project=None):
    ip_dir = _ip_dir()
    if not os.path.isdir(ip_dir):
        return []
    out = []
    for fn in sorted(os.listdir(ip_dir)):
        if not fn.endswith(".md") or fn == "JOURNAL.md":
            continue
        slug = fn.split("_IP_")[0] if "_IP_" in fn else fn[:-3]
        if project and slug != project:
            continue
        if slug.startswith("_") or "selftest" in slug.lower():
            continue
        path = os.path.join(ip_dir, fn)
        out.append((slug, path))
    return out


def _parse_claims(path):
    """Yield {claim_id, title, status, line_no} per claim in the file."""
    lines = open(path, errors="ignore").readlines()
    claims = []
    cur = None
    for i, ln in enumerate(lines):
        m = CLAIM_HDR_RE.match(ln)
        if m:
            cur = dict()
            cur["claim_id"] = m.group("cid")
            cur["title"] = ln.strip()
            cur["header_line"] = i
            cur["status"] = "?"
            cur["status_line"] = None
            claims.append(cur)
            continue
        if cur is not None:
            ms = STATUS_LINE_RE.match(ln)
            if ms:
                cur["status"] = ms.group(2)
                cur["status_line"] = i
    return lines, claims


def _sign_one_in_file(path, claim_id):
    lines, claims = _parse_claims(path)
    target = None
    for c in claims:
        if c["claim_id"] == claim_id:
            target = c
            break
    if target is None:
        return False, "claim not found in " + path
    if target["status"] == "SIGNED":
        return False, "already SIGNED"
    if target["status_line"] is None:
        return False, "no Status line"
    ln = lines[target["status_line"]]
    new = STATUS_LINE_RE.sub(r"\1SIGNED\3", ln, count=1)
    lines[target["status_line"]] = new
    # Insert a "Signed UTC" line right after the Status line.
    sig_line = "- Principal signature UTC: " + _utc() + " - " + PRINCIPAL + "\n"
    lines.insert(target["status_line"] + 1, sig_line)
    open(path, "w").write("".join(lines))
    return True, target["title"]


def _append_master(claim_id, title, project, path):
    mp = _master_path()
    if not os.path.exists(mp) or os.path.getsize(mp) == 0:
        hdr = "# IP Master Index - BRAD Engine\n\n"
        hdr += "**PROVENANCE-TRACKED - " + PRINCIPAL + "**\n\n"
        hdr += "| Claim ID | Title | Project | Signed UTC |\n"
        hdr += "|---|---|---|---|\n"
        open(mp, "w").write(hdr)
    short_title = title.split("`", 2)[-1].lstrip("`").strip(" -") if "`" in title else title
    row = "| `" + claim_id + "` | " + short_title[:60] + " | `" + project + "` | " + _utc() + " |\n"
    with open(mp, "a") as f:
        f.write(row)


def list_draft(project=None):
    found = []
    for slug, path in _scan_journals(project):
        _, claims = _parse_claims(path)
        for c in claims:
            if c["status"] == "DRAFT":
                found.append((slug, c["claim_id"], c["title"]))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--sign", default=None, help="claim ID to sign")
    ap.add_argument("--sign-all", action="store_true")
    ap.add_argument("--project", default=None)
    args = ap.parse_args()

    if args.list:
        rows = list_draft(args.project)
        print("DRAFT IP rows: " + str(len(rows)))
        for slug, cid, title in rows:
            print("  [" + slug + "] " + cid + "  " + title[:60])
        return

    if args.sign_all:
        rows = list_draft(args.project)
        if not rows:
            print("no DRAFT rows to sign")
            return
        signed = 0
        for slug, cid, _ in rows:
            for s2, path in _scan_journals(args.project):
                if s2 != slug:
                    continue
                ok, msg = _sign_one_in_file(path, cid)
                if ok:
                    _append_master(cid, msg, slug, path)
                    print("SIGNED " + slug + "/" + cid)
                    signed += 1
                else:
                    print("SKIP " + slug + "/" + cid + ": " + msg)
        print("\nTotal signed: " + str(signed))
        return

    if args.sign:
        for slug, path in _scan_journals(args.project):
            ok, msg = _sign_one_in_file(path, args.sign)
            if ok:
                _append_master(args.sign, msg, slug, path)
                print("SIGNED " + slug + "/" + args.sign)
                return
        print("claim not found: " + args.sign)
        sys.exit(1)

    ap.print_help()


if __name__ == "__main__":
    main()
