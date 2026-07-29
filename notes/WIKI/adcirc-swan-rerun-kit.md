# ADCIRC(+SWAN) re-run kit — research synthesis (2026-07-23)

**Goal:** Know exactly what must be archived to **run** ADCIRC / ADCIRC+SWAN again, without multi-hundred-GiB dumps.  
**Drives:** surgical pull script tiers (`unity-pull-surgical-gems.sh --tier t0|t1|t2`).  
**Related:** [what-we-use-and-need.md](what-we-use-and-need.md), [unity-project-triage-inventory.md](unity-project-triage-inventory.md).

---

## Verdict (executive)

| Question | Answer |
|----------|--------|
| #1 critical? | **Run executables** (`padcirc`, `padcswan`, `adcprep`) + **configs** (Floodwater/ASGS/ecflow) + **templates/meshes** |
| Can we skip PE* / fort.63? | **Yes** — those are regenerable outputs |
| Can we skip project `ecflow_output`? | **Yes** — regenerable via Floodwater |
| Whole ManualRuns soft-exclude? | **FAIL** — still **488–664 GiB** residual (fort.221/222, multi fort.14, fort.22, json, fort.80) |
| Manageable path? | **Allowlist** re-run kits + binaries + wind lib + **final RICHAMP/graphs deliverables** (layer C). Skip raw field nc (layer B). |
| Keep all ScenarioRuns post products? | **Yes for finals** — `RICHAMP_*`, `graphs/`, `scenario_files/out/`, project RICHAMP packs. Not PE*/full fort.63. |

**Current old surgical approach (whole ManualRuns − PE/nc) fails the size contract.** Script rewritten to tiered allowlists.

### Dec22 / Dec17 science (three parallel waters)

| Run | Water meaning |
|-----|----------------|
| tides | tides only |
| wind / stillwater | tides + **storm surge** |
| full / waves | tides + storm surge + **wave setup** |

Differences: `surge ≈ stillwater − tides`, `setup ≈ full − stillwater`.  
**SWAN setup-as-nc never worked** → parallel runs are the method (see [how-to-construct-an-adcirc-run.md](how-to-construct-an-adcirc-run.md)).  
**Thesis science:** same budget underpins Napatree \(R_{2\%}\) validation — [thesis-wave-runup-crescendo.md](thesis-wave-runup-crescendo.md).

---

## How ADCIRC(+SWAN) runs (this project)

### Manual pathway (A)

1. Rundir has mesh + control + forcing + launch script  
2. `adcprep` → PE* (local, regenerable)  
3. `sbatch run_padc.sh` (ADCIRC) or `run_pads.sh` (ADCIRC+SWAN) — names from Unity templates / Deb notes  
4. Products: `fort.63.nc`, optionally `swan_*.63.nc`, …  
5. Post: **`localGenerator.sh`** → `generateGraphs.py` pointed at products  

### Floodwater / ASGS pathway (B)

1. Home **floodwater_files** + **ecflow_configs** + ASGS  
2. Orchestration produces simulation rundirs  
3. Post: **`richamp_scale_and_subset*`** (full E2E)  
4. **`ecflow_output` bulk not needed** to stand up again  

---

## Input file matrix

### ADCIRC alone — coldstart (archive these)

| Artifact | Required? | Notes |
|----------|-----------|--------|
| **`padcirc`** + **`adcprep`** | YES | From `adcirc-cg-custom-intel-unity/work/` (~6 MB each) |
| **`fort.14`** | YES | Mesh — keep **once** under Ricv1Meshes / ManualRuns/meshes |
| **`fort.15`** | YES | Control (NWS, time, tides, outputs) |
| **`fort.13`** | usually | Nodal attributes |
| **`fort.22`** | if NWS uses it | Met/track — **per golden case** |
| **`fort.221` + `fort.222`** | if OWI NWS12 | **Huge** — archive **once** in wind library, not N copies |
| **`fort.20` / fort.19 / weir** | case | Rivers / barrier timing |
| **Launch `run_padc.sh` / sbatch** | YES | From templates |
| **PE\*** | NO | `adcprep` regenerates |
| **`fort.63*`, fort.64, fort.74, fort.80, maxele\*** | NO | Outputs |
| **`fort.68.nc` hotstart** | optional | Prefer coldstart re-run for size; all `*.nc` out of kits by default |

