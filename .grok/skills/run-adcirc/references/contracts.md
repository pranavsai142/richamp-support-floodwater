# run-adcirc contracts

## Timeline (one coldstart)

```text
coldstart base_date
    │
    ├── analysis (NWS=0, IHOT=0)  [5–7 days typically; smoke may be hours]
    │       NHSTAR=3 → fort.68.nc
    │
    ├── [optional continuous] analysis hotstarts every ~½ h
    │       IHOT=368, short RNDAY, NHSTAR=3 → new fort.68.nc
    │
    └── forecast (IHOT=368, NWS=6/306)
            RNDAY = days from coldstart to storm end
            = analysis_days + forecast_storm_days
            met fort.22 aligned from coldstart through end
```

RNDAY is always **days since coldstart**, not “storm duration alone.”

## fort.15 cards

| Card | Analysis | Forecast wind |
|------|----------|----------------|
| IHOT | 0 | 368 (netCDF fort.68.nc) |
| NWS | 0 | **6** padcirc / **306** padcswan |
| base_date | same UTC | same UTC |
| NTIF/NBFR | 8 constituents | identical FF/FACE after tide_fac |
| NHSTAR | 3 + NHSINC | 0 or 3 |
| NOUTGE | −5, TOUTF≤RNDAY, NSPOOL~360 multi-day | same |
| NOUTM/NSTAM | **absent** | **required** if NWS≠0 |
| NOUTGW | **absent** | **required** if NWS≠0 |
| Met line after REFTIM | no | NWLAT NWLON WLATMAX WLONMIN WLATINC WLONINC WTIMINC |

base_date sits in the **metadata block after ITITER** (bottom of fort.15).  
Post reads coldstart via netCDF `time.units` → `Reader._parseColdStartDate` (handles `0Z`).

## fort.15 output block when NWS≠0

```text
NOUTE … / NSTAE
NOUTV … / NSTAV
NOUTM … / NSTAM     ← only if NWS≠0
NOUTGE …
NOUTGV …
NOUTGW …            ← only if NWS≠0
NHARFR …
```

Missing NOUTM/NOUTGW → adcprep: `Bad integer` after “MET Station Locations”.

## tide_fac

```bash
cd $CASE_ROOT
gfortran -O2 -o tide_fac tide_fac.f   # native Mac; never Linux a.out here
printf "%s\n%s\n" "$XDAYS" "$BHR $IDAY $IMO $IYR" | ./tide_fac
```

| Input | Meaning |
|-------|---------|
| XDAYS | **forecast RNDAY** (full campaign) |
| BHR IDAY IMO IYR | Coldstart hour, day, month, year |

Constituents fort.15 order (typical): M2 S2 N2 K2 K1 O1 P1 Q1  
`tide_fac.out` order differs — **map by name**.

Patch only **FF** and **FACE** on NTIF + NBFR. Leave open-boundary EAMP/EPHA alone.

## Met: fort.22 (NWS=6 / 306)

| NWS | Meaning | Binary |
|-----|---------|--------|
| 6 | rectangular U V P fort.22 | padcirc |
| 306 | NWS=6 + NRS=3 SWAN couple | padcswan |

**Waves products (swan_HS / DIR / TMM10 / TPS, rads.64):** specifier is **NOUTGW**, not NOUTGE.  
`NOUTGW=0` + `SWANOutputControl=T` still writes **no** wave field files. Use `-5 0.0 RNDAY 360` for multi-day netCDF. NWS=306 met line needs **RSTIMINC** (match fort.26, usually 600).
### Build chain

1. `source ~/projects/setApiKey.sh`  
2. `pipenv run metget build … --format owi-ascii --variable wind_pressure --timestep 3600 --multiple-forecasts`  
3. gunzip `.wnd` / `.pre`  
4. `pipenv run python OceanweatherTo306.py --wind … --pressure … --output fort.22`  
5. Apply `fort.22.meta` → fort.15 met line after REFTIM  
6. Units: U,V m/s; **P Pascals** (hPa×100 in converter)

