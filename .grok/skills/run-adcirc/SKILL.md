---
name: run-adcirc
description: >
  Stage, configure, launch, optionally monitor, and postprocess local manual ADCIRC(+SWAN)
  runs. Meshes: ricv1 (Floodwater skill/obs — preferred when named), v18, ec95d smoke.
  Phrases like "ricv1 latest gfs" → wind + latest GFS cycle + full pipeline. Covers
  tides/wind/waves, MetGet fort.22, hotstart chains, stripped post (water+wind obs;
  runup opt-in). Use for /run-adcirc, "run-adcirc ricv1 latest gfs", "kick off ADCIRC", etc.
---

# /run-adcirc — Local Manual ADCIRC Orchestrator

You are running **pathway A: manual ADCIRC** on the **local machine** (this Mac / soon always-on box).  
Unity is a **template/lore reference only**, not the default launch backend.

**This is a skill family glued by one entry point.** Do not invent fort.15 physics. Follow contracts.  
When something fails in the real world, **fix this skill and/or** `notes/GROK/research/2026-07-25-run-adcirc-foundations.md` with the scar.

**Proven:** `references/proven-runs.md`.  
**Meshes (progressive load):** parse alias → read **only** `references/mesh-<alias>.md` (index: `meshes.md`). Do not load all mesh cards.

## Mandatory reads (first time in a session)

1. After parse: **one** of `mesh-ricv1.md` / `mesh-v18.md` / `mesh-ec95d.md`  
2. `references/contracts.md` + `references/checklist.md` (shared pipeline)  
3. If **met=parametric**: `references/met-parametric.md` (do not improvise windgfdl)  
4. `references/proven-runs.md` only if repeating a known path  
5. Research note only on new scars

## Parse the user request

**Shorthand that must just work:**

| User says | Infer |
|-----------|--------|
| `ricv1 latest gfs` | mesh=**ricv1**, mode=**wind**, forecast_start=**latest GFS**, analysis 6 d, forecast 5 d, post water+wind+obs |
| `ec95d …` / smoke | mesh=ec95d, same clocks defaults |
| `v18 …` | mesh=v18 (warn multi-day wall time on Mac) |
| `waves` | mode=waves only if padcswan available |
| `parametric lee` / `lee parametric` | met=**parametric**, storm=**Lee AL13 2023**, clocks from handoff; **not** MetGet GFS drive |

Extract (infer defaults when missing; **state them once**):

| Parameter | Default | Notes |
|-----------|---------|--------|
| **mode** | `wind` | `tides` · `wind` · `waves` |
| **template / mesh** | **ricv1** if named/implied skill; else v18 if drive; else ec95d | see `meshes.md`; never mix families |
| **forecast_start** | user / “latest GFS cycle” | UTC |
| **analysis_days** | **6** (range 5–7; user may shorten for smoke) | days **before** forecast start |
| **forecast_days** | 5 | storm window after forecast_start; forecast **RNDAY** = analysis_days + forecast_days |
| **met** | GFS via MetGet **or** `parametric` (NHC/PWM/windgfdl) | fort.22 NWS=6 (padcirc) or 306 (padcswan); parametric → fort.15 domain **565×625 PWM box** — see S3p handoff |
| **met_res** | 0.25° multi-day | domain covers full mesh (`meshes.md`) |
| **work_root** | external `…/adcirc-local-smoke/` if free &lt;~15 GB else `~/projects/adcirc-local-smoke/` | |
| **np** | **min(8, ncpu)** ricv1/v18; min(4,ncpu) ec95d | match adcprep |
| **nspool_ge** | hourly: **14400** @ DT=0.25 (ricv1/v18); **360** @ DT=10 (ec95d) | never nspool=1 multi-day |
| **monitor** | true if user wants watch | else launch + how to monitor |
| **post** | true | water + mesh + obs; **wind post when met present**; runup off |
| **analysis_mode** | `auto` | coldstart · continue · attach fort.68 |

### “latest GFS cycle”

