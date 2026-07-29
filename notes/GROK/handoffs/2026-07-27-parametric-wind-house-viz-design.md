# Design — Parametric wind in the integrated house viz

**Date:** 2026-07-27  
**Plan:** `2026-07-27-parametric-wind-house-viz-plan.md`  
**Research:** `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
**Wiki:** `notes/WIKI/parametric-wind-pipeline.md`

---

## 1. Overview / Background & Motivation

The dual suite already displays MetGet GFS wind (`wind_gfs`), mesh wind (`wind_fort74`), and RICHAMP post wind (`wind_post`), and can **force** ADCIRC from SHiELD via `wind_bridge`. A large fraction of historical RICHAMP / Floodwater / scenario work used **NHC parametric wind** (`generateParametricInput` + `windgfdl` → `richamp.wnd`), including Milton and Erin operator recipes.

That path is production-real but **invisible as an honest product** in the house fieldpack: the only ways to see it today are (a) pretend it is GFS via `--path wind_gfs=…`, (b) downscale to `RICHAMP_wind` and use `wind_post`, or (c) run ADCIRC and use fort.74. None of those preserve “this is PWM / parametric vortex wind” for science integrity.

## 2. Goals & Non-Goals

### Goals

1. Export parametric wind netCDF into `adcirc-fieldpack/v0` with correct units, times, and source labels.
2. Render it in the existing suite shell (globe + 2D, particles, scrub) without a second SPA.
3. Keep drive-met ops knowledge (fort.15 565×625 domain, NWS 6/306) in wiki + thin skill pointers.
4. Enforce explicit decimation/subset for large basin grids (parity with `wind_post` stride policy).

### Non-Goals

- Reimplement `windgfdl` or ship a Mac binary.
- Close the ASGS post_init automation TODO in the first PR.
- Parametric rain fieldpack adapter (document only until a golden rain pack is needed).
- Invent lon/lat or synthetic storms for demos.

## 3. Technical Requirements

### Functional

| ID | Requirement |
|----|-------------|
| FR-1 | Accept a product path to an owi2wind-style netCDF (`wind_u`, `wind_v`, `lon`, `lat`, optional `PSFC`). |
| FR-2 | Write fieldpack rows: `wind_u`, `wind_v`, `wind_speed`, vector `wind`, optional `pressure_surface` (same semantics as GFS adapter for PSFC→mb trap). |
| FR-3 | Register a dedicated time stream `"parametric"` (do not share GFS or ADCIRC scrub indices). |
| FR-4 | Grid type regular lat/lon; coords from file, never synthesized. |
| FR-5 | Long names / source metadata must say parametric / PWM / file stem — never “GFS”. |
| FR-6 | CLI: `--products …,wind_parametric` and `--path wind_parametric=/path/to.nc`. |
| FR-7 | If full-basin dimensions exceed a documented threshold (e.g. nx×ny×nt f16 > budget), refuse unless `--wind-stride N` or bbox subset is provided; record in `meta.fidelity`. |
| FR-8 | Suite shell lists the stream/source; particles use existing earth-relative u/v convention `atan2(-v, u)`. |
| FR-9 | Drive-path docs remain authoritative for fort.15 domain line when using windgfdl met for runs. |

### Non-functional

| ID | Requirement |
|----|-------------|
| NFR-1 | Scientific integrity ≥ offline Reader/Grapher for the same nc (parity via Reader GFS path). |
| NFR-2 | G-EXT: new product = adapter + one import line; no chrome rewrite. |
| NFR-3 | No NetCDF in the browser — fieldpack only. |
| NFR-4 | Existing gates G-LOAD / G-HOUSE / G-MULTI (wind) must still pass. |

## 4. User Stories

### US-1 — Export parametric wind into a coastal pack

**As** a coastal modeler, **I can** point export at `erin_parametric_wind.nc`, **so that** the pack contains wind fields labeled parametric.

**Acceptance:**

- `python -m post.export.cli … --products mesh,water,wind_parametric --path wind_parametric=$NC` exits 0  
- `meta.json` field long_name contains “parametric” (or “PWM”)  
- `time_streams.parametric` present; timestamps match Reader-parsed times  

### US-2 — Inspect parametric wind in the house shell

**As** a scientist, **I can** load that pack in the suite shell, toggle wind speed / particles, scrub time, **so that** I inspect the vortex field without Grapher.

**Acceptance:**

- G-MULTI-equivalent: wind layer changes with time; particles advect when visible  
- Units m s-1 on colorbar from meta  
- Source drawer does not say GFS  

### US-3 — Drive ADCIRC with windgfdl met (ops, docs)

**As** an operator, **I can** follow the wiki recipe and set fort.15 domain to the 565×625 line, **so that** padcirc/padcswan accepts the parametric met.

**Acceptance:**

- Wiki + research note reconstruct Milton/Erin steps  
- Checklist mentions domain line and NWS 6 vs 306  

### US-4 — Refuse silent megapacks

**As** a maintainer, **I can** trust export will not ship a multi-hundred-MB basin wind pack by default, **so that** the browser stays usable.

**Acceptance:**

- Export exit 2/3 or hard error without stride/subset when over threshold  
- When stride used, `meta.fidelity.decimation` records it  

## 5. Technical Guidelines (invariants)

1. **Fieldpack is display SoT** — same house law as ORDER 0–11.  
2. **NaN is no data** — never zero-fill calm as “wet science” unless the product truly is 0.  
3. **One wind direction convention:** `atan2(-v, u)` in the shell only.  
4. **NWS 306 = 6 + SWAN** for drive met — do not invent a second met format for waves.  
5. **Domain for windgfdl drive:** `565 625 51.000000 -101.000000 0.083333 0.083333` only (unless Wind_Inp is deliberately regenerated with a different box — then recompute counts; do not mix boxes).  
6. **Stream isolation:** parametric timestamps map by ISO time, never by shared index with fort.63.  
7. **Binary black box:** `windgfdl` stays external; house only consumes its outputs.  
8. **Honest labels:** source family ∈ {gfs, parametric, fort74, post, shield_bridge}.

## 6. Proposed Design

### 6.1 Architecture

```text
                    Operator / archive
              ┌─────────────┴─────────────┐
              │  parametric.nc (owi2wind) │
              └─────────────┬─────────────┘
                            │
              post.export.cli --products wind_parametric
                            │
              WindParametricAdapter  (clone WindGfsAdapter)
                            │
              PackWriter: grid "parametric", stream "parametric"
                            │
              adcirc-fieldpack/v0
                            │
              suite-shell (Path B)  — existing wind layers
