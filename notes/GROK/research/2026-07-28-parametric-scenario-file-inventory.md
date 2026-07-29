# Research — Parametric-forced scenario file inventory (Lee golden, 2026-07-28)

**Mission:** Record **exactly what a completed parametric ADCIRC campaign produces** so house-viz integration maps real paths, not hypothetical Milton stubs. Also record the **paired GFS Lee case** as the first dual-scenario compare fixture.

**Campaign SoT:** `/Volumes/Pranav's Hard Drive/adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md`  
**Cases:**

| Role | Path | Size (order) |
|------|------|----------------|
| **Parametric** | `…/ec95d_lee_param_20230909/` | ~4.7 G (fort.22 + richamp.wnd dominate) |
| **GFS twin** | `…/ec95d_lee_gfs_20230909/` | ~474 M |

**Shared clocks:** coldstart **2023-09-09 00Z**, analysis RNDAY=6, forecast RNDAY=9 → end **2023-09-18 00Z**, mesh **ec95d**, NWS=6 both.

---

## 1. Parametric case tree (authoritative)

```text
ec95d_lee_param_20230909/
  run_manifest.json                 # modes.wind=parametric_nws6, track=true, storm Lee AL13
  analysis/
    fort.14 fort.15 fort.63.nc fort.67.nc fort.68.nc maxele.63.nc
    PE*/
  forecast/
    fort.14 fort.15 fort.22 (~2.2G) fort.63.nc fort.68.nc maxele.63.nc
    PE*/
  met_pwm/                          # PWM generation workspace (keep)
    lee_best_track.trk              # BEST track used for drive (not OFCL merge)
    nhc_merge_2023_al_13_036.trk    # advisory merge (scar: late RMW=0 — not used for drive)
    nhc_btk_2023_al_13.btk
    nhc_fcst_2023_al_13_036.fcst
    track.richamp                   # PWM input geometry/time
    Wind_Inp.txt                    # 216 h, basin −101…−49 / 4…51, 12. → 1/12°
    Wind_Inp.note                   # coldstart-trimmed hours note
    TrackRMW.txt
    diag_parm.nml
    windgfdl                        # binary copy used for run
    richamp.wnd                     # ~2.2G raw 306 grid (u v p)
    lee_parametric_wind.nc          # ~185M owi2wind product (house-ready)
    RICHAMP_rain.nc                 # parametric rain
    center.out date.out debug.dat bal132023.dat filelist.json …
  properties/
    run.properties                  # stormname LEE, met : parametric_pwm_windgfdl
    lee_best_track.trk              # copy
    track.richamp                   # copy
    # NOTE: NHC GIS Track.shp / Cone / Points were NOT downloaded on this golden
  post_analysis/  graphs/ (30 PNGs) + temp/ JSON (water + obs)
  post_forecast/  graphs/ (30 PNGs) + temp/
  post_wind/      graphs/ (29 PNGs) + temp/  # from lee_parametric_wind.nc via --gfsExists path
  tide_fac* windgfdl_*.log met_track.log
```

### 1.1 `run_manifest.json` (parametric) — excerpt

```json
"modes": {
  "water": true, "mesh": true, "waves": false,
  "wind": "parametric_nws6",
  "obs": true, "generate_runup": false, "track": true
},
"storm": { "name": "Lee", "basin": "AL", "number": "13", "year": 2023 },
"products": {
  "fort63_water": "…/forecast/fort.63.nc",
  "fort63_analysis": "…/analysis/fort.63.nc",
  "fort14_mesh": "…/forecast/fort.14",
  "fort68_hotstart": "…/analysis/fort.68.nc",
  "fort22_met": "…/forecast/fort.22",
  "track_source": "met_pwm/lee_best_track.trk",
  "parametric_wnd": "met_pwm/richamp.wnd",
  "parametric_wind_nc": "met_pwm/lee_parametric_wind.nc",
  "nhc_gis_dir": "properties/"
}
```

### 1.2 Wind_Inp (as run)

```text
richamp
3
2023 09 09 00 00 00
1.0
216
-101.0 -49.0
4.0 51.0
12.
```

→ grid **565 × 625**, **216** hourly snaps from coldstart (trimmed from full-track 330 h).

### 1.3 `lee_parametric_wind.nc` (owi2wind)

| | |
|--|--|
| dims | time=**216**, latitude=**565**, longitude=**625** |
| vars | `time`, `lon`, `lat`, `PSFC`, `wind_u`, `wind_v` |
| time | minutes since 1990-01-01 00:00:00 Z |
| size | ~185 M |

Same variable names as MetGet/GFS post nc — **honest labels must come from meta**, not var names.

### 1.4 fort.22 drive