1. Resolve current UTC; subtract ~4 h lag; pick latest 00/06/12/18Z MetGet can fill.  
2. Forecast window: cycle start → cycle start + forecast_days.  
3. Coldstart / analysis begin: **forecast_start − analysis_days**.  
4. **State the window explicitly** before mutating fort.15.  
5. Met pull window: **coldstart → forecast end** so fort.22 indexes correctly after hotstart.

### Continuous analysis (super key)

After one successful multi-day coldstart analysis:

- Prefer **½ hour (or similar) hotstart continuations** instead of re-running 5–7 days.  
- Keep a durable analysis rundir with latest `fort.68.nc`.  
- Forecasts **attach** that hotstart (`IHOT=368`).

Do **not** default to “coldstart the whole ocean every forecast.”

### Parallelism (proven)

**Analysis is NWS=0** — it does not need fort.22.  
After clocks + tides are set: **start MetGet in parallel with analysis** (or start analysis first if MetGet is slow). Attach fort.22 + met line before forecast adcprep only.

---

## Ordered execution pipeline

Use `todo_write` for multi-step runs. Execute in order; stop on failed gate with diagnosis.

### S0 — Stage case

1. Resolve mesh alias → load **only** that `mesh-*.md` card; stage from paths there. Gate fort.14 title per card.  
2. Copy fort.13/14 (+ fort.15 template, fort.20, TVW file if card says so) into `$WORK/$RUN_ID/{analysis,forecast}/`.  
3. **NWP names in fort.15 = fort.13 exactly** (per mesh card).  
4. Copy repo `tide_fac.f` / native `tide_fac` into case root.  
5. Disk: prefer external if free &lt; ~15 GB; nspool=1 multi-day = multi-GB.  
6. Record `run_id`, paths, stated time window.

### S1 — fort.15 clocks

For **both** analysis and forecast:

1. Set **base_date / coldstart metadata** (bottom fort.15 after ITITER) to the **same** UTC instant.  
2. Set **RNDAY**:
   - analysis: `analysis_days`
   - forecast: **analysis_days + forecast_days** (days since coldstart to storm end)
3. Mode cards:
   - analysis: `IHOT=0`, `NWS=0`, `NHSTAR=3` + NHSINC (e.g. 2160 @ DT=10 ≈ 6 h)
   - forecast wind: `IHOT=368`, `NWS=6` (padcirc) or `306` (padcswan)
4. **NOUTGE**: `-5 0.0 RNDAY NSPOOL` hourly (NSPOOL from mesh DT — see meshes.md). TOUTF ≤ RNDAY. NSCREEN large (e.g. hourly), not every step.  
5. DRAMP: ~0.5 d multi-day; short smoke 0.01.  
6. **Never** change only RUNDES/RUNID labels and call it re-dated.  
7. ricv1: keep `&TVWControl` if template has it; do not invent barrier schedules unless user asks.

### S1b — fort.15 output cards when NWS≠0 (adcprep footgun)

Flipping NWS from 0 → 6/306 **without** met output cards → adcprep dies:

`Bad integer` near “MET Station Locations Contained in fort.15”.

After `NOUTV` / `NSTAV`, **insert** (forecast only):

```text
0 0.0 0.0 0   !NOUTM
0               !NSTAM
```

After `NOUTGV`, **insert** NOUTGW:

```text
# wind-only (no SWAN field products needed): card present for adcprep
0 0.0 0.0 0   !NOUTGW
# waves (padcswan): ENABLE — SWAN globals + rads + fort.74 follow NOUTGW
-5 0.0 RNDAY 360 !NOUTGW netcdf4 hourly
```

Analysis (`NWS=0`) must **not** have these cards.

Met grid line sits **after REFTIM, before RNDAY**:

```text
# NWS=6 (padcirc):
NWLAT NWLON WLATMAX WLONMIN WLATINC WLONINC WTIMINC
# NWS=306 (padcswan): add RSTIMINC (match fort.26 COMPUTE interval, usually 600)
NWLAT NWLON WLATMAX WLONMIN WLATINC WLONINC WTIMINC RSTIMINC
```

### S2 — Tides (`tide_fac`)

```bash
cd $CASE_ROOT   # tide_fac.f lives in repo root; copy into case
# Mac: Linux a.out will NOT run — always compile native:
gfortran -O2 -o tide_fac tide_fac.f
printf "%s\n%s\n" "$XDAYS" "$BHR $IDAY $IMO $IYR" | ./tide_fac
# XDAYS = forecast RNDAY (full campaign); start = coldstart hour day month year
```