```

### 6.2 Adapter sketch

Clone `post/export/field_adapters/wind_gfs.py`:

```python
@register
class WindParametricAdapter:
    name = "wind_parametric"
    products = ("wind_parametric", "wind")  # "wind" only if no gfs preferred — prefer exclusive product key

    def _path(self, ctx):
        case = ctx.case_dir or ctx.rundir.parent
        return ctx.resolve(
            "wind_parametric",
            case / "met" / "parametric_wind.nc",
            case / "met" / "richamp_parametric.nc",
            ctx.rundir / "parametric_wind.nc",
        )

    def export(self, ctx):
        # same body as wind_gfs with:
        #   open_with_times(path, "GFS", "gfs")  # Reader format token for minutes-since-1990
        #   stream = "parametric"
        #   grid = "parametric"
        #   long_name = "Parametric (PWM) 10 m wind, …"
```

**Conflict policy:** if both `wind_gfs` and `wind_parametric` are requested, both may export with distinct field names:

| GFS keys | Parametric keys (recommended) |
|----------|-------------------------------|
| `wind_u`, `wind_v`, `wind_speed`, vector `wind` | `param_wind_u`, `param_wind_v`, `param_wind_speed`, vector `param_wind` |

Alternatively share component names only when exclusive — prefer **prefixed keys** to avoid meta collisions when dual-met packs are desired (compare GFS forcing vs parametric forcing on the same water run).

### 6.3 Shell

Minimal: field-agnostic layer registry already iterates `meta.fields[]`. Ensure:

- vector convention string present  
- stream scrubber binds to field dims  
- optional display name map for `param_wind_*`  

No new globe geometry type.

### 6.4 Drive-met companion (docs + optional CLI later)

Not required for viz PR:

```text
fort.15 met domain when using windgfdl 306:
565 625 51.000000 -101.000000 0.083333 0.083333
NWS = 6 | 306
```

Future P3: `python -m post.export.parametric_bridge --track … --out …` wrapping generateParametricInput + documenting that windgfdl must still run on Linux.

### 6.5 Size policy (proposed defaults)

| Condition | Action |
|-----------|--------|
| `nx * ny * nt * 2 * 2 bytes` ≤ 80 MiB | export full f16 |
| larger | require `--wind-stride ≥ 2` or lon/lat bbox in CLI |
| still larger after stride | fail loud |

Basin 565×625×120×2×2 ≈ 170 MiB → stride 2 or regional crop for RI house demos.

## 7. Boilerplate / placeholder

### 7.1 Register

```python
# post/export/field_adapters/__init__.py
from . import wind_parametric  # noqa: F401
```

### 7.2 CLI products help

```text
--products mesh,water,wind_parametric,stations
--path wind_parametric=/path/to/erin_parametric_wind.nc
--wind-stride 2
```

### 7.3 Contract table row (`ADCIRC_FIELDPACK_V0.md`)

```markdown
| parametric PWM | owi2wind `*.nc` from richamp.wnd | stream `parametric`; u/v m/s; optional PSFC mb |
```

### 7.4 Verify

```bash
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir $CASE/forecast --mesh $CASE/forecast/fort.14 --case $CASE \
  --products mesh,water,wind_parametric \
  --path wind_parametric=$CASE/met/parametric_wind.nc \
  --wind-stride 2 \
  --outdir $CASE/products/fieldpack
