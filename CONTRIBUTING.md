# Contributing

Thanks for looking at `lindsey-provenance`. A few norms keep this project honest.

## Dev setup

```bash
git clone https://github.com/bradmlindsey/lindsey-provenance
cd lindsey-provenance
pip install -e .
bash examples/hello-world/run.sh   # sanity check
```

## Standard library only

The package depends on the Python standard library and nothing else. Please do
not add third-party runtime dependencies. If a feature seems to need one, open
an issue first — the closed-form re-route practice exists precisely to avoid
dependency creep.

## Claims must match evidence

This is a provenance tool; it should hold itself to its own rule: **a claim may
advance only as far as its evidence.** For a pull request:

- Don't describe something as validated, tested, or working unless the PR shows
  how to reproduce that.
- Keep proof-state language accurate (`idea → planned → implemented → simulated
  → artifact-generated → physically-validated`).
- Run the round-trip (`examples/hello-world/run.sh`) and the package self-tests
  before submitting; note the result in the PR.

## Scope

Bug fixes, docs, tests, and small focused features are welcome. For larger
changes, open an issue to discuss direction first.
