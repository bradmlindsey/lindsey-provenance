# Project Intake — `<slug>`

**Brad M. Lindsey · Lindsey Lab**
**Inherits:** `my-engine.v1.freeze-1` = `9f9d28e5bfbcbc8c66c9c9e167ae20b6389493fef28e3caec59cdb47c00fbb57`
**Intake date:** `YYYY-MM-DD`

> This template is the input contract for every new project spawned under the sealed baseline. Fill in every section. Where a section is not applicable, write **N/A** rather than leaving blank. Conforms to `PROJECT_INTAKE_SCHEMA.json`.

---

## 1. Identity

- **Slug:** `<slug>` (kebab-case, 3–32 chars)
- **Project name:** `<full name>`
- **Project codename:** `<optional short codename, e.g. PT-1, BR-1>`
- **Principal:** `<your name>`
- **Institution:** `<your institution, or "independent">`
- **IP classification:** `<your IP classification, e.g. internal-only, proprietary, MIT-licensed-on-release>`

## 2. Definitions

- **One-sentence technical definition:**
  `<≥ 40 chars; precise scientific framing>`

- **One-sentence non-technical definition:**
  `<≥ 40 chars; plain-language framing for an investor or external party>`

- **Must NEVER be confused with:**
  - `<counter-indication 1>`
  - `<counter-indication 2>`

## 3. Inheritance

- **sealed baseline:** `my-engine.v1.freeze-1` = `9f9d28e5bfbcbc8c66c9c9e167ae20b6389493fef28e3caec59cdb47c00fbb57` (mandatory)
- **Additional prior project inheritances (optional):**
  | Slug | Phase freeze | SHA-256 |
  |---|---|---|
  | `<e.g. fed-cab>` | `fed.phase4.freeze-1` | `68bb...04fa4` |

## 4. Six-section intent

### 4.1 Structural

```
material_card     = <SLA_RIGID_10K | TPE_SHORE85 | PDMS | NEOPRENE | CONCRETE_CL | CUSTOM>
scale_axis_m      = <0.060 - 2.000>
min_feature_size_m = <≥ 3.00e-4>
min_wall_thickness_m = <≥ 6.00e-4>
edge_snap_tolerance_m = 1.0e-6
eps_target         = <0.001 - 0.040>
wall_amp_ratio     = <0.0 - 1.0>
span_mm            = <free>
```

### 4.2 Environmental fields

```
peak_mechanical_load_n     = <N>
von_mises_threshold_pa     = <≤ 1.2e7>
external_hydro_pressure_pa = <Pa>
temp_c                     = 22.0
```

### 4.3 Acoustic carriers

```
center_frequency_hz   = <Hz>
sweep_range_hz        = [<lo>, <hi>]
target_quality_factor = <Q>
f_corner_lc_match_hz  = 5000.0
```

### 4.4 Fluidic transport

```
max_mach_number       = <≤ 0.30>
fluid_viscosity_pa_s  = <Pa·s>
saturation_pressure_pa = 2340.0
inlet_v_ms            = <m/s>
```

### 4.5 Invariants

```
laminar_override          = true
zero_telemetry_enclosure  = true       # Rule 8 — cannot be disabled
bfs_drainage_check        = true
```

### 4.6 Process gates

```
max_rmse_convergence       = 1.0e-6    # Rule 75 ceiling
min_mpi_processes_per_case = 64        # Rule 76 floor
min_pearson_r              = 0.95      # Rule 78 floor
max_cascade_leak           = 1.0e-6    # Rule 79 ceiling
min_macro_margin           = 2.5       # Rule 80 floor
min_drainage_pct           = 99.0
```

## 5. Phase plan

- **Phases planned:** 4 (Phase 1 / 2 / 3 / 4 — canonical)
- **Expected theory branches:** `<1-5>` (Rule 76 caps at 5)
- **Phase target dates (tentative):**
  - Phase 1: `YYYY-MM-DD`
  - Phase 2: `YYYY-MM-DD`
  - Phase 3: `YYYY-MM-DD`
  - Phase 4: `YYYY-MM-DD`

## 6. Demo target

- **Smallest physical demo:** `<description>`
- **Estimated cost (USD):** `<$>`
- **Estimated time (weeks):** `<wk>`

## 7. Long-term vision (speculative — marked as such)

`<description>` — explicitly marked SPECULATIVE until Phase 5 wet-bench. Avoid overclaim language.

## 8. Prohibited language

Standard prohibition list (cannot be relaxed):
- "sentient"
- "cognitive"
- "biological intelligence"
- "autonomous choice"

Project-specific additions:
- `<term>`

## 9. Principal sign-off

> *I, `<your name>`, authorise the spawn of project `<slug>` under the lindsey-provenance framework, inheriting `<sealed-baseline-name>`, with all output classified as `<IP classification>`.*

- **Signed by:** `<your name>`
- **Signed UTC:** `YYYY-MM-DDThh:mm:ssZ`
- **Note:** `<optional>`

---

— Filled by the operator under directive of Brad M. Lindsey · Lindsey Lab
