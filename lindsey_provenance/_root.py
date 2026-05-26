"""lindsey_provenance._root -- locate project root + standard subdirectories.

lindsey-provenance projects use this layout (under your repo root):

    <project_root>/
    +-- .lindsey_provenance/config.json        # identity (replicator baseline, principal)
    +-- operator/
    |   +-- projects/<slug>/          # each project's intake, proto, artifacts
    |   |   +-- INTAKE.md
    |   |   +-- PROJECT_MANIFEST.json
    |   |   +-- phases/PHASE_<N>.md
    |   |   +-- proto/<modules>.py
    |   |   +-- artifacts/...
    |   |   +-- docs/...
    |   |   +-- notebooks/...
    |   +-- briefs/                   # archived client briefs + BRIEF_LOG.md
    |   +-- proof_state_ledger/       # append-only LEDGER.jsonl
    |   +-- ip_journal/               # per-project IP journals + JOURNAL.md
    |   +-- sealed_core_audit/        # daily audit reports + ALERTS.log
    |   +-- templates/                # lindsey_provenance templates
    +-- core/                         # YOUR sealed engine modules (optional)
    +-- docs/                         # YOUR documentation suite

The .lindsey_provenance/config.json anchors the root. If absent, the current working
directory is used.
"""

import os


def project_root(start_dir=None):
    """Walk upward from start_dir looking for .lindsey_provenance/. Falls back to cwd."""
    if start_dir is None:
        start_dir = os.getcwd()
    cur = os.path.abspath(start_dir)
    while True:
        if os.path.isdir(os.path.join(cur, ".lindsey_provenance")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.abspath(start_dir)
        cur = parent


def operator_root(start_dir=None):
    return os.path.join(project_root(start_dir), "operator")


def projects_root(start_dir=None):
    return os.path.join(operator_root(start_dir), "projects")


def briefs_root(start_dir=None):
    return os.path.join(operator_root(start_dir), "briefs")


def ledger_path(start_dir=None):
    return os.path.join(operator_root(start_dir), "proof_state_ledger", "LEDGER.jsonl")


def ip_journal_root(start_dir=None):
    return os.path.join(operator_root(start_dir), "ip_journal")


def audit_root(start_dir=None):
    return os.path.join(operator_root(start_dir), "sealed_core_audit")


def templates_root(start_dir=None):
    return os.path.join(operator_root(start_dir), "templates")