- Map `tide_fac.out` by **constituent name** (order ≠ fort.15 / ≠ print order).  
- Patch **FF and FACE only** in NTIF + NBFR of **both** fort.15s.  
- Do **not** touch open-boundary amp/phase tables.  
- Gate: analysis FF/FACE == forecast FF/FACE.

### S3/S4/S5 — Meteorology (default fort.22)

#### S3p — Parametric / NHC (PWM · windgfdl) — alternate met family

**Not the default.** Full recipe lives in **`references/met-parametric.md`** (progressive load — only when met=parametric).  
Proven: **Run D** Lee ec95d dual (`proven-runs.md`).

When user asks for **parametric** met (e.g. `/run-adcirc parametric lee`):

1. **Read** `references/met-parametric.md` before mutating fort.15 or launching Docker.  
2. **Drive:** best track (prefer) → `generateParametricInput` → **`windgfdl` in Docker** → `richamp.wnd` → `forecast/fort.22`.  
3. **fort.15 met line (PWM basin — never MetGet track box):**  
   `565 625 51.000000 -101.000000 0.083333 0.083333 3600`  
4. **Mac windgfdl:** write in container `/tmp`, **stdout → /dev/null**, copy `.wnd` out once (host log redirect = multi-GB WSMAX spam).  
5. **BEST track:** rewrite `Wind_Inp` NHOURS manually (ATCF hours field is 0 → generator writes 0). Need `haversine` in pipenv.  
6. **Gate:** P in Pascals; spot domain max near track (not SW corner only); watch post-ET domain blow-up.  
7. **Post:** `owi2wind.py richamp.wnd Wind_Inp.txt` then `--gfsExists` graphs; optional scale_and_subset `-parametric true`.  
8. Env names: `TC_FORCING`, `PARAMETRIC_WIND`, `RICHAMP_TC_FORCING` — not `USE_TC_FORCING`. post_init does **not** auto-call generateParametricInput.

**Operator-proven drive path (local padcirc) — default GFS:**

```bash
source ~/projects/setApiKey.sh   # METGET_API_KEY + METGET_ENDPOINT
# pipenv install metget  # once in repo
export PATH="$(cd <repo> && pipenv --venv)/bin:$PATH"   # or: pipenv run metget …

# Domain: full mesh bbox (meshes.md; East Coast pad e.g. -100 5 -55 47)
metget --apikey "$METGET_API_KEY" --endpoint "$METGET_ENDPOINT" build \
  --domain gfs 0.25 $LONMIN $LATMIN $LONMAX $LATMAX \
  --start 'YYYY-MM-DD HH:MM' --end 'YYYY-MM-DD HH:MM' \
  --variable wind_pressure --format owi-ascii --timestep 3600 \
  --multiple-forecasts --compression --strict \
  --output $METBASE --output-directory $METDIR \
  --check-interval 20 --max-wait 3

gunzip -fk ${METDIR}/${METBASE}*.wnd.gz ${METDIR}/${METBASE}*.pre.gz
pipenv run python OceanweatherTo306.py \
  --wind  ${METDIR}/${METBASE}*_00.wnd \
  --pressure ${METDIR}/${METBASE}*_00.pre \
  --output $FORECAST/fort.22
# Paste fort.22.meta → forecast fort.15 met line; NWS=6 (padcirc) or 306 (padcswan)
```

**Rules:**

- Domain must **cover entire fort.14 mesh** (not RI-only post boxes).  
- Snaps from **coldstart through forecast end** (hotstart time indexes into fort.22).  
- P in **Pascals** in fort.22 (converter multiplies hPa×100).  
- Prefer `metget` CLI over `get_metget_data.py` (fragile / SyntaxError).  
- fort.221/222 **not required** for NWS=6/306 drive.

### S6 — Waves (mode=waves only)

1. **padcswan** required for NWS=306. If missing → NWS=6 wind-only.  
   Build: `cmake .. -DBUILD_PADCSWAN=ON && cmake --build . --target padcswan -j4`  
   (`thirdparty/swan` present; Unity `padcswan` is Linux ELF — not for Mac).  