PYTHONPATH=. pipenv run python -m post.export.verify_pack $CASE/products/fieldpack
node $VIZ/verify-fieldpack.js $CASE/products/fieldpack --require-fields param_wind_u,param_wind_v
```

## 8. Alternatives Considered

| Alt | Why not preferred |
|-----|-------------------|
| Reuse `wind_gfs` only with path override | Works technically; **lies** in long_name/source; dual-met packs collide |
| Only `wind_post` via scale_and_subset | Heavy RI product; needs roughness assets; not raw PWM |
| fort.74 only | Requires full ADCIRC run; not a wind library |
| New SPA / MapLibre fork | Violates house law (Path B only) |
| Parse `.wnd` in the browser | Violates fieldpack SoT |

## 9. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Schema source | owi2wind netCDF | Already MetGet-class vars; offline Reader works |
| Adapter | New `wind_parametric` | Honest labels + dual-met packs |
| Field key prefix | `param_wind_*` | Avoid collision with GFS keys |
| Stream name | `parametric` | Separate scrub clock |
| Size | Explicit stride/subset | Same lesson as wind_post 6 GB |
| rain | Defer | No adapter demand this session |
| windgfdl on Mac | Out of scope | Use Linux or golden fixtures |
| ASGS TODO | Document only | Not house-viz critical path |

## 10. PR Plan

### PR1 — Docs already landed (this session)

- research note, wiki, INDEX, how-to-construct, what-we-use, this design, handoff, DEV_NOTES  
- **No code**

### PR2 — Export adapter + size guard

**Files:**

- `post/export/field_adapters/wind_parametric.py` (new)  
- `post/export/field_adapters/__init__.py`  
- `post/export/cli.py` (`--wind-stride` or reuse post-stride pattern)  
- `post/export/ADCIRC_FIELDPACK_V0.md`  
- `post/export/parity_check.py` (adapter var set)  
- optional fixture under `test/` or case `met/`

**Deps:** golden nc  
**Gate:** export + verify_pack  

### PR3 — Shell labels + dual-met smoke

**Files:** CloudVision `threejs-shield-live-viz` (display names only if needed)  
**Gate:** verify-shell G-HOUSE / wind subset of G-MULTI  

### PR4 — Ops thin pointers

**Files:** `.grok/skills/run-adcirc/SKILL.md` or checklist — link wiki parametric recipe + fort.15 domain line  
**Gate:** skill length stays thin; no roadmap dump  

## 11. Open Questions

1. Prefixed field keys vs exclusive `wind_*` when only parametric is present — recommend prefix always for stable UI bookmarks.  
2. Exact MiB threshold / stride default for basin packs.  
3. Whether `PSFC` from owi2wind 306 is true surface pressure or MSLP from the vortex model (label carefully after ncdump of a golden).  
4. Golden fixture location: case `met/` vs repo `test/fixtures/` (large files → external preferred).  
5. Promote parametric rain adapter when `RICHAMP_rain.nc` is needed in-pack.

## 12. References

- Research: `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
- Wiki: `notes/WIKI/parametric-wind-pipeline.md`  
- `generateParametricInput.py`, `owi2wind.py`, `windgfdl`, `diag_parm.nml`  
- `post/export/field_adapters/wind_gfs.py`, `wind_bridge.py`  
- House complete: `2026-07-25-richamp-support-web-orders-complete-handoff.md`  
- Run foundations: `notes/GROK/research/2026-07-25-run-adcirc-foundations.md`  
