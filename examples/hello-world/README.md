# hello-world

A one-minute, end-to-end tour of the `lindsey-provenance` CLI.

## Run it

From the repo root, after installing the package:

```bash
pip install -e .
bash examples/hello-world/run.sh
```

## What it does

1. `init` — scaffolds a project root (`.lindsey_provenance/config.json`, the operator layout).
2. `new-project --slug hello-world` — writes a `PROJECT_MANIFEST.json` that inherits the sealed baseline.
3. `freeze --project hello-world --phase 1` — seals a phase with a SHA-256 manifest tied to the inheritance chain.
4. `audit --project hello-world` — runs the gates (sealed-core, inheritance, ledger). Expect `ALL=PASS`.
5. `status` — prints the cross-project snapshot.

Every command is real and runs against a freshly scaffolded project in a temp directory, so it leaves your repo untouched.
