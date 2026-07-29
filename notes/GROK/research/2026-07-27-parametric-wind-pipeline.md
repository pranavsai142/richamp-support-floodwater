# Research — Parametric wind pipeline (2026-07-27)

**Mission:** Capture the operator’s manual parametric wind generation procedure as reconstructible knowledge, bind every step to first-party code/assets, and resolve how parametric wind plugs into the integrated house viz (fieldpack + suite shell) alongside MetGet GFS, fort.74, RICHAMP post wind, and the SHiELD wind bridge.

**Scope of this note:** research only. Integration design lives in  
`notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-*.md`.

**User source:** operator notes (Milton AL14, Erin AL05, fort.22 shortcut, fort.15 domain line).

---

## 1. Sharpened picture

Parametric wind is a **third atmospheric met family** in this suite:

| Family | Producer | Typical ADCIRC NWS | Display path today |
|--------|----------|--------------------|--------------------|
| MetGet GFS | `metget build` → OWI / fort.22 / `gfs_wind.nc` | 6 / 306 | `wind_gfs` adapter |
| SHiELD / FV3 | `post.export.wind_bridge` → OWI / fort.22 | 6 / 306 | atmos pack + optional re-force |
| **NHC parametric (PWM / windgfdl)** | track → `generateParametricInput` → **`windgfdl`** → `richamp.wnd` | 6 / 306 + **hardcoded domain** | **none first-class** (post uses `scale_and_subset` → `RICHAMP_wind` → `wind_post`) |

**Two end products that must not be conflated:**

1. **Drive met** — what ADCIRC reads (`fort.22` / `.wnd` as NWS=6 or 306; fort.15 met domain line must match).
2. **Post / viz product** — netCDF for graphs and fieldpack (`owi2wind` → `*.nc`, or `scale_and_subset` → `RICHAMP_wind.nc`).

---

## 2. Operator procedure (canonical, reconstructed)

### 2.1 Full track → parametric wind (Milton example)

```bash
# 1) Download NHC merge track via MetGet (raw track domain — not the wind grid)
floodwater metget build \
  --domain nhc-2024-al-14-013 0.1 -100.0 5.0 -60.0 47.0 \
  --start '2024-10-06 00:00' --end '2024-10-16 00:00' \
  --timestep 3600 --strict --compression --format raw \
  --output milton_track_13
# → produces nhc_merge_2024_al_14_013.trk (name from NHC merge, not necessarily --output)

# 2–4) Track → PWM inputs + parametric rain
python3 - <<'PY'
import generateParametricInput
generateParametricInput.main("nhc_merge_2024_al_14_013.trk")
PY
# CWD outputs: track.richamp, Wind_Inp.txt, TrackRMW.txt, RICHAMP_rain.nc

# 5–6) Black-box parametric wind generator (Linux ELF)
./windgfdl
# expects CWD: track.richamp, Wind_Inp.txt, diag_parm.nml
# produces: richamp.wnd  (and possibly fort.22 — see §4)

# 7) 306 .wnd → netCDF (post/viz)
python owi2wind.py richamp.wnd Wind_Inp.txt -o milton_parametric_wind
# → milton_parametric_wind.nc  (wind_u, wind_v, PSFC, lon, lat)
```

### 2.2 fort.22 track shortcut

```python
generateParametricInput.main("fort.22")  # ATCF-like track from an ADCIRC rundir
```

Used in production by `generateRunProperties.py` when `TC_FORCING` / advisory metadata is present (calls `generateParametricInput.main(indir + "/fort.22")`).

### 2.3 Erin (v18) example

```bash
metget build --domain nhc-2025-al-05-021 0.1 -100.0 5.0 -60.0 47.0 \
  --start '2025-08-17 00:00' --end '2025-08-21 12:00' \
  --timestep 3600 --strict --compression --format raw \
  --output erin_track_21
# → nhc_merge_2025_al_05_021.trk
# then same generateParametricInput → windgfdl → owi2wind:
python owi2wind.py richamp.wnd Wind_Inp.txt -o erin_parametric_wind
```

### 2.4 Rain-only / alternate track readers

| Entry | Role |
|-------|------|
| `readParametricTrack.py --file <track.richamp-like>` | Rain only → `RICHAMP_rain.nc` |
| `readHurdatTrack.py --file <HURDAT>` | Rain only from HURDAT |
| `generateParametricInput.main` | Rain **and** PWM inputs for `windgfdl` |