2. Retarget all fort.26 NONSTAT + COMPUTE stamps to forecast/storm window.  
3. 600 SEC ↔ **RSTIMINC** (8th field on met line when NWS has hundreds digit 3):  
   `NWLAT NWLON WLATMAX WLONMIN WLATINC WLONINC WTIMINC RSTIMINC`  
4. **NOUTGW must be −3/−5 with real spool** — not `0`.  
   SWAN global fields (`swan_HS`, `swan_DIR`, `swan_TMM10`, `swan_TPS`, `rads.64`) use  
   **`NOUTGW`** in `write_output.F` (`SwanHSDescript % specifier = NOUTGW`), **not NOUTGE**.  
   `SWANOutputControl HS/DIR/…=T` is necessary but **not sufficient**.  
   Match NOUTGE for multi-day: `-5 0.0 RNDAY 360` (hourly @ DT=10).  
5. After adcprep: **copy `swaninit` into each PE\*** (prep distributes fort.26 only).  
6. Launch `mpirun -np $NP padcswan` (not padcirc).  
7. Gate: `swan_HS.63.nc` (and ideally DIR/TMM10/TPS) exist with `ntimes > 0`.

### S8 — Hotstart chain

**Coldstart analysis:**

1. IHOT=0, NWS=0, NHSTAR=3  
2. adcprep + padcirc  
3. Gate: `analysis/fort.68.nc` + `ADCIRC terminating normally`

**Forecast attach:**

```bash
cp analysis/fort.68.nc forecast/fort.68.nc
# forecast fort.15: IHOT=368; fort.22 + met line + NOUTM/NOUTGW present
```

**Continuous analysis:** IHOT=368, short RNDAY, NHSTAR=3; never `cldir.sh` `rm *.nc` without restore.

### S7 — Launch + monitor (local)

| Role | Paths |
|------|--------|
| padcirc/adcprep | `~/projects/adcirc/build/` |
| padcswan | only if built |

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/netcdf/lib:/opt/homebrew/opt/netcdf-fortran/lib:/opt/homebrew/opt/hdf5/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
export PATH="$ADCDIR:$PATH"
cd $PHASE_DIR
adcprep --np $NP --partmesh && adcprep --np $NP --prepall
mpirun -np $NP padcirc
```

Success: `ADCIRC terminating normally`, MPI 0, fort.63.nc / fort.68.nc as expected.  
Do not Unity sbatch unless user asks.

### S9 — Postprocess (stripped default + optional wind)

Default post is **generic ADCIRC**: model water + station maps + **live CO-OPS water obs**.  
**Not** runup/transect/ASSET bathy (thesis path only).  
**Wind** is a first-class optional post leg (met field validation), not the water default.

```bash
cd <repo richamp-support-floodwater>
# per phase (analysis and/or forecast) — water:
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --waterExists true --water $PHASE/fort.63.nc \
  --meshExists true --mesh $PHASE/fort.14 \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $POST/$PHASE/temp/ \
  --graphDirectory $POST/$PHASE/graphs/ \
  --prefix "${RUN_ID}_${PHASE}_"
```

#### S9e — Coastal fieldpack for the suite viz (optional, proven 2026-07-25)

Interactive inspection lives in the suite shell; `generateGraphs` stays for print.

```bash
cd <repo richamp-support-floodwater>
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir $PHASE --mesh $PHASE/fort.14 --case $CASE \
  --products mesh,water,wind,waves,stations,obs_water \
  --temp-dir $CASE/products/_export_temp \
  --outdir $CASE/products/fieldpack
# gate
PYTHONPATH=. pipenv run python -m post.export.verify_pack $CASE/products/fieldpack \
  --source-check --rundir $PHASE --mesh $PHASE/fort.14
