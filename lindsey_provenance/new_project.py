#!/usr/bin/env python3
"""brad_new_project - scaffold a new lindsey-provenance project.

Provenance-tracked build (lindsey-provenance framework).

Rev 1.1 changes:
    * Restored --from-intake argparse argument.
    * Allow re-scaffolding when only INTAKE.md is present in the slug dir.
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


SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{2,31}$")


class NewProjectError(Exception):
    pass


def _operator_root():
    # lindsey_provenance: discover project root via .lindsey_provenance/ marker (or cwd fallback)
    from lindsey_provenance import _root as _br
    return _br.operator_root()


def _project_root(slug):
    return os.path.join(_operator_root(), "projects", slug)


def _ledger_path():
    return os.path.join(_operator_root(), "proof_state_ledger", "LEDGER.jsonl")


def _registry_path():
    return os.path.join(_operator_root(), "projects", "REGISTRY.md")


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _scaffold_dirs(slug):
    root = _project_root(slug)
    for sub in ("proto", "artifacts", "artifacts/production", "docs", "phases", "notebooks"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    return root


def _write_project_manifest(slug, name, codename, root):
    manifest = dict()
    manifest["slug"] = slug
    manifest["project_name"] = name
    manifest["project_codename"] = codename or ""
    manifest["principal"] = PRINCIPAL
    manifest["institution"] = INSTITUTION
    manifest["ip_classification"] = "internal"
    manifest["created_utc"] = _utc()
    inh = dict()
    inh["brad_engine"] = REPLICATOR_BASELINE
    inh["brad_engine_sha256"] = REPLICATOR_SHA256
    inh["additional_projects"] = []
    manifest["inherits_from"] = inh
    manifest["replicator_baseline_sha256"] = REPLICATOR_SHA256
    manifest["phases_planned"] = 4
    ps = dict()
    ps["phase_1"] = "idea"
    ps["phase_2"] = "idea"
    ps["phase_3"] = "idea"
    ps["phase_4"] = "idea"
    manifest["phase_status"] = ps
    manifest["secret_ip"] = False
    p = os.path.join(root, "PROJECT_MANIFEST.json")
    open(p, "w").write(json.dumps(manifest, indent=2, sort_keys=True))
    return p


def _copy_intake(slug, root, src):
    dst = os.path.join(root, "INTAKE.md")
    if src and os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
        open(dst, "w").write(open(src).read())
    elif not os.path.exists(dst):
        stub = "# Project Intake - " + slug + "\n\n"
        stub += "PROVENANCE-TRACKED - " + PRINCIPAL + (" - " + INSTITUTION if INSTITUTION else "") + "\n\n"
        stub += "Populate from operator/templates/PROJECT_INTAKE_TEMPLATE.md\n\n"
        stub += "Inherits: " + REPLICATOR_BASELINE + " = " + REPLICATOR_SHA256 + "\n"
        open(dst, "w").write(stub)
    return dst


def _write_proto_init(slug, root):
    p = os.path.join(root, "proto", "__init__.py")
    body = '"""' + slug + ' - operator-authored modules under BRAD.\n\n'
    body += 'Provenance-tracked build (lindsey_provenance).\n'
    body += '(lindsey-provenance framework)\n\n'
    body += 'Inherits ace.phase4.freeze-1 = ' + REPLICATOR_SHA256 + '\n'
    body += '"""\n'
    body += '__slug__ = "' + slug + '"\n'
    body += '__principal__ = "' + PRINCIPAL + '"\n'
    body += '__institution__ = "' + INSTITUTION + '"\n'
    body += '__replicator_baseline_sha256__ = "' + REPLICATOR_SHA256 + '"\n'
    open(p, "w").write(body)
    return p


