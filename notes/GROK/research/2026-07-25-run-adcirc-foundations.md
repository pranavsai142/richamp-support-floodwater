# Research — `run-adcirc` foundations (2026-07-25)

**Status:** Research complete. **Skill created:** `.grok/skills/run-adcirc/` (2026-07-25).  
**Intent:** Skill family so agents can stage/configure/run manual ADCIRC(+SWAN) and hand off to postprocess (e.g. “run-adcirc latest gfs cycle”). Iterate skill + this note when real runs scar.

## North star

Not one opaque skill. A **thin orchestrator** + **specialist slices** that encode what you already do by hand: template copy → coldstart dates → `tide_fac` → met (default **306 fort.22**, with optional 221/222 or netCDF when proven) → optional fort.26 → **multi-day analysis once** → **continuous short hotstarts** → forecast → launch+monitor → post manifest.

**Runtime:** machine-local (this Mac / soon always-on box). Not Unity-as-default.

## Skill family map (implemented as orchestrator + references)

| Slice | Responsibility |
|-------|----------------|
| S0 stage | Copy `v18RunTemplate` (or named template) |
| S1 fort15-clock | base_date, RNDAY, clocks on analysis **and** forecast |
| S2 tides | `tide_fac` → FF/FACE both fort.15s |
| S3/S5 met | MetGet → drive format; **default 306 fort.22** via converters; optional 221/222 or netCDF |
| S4 MetGet | Pull GFS; “latest cycle” resolution |
| S6 waves | fort.26 dates + padcswan |
| S7 launch+monitor | Local MPI/process launch; **start + optional watch** |
| S8 hotstart + continuous analysis | Initial 5–7 d spinup → fort.68.nc; then ½ h continuations; forecast IHOT=368 |
| S9 post | Product matrix + run_manifest.json for generateGraphs |

**Mode presets:** `tides` (NWS=0 padcirc) · `wind` (306/6 + fort.22, or validated shortcuts) · `waves` (306 + fort.26 + padcswan).

## Critical contracts (gold)

### One coldstart timeline

- **Same base_date** on analysis and forecast fort.15.
- Template gold: `2018-02-23 0Z` (analysis) / `2018 02 23 0Z` (forecast) — same instant.
- RNDAY is always **days from coldstart**, not “storm length only.”
- Forecast IHOT=368 reads **fort.68.nc** from analysis (NHSTAR=3 writes it).

### tide_fac

```bash
cd CaseRoot
printf "%s\n%s\n" "$XDAYS" "$BHR $IDAY $IMO $IYR" | ./a.out   # writes ./tide_fac.out
```

- Map by **constituent name** (tide_fac order ≠ fort.15 order).
- Patch NTIF FF/FACE + NBFR FF/FACE in **both** fort.15s; leave open-boundary amp/phase alone.
- Use XDAYS = forecast RNDAY (full campaign).

### Met default = NWS=306 fort.22 (not 221/222)

```text
metget build --domain gfs 0.1 … --variable wind_pressure --format owi-ascii \
  --timestep 3600 --multiple-forecasts --output BASE
gunzip *.wnd.gz *.pre.gz
python OceanweatherTo306.py --wind …wnd --pressure …pre --output fort.22
# paste fort.22.meta → fort.15 met line; NWS=306 (padcswan) or NWS=6 (padcirc-only)
```

- ADCIRC NWS=306 = **NWS=6 rectangular fort.22** + **NRS=3 SWAN coupling**.
- Unity template fort.221/222 can be **fillers** (zeros/1010); real wind is fort.22.
- Domain must **cover entire mesh** (RI-only MetGet box is post-only, not drive).
- `get_metget_data.py` is unreliable; prefer `metget` CLI + env `METGET_*`.

### Waves fort.26

- Edit all `YYYYMMDD.HHMMSS` on INPGRID NONSTAT + COMPUTE to storm window.
- Interval 600 SEC must match fort.15 RSTIMINC when NWS has hundreds digit 3.
- swaninit usually unchanged (points at fort.26).

### Launch (Unity production)

```bash
module load uri/main intel/2021b HDF5/1.12.1-iimpi-2021b \
  netCDF-C++4/4.3.1-iimpi-2021b netCDF-Fortran/4.5.3-iimpi-2021b
ulimit -s unlimited
export FI_PROVIDER=verbs   # manual multi-node scripts
adcprep --np $SLURM_NTASKS --partmesh && adcprep --np $SLURM_NTASKS --prepall
srun $adcdir/padcirc      # analysis / wind-only
srun $adcdir/padcswan    # waves
```

- Live scripts do **not** require `--wait-all-nodes=1` / `srun --mpi=pmi2` / `I_MPI_LIBRARY` (optional hardening lore).
- Mac smoke: cmake `padcirc` only (no padcswan built yet).

### Post handoff

| Mode | Minimum products |
|------|------------------|
| water | fort.63.**nc** |
| + mesh | fort.14 |
| waves | swan_HS (+ DIR/TMM10/TPS/rads per recipe) |
| runup | full + still + tide fort.63 + mesh + waves |