# open
ln -sfn $CASE/products/fieldpack ~/projects/CloudVision/threejs-shield-live-viz/data/coast
cd ~/projects/CloudVision/threejs-shield-live-viz && ./serve.py 3412
```

`--products` takes any adapter (`--list-products`). `--post-stride N` is required
before the multi-GB RICHAMP wind is exported, and the stride is recorded in the
pack. Contract: `post/export/ADCIRC_FIELDPACK_V0.md`.

#### S9b — Wind graph + CO-OPS wind obs (proven 2026-07-25)

Met drive stays **fort.22 NWS=6**. For **post**, convert MetGet OWI → GFS-schema netCDF, then graph:

```bash
# 1) OWI ASCII → netCDF (wind_u / wind_v / lat / lon / time minutes since 1990)
#    pre file first, then wnd. Do NOT pass Wind_Inp here (that is 306 path).
pipenv run python owi2wind.py \
  $METDIR/${METBASE}*_00.pre \
  $METDIR/${METBASE}*_00.wnd \
  -o $POST/wind/gfs_wind
# writes $POST/wind/gfs_wind.nc  (~50M for 0.25° full-mesh 11d hourly)

# 2) Station series + live wind obs
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --gfsExists true \
  --wind $POST/wind/gfs_wind.nc \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $POST/wind/temp/ \
  --graphDirectory $POST/wind/graphs/ \
  --prefix "${RUN_ID}_wind_"
```

| Flag | Reader | Input schema |
|------|--------|--------------|
| `--gfsExists` | `GFSWindReader` | `wind_u`, `wind_v`, `lat`, `lon`, `time` minutes (owi2wind output) |
| `--adcircExists` | `Fort74Reader` | fort.74.nc `windx`/`windy` (needs **NOUTGW** ≠ 0 on run) |
| `--postExists` | `PostWindReader` | RICHAMP `spd`/`dir` under `/Main` (scale_and_subset) |

**Wind rules:**

- `owi2wind` is306 detection must be real `"Inp" in filename` (list-literal bug fixed 2026-07-25).  
- `GetBuoyWind` uses NOAA product API `product=wind` (same host as water); ERDDAP `.mat` is dead.  
- Obs dir is met-from +90° to match `Grapher.vectorDirection(atan2(-v,u))`.  
- Not every NOS station has wind (Quonset/New London often empty; USGS-style IDs fail).  
- This validates **forcing**, not ADCIRC response wind (fort.74) unless NOUTGW enabled.  
- Full-domain 265-snap convert ~5 min on Mac; output ~50 MB compressed.

**Water rules (unchanged):**

- netCDF fort.63 only (`NOUTGE` −3/−5).  
- `tempDir` **must end with `/`**.  
- Never `--fooExists false` (`bool("false")` is True).  
- **Do not** pass `--generateRunup` unless user asks for runup stack.  
- Obs: `GetBuoyWater` product API; local CO-OPS CSVs optional/stale.  
- Expect log: `Skipping USGS beach-profile / transect overlays (generic ADCIRC post)`.  
- Gate: PNG count &gt; 0; obs JSON has `n_times &gt; 0` for most stations when dates are real.

**Runup opt-in only:** `--generateRunup true` + waves + still/tide water → `GetObsElevation` + transect overlays (`BYPASS_RUNUP_TRANSECT_OVERLAYS` off when ASSET/RUNUP present).

#### S9c — Waves graph + NDBC obs (proven 2026-07-25)

```bash
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --wavesExists true \
  --waveswh $CASE/swan_HS.63.nc \
  --wavemwd $CASE/swan_DIR.63.nc \
  --wavemwp $CASE/swan_TMM10.63.nc \
  --wavepwp $CASE/swan_TPS.63.nc \
  --waverad $CASE/rads.64.nc \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $POST/temp/ \
  --graphDirectory $POST/graphs/ \
  --prefix "waves_"
