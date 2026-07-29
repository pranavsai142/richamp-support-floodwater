# Proven local runs (operator evidence)

Do not treat these as the only allowed configs — they are **known-good** end-to-end smokes on this Mac.

## Shared stack

| Piece | Location / command |
|-------|-------------------|
| Solver | `~/projects/adcirc/build/{padcirc,padcswan,adcprep}` (cmake arm64) |
| MPI | Homebrew `mpirun`; ricv1/v18 prefer `np≤8`; waves often `np=4–7` |
| Mesh card | `references/meshes.md` (Floodwater ricv1 path + NWP) |
| Dylibs | `DYLD_LIBRARY_PATH` = netcdf + netcdf-fortran + hdf5 under `/opt/homebrew/opt/` |
| MetGet key | `source ~/projects/setApiKey.sh` → `METGET_API_KEY`, `METGET_ENDPOINT=https://api.metget.org` |
| MetGet CLI | `pipenv install metget` once; `pipenv run metget …` |
| tide_fac | repo `tide_fac.f` → `gfortran -O2 -o tide_fac tide_fac.f` (never Linux `a.out` on Mac) |
| Met drive | MetGet owi-ascii → `OceanweatherTo306.py` → `fort.22`, **NWS=6** padcirc / **NWS=306** padcswan |
| Work root | `~/projects/adcirc-local-smoke/` when external free; external `…/Hard Drive/adcirc-local-smoke/` if Mac disk tight |
| padcswan build | `cmake .. -DBUILD_PADCSWAN=ON` then `cmake --build . --target padcswan -j4` (~3 min; needs `thirdparty/swan`) |

## Run A — 6 h + 6 h shakeout (2026-07-25)

**Dir:** `~/projects/adcirc-local-smoke/ec95d_gfs_6h_20260725T2144Z/`

| Field | Value |
|-------|--------|
| Mesh | ec95d (~31k nodes, full East Coast box) |
| Coldstart | 2026-07-25 12Z |
| Analysis | RNDAY=0.25, NWS=0, IHOT=0, NHSTAR=3 |
| Forecast | RNDAY=0.50, NWS=6, IHOT=368 |
| Met | GFS 0.25°, −98…−59.5 E, 7.5…46.5 N, 13 hourly snaps |
| Result | both phases terminating normally |

**First scar:** forecast adcprep failed without `NOUTM`/`NSTAM`/`NOUTGW`.

## Run B — 6 d analysis + 5 d forecast (2026-07-25)

**Dir:** `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/`

| Field | Value |
|-------|--------|
| GFS cycle | 2026-07-25 **12Z** (latest with ~4 h lag) |
| Coldstart | 2026-07-19 12Z |
| Analysis | RNDAY=**6**, NWS=0 → fort.68.nc (~5.6M) |
| Forecast | RNDAY=**11** (coldstart→end), NWS=6, IHOT=368 |
| Storm window | 12Z Jul 25 → 12Z Jul 30 |
| Met | same domain 0.25°, **265** hourly snaps, fort.22 ~129M |
| NOUTGE | `-5 0.0 RNDAY 360` (hourly at DT=10 s) — multi-day disk safety |
| Parallelism | analysis launched while MetGet built (analysis needs no met) |
| Wall time | analysis ~9 min; forecast ~9 min; MetGet ~3 min |
| Case size | ~480M total (not multi-GB) |

## Post (stripped, same day)

**Dirs:** `post_analysis/graphs/`, `post_forecast/graphs/` (30 PNGs each)

```bash
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --waterExists true --water $PHASE/fort.63.nc \
  --meshExists true --mesh $PHASE/fort.14 \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $PHASE_POST/temp/ \
  --graphDirectory $PHASE_POST/graphs/
```

| Obs | Result |
|-----|--------|
| Local CO-OPS CSV | Often stale / missing → fall through |
| Live API | `api.tidesandcurrents.noaa.gov` product=water_level (+ predictions) |
| Run B analysis | **13/13** stations with data |
| Runup path | **Not** invoked — no GetObsElevation, no USGS transect spam |

## What stayed runup-only (do not enable by default)

- `GetObsElevation` / opentopography-style ASSET bathy  
- USGS beach-profile / dune SL–DT–DC transect overlays in `Grapher.py`  
- `--generateRunup true` three-water stack  

These remain in the repo for thesis work; default ADCIRC post is **water + mesh maps + CO-OPS obs**.

## Post wind (same Run B met, 2026-07-25)

**Dir:** `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_wind/`

```bash
pipenv run python owi2wind.py \
  met/gfs_ec95d_5d_00_00.pre met/gfs_ec95d_5d_00_00.wnd \
  -o post_wind/gfs_wind
# → post_wind/gfs_wind.nc  (~50M, 265×157×155, wind_u/wind_v)

pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --gfsExists true --wind post_wind/gfs_wind.nc \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir post_wind/temp/ \
  --graphDirectory post_wind/graphs/
```

