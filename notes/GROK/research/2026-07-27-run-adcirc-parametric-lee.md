# Research — /run-adcirc with parametric (NHC) forcing · Hurricane Lee golden

**Date:** 2026-07-27  
**Mission:** Define a **pathway-A manual ADCIRC** campaign that uses **parametric PWM / windgfdl met** (not MetGet GFS), mirrors the **TC_FORCING** branch of `richamp_scale_and_subset_post_init.scr`, and produces a full product tree so house-viz integration has **real sample files**. Storm: **Hurricane Lee (AL13, 2023)**.

**Depends on:**

- `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
- `notes/GROK/research/2026-07-27-house-scenario-catalog-and-tracks.md`  
- `/run-adcirc` skill + `references/contracts.md` + proven GFS runs  

**Out of this research:** implementing the run; this is the religious recipe + contracts.

---

## 1. Why this exists

House design says “integrate parametric wind + track.” Without a **real case directory** that contains:

| Product family | Example files |
|----------------|---------------|
| ADCIRC water | `forecast/fort.63.nc`, analysis hotstart |
| Drive met | `forecast/fort.22` (PWM 306 grid), fort.15 met line |
| PWM raw | `track.richamp`, `Wind_Inp.txt`, `richamp.wnd`, track `.trk` |
| Post wind | `owi2wind` nc and/or `RICHAMP_wind.nc` |
| Rain | `RICHAMP_rain.nc` |
| Track GIS | `properties/Track.*`, `Cone.*`, `Points.*`, `run.properties` |
| Graphs | station/map PNGs |
| Manifest | `run_manifest.json` with `modes.wind: parametric_*` |

…integration work invents paths. **Generate the files first**, following Floodwater post_init, then wire house viz.

---

## 2. Two different “TC” switches (do not confuse)

| Variable / place | Values | What it does |
|------------------|--------|--------------|
| **`TC_FORCING`** | `"True"` | **post_init.scr** — skip MetGet GFS; run **`windgfdl`**; `richamp.wnd` + owi-306 → `scale_and_subset`; rain = parametric `RICHAMP_rain` |
| **`RICHAMP_TC_FORCING`** | `"on"` | **scale_and_subset.scr** (post-forecast) — only sets Matlab `forcing=NHC` vs `GFS` for max-inundation plot labels |
| **`PARAMETRIC_WIND`** | `"True"` | Forces `-parametric true` on scale_and_subset (uniform roughness) even outside full TC branch |
| **ADCIRC NWS** | 6 / 306 | **Drive** met format (same grid contract); independent of post env vars |

ASGS sets these in the scenario environment. Local `/run-adcirc parametric` must **set them explicitly** (or run the same Python/binary steps without Slurm).

There is **no** `USE_TC_FORCING` string in-repo; the live name is **`TC_FORCING`**.

---

## 3. What post_init actually does when `TC_FORCING=True`

Source: `richamp_scale_and_subset_post_init.scr` (authoritative order).

```text
1. generateRunProperties.py --indir $RICHAMP_INDIR
     → properties/run.properties
     → if TC metadata in adcirc_simulation.1:
          generateParametricInput.main(fort.22)
          download NHC GIS zip → Track/Cone/Points.*
2. Read start/end from run.properties
3. if TC_FORCING:
     ./windgfdl                    # CWD: track.richamp, Wind_Inp.txt, diag_parm.nml
     mv track.richamp properties/
     wind = richamp.wnd, format=owi-306, parametric=-parametric true
     rain_filename=RICHAMP_rain    # already from generateParametricInput
   else:
     metget GFS rain + wind (RI box −72…−70, 40…43)  ← post box, not drive box
