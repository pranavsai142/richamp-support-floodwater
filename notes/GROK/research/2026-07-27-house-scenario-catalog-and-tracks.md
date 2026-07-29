# Research — House scenario catalog + storm tracks (2026-07-27)

**Mission:** Understand how the suite live-viz “scenario” dropdown works today, how cases/scenarios should be *defined* for full integration (especially **parametric wind**), and how NHC track / cone / points shapefiles are produced offline so the house can show the **driving track** with parametric met.

**Parallel to:** `2026-07-27-parametric-wind-pipeline.md`  
**Shell code:** `~/projects/CloudVision/threejs-shield-live-viz/`

---

## 1. What the dropdown actually is today

### 1.1 Catalog file: `data/packs.json`

```json
{
  "note": "packs served by this shell; add entries or use ?pack=<url>",
  "packs": [
    {
      "label": "Ida 36h — SHiELD/FV3 nest + cube tiles",
      "url": "./data/fieldpack",
      "suite": "atmos"
    },
    {
      "label": "ec95d GFS 5d forecast — ADCIRC coast",
      "url": "./data/coast-ec95d",
      "suite": "coast"
    }
  ]
}
```

| Field | Role today |
|-------|------------|
| `label` | Dropdown text |
| `url` | HTTP path to a **fieldpack directory** (must be served statically) |
| `suite` | Cosmetic tag in the option text (`[atmos]` / `[coast]`) |

**Not present today:** storm name, advisory, met family (GFS vs parametric), time window, track path, coldstart, mesh id, “default date to open on.”

### 1.2 Shell wiring (`suite-shell.js`)

| Piece | Behavior |
|-------|----------|
| `#pack-select` | Built by `buildPackPicker(packs)` from `packs.json` |
| On change | `stopPlay()` → clear field/station → **`loadPack(url, {})`** |
| `loadPack` | `Loader.loadFieldpack(url)` → clear scene → rebuild layers from **that pack’s `meta.json`** only |
| Deep link | `?pack=<url>&t=&field=&layers=&view=&station=&c=` |
| “Scenario inventory” rail | **Not a catalog** — product checklist for the *already loaded* pack (fields present ✓/✗, stations, particles, tiles) |

**Seamless scenario switch today = swap fieldpack URL.** Time scrubber resets to `t=0` (or URL `t`) of the *new* pack’s default stream. There is no cross-pack “same absolute date” logic yet.

### 1.3 What is *not* a scenario object

| Artifact | What it is |
|----------|------------|
| Fieldpack | Display SoT for **one** exported realization |
| `run_manifest.json` | Case-level ops truth (modes, products, timeline) — **export reads it** into provenance / coldstart |
| `meta.json` | Pack-level science catalog (streams, fields, stations, modes) |
| `packs.json` | Thin **shell index** of packs |

So: scenarios *exist* as cases + packs, but the **dropdown schema is too thin** for “parametric Milton with track and open on landfall day.”

---

## 2. Case / pack law already in the suite (reuse, don’t invent)

### 2.1 `run_manifest.json` (example: ec95d GFS 5d)

```json
{
  "manifest_version": "s9.v1",
  "run_id": "ec95d_gfs_5d_2026072512",
  "pathway": "A_local_run-adcirc",
  "modes": {
    "water": true,
    "mesh": true,
    "waves": false,
    "wind": "gfs_nws6_fort22",
    "obs": false
  },
  "products": { "fort63_water": "…", "fort22_met": "…", "fort14_mesh": "…" },
  "coldstart": { "base_date_iso": "2026-07-19T12:00:00Z" },
  "timeline": {
    "gfs_cycle": "2026-07-25 12Z",
    "forecast_window_utc": ["2026-07-25T12:00:00Z", "2026-07-30T12:00:00Z"],
    "met_domain": "gfs 0.25 -98 7.5 -59.5 46.5"
  }
}
```

This is the **closest thing to a scenario definition** on the coastal side. Export already:

