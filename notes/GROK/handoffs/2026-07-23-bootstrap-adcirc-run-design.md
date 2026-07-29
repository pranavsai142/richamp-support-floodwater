# Design / runbook — Run ADCIRC(+SWAN) from the bootstrap archive

**Date:** 2026-07-23  
**Archive:** `/Volumes/Pranav's Hard Drive/unity-archive/surgical/` (~12 GiB, tier=bootstrap, exit 0)  
**Related:** `notes/WIKI/adcirc-swan-rerun-kit.md`, `notes/WIKI/what-we-use-and-need.md`, this repo root `README.md` / `README.txt`

---

## 1. Technical requirements

### R1 — Bootstrap contents (what you already have)

Root: `…/unity-archive/surgical/{home,work,project}/`

| Asset | Path (under surgical/) | Role |
|-------|------------------------|------|
| **Binaries** | `project/adcirc-cg-custom-intel-unity/work/{padcirc,padcswan,adcprep,adcirc,adcswan,hstime,aswip}` | Solver + prep (~39 MB total). **padcswan** present for coupled runs. |
| **v18 mesh pack** | `project/AdcircManualRuns/meshes/englandv18/{fort.13,fort.14,fort.15}` | Preferred mesh (~269 MB fort.14) |
| **ricv1 mesh pack** | `project/AdcircManualRuns/meshes/ricv1/…` + `project/Ricv1Meshes/…` | Second mesh / Floodwater ricv1 |
| **navd88 mesh** | `project/AdcircManualRuns/meshes/navd88/…` | Alternate |
| **Templates** | `project/AdcircManualRuns/{ManualRunTemplate,RunTemplate,FloodwaterRunTemplate}/` | Copy-from skeletons |
| **v18 cases** | `project/AdcircManualRuns/ScenarioRuns/{v18RunTemplate,v18SandyRun,DebV18Run}/` | Wired scenarios (inputs only; no PE*, no field nc) |
| **Floodwater YAML** | `home/floodwater_files/`, `project/floodwater_files/` | Path B configs (not enough alone for full ASGS without t1) |
| **Scripts/conf** | `home/scripts/`, `home/asgs_files/`, `home/{unity.h,slurm_head_unity.h,asgs-global.conf}` | Launch helpers / machine hints |
| **Wind seeds** | `work/scenario_files/wind/{scenario1,5,7}wind.txt` | Extra met library |
| **QoL** | `project/readPostUtil.py`, `readFortUtil.py`, Post_*.json | NetCDF vets / station maps |

**Typical case layout (spinup + storm):**

```text
CaseName/
  analysis/   or  a_su/     # spinup (ADCIRC-only)  → run_padc.sh
  forecast/   or  b_st/     # storm (often ADCIRC+SWAN) → run_pads.sh
```

**Inside a phase dir (what bootstrap kept):**  
`fort.13`, `fort.14`, `fort.15`, `fort.20`, `fort.22`, weir/tide files, `run_padc.sh` / `run_pads.sh`, and for wave phase: `fort.26`, `swaninit`.  
**Not kept:** PE*, fort.63/64/68.nc, fort.221/222 (OWI bulk — use wind library or regenerate), RICHAMP products, graphs.

### R2 — What still needs setup (every new Unity session / new machine)

These are **not** fully solved by the bootstrap tarball alone:

| Setup item | Why | How (rough) |
|------------|-----|-------------|
| **1. Stage to a writable work tree** | External drive / archive is for storage; runs need fast shared FS | `cp -a` surgical case → `/work/.../pranav_sai_uri_edu/…` or scratch |
| **2. Modules / MPI / NetCDF** | Binaries are dynamic ELF built for Unity Intel stack | `module load` matching original ASGS/intel-unity profile (see `custom-intel-unity*` profiles if pulled; buildinfo on Unity pointed at ASGS opt NetCDF). **Smoke:** `ldd padcswan` / short `adcprep` |
| **3. Binary on PATH or absolute path** | Templates may assume `padcirc`/`padcswan` in PATH or local copy | `export PATH=…/work:$PATH` or copy binaries into rundir; edit sbatch if needed |
| **4. PE decomposition** | PE* not archived | In phase dir: `adcprep` (interactive or scripted) for N ranks matching sbatch |
| **5. Hotstart for storm phase** | fort.68.nc stripped | After spinup completes, **copy fort.68.nc** from analysis → forecast (Deb’s workflow); or coldstart storm if fort.15 allows |
| **6. Met forcing for *new* storms** | Only case fort.22 + 3 wind txt files in library | Swap fort.22 / OWI / wnd; or MetGet via this repo’s `get_metget_data.py` (API key). fort.221/222 not in kits — pull from wind lib or regenerate |
| **7. Tide factors / dates** | fort.15 times + tidal nodal factors | Update fort.15 coldstart date/duration; re-run `tide_fac` if present (`tide_fac.f` in templates) |
| **8. Barrier / weir timing** | `time_varying_weir.in` | Edit closure times for new scenarios |
| **9. sbatch account/partition** | Scripts may hardcode old partitions | Align with current Unity (`uri-cpu`, account, time, nodes) |
| **10. Postprocess** | Products not in bootstrap | After run: point **this repo** (`localGenerator.sh` / `generateGraphs.py`) at rundir products; or Floodwater `richamp_scale_and_subset*` (needs static assets from README + MetGet env) |

### R3 — Minimal “arbitrary run” recipe