def _append_registry(slug, name, codename):
    p = _registry_path()
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        header = "# Project Registry\n\n"
        header += "**PROVENANCE-TRACKED - " + PRINCIPAL + (" - " + INSTITUTION if INSTITUTION else "") + "**\n"
        header += "**Replicator:** `" + REPLICATOR_BASELINE + "` = `" + REPLICATOR_SHA256 + "`\n\n"
        header += "| Slug | Project name | Codename | Status | Created UTC |\n"
        header += "|---|---|---|---|---|\n"
        open(p, "w").write(header)
    row = "| `" + slug + "` | " + name + " | " + (codename or "") + " | spawned | " + _utc() + " |\n"
    with open(p, "a") as f:
        f.write(row)
    return p


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _append_ledger(slug):
    p = _ledger_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p):
        open(p, "w").close()
    pm_path = os.path.join(_project_root(slug), "PROJECT_MANIFEST.json")
    row = dict()
    row["ts"] = _utc()
    row["project"] = slug
    row["artifact"] = "PROJECT_MANIFEST.json"
    row["from_state"] = None
    row["to_state"] = "idea"
    row["operator"] = "brad_new_project"
    row["evidence_sha256"] = _sha256_file(pm_path)
    with open(p, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return p


def spawn(slug, name=None, codename=None, from_intake=None):
    if not SLUG_RE.match(slug):
        raise NewProjectError("invalid slug")
    root = _project_root(slug)
    if os.path.isdir(root):
        contents = set(os.listdir(root))
        allowed = {"INTAKE.md"}
        unexpected = contents - allowed
        if unexpected:
            raise NewProjectError("project dir not empty: " + slug + " contains " + ",".join(sorted(unexpected)))
    name = name or slug.replace("-", " ").title()
    _scaffold_dirs(slug)
    intake = _copy_intake(slug, root, from_intake)
    manifest = _write_project_manifest(slug, name, codename, root)
    proto_init = _write_proto_init(slug, root)
    registry = _append_registry(slug, name, codename)
    ledger = _append_ledger(slug)
    out = dict()
    out["slug"] = slug
    out["root"] = root
    out["intake"] = intake
    out["manifest"] = manifest
    out["proto_init"] = proto_init
    out["registry"] = registry
    out["ledger"] = ledger
    out["replicator_sha256"] = REPLICATOR_SHA256
    return out


def _selftest():
    print("brad_new_project - self-test (rev 1.1)")
    slug = "selftest-np-" + str(int(time.time()))
    try:
        out = spawn(slug, name="Operator Self-Test", codename="OP-ST")
    except Exception as e:
        print("  FAIL: " + repr(e))
        return 1
    functional_pass = True
    for k, v in out.items():
        if isinstance(v, str) and ("/" in v or "\\" in v):
            ok = os.path.exists(v)
            if not ok:
                functional_pass = False
            mark = "PASS" if ok else "FAIL"
            print("  " + k.ljust(18) + ": " + mark)
    cleanup_ok = True
    try:
        import shutil
        shutil.rmtree(out["root"])
        with open(out["registry"]) as f:
            lines = f.readlines()
        with open(out["registry"], "w") as f:
            for ln in lines:
                if "`" + slug + "`" not in ln:
                    f.write(ln)
        with open(out["ledger"]) as f:
            lines = f.readlines()
        with open(out["ledger"], "w") as f:
            for ln in lines:
                if '"project": "' + slug + '"' not in ln:
                    f.write(ln)
    except Exception:
        cleanup_ok = False
    print("  cleanup            : " + ("PASS" if cleanup_ok else "BEST-EFFORT"))
    verdict = "PASS" if functional_pass else "FAIL"
    print("---")
    print("  brad_new_project: " + verdict)
    return 0 if functional_pass else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug")
    ap.add_argument("--name", default=None)
    ap.add_argument("--codename", default=None)
    ap.add_argument("--from-intake", dest="from_intake", default=None, help="path to a pre-filled INTAKE.md (rev 1.1)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(_selftest())
    if not args.slug:
        ap.error("--slug required (or use --selftest)")
    out = spawn(args.slug, args.name, args.codename, args.from_intake)
    print("[brad_new_project: PASS - slug=" + args.slug + "]")
    print("  root             : " + out["root"])


if __name__ == "__main__":
    main()