### Met geometry

- lines_per_snap = NWLAT × NWLON  
- n_snaps × WTIMINC covers **coldstart → forecast end**  
- **domain covers entire fort.14 mesh**  
- fort.221/222 not required for this drive path  

### Mesh bbox examples

See **`meshes.md`** for paths/NWP/DT. MetGet pad (full mesh):

| Mesh | Rough MetGet domain |
|------|---------------------|
| ricv1 / v18 / ec95d | gfs 0.25 −100 5 −55 47 |

### Parametric met (alternate family)

See **`met-parametric.md`**. Summary:

| Item | Contract |
|------|----------|
| fort.15 line | `565 625 51.000000 -101.000000 0.083333 0.083333 3600` |
| fort.22 source | `richamp.wnd` from windgfdl (same u v P line family as OceanweatherTo306) |
| Track box | MetGet NHC download only — **never** paste into fort.15 |
| Mac | Docker linux/amd64; quiet stdout; write `/tmp` then copy |
| Manifest | `modes.wind`: `parametric_nws6` |

**Solver:** mainline `~/projects/adcirc/build/` for Floodwater ricv1 + v18 + ec95d. **adcirc-cg** only if mesh has IBTYPE 6/26 pumps (not Floodwater `ricv1_noriv_nopump`).

## Hotstart

| Action | Detail |
|--------|--------|
| Write | analysis NHSTAR=3 → `fort.68.nc` |
| Copy | `cp analysis/fort.68.nc forecast/fort.68.nc` |
| Read | forecast IHOT=368 |
| Continuous | next analysis: IHOT=368, short RNDAY, NHSTAR=3 |
| Danger | `cldir.sh` `rm *.nc` deletes hotstart |

Analysis (NWS=0) can run **in parallel with MetGet**; forecast needs fort.22 first.

## Local launch

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/netcdf/lib:/opt/homebrew/opt/netcdf-fortran/lib:/opt/homebrew/opt/hdf5/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
adcprep --np $NP --partmesh && adcprep --np $NP --prepall
mpirun -np $NP padcirc
```

Binaries: `~/projects/adcirc/build/`.  
Success: `ADCIRC terminating normally`, fort.63.nc / fort.68.nc as expected.

## Post (generateGraphs) — default stripped + wind opt-in

| Mode | Minimum | Notes |
|------|---------|--------|
| water | fort.63.nc | always (default) |
| +mesh | fort.14 | closest-node / map elevation — **not** runup ASSET bathy |
| +obs water | `--obsExists true` with water | CO-OPS water via `GetBuoyWater` (live API) |
| **wind** | owi2wind `.nc` or fort.74.nc | `--gfsExists` / `--adcircExists` / `--postExists` + `--obsExists` |
| +obs wind | with any wind flag | CO-OPS wind via `GetBuoyWind` product=wind |
| **waves** | swan_HS (+ DIR/TMM10/TPS/rads) | NDBC via `GetBuoyWaves`; needs **NOUTGW≠0** on run |
| runup | waves + still + tide + mesh + `--generateRunup true` | thesis only |

### Closest-node threshold (post interpolation)

Station values = interpolate from fort.14/netCDF nodes within `thresholdDistance` of the station (`Reader.initializeClosestNodes`). **Must scale with mesh density:**

| Mesh | Guidance |
|------|----------|
| ricv1 (dense) | **small** threshold — avoid grabbing distant nodes |
| v18 | **medium** (historical “happy medium”; location-dependent near RI vs shelf) |
| ec95d (coarse ~31k) | **large** threshold so neighbors exist; graphs still **not science-grade** at coastal gauges |

Current hardcodes (2026-07-25): water `Fort63Reader` ≈ **0.25**, waves `WaveReader` ≈ **7**, mesh maps ≈ **3**. A run can therefore post water and waves with **different neighbor sets**.  
**ec95d:** pipeline smoke only — expect poor station skill vs obs even when JSON/PNGs look populated.

```bash
# water default
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --waterExists true --water $CASE/fort.63.nc \
  --meshExists true --mesh $CASE/fort.14 \
  --obsExists true \
  --tempDir $TMP/ \
  --graphDirectory $GRAPHS/ \
  --backgroundChoice EAST_COAST_OUTLINE

