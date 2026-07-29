# Design — Full house integration: parametric wind + scenario catalog + track

> **SUPERSEDED for compare + real fixtures (2026-07-28):**  
> `2026-07-28-house-multi-scenario-compare-design.md` + inventory research.  
> Catalog/track ideas below remain useful; Lee dual paths replace Milton stubs.

**Date:** 2026-07-27  
**Supersedes for scope:** expands (does not delete) `2026-07-27-parametric-wind-house-viz-design.md`  
**Research:**

- `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md` — track → windgfdl → nc  
- `notes/GROK/research/2026-07-27-house-scenario-catalog-and-tracks.md` — packs.json, run_manifest, NHC shapefiles  

**Shell:** `~/projects/CloudVision/threejs-shield-live-viz/`  
**Bar:** scientific integrity ≥ offline RICHAMP; one shell; fieldpack SoT

---

## 1. Overview / Motivation

The user wants **full integration**, not only “add a wind adapter”:

1. **Raw driver first** — the track (and domain) that feeds PWM matters as much as the gridded wind.  
2. **Scenario dropdown** — pick a scenario and seamlessly load the right pack, time window, and defaults.  
3. **When met is parametric** — **always show the driving track** (and optionally NHC cone/points shapefiles).  
4. **Scenario structure** — define scenarios deliberately; the pack family is already the display SoT, but the catalog card and case manifest must carry met/track identity.

Today the house can switch Ida vs ec95d GFS via `data/packs.json`, but cards are only `{label, url, suite}`. “Scenario inventory” is a product checklist of the loaded pack, not a scenario catalog. Tracks/shapefiles exist offline (`generateRunProperties`, `generateTrackShapefile`) but **never enter the fieldpack or shell**.

---

## 2. Goals & Non-Goals

### Goals

| # | Goal |
|---|------|
| G1 | Enrich **scenario catalog** so the topbar dropdown is a real scenario picker (met family, storm, default time). |
| G2 | Export **parametric wind** as first-class pack product (prior design P0). |
| G3 | Export **driving track** into the pack; shell draws track on globe + 2D. |
| G4 | When scenario/pack is parametric, **track layer on by default**. |
| G5 | Optional NHC Track/Cone/Points (from generateRunProperties zip) as pack overlays. |
| G6 | Preserve run_manifest as case-level scenario law; pack meta as display law; packs.json as shell index. |
| G7 | Absolute-time default on load (`default_utc` → nearest master-stream index). |

### Non-Goals

- Second SPA or MapLibre fork  
- Shipping raw `.shp` to the browser without conversion  
- Reimplementing windgfdl on Mac  
- Multi-tenant auth / SaaS scenario server  
- Auto-scraping all NHC storms into packs  

---

## 3. Scenario structure (three layers — do not collapse)

```text
┌─────────────────────────────────────────────────────────────────┐
│ 1. CASE — run_manifest.json (ops / science scenario)            │
│    run_id, modes.wind, products{}, coldstart, timeline, storm{} │
├─────────────────────────────────────────────────────────────────┤
│ 2. FIELDPACK — products/fieldpack/ (display SoT)                │
│    meta.json + mesh + fields + stations + tracks/               │
├─────────────────────────────────────────────────────────────────┤
│ 3. SHELL CATALOG — data/packs.json (or scenarios.json)          │
│    id, label, url, suite, optional card mirrors for UX          │
└─────────────────────────────────────────────────────────────────┘
```

**Rules:**

- Science always comes from the **loaded pack**.  
- Catalog cards may mirror labels for the dropdown; on load, **pack meta wins** if they disagree.  
- GFS and parametric scenarios are **different cards** (different packs or different met product sets), not a toggle that invents wind.

### 3.1 Case `run_manifest.json` extensions (s9.v1+)

Keep existing keys. Add:

