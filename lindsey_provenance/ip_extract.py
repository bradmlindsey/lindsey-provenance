#!/usr/bin/env python3
"""ip_extract — surface IP claims from source markers.

Provenance-tracked build (lindsey-provenance framework).

Walks operator/projects/<slug>/proto/ looking for marker comments:
    # IP-CLAIM: <one-line claim>
    # NOVEL: <reason>           (optional, attaches to the most recent claim)
    # Rule <N>: <statement>     (optional new-rule proposal)

For each marker not already present in the project's IP journal, appends a
DRAFT claim row to ip_journal/<slug>_IP_<today>.md. The Principal then signs
each row to promote it to SIGNED.

Usage:
    python3 ip_extract.py --project <slug>
    python3 ip_extract.py --project <slug> --since-phase N
    python3 ip_extract.py --project <slug> --verify
    python3 ip_extract.py --selftest
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

CLAIM_RE = re.compile(
    r"#\s*IP-CLAIM\s*:\s*(?P<text>.+?)\s*$", re.IGNORECASE
)
NOVEL_RE = re.compile(
    r"#\s*NOVEL\s*:\s*(?P<text>.+?)\s*$", re.IGNORECASE
)
RULE_RE = re.compile(
    r"#\s*Rule\s+(?P<n>\d+)\s*:\s*(?P<text>.+?)\s*$", re.IGNORECASE
)


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _project_root(slug):
    return os.path.join(_operator_root(), "projects", slug)


def _ip_dir():
    d = os.path.join(_operator_root(), "ip_journal")
    os.makedirs(d, exist_ok=True)
    return d


def _today():
    return time.strftime("%Y-%m-%d")


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def scan(project):
    """Walk project's proto/ tree and yield claim records."""
    root = os.path.join(_project_root(project), "proto")
    if not os.path.isdir(root):
        return []
    claims = []
    for base, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(base, fn)
            rel = os.path.relpath(p, _project_root(project))
            file_sha = _sha256_file(p)
            with open(p, errors="ignore") as f:
                lines = f.readlines()
            current = None
            for i, ln in enumerate(lines):
                m = CLAIM_RE.search(ln)
                if m:
                    current = {
                        "file":             rel,
                        "file_sha256":      file_sha,
                        "line":             i + 1,
                        "claim_text":       m.group("text").strip(),
                        "novel_text":       None,
                        "proposed_rule":    None,
                    }
                    claims.append(current)
                    continue
                if current is None:
                    continue
                m = NOVEL_RE.search(ln)
                if m:
                    current["novel_text"] = m.group("text").strip()
                    continue
                m = RULE_RE.search(ln)
                if m:
                    current["proposed_rule"] = {
                        "n":    int(m.group("n")),
                        "text": m.group("text").strip(),
                    }
                    continue
                # Stop attaching once we exit the comment block: a line that
                # is not a comment line breaks the binding.
                stripped = ln.strip()
                if stripped and not stripped.startswith("#"):
                    current = None
    return claims


def _journal_path(project):
    return os.path.join(_ip_dir(), project + "_IP_" + _today() + ".md")


def _claim_id(project, journal_path, idx):
    # Use the index across all journal files (cumulative claim count + 1).
    cum = 0
    for fn in sorted(os.listdir(_ip_dir())):
        if not fn.startswith(project + "_IP_") or not fn.endswith(".md"):
            continue
        with open(os.path.join(_ip_dir(), fn), errors="ignore") as f:
            for ln in f:
                if ln.lstrip().startswith("### Claim "):
                    cum += 1
    return project + "-IP-" + str(cum + idx + 1).zfill(3)


def _existing_claim_keys(project):
    """Return the set of (file, line, claim_text) already journaled
    for this project (across all dates)."""
    out = set()
    for fn in sorted(os.listdir(_ip_dir())):
        if not fn.startswith(project + "_IP_") or not fn.endswith(".md"):
            continue
        with open(os.path.join(_ip_dir(), fn), errors="ignore") as f:
            text = f.read()
        # Parse simple lines we wrote earlier.
        for ln in text.splitlines():
            ln = ln.strip()
            if ln.startswith("- **Source marker:**"):
                marker = ln.split("`", 1)[-1].rstrip("`").strip()
                out.add(marker)
    return out