- sets `meta.run_id` from manifest  
- copies `coldstart_utc`  
- records provenance path  

**Gap:** `modes.wind` is a free string; house does not yet require or display `parametric_*` vs `gfs_*`. No track product paths in `products{}`.

### 2.2 Fieldpack `meta.json` (coast)

Already carries: `schema`, `run_id`, `phase`, `coldstart_utc`, `time_streams`, `fields[]`, `stations`, `bookmarks`, `modes` `{water, mesh, wind, rain, waves, runup}`, `provenance`, `fidelity`.

**Missing for parametric scenarios:**

- `modes.wind` detail (boolean only after export — cli collapses to true/false)  
- `storm` / track block  
- `scenario` card fields for the picker  
- track geometry product under pack layout  

### 2.3 Staging pattern (ops)

```bash
# symlink or rsync packs under the shell's data/
ln -sfn $CASE/products/fieldpack ./data/coast-ec95d
# list in packs.json → dropdown
```

That pattern **is** the scenario registration path today. Full integration extends the **JSON card**, not invents a second product religion.

---

## 3. Track & shapefile production (offline — first-party)

### 3.1 Path A — NHC GIS archive via `generateRunProperties.py`

When `adcirc_simulation.1` contains `get_advisory_time.py` (TC advisory metadata):

1. Parse start/end, storm, advisory, year.  
2. Call `generateParametricInput.main(indir + "/fort.22")` → PWM inputs + rain (side effect).  
3. Write `properties/run.properties` with `stormtype : nhc`, storm name/class/number/advisory/year, track LEFT/CENTER/RIGHT from path.  
4. **Download NHC 5-day GIS zip:**

```text
http://www.nhc.noaa.gov/gis/forecast/archive/al{SS}{YYYY}_5day_latest.zip
```

5. Extract under `properties/`; rename members:

| NHC fragment in filename | Renamed product |
|--------------------------|-----------------|
| `*lin*` (not ww_wwlin) | **`Track.*`** (shp/dbf/shx/…) |
| `*pgn*` | **`Cone.*`** |
| `*pts*` | **`Points.*`** |
| `ww_wwlin` | deleted |

**ASGS post contract** (root `README.md`): deliver `Track.dbf`, `Track.shp`, `Track.shx` as `postAdditionalFiles`.

**Caveats:**

- Uses `_5day_latest.zip` (advisory-specific URL is commented out) — **latest**, not pinned advisory.  
- Requires network at generate time.  
- Shapefile is ESRI binary — **not** browser-native; house needs GeoJSON / polyline JSON in the pack.  
- Only runs when TC metadata is found in the log; pure GFS → `stormtype : gfs` and **no shapefile download**.

### 3.2 Path B — Custom track → shapefile via `generateTrackShapefile.py`

```bash
python generateTrackShapefile.py <track.txt> <out/Track>
# e.g. 1938_night_track.txt → Track.shp polyline + .prj (WGS84)
```

Parses ATCF-like lat/lon tokens (`298N`, `0749W`), builds a **single polyline** with Azimuth attribute. Used for historical / modified tracks not in NHC “latest” GIS.

### 3.3 Path C — Track file products from parametric pipeline

| File | Role for viz track |
|------|--------------------|
| `track.richamp` | PWM input to windgfdl; fixed-width positions + heading |
| `.trk` / `fort.22` | Source track; also input to `generateParametricInput` |
| `TrackRMW.txt` | RMW / pressure time series (not geometry, but useful inspect panel) |
| NHC `Track.shp` | Official forecast track line (when TC zip available) |
| NHC `Cone.shp` | Uncertainty cone polygon |
| NHC `Points.shp` | Advisory points |

**For parametric forcing, the driving track is the scientific overlay** — not optional chrome. Prefer exporting a **canonical track series** derived from the same file that fed `generateParametricInput` (lon/lat/time/intensity), plus optional NHC GIS cone when available.

### 3.4 post_init relationship

