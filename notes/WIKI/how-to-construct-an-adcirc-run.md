# How to construct an ADCIRC(+SWAN) run — operational mental model

Not a substitute for the [ADCIRC wiki](https://wiki.adcirc.org/) / user’s manual. This is the **coastal-suite / Unity / RICHAMP** map: what each file *is for*, how wind and tides enter, how hotstarts and SWAN couple, and why **Dec22 / Dec17** are chaos.

**Scientific crest:** why three waters (tides / stillwater / full+setup) and how runup is predicted after the run — [thesis-wave-runup-crescendo.md](thesis-wave-runup-crescendo.md).

---

## 0. One-sentence truth

An ADCIRC run is a **finite-element ocean** on a **triangular mesh** (`fort.14`), driven by a **control file** (`fort.15`) that says *how long*, *what physics*, *what forcing files*, *what outputs*, and (if coupled) a **SWAN command file** (`fort.26` + `swaninit`) run by a **coupled binary** (`padcswan`), not plain `padcirc`.

Brick one field in `fort.14` or mismatch NWS ↔ wind files → model dies or silently lies.

---

## 1. The two always-required files

Per [ADCIRC wiki — File formats](https://wiki.adcirc.org/File_formats):

| File | Role |
|------|------|
| **`fort.14`** | **Grid / mesh**: nodes (lon/lat/depth), triangles, **boundary strings** (ocean open boundary, land, islands, weirs, etc.) |
| **`fort.15`** | **Control**: model type, timestep `DT`, duration, ramping, **tidal harmonics**, **NWS** (met type), output flags, hotstart flags, coupling-related timing |

Everything else is *optional but configuration-dependent*.

---

## 2. `fort.14` — the headache mesh

**What it is:** unstructured mesh + BC topology. Not “just coordinates.”

Rough structure (conceptual):

1. Header / AGRID title  
2. **NE, NP** — number of elements, number of nodes  
3. **Node table:** `ID  lon  lat  depth` (depth sign convention matters)  
4. **Element table:** `ID  3  n1 n2 n3` (always triangles for classic 2DDI)  
5. **Boundary blocks:** open ocean elev/flux segments, mainland, islands, **internal barriers / weirs** (pair of nodes + parameters)

**Why one misformat bricks the run:**

- Wrong NP/NE counts vs tables  
- Node IDs not matching element connectivity  
- Open boundary node string not closed / wrong length  
- Weir pairs not on edges that exist  
- Coordinate system / lon wrap issues  
- Depth units / dry elevation inconsistent with fort.15 wetting-drying  

**This suite’s mesh family:** ricv1 (RICHAMP / Floodwater), navd88, v18/england variants under `AdcircManualRuns/meshes` and `Ricv1Meshes/`. Barrier closed vs open is often a **different fort.14** (weir elevations) — see `TIMEVARYINGWIER_NOTES.txt` and `ricv1_noriv_nopump_closedbar2.grd` diffs.

**Mesh is not configured inside fort.14 as “runtime knobs”** — runtime knobs live in **fort.15**. fort.14 *is* the geometry + static BC topology. fort.13 (optional) is per-node attributes (Manning’s n, canopy, …) aligned **by node index** with fort.14.

---

## 3. `fort.15` — the brain

Owns (among many):

| Concern | Typical fort.15 knobs (names from manual/wiki) |
|---------|-----------------------------------------------|
| Duration | `RNDAY` (days), `DT` (s) — **duration is fort.15, not fort.14** |
| Cold vs hot | `IHOT` — 0 cold; nonzero reads fort.67/68 (or netCDF hotstart) |
| Tides | Harmonic BC: constituent list, frequencies, nodal factors, equilibrium args; open-boundary elev harmonics |
| Met | **`NWS`** digit code → which wind/pressure files and format |
| Met timing | `WTIMINC`, met start relative to model time |
| Ramp | `NRAMP`, `DRAMP*`, special **hotstart met ramp** (`NRAMP=8` + `DRAMPUnMete`) |
| Output | `NOUTGE`/`NOUTGV`/… and spool intervals → fort.63/64 etc. |
| Wave coupling | Met output interval must align with SWAN coupling interval (see fort.26 notes) |

**Tidal-only run:** NWS=0 (no met), harmonics on, coldstart, long enough for spinup.  
**Wind-forced:** NWS ≠ 0, wind/pressure files present and consistent with NWS.  
**Tide + wind:** both on (common coastal “spinup tides then storm” or simultaneous).

---

## 4. How you source the wind (NWS → files)

`NWS` in fort.15 selects the **contract**. Wrong NWS + right files (or reverse) = brick.

| Family (conceptual) | Files | How you get them in this suite |
|---------------------|-------|--------------------------------|
| Best-track / parametric | `fort.22` (ATCF-like or model-specific) | HURDAT / NHC / parametric generators; `generateParametricInput`, `windgfdl` (Floodwater post_init path) |
| **PWM / windgfdl 306** | **`richamp.wnd`** + `Wind_Inp.txt` (drive or convert) | Manual: track → `generateParametricInput` → `./windgfdl` → optional `owi2wind`. **fort.15 domain must be** `565 625 51.000000 -101.000000 0.083333 0.083333`. Full recipe: [parametric-wind-pipeline.md](parametric-wind-pipeline.md) |
| OWI ASCII (NWS12-class) | **`fort.221`** (P), **`fort.222`** (U/V) | Oceanweather, MetGet, `oceanWeatherGenerator.py`, `owi2wind.py`, scenario packs |
| OWI NetCDF (NWS13-class) | netCDF wind | MetGet / converters |
| Prebuilt suite winds | `*.wnd`, large fort.22, scenario winds | `project/scenario_files`, `work/.../wind`, Deb/RICHAMP packs |
| GFS / analysis | netCDF / OWI products | MetGet (`get_metget_data.py`), GFSForecasts |

**Floodwater full post path** (`richamp_scale_and_subset_post_init`): generates/scales winds *for post*, not always the same as the met that drove ADCIRC — but the **run itself** needed fort.22/221/222/wnd present **before** `padcirc`/`padcswan`.

Deb manual recipe (from Unity ManualRuns README era): storm dir gets **fort.22** (e.g. type 306), copy **fort.68.nc** from spinup.

---

## 5. Other fort files (cheat sheet)

| File | When |
|------|------|
| **fort.13** | Nodal attributes (friction, …) — node count must match fort.14 |
| **fort.19 / fort.20** | Nonperiodic elev / river flux time series |
| **fort.22** | Met control / track / single-file met (NWS-dependent) |
| **fort.221 / fort.222** | OWI pressure / wind grids |
| **fort.23 / fort.24** | Wave radiation stress (when waves force circulation **without** full SWAN coupling, or related modes — project-specific; **rads.64.nc** is SWAN *output* of radiation stress) |
| **fort.26** | SWAN command file (ADCIRC’s name for SWAN `INPUT`) |
| **swaninit** | SWAN initialization (same idea as standalone SWAN) |
| **fort.67 / fort.68** (+ `.nc`) | Hotstart state |
| **time_varying_weir.in** (or similar) | Barrier open/close schedule (Deb + `TIMEVARYINGWIER_NOTES.txt`) |

Outputs (not inputs): **fort.63** elev, **fort.64** velocity, **fort.74** met on mesh, **swan_HS.63**, **swan_DIR.63**, **swan_TMM10.63**, **swan_TPS.63**, **rads.64**, maxele, etc.

---

## 6. Hotstarts — the two-phase coastal pattern

Classic Deb / ManualRuns pattern:

```
Phase A — spinup (analysis / a_su)
  IHOT = 0 (cold)
  tides on, often weak or no storm met
  run long enough → write fort.68(.nc)

Phase B — storm (forecast / b_st)
  copy fort.68.nc into storm rundir
  IHOT points at that hotstart
  turn on storm met (fort.22 / OWI)
  optional SWAN coupling for wave-driven setup
```

**Met ramp at hotstart:** wiki notes `NRAMP=8` and `DRAMPUnMete` so met ramps from **hotstart time**, not coldstart day 0 — otherwise you shock the model.

**Archive implication:** fort.68.nc is large; surgical kits default to **coldstart re-run** or keep one hotstart per golden case only.

---

## 7. Wave coupling (oh god) — honest model

### What must be true

1. Binary is **`padcswan`** (or adcswan), **not** plain `padcirc`  
2. **fort.26** present (SWAN commands + unstructured-grid coupling commands)  
3. **swaninit** present  
4. fort.15 allows coupling / met output timing compatible with SWAN  
5. fort.26 **SWAN computation interval** must line up with ADCIRC met output interval or SWAN global fields won’t write ([wiki fort.26](https://wiki.adcirc.org/Fort.26_file))  
6. Launch via **`run_pads.sh`**-class sbatch (coupled), not only `run_padc.sh`

### Extra SWAN outputs that never landed (setup, etc.)

- **Wave setup as its own SWAN netCDF:** tried; **never got a usable setup field out of SWAN.** That failure is *why* Dec22/Dec17 use **three parallel ADCIRC(+SWAN) runs** and differencing instead of a single SWAN setup variable.  
- **Global** SWAN fields timing is largely tied to ADCIRC met output timing in fort.15 — not free-form.  
- **Point** spectra/tables: POINTS + SPECOUT / TABLE in fort.26 (wiki examples).  
- **Radiation stress** (`rads.64` class) and other QUANTITY experiments: same pain class (fort.26 + rebuild) — treat as **open research debt**, not solved lore.

### Why padcirc vs padcswan shows up in runup science

`GetRunup.py` notes: still water / setup separation uses **padcswan** full water vs **padcirc** still-water-ish runs; SWAN wet/dry vs padcirc waterline keys can disagree in time. Multi-folder design is **by design** for the three-way water dissection (tides / surge / setup), not an accident.

---

## 8. Kicking off a run on Unity

Typical manual path:

```bash
cd /path/to/rundir          # has fort.14, fort.15, forcing, scripts
# often: adcprep (domain decomposition) → creates PE0000..PE####
sbatch run_padc.sh         # or run_pads.sh for SWAN-coupled
# watch: squeue, PE*/fort.16, slurm out/err
```

Floodwater/ASGS: suite YAML + ecflow; you don’t hand-assemble fort.* every cycle — but the **physics files under the hood are the same**.

Modules / intel MPI / netCDF must match the **binary** you built (`adcirc.bin.buildinfo.json` on intel-unity tree).

---

## 9. Run “kinds” as recipes

### A. Tidal only (cold)

1. fort.14 + fort.15 (NWS=0, harmonics on) + fort.13 if used  
2. `padcirc` + `adcprep`  
3. Long RNDAY, no fort.22  

### B. Wind-forced (cold or hot)

1. Same mesh/control  
2. Choose NWS → provide fort.22 and/or fort.221/222/wnd  
3. Align WTIMINC and start times with met file clocks  

### C. Spinup → storm (standard surge)

1. Tide spinup → fort.68  
2. Storm fort.15 IHOT + storm met + optional SWAN  
3. Copy hotstart into storm dir  

### D. Coupled waves (padcswan)

1. C + fort.26 + swaninit + padcswan + run_pads  
2. Accept fort.26 output surgery is brittle  

### E. “Science decomposition” runs (Dec22 / Dec17 style)

Same mesh era; **three parallel configs** so post can difference:

1. tides only  
2. tides + storm surge (wind)  
3. tides + storm surge + wave setup (coupled)  

Needed because **SWAN would not emit setup as a standalone `.nc`**.

---

## 10. Final boss: Dec22 vs Dec17 chaos

Evidence: `localGenerator.sh` post recipes + Unity tree names under  
`Aug29ScratchCopy/pranav_sai_uri_edu-runup/{Dec222022RunupRun,Dec172023RunupRun}/`.

### Why three parallel runs exist (the science)

**Whole point:** dissect water-level influences for runup:

| Component | Physics | How you get it |
|-----------|---------|----------------|
| **Tides** | Astronomical tide only | tides-branch fort.63 |
| **Storm surge** | Wind/pressure mean-water response (no waves) | `(tides+wind) − tides` |
| **Wave setup** | Extra mean water from waves | `(tides+wind+waves) − (tides+wind)` |

```text
tidewater   ≈  tides only
stillwater  ≈  tides + storm surge              (wind branch; padcirc-class)
water       ≈  tides + storm surge + setup      (full padcswan-class)

storm_surge ≈ stillwater − tidewater
wave_setup  ≈ water − stillwater                # proxy — SWAN never emitted setup.nc
```

**Why not one SWAN netCDF of setup?**  
Tried to get **wave setup out of SWAN as another `.nc` output.** Never worked (fort.26 / rebuild pain, same class as other extra QUANTITY fights).  
So the **only reliable setup signal is the parallel-run difference**, not a SWAN variable.

GetRunup implements this: `adcircSetup ≈ full − stillwater`, `adcircStormSurge ≈ stillwater − tidewater` (NAVD88 frame vs Stockdon SWL=0).

### Shared leaf map (both years)

| Leaf (typical) | Intended water |
|----------------|----------------|
| `forecast_RI_track` or `..._waves` | tides + storm surge + **setup** (`padcswan`) |
| `forecast_RI_track_wind` | tides + storm surge (often `padcirc`) |
| `forecast_RI_track_tides` | tides only |
| Shared `fort.14` | Napatree mesh |
| Met products | `dec22conv.nc` / `dec23wind.nc` for graphs (may ≠ model fort.221/222) |

Post also needs **wave parameters** (Hs, Dir, TMM10, TPS, rads if present) for empirical runup formulas — separate from the **setup dissection**, which is pure fort.63 differencing.

### Dec 22 2022 — cleaner story

- Explicit `forecast_RI_track_waves`  
- Parallel `_wind` / `_tides`  
- Post: `dec22conv.nc`, Runup2022* / ObsWater2022 / ObsWave2022 / Transect2022  

### Dec 17 2023 — maximum chaos

| Artifact | Meaning |
|----------|---------|
| `forecast_RI_track` vs `..._master_build` | Different binaries of “same” case |
| TMM10 from **master_build**, HS/DIR from **forecast_RI_track** | Post mixes leaves (`localGenerator` wires this) |
| `..._padcirc` / `..._padcirc_master_build` | Hydro-only stillwater comparison |
| `..._plus`, `..._tides_master_build` | More variants |
| `analysis_mybuild_1day.fort.68.nc` | Self-built hotstart |
| Multiple rebuilds | SWAN setup/output experiments that never landed |

**Intentional:** three-way water dissection (tides / surge / setup).  
**Entropy:** build zoo + mixed swan products + failed setup-as-nc quest.

**Boss clear:** explain *why* three fort.63s exist (setup proxy), not “oops duplicate runs.”

---

## 11. Self-score (game show)

| Topic | Understanding | Confidence |
|-------|---------------|------------|
| fort.14 role + BC/weir pain | Strong conceptual | High |
| fort.15 duration/NWS/tides/hotstart | Strong | High |
| Wind sourcing by NWS family | Strong for this suite’s tools | High |
| Deb spinup→storm hotstart | Strong (first-party README pattern) | High |
| Unity sbatch padc/pads | Strong pattern | Med (exact scripts live on Unity templates) |
| fort.26 + timing coupling | Solid wiki-level | Med |
| Getting extra SWAN outputs (rad stress) | **Knows why it’s hard; has not solved it** | Low-ops |
| Dec22 structure | Strong from post recipes | High |
| Dec17 multi-build chaos | Strong map of *what* and *why* | High |
| Authoring a perfect fort.14 from scratch | **No** — need mesh tools + validation | N/A |

**Verdict:** Enough to **construct / re-run kits, triage archives, and narrate Dec22/Dec17**. Not enough to claim “I fixed SWAN radiation stress output” or “I can hand-author a new fort.14 without mesh tooling.”

---

## 12. Pointers

- Wiki: https://wiki.adcirc.org/File_formats , Fort.14, Fort.15, Fort.26  
- Suite map: [what-we-use-and-need.md](what-we-use-and-need.md)  
- Archive sizes: [adcirc-swan-rerun-kit.md](adcirc-swan-rerun-kit.md)  
- Post recipes: `localGenerator.sh` (Dec22/Dec17 blocks)  
- Barrier notes: `TIMEVARYINGWIER_NOTES.txt`  
- Runup physics notes: `GetRunup.py` comments (padcswan vs padcirc)  

*Living. Update when a real fort.15 from Dec17 is frozen into the surgical kit.*
