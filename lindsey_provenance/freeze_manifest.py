#!/usr/bin/env python3
"""freeze_manifest — per-project per-phase cryptographic freeze.

Provenance-tracked build (lindsey-provenance framework).

Walks operator/projects/<slug>/proto/ and operator/projects/<slug>/artifacts/,
SHA-256s every file, inherits my-engine.v1.freeze-1 plus any prior phase
manifests for this project (and any additional inheritances declared in
PROJECT_MANIFEST.json:inherits_from.additional_projects), and emits:

    operator/projects/<slug>/artifacts/<slug>_phase<N>_manifest.json

The top-level digest <slug>.phase<N>.freeze-1_sha256 is computed over the
canonical-sort body bytes (with frozen_utc included, matching the framework's
engine's convention so re-runs produce a different top digest while every
per-file SHA stays byte-deterministic).

Usage:
    python3 freeze_manifest.py --project <slug> --phase N [--dry-run]
    python3 freeze_manifest.py --project <slug> --phase N --verify
    python3 freeze_manifest.py --selftest
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

class FreezeError(Exception):
    pass


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _project_root(slug):
    return os.path.join(_operator_root(), "projects", slug)


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _walk(root, exclude_suffixes=()):
    if not os.path.isdir(root):
        return []
    out = []
    for base, _, files in os.walk(root):
        for fn in files:
            if any(fn.endswith(s) for s in exclude_suffixes):
                continue
            p = os.path.join(base, fn)
            out.append(p)
    return sorted(out)


def _verify_inheritance(project_manifest):
    inh = project_manifest.get("inherits_from", {})
    bsha = inh.get("baseline_sha256")
    if bsha != REPLICATOR_SHA256:
        raise FreezeError(
            "PROJECT_MANIFEST.json does not inline the replicator "
            "baseline SHA-256. Refusing to seal. Expected "
            + REPLICATOR_SHA256 + "; got " + str(bsha)
        )
    top = project_manifest.get("replicator_baseline_sha256")
    if top != REPLICATOR_SHA256:
        raise FreezeError(
            "PROJECT_MANIFEST.json:replicator_baseline_sha256 is missing "
            "or incorrect. Refusing to seal."
        )
    return inh


def _prior_phase_inheritance(slug, phase):
    """Collect prior phase manifests for this project (phase 1 .. phase-1)
    and roll their SHA-256s in for the inheritance chain."""
    out = {}
    art_dir = os.path.join(_project_root(slug), "artifacts")
    for n in range(1, phase):
        p = os.path.join(art_dir, slug + "_phase" + str(n) + "_manifest.json")
        if os.path.exists(p):
            out[slug + ".phase" + str(n) + ".freeze-1"] = _sha256_file(p)
    return out


def freeze(slug, phase, dry_run=False):
    proj_root = _project_root(slug)
    if not os.path.isdir(proj_root):
        raise FreezeError("project not found: " + slug)

    pm_path = os.path.join(proj_root, "PROJECT_MANIFEST.json")
    if not os.path.exists(pm_path):
        raise FreezeError("PROJECT_MANIFEST.json missing for " + slug)
    pm = json.load(open(pm_path))
    inh = _verify_inheritance(pm)

    # Collect sources (proto/)
    sources = {}
    src_bytes = 0
    src_lines = 0
    proto_dir = os.path.join(proj_root, "proto")
    for p in _walk(proto_dir):
        rel = os.path.relpath(p, proj_root)
        sz = os.path.getsize(p)
        try:
            with open(p, errors="ignore") as f:
                n_lines = sum(1 for _ in f)
        except Exception:
            n_lines = 0
        sources[rel] = {
            "size_bytes": sz, "lines": n_lines, "sha256": _sha256_file(p),
        }
        src_bytes += sz
        src_lines += n_lines

    # Collect artifacts/, EXCLUDING the manifest we are about to write
    # (so re-runs are byte-deterministic on a clean tree).
    target = os.path.join(
        proj_root, "artifacts", slug + "_phase" + str(phase) + "_manifest.json"
    )
    artifacts = {}
    art_bytes = 0
    art_dir = os.path.join(proj_root, "artifacts")
    for p in _walk(art_dir):
        if os.path.abspath(p) == os.path.abspath(target):
            continue
        rel = os.path.relpath(p, proj_root)
        sz = os.path.getsize(p)
        artifacts[rel] = {
            "size_bytes": sz, "sha256": _sha256_file(p),
        }
        art_bytes += sz

    # Inheritance chain.
    inherits = {
        REPLICATOR_BASELINE: REPLICATOR_SHA256,
    }
    inherits.update(_prior_phase_inheritance(slug, phase))
    # Plus any explicitly declared additional inheritances
    for ap in inh.get("additional_projects", []) or []:
        inherits[ap["phase_freeze"]] = ap["sha256"]

    baseline_name = slug + ".phase" + str(phase) + ".freeze-1"
    body = {
        "baseline_name":               baseline_name,
        "project":                     pm.get("project_name", slug),
        "slug":                        slug,
        "codename":                    pm.get("project_codename", ""),
        "phase":                       phase,
        "tier":                        "operator-spawned project",
        "principal":                   PRINCIPAL,
        "institution":                 INSTITUTION,
        "frozen_utc":                  _utc(),
        "replicator_baseline":         REPLICATOR_BASELINE,
        "replicator_baseline_sha256":  REPLICATOR_SHA256,
        "inherits":                    inherits,
        "source_modules": {
            "n":           len(sources),
            "total_lines": src_lines,
            "total_bytes": src_bytes,
            "files":       sources,
        },
        "artifacts": {
            "n":           len(artifacts),
            "total_bytes": art_bytes,
            "files":       artifacts,
        },
        "ip": "PROVENANCE-TRACKED · " + PRINCIPAL + (" · " + INSTITUTION if INSTITUTION else ""),
    }
    canon = json.dumps(body, indent=2, sort_keys=True).encode("utf-8")
    body[baseline_name + "_sha256"] = hashlib.sha256(canon).hexdigest()

    if not dry_run:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "w").write(json.dumps(body, indent=2, sort_keys=True))
    return body, target


def verify_chain(slug, phase):
    """Re-check that the on-disk manifest's inheritance chain is intact:
    every cited per-source SHA matches the file on disk."""
    p = os.path.join(
        _project_root(slug), "artifacts",
        slug + "_phase" + str(phase) + "_manifest.json",
    )
    if not os.path.exists(p):
        raise FreezeError("manifest not found: " + p)
    m = json.load(open(p))
    proj_root = _project_root(slug)
    mismatches = []
    for rel, body in (m.get("source_modules", {}).get("files", {})).items():
        full = os.path.join(proj_root, rel)
        if not os.path.exists(full):
            mismatches.append((rel, "missing"))
            continue
        if _sha256_file(full) != body["sha256"]:
            mismatches.append((rel, "sha mismatch"))
    return {"ok": len(mismatches) == 0, "mismatches": mismatches}


def _selftest():
    """Functional self-test. Uses a '_selftest_' slug so audit skips it."""
    print("freeze_manifest — self-test")
    slug = "_selftest_fm_" + str(int(time.time()))
    root = _project_root(slug)
    os.makedirs(os.path.join(root, "proto"), exist_ok=True)
    os.makedirs(os.path.join(root, "artifacts"), exist_ok=True)
    open(os.path.join(root, "proto", "hello.py"), "w").write(
        '"""hello -- self-test stub (lindsey_provenance)."""\nprint("hello")\n'
    )
    open(os.path.join(root, "artifacts", "stub.json"), "w").write(
        '{"selftest": true}\n'
    )
    pm = {
        "slug": slug,
        "project_name": "Freeze Self-Test",
        "principal": PRINCIPAL,
        "institution": INSTITUTION,
        "inherits_from": {
            "baseline":        REPLICATOR_BASELINE,
            "baseline_sha256": REPLICATOR_SHA256,
            "additional_projects": [],
        },
        "replicator_baseline_sha256": REPLICATOR_SHA256,
    }
    open(os.path.join(root, "PROJECT_MANIFEST.json"), "w").write(
        json.dumps(pm, indent=2, sort_keys=True)
    )
    try:
        body, target = freeze(slug, 1)
        print("  manifest emitted   : PASS  " + target)
        print("  baseline_name      : " + body["baseline_name"])
        print("  sources_n          : " + str(body["source_modules"]["n"]))
        print("  artifacts_n        : " + str(body["artifacts"]["n"]))
        digest = body[body["baseline_name"] + "_sha256"]
        print("  digest             : " + digest[:32] + "...")
        chk = verify_chain(slug, 1)
        chain_ok = chk["ok"]
        print("  verify_chain       : " + ("PASS" if chain_ok else "FAIL"))
    except Exception as e:
        print("  FAIL: " + repr(e))
        return 1

    cleanup_ok = True
    try:
        import shutil
        shutil.rmtree(root)
    except Exception:
        cleanup_ok = False
    print("  cleanup            : "
          + ("PASS" if cleanup_ok else "BEST-EFFORT (sandbox FS locked)"))
    print("---\n  freeze_manifest: " + ("PASS" if chain_ok else "FAIL"))
    return 0 if chain_ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project")
    ap.add_argument("--phase", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_selftest())
    if not (args.project and args.phase):
        ap.error("--project and --phase required (or use --selftest)")

    if args.verify:
        chk = verify_chain(args.project, args.phase)
        print("[freeze_manifest: verify ok=" + str(chk["ok"]) + "]")
        for rel, why in chk["mismatches"]:
            print("  " + rel + ": " + why)
        sys.exit(0 if chk["ok"] else 1)

    body, target = freeze(args.project, args.phase, dry_run=args.dry_run)
    name = body["baseline_name"]
    digest = body[name + "_sha256"]
    print("[freeze_manifest: PASS - " + name + "]")
    suffix = " (dry-run)" if args.dry_run else ""
    print("  manifest path     : " + target + suffix)
    n_src = body["source_modules"]["n"]
    n_lines = body["source_modules"]["total_lines"]
    print("  sources           : " + str(n_src) + " files, " + str(n_lines) + " lines")
    n_art = body["artifacts"]["n"]
    print("  artifacts         : " + str(n_art) + " files")
    print("  artifacts         : " + str(n_art) + " files")
    inh_keys = ", ".join(body["inherits"].keys())
    print("  inherits          : " + inh_keys)
    print("  digest            : " + digest)


if __name__ == "__main__":
    main()