1. **Pick base:** prefer `v18RunTemplate` (clean) or `v18SandyRun` / `DebV18Run` (already storm-specific).  
2. **Copy** to work: `cp -a v18RunTemplate myNewCase`.  
3. **Choose mesh:** already embedded fort.14 in case; or replace from `meshes/englandv18` / `meshes/ricv1`.  
4. **Edit fort.15:** start/end, NWS, IHOT, outputs, barrier flags.  
5. **Edit met:** fort.22 (and wind format consistent with NWS).  
6. **Edit weir/rivers** if needed.  
7. **Spinup:** `cd analysis && adcprep && sbatch run_padc.sh`.  
8. **Hotstart:** copy fort.68.nc → forecast; set IHOT in forecast fort.15.  
9. **Storm:** `cd forecast && adcprep && sbatch run_pads.sh` (SWAN) or `run_padc.sh` (hydro only).  
10. **Post:** from richamp-support-floodwater clone, `localGenerator.sh` lines for water/waves/wind with paths into `forecast/`.

### R4 — Two meshes

| Mesh | Where in bootstrap | Use |
|------|-------------------|-----|
| **v18 (englandv18)** | `meshes/englandv18`, cases under ScenarioRuns v18* | Preferred for “arbitrary” modern runs |
| **ricv1** | `meshes/ricv1`, `Ricv1Meshes/ricv1_sea_level*` | Floodwater / sea-level / barrier packs |

### R5 — What bootstrap is *not*

- Full ASGS install + ecflow server (use `--tier t1` for ecflow_configs; t2 for home asgs tree)
- Final RICHAMP deliverables/graphs (use `--tier deliverables`)
- All ScenarioRuns / thesis ScratchCopy
- Ability to postprocess **without** re-running (no field nc, no RICHAMP_fort63)

---

## 2. User stories

### US1 — Rerun an existing bootstrap case on Unity
**As** an operator, **I can** stage `v18SandyRun` to work, load modules, adcprep, sbatch spinup then storm, **so that** I get fort.63/swan products again.

**AC:**
- Binaries load / run without missing libs  
- Spinup completes and produces hotstart  
- Storm completes with padcswan path  
- fort.63.nc (or ascii fort.63) appears in forecast  

### US2 — New storm from template
**As** a modeler, **I can** copy `v18RunTemplate`, replace fort.22 and fort.15 times, **so that** I run an arbitrary storm on v18 without rebuilding the mesh.

**AC:**
- New fort.22 consistent with fort.15 NWS  
- Tide/weir updated  
- Same sbatch path as US1  

### US3 — Postprocess after run
**As** an analyst, **I can** point this repo’s `localGenerator.sh` / `generateGraphs.py` at the new rundir, **so that** I get station graphs without Floodwater.

**AC:**
- Paths to fort.63 / swan_* / fort.14 valid  
- Graphs written under tempDir/graphDirectory  

---

## 3. Technical guidelines

1. **Never run long jobs from the external drive** — always stage to `/work` or scratch.  
2. **adcprep every time** PE* count changes or mesh changes.  
3. **Spinup → hotstart → storm** is the default manual pattern; don’t skip fort.68 copy.  
4. **padcswan** for forecast with waves; **padcirc** for spinup / pure hydro.  
5. Keep **one mesh family per case**; don’t mix v18 fort.14 with ricv1 fort.15 blindly.  
6. Secrets: `credentials.yaml` in floodwater_files — do not commit.  
7. Postprocess lives in **git** (`~/projects/richamp-support-floodwater`); bootstrap does not replace it.

---

## 4. Boilerplate / checklist (copy-paste)

```bash
# On Mac — after drive mounted
ARCHIVE="/Volumes/Pranav's Hard Drive/unity-archive/surgical"
# On Unity — after rsync/scp of needed subset to WORK
WORK=/work/pi_iginis_uri_edu/pranav_sai_uri_edu/runs
BIN=$WORK/bin   # copy padcirc padcswan adcprep here
CASE=$WORK/myNewCase

cp -a $ARCHIVE/project/AdcircManualRuns/ScenarioRuns/v18RunTemplate "$CASE"
# or: v18SandyRun / DebV18Run

export PATH="$BIN:$PATH"
# module load ...  # match Unity intel/MPI/netcdf used at build time

cd "$CASE/analysis"   # or a_su
# edit fort.15 / fort.22 as needed
adcprep                 # follow prompts / script for N cores
sbatch run_padc.sh

# after success:
cp fort.68.nc ../forecast/   # paths may vary; confirm fort.15 IHOT
cd ../forecast
# edit fort.15 hotstart + met
adcprep
sbatch run_pads.sh            # or run_padc.sh if no SWAN

# postprocess (on clone of this repo):
# edit localGenerator.sh to point --water/--waves/--mesh at $CASE/forecast
```

---

## 5. Key decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bootstrap size vs completeness | Inputs + binaries + 3 v18 cases; no field nc | Manageable ~12 GiB; re-run for products |
| Default mesh | v18 (englandv18) | User preference; ricv1 also present |
| Hotstart policy | Not archived; re-spinup | fort.68.nc too large / excluded |
| Floodwater in bootstrap | Configs only | Full ASGS/ecflow is t1/t2 |
| Postprocess | This git repo | Not duplicated in surgical pack |

## 6. PR / next-step plan (operational, not code)

1. Remount drive; confirm `surgical/` tree still ~12 GiB.  
2. Rsync bootstrap → Unity `/work/.../bootstrap` once (or subset: bin + one case + meshes).  
3. Smoke: `ldd padcswan`; adcprep on v18RunTemplate analysis with 2 ranks.  
4. Document exact `module load` lines after first successful smoke (fill gap).  
5. Optional: `--tier deliverables` if final RICHAMP graphs needed without re-run.  
6. Optional: `--tier t1` for more scenarios + ecflow_configs + full wind lib.