```json
{
  "manifest_version": "s9.v1",
  "run_id": "v18_milton_param_adv13",
  "modes": {
    "water": true,
    "mesh": true,
    "waves": true,
    "wind": "parametric_nws306",
    "rain": "parametric",
    "track": true,
    "obs": true
  },
  "storm": {
    "name": "Milton",
    "basin": "AL",
    "number": "14",
    "year": 2024,
    "advisory": "013",
    "stormtype": "nhc"
  },
  "products": {
    "fort63_water": "…",
    "fort14_mesh": "…",
    "track_source": "met/nhc_merge_2024_al_14_013.trk",
    "parametric_wind_nc": "met/milton_parametric_wind.nc",
    "wind_inp": "met/Wind_Inp.txt",
    "nhc_gis_dir": "properties/",
    "fort22_met": "forecast/fort.22"
  },
  "timeline": {
    "window_utc": ["2024-10-06T00:00:00Z", "2024-10-16T00:00:00Z"],
    "default_utc": "2024-10-09T18:00:00Z",
    "met_domain": "565 625 51.000000 -101.000000 0.083333 0.083333"
  }
}
```

`modes.wind` values (controlled vocabulary):

| Value | Meaning |
|-------|---------|
| `gfs_nws6_fort22` | MetGet GFS fort.22 (current ec95d) |
| `parametric_nws6` | windgfdl / PWM, circulation only |
| `parametric_nws306` | PWM + SWAN |
| `shield_owi` | SHiELD wind bridge |
| `none` / omit | tides-only |

### 3.2 Fieldpack `meta.scenario` (written by export)

```json
"scenario": {
  "id": "v18_milton_param_adv13",
  "label": "Milton AL14 — parametric · v18 · adv 13",
  "suite": "coast",
  "storm": { "…same as manifest…" },
  "met": {
    "family": "parametric",
    "nws": 306,
    "domain_line": "565 625 51.000000 -101.000000 0.083333 0.083333",
    "track_source": "nhc_merge_2024_al_14_013.trk"
  },
  "default_utc": "2024-10-09T18:00:00Z"
}
```

Also keep `modes.track: true` when drive track is present.  
**Do not** collapse `modes.wind` to a bare boolean when scenario.met exists — retain boolean for legacy verifier **or** extend verifier to accept string/object.

### 3.3 Shell catalog entry (backward compatible)

```json
{
  "id": "v18_milton_param_adv13",
  "label": "Milton AL14 — parametric wind · v18 · adv 13",
  "url": "./data/coast-milton-param",
  "suite": "coast",
  "default_utc": "2024-10-09T18:00:00Z",
  "met_family": "parametric"
}
```

Minimal legacy entries (`label`/`url`/`suite` only) still work.

---

## 4. Technical requirements

### 4.1 Scenario catalog & load

| ID | Requirement |
|----|-------------|
| FR-S1 | Dropdown built from catalog; changing selection loads that pack and clears stale layers (already true). |
| FR-S2 | After load, if `default_utc` (catalog or pack) is set, scrubber jumps to **nearest time on master stream** by absolute ISO time. |
| FR-S3 | Deep link may use `?pack=` + `?t=` and optionally `?t_utc=`. |
| FR-S4 | Inventory rail shows met family, track present/absent, parametric wind stream. |
| FR-S5 | Pack meta overrides catalog for storm/met labels in the meta drawer. |

### 4.2 Parametric wind (from prior design)

| ID | Requirement |
|----|-------------|
| FR-W1–W9 | As in parametric-wind design (adapter, stream, labels, stride, units). |
| FR-W10 | When `met.family=parametric`, inventory marks wind source parametric, not GFS. |

### 4.3 Track

