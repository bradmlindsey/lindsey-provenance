# lindsey-provenance

A small Python framework for working with an LLM on a real codebase without losing your mind.

I started writing code for the first time on April 4, 2026. By May 20, I had ~280,000 lines of Python in cumulative authorship across several projects, all written with LLM co-authorship. Most of it works. Some of it didn't. The pattern that separated "works" from "didn't" was discipline — specifically, the few practices in this repo.

`lindsey-provenance` is those practices extracted into a tool. It is what I wish I'd had on day one.

## Publications

This work is documented in three open-access papers (CC BY 4.0):

- **Phase-Chain Freeze and Closed-Form Re-Route: A Discipline for LLM-Collaborative Engineering with Cryptographic Provenance** — the methodology. https://doi.org/10.5281/zenodo.20481729
- **One Operator, Nine Trunks, Seven Weeks** — an experience report on building it. https://doi.org/10.5281/zenodo.20469751
- **Zero of Forty-Nine** — a calibrated self-audit of the portfolio's novelty claims. https://doi.org/10.5281/zenodo.20470317

arXiv version of record forthcoming. Author of record: ORCID 0009-0004-6392-2720.

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

ORCID: [0009-0004-6392-2720](https://orcid.org/0009-0004-6392-2720)

## License

MIT. See `LICENSE`.

## Citing this work

If you use lindsey-provenance or the disciplines in it in academic work, please cite the companion preprint:

> Lindsey, B. M. (2026). *Phase-chain freeze and closed-form re-route: a discipline for LLM-collaborative engineering with cryptographic provenance.* arXiv preprint. (URL to be added when published.)

## Verification

The author identity that signs this repository, the companion preprint, the retro-signed proof-state ledger, and all five web surfaces (`bradmlindsey.com`, `lindseyprovenance.com`, `bygyze.com`, `gizuiz.com`, `aenoris.com`) is bound to a single Ed25519 public key.

**Public-key fingerprint:**

```
62ad9c80005a2c58e574ec3232d9bf09416ffd7bdf1a47077afe745c4c37b6db
```

This is the raw-bytes hex of the Ed25519 public key. SHA-256 over the raw public key starts with `907a5aab75724821…`. The key was generated 2026-05-26 PM and is referenced from the master ledger at `02_methodology/master_authorship_ledger.md` Section E.1.

### What this public key signs

- **The proof-state ledger.** All 152 transitions in the project's `proof_state_ledger/LEDGER.jsonl` were retro-signed in a single pass at `2026-05-26T22:47:09Z`, producing `LEDGER.signed.jsonl`. The sign-pass timestamp is recorded as a distinct field (`retro_signature_ts`) from the original transition timestamps, so verifiers can distinguish original-event time from binding-event time.
- **The master authorship ledger.** `02_methodology/master_authorship_ledger.md` Section A canonical entries. The full workspace state at the time of the public flip of this repository is anchored at SHA-256 path-plus-size rollup `234ea7b3…0416` / IP-critical content rollup `5a71881d…cf95` (E.1 row dated `2026-05-26 PM drop Step 4`).
- **Future signed artifacts.** Any document, slide deck, or artifact that links back to the verification procedure with this fingerprint claims the same author identity.

### How to verify a signed ledger entry

The signed ledger (`LEDGER.signed.jsonl`) is one JSON object per line. Each line carries the seven authoritative fields (`artifact_name`, `prior_state`, `new_state`, `transition_ts`, `operator_id`, `evidence_sha256`, plus the LEDGER protocol version) and three signature fields appended by the retro-sign script:

- `retro_signature_ed25519` — hex-encoded Ed25519 signature, 128 hex chars (64 bytes)
- `retro_signature_ts` — ISO 8601 UTC sign-pass timestamp
- `retro_signature_method` — `"ed25519_v1"`

To verify a single row with the public key, using Python and the `cryptography` library:

```python
import json
import binascii
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

# Load the public key (PEM format from the canonical pub file)
with open("brad_authorship.pub", "rb") as f:
    pub = load_pem_public_key(f.read())

# Parse a row from LEDGER.signed.jsonl
row = json.loads(LINE_FROM_LEDGER)

# Reconstruct the canonical form (the seven authoritative fields,
# JSON-serialized with sorted keys, no whitespace, UTF-8 bytes)
auth_fields = {
    k: row[k] for k in [
        "artifact_name", "prior_state", "new_state",
        "transition_ts", "operator_id", "evidence_sha256",
        "ledger_version"
    ]
}
canonical = json.dumps(auth_fields, sort_keys=True, separators=(",", ":")).encode("utf-8")

# Decode the signature and verify
sig = binascii.unhexlify(row["retro_signature_ed25519"])
try:
    pub.verify(sig, canonical)
    print("verified")
except InvalidSignature:
    print("FAILED")
```

The canonical-form discipline binds only the seven authoritative fields. Adding extra fields to a row after signing does not change the signature (verified in the 2026-05-26 PM dry-run; the canonical form is stable under extra-field addition).

### Obtaining the public key file

The PEM-encoded public key is published at `02_methodology/keys/brad_authorship.pub` in this repository (the private key is never committed). You can also reproduce the fingerprint locally:

```bash
openssl pkey -pubin -in brad_authorship.pub -outform DER | sha256sum
# (Note: this hashes the DER-encoded SubjectPublicKeyInfo, not the raw bytes.
# The raw-bytes fingerprint above is what's published; SHA-256 of the raw
# bytes gives 907a5aab75724821… as the prefix.)
```

### When the key rotates

Key rotation would be a major identity event and would require a coordinated update across this repository, all five web surfaces, the LinkedIn featured section, the ORCID profile, and any active arXiv submissions. The brand package at `04_external/websites/BRAND_PACKAGE_v1.md` documents the rotation protocol. As of 2026-05-27 the public key has not rotated and no rotation is scheduled.

### What this public key does NOT sign

- It does not vouch for the truth of any claim in this repository's documentation. It vouches that this author wrote those words at the sign-pass timestamp.
- It does not establish that any proof-state transition's content is true. It establishes that whoever held the private key on 2026-05-26 attested to the recorded state of each transition.
- It does not extend to derivative works by other authors. A fork's commit history is bound to the forker's keys, not this one.

## Contributing

External code contributions are not accepted in v0.1 — I want 60–90 days to see how the repo behaves in the wild before taking on maintainer load. Issues are very welcome; please open them. Discussion of the methodology is encouraged.

## Contact

GitHub issues for technical questions. For consulting on AI-assisted engineering discipline at mid-market companies, contact via the email on my GitHub profile.

---

*v0.1.0 — released alongside the companion preprint. No major API changes intended before v1.0. Patch releases will be cut as the few sharp edges get filed.*
