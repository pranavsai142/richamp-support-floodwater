# 2026-07-27 — Handoff: Full parametric + scenario catalog + track integration

> **SUPERSEDED for integration law (2026-07-28):**  
> Parametric run completed (Lee dual campaign). Use  
> **`2026-07-28-house-multi-scenario-compare-handoff.md`** + design sibling +  
> `notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md`.  
> This document remains historical for pre-golden requirements.

**Session type:** expand requirements after user intent — full house integration  
**Status:** research + design complete; implement not started  
**Primary design:** `2026-07-27-parametric-full-house-integration-design.md`  
**Earlier (still valid) subset:** `2026-07-27-parametric-wind-house-viz-design.md`  
**Research:**

1. Parametric pipeline — `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md`  
2. Scenario catalog + tracks — `notes/GROK/research/2026-07-27-house-scenario-catalog-and-tracks.md`  

---

## 1. One-screen status

| Item | State |
|------|--------|
| Scenario dropdown today | **`data/packs.json`** → `{label, url, suite}` → `loadPack` — works, but **thin** |
| “Scenario inventory” UI | Product checklist of **loaded** pack — **not** the catalog |
| Case scenario law | **`run_manifest.json`** (s9.v1) already has `modes.wind`, products, timeline |
| Fieldpack scenario block | **Missing** — only modes bools + run_id |
| Parametric wind in pack | Designed, not implemented |
| Track / NHC shapefiles in pack | **Missing** — offline only |
| Shapefile download path | **`generateRunProperties.py`** → NHC `_5day_latest.zip` → `Track.*` / `Cone.*` / `Points.*` |
| Custom track shp | **`generateTrackShapefile.py`** |
| Full integration design | **This handoff + full design doc** |

---

## 2. What you asked for (captured)

> From track → windgfdl is the generator path, but **raw driving data** matters most.  
> House dropdown should **choose scenarios** seamlessly (right pack, right date).  
> Scenarios need a **defined structure** (pack family is the seed).  
> When forcing is **parametric**, load **track with it** (nice UX + science).  
> Pull shapefiles the way postprocess already does — research `generateRunProperties` + scale/subset world.

---

## 3. How scenarios work today (research verdict)

```text
packs.json  ──select──►  fieldpack URL  ──load──►  meta.fields[] + mesh + stations
                              ▲
                     case products/fieldpack
                              ▲
                     run_manifest.json (ops identity, partially copied)
```

- **Seamless switch** already means: clear scene, load new pack, rebuild layers.  
- **Missing for “parametric Milton”:** met family, storm card, default absolute time, track overlay.  
- Do **not** invent a second product format — **enrich** catalog + manifest + pack meta + `tracks/`.

---

## 4. Full integration north star

| Layer | Role |
|-------|------|
| **run_manifest** | Scenario definition at case root (`modes.wind=parametric_nws306`, track_source, default_utc, storm{}) |
| **fieldpack** | Display SoT: water + parametric wind + **tracks/drive_track.json** (+ optional NHC GeoJSON) + `meta.scenario` |
| **packs.json** | Shell dropdown index (label, url, suite, optional default_utc / met_family) |

**Invariant:** Parametric scenario ⇒ **wind product + driving track from the same track file** in one pack; track layer **on by default**.

---

## 5. Shapefile / track law (offline)

### generateRunProperties (TC path)

1. Parse storm/advisory/year from `adcirc_simulation.1`  
2. `generateParametricInput.main(fort.22)`  
3. Download `http://www.nhc.noaa.gov/gis/forecast/archive/al{SS}{YYYY}_5day_latest.zip`  
4. Rename: `*lin*` → `Track.*`, `*pgn*` → `Cone.*`, `*pts*` → `Points.*`  

### generateTrackShapefile

Custom/historical track text → `Track.shp` polyline + WGS84 `.prj`.

### House export

Convert to **GeoJSON / JSON in the pack** — do not serve raw shapefiles to the browser.

---

## 6. Implement order (from full design)

| PR | Deliverable |
|----|-------------|
| **A** | Scenario schema docs + catalog fields + optional default_utc scrub |
| **B** | Track export + shell track layer |
| **C** | Parametric wind adapter + size stride |
| **D** | Glue: meta.scenario, parametric ⇒ track default on, inventory |
| **E** | NHC GIS → GeoJSON optional |
| **F** | Golden Milton/Erin staged + packs.json card + screenshots |

B ‖ C after A is fine.

---

## 7. Next session start

```text
/init
Read:
  notes/GROK/handoffs/2026-07-27-parametric-full-house-integration-handoff.md
  notes/GROK/handoffs/2026-07-27-parametric-full-house-integration-design.md
  notes/GROK/research/2026-07-27-house-scenario-catalog-and-tracks.md

Implement PR-A then PR-B (or PR-C if golden parametric nc is ready).
No second SPA. Fieldpack SoT. Parametric without track is incomplete.
```

---

## 8. Open items

- Soft vs hard verify parametric without track  
- Pin NHC advisory zip vs `_latest`  
- Golden parametric nc on this machine (windgfdl Linux-only)  
- Wave spatial / basemap / wind-bridge loop (unchanged house gaps)  

---

## 9. Anti-patterns

- Calling the inventory rail the “scenario system”  
- Storing science only in packs.json  
- Parametric wind labeled GFS  
- Track path that is not the PWM driver  
- Pasting MetGet track domain into fort.15 PWM met line  
- Shipping .shp as display SoT  

---

*Dropdown picks a pack. The pack is the scenario you can see. Parametric means the track that wrote the wind rides with it.*
