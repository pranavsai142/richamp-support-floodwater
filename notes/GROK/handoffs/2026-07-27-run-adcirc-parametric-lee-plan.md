# Plan — /run-adcirc parametric · Hurricane Lee golden

**Goal:** Produce a complete local case directory for **Hurricane Lee (AL13 2023)** forced by **NHC parametric / windgfdl** met, with postprocess mirroring **`TC_FORCING=True`** in `richamp_scale_and_subset_post_init.scr`, so house-viz integration has real reference products.

**Research SoT:** `notes/GROK/research/2026-07-27-run-adcirc-parametric-lee.md`  
**Skill base:** `.grok/skills/run-adcirc/` (GFS path remains default; this is a **met-family variant**)

---

## Success criteria

1. Analysis + forecast **ADCIRC terminating normally** with **NWS=6** (or 306) and fort.15 domain **565×625 PWM box**.  
2. Case tree includes track → PWM → `richamp.wnd` → fort.22 → fort.63 + post graphs + properties Track GIS (or documented fallback).  
3. `run_manifest.json` has `modes.wind: parametric_nws6` (or `_nws306`) and product paths.  
4. Operator can re-run from the handoff without inventing steps.  
5. House team can point at `$CASE` for track/wind/station fixtures.

## Non-goals (first golden)

- Full ASGS/Slurm post_init (local Python legs are enough)  
- Matlab dashboard plots if Matlab absent  
- ricv1 multi-day science skill (ec95d process golden OK first)  
- House adapter implementation (consume outputs later)  
- Runup  

## Phases

| Phase | Name | Gate |
|------:|------|------|
| 0 | Stage case + clocks (Lee P0) | fort.15 analysis/forecast consistent |
| 1 | Tides | FF/FACE both phases |
| 2 | Download Lee track | `.trk` present |
| 3 | generateParametricInput | track.richamp, Wind_Inp, rain |
| 4 | windgfdl (Linux/Docker) | richamp.wnd; pressure unit check |
| 5 | Install fort.22 + met line | domain 565×625 |
| 6 | Analysis NWS=0 | fort.68.nc |
| 7 | Forecast NWS=6 | fort.63.nc terminating normally |
| 8 | Post TC path | owi2wind nc, scale_and_subset optional, graphs, properties |
| 9 | Manifest + proven-runs entry | handoff checklist green |

## Default case id

```text
ec95d_lee_param_20230905
~/projects/adcirc-local-smoke/ec95d_lee_param_20230905/
```

Upgrade mesh to ricv1/v18 only after process golden works.