### 2.5 Verify netCDF offline

```bash
python ~/scripts/readPostUtil.py --file milton_parametric_wind.nc
# or this repo’s Reader / test harnesses once a golden nc is local
```

---

## 3. Artifact chain (file matrix)

| Step | Input | Output | Owner in repo |
|------|-------|--------|---------------|
| MetGet track | NHC domain id + window | `nhc_merge_YYYY_al_NN_AAA.trk` | MetGet CLI (not vendored) |
| PWM inputs | `.trk` or `fort.22` | `track.richamp`, `Wind_Inp.txt`, `TrackRMW.txt`, `RICHAMP_rain.nc` | `generateParametricInput.py` |
| Parametric wind | `track.richamp` + `Wind_Inp.txt` + `diag_parm.nml` | **`richamp.wnd`** | **`windgfdl`** (binary, no source) |
| Drive met domain | `Wind_Inp.txt` bounds | fort.15 met line | Operator paste — see §5 |
| Post netCDF | `richamp.wnd` + `Wind_Inp.txt` | `*.nc` (`wind_u`/`wind_v`/`PSFC`) | `owi2wind.py` (`Owi306Wind`) |
| RI downscale (optional) | `richamp.wnd` + roughness assets | `RICHAMP_wind.nc` | `scale_and_subset.py` (`wfmt=owi-306`, `-parametric true`) |
| ASGS post_init | scenario env `TC_FORCING` | same windgfdl branch | `richamp_scale_and_subset_post_init.scr` |

**Wind_Inp.txt shape** (from `generateParametricInput.py` L306–317 and sample `Param_Wind_Inp.txt`):

```text
richamp                 # storm name / label
3                       # fixed (unknown semantics in comments)
YYYY MM DD HH MM SS     # start time (dynamic)
1.0                     # time step hours? (dynamic field 3 in comments; often 1.0)
N                       # number of timesteps = max(trackDeltaHours)
W_lon E_lon             # e.g. -101.0 -49.0
S_lat N_lat             # e.g. 4.0 51.
12.                     # 1/Δ° = 12 → Δ = 1/12° ≈ 0.083333°
```

**track.richamp:** fixed-width-ish lines; field widths must stay padded (`generateParametricInput.py` L50–56, L319–330). Filename **must be** `track.richamp` for `windgfdl` (operator note + post_init).

**diag_parm.nml** (repo root, knobs for the binary):

```fortran
&diag_nml
    scale_rmw=1.0
    scale_mw=0.8
    co_tsp=0.70
    gust_fac=0.93
/
```

---

## 4. What windgfdl is (and is not)

| Fact | Evidence |
|------|----------|
| Binary, **not source** | `file windgfdl` → ELF 64-bit LSB x86-64, dynamically linked for GNU/Linux |
| Provenance | README.md step 5: copy from Hatteras/Unity postprocess trees with `diag_parm.nml` |
| CWD contract | post_init runs `$postprocessdir/windgfdl` after track inputs exist; then `wind_filename=richamp.wnd` |
| Mac | **Will not run natively on macOS** — implement/smoke needs Linux (Unity, Docker, or archive golden `.wnd`/`.nc`) |
| Open automation gap | post_init has **commented-out** `generateParametricInput` / Matlab `ASGS_fort22_to_PWM_inputs`; live TC branch only runs `windgfdl` and assumes inputs already present. Explicit TODO L96–99: integrate parametric as MetGet alternative |

**Observed production branch** (`richamp_scale_and_subset_post_init.scr` L64–77):

```bash
if [[ $TC_FORCING == "True" ]]; then
    $postprocessdir/windgfdl
    mv track.richamp properties/.
    wind_filename=richamp.wnd
    wind_inp=Wind_Inp.txt
    wind_format="owi-306"
    parametric="-parametric true"
    rain_filename=RICHAMP_rain
fi
```

So post_init treats parametric as **owi-306 + richamp.wnd**, then `scale_and_subset`.

---

## 5. Domain contract (do not invent)

### 5.1 Hardcoded PWM domain (`generateParametricInput.py` L105–110)

| Bound | Value |
|-------|-------|
| MIN_LATITUDE | 4.0 |
| MAX_LATITUDE | 51.0 |
| MIN_LONGITUDE | −101.0 |
| MAX_LONGITUDE | −49.0 |
| SPATIAL_RESOLUTION | 1/12 ° |

