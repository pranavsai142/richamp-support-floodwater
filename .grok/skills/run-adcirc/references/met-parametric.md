# Met family: parametric (NHC / PWM / windgfdl)

**Load when:** user says `parametric`, `lee parametric`, TC/NHC drive met, or `S3p`.  
**Not GFS.** Do not put MetGet track bbox on fort.15.

**Proven:** Run D — `references/proven-runs.md`  
**Deep lore:** `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`,  
`notes/GROK/research/2026-07-27-run-adcirc-parametric-lee.md`  
**Campaign note:** `/Volumes/Pranav's Hard Drive/adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md`

---

## One-screen contract

| Item | Value |
|------|--------|
| Drive product | `richamp.wnd` → copy to `forecast/fort.22` |
| fort.15 met line | `565 625 51.000000 -101.000000 0.083333 0.083333 3600` |
| NWS | **6** padcirc (or **306** + RSTIMINC if padcswan) |
| P units | **Pascals** (~1e5), not mb |
| Binary | repo `windgfdl` = **Linux x86_64 ELF** (Docker/Unity on Mac) |
| Track | Prefer **NHC best track**, not advisory OFCL merge for historical goldens |
| Post owi2wind | `owi2wind.py richamp.wnd Wind_Inp.txt -o stem` (306 path via `Inp` in second name) |

**Track domain ≠ fort.15 domain.** MetGet NHC bbox is only for download; PWM basin is always the 565×625 line above.

---

## Lee AL13 2023 defaults (proven NE-impact dual)

| Field | Value |
|-------|--------|
| Coldstart | **2023-09-09 00:00 UTC** |
| Analysis | RNDAY=**6** → ends 2023-09-15 00Z, NWS=0 |
| Forecast end | **2023-09-18 00:00 UTC**, RNDAY=**9** |
| Case id | `ec95d_lee_param_20230905` style → actual golden: `ec95d_lee_param_20230909` |
| Dual GFS twin | same clocks, MetGet GFS 0.25° (Run E) |

Why not full life Sep 5–17: Cat-5 peak is far from East Coast mesh; NE surge/skill window is Sep 14–16; PWM multi-day is multi-GB.

---

## Ordered recipe (S3p)

### 1) Track (best track preferred)

```bash
source ~/projects/setApiKey.sh
export PATH="$(cd <repo> && pipenv --venv)/bin:$PATH"
cd $CASE/met_pwm

# Best track via MetGet: advisory domain id must be real (not 000 — client rejects advisory 0)
# nhc-YYYY-basin-storm-advisory  e.g. nhc-2023-al-13-036 returns btk + merge
metget --apikey "$METGET_API_KEY" --endpoint "$METGET_ENDPOINT" build \
  --domain nhc-2023-al-13-036 0.1 -100.0 5.0 -60.0 47.0 \
  --start '2023-09-05 00:00' --end '2023-09-18 00:00' \
  --timestep 3600 --strict --compression --format raw \
  --output lee_track --output-directory $CASE/met_pwm

# Prefer pure BEST for historical golden:
#   nhc_btk_2023_al_13.btk  or  ATCF bal132023.dat
#   cp nhc_btk_*.btk lee_best_track.trk
# Avoid using nhc_merge_* OFCL tail alone for post-ET — late RMW/P can go zero or blow up.
```

**ATCF fallback:** `https://ftp.nhc.noaa.gov/atcf/archive/2023/bal132023.dat.gz`

### 2) PWM inputs (`generateParametricInput`)

```bash
# pipenv install haversine  # once — import is hard-required
cd $CASE/met_pwm
pipenv run python - <<PY
import sys, os
sys.path.insert(0, "<repo>")
os.chdir("$CASE/met_pwm")
import generateParametricInput
generateParametricInput.main("lee_best_track.trk")
PY
# → track.richamp Wind_Inp.txt TrackRMW.txt RICHAMP_rain.nc
```

**BEST-track hours footgun:** ATCF BEST lines use absolute dates with **hours field = 0**.  
`generateParametricInput` writes `Wind_Inp` timestep count = `max(hours)` → **0**.  
**Always overwrite Wind_Inp** for the campaign:

```text
richamp
3
YYYY MM DD HH MM SS    # coldstart (e.g. 2023 09 09 00 00 00)
1.0
NHOURS                 # hours from coldstart to forecast end (e.g. 216 for 9 d)
-101.0 -49.0
4.0 51.0
12.
```

Copy repo `diag_parm.nml` + `windgfdl` into `met_pwm/`.

### 3) windgfdl on Mac (Docker) — **do not reinvent**

