# 2026-07-27 — Handoff: /run-adcirc with parametric forcing · Hurricane Lee golden

**Status:** research + design complete — **EXECUTED 2026-07-28** (see dual campaign)  
**Actual cases:** `ec95d_lee_param_20230909` + GFS twin `ec95d_lee_gfs_20230909` on external smoke root (clocks 2023-09-09, not the draft 09-05 id).  
**House follow-on:** `2026-07-28-house-multi-scenario-compare-handoff.md`  
**Goal:** Generate a full ADCIRC + RICHAMP post case using **NHC parametric wind** so house-viz work has real files (track, wnd, fort.22, fort.63, graphs, properties).

| Companion | Path |
|-----------|------|
| Research | `notes/GROK/research/2026-07-27-run-adcirc-parametric-lee.md` |
| Plan | `notes/GROK/handoffs/2026-07-27-run-adcirc-parametric-lee-plan.md` |
| Design | `notes/GROK/handoffs/2026-07-27-run-adcirc-parametric-lee-design.md` |
| Prior parametric ops | `2026-07-27-parametric-wind-pipeline.md` |
| House integration (later) | `2026-07-27-parametric-full-house-integration-handoff.md` |
| Skill base | `.grok/skills/run-adcirc/SKILL.md` |

---

## 1. One-screen status

| Item | State |
|------|--------|
| GFS run-adcirc path | Proven (ec95d 5d) |
| Parametric run-adcirc path | **Designed for Lee — not yet run** |
| TC post path (`TC_FORCING`) | Mapped from `post_init.scr` |
| windgfdl on Mac | Linux ELF — Docker/Unity required |
| generateParametricInput in post_init | **Commented out** — must call explicitly |
| House needs this golden before track UI | Yes |

---

## 2. Why this before more house viz

> Don’t only “design track layers” — **generate the parametric run religiously**, keep every intermediate, then integrate house against real `$CASE` outputs.

The Floodwater TC path already does generateRunProperties, windgfdl, scale_and_subset, graphs, Track shapefiles. Local golden = same science, pathway A, no Slurm.

---

## 3. TC env vars (names that exist in repo)

| Name | Where | Meaning |
|------|--------|---------|
| **`TC_FORCING=True`** | post_init.scr | Use windgfdl / richamp.wnd / owi-306 / parametric rain (not MetGet GFS post box) |
| **`PARAMETRIC_WIND=True`** | post_init | `-parametric true` on scale_and_subset |
| **`RICHAMP_TC_FORCING=on`** | scale_and_subset.scr | Matlab inundation label NHC vs GFS only |

There is **no** `USE_TC_FORCING` symbol — use **`TC_FORCING`**.

---

## 4. Lee campaign (locked defaults)

| Field | Value |
|-------|--------|
| Storm | **Hurricane Lee**, AL **13**, **2023** |
| Coldstart | **2023-09-05 00:00 UTC** |
| Analysis | RNDAY **6**, NWS=**0** |
| Forecast end | **2023-09-17 00:00 UTC** |
| Forecast RNDAY | **12**, NWS=**6**, IHOT=**368** |
| fort.15 met domain | `565 625 51.000000 -101.000000 0.083333 0.083333 3600` |
| Mesh (first golden) | **ec95d** process smoke |
| Case id | `ec95d_lee_param_20230905` |
| Work root | `~/projects/adcirc-local-smoke/` |

---

## 5. Execution spine (next session)

```text
/run-adcirc parametric lee

S0  Stage ec95d case
S1  fort.15 clocks (Lee table above) + NOUTM/NOUTGW on forecast
S2  tide_fac native
S3p MetGet Lee track → generateParametricInput → windgfdl (Docker) → fort.22
    [pressure unit gate]
S4  Analysis NWS=0 → fort.68
S5  Forecast attach + padcirc NWS=6
S9p Post: owi2wind, scale_and_subset -parametric, graphs, NHC GIS properties/
S9e Optional fieldpack (path override until wind_parametric lands)
S10 run_manifest + proven-runs.md + skill S3p note
```

Full commands: **research note §8**.  
Expected tree: **research note §9**.

---

## 6. Critical scars to not relearn

1. post_init **does not** auto-call generateParametricInput (commented) — you must.  
2. generateRunProperties TC GIS needs ASGS log **or** manual NHC zip / shapefile.  
3. Track MetGet domain ≠ PWM fort.15 domain.  
4. windgfdl **Linux only**.  
5. fort.22 pressure **Pa** (check windgfdl output).  
6. Met time coverage **coldstart → forecast end**.  
7. Matlab optional; Python products are the house gold.

---

## 7. Sample products house will consume

| Need | Path under `$CASE` |
|------|---------------------|
| Drive track | `met_pwm/*.trk`, `track.richamp` |
| PWM wind | `met_pwm/richamp.wnd`, `lee_parametric_wind.nc` |
| ADCIRC water | `forecast/fort.63.nc` |
| NHC GIS | `properties/Track.*` (Cone/Points) |
| Storm props | `properties/run.properties` |
| Graphs | `post_forecast/graphs/`, `post_wind/graphs/` |
| Manifest | `run_manifest.json` |

---

## 8. Next session start prompt

```text
/init
Then: /run-adcirc parametric lee

Read first:
  notes/GROK/handoffs/2026-07-27-run-adcirc-parametric-lee-handoff.md
  notes/GROK/research/2026-07-27-run-adcirc-parametric-lee.md
  .grok/skills/run-adcirc/SKILL.md (S0–S2, S7–S9; replace met with S3p)

Execute phases 0–10. Stop on first failed gate with diagnosis.
Do not invent fort.15 domain — use 565×625 PWM line.
Do not use MetGet GFS for drive met.
```

---

## 9. After green run

1. Append to `references/proven-runs.md` as **Run D — Lee parametric**.  
2. Thin skill section **S3p** + footgun list.  
3. Tell house session: `$CASE` is the fixture root.  
4. Only then implement track layer / wind_parametric against real files.

---

## 10. Open items (execution)

- [ ] MetGet Lee track domain id works in 2026  
- [ ] Docker windgfdl produces richamp.wnd  
- [ ] Pressure unit confirmation  
- [ ] Analysis + forecast green  
- [ ] Post graphs + properties  
- [ ] Manifest + proven-runs  

---

*One track writes the parametric wind. One fort.22 drives the water. One case tree teaches the house.*
