# Builder Prompt Template

**Purpose:** This file renders a phase brief into a canonical directive for a build agent (Claude, Gemini, or any qualified successor). It is the **standardised dispatch format** for any phase of any project under the BRAD engine. The operator copies this template, fills the slots, and pastes the result to the build agent verbatim.

**SECRET IP · Brad M. Lindsey · Lindsey Lab**
**Replicator baseline:** `ace.phase4.freeze-1` = `9f9d28e5bfbcbc8c66c9c9e167ae20b6389493fef28e3caec59cdb47c00fbb57`

---

## How to use this template

1. Open `phases/PHASE_<N>.md` for the project to dispatch.
2. Open `PROJECT_MANIFEST.json` for the project.
3. Replace every `<...>` slot below with the corresponding content.
4. Save the rendered file as `phases/<slug>_phase<N>_BUILDER_PROMPT.md`.
5. Dispatch the rendered prompt to the build agent.
6. After dispatch, log the prompt SHA-256 + dispatch UTC into `lab_notebooks/<slug>_LN_<date>.md`.

---

## RENDERED PROMPT BEGINS BELOW THIS LINE — copy from here

```
═══════════════════════════════════════════════════════════════════════════
                 LINDSEY PROVENANCE DISCIPLINE · BUILD AGENT DIRECTIVE
═══════════════════════════════════════════════════════════════════════════

Principal:         <your name>
Institution:       <your institution, or "independent">
Project slug:      <slug>
Project codename:  <codename>
Phase:             <N> of 4 — <phase title>
Replicator:        <baseline-name> = <sha-256>
Dispatch UTC:      <YYYY-MM-DDThh:mm:ssZ>
IP classification: SECRET IP · institutional reserve

═══════════════════════════════════════════════════════════════════════════
SCOPE
═══════════════════════════════════════════════════════════════════════════

You are building Phase <N> of the project <slug> under the WOQFEW
programme, replicated from the sealed BRAD engine.

Phase scope (one line):
    <one-line scope from PHASE_<N>.md §1>

This phase covers the following steps of the canonical 12-step partition:
    <list from PHASE_<N>.md §2>

═══════════════════════════════════════════════════════════════════════════
INHERITANCE — DO NOT MODIFY
═══════════════════════════════════════════════════════════════════════════

You inherit from the sealed BRAD engine at:

    ace.phase4.freeze-1 = 9f9d28e5bfbcbc8c66c9c9e167ae20b6389493fef28e3caec59cdb47c00fbb57

You may import from PROGECT BRAD/core/ — read-only. You must NEVER modify
any file under PROGECT BRAD/core/. Doing so triggers a sealed-core drift
alert and invalidates this phase.

You inherit from prior project phases:
    <list from PROJECT_MANIFEST.json:inherits_from.additional_projects>

Every output of this phase MUST inline the replicator baseline SHA-256
into its manifest under the key replicator_baseline_sha256. The freeze
tool refuses to seal without this assertion.

═══════════════════════════════════════════════════════════════════════════
DELIVERABLES
═══════════════════════════════════════════════════════════════════════════

Modules to author (write to operator/projects/<slug>/proto/):
    <list from PHASE_<N>.md §3>

Artifacts to emit (write to operator/projects/<slug>/artifacts/):
    <list from PHASE_<N>.md §9>

Reports to produce (write to operator/projects/<slug>/docs/):
    <slug>_PHASE<N>_REPORT.md

═══════════════════════════════════════════════════════════════════════════
NUMERICAL GUARDRAILS
═══════════════════════════════════════════════════════════════════════════

Every step of every module must audit the following envelopes. On breach,
raise the named exception with the field value and the rule crossed.

    <table from PHASE_<N>.md §4>

These are not stylistic preferences. They are architecturally enforced
invariants inherited from the sealed BRAD engine.

═══════════════════════════════════════════════════════════════════════════
ACCEPTANCE CRITERIA
═══════════════════════════════════════════════════════════════════════════

The phase is accepted only when every row below is PASS. Each row maps
to a specific on-disk artifact.

    <table from PHASE_<N>.md §5>

═══════════════════════════════════════════════════════════════════════════
IP CAPTURE — IN FLIGHT
═══════════════════════════════════════════════════════════════════════════

While writing source, mark every novel combination with a comment of the
form:

    # IP-CLAIM: <one-line description>
    # NOVEL: <reason>
    # Rule <N>: <one-line statement>  (only if you are proposing a new rule)

The operator's brad_ip_extract.py tool scans for these markers and
pre-populates ip_journal/ rows. You are NOT to declare novelty
unilaterally; you mark candidates. The Principal signs.

═══════════════════════════════════════════════════════════════════════════
DETERMINISM
═══════════════════════════════════════════════════════════════════════════

- All randomness via np.random.default_rng(seed) with a module-scope seed.
- All JSON manifests serialised with sort_keys=True, indent=2.
- All STL vertices quantised to 1 µm before write.
- No floating-point comparisons without an explicit tolerance.

═══════════════════════════════════════════════════════════════════════════
DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════

Allowed:    numpy (≥ 1.22) + Python 3.10+ stdlib.
Forbidden:  torch, tensorflow, keras, jax, scipy.optimize, ML wrappers,
            any external geometric or topological optimisation library,
            any networked dependency.

═══════════════════════════════════════════════════════════════════════════
ATTRIBUTION (REQUIRED IN EVERY MODULE DOCSTRING)
═══════════════════════════════════════════════════════════════════════════

    """<module name> — <one-line purpose>

    SECRET IP BUILD — Property of Brad M. Lindsey at the institutional
    level. Lindsey Lab · Project <slug>.

    Inherits ace.phase4.freeze-1.
    """

═══════════════════════════════════════════════════════════════════════════
SELF-TEST CONTRACT
═══════════════════════════════════════════════════════════════════════════

Every module ends with:

    if __name__ == "__main__":
        _selftest()

The _selftest() must:
    1. Build a representative input.
    2. Run the module's primary entry point.
    3. Print exactly one verification line of the form:
           [<slug>_<MODULE>: PASS — <metric>=<value> <units>]
    4. Exit 0 if all audits pass; exit non-zero with a named exception
       on any breach.

═══════════════════════════════════════════════════════════════════════════
ANTI-OVERCLAIM
═══════════════════════════════════════════════════════════════════════════

Forbidden language in source, comments, docstrings, and reports:
    "sentient", "cognitive", "biological intelligence",
    "autonomous choice", and any project-specific additions from
    PHASE_<N>.md §8.

The framework is a deterministic, multi-physics field-state analog
optimisation engine. State it that way.

═══════════════════════════════════════════════════════════════════════════
OUT OF SCOPE FOR THIS PHASE
═══════════════════════════════════════════════════════════════════════════

- Modifying PROGECT BRAD/core/.
- Authoring IP claims (only mark candidates).
- Declaring proof states (only emit artifacts; brad_proof_state.py
  classifies).
- Sealing the freeze (only run the audit; brad_freeze_manifest.py seals).
- Wet-bench claims (Phase 5 only; this is a compiler-side phase).

═══════════════════════════════════════════════════════════════════════════
TAIL-SAFE CODE STYLE (v2 - lessons from XT-1 and XT-2 friction)
═══════════════════════════════════════════════════════════════════════════

Some build environments truncate Python module tails at multi-line
print() statements, dict literals, and bracketed expressions. The build
agent must defensively author tails to survive truncation:

  1. NEVER use multi-line print() across two or more lines. Build the
     message string first as a local variable, then print on a single line:
        line = "foo " + str(x) + " bar " + str(y)
        print(line)
     NOT:
        print("foo " + str(x)
              + " bar " + str(y))

  2. NEVER use multi-line dict literals near module tail. Use dict() +
     line-by-line item assignment:
        d = dict()
        d["a"] = 1
        d["b"] = 2
     NOT:
        d = {
            "a": 1,
            "b": 2,
        }

  3. For modules whose self-test runs heavy geometry, write an EXTERNAL
     runner script (run_<module>_test.py) that imports the module and
     hosts the test logic. This isolates the module body from any tail
     friction.

  4. After every file save, strip null bytes:
        python3 -c "d=open(F,'rb').read(); open(F,'wb').write(d.replace(b'\x00',b''))"

  5. Always confirm the file compiles BEFORE running:
        python3 -c "import ast; ast.parse(open(F).read())"

═══════════════════════════════════════════════════════════════════════════
HONESTY REQUIREMENT
═══════════════════════════════════════════════════════════════════════════

If you cannot clear an audit, halt and report. Do not relax a threshold.
Do not silently re-seed to dodge a violation. Do not paper over a
non-manifold edge. Honesty is the load-bearing surface of every WOQFEW
freeze.

═══════════════════════════════════════════════════════════════════════════
END OF DIRECTIVE
═══════════════════════════════════════════════════════════════════════════
```

## RENDERED PROMPT ENDS ABOVE THIS LINE

---

## Post-dispatch operator checklist

After dispatching the rendered prompt, the operator:

1. Logs the rendered-prompt SHA-256 into the day's lab-notebook entry.
2. Watches the build session output; flags any audit failure on the spot.
3. After the build agent returns, runs:
   ```
   python3 operator/tools/brad_audit.py --project <slug> --phase <N> --quick
   ```
4. Pre-populates IP-journal rows from `brad_ip_extract.py`.
5. Transitions affected artifact proof states via `brad_proof_state.py`.
6. Requests Principal sign-off on §10 of the phase template before sealing.
7. Runs `brad_freeze_manifest.py --project <slug> --phase <N>` to seal.

---

— Builder prompt generator · Brad M. Lindsey · Lindsey Lab
