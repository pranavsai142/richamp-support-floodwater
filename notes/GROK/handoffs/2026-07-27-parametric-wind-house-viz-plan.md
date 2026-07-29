# Plan — Parametric wind → integrated house viz (2026-07-27)

**Status:** research complete; implement deferred  
**Research SoT:** `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
**Wiki:** `notes/WIKI/parametric-wind-pipeline.md`  
**Prior house law:** `2026-07-25-richamp-support-web-orders-complete-handoff.md`

---

## Goal

Make **NHC parametric / windgfdl wind** a first-class, honestly labeled wind source in the dual-suite house (fieldpack export + suite shell), without inventing geometry, without a second SPA, and without silently calling it “GFS.”

## Non-goals (this ladder)

- Reimplement or reverse-engineer `windgfdl`
- Full ASGS post_init automation close (TODO remains; document only)
- Parametric rain adapter (note only; promote later)
- Runup / waves golden (orthogonal open gaps)
- Mac-native rebuild of windgfdl

## Preferred path (locked by research)

**P0 — Raw parametric netCDF as regular lat/lon wind**

```text
track → generateParametricInput → windgfdl → richamp.wnd
     → owi2wind → parametric.nc  (wind_u, wind_v, PSFC)
     → new field adapter wind_parametric (clone wind_gfs)
     → fieldpack stream "parametric"
     → suite shell: same wind layers / particles as GFS
```

Evidence: owi2wind `OwiNetcdf` already writes MetGet-class var names.

**P1 fallback:** `scale_and_subset` → `RICHAMP_wind.nc` → existing `wind_post` (stride required).  
**P2:** drive ADCIRC → fort.74 (mesh truth, not library).  
**P3:** optional later `parametric_bridge` CLI for one-shot track→fort.22 (ops QoL).

## Ordered implement slices (next sessions)

| # | Slice | Deliverable | Gate |
|---|-------|-------------|------|
| 0 | Golden fixture | One short-window parametric `.nc` (or subset) under a case or `test/fixtures/` | `ncdump -h` shows wind_u/v |
| 1 | Adapter | `post/export/field_adapters/wind_parametric.py` + `__init__` import | export writes fields; long_name says parametric |
| 2 | CLI / paths | resolve `parametric_wind.nc`, `--path wind_parametric=…` | cli dry-run finds product |
| 3 | Contract doc | `ADCIRC_FIELDPACK_V0.md` sources row + stream `"parametric"` | doc matches meta |
| 4 | Fidelity policy | basin pack: require `--wind-stride` or bbox subset; record in `meta.fidelity` | no silent full-basin ship |
| 5 | Shell | source label in layer registry / case picker (minimal) | G-HOUSE still pass; wind scrub on parametric stream |
| 6 | Optional ops | thin `/run-adcirc` pointer to wiki parametric recipe | skill stays thin |
| 7 | Optional drive loop | fort.15 domain paste checklist when NWS=6/306 from windgfdl | run-adcirc checklist line |

## Success bar

Human: open suite shell, load a coastal pack that includes parametric wind, scrub real times, see u/v/speed/particles with **units from meta** and source **not labeled GFS**.  
Machine: `verify_pack` + `verify-fieldpack.js` + existing shell gates still green.

## Expanded scope (same day)

User expanded to **full house integration**: scenario catalog structure, seamless dropdown + default date, **track overlay required with parametric**, NHC shapefile path.  
**Authoritative design for full scope:** `2026-07-27-parametric-full-house-integration-design.md`  
**Handoff:** `2026-07-27-parametric-full-house-integration-handoff.md`  
**Research:** `notes/GROK/research/2026-07-27-house-scenario-catalog-and-tracks.md`

## Dependencies

- House ORDER 0–11 complete (done)
- owi2wind is306 fix (done)
- Golden `.nc` or ability to run windgfdl on Linux / use archive
