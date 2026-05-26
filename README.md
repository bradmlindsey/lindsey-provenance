# lindsey-provenance

A small Python framework for working with an LLM on a real codebase without losing your mind.

I started writing code for the first time on April 4, 2026. By May 20, I had ~280,000 lines of Python across several projects, all written with LLM co-authorship. Most of it works. Some of it didn't. The pattern that separated "works" from "didn't" was discipline — specifically, the few practices in this repo.

`lindsey-provenance` is those practices extracted into a tool. It is what I wish I'd had on day one.

## What problem this solves

When you collaborate with an LLM on a codebase that gets bigger than a single file, three things go wrong:

1. **The codebase drifts.** Every conversation, the LLM cheerfully reaches for a new dependency, a new style, a new abstraction. After a month you have torch and scipy and four "helper" modules nobody can explain.
2. **Claims inflate.** The LLM writes confident text. The human reads confident text. After a few weeks, simulated demos start getting described like validated systems. By month three you're not sure what's actually true.
3. **Provenance evaporates.** You can't reconstruct why a given decision was made three weeks ago, or which version of the codebase a paper figure came from.

This repo handles all three.

## The four practices

| Practice | What it actually does |
|---|---|
| **Closed-form re-route at intake** | Every brief that arrives from the LLM gets triaged before any code is written. If it imports torch / scipy / scikit / etc., we re-route to a stdlib + numpy substitute that preserves the algorithmic intent. Done four times against four structurally different torch surfaces in the source projects; works. |
| **Phase-chain freeze** | Each project phase produces a SHA-256 manifest that inherits the prior phase's SHA. The chain runs unbroken from the sealed baseline through every subsequent phase. If a file silently drifts, the next freeze fails loudly. |
| **Six-state proof-state ledger** | An artifact's claim level is one of six states: `idea → planned → implemented → simulated → artifact-generated → physically-validated`. Monotonic. You can't claim a state you haven't reached. Forces honesty about what's demonstrated vs. described. |
| **Multi-modal brief assimilation** | A seven-phase pipeline that ingests `.docx`, `.eml`, photos, and handwriting from the operator and emits a domain-tagged triage report. Stop losing intent in long Slack threads. |

That's the whole repo. About 14 modules. Stdlib + numpy only.

## Quickstart

```bash
pip install -e .
lindsey-provenance init my-project
cd my-project
lindsey-provenance new-project my-first-project
lindsey-provenance proof-state set my-first-project planned
lindsey-provenance freeze my-first-project --phase 1
lindsey-provenance audit
```

The hello-world example in `examples/hello-world/` exercises every CLI tool end-to-end in under a minute.

## The ten CLI tools

| Command | What it does |
|---|---|
| `lindsey-provenance init <dir>` | Scaffold a new operator workspace with the discipline pre-wired |
| `lindsey-provenance new-project <slug>` | Add a project to the workspace; opens an `INTAKE.md` template |
| `lindsey-provenance proof-state` | Transition a project through the six states |
| `lindsey-provenance freeze <slug> --phase N` | Compute the phase-N SHA-256 manifest, inheriting phase N-1 |
| `lindsey-provenance audit` | Sealed-core drift + inheritance + ledger + IP + chain checks |
| `lindsey-provenance ip-extract <slug>` | Surface `# IP-CLAIM:` markers into a draft IP journal |
| `lindsey-provenance sign-ip` | Flip DRAFT IP entries to SIGNED with operator signature |
| `lindsey-provenance status` | Cross-project snapshot |
| `lindsey-provenance purge-selftest` | Clean up self-test artifacts |
| `lindsey-provenance assimilate <brief-path>` | Seven-phase ingestion of .docx / .eml / photos / handwriting |
| `lindsey-provenance run-phase <slug> <N>` | Execute a phase end-to-end: build → self-test → IP extract → freeze |

## What this is NOT

- Not a build-system replacement. Use Bazel / Nix / make for actual reproducible builds. lindsey-provenance tracks the *output state*; it does not control the build.
- Not a formal-verification tool. The fail-loud gates are conventions enforced at audit time, not theorem-prover proofs.
- Not magic. If your LLM session uses non-deterministic sampling, lindsey-provenance cannot make the generation deterministic. It just makes the output state auditable after the fact.
- Not a substitute for physical validation. The `physically-validated` proof state requires real instruments and witnesses, not a flag you flip.

## Who I am, briefly

Brad M. Lindsey. Master Electrician + Master HVAC Technician. Started writing code on 2026-04-04. This repo is the methodology that made the rest of my codebase survive its own creation rate. The author bio on the companion arXiv preprint has the longer version.

## License

MIT. See `LICENSE`.

## Citing this work

If you use lindsey-provenance or the disciplines in it in academic work, please cite the companion preprint:

> Lindsey, B. M. (2026). *Phase-chain freeze and closed-form re-route: a discipline for LLM-collaborative engineering with cryptographic provenance.* arXiv preprint. (URL to be added when published.)

## Contributing

External code contributions are not accepted in v0.1 — I want 60–90 days to see how the repo behaves in the wild before taking on maintainer load. Issues are very welcome; please open them. Discussion of the methodology is encouraged.

## Contact

GitHub issues for technical questions. For consulting on AI-assisted engineering discipline at mid-market companies, contact via the email on my GitHub profile.

---

*v0.1.0 — released alongside the companion preprint. No major API changes intended before v1.0. Patch releases will be cut as the few sharp edges get filed.*