| Check | Result |
|-------|--------|
| Convert | 265 snaps, exit 0 (~5 min) |
| Graphs | **29 PNGs** (speed + direction per station + all_stations + closest_points) |
| Wind obs | 10/13 stations with ~1540–1549 6-min points; Quonset/New London empty; Watch Hill non-COOPS id |
| Validation | Newport etc. model tracks obs through analysis; forecast half is future vs live obs cutoff |
| Scars fixed | `owi2wind` is306 always-true list; `GetBuoyWind` → product API |

**Note:** this is **met/GFS field** validation at stations, not ADCIRC fort.74 (NOUTGW was 0 on this run).

## Run C — waves padcswan (NOUTGW fix / 2026-07-25)

### C0 — failed product run (cancelled)

**Dir:** `…/ec95d_gfs_5d_waves_2026072512/`  
NWS=306 + fort.26 + padcswan **coupled** (hydro OK) but **NOUTGW=0** → no `swan_*.nc` / rads. Cancelled ~33%.

### C1 — NOUTGW + 1 d forecast proven (2026-07-25)

**Dir:** `/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_gfs_1d_waves_noutgw_2026072512/`

| Field | Value |
|-------|--------|
| Same clocks as Run B | coldstart 2026-07-19 12Z; attach Run B fort.68 + fort.22 |
| Storm window | **1 d**: 2026-07-25 12Z → 2026-07-26 12Z (RNDAY=7) |
| Forecast | NWS=**306**, RSTIMINC=**600**, **NOUTGW=−5 0.0 7 360**, IHOT=368 |
| Binary / np | local `padcswan`, **np=7** (~15 min wall) |
| Products | `swan_HS/DIR/TMM10/TPS.63.nc` + `rads.64.nc` + fort.63.nc — **ntimes=24** each |
| Post | `post_forecast/graphs/` — **71 PNGs** (swh/mwd/mwp/pwp/rad, no runup) |

**Scar:** `NWS=306 + SWANOutputControl ≠ swan files; NOUTGW must be −3/−5 with real spool.`  
**Note:** 7 padcswan PIDs = one MPI job with 7 ranks, not 7 runs.  
**Post quality:** pipeline OK (JSON/PNGs/obs). **Do not treat ec95d station skill as science** — coarse mesh + closest-node threshold (waves default `thresholdDistance=7` vs water `~0.25`). ricv1 → small threshold; v18 → medium; ec95d → large, but resolution still dominates error.

## Run D — Lee parametric (PWM / windgfdl) · ec95d (2026-07-28)

**Dir:** `/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_param_20230909/`

| Field | Value |
|-------|--------|
| Storm | Hurricane Lee AL13 2023 |
| Coldstart | **2023-09-09 00Z** |
| Analysis | RNDAY=**6**, NWS=0 → fort.68 (shared with Run E) |
| Forecast | RNDAY=**9** → 2023-09-18 00Z, NWS=**6**, IHOT=368 |
| Met | best track → generateParametricInput → **windgfdl** (Docker linux/amd64) → `richamp.wnd` → fort.22 |
| fort.15 domain | `565 625 51.000000 -101.000000 0.083333 0.083333 3600` |
| Result | analysis + forecast terminating normally; post 30+30+29 PNGs |
| Products | `met_pwm/richamp.wnd` (~2.2G), `lee_parametric_wind.nc` (~185M), `track.richamp`, `run_manifest.json` |

**Scars:** (full recipe → `met-parametric.md`)
1. Never host-redirect windgfdl stdout (WSMAX spam → multi-GB log). Write in container `/tmp`, copy out once (~8.5 min for 216 snaps under qemu).
2. Use **NHC best track**, not advisory-036 OFCL merge (late RMW=0 → ambient wind at NE impact).
3. BEST ATCF has hours=0 on every line → `generateParametricInput` writes Wind_Inp hours=0; set campaign duration manually.
4. `haversine` required for generateParametricInput (pipenv).
5. **Post-ET domain blow-up** ~Sep 17 00–04Z: ~99% of basin >15 m/s, max on SW corner ~70 m/s while center near NS — station “spike to 35 m/s everywhere” is **not** local TC; prefer science window through ~Sep 16 20Z.
6. Early station zeros = PWM far-field (normal), not a broken reader.

## Run E — Lee GFS dual (same clocks) · ec95d (2026-07-28)

**Dir:** `/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_gfs_20230909/`

| Field | Value |
|-------|--------|
| Same clocks as Run D | coldstart 2023-09-09 00Z; RNDAY 6 / 9 |
| Met | MetGet GFS 0.25° −98…−59.5 / 7.5…46.5, historical 2023-09-09→18 |
| fort.22 | ~111M, P in Pascals |
| Result | terminating normally; post water+wind graphs |
| Case size | ~474M |

**Dual purpose:** parametric vs GFS met comparison on identical mesh/clocks for house fixtures.