`richamp_scale_and_subset_post_init.scr` TC branch runs `windgfdl`, sets `richamp.wnd` / owi-306; moves `track.richamp` into `properties/`. Shapefile download is **`generateRunProperties`**, not the scale script itself. README still lists Track.* as post deliverables.

---

## 4. Browser constraints (why we don’t ship .shp raw)

| Format | Shell feasibility |
|--------|-------------------|
| ESRI shapefile | Needs extra parser / shpjs; multi-file; awkward with static pack layout |
| GeoJSON FeatureCollection | First-class JSON; fetch with meta; Three.js / 2D easy |
| Pack-native `tracks/track.json` | Same family as `stations/catalog.json` — **recommended** |

**Recommended pack layout extension:**

```text
fieldpack/
  meta.json                 # + scenario + storm + tracks[] index
  tracks/
    catalog.json            # list of track layers
    drive_track.json        # driving track used for parametric (required if modes.wind is parametric)
    nhc_track.geojson       # optional official line
    nhc_cone.geojson        # optional
    nhc_points.geojson      # optional
  … mesh / fields / stations …
```

Driving track JSON minimum schema:

```json
{
  "id": "drive_track",
  "role": "forcing",
  "source": "nhc_merge_2024_al_14_013.trk",
  "crs": "EPSG:4326",
  "times_utc": ["2024-10-06T00:00:00Z", "…"],
  "lon": [-…],
  "lat": […],
  "vmax_kt": […],
  "mslp_mb": […],
  "rmw_km": […],
  "label": "Milton AL14 advisory 13 BEST/OFCL merge"
}
```

Optional GeoJSON layers for cone/points stay separate (different geometry type).

---

## 5. Expanded scenario card (what the dropdown should become)

### 5.1 Two layers of definition

```text
CASE (run_manifest.json)          ← ops / science scenario
   products/fieldpack/            ← display SoT
SHELL (packs.json / scenarios.json) ← catalog of available packs for the house
```

### 5.2 Proposed `packs.json` (or `scenarios.json`) entry

Backward compatible: old `{label, url, suite}` still load.

```json
{
  "id": "milton-parametric-v18-adv13",
  "label": "Milton AL14 — parametric wind · v18 · adv 13",
  "url": "./data/coast-milton-param",
  "suite": "coast",
  "storm": {
    "name": "Milton",
    "basin": "AL",
    "number": "14",
    "year": 2024,
    "advisory": "013"
  },
  "met": {
    "family": "parametric",
    "nws": 306,
    "domain": "565 625 51.000000 -101.000000 0.083333 0.083333",
    "track_source": "nhc_merge_2024_al_14_013.trk"
  },
  "time": {
    "coldstart_utc": "2024-10-06T00:00:00Z",
    "window_utc": ["2024-10-06T00:00:00Z", "2024-10-16T00:00:00Z"],
    "default_utc": "2024-10-09T18:00:00Z"
  },
  "mesh": "v18",
  "modes": { "water": true, "wind": "parametric", "waves": true, "track": true }
}
```

### 5.3 Seamless load behavior (target)

On dropdown change:

1. `loadPack(card.url)` as today.  
2. If `card.time.default_utc` (or pack `meta.scenario.default_utc`): set scrubber to **nearest timestamp on the master stream** (absolute time, not always t=0).  
3. If pack has `tracks/` and `modes.wind` is parametric (or `met.family === "parametric"`): **enable track layer by default**.  
4. Inventory rail shows: met family, track ✓, cone ✓/✗, parametric wind stream.  
5. Deep link includes `pack` + absolute `t` (or ISO) + track layer visibility.

### 5.4 Where truth lives

| Fact | Authoritative source |
|------|----------------------|
| Science fields, times, track geometry | **Fieldpack** (exported) |
| How the run was forced (parametric vs GFS) | `run_manifest.modes.wind` → pack `meta.modes` / `meta.scenario.met` |
| Dropdown labels & staging URLs | Shell `packs.json` (can be generated from cases) |
| NHC cone official GIS | Offline download → converted into pack (optional) |

