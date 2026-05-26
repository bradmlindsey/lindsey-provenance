"""lindsey_provenance.config -- runtime configuration for the lindsey-provenance framework.

Reads from .lindsey_provenance/config.json in the project root (or any ancestor),
falling back to environment variables, then to neutral defaults.

The four configurable identity fields are:

    REPLICATOR_BASELINE       e.g. "my-engine.v1.freeze-1"
    REPLICATOR_SHA256         the SHA-256 of your sealed baseline
    PRINCIPAL                 your name (used in manifests / headers)
    INSTITUTION               your org name (optional; can be empty)

Override priority (highest first):
    1. .lindsey_provenance/config.json
    2. LINDSEY_PROVENANCE_REPLICATOR_BASELINE / LINDSEY_PROVENANCE_REPLICATOR_SHA256 /
       LINDSEY_PROVENANCE_PRINCIPAL / LINDSEY_PROVENANCE_INSTITUTION env vars
    3. Defaults below.
"""

import json
import os


# ---- DEFAULTS ---------------------------------------------------------------
# Placeholder SHA = all-zeros. Tools warn if they see this and the user hasn't
# overridden it -- it means the user has not yet sealed a baseline.

DEFAULTS = {
    "replicator_baseline": "my-engine.v1.freeze-1",
    "replicator_sha256": "0" * 64,
    "principal": "Operator",
    "institution": "",
}


def _find_config_file(start_dir=None):
    if start_dir is None:
        start_dir = os.getcwd()
    cur = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(cur, ".lindsey_provenance", "config.json")
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def load(start_dir=None):
    """Return a dict with the four identity fields populated."""
    cfg = dict(DEFAULTS)
    path = _find_config_file(start_dir)
    if path is not None:
        try:
            with open(path) as fh:
                file_cfg = json.load(fh)
            for k in ("replicator_baseline", "replicator_sha256",
                      "principal", "institution"):
                if k in file_cfg and file_cfg[k] is not None:
                    cfg[k] = file_cfg[k]
        except (OSError, json.JSONDecodeError):
            pass
    # env-var overrides
    env_map = {
        "LINDSEY_PROVENANCE_REPLICATOR_BASELINE": "replicator_baseline",
        "LINDSEY_PROVENANCE_REPLICATOR_SHA256":   "replicator_sha256",
        "LINDSEY_PROVENANCE_PRINCIPAL":           "principal",
        "LINDSEY_PROVENANCE_INSTITUTION":         "institution",
    }
    for env_key, cfg_key in env_map.items():
        if env_key in os.environ:
            cfg[cfg_key] = os.environ[env_key]
    return cfg


def project_root(start_dir=None):
    """Find the directory containing .lindsey_provenance/config.json (or cwd if none)."""
    if start_dir is None:
        start_dir = os.getcwd()
    path = _find_config_file(start_dir)
    if path is None:
        return os.path.abspath(start_dir)
    return os.path.dirname(os.path.dirname(path))


# Module-level constants for easy `from lindsey_provenance.config import PRINCIPAL` use.
_CFG = load()
REPLICATOR_BASELINE = _CFG["replicator_baseline"]
REPLICATOR_SHA256 = _CFG["replicator_sha256"]
PRINCIPAL = _CFG["principal"]
INSTITUTION = _CFG["institution"]


def is_unconfigured():
    """True if the baseline SHA looks like the all-zeros placeholder."""
    return REPLICATOR_SHA256 == "0" * 64