| ID | Requirement |
|----|-------------|
| FR-T1 | Export `--products track` (or auto when parametric + track_source exists) writes `tracks/drive_track.json`. |
| FR-T2 | Drive track lon/lat/time come from the **same track file** that fed generateParametricInput / windgfdl — no invented path. |
| FR-T3 | Optional: convert NHC `Track.shp` / `Cone.shp` / `Points.shp` → GeoJSON under `tracks/`. |
| FR-T4 | Shell layer `track` (polyline) + optional `track_cone` (polygon) + `track_points`. |
| FR-T5 | If `meta.scenario.met.family === "parametric"` **or** `modes.track` and drive track exists → **track visible by default**. |
| FR-T6 | Optional marker at track position nearest current scrub time (storm center hint). |
| FR-T7 | No NetCDF track requirement — JSON/GeoJSON only in pack. |

### 4.4 Offline shapefile pipeline (document + export hook)

| ID | Requirement |
|----|-------------|
| FR-G1 | Document generateRunProperties NHC zip → Track/Cone/Points rename. |
| FR-G2 | Document generateTrackShapefile for historical/custom tracks. |
| FR-G3 | Export accepts `--path nhc_gis=properties/` or manifest `products.nhc_gis_dir`. |
| FR-G4 | Prefer drive_track from track file; NHC GIS is **supplemental** official overlay. |

### Non-functional

| ID | Requirement |
|----|-------------|
| NFR-1 | No second SPA; Path B only. |
| NFR-2 | G-HOUSE / G-LOAD still pass when switching GFS ↔ parametric packs. |
| NFR-3 | Track geometry finite lon/lat only; refuse empty track silently labeled OK. |
| NFR-4 | Catalog may be hand-edited; optional generator later. |

---

## 5. User stories

### US-S1 — Scenario dropdown with identity

**As** a dual-suite user, **I can** open the topbar dropdown and see labeled scenarios (e.g. “Ida 36h atmos”, “ec95d GFS coast”, “Milton parametric v18”), **so that** I pick science by name not by path.

**AC:** packs.json entries with labels; selecting Milton loads Milton pack; meta drawer shows storm + met family from pack.

### US-S2 — Land on the right date

**As** a scientist, **I can** select a multi-day scenario and land near a meaningful default time (e.g. landfall window), **so that** I do not scrub from coldstart every time.

**AC:** `default_utc` → nearest master-stream index; deep link round-trips that time.

### US-P1 — Parametric scenario loads wind + track together

**As** a modeler comparing forcing, **I can** select a parametric scenario and immediately see PWM wind (or particles) **and** the driving track, **so that** the vortex and the track that generated it are one story.

**AC:** track layer default on; param wind fields present; inventory shows both; source ≠ GFS.

### US-T1 — NHC cone when available

**As** a forecaster-minded user, **I can** toggle the official NHC cone under the drive track, **so that** I compare PWM track geometry to the advisory cone.

**AC:** if GeoJSON cone in pack, layer toggle works; if absent, inventory ✗ cone, no crash.

### US-O1 — Operator registers a new scenario

**As** an operator, **I can** export a case fieldpack, symlink under `data/`, add one catalog card, **so that** the scenario appears in the house without code changes.

**AC:** three steps documented; G-LOAD on new pack path.

---

## 6. Technical guidelines (invariants)

1. **Fieldpack is display SoT** — including track geometry once exported.  
2. **Raw track drives parametric** — drive_track must cite the same source file as PWM.  
3. **Three boxes stay distinct** — MetGet track download domain ≠ PWM 565×625 ≠ RI GFS post box.  
4. **Honest met labels** — never call parametric wind GFS.  
5. **Parametric ⇒ track** — UI default; verifier may soft-warn if parametric without track.  
6. **Catalog is an index** — not a second science store.  
7. **Shapefiles offline only** — convert to GeoJSON/JSON at export.  
8. **Stream-aware time** — track marker uses absolute time match to scrubber.  
9. **NaN / dry laws unchanged** for water.  
10. **Skills stay thin** — scenario recipe in wiki/handoff, not a novel skill dump.

---

## 7. Proposed design detail

### 7.1 Pack layout (tracks)