4. scale_and_subset.py → RICHAMP_wind.nc  (NLCD z0 scale)
5. generateGraphs.py  (flags from GRAPH_*)
6. Matlab subset fort.63 + max inundation (forcing label NHC vs GFS)
7. Copy products + properties + graphs → RICHAMP_OUTDIR
```

**Critical gaps in the live script (documented TODO L96–99):**

- `generateParametricInput` / Matlab `ASGS_fort22_to_PWM_inputs` are **commented out** in the TC branch.  
- Live TC branch assumes **PWM inputs already exist in CWD** before `windgfdl` (or that generateRunProperties just wrote them from fort.22).  
- Local religious recipe must **explicitly** run generateParametricInput on the NHC track **before** windgfdl.

---

## 4. Drive met vs post met (same storm, two roles)

```text
                    NHC track (.trk)
                           │
              generateParametricInput
                 │                    │
         track.richamp          RICHAMP_rain.nc
         Wind_Inp.txt           TrackRMW.txt
                 │
              windgfdl  (Linux)
                 │
            richamp.wnd  ──────────────────────────────┐
                 │                                     │
    copy / use as fort.22                    owi2wind → parametric.nc
    fort.15 domain 565×625                   scale_and_subset → RICHAMP_wind.nc
                 │                                     │
            padcirc NWS=6                          generateGraphs --gfsExists / --postExists
            → fort.63.nc
```

| Role | Files | fort.15 |
|------|-------|---------|
| **Drive** | `forecast/fort.22` from PWM 306 grid | NWS=6 (or 306+SWAN); met line **565 625 51.000000 -101.000000 0.083333 0.083333** (+ WTIMINC 3600; + RSTIMINC if 306) |
| **Post** | `richamp.wnd` + Wind_Inp → nc / RICHAMP_wind | N/A (Python) |

**Pressure units gate:** `OceanweatherTo306` writes **Pascals** in fort.22. After windgfdl, inspect a few fort.22 / wnd pressure values:

- ~1e3 → likely **mb** (wrong for ADCIRC NWS=6; multiply ×100 or convert)  
- ~1e5 → **Pa** (correct for proven MetGet path)

Do not skip this check on the first Lee run.

Operator note: *“When using the fort.22 file generated by windgfdl, change the meteorology domain in fort.15”* — confirms windgfdl can emit fort.22; also `richamp.wnd` is the same u/v/p line family as 306 fort.22 (`Owi306Wind` / `OceanweatherTo306` layout).

---

## 5. Hurricane Lee (AL13 2023) — fixed scenario parameters

| Field | Value |
|-------|--------|
| Name | Lee |
| Basin / number | AL **13**, year **2023** |
| NHC TCR window | ~**5 Sep – 16 Sep** 2023 (extratropical ~16–18) |
| Peak interest NE US / Canada | ~**14–16 Sep** |
| Stormtype | `nhc` |

### Recommended time windows (state before editing fort.15)

**Option P0 — process golden (ec95d smoke, full enough for products):**

| Phase | Clock |
|-------|--------|
| Coldstart / base_date | **2023-09-05 00:00 UTC** |
| Analysis | RNDAY=**6** → ends 2023-09-11 00Z, NWS=0 |
| Forecast attach | IHOT=368 from fort.68 |
| Forecast end | **2023-09-17 00:00 UTC** |
| Forecast RNDAY | **12** (days since coldstart) |
| Met snaps | hourly from coldstart → forecast end (≈ 12×24 + 1) |

**Option P1 — NE impact focus (shorter wall time):**

| Phase | Clock |
|-------|--------|
| Coldstart | 2023-09-10 00Z |
| Analysis | RNDAY=4 |
| Forecast end | 2023-09-17 00Z |
| Forecast RNDAY | 7 |

Prefer **P0** for house sample completeness unless disk/time forces P1.

### Track download (MetGet — same pattern as Milton/Erin)

```bash
source ~/projects/setApiKey.sh
export PATH="$(cd <repo> && pipenv --venv)/bin:$PATH"

# Advisory-centered pull (adjust advisory as needed; best-track merge preferred for golden)
metget build \
  --domain nhc-2023-al-13-000 0.1 -100.0 5.0 -60.0 47.0 \
  --start '2023-09-05 00:00' --end '2023-09-17 00:00' \
  --timestep 3600 --strict --compression --format raw \
  --output lee_track