```bash
# colima or Docker Desktop; image needs linux/amd64 (qemu on arm64 is OK if quiet)
docker run --rm --platform linux/amd64 \
  -v "$CASE/met_pwm":/host \
  rockylinux:8 \
  bash -c '
    set -e
    mkdir -p /tmp/wg && cd /tmp/wg
    cp /host/windgfdl /host/diag_parm.nml /host/track.richamp /host/Wind_Inp.txt .
    chmod +x windgfdl
    # CRITICAL: never host-redirect stdout — WSMAX spam is multi-GB and kills wall time
    ./windgfdl >/dev/null 2>&1
    cp -f richamp.wnd date.out /host/
  '
# expect ~minutes–tens of min for ~9 d hourly basin under qemu; hours if log spam
```

**Gates:**
- `date.out` line count ≈ NHOURS  
- `richamp.wnd` non-empty (~2 GB for 9 d 565×625)  
- Spot-check: storm hours have domain max near track, not only domain corners  
- P in file ~1e5 (Pa)

**Anti-patterns:**
- `docker run … ./windgfdl > windgfdl.log` on external drive → 1 GB+ log, multi-hour wall  
- Writing `.wnd` only on slow external mount (prefer container `/tmp`, copy once)  
- Expecting native `./windgfdl` on macOS arm64  

### 4) Attach to forecast

```bash
cp $CASE/met_pwm/richamp.wnd $CASE/forecast/fort.22
# forecast fort.15: NWS=6, met line 565×625, NOUTM/NSTAM/NOUTGW present, IHOT=368
cp $CASE/analysis/fort.68.nc $CASE/forecast/fort.68.nc
```

### 5) Post (parametric)

```bash
# OWI 306-style nc for graphs / fieldpack path override
pipenv run python owi2wind.py \
  $CASE/met_pwm/richamp.wnd $CASE/met_pwm/Wind_Inp.txt \
  -o $CASE/met_pwm/lee_parametric_wind

# Station wind graphs (GFS reader schema)
pipenv run python generateGraphs.py \
  --stations OBS_STATIONS.json \
  --gfsExists true --wind $CASE/met_pwm/lee_parametric_wind.nc \
  --obsExists true \
  --backgroundChoice EAST_COAST_OUTLINE \
  --tempDir $CASE/post_wind/temp/ \
  --graphDirectory $CASE/post_wind/graphs/

# Map animation (wind.gif): requires Reader getMap enabled for gfs (map frames)
# Optional RICHAMP scale_and_subset -wfmt owi-306 -parametric true (needs NLCD + gfs-roughness)
```

Env names (ASGS post_init): **`TC_FORCING`**, **`PARAMETRIC_WIND`**, **`RICHAMP_TC_FORCING`** — not `USE_TC_FORCING`.  
post_init leaves `generateParametricInput` **commented** — always run it yourself.

---

## QA scars (Lee 2026-07-28)

### A. Station series look “flat then spike”

| Pattern | Meaning |
|---------|---------|
| Early zeros at coastal gauges | **Expected** pure PWM far-field (no background wind) while storm is tropical far away |
| Gradual ramp Sep 15–16 at NE | Credible outer circulation as Lee approaches |
| **Same-hour spike at ALL stations** (RI + FL) to ~30–40 m/s | **Not physical** — domain-wide windgfdl blow-up |

### B. Domain-wide blow-up (post-ET / northern edge)

Near **Sep 17 00–04Z** on the Lee golden:

- ~99% of basin cells had speed > 15 m/s  
- Domain max on **SW corner (−101°, ~20°N)** ~70 m/s  
- Storm center was near **NS**, not Florida  

Likely: extratropical / large RMW / track near **PWM north edge (51°N)** → windgfdl unstable field.

**Mitigation for science windows:** end met/forecast by **~2023-09-16 18–20Z** (after NE impact, before blow-up), or mask frames where domain-mean speed explodes / max is on a corner.

### C. Track source

| Source | Use |
|--------|-----|
| `nhc_btk_*` / ATCF BEST | **Preferred** historical golden |
| `nhc_merge_*_036` | OK for advisory-time forecast experiments; OFCL tail can poison late hours |
| `nhc-…-000` | MetGet client may **reject** advisory 0 |

### D. Far-field zeros vs GFS

Do not compare early parametric station series to GFS and call PWM “broken” — GFS has ambient weather; PWM does not.

---

## Case tree checklist

```text
$CASE/
  analysis/ fort.15 fort.68.nc fort.63.nc …
  forecast/ fort.15 fort.22 fort.63.nc fort.68.nc …
  met_pwm/
    lee_best_track.trk  (or nhc_btk_*)
    track.richamp Wind_Inp.txt TrackRMW.txt diag_parm.nml windgfdl
    richamp.wnd date.out
    lee_parametric_wind.nc
    RICHAMP_rain.nc
  properties/ run.properties  [Track.* optional]
  post_forecast/graphs/  post_wind/graphs/
  run_manifest.json   modes.wind = parametric_nws6
```

---

## Manifest modes

```json
"modes": { "wind": "parametric_nws6", "track": true, "waves": false, "generate_runup": false },
"storm": { "name": "Lee", "basin": "AL", "number": "13", "year": 2023 }
```
