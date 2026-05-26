"""lindsey_provenance.cli -- unified CLI dispatcher.

Usage:
    lindsey-provenance <command> [args...]

Commands (run `lindsey-provenance <cmd> --help` for details):

    init <project-name>     Scaffold a new lindsey-provenance project root in cwd
    new-project <slug>      Scaffold a project under operator/projects/
    proof-state ...         Transition artifacts through the 6-state ledger
    freeze ...              Per-phase SHA-256 manifest seal
    audit ...               5-gate audit run
    ip-extract ...          Surface IP-CLAIM markers to draft journal
    sign-ip ...             Flip DRAFT IP rows to SIGNED
    status                  Cross-project snapshot
    purge-selftest          Clean self-test residue
    assimilate <brief>      7-phase multi-modal brief intake
    run-phase ...           Execute a phase end-to-end
"""

import json
import os
import sys


COMMANDS = {
    "new-project":     "lindsey_provenance.new_project",
    "proof-state":     "lindsey_provenance.proof_state",
    "freeze":          "lindsey_provenance.freeze_manifest",
    "audit":           "lindsey_provenance.audit",
    "ip-extract":      "lindsey_provenance.ip_extract",
    "sign-ip":         "lindsey_provenance.sign_ip",
    "status":          "lindsey_provenance.status",
    "purge-selftest":  "lindsey_provenance.purge_selftest",
    "assimilate":      "lindsey_provenance.assimilate_brief",
    "run-phase":       "lindsey_provenance.run_phase",
}


def scaffold_project_root(name):
    """`lindsey-provenance init <name>`: create a new project root with the standard layout."""
    root = os.path.abspath(name)
    if os.path.exists(root):
        print("ERROR: directory already exists: " + root, file=sys.stderr)
        return 2
    subdirs = [
        ".lindsey_provenance",
        "operator/projects",
        "operator/briefs",
        "operator/proof_state_ledger",
        "operator/ip_journal",
        "operator/sealed_core_audit",
        "operator/templates",
        "core",
        "docs/internal_record",
    ]
    for sub in subdirs:
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    # Default config
    cfg = {
        "replicator_baseline": "my-engine.v1.freeze-1",
        "replicator_sha256": "0" * 64,
        "principal": os.environ.get("USER", "Operator"),
        "institution": "",
    }
    with open(os.path.join(root, ".lindsey_provenance", "config.json"), "w") as fh:
        json.dump(cfg, fh, indent=2)
    # Seed empty registry, ledger, journal index files
    with open(os.path.join(root, "operator", "projects", "REGISTRY.md"), "w") as fh:
        fh.write("# Project Registry\n\n| slug | phase_status | replicator_baseline |\n|---|---|---|\n")
    with open(os.path.join(root, "operator", "proof_state_ledger", "LEDGER.jsonl"), "w") as fh:
        fh.write("")
    with open(os.path.join(root, "operator", "ip_journal", "JOURNAL.md"), "w") as fh:
        fh.write("# IP Journal Index\n\n")
    with open(os.path.join(root, "operator", "briefs", "BRIEF_LOG.md"), "w") as fh:
        fh.write("# Brief Log\n\n| filename | format | words | sha-256 | received_utc | triage | verdict |\n|---|---|---:|---|---|---|---|\n")
    # README skeleton
    with open(os.path.join(root, "README.md"), "w") as fh:
        fh.write("# " + os.path.basename(root) + "\n\n")
        fh.write("lindsey-provenance project root. Configure `.lindsey_provenance/config.json` with your baseline + identity, then:\n\n")
        fh.write("```\nlindsey-provenance status\nlindsey-provenance new-project my-first-project\n```\n")
    print("Initialized lindsey-provenance project root at: " + root)
    print("Next step: edit " + os.path.join(root, ".lindsey_provenance/config.json"))
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]  # shift args for subcommand
    if cmd == "init":
        if not sys.argv[1:]:
            print("ERROR: usage: lindsey-provenance init <project-name>", file=sys.stderr)
            return 2
        return scaffold_project_root(sys.argv[1])
    if cmd not in COMMANDS:
        print("ERROR: unknown command: " + cmd, file=sys.stderr)
        print("Available: init, " + ", ".join(COMMANDS.keys()), file=sys.stderr)
        return 2
    module_name = COMMANDS[cmd]
    mod = __import__(module_name, fromlist=["main"])
    if not hasattr(mod, "main"):
        print("ERROR: " + module_name + " has no main()", file=sys.stderr)
        return 2
    rv = mod.main()
    if isinstance(rv, dict):
        return 0 if rv.get("status") == "PASS" else 1
    if isinstance(rv, int):
        return rv
    return 0


if __name__ == "__main__":
    sys.exit(main())