| | |
|--|--|
| size | ~2.2 G |
| sample | `0.000 0.000 101000.00` → pressure **Pascals** (correct for NWS=6) |
| domain | fort.15 PWM line 565×625 / 0.083333 (campaign docs) |

### 1.5 Track products present vs missing

| Present | Missing on this golden |
|---------|-------------------------|
| `lee_best_track.trk` (BEST) | NHC GIS `Track.shp` / `Cone.*` / `Points.*` |
| `track.richamp` | scale_and_subset `RICHAMP_wind.nc` (not run — optional RI post) |
| `TrackRMW.txt` | fieldpack export (not yet) |
| `properties/run.properties` | |

**House track export** must parse **best track / track.richamp** first; NHC shapefile path is optional when present.

### 1.6 Post graphs

| Dir | Count | Content |
|-----|------:|---------|
| post_analysis/graphs | 30 | water + mesh + obs (analysis window) |
| post_forecast/graphs | 30 | water + mesh + obs (forecast) |
| post_wind/graphs | 29 | parametric wind at stations (via GFS reader schema) |

ec95d station skill remains **process smoke**, not coastal science.

---

## 2. GFS twin case (compare fixture)

```text
ec95d_lee_gfs_20230909/
  run_manifest.json          # modes.wind=gfs_nws6_fort22, track=false
  analysis/ forecast/        # same clocks, different fort.22
  met/
    gfs_lee_ec95d_00_00.wnd / .pre (+ .gz)
    filelist.json
  post_wind/
    gfs_wind.nc (~41M)       # 217 × 157 × 155
    graphs/ (29 PNGs)
  post_analysis/ post_forecast/ graphs (30 each)
  properties/                # empty on this golden
```

### 2.1 `gfs_wind.nc`

| | |
|--|--|
| dims | time=**217**, lat=**157**, lon=**155** (MetGet 0.25° mesh pad — not PWM basin) |
| vars | same family: `wind_u`, `wind_v`, `PSFC`, `lon`, `lat`, `time` |

**Compare implication:** GFS and parametric wind grids **differ in shape and spacing**. Station-series compare and ζ compare are natural; raw grid residual needs regrid or station-only compare.

---

## 3. Dual-campaign identity (what “same scenario family” means)

| Shared | Differs |
|--------|---------|
| Storm Lee AL13 2023 | Met family: `parametric_nws6` vs `gfs_nws6_fort22` |
| Mesh ec95d | fort.22 size/domain |
| Coldstart / RNDAY / forecast end | Wind nc grid |
| Water post recipe | Track artifacts (param only) |
| Obs stations list | |

This pair is the **first concrete multi-scenario compare golden** — not a special case that hardcodes “GFS vs param” forever.

---

## 4. House export mapping (from real files)

| House product | Parametric source path | GFS twin source |
|---------------|------------------------|-----------------|
| mesh + ζ | forecast/fort.14 + fort.63.nc | same pattern |
| analysis ζ (optional) | analysis/fort.63.nc | same |
| maxele | forecast/maxele.63.nc | same |
| drive wind (grid) | `met_pwm/lee_parametric_wind.nc` | `post_wind/gfs_wind.nc` |
| raw drive (optional offline) | richamp.wnd / fort.22 | met/*.wnd + fort.22 |
| rain | `met_pwm/RICHAMP_rain.nc` | (none on twin) |
| track | track.richamp + lee_best_track.trk | — |
| stations / obs | post_* temp JSON + live API at export | same |
| meta.scenario.met.family | `parametric` | `gfs` |
| meta.scenario.storm | Lee AL13 | Lee AL13 |

**Do not ship** richamp.wnd (2.2 G) or fort.22 (2.2 G) into the browser pack — nc + track JSON only.

---

## 5. Scars earned on the golden (house must not re-hit)

1. Advisory OFCL merge can have **late RMW=0** — use **BEST** track for PWM drive.  
2. `generateParametricInput` max(hours)=0 on pure BEST ATCF → **set Wind_Inp hours manually** to coldstart→end.  
3. windgfdl on Mac: no host stdout redirect; write inside container, copy out.  
4. fort.22 pressure **Pa** (101000) — verified.  
5. NHC GIS zip optional — golden has track files without shapefiles.  
6. Dual cases share clocks → absolute-time compare is well-defined.

---

## 6. Citations

- `LEE_DUAL_CAMPAIGN.md` on adcirc-local-smoke external root  
- Case manifests under both `ec95d_lee_*_20230909/`  
- Prior pipeline research `2026-07-27-parametric-wind-pipeline.md`  
- run-adcirc parametric handoff `2026-07-27-run-adcirc-parametric-lee-handoff.md`  

---

*These directories are the dictionary. House code only translates them into fieldpacks and compare slots.*
