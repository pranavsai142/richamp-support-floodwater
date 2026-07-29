# Design — /run-adcirc parametric forcing (Hurricane Lee golden)

**Date:** 2026-07-27  
**Plan:** `2026-07-27-run-adcirc-parametric-lee-plan.md`  
**Research:** `notes/GROK/research/2026-07-27-run-adcirc-parametric-lee.md`  
**Base skill:** `.grok/skills/run-adcirc/SKILL.md` (extend, do not fork)

---

## 1. Overview

Extend pathway-A manual ADCIRC so **met family = NHC parametric (PWM / windgfdl)** instead of MetGet GFS, targeting **Hurricane Lee (AL13 2023)** as the first end-to-end golden. Postprocess follows the **`TC_FORCING=True`** branch of Floodwater `richamp_scale_and_subset_post_init.scr` (generateRunProperties / PWM / windgfdl / scale_and_subset / graphs / Track GIS), executed **locally** without requiring Slurm.

Outputs become the **reference corpus** for house-viz parametric + track integration.

## 2. Goals & Non-Goals

### Goals

- Religious parametric **drive** (fort.22 + fort.15 domain) and **post** (richamp.wnd, rain, properties, graphs).  
- Document every env var (`TC_FORCING`, `PARAMETRIC_WIND`, `RICHAMP_TC_FORCING`) and gap (commented generateParametricInput in post_init).  
- Lee time windows, MetGet track recipe, windgfdl Linux workaround.  
- Case layout + run_manifest contract for `parametric_*` wind.  
- Checklist an agent can execute as `/run-adcirc parametric lee`.

### Non-Goals

- Replacing default GFS path in the skill  
- House fieldpack adapter code in this campaign  
- Perfect coastal skill on ec95d  
- Automated ASGS ensemble  

## 3. Technical requirements

| ID | Requirement |
|----|-------------|
| FR-1 | Stage mesh (default ec95d) under `adcirc-local-smoke/ec95d_lee_param_20230905`. |
| FR-2 | Coldstart **2023-09-05 00Z**; analysis RNDAY=6; forecast RNDAY=12; end **2023-09-17 00Z**. |
| FR-3 | Download NHC Lee track via MetGet `nhc-2023-al-13-*` (or HURDAT fallback). |
| FR-4 | `generateParametricInput.main(trk)` before windgfdl (do not rely on commented post_init lines). |
| FR-5 | Run `windgfdl` on Linux (Docker/Unity); produce `richamp.wnd`. |
| FR-6 | Forecast `fort.22` from PWM grid; fort.15 met line **565 625 51.000000 -101.000000 0.083333 0.083333 3600**. |
| FR-7 | Verify pressure units Pa vs mb before padcirc. |
| FR-8 | Analysis NWS=0 → fort.68; forecast IHOT=368 NWS=6 (+ NOUTM/NOUTGW). |
| FR-9 | Post: owi2wind nc; optional scale_and_subset `-parametric true`; water+wind graphs; NHC Track/Cone/Points into `properties/`. |
| FR-10 | `run_manifest.json` modes.wind = `parametric_nws6` + storm + product paths. |
| FR-11 | Append proven-runs + skill pointer after success. |

## 4. User stories

### US-1 — Agent runs parametric Lee

**As** an operator agent, **I can** follow `/run-adcirc parametric lee` and produce a green case, **so that** the suite has a parametric reference.

**AC:** checklist gates pass; tree matches research §9.

### US-2 — House eng uses the case

**As** a house-viz implementer, **I can** open `$CASE/met_pwm` and `$CASE/properties` and wire track + wind without guessing filenames.

**AC:** paths listed in manifest; ncdump / ls documented in proven-runs.

## 5. Technical guidelines

1. Prefer skill S0–S2/S7–S9 unchanged; only S3–S5 met family changes.  
2. Never paste MetGet track bbox into fort.15.  
3. Explicit generateParametricInput — post_init is incomplete.  
4. windgfdl is a black box; only CWD contract is sacred.  
5. Python post legs > Matlab for local desert-island.  
6. Stripped post default (no runup).  
7. Record scars in research note + skill footguns.

## 6. Design — skill extension (thin)

Add to `run-adcirc` parse table:

| User says | Infer |
|-----------|--------|
| `parametric lee` / `lee parametric` | met=**parametric**, storm=Lee AL13 2023, windows from research |
| `parametric <storm>` | same family; require storm id/dates |

Add section **S3p — Parametric / NHC met** pointing at:

- research note  
- domain line  
- Docker windgfdl  
- TC_FORCING post recipe  

Do **not** dump full Floodwater script into the skill — keep thin + handoff link.

## 7. Case layout (contract)

See research §9. Manifest excerpt:

```json
{
  "manifest_version": "s9.v1",
  "run_id": "ec95d_lee_param_20230905",
  "pathway": "A_local_run-adcirc",
  "modes": {
    "water": true,
    "wind": "parametric_nws6",
    "track": true,
    "waves": false,
    "generate_runup": false
  },
  "storm": {
    "name": "Lee",
    "basin": "AL",
    "number": "13",
    "year": 2023,
    "stormtype": "nhc"
  }
}
```

## 8. PR / execution plan

| Step | Action | Owner |
|------|--------|-------|
| 1 | Land this design + research + handoff (docs) | this session |
| 2 | Execute pipeline on machine (Docker windgfdl + padcirc) | next `/run-adcirc parametric lee` session |
| 3 | Patch skill S3p + proven-runs + contracts met family | after first green |
| 4 | Feed `$CASE` into house PR-B/C/D | house session |

## 9. Open questions

1. Does windgfdl emit `fort.22` as well as `richamp.wnd` on this binary? (inspect after first Docker run)  
2. Pressure units in wnd (Pa vs mb)?  
3. MetGet domain id that returns Lee merge track in 2026 (`nhc-2023-al-13-000` may need trial)  
4. NHC `_5day_latest` still hosted for 2023?  

## 10. References

- Research: `notes/GROK/research/2026-07-27-run-adcirc-parametric-lee.md`  
- Parametric pipeline + scenario/track research (same day)  
- `richamp_scale_and_subset_post_init.scr`  
- `generateRunProperties.py`, `generateParametricInput.py`, `windgfdl`, `owi2wind.py`, `scale_and_subset.py`  
- proven GFS: `ec95d_gfs_5d_2026072512`  