### 5.2 fort.15 met line (operator + oceanWeatherGenerator)

When driving ADCIRC with **306 wind from windgfdl**, set the meteorology domain to:

```text
565 625 51.000000 -101.000000 0.083333 0.083333
```

Interpretation (ADCIRC gridded met header style):  
**NWLAT NWLON WLATMAX WLONMIN WLATINC WLONINC**

Cross-check math (must hold):

- `n_lat = (51 − 4) / (1/12) + 1 = 565`
- `n_lon = (−49 − (−101)) / (1/12) + 1 = 625`

Same constants appear in `oceanWeatherGenerator.py` (`NUM_LATITUDES=565`, `NUM_LONGITUDES=625`, `DX=0.0833`, `SWLon=-101`).

`owi2wind.Owi306Wind` recomputes the same grid from Wind_Inp (L245–253):  
`spatial_res = 1 / float(lines[7])` with line 7 = `12.`.

### 5.3 MetGet track domain ≠ wind grid

Operator MetGet boxes for track download (e.g. −100…−60, 5…47) are **track extent**, not the PWM wind grid. Do not paste the MetGet track domain into fort.15 for windgfdl met.

RI post MetGet GFS box in post_init (−72…−70, 40…43) is a **third** box (Rhode Island post subset) — again not the PWM basin grid.

### 5.4 NWS numbering (already settled for the suite)

- `NWS = 6` → gridded met, circulation only  
- `NWS = 306` → **same met format** + SWAN coupling (300-series prefix)  
- Wind bridge / MetGet / parametric **drive files** share this contract; waves change fort.15 NWS, not a second met product  
  (see `post/export/wind_bridge.py`, house-viz orders-complete handoff §5.3)

---

## 6. owi2wind 306 → netCDF schema (house-viz gold)

**CLI (306 pair):** second filename must contain `"Inp"`:

```bash
python owi2wind.py richamp.wnd Wind_Inp.txt -o OUT
# is306 detect: num_files >= 2 and "Inp" in file_list[1]  (fixed; was always-true list bug)
```

**NetCDF variables written by `OwiNetcdf`** (`owi2wind.py` L152–166):

| Variable | Dims | Units |
|----------|------|-------|
| `time` | time | minutes since 1990-01-01 00:00:00 Z |
| `lon` | longitude | degrees_east |
| `lat` | latitude | degrees_north |
| `wind_u` | time, latitude, longitude | m s-1 |
| `wind_v` | time, latitude, longitude | m s-1 |
| `PSFC` | time, latitude, longitude | mb |

This is the **same variable names** `wind_gfs` expects (`wind_u`/`wind_v`/`lon`/`lat`, optional `PSFC`).  
Caveats for implementers:

1. Dim names are `latitude`/`longitude` (variables still `lat`/`lon`) — Reader GFS path already handles MetGet-class files this way.
2. Full basin × multi-day hourly packs are large (~565×625×T×2 f16) — same class of problem as `wind_post` (needs explicit stride or regional subset before browser pack).
3. `Owi306Wind` hardcodes **1-hour** time delta when walking snaps (`timedelta(seconds=3600)`), while Wind_Inp line 3 is often `1.0` — treat hourly as the current law unless proven otherwise.
4. Row order in `.wnd` is **N→S** when filling arrays (L281–296).

---

## 7. Relationship to existing house-viz wind slots

| Adapter / tool | Product keys | Status for parametric |
|----------------|--------------|------------------------|
| `wind_gfs` | `wind_u`, `wind_v`, `wind_speed`, vector `wind`, optional `pressure_surface` | **Schema-compatible** with owi2wind nc if pointed via `--path wind_gfs=….nc` — but long_names/source would falsely say “GFS” |
| `wind_fort74` | mesh wind | Only after padcirc writes fort.74 |
| `wind_post` | `wind_post_speed`, `wind_post_dir` | Parametric **after** `scale_and_subset` RI downscale; needs `--post-stride` |
| `wind_bridge` | SHiELD → OWI/fort.22 | Parallel **drive** path; not parametric |
| **Missing** | honest `wind_parametric` / stream `"parametric"` | Design target — see handoff |

**Preferred integration path (P0):** treat owi2wind parametric nc as a regular lat/lon wind product with its own stream identity (`parametric`), cloning `wind_gfs` adapter pattern (G-EXT = adapter + import line).