# wind validation (met field → GFS schema)
pipenv run python owi2wind.py $MET/*.pre $MET/*.wnd -o $POST/gfs_wind
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --gfsExists true --wind $POST/gfs_wind.nc \
  --obsExists true \
  --tempDir $POST/wind_temp/ \
  --graphDirectory $POST/wind_graphs/ \
  --backgroundChoice EAST_COAST_OUTLINE
```

**Contracts:**

- `tempDir` trailing `/`  
- never `--flag false`  
- netCDF only  
- **Do not** call `GetObsElevation` unless `generateRunup`  
- Grapher: `BYPASS_RUNUP_TRANSECT_OVERLAYS=True` by default; log should say skipping USGS transect overlays  
- Water obs API: `…/datagetter` product=`water_level` (+ predictions)  
- Wind obs API: same host, product=`wind` (metric, GMT)  
- Local `CO-OPS_*.csv` optional for water; if missing/out-of-window → API  
- owi2wind schema: `wind_u`, `wind_v`, `lat`, `lon`, `time` minutes since 1990-01-01 (matches `GFSWindReader`)  
- owi2wind: pre then wnd; `"Inp" in` second file ⇒ 306 path only  
- Wind post validates **forcing** unless fort.74 from nonzero NOUTGW  
- Waves post needs `swan_*.nc` from **NOUTGW −3/−5** (not NOUTGE alone)  
- Mesh-aware closest-node threshold before trusting station skill (see above)

## run_manifest.json

```json
{
  "manifest_version": "s9.v1",
  "run_id": "...",
  "pathway": "A_local_run-adcirc",
  "case_dir": "/abs/path/forecast",
  "modes": {
    "water": true,
    "mesh": true,
    "waves": false,
    "wind": "gfs_nws6_fort22",
    "obs": true,
    "generate_runup": false
  },
  "products": {
    "fort63_water": ".../forecast/fort.63.nc",
    "fort63_analysis": ".../analysis/fort.63.nc",
    "fort14_mesh": ".../fort.14",
    "fort68_hotstart": ".../analysis/fort.68.nc",
    "fort22_met": ".../forecast/fort.22"
  },
  "coldstart": {
    "base_date_iso": "YYYY-MM-DDTHH:MM:SSZ",
    "base_date_raw": "...",
    "source": "fort15_base_date"
  },
  "timeline": {
    "analysis_rnday_days": 6.0,
    "forecast_rnday_days": 11.0,
    "gfs_cycle": "YYYY-MM-DD HHZ"
  },
  "post": {
    "temp_dir": "post_forecast/temp/",
    "graph_directory": "post_forecast/graphs/",
    "stations_file": "OBS_STATIONS.json",
    "background_choice": "EAST_COAST_OUTLINE",
    "obs_api": "tidesandcurrents_product_api"
  },
  "status": {
    "analysis_ok": true,
    "forecast_ok": true,
    "post_ready": true,
    "post_blockers": []
  }
}
```

## Paths cheat sheet

| Asset | Typical location |
|-------|------------------|
| **ricv1 mesh** | `…/floodwater_files/ricv1_noriv_nopump/linked_files/{ricv1_noriv_nopump.grd,ricv1_noriv_nopump_fort.13}` |
| Bootstrap v18 | `…/ScenarioRuns/v18RunTemplate/` |
| ec95d smoke | `~/projects/adcirc-local-smoke/ec95d_run/` |
| Cases | external or `~/projects/adcirc-local-smoke/` |
| Solver | `~/projects/adcirc/build/{padcirc,adcprep}` |
| Mesh card | `references/meshes.md` |
| MetGet | `source ~/projects/setApiKey.sh` |
| Converters / post | `OceanweatherTo306.py`, `owi2wind.py`, `generateGraphs.py`, `GetBuoy*` |