Picker cards may **mirror** pack meta for UX, but must not contradict the loaded pack. On load, shell prefers pack meta over catalog for storm/met labels.

---

## 6. Parametric scenario = wind + track (invariant)

When a scenario is declared parametric wind forcing:

| Required in pack | Why |
|------------------|-----|
| Parametric (or drive) wind product on its stream | Raw met the user cares about |
| `tracks/drive_track.json` from the **same track file** that fed PWM | Scientific overlay of the driver |
| `meta.scenario.met.family = "parametric"` | Honest inventory / UI defaults |
| fort.15 domain recorded in meta (565×625 line) | Ops/debug parity |

Optional but high value:

- NHC Track/Cone/Points GeoJSON from `generateRunProperties` zip  
- `TrackRMW.txt` series in inspect drawer  
- Rain parametric (`RICHAMP_rain.nc`) as separate product  

**Raw data first:** track + Wind_Inp domain + `.wnd`/nc are the story; `windgfdl` is the generator between track and gridded wind, not the display SoT.

---

## 7. Export pipeline implications (design feed)

| New / extended piece | Role |
|----------------------|------|
| `post/export/track_export.py` | Parse track.richamp / trk / fort.22 → `tracks/drive_track.json` |
| Optional GIS convert | `Track.shp` → GeoJSON (pyshp or ogr) into `tracks/` |
| `cli --products …,track` | Opt-in product |
| `cli` modes | `modes.wind` string or nested met block; `modes.track` |
| `run_manifest` products | `track_source`, `parametric_wind_nc`, `nhc_gis_dir` |
| Shell | Track layer (globe + 2D polyline); catalog card schema; default_utc scrub |
| `packs.json` generator | Optional: scan cases → write catalog (later) |

---

## 8. Gaps ranked

1. **No track product in fieldpack / shell** — biggest UX gap for parametric.  
2. **packs.json too thin** — no met family, storm, default time.  
3. **modes.wind collapsed to bool** on export — loses `gfs_nws6` vs `parametric`.  
4. **NHC zip is “latest”** — not reproducible advisory pin.  
5. **Shapefile not web-native** — conversion step required.  
6. **Absolute time on pack switch** — only index-based today.  
7. **generateRunProperties TC detection** depends on ASGS log line — pure manual parametric cases need explicit storm metadata in run_manifest.

---

## 9. Verdicts

| Question | Verdict |
|----------|---------|
| Is scenario structure already there? | **Partially** — fieldpack + run_manifest + packs.json; dropdown is pack index only |
| Can we “just” use packs.json? | Yes as **index**; must **enrich** cards + pack meta for parametric/track |
| Where do shapefiles come from? | `generateRunProperties` NHC zip rename; or `generateTrackShapefile` for custom tracks |
| What must load with parametric? | Gridded parametric wind **and** driving track overlay from same track source |
| Invent new SPA? | **No** — extend catalog + pack layout + one track layer |

---

## 10. Citations

- `CloudVision/threejs-shield-live-viz/data/packs.json`  
- `suite-shell.js` — `buildPackPicker`, `loadPack`, `buildInventory`  
- `post/export/cli.py` — run_manifest → meta; modes bool collapse  
- `post/export/ADCIRC_FIELDPACK_V0.md` — layout  
- `generateRunProperties.py` L57–104 — TC properties + NHC zip → Track/Cone/Points  
- `generateTrackShapefile.py` — custom track → polyline shp  
- `README.md` — postAdditionalFiles Track.*  
- `run_manifest.json` ec95d example — s9.v1 modes/timeline  
- Research parametric pipeline: `2026-07-27-parametric-wind-pipeline.md`  

---

*The dropdown is a pack catalog. The scenario is the case + manifest. Parametric honesty is wind + the track that drove it, in the same pack, selected as one card.*
