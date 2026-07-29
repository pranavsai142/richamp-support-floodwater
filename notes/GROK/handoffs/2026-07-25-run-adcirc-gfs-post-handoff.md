# Handoff — run-adcirc GFS + stripped post (2026-07-25)

## What this session accomplished

1. **Short GFS shakeout** (ec95d, 6h analysis + 6h forecast) with real `tide_fac`, MetGet GFS, fort.22 NWS=6, hotstart chain.  
2. **First adcprep failure** diagnosed and fixed: forecast fort.15 needs `NOUTM`/`NSTAM`/`NOUTGW` when NWS≠0.  
3. **Full-shaped run:** 6-day analysis + 5-day forecast from latest GFS 12Z cycle; both phases terminating normally.  
4. **Postprocess:** analysis + forecast graphs with obs enabled; then **stripped** runup/transect/GetObsElevation from the default path; switched CO-OPS to live product API.  
5. **Documented** into `/run-adcirc` skill, contracts, checklist, `references/proven-runs.md`, research note, DEV_NOTES.

## Durable artifacts

| Path | Role |
|------|------|
| `.grok/skills/run-adcirc/SKILL.md` | Full pipeline + scars |
| `.grok/skills/run-adcirc/references/contracts.md` | fort.15 / met / post contracts |
| `.grok/skills/run-adcirc/references/checklist.md` | Pre/post gates |
| `.grok/skills/run-adcirc/references/proven-runs.md` | Known-good case table |
| `notes/GROK/research/2026-07-25-run-adcirc-foundations.md` | Research + session evidence |
| `tide_fac.f` | Nodal factor source (compile native) |
| `GetBuoyWater.py` | Live CO-OPS product API |
| `generateGraphs.py` | GetObsElevation only if generateRunup |
| `Grapher.py` | `BYPASS_RUNUP_TRANSECT_OVERLAYS` |

## Case directories (local)

```text
~/projects/adcirc-local-smoke/
  ec95d_gfs_6h_20260725T2144Z/     # 6h+6h smoke
  ec95d_gfs_5d_2026072512/         # 6d analysis + 5d forecast
    analysis/  fort.63.nc fort.68.nc
    forecast/  fort.63.nc fort.22 fort.68.nc
    post_analysis/graphs/          # 30 PNGs + obs
    post_forecast/graphs/
    met/  MetGet owi
    run_manifest.json
  ec95d_run/                       # mesh source fort.13/14/15
```

## Key decisions

| Decision | Choice |
|----------|--------|
| Runtime | Local Mac only (not Unity) |
| Drive met | NWS=6 fort.22 via MetGet→OceanweatherTo306 |
| Mesh when drive offline | ec95d |
| Multi-day output | Hourly NOUTGE (NSPOOL=360 @ DT=10) |
| Default post | water + mesh maps + CO-OPS obs |
| Runup/transects/bathy | Opt-in `--generateRunup` only |
| MetGet auth | `source ~/projects/setApiKey.sh` |

## Hard lessons

1. Linux `a.out` tide_fac ≠ Mac — compile `tide_fac.f`.  
2. NWS flip without NOUTM/NOUTGW → adcprep death.  
3. ERDDAP CO-OPS mat endpoint is dead for ops; use product API.  
4. meshExists + obsExists used to drag in entire runup elevation/transect stack — wrong for surge post.  
5. Analysis does not need MetGet; parallelize.

## Current state checklist

- [x] Skill + references updated for full pipeline  
- [x] 6d/5d GFS run green  
- [x] Post stripped + live obs green (13/13 stations analysis)  
- [ ] Continuous ½ h analysis chain  
- [ ] v18 on external bootstrap when mounted  
- [ ] padcswan / waves mode local  

## Next session (`/init` then)

1. Read this handoff + `references/proven-runs.md`.  
2. Prefer **attach** existing fort.68 for new forecasts once continuous analysis exists; else coldstart multi-day once.  
3. Do not re-enable runup overlays unless user asks.  
4. Optional: datum alignment (MSL obs vs model) for quantitative skill scores.

---

*Coastal sister of CloudVision. Atmosphere stays in CloudVision; here = ADCIRC(+SWAN) + RICHAMP postprocess.*
