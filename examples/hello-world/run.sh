#!/usr/bin/env bash
# hello-world — exercises the lindsey-provenance CLI end-to-end in under a minute.
# Run from anywhere after `pip install -e .` at the repo root.
set -euo pipefail

WORK="$(mktemp -d)"
cd "$WORK"
echo ">>> 1. init a project root"
lindsey-provenance init demo-root
cd demo-root

echo ">>> 2. scaffold a project"
lindsey-provenance new-project --slug hello-world

echo ">>> 3. seal phase 1 (SHA-256 manifest, inheritance chain)"
lindsey-provenance freeze --project hello-world --phase 1

echo ">>> 4. run the audit gates"
lindsey-provenance audit --project hello-world

echo ">>> 5. cross-project status"
lindsey-provenance status

echo ""
echo "OK — full provenance round-trip passed. Workspace: $WORK"