### ADCIRC+SWAN — coldstart (add)

| Artifact | Required? |
|----------|-----------|
| **`padcswan`** (coupled binary) | YES — padcirc alone is not enough for wave-coupled cases |
| **`swaninit`** | YES |
| **fort.26 / SWAN INPUT** | YES |
| **`run_pads.sh`** (or pads sbatch) | YES |
| **`swan_*.63.nc`, rads.64.nc** | NO (outputs) |

First-party evidence of dual binaries: `GetRunup.py` comments distinguish padcirc vs padcswan still-water vs wave runs.  
External: fort.26 + swaninit required for ADCIRC+SWAN coupling (ADCIRC wiki / CCHT examples).

### Three archive layers (do not conflate)

| Layer | Purpose | Keep? |
|-------|---------|-------|
| **A. Re-run kit** | fort.14/15/scripts + binaries + configs | YES (allowlisted) |
| **B. Raw solver field outputs** | PE*, fort.63/64.nc, swan_*.63.nc full mesh fields | **NO** — too large |
| **C. Final RICHAMP deliverables + graphs** | Subset products + plots for delivery/paper | **YES** — cannot rebuild without B |

Because we **exclude B**, we **cannot** re-run `localGenerator` / `richamp_scale_and_subset` later to recreate C without multi-day re-simulations. So C is first-class archive material, not optional fluff.

### Layer C — what “final postprocess” means (this repo)

From `richamp_scale_and_subset.scr` / post_init / `README.md`:

| Deliverable | Role |
|-------------|------|
| `RICHAMP_fort63.nc` | Subset water product (not full-mesh fort.63) |
| `RICHAMP_wind.nc` | Scaled/subset wind product |
| `RICHAMP_rain.nc` | Rain product when generated |
| `RICHAMP_max_inundation.png` | Max inundation figure |
| `graphs/` | Time-series / map panels from `generateGraphs.py` |
| `Track.shp` / `.shx` / `.dbf` (and friends) | Track shapefiles for postAdditionalFiles |
| Project `RICHAMP*`, `post_output/` | Consolidated delivery packs |
| `work/.../scenario_files/out/` | Scenario post **OUTDIR** from `scenarioFileGenerator.sh` (~23 G measured) |

**Include patterns for surgical pull (layer C):**  
`RICHAMP_*`, `graphs/**`, `Track.*`, `*max_inundation*`, `post_output/`, named `RICHAMP*` packs, `scenario_files/out/`.

**Still exclude:** PE*, raw `fort.63*` / `fort.64*` / `swan_*.63*` / `rads.64*` solver dumps, fort.80, graph `*_data_file.json` intermediates.

Static post assets already in git/README (`NLCD_z0_*`, `gfs-roughness.nc`, `windgfdl`) — not scenario deliverables.

---


## Size autopsy (why soft exclude failed)

| Class | Typical mass | Policy |
|-------|-------------:|--------|
| PE* | multi-TB | **Exclude** |
| fort.63/64.nc | 13–26 GiB × many | **Exclude** |
| fort.221/222 | tens of GiB × many rundirs | **Wind library once** |
| fort.14 copies | multi-GiB × many | **Mesh library once** |
| `*_data_file.json` | multi-GiB | **Exclude** |
| fort.80 | large ASCII output | **Exclude** |
| work `scenario_files/v18Runs` | **121 G** | **Exclude** |
| work `scenario_files/out` | **23 G** | **Exclude** |
| work `scenario_files/wind` | **~1.5 G** | **Keep (T1)** |
| project `scenario_files` | **~5.6 G** | **Keep (T1) wind library** |
| Templates+meshes+README | **~5 G** | **Keep (T0)** |
| Binaries | **&lt;50 MB** | **Keep (T0) #1** |
| home floodwater | 128 M | **Keep (T0)** |
| project floodwater | 565 M | **Keep (T0)** |
| home ecflow_configs | 4.4 G | **T1** |
| home asgs full | 11 G | **T2 only** (stripped) |
| project ecflow_output | 78 G filtered | **NEVER pull** |