- `tempDir` **must end with `/`**.
- Never pass `--fooExists false` (Python `bool("false")` is True).
- Coldstart comes from netCDF `time.units` (`Reader._parseColdStartDate` handles `0Z`).
- Emit future **`run_manifest.json`** (schema drafted in research; not implemented).

## User footgun checklist (automate later)

1. Bottom fort.15 base_date wrong / only labels changed  
2. Tides forgotten after re-date  
3. RNDAY = storm length instead of days-since-coldstart  
4. fort.26 dates not updated  
5. Met box doesn’t cover mesh  
6. Hotstart not copied; cldir.sh deleted fort.68.nc  
7. run_pads.sh still launches padcirc (waves disabled)  
8. Disk: OWI 221/222 multi-GB + PE* + fort.68 — Mac full v18 needs external disk  

## Decisions locked (2026-07-25 operator answers)

### 1. Where it runs
- **Always machine-local** for now (this Mac / soon always-on local box).
- Prepping the local stack so the skill surface is **not Unity-dependent**.
- Unity stays a reference for templates, modules lore, and historical runs — not the default backend.

### 2. Analysis length + continuous spinup (super key)
- **Analysis is typically 5–7 days prior to forecast start** (full coldstart campaign once).
- After one good multi-day analysis, the operational model is:
  - keep **analysis cycles running**
  - advance with **short hotstart continuations** (e.g. ~½ hour → ½ hour)
- That continuous-analysis chain is first-class (S8+), not “re-run 5 days every forecast.”
- One-shot spinup+storm in a single long fort.15 is possible but **not** the preferred repeatable path.

### 3. Met formats
- Proven operator path: **drive ADCIRC with 306 fort.22** when needed; converters support that.
- Converter roles:
  - MetGet owi → **OceanweatherTo306** → fort.22 for **ADCIRC**
  - 306 → owi2wind / scale_and_subset for **post viz / MetGet graph path**
- **221/222 and netCDF are desirable** if they work straight MetGet → forecast (Floodwater already uses 221/222; past failures were setup quirks).
- Skill v1 default automated path = **306 chain**; treat 221/222 and netCDF as **preferred shortcuts once validated**, not blockers.

### 4. Launch + monitor
- `run-adcirc` **kicks off** the run **and can monitor** it when desired (local process or scheduler).
- Not “stage and walk away only.”

### 5. Hotstart doctrine
- **Yes — real forecasts want a spinup.**
- Preferred: multi-day analysis once → **hotstart chain** forever after.
- Avoid “coldstart full ocean every time” as default UX.

## Session evidence

- Local v18 analysis smoke: padcirc + fort.63.nc + post graphs (flat series = short coldstart, expected).  
- Forecast hotstart path blocked mid-session by **disk full** when pulling fort.221/222 (not needed for 306).  
- Post coldstart parse fixed for `2018-02-23 0Z`.

## Session evidence (2026-07-25) — full day

### A) GFS 6h+6h ec95d shakeout

**Run:** `~/projects/adcirc-local-smoke/ec95d_gfs_6h_20260725T2144Z/`  
Coldstart 12Z → analysis RNDAY=0.25 NWS=0 → forecast RNDAY=0.50 IHOT=368 NWS=6.  
Both phases terminating normally. First **adcprep** failure fixed by NOUTM/NOUTGW.

### B) GFS 6d analysis + 5d forecast (production-shaped smoke)

**Run:** `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/`  

| Item | Value |
|------|--------|
| GFS cycle | 2026-07-25 **12Z** |
| Coldstart | 2026-07-19 12Z |
| Analysis RNDAY | **6** → fort.68.nc ~5.6M |
| Forecast RNDAY | **11** (to 2026-07-30 12Z) |
| Met | 0.25° full mesh box, **265** hourly snaps, fort.22 ~129M |
| NOUTGE | NSPOOL=360 (hourly) — whole case ~480M |
| Parallel | analysis while MetGet built |
| Result | both phases terminating normally |

### C) Post stripped for generic ADCIRC

**Dirs:** `post_analysis/graphs/`, `post_forecast/graphs/` — **30 PNGs each**.  
**Obs:** 13/13 stations with live CO-OPS data after API fix.

| Change | File / behavior |
|--------|-----------------|
| No GetObsElevation on mesh+obs | `generateGraphs.py` — only with `--generateRunup` |
| No USGS transect spam default | `Grapher.py` `BYPASS_RUNUP_TRANSECT_OVERLAYS=True` |
| Live water obs | `GetBuoyWater.py` → `api.tidesandcurrents.noaa.gov` product API |
| Stale CSV | fall through to API; do not hard-fail |

### D) Wind post (met → netCDF → obs) — same day, evening

**Dir:** `…/ec95d_gfs_5d_2026072512/post_wind/`