```text
fieldpack/
  meta.json
  tracks/
    catalog.json
    drive_track.json          # required for parametric scenarios
    nhc_track.geojson         # optional
    nhc_cone.geojson          # optional
    nhc_points.geojson        # optional
  mesh/  fields/  grids/  stations/
```

`tracks/catalog.json`:

```json
{
  "tracks": [
    { "id": "drive_track", "role": "forcing", "format": "series", "path": "tracks/drive_track.json" },
    { "id": "nhc_cone", "role": "advisory_cone", "format": "geojson", "path": "tracks/nhc_cone.geojson" }
  ]
}
```

### 7.2 Export modules

| Module | Role |
|--------|------|
| `field_adapters/wind_parametric.py` | PWM nc → fields (prior design) |
| `track_export.py` | track file → drive_track.json; optional shp→geojson |
| `cli.py` | products `track`, `wind_parametric`; path keys; write `meta.scenario` from manifest |
| `verify_pack.py` | if scenario.met.family=parametric, warn/fail without drive_track (policy: **warn** v0, **fail** v1) |
| `pack_writer.py` | `set_scenario()`, `add_track()` helpers |

### 7.3 Track parse sources (priority)

1. Explicit `--path track_source=`  
2. `run_manifest.products.track_source`  
3. `case/met/*.trk` / `track.richamp`  
4. `fort.22` ATCF-like lines (same family as generateParametricInput)

Parser should share conversion logic with `generateParametricInput` lat/lon helpers (or call into it carefully without forcing full PWM regen).

### 7.4 NHC GIS conversion

Offline already:

```text
generateRunProperties → properties/al{SS}{YYYY}_5day_latest.zip
  → Track.*  Cone.*  Points.*
```

Export:

```bash
# pseudocode
for name in Track Cone Points:
  if properties/{name}.shp exists:
    pyshp/fiona → tracks/nhc_{name.lower()}.geojson
```

**Pin advisory** when possible (manifest storm.advisory); document that `_latest` is non-reproducible.

### 7.5 Shell changes (suite-shell.js + loader)

| Change | Detail |
|--------|--------|
| Catalog | Read optional fields; show met badge in option text |
| loadPack | After build, `applyDefaultUtc(meta/catalog)` |
| Track layer | Polyline from drive_track lon/lat; color by suite; z-order above mesh, below stations |
| Cone layer | Optional fill from GeoJSON |
| Inventory | met family, track, cone, parametric wind |
| Particles | Prefer parametric vector when that scenario’s active wind vector is parametric |

### 7.6 Seamless scenario switch sequence

```text
user selects card
  → stopPlay, clear station
  → loadFieldpack(url)
  → rebuild layers from meta only
  → if parametric: track.on = true; prefer param wind field in field-select if present
  → setTime(nearest(default_utc || t0))
  → buildInventory (honest ✓/✗)
  → pushUrlState
```

---

## 8. Boilerplate

### 8.1 drive_track.json

```json
{
  "id": "drive_track",
  "role": "forcing",
  "source": "nhc_merge_2024_al_14_013.trk",
  "crs": "EPSG:4326",
  "times_utc": ["2024-10-06T00:00:00Z"],
  "lon": [-90.1],
  "lat": [22.4],
  "vmax_kt": [30],
  "mslp_mb": [1008],
  "label": "driving track (PWM input)"
}
```

### 8.2 packs.json card

```json
{
  "id": "milton-param",
  "label": "Milton — parametric · coast",
  "url": "./data/coast-milton-param",
  "suite": "coast",
  "met_family": "parametric",
  "default_utc": "2024-10-09T18:00:00Z"
}
```

### 8.3 Export CLI sketch

```bash
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir $CASE/forecast --mesh $CASE/forecast/fort.14 --case $CASE \
  --products mesh,water,wind_parametric,track,stations,obs_water \
  --path wind_parametric=$CASE/met/milton_parametric_wind.nc \
  --path track_source=$CASE/met/nhc_merge_2024_al_14_013.trk \
  --path nhc_gis=$CASE/properties \
  --wind-stride 2 \
  --outdir $CASE/products/fieldpack
```