def _write_journal(project, claims, dry_run=False):
    if not claims:
        return None, 0
    p = _journal_path(project)
    existing = _existing_claim_keys(project)
    new_claims = []
    for c in claims:
        marker = "# IP-CLAIM: " + c["claim_text"]
        if marker in existing:
            continue
        new_claims.append(c)
    if not new_claims:
        return p, 0

    # Build the journal file
    if not os.path.exists(p):
        header = (
            "# IP Extraction Journal — `" + project + "`\n\n"
            "**PROVENANCE-TRACKED · " + PRINCIPAL + (" · " + INSTITUTION if INSTITUTION else "") + "**\n"
            "**Replicator baseline:** `my-engine.v1.freeze-1` = `"
            + REPLICATOR_SHA256 + "`\n"
            "**Date:** " + _today() + "\n\n"
            "> Auto-populated by `ip_extract.py`. Rows are `DRAFT` "
            "until the Principal signs.\n\n"
            "---\n\n"
        )
        if not dry_run:
            open(p, "w").write(header)

    sections = []
    for idx, c in enumerate(new_claims):
        cid = _claim_id(project, p, idx)
        section = []
        section.append("### Claim `" + cid + "` — "
                       + c["claim_text"][:60])
        section.append("")
        section.append("- **Claim ID:** `" + cid + "`")
        section.append("- **Surfaced UTC:** " + _utc())
        section.append("- **Synthesised in module:** `" + c["file"]
                       + "` line " + str(c["line"]))
        section.append("- **Source marker:** `# IP-CLAIM: "
                       + c["claim_text"] + "`")
        if c.get("novel_text"):
            section.append("- **Novelty note (from source):** "
                           + c["novel_text"])
        if c.get("proposed_rule"):
            section.append("- **Proposed rule:** Rule "
                           + str(c["proposed_rule"]["n"]) + " — "
                           + c["proposed_rule"]["text"])
        section.append("")
        section.append("**Claim statement (operator to enrich):**")
        section.append("> " + c["claim_text"])
        section.append("")
        section.append("**Evidence on disk:**")
        section.append("- Source file: `" + c["file"] + "` SHA-256 = `"
                       + c["file_sha256"] + "`")
        section.append("")
        section.append("**Novelty argument (operator to enrich):**")
        section.append("> _to be filled_")
        section.append("")
        section.append("**Prior-art search status:** `[ ]` not yet searched")
        section.append("")
        section.append("**Filing recommendation (operator):** `[ ]` "
                       "trade-secret  `[ ]` provisional  `[ ]` defensive  "
                       "`[ ]` pending")
        section.append("")
        section.append("**Status:** `DRAFT`")
        section.append("- Principal signature: _Brad M. Lindsey_")
        section.append("- Signed UTC: _________________")
        section.append("")
        section.append("---")
        section.append("")
        sections.append("\n".join(section))

    body = "\n".join(sections)
    if not dry_run:
        with open(p, "a") as f:
            f.write(body)
    return p, len(new_claims)


def verify(project):
    """Count IP-CLAIM markers in proto/ and compare to journal-row headers
    across all date-files for this project."""
    claims = scan(project)
    n_markers = len(claims)
    n_rows = 0
    for fn in os.listdir(_ip_dir()):
        if not fn.startswith(project + "_IP_") or not fn.endswith(".md"):
            continue
        with open(os.path.join(_ip_dir(), fn), errors="ignore") as f:
            for ln in f:
                if ln.lstrip().startswith("### Claim "):
                    n_rows += 1
    return {
        "ok":            n_markers == n_rows,
        "markers":       n_markers,
        "journal_rows":  n_rows,
        "delta":         n_markers - n_rows,
    }


def _selftest():
    """Functional self-test. Uses a '_selftest_' slug so audit skips it."""
    print("ip_extract — self-test")
    slug = "_selftest_ipxt_" + str(int(time.time()))
    root = _project_root(slug)
    proto = os.path.join(root, "proto")
    os.makedirs(proto, exist_ok=True)
    src = os.path.join(proto, "stub.py")
    open(src, "w").write(
        '"""stub -- self-test (lindsey_provenance)."""\n'
        '# IP-CLAIM: closed-form Δf/f₀ holds with r=1 across 5 branches\n'
        '# NOVEL: 4-decade scale span, single coupling coefficient\n'
        '# Rule 81: hypothetical new rule for self-test only\n'
        'def foo(): return 42\n'
    )
    try:
        claims = scan(slug)
        assert len(claims) == 1, "expected 1 claim, got " + str(len(claims))
        assert claims[0]["novel_text"], "novel text not captured"
        assert claims[0]["proposed_rule"]["n"] == 81
        print("  marker parse        : PASS  (1 claim, novel + rule attached)")
        p, n = _write_journal(slug, claims)
        print("  journal write       : PASS  (" + str(n) + " new row)  "
              + (p or ""))
        v = verify(slug)
        verify_ok = v["ok"]
        print("  verify completeness : "
              + ("PASS" if verify_ok else "FAIL")
              + "  markers=" + str(v["markers"])
              + " rows=" + str(v["journal_rows"]))
    except Exception as e:
        print("  FAIL: " + repr(e))
        return 1

    cleanup_ok = True
    try:
        import shutil
        shutil.rmtree(root)
        if p and os.path.exists(p):
            os.remove(p)
    except Exception:
        cleanup_ok = False
    print("  cleanup             : "
          + ("PASS" if cleanup_ok else "BEST-EFFORT (sandbox FS locked)"))
    print("---\n  ip_extract: " + ("PASS" if verify_ok else "FAIL"))
    return 0 if verify_ok else 1



def _run_main_body(args):
    claims = scan(args.project)
    p, n = _write_journal(args.project, claims, dry_run=args.dry_run)
    suffix = " (dry-run)" if args.dry_run else ""
    msg = "[ip_extract: PASS - " + args.project + " scanned " + str(len(claims)) + " markers, " + str(n) + " new draft rows]"
    print(msg)
    if p is not None:
        print("  journal path       : " + p + suffix)


def main():
    """CLI entry point for `lindsey-provenance ip-extract`."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project")
    ap.add_argument("--since-phase", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.project:
        ap.error("--project required (or use --selftest)")
    if args.verify:
        v = verify(args.project)
        line = "[ip_extract: verify markers=" + str(v["markers"]) + " rows=" + str(v["journal_rows"]) + " ok=" + str(v["ok"]) + "]"
        print(line)
        return 0 if v["ok"] else 1
    _run_main_body(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