1. Fixed `owi2wind.py` is306 detection (`if ["Inp" in f]` was always true → broke OWI→nc).  
2. Converted MetGet `.pre`+`.wnd` → `gfs_wind.nc` (265×157×155, `wind_u`/`wind_v`).  
3. Ported `GetBuoyWind` to CO-OPS product API `product=wind` (ERDDAP mat dead, same as water).  
4. `generateGraphs --gfsExists --obsExists` → **29 PNGs**; Newport model tracks obs well.

### Scars locked (cumulative)

1. NWS≠0 requires **NOUTM/NSTAM + NOUTGW** (analysis must not have them).  
2. **tide_fac.f** native gfortran on Mac; Linux `a.out` useless.  
3. MetGet: `source ~/projects/setApiKey.sh`; package name **`metget`** in pipenv.  
4. **ec95d** = full East Coast coarse mesh; fine when v18 drive offline.  
5. Multi-day: **hourly NOUTGE** (NSPOOL=360 @ DT=10); nspool=1 is multi-GB.  
6. Analysis ∥ MetGet (analysis NWS=0 needs no fort.22).  
7. Post default = water+mesh+obs; **runup/transect/bathy is opt-in**.  
8. ERDDAP CO-OPS `.mat` dead → product API (**water + wind**).  
9. Skill + `references/proven-runs.md` updated 2026-07-25 EOD.  
10. **owi2wind is306 list bug** → OWI ASCII never converted correctly until fixed.  
11. Wind post graphs **forcing netCDF**, not fort.74, when NOUTGW=0.

### E) Waves scar — NOUTGW gates swan products (2026-07-25 evening)

**First padcswan attach** (`ec95d_gfs_5d_waves_2026072512`): NWS=306, fort.26/swaninit OK, hydro+SWAN coupled (`WAVES WILL BE COUPLED TO SWAN!`), but **no** `swan_HS.63.nc` / DIR / TMM10 / TPS / rads.

| Root cause | Detail |
|------------|--------|
| **NOUTGW=0** | `write_output.F`: `SwanHSDescript % specifier = NOUTGW` (also DIR/TPS/TMM10, rads.64, fort.74) |
| **NOUTGE≠NOUTGW** | Water uses NOUTGE; wave globals do **not** |
| **SWANOutputControl alone** | HS/DIR/…=T is necessary but **not sufficient** without NOUTGW ≠ 0 |

**Fix re-run:** `ec95d_gfs_5d_waves_noutgw_2026072512/`  
`-5 0.0 11.0000 360 !NOUTGW` matching NOUTGE. fort.16: `NOUTGW = -5`.  
Within seconds: `swan_*.nc` + `rads.64.nc` appear.

**Also:** local cmake `BUILD_PADCSWAN=ON` → `~/projects/adcirc/build/padcswan`; copy `swaninit` into PE\* after adcprep; RSTIMINC=600 on met line; Reader debug node must not hardcode 200000 on ec95d.

### F) 1 d waves + post vet + mesh threshold lore (2026-07-25 night)

**Proven run:** `…/ec95d_gfs_1d_waves_noutgw_2026072512/` — np=7, ~15 min wall, ntimes=24 on HS/DIR/TMM10/TPS/rads, post **71 PNGs** + NDBC obs (9/11 buoys with real WVHT).

| Scar / lore | Detail |
|-------------|--------|
| NOUTGW | −5 hourly required for swan products |
| Post waves | generateGraphs MWD/MWP/RAD re-enabled; no runup |
| **Closest-node threshold** | `Reader.initializeClosestNodes(thresholdDistance)` — **depends on mesh density** |
| ricv1 | high res → **small** threshold |
| v18 | mixed → **happy medium** (historical tuning); can depend on location |
| ec95d | coarse → **large** threshold or few neighbors; **series still look bad** vs obs because mesh cannot resolve coast/shelf, not only bad threshold |
| Water vs wave defaults | water often ~0.25, waves hardcoded **7** in `WaveReader` — same case can use different neighbor clouds |
| Skill implication | ec95d = **process smoke**; science station skill → ricv1/v18 |

## Next

1. Continuous analysis ½ h hotstart chain after multi-day fort.68.  
2. v18 / ricv1 when bootstrap external drive mounted (science-grade station graphs).  
3. Optional: mesh-aware or CLI `thresholdDistance` shared across Fort63/Wave/mesh readers.  
4. Keep refining CO-OPS datum (MSL vs NAVD) vs model vertical datum if comparing absolute levels.

## Researcher dig sites

- Template: Unity `…/ScenarioRuns/v18RunTemplate/{analysis,forecast}/`  
- Deb notes: Unity `…/AdcircManualRuns/README.txt`  
- Converters: `OceanweatherTo306.py`, `owi2wind.py`, `get_metget_data.py`  
- Post: `generateGraphs.py`, `Reader.py`, `localGenerator.sh`  
- Wiki: `notes/WIKI/how-to-construct-an-adcirc-run.md`, bootstrap handoffs under `notes/GROK/handoffs/`