### 8.4 Staging

```bash
ln -sfn $CASE/products/fieldpack $VIZ/data/coast-milton-param
# edit $VIZ/data/packs.json — add card
```

---

## 9. Alternatives considered

| Alt | Why not |
|-----|---------|
| Only path-override wind_gfs | Lies about source; no track story |
| Browser reads shapefile from case dir | Breaks fieldpack SoT; multi-file pain |
| Scenario = folder of raw fort files in browser | Rejects house law |
| One mega suite-fieldpack with all storms | Huge; harder gates; keep one pack per scenario |
| Catalog as sole SoT without pack scenario block | Dropdown survives offline copy poorly |

---

## 10. Key decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Scenario definition home | run_manifest + pack meta.scenario; packs.json index | Matches existing ops + display split |
| Track in pack | JSON series + optional GeoJSON | Web-native; stations-like |
| Parametric default UI | Track on | User priority: driver visible |
| NHC shapefiles | Offline generateRunProperties + export convert | Existing code path |
| default_utc | Catalog and/or pack | Seamless “right date” |
| modes.wind | String vocabulary in manifest | Already used (gfs_nws6_fort22) |
| windgfdl | Still offline generator | Raw track + nc are house inputs |

---

## 11. PR plan (ordered)

### PR-A — Scenario meta + catalog schema (docs + thin code)

- Document schema in `ADCIRC_FIELDPACK_V0.md`  
- Extend packs.json schema in shell README  
- Optional: shell reads `default_utc` if present (small)  
- **No** parametric required yet  

### PR-B — Track export + shell track layer

- `track_export.py`, cli product `track`  
- loader + suite-shell polyline layer  
- Gate: pack with track draws ≥ N segments; G-HOUSE still pass  

### PR-C — Parametric wind adapter + stride (prior design)

- `wind_parametric.py`  
- Prefer vector for particles when present  

### PR-D — Parametric scenario glue

- Export writes `meta.scenario` from run_manifest  
- Default track-on when parametric  
- Inventory met family  
- Soft verify: parametric ⇒ track recommended  

### PR-E — NHC GIS optional path

- shp→geojson in export when properties/ present  
- Cone/points layers  

### PR-F — Ops golden

- One Milton or Erin parametric case staged + packs.json card  
- Screenshots for G-MULTI + track  

**Dependency order:** A → B → C → D → E/F (B and C can parallel after A).

---

## 12. Verification matrix

| Gate | Meaning |
|------|---------|
| G-PACK | Export includes track JSON when requested; coords finite |
| G-LOAD | Loader accepts tracks/ without breaking atmos packs |
| G-TRACK | Drive track visible; ≥1 segment; lon in (−180,180) |
| G-PARAM | Parametric wind fields + labels; not named GFS |
| G-SCEN | Dropdown switch A→B clears stale; default_utc applied |
| G-HOUSE | Atmos + coast still both work in one shell |
| G-OPS | Deep link pack + time (+ track vis) round-trip |

---

## 13. Open questions

1. Soft-warn vs hard-fail when parametric pack lacks track (recommend soft v0 / hard after golden).  
2. Storm-center marker: always vs only when scrub time within track window.  
3. Advisory-pinned NHC zip URL vs `_latest` for reproducibility.  
4. Whether `suite-fieldpack/v0` ever bundles atmos+coast for one named storm (later).  
5. Auto-generate packs.json from a cases root (nice-to-have).  

---

## 14. References

- `data/packs.json`, `suite-shell.js` pack picker / inventory  
- `generateRunProperties.py` — NHC zip → Track/Cone/Points  
- `generateTrackShapefile.py` — custom track → shp  
- `run_manifest.json` s9.v1 (ec95d)  
- Prior parametric design + research notes (same date stem)  
