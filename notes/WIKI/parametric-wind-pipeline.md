# Parametric wind pipeline (operator mental model)

**Sister-suite context:** ADCIRC(+SWAN) met can come from MetGet GFS, SHiELD wind bridge, **or NHC parametric (PWM / `windgfdl`)**. This page is the desert-island reconstruction of the parametric path.

**Deep research:** `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
**House-viz integration:** `notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-handoff.md`

---

## When you use this

- Storm is NHC-tracked (or you have ATCF-like `fort.22` / HURDAT / track.richamp).
- You want a **vortex-based wind field** on the RICHAMP Atlantic basin grid, not a GFS analysis.
- You need either **drive met for padcirc/padcswan** or a **netCDF for post/graphs/fieldpack**.

---

## Manual recipe (short)

```text
MetGet NHC track (.trk)
    → generateParametricInput.main(track)
         writes: track.richamp, Wind_Inp.txt, TrackRMW.txt, RICHAMP_rain.nc
    → ./windgfdl   (Linux; needs diag_parm.nml in CWD)
         writes: richamp.wnd
    → owi2wind.py richamp.wnd Wind_Inp.txt -o <stem>
         writes: <stem>.nc   (wind_u, wind_v, PSFC)
```

**fort.22 shortcut:** `generateParametricInput.main("fort.22")` (also used by `generateRunProperties.py`).

**Examples preserved from ops:**

| Storm | MetGet domain id | Output stem |
|-------|------------------|-------------|
| Milton AL14 | `nhc-2024-al-14-013` | `milton_parametric_wind` |
| Erin AL05 | `nhc-2025-al-05-021` | `erin_parametric_wind` |

---

## fort.15 domain (required for windgfdl 306)

When using **306 wind from windgfdl**, set met domain to:

```text
565 625 51.000000 -101.000000 0.083333 0.083333
```

This is the **same box** as `Wind_Inp.txt` / `generateParametricInput` defaults:

| | |
|--|--|
| Lon | −101 … −49 |
| Lat | 4 … 51 |
| Δ | 1/12° ≈ 0.083333° |
| Shape | 565 × 625 |

Do **not** paste the MetGet *track download* box or the RI GFS post box (−72…−70, 40…43) here.

**NWS:** `6` (wind only) or `306` (same met + SWAN). Same file family either way.

---

## Tools map

| Tool | Role |
|------|------|
| `generateParametricInput.py` | Track → PWM inputs + parametric rain |
| `readParametricTrack.py` / `readHurdatTrack.py` | Rain-only from track/HURDAT |
| `windgfdl` + `diag_parm.nml` | Binary parametric wind → `richamp.wnd` |
| `owi2wind.py` | `.wnd`+`Wind_Inp` → netCDF **or** OWI ASCII → nc |
| `scale_and_subset.py` | Optional RI downscale → `RICHAMP_wind.nc` (`wfmt=owi-306`, `-parametric true`) |
| `OceanweatherTo306.py` | MetGet OWI → 306 fort.22 (**different** producer; same NWS family) |
| `post/export/wind_bridge.py` | SHiELD → OWI/fort.22 (**different** producer) |

---

## Drive vs post vs house viz

```text
                    generateParametricInput + windgfdl
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         richamp.wnd     fort.15 domain   RICHAMP_rain.nc
              │           565×625 box
     ┌────────┴────────┐
     ▼                 ▼
  padcirc NWS=6/306   owi2wind → *.nc
  (drive met)           │
                        ├─ graphs / Reader
                        ├─ fieldpack (planned: wind_parametric)
                        └─ scale_and_subset → RICHAMP_wind (wind_post)
```

---

## Platform note

`windgfdl` is a **Linux x86-64 ELF**. On Mac, regenerate on Linux/Unity or reuse archived `.wnd` / `.nc` from the wind library (`scenario_files`, surgical gems `parametric-wind-generation`).

---

## ASGS / Floodwater

`richamp_scale_and_subset_post_init.scr` TC_FORCING branch runs `windgfdl` and sets `owi-306`, but **generateParametricInput is still commented out** — full auto track→PWM is a known TODO. Manual or pre-staged CWD is still the reliable path.

---

## /run-adcirc parametric golden — DONE (Lee dual)

**Campaign:** `/Volumes/Pranav's Hard Drive/adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md`  
**Cases:** `ec95d_lee_param_20230909` (PWM) + `ec95d_lee_gfs_20230909` (GFS twin).  
**Inventory:** `notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md`

| Product | Path (param case) |
|---------|-------------------|
| Wind nc | `met_pwm/lee_parametric_wind.nc` (216×565×625) |
| Track | `met_pwm/track.richamp`, `lee_best_track.trk` |
| Drive | `forecast/fort.22` (Pa, ~2.2 G — not for browser pack) |
| Water | `forecast/fort.63.nc` + post graphs |

| Env (post) | Role |
|------------|------|
| `TC_FORCING=True` | post_init: windgfdl + richamp.wnd + owi-306 |
| `PARAMETRIC_WIND=True` | scale_and_subset `-parametric true` |

---

## House viz: multi-scenario compare (law)

**Handoff:** `notes/GROK/handoffs/2026-07-28-house-multi-scenario-compare-handoff.md`  
**Design:** `notes/GROK/handoffs/2026-07-28-house-multi-scenario-compare-design.md`

| Layer | What it is |
|-------|------------|
| Shell dropdown | `packs.json` — index of fieldpacks |
| Case scenario | `run_manifest.json` |
| Display SoT | fieldpack per scenario |
| **Compare** | **N slots + field roles + UTC + residual tree R0–R4** — anything vs anything; residual of residual is first-class (Lee GFS↔param is a residual preset) |

**Parametric house law:** pack includes parametric wind **and** driving track; track on by default. Do not ship `richamp.wnd` / fort.22.

**Track sources:** BEST/`track.richamp` first; NHC `Track.shp` optional when present.

---

## See also

- [how-to-construct-an-adcirc-run.md](how-to-construct-an-adcirc-run.md) §4 wind families  
- [what-we-use-and-need.md](what-we-use-and-need.md) wind library  
- `/run-adcirc` skill — MetGet GFS default; parametric is alternate met  
- House fieldpack: `post/export/ADCIRC_FIELDPACK_V0.md`