**P1:** parametric → `RICHAMP_wind.nc` → existing `wind_post` (already gated, heavy).  
**P2:** drive ADCIRC → fort.74 (truth for “what the mesh felt,” not a wind library).  
**P3:** new `parametric_bridge` CLI symmetric to `wind_bridge` — only if ops want one-shot track→fort.22 without manual CWD ritual.

---

## 8. Footguns (ranked)

1. **Domain mismatch** — fort.15 still on MetGet/GFS box while forcing windgfdl 565×625 basin → wrong met or crash.
2. **windgfdl is Linux-only** — Mac session cannot regenerate; need golden `.wnd`/`.nc` from archive or remote.
3. **post_init TC path incomplete** — `generateParametricInput` commented out; bare `windgfdl` assumes pre-staged inputs.
4. **owi2wind is306 detect** — second arg must contain `"Inp"`; wrong order/name falls into OWI ASCII path.
5. **Confusing drive met vs post wind** — `RICHAMP_wind.nc` is downscaled RI product; `milton_parametric_wind.nc` is basin PWM.
6. **Track name** — binary expects `track.richamp` exactly.
7. **Basin fieldpack size** — do not ship full Atlantic 10-day hourly grid to the browser without stride/subset (explicit fidelity record required).
8. **Rain is coupled** — `generateParametricInput` always builds `RICHAMP_rain.nc`; house rain adapter today is GFS-only (`rain_gfs`).

---

## 9. Foundation & testability

| Claim | How to verify without a full storm |
|-------|-------------------------------------|
| Domain math 565×625 | Static: Wind_Inp bounds + 1/12° → counts |
| Wind_Inp writer | Read `generateParametricInput.py` L306–317; sample `Param_Wind_Inp.txt` |
| owi2wind schema | Read `OwiNetcdf` constructors (no binary needed) |
| windgfdl output name | post_init L74 `richamp.wnd` |
| Adapter reuse feasibility | Variable names match `wind_gfs.py` |
| Binary platform | `file windgfdl` → ELF Linux |

**Golden fixtures (external / Unity):**  
`project/.../scenario_files` wind library (`richamp.wnd` ~2.5 G historical, parametric test ncs), `home/projects/parametric-wind-generation`, Milton/Erin products if archived. **Not required for KB**; required for implement smoke.

---

## 10. Verdicts

| Insight | Verdict |
|---------|---------|
| Operator procedure is real and maps to repo tools | **Confirmed** |
| Domain line is same box as Wind_Inp / oceanWeatherGenerator | **Confirmed** (math + constants) |
| owi2wind nc ≈ GFS var names | **Confirmed** (`wind_u`/`wind_v`/`lon`/`lat`/`PSFC`) |
| First-class house-viz parametric wind exists today | **Gap** — no adapter, no product key honesty |
| windgfdl runnable on this Mac for regen | **No** (Linux ELF) |
| Rain parametric in house pack | **Gap** (defer unless promoted) |
| ASGS full automation closed | **No** — post_init TODO remains |

---

## 11. Citations (first-party)

- `generateParametricInput.py` — track → PWM inputs + rain  
- `owi2wind.py` — `Owi306Wind`, `OwiNetcdf`, is306 detect L423–425  
- `oceanWeatherGenerator.py` — 565×625 / 0.0833 / SWLon −101  
- `richamp_scale_and_subset_post_init.scr` L64–130 — TC_FORCING / owi-306  
- `generateRunProperties.py` L63 — `generateParametricInput.main(.../fort.22)`  
- `post/export/field_adapters/wind_gfs.py` — pack pattern to clone  
- `post/export/wind_bridge.py` — NWS 6 ≡ 306 drive contract  
- `notes/GROK/research/2026-07-25-run-adcirc-foundations.md` — MetGet fort.22 path  
- `notes/GROK/handoffs/2026-07-25-richamp-support-web-orders-complete-handoff.md` — house gates  
- Operator notes (this session) — Milton/Erin recipes, fort.15 line  

---

## 12. Next (implement elsewhere)

See handoff design:  
`notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-design.md`  
and narrative:  
`notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-handoff.md`.

---

*One system writes the wind and the pressure — sometimes that system is a parametric vortex on an NHC track, not GFS or SHiELD. Same house; honest labels.*