# Expect something like:
#   nhc_merge_2023_al_13_*.trk
# If advisory-specific domains fail, try best-track / other nhc-2023-al-13-* ids
# or fall back to NHC ATCF / HURDAT file + generateParametricInput
```

**Track domain (−100…−60, 5…47) is NOT the fort.15 wind grid.**  
fort.15 PWM domain remains:

```text
565 625 51.000000 -101.000000 0.083333 0.083333 3600.0
# NWS=306: append RSTIMINC e.g. 600
```

### NHC GIS shapefiles (generateRunProperties path)

```text
http://www.nhc.noaa.gov/gis/forecast/archive/al132023_5day_latest.zip
→ properties/Track.* Cone.* Points.*
```

For a **reproducible** golden, prefer a **pinned advisory zip** if still on archive (e.g. advisory near NE approach), not only `_latest` (may 404 years later). Fallback: `generateTrackShapefile.py` from the same `.trk` / track.richamp positions → `Track.shp`.

---

## 6. generateRunProperties dependency on ASGS log

`generateRunProperties.py` only takes the TC branch if `adcirc_simulation.1` contains a line with `get_advisory_time.py` and storm/advisory/year flags.

**Manual Lee case will not have that log by default.** Options:

| Approach | When |
|----------|------|
| **A. Manual religious steps** (recommended for first golden) | Call generateParametricInput + NHC zip + windgfdl yourself; write `properties/run.properties` by hand |
| **B. Stub log** | Minimal `adcirc_simulation.1` with SIMULATION_START/END + synthetic get_advisory_time line for storm=13 advisory=… year=2023 |
| **C. Patch script later** | CLI flags for storm metadata (out of scope for first golden) |

Hand-written `run.properties` minimum:

```text
forecastValidStart : 20230905000000
forecastValidEnd : 20230917000000
rawstart: 2023-09-05 00:00
rawend: 2023-09-17 00:00
stormname : LEE
stormclass : HU
stormtype : nhc
stormnumber : 13
advisory : 000
year : 2023
track : CENTER
```

---

## 7. windgfdl on this Mac

| Fact | Detail |
|------|--------|
| Binary | repo `windgfdl` — **ELF Linux x86_64** |
| Host | Mac arm64 — **will not exec natively** |
| Workarounds | (1) Docker linux/amd64 with mounted case dir (2) Unity/Linux node (3) prebuilt `richamp.wnd` from archive |

**Docker sketch (verify on first use):**

```bash
cd $CASE/met_pwm
# files present: track.richamp Wind_Inp.txt diag_parm.nml windgfdl
docker run --rm --platform linux/amd64 -v "$PWD":/work -w /work \
  rockylinux:8 ./windgfdl
# expect richamp.wnd (and possibly fort.22 — inspect)
```

If Docker lacks libs, use a fuller image or run on Unity. **Gate:** `richamp.wnd` non-empty; line count ≈ 565×625×N_times.

Static knobs: repo `diag_parm.nml` (`scale_rmw`, `scale_mw`, `co_tsp`, `gust_fac`).

---

## 8. Ordered pipeline: `/run-adcirc parametric lee`

Reuse S0–S2, S7–S9 from run-adcirc skill; **replace S3–S5 met** with parametric; **add S3p post TC path**.

### S0 — Stage

```text
RUN_ID=ec95d_lee_param_20230905   # or ricv1_lee_param_… for science mesh
CASE=~/projects/adcirc-local-smoke/$RUN_ID
mesh=ec95d (process) | ricv1 (skill) | v18 (if drive mounted)
```

Stage fort.13/14/15/20 as GFS golden; **do not** attach MetGet fort.22 yet.

### S1 — fort.15 clocks (Lee P0)

| | Analysis | Forecast |
|--|----------|----------|
| base_date | 2023-09-05 00:00:00 | same |
| RNDAY | 6 | 12 |
| IHOT | 0 | 368 |
| NWS | 0 | **6** (padcirc) or **306** if waves |
| NOUTM/NOUTGW | absent | present |
| Met line | none | **565 625 51.000000 -101.000000 0.083333 0.083333 3600.0** |
| NOUTGE | hourly | hourly |

### S2 — tide_fac

Native compile; XDAYS = forecast RNDAY; start = coldstart h d m y.

### S3p — Parametric met (replaces MetGet fort.22)

Working directory: `$CASE/met_pwm/` (keep clean).

```bash
REPO=~/projects/richamp-support-floodwater
cd $CASE/met_pwm
cp $REPO/diag_parm.nml $REPO/windgfdl .