# Do NOT pass --generateRunup for product vet
```

Gate: `swan_*.nc` ntimes &gt; 0; station JSON 24/hourly frames; PNGs for swh/mwd/mwp/pwp/rad; NDBC obs for buoys that report WVHT (not every NDBC id has waves).

#### S9d — Closest-node threshold vs mesh density (critical for post quality)

`Reader.initializeClosestNodes(..., thresholdDistance, …)` selects mesh nodes near stations for **interpolation**. Units are the same lon/lat degree-ish distance used in the search (see `Reader.py`). **Hardcoded per product path today** — not auto mesh-aware:

| Reader path | Current default | Notes |
|-------------|-----------------|-------|
| `Fort63Reader` (water) | **0.25** | tighter — ok on dense coastal mesh |
| `WaveReader` (waves) | **7** | much looser — needed so coarse meshes still get neighbors |
| `Fort14Reader` (mesh maps) | **3** | |
| GFS wind/rain | **20** | met grid, not fort.14 |

**Mesh guidance (operator lore):**

| Mesh | Density | Threshold guidance |
|------|---------|-------------------|
| **ricv1** | high coastal res | **small** threshold — large radius grabs far nodes and smears local physics |
| **v18 / england** | mixed; fine near RI, coarser offshore | **happy medium** (historical tuning sat here); may need location-aware values |
| **ec95d** | coarse full East Coast (~31k nodes) | **large** threshold or stations find few/no neighbors; even with a hit, series can look **physically bad** |

**Do not over-read ec95d station graphs as science.** Post can “work” (JSON + PNGs + obs overlay) while model-at-station values are poor because:

1. Coarse mesh cannot resolve harbors / barriers / local shelf waves.  
2. Threshold may differ between water (0.25) and waves (7) in the same case — water and wave station nodes need not match.  
3. A large threshold that “finds nodes” still interpolates from distant open-ocean nodes.

When validating against buoys/CO-OPS for real skill, prefer **ricv1 / v18** (or other coastal-res meshes). Treat **ec95d as process/smoke** (pipeline, NWS, NOUTGW, obs plumbing), not coastal accuracy.

Future: mesh-aware or CLI `--thresholdDistance` shared across water/wave/mesh readers. Until then, edit `Reader.py` Fort63/Wave/mesh thresholds before science posts.

Write `$WORK/run_manifest.json` (see contracts).

---

## Preflight gates (fail closed)

See `references/checklist.md`. Minimum:

- [ ] analysis.base_date == forecast.base_date  
- [ ] tides FF/FACE both fort.15s  
- [ ] RNDAY analysis = days to forecast start; forecast RNDAY = coldstart → end  
- [ ] forecast: NWS=6/306, NOUTM/NSTAM, NOUTGW, met line, fort.22  
- [ ] met domain covers mesh; snaps cover full campaign  
- [ ] forecast fort.68.nc + IHOT=368  
- [ ] disk + NSPOOL sensible  
- [ ] NP matches adcprep  

---

## Modes quick card

| Mode | Analysis | Forecast | Binary |
|------|----------|----------|--------|
| **tides** | NWS=0 | optional NWS=0 | padcirc |
| **wind** | NWS=0 → fort.68 | NWS=6 + fort.22 | padcirc |
| **waves** | same | NWS=306 + fort.26 | **padcswan** |

---

## Footguns (do not relearn the hard way)

1. Bottom fort.15 base_date wrong / only labels changed  
2. Tides forgotten after re-date  
3. RNDAY = storm length instead of days-since-coldstart  
4. fort.26 dates not updated  
5. Met box too small (RI post box on full mesh)  
6. Hotstart missing; cldir deleted fort.68.nc  
7. run_pads still launches padcirc while NWS=306  
8. Disk full mid OWI / PE* / fort.68  
9. Short smoke RNDAY → flat water graphs (expected)  
10. Using smoke fort.15 as gold without NOUTM/NOUTGW when NWS≠0  
11. **NWS≠0 without NOUTM/NSTAM + NOUTGW** → adcprep `Bad integer`  
12. **Linux `a.out` tide_fac on Mac** → compile `tide_fac.f`  
13. MetGet: `source ~/projects/setApiKey.sh`; `pipenv run metget` (package `metget`)  
14. **NOUTGE nspool=1 on multi-day** → multi-GB fort.63; use ~hourly  
15. **Post with mesh+obs used to call GetObsElevation + USGS transects** — stripped; only with `--generateRunup`  
16. **Obs ERDDAP `.mat` endpoint dead** — use NOAA product API in `GetBuoyWater` **and** `GetBuoyWind`  
17. Waiting on MetGet before analysis — analysis can run in parallel (NWS=0)  
18. **`owi2wind` is306 bug** — `if ["Inp" in f]` is always true; must be `if "Inp" in f` or OWI→nc is broken  
19. Wind post graphs **met field** (owi2wind), not fort.74, unless NOUTGW was nonzero  
20. **NWS=306 + SWANOutputControl ≠ swan_*.nc files** — `NOUTGW` must be −3/−5 with real spool (SWAN HS/DIR/TPS use NOUTGW, not NOUTGE)  
21. **adcprep does not copy swaninit** into PE\* — copy after prepall  
22. **Reader wave debug node 200000** OOBs on ec95d (~31k nodes) — use `min(200000, nnodes-1)`  
23. **Closest-node `thresholdDistance` is mesh-density dependent** — large for ec95d, small for ricv1, medium for v18; water vs wave currently use different hardcodes (0.25 vs 7).  
24. **ec95d station series can look “bad” even when post succeeds** — coarse mesh + far neighbors, not only a NOUT/SWAN bug. Science graphs → ricv1/v18.  
25. **N MPI padcswan PIDs = one job** (`mpirun -np N`), not N separate runs.  
26. **Deb `ec95_v18_weirpumps` ≠ Floodwater ricv1** — wrong fort.14; IBTYPE 26 needs adcirc-cg, Floodwater ricv1 does not.  
27. **ricv1 NWP** must be the 4 fort.13 names only (no `sea_surface_height_above_geoid`).  
28. **TVW times are days-since-coldstart** — stock day-16 close never fires on RNDAY=11 unless retimed.  
29. **np=4 default was too timid** for ricv1/v18 — use up to 8 cores on this Mac.  
30. **`elev_stat.151` / “External File Used for Elevation Station Locations”** on noriv_nopump — almost always **extra `NFFR` line** after ANGINN. Mesh has no flux IBTYPE (2/12/22), so `presizes` does **not** read NFFR; the `0 ! NFFR` line is consumed as NOUTE and the next value (`-5` from NOUTE) is read as **negative NSTAE** → elev_stat.151. **Fix: omit NFFR when fort.14 has no flux BCs.** Deb weirpumps templates include NFFR because they have IBTYPE 22.  
31. **Parametric:** host-redirect windgfdl stdout → multi-GB log / multi-hour wall; write `/tmp` in Docker, quiet stdout (`met-parametric.md`).  
32. **Parametric:** BEST ATCF → Wind_Inp hours=0 unless you set NHOURS manually.  
33. **Parametric:** advisory OFCL merge can zero late RMW; prefer **best track** for historical goldens.  
34. **Parametric:** early station zeros are PWM far-field (normal); **same-hour spike at all stations** = domain blow-up — do not trust as local TC.  
35. **Parametric:** MetGet `nhc-…-000` may reject advisory 0; use real advisory id or ATCF file.

---

## After a run (iteration duty)

1. Append scars to `notes/GROK/research/2026-07-25-run-adcirc-foundations.md` or dated research note  
2. Patch this `SKILL.md` / `references/*`  
3. Update `references/proven-runs.md` if a new config is proven  
4. Tell the user what changed  

---

## Out of scope (unless user asks)

- Floodwater / ASGS / ecflow as primary path  
- Unity sbatch as default  
- Runup three-water stack as default post  
- Claiming 221/222 or netCDF drive works without a successful local smoke  

## References

- `references/meshes.md` — index only; then `mesh-ricv1.md` / `mesh-v18.md` / `mesh-ec95d.md`  
- `references/contracts.md` — clocks, met, hotstart, post, manifest  
- `references/checklist.md` — printable gates  
- `references/proven-runs.md` — known-good local cases (Run D/E = Lee parametric + GFS dual)  
- `references/met-parametric.md` — **S3p only** (track → windgfdl Docker → fort.22, scars)  
- `notes/GROK/research/2026-07-25-run-adcirc-foundations.md`  
- `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
- `post/export/ADCIRC_FIELDPACK_V0.md` — coastal fieldpack (S9e)  
- Repo: `OceanweatherTo306.py`, `owi2wind.py`, `generateGraphs.py`, `GetBuoy*`, `tide_fac.f`, `generateParametricInput.py`, `windgfdl`, `scale_and_subset.py`