---

## Filtered tier sizes (measured Unity 2026-07-23)

| Component | Size | Notes |
|-----------|-----:|-------|
| Binaries (`padcirc`/`padcswan`/`adcprep`/`adcswan`/…) | **39 MB** | All present |
| ManualRuns/meshes (englandv18 + ricv1 + navd88) | **613 MB** | **v18** fort.14 ≈ 269 MB |
| Ricv1Meshes | **313 MB** | |
| `v18RunTemplate` (re-run filter) | **0.71 GiB** | |
| `v18SandyRun` (re-run filter) | **4.20 GiB** | complete wired v18 |
| `DebV18Run` (re-run filter) | **2.46 GiB** | |
| Other allowlist cases (each) | **0.1–0.6 GiB** | |
| home+project floodwater | **0.7 GiB** | |
| work wind | **1.5 GiB** | |
| project scenario_files | **5.6 GiB** | richamp.wnd dominates |
| ecflow_configs | **4.4 GiB** | |
| work scenario `out/` | **23 GiB** | post deliverables |
| post_output | **3.2 GiB** | |
| ScenarioRuns RICHAMP+graphs | **~4 GiB** | |
| All project RICHAMP* packs | **~42 GiB** | Henri variants — opt-in only |

### Tier rollups

| Tier | Predicted | Contents |
|------|----------:|----------|
| **bootstrap** | **~8–11 GiB** | Binaries + **both meshes (v18+ricv1)** + templates + **v18RunTemplate / v18SandyRun / DebV18Run** + Floodwater + work wind. **Minimum functioning coastal system.** |
| **t0** | **~5–7 GiB** | Binaries + meshes + templates + Floodwater (no full scenario) |
| **t1** | **~22–26 GiB** | + ecflow 4.4 + winds 7 + all allowlist scenarios ~7 |
| **t2** | **&lt;50 GiB** | + stripped asgs + thesis |
| **deliverables (smart)** | **~25–30 GiB** | work `out` 23 + post 3 + case graphs 4 |
| **deliverables (all RICHAMP\*)** | **~70 GiB** | too big — not default |

Login rsync ~1.5–2 MB/s: bootstrap ~1–2 h; t1 ~4–5 h; smart deliverables ~4–6 h.

### Commands

```bash
./unity-pull-surgical-tmux.sh "/Volumes/Pranav's Hard Drive" --tier bootstrap
./unity-pull-surgical-tmux.sh "/Volumes/Pranav's Hard Drive" --tier t1
./unity-pull-surgical-tmux.sh "/Volumes/Pranav's Hard Drive" --tier deliverables
```

**Bootstrap** = can run ADCIRC(+SWAN) on **v18 or ricv1**, with wired v18 cases and Floodwater configs; postprocess via this git repo after re-run. Does **not** include all ScenarioRuns products or 42 G RICHAMP packs.

Per-kit excludes: PE*, raw field nc, fort.221/222 in rundirs, graph intermediates.

---

## Open checks

1. ~~padcswan exists~~ — yes, 8.9 MB under intel-unity work  
2. fort.15 NWS mode per golden case (OWI vs fort.22) for wind coverage  
3. After bootstrap pull, smoke: `file` binaries + list fort.14/15 in v18RunTemplate  

---

## Pass/fail of prior surgical script

| Brief rule | Old script | New script |
|------------|------------|------------|
| Binaries #1 | Buried in full tree | **Explicit binary-only pack** |
| Configs | Yes | Yes (t0 floodwater; t1 ecflow) |
| No ecflow_output | Pass | Pass |
| No whole ManualRuns | **Fail** (~92–664 G) | **Allowlist only** |
| work wind only | Pulled scenario_1–7 too | **wind/ only** |
| Size &lt;50 GiB | **Fail** | **Tiered ceilings** |

---

*Research date: 2026-07-23. Prospect Brief + researcher audit + Unity size measurements from triage session.*