# 1) Track
metget … --output lee_track
TRK=$(ls nhc_merge_2023_al_13*.trk | head -1)

# 2) PWM inputs + rain (CWD outputs)
cd $CASE/met_pwm
python3 - <<PY
import sys
sys.path.insert(0, "$REPO")
import generateParametricInput
generateParametricInput.main("$TRK")
PY
# → track.richamp Wind_Inp.txt TrackRMW.txt RICHAMP_rain.nc

# 3) windgfdl (Linux)
docker run --rm --platform linux/amd64 -v "$PWD":/work -w /work <linux-image> ./windgfdl
# or Unity: ./windgfdl
# → richamp.wnd

# 4) Drive file for ADCIRC
cp richamp.wnd $CASE/forecast/fort.22
# verify pressure units; fix if mb

# 5) Optional OWI→nc for post/graphs/fieldpack
python3 $REPO/owi2wind.py richamp.wnd Wind_Inp.txt -o $CASE/met_pwm/lee_parametric_wind
```

### S4 — Analysis (parallel with S3p if desired)

NWS=0; no fort.22. Gate fort.68.nc.

### S5 — Forecast

```bash
cp analysis/fort.68.nc forecast/fort.68.nc
# fort.15: NWS=6, met line 565×625, fort.22 present
adcprep + padcirc
```

Gate: terminating normally; fort.63.nc; optional fort.74 if NOUTGW≠0.

### S9p — Post (mirror TC_FORCING, local, no Slurm)

```bash
export TC_FORCING=True
export PARAMETRIC_WIND=True
export RICHAMP_INDIR=$CASE/forecast
export RICHAMP_OUTDIR=$CASE/richamp_out
export POSTHOME=$REPO
export POST_TEMP_DIR=$CASE/post_pwm/temp/
export BACKGROUND_CHOICE=EAST_COAST_OUTLINE
export WIND_STATIONS=$REPO/OBS_STATIONS.json
export GRAPH_WATER=True GRAPH_POST=True GRAPH_OBS=True
# GRAPH_GFS only if lee_parametric_wind.nc staged as wind_filename.nc
# Skip Matlab if no module — do Python legs religiously:

cd $CASE/met_pwm   # has richamp.wnd Wind_Inp from S3p
# scale_and_subset (needs NLCD + gfs-roughness in repo)
python3 $REPO/scale_and_subset.py \
  -o $CASE/post_pwm/RICHAMP_wind -sl up-down \
  -hr $REPO/NLCD_z0_RICHAMP_Reg_Grid.nc \
  -w richamp.wnd -winp Wind_Inp.txt -wfmt owi-306 \
  -wr $REPO/gfs-roughness.nc -z0name $CASE/post_pwm/z0_interp \
  -r 3000 -sigma 1000 -t 3 -wasync -parametric true

# NHC GIS (manual if generateRunProperties skipped)
# curl NHC zip → properties/

# Graphs — water
python3 $REPO/generateGraphs.py \
  --stations $REPO/OBS_STATIONS.json \
  --waterExists true --water $CASE/forecast/fort.63.nc \
  --meshExists true --mesh $CASE/forecast/fort.14 \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $CASE/post_forecast/temp/ \
  --graphDirectory $CASE/post_forecast/graphs/ \
  --prefix lee_param_water_

# Graphs — parametric wind field (owi2wind nc)
python3 $REPO/generateGraphs.py \
  --stations $REPO/OBS_STATIONS.json \
  --gfsExists true --wind $CASE/met_pwm/lee_parametric_wind.nc \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $CASE/post_wind/temp/ \
  --graphDirectory $CASE/post_wind/graphs/ \
  --prefix lee_param_wind_

# Graphs — RICHAMP post wind if scale_and_subset succeeded
python3 $REPO/generateGraphs.py \
  --stations $REPO/OBS_STATIONS.json \
  --postExists true --wind $CASE/post_pwm/RICHAMP_wind.nc \
  --tempDir $CASE/post_pwm/temp/ \
  --graphDirectory $CASE/post_pwm/graphs/ \
  --prefix lee_param_post_
```

Matlab `subset_fort63_richamp` / `plot_max_inundation` are **ASGS dashboard** legs — optional on Mac if Matlab missing; **Python products are the house-viz gold**.

### S9e — Fieldpack (after products exist)

```bash
PYTHONPATH=$REPO pipenv run python -m post.export.cli \
  --rundir $CASE/forecast --mesh $CASE/forecast/fort.14 --case $CASE \
  --products mesh,water,wind,stations,obs_water \
  --path wind_gfs=$CASE/met_pwm/lee_parametric_wind.nc \
  --outdir $CASE/products/fieldpack
# later: wind_parametric + track products per full-integration design
```

Until `wind_parametric` ships, path override is OK for **fixture generation only** — meta will still say GFS unless adapted; fix in house PR-C.

### Manifest

```json
"modes": {
  "wind": "parametric_nws6",
  "track": true,
  "waves": false,
  "generate_runup": false
},
"storm": {
  "name": "Lee", "basin": "AL", "number": "13", "year": 2023
},
"products": {
  "track_source": "met_pwm/nhc_merge_….trk",
  "parametric_wnd": "met_pwm/richamp.wnd",
  "parametric_wind_nc": "met_pwm/lee_parametric_wind.nc",
  "fort22_met": "forecast/fort.22",
  "nhc_gis_dir": "properties/"
}
```

---

## 9. Expected case tree (house sample checklist)

```text
$CASE/
  run_manifest.json
  analysis/   fort.15 fort.14 fort.63.nc fort.68.nc …
  forecast/   fort.15 fort.14 fort.22 fort.63.nc …
  met_pwm/
    nhc_merge_2023_al_13_*.trk
    track.richamp  Wind_Inp.txt  TrackRMW.txt
    diag_parm.nml
    richamp.wnd
    RICHAMP_rain.nc
    lee_parametric_wind.nc
  properties/          # Track/Cone/Points + run.properties
  post_forecast/graphs/
  post_wind/graphs/
  post_pwm/            # RICHAMP_wind.nc + graphs if scale_and_subset ran
  products/fieldpack/  # optional S9e
```

**Done when:** every row above exists (Matlab-only outs optional) and pressure/domain gates pass.

---

## 10. Footguns specific to parametric run-adcirc

1. MetGet track domain ≠ fort.15 PWM domain  
2. windgfdl Linux-only  
3. generateRunProperties TC branch needs ASGS log — stub or manual  
4. post_init comments out generateParametricInput — do not assume magic  
5. Pressure mb vs Pa in fort.22  
6. Met snaps must cover **coldstart → end** (hotstart index)  
7. scale_and_subset needs NLCD + gfs-roughness (in repo)  
8. RI MetGet post box is irrelevant for TC_FORCING wind  
9. ec95d station skill still not science — process golden  
10. `_5day_latest` NHC zip may 404 — pin advisory or shapefile from track  

---

## 11. Relation to house viz handoffs

| After this golden exists | House PR can |
|--------------------------|--------------|
| `lee_parametric_wind.nc` | wind_parametric adapter smoke |
| track.richamp / trk / Track.shp | track_export + shell track layer |
| run_manifest modes.wind | scenario catalog card |
| properties/Track.* | NHC GeoJSON path |
| fort.63 + stations graphs | G-STN / water parity |

Do **not** start house track UI without this tree (or an archived equivalent).

---

## 12. Citations

- `richamp_scale_and_subset_post_init.scr` L33–131, L176–178, L96–99 TODO  
- `richamp_scale_and_subset.scr` L29–33 `RICHAMP_TC_FORCING`  
- `generateRunProperties.py` — fort.22 → PWM + NHC zip  
- `generateParametricInput.py` — hardcoded basin domain  
- `OceanweatherTo306.py` — fort.22 Pa + meta line  
- `/run-adcirc` SKILL.md S0–S9, contracts, proven-runs GFS  
- Parametric pipeline research 2026-07-27  
- NHC Lee AL13 2023 ~5–16 Sep  

---

*Generate the storm. Keep every intermediate. Then the house has something true to load.*
