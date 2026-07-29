# Design: richamp-support-web — high-fidelity interactive ADCIRC(+SWAN) visualization

**Date:** 2026-07-25  
**Plan:** `2026-07-25-richamp-support-web-plan.md`  
**Handoff:** `2026-07-25-richamp-support-web-handoff.md` (**reworked same day — suite house alignment with twin Path B**)  
**Operator path:** `/run-adcirc` + offline Grapher (unchanged; web is add-on product)

### Supersession note (latest handoff is law)

**Primary SoT:** `2026-07-25-richamp-support-web-handoff.md` — full **scientific integrity** bar, fabel product index, multiphysics coast, **ORDER 9 = Ida 36h SHiELD/FV3 fieldpack contract**.

| Pillar | Law |
|--------|-----|
| Fidelity | ≥ offline RICHAMP for shared products; interactive is additive |
| Path B | House spine — fieldpack SoT, `fields[]`, verify, globe + tiles, no dycore SoT |
| Atmos golden | `ida-smoke-20260725T232930Z` — 36h, nest + `tiles/tile1..6`, PRMSL **mb** |
| Coast | water · wind · rain · topo · **waves** (not runup) |
| ORDER 9 | Real FV3 integrate + dual suite + wind bridge (handoff §6.A / §7) |
| Presentation | Extend Path B; 2D ORDER 8; no rival SPA |

UI catalog §6.6 + Reader Lego still in force on the **suite shell**.

---

## 1. Overview / Background & Motivation

### 1.1 Problem

RICHAMP post-processing already has **technical fidelity** that took years to earn:

- Format-specific NetCDF adapters (ADCIRC fort.*, SWAN, GFS, POST wind, rain)
- Closest-node station stencil + interpolation → intermediate JSON
- Live obs (CO-OPS product API, NDBC, USGS)
- Mesh triangulation overlays, swaths, multipanel station timeseries, optional runup thesis stack

What it **does not** have is **interactive spatial exploration**. Maps are static satellite frames with baked bounds (`MapGenerator.py` + `MAP_BACKGROUND_BOUNDS.txt` + `Grapher.imshow`). That was a conscious early tradeoff (correct fixed extents for thesis/ASGS deliverables). It is the wrong foundation for a weather-website-class tool.

### 1.2 Opportunity

The atmospheric twin just established the pattern for **ops NetCDF → fieldpack → interactive explorer** (SHiELD view3d + planned Three live viz + `gfdl-fieldpack/v0`). Coastal sister needs the same:

> **The run is the map.**  
> Field-agnostic export + product-specific adapters + modular renderers.  
> New NetCDF? Add a class. Do not re-solve station interpolation.

### 1.3 Product name

**richamp-support-web** (working title). May live as:

- Sibling repo, or
- Package under this monorepo: `web/` + `post/export_fieldpack.py`

Recommend **sibling package in-repo first** (`web/`) so fieldpack export shares Python Readers without packaging hell; split later if needed.

---

## 2. Goals & Non-Goals

### Goals

| ID | Goal |
|----|------|
| G1 | **`adcirc-fieldpack/v0`** multiphysics export (water, wind, rain, topo, **waves**) twin-compatible envelope |
| G2 | Extend **Path B** for unstructured coastal + all field roles (preserve shield-fv3-viz laws) |
| G3 | **Globe** north-star presentation; **2D** finality ORDER 8 (same pack) |
| G4 | Unified house: atmos FV3/GFS pack + coastal pack in one shell |
| G5 | UI: layers, wind particles, **wave fields**, stations, click sample |
| G6 | Extensibility = Reader Lego + `meta.fields[]` (Path B agnosticism) |
| G7 | Roadmap in handoffs; G-DEPRECATE-READY ORDER 11; no runup this ladder |

### Non-Goals

| ID | Non-goal |
|----|----------|
| NG1 | Second SPA / second sacred JSON forked from twin |
| NG2 | Importing FV3 JS dycore into this repo |
| NG3 | Multi-tenant cloud SaaS |
| NG4 | Perfect datum skill scores before interactive viz |
| NG5 | Replacing print PNG capability *before* suite viz is boring |
| NG6 | Dumping ORDER list into `/run-adcirc` skill |
| NG7 | **Runup / transect / Holman / Stockdon / ASSET OpenTopo / TWLCC** in ORDER 0–11 |

---

## 3. Technical Requirements

### 3.1 Functional requirements

#### Data & export

| ID | Requirement |
|----|-------------|
| FR1 | Export mesh (nodes lon/lat/depth, triangles 0-based, optional exterior mask) from fort.14 |
| FR2 | Export scalar fields on mesh nodes with full time dimension (ζ water; optional still/tide) |
| FR3 | Export vector fields on mesh or structured grid (wind u/v or speed/dir) |
| FR4 | Export structured grids (GFS rain/wind) with lon/lat 1D or 2D coords |
| FR4b | Export **wave quantities** when present: SWH (swan_HS), MWD (swan_DIR), mean/peak period, rad stress mag/dir (rads.64) — same mesh/node model as water |
| FR5 | Export station catalog + model-interpolated series + optional obs (NOS/NDBC/USGS) |
| FR6 | Config-driven field list in `meta.json` — UI iterates `fields[]` |
| FR7 | Each field declares `{name, units, dims, role: scalar\|vector\|mesh_topo, grid: unstructured\|regular, path, dtype, cmap_hint?, range_hint?}` |
| FR8 | Preserve UTC timestamps (unix ms or ISO-8601 array); coldstart parse parity with `Reader._parseColdStartDate` |
| FR9 | Swath/max and accumulation products may be precomputed or derived client-side; semantics match Grapher (`max` / `sum` over time) |
| FR10 | Obs adapters may run at export time or live at runtime; product API for CO-OPS (not ERDDAP mat) |

#### Map & layers

| ID | Requirement |
|----|-------------|
| FR11 | Interactive pan/zoom basemap (raster tiles) with georeferenced overlays |
| FR12 | Water surface heatmap on unstructured mesh (tripcolor/WebGL equivalent) |
| FR13 | Wind visualization: particle tracers (primary), optional arrows/barbs/streamlines/speed fill |
| FR14 | Precipitation rate and accumulation layers (MetGet/GFS) |
| FR15 | Mesh layer: wireframe, node density, bathymetry/topo colormap |
| FR16 | Wave **SWH, MWD, MWP/PWP, rad stress** as first-class layers when present (parity with offline Grapher wave product set) |
| FR17 | Station markers by group (NOS/NDBC/USGS/ASSET) with hover labels |
| FR18 | Layer stack: toggle, opacity, z-order, colormap, fixed or auto range |
| FR19 | Region bookmarks matching `MAP_BACKGROUND_BOUNDS` presets (Rhode Island, Napatree, East Coast, America, …) |
| FR20 | Optional max-inundation / swath overlay |

#### Time & interaction

| ID | Requirement |
|----|-------------|
| FR21 | Time scrubber spanning all model times; play / pause / step / speed |
| FR22 | Jump to time of domain max for active scalar field |
| FR23 | Click map → sample value at time + open timeseries (nearest node or triangle interpolate) |
| FR24 | Click station → timeseries panel (model ± obs when available) |
| FR25 | Multi-station compare chart (shared y-axis option like multipanel Grapher) |
| FR26 | Analysis vs forecast segments selectable when run_manifest provides them |
| FR27 | Meta drawer: run_id, mesh name, NWS, coldstart, field units, node count, selected node id |

#### Modes & gating

| ID | Requirement |
|----|-------------|
| FR28 | Default mode: surge dashboard (water, mesh, CO-OPS, optional wind/rain if present) |
| FR29 | **No runup mode** in this ladder; packs must not require runup data for surge default |
| FR30 | Deep-linkable UI state (run, time, layers, station, lat/lon center, zoom) |
| FR31 | Export snapshot PNG of current map view; optional station chart PNG |

#### Extensibility

| ID | Requirement |
|----|-------------|
| FR32 | New model source = new Python `FieldAdapter` (+ optional JS renderer if not covered by scalar/vector defaults) |
| FR33 | New obs source = new `ObsAdapter` implementing common series contract |
| FR34 | No map-chrome edits required for new scalar field with standard dims |
| FR35 | Registry discovery from pack meta and/or plugin manifest |

### 3.2 Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Golden ec95d full mesh must remain loadable; quality modes may decimate **display** only with explicit flag |
| NFR2 | Offline Path A preferred for ops (vendored JS, local fieldpack) |
| NFR3 | Disk-conscious export: float16 for large time×node arrays where dynamic range allows; float32 coords/mesh |
| NFR4 | First paint < 5 s on laptop for subset RI domain; progressive load for basin meshes |
| NFR5 | Pure display logic unit-testable without browser (twin `wind-viz-display` spirit) |
| NFR6 | Coords wrong = hard fail (no silent degree/radian or lon wrap bugs) |
| NFR7 | API keys never committed; basemap tokens via env |
| NFR8 | Accessibility baseline: keyboard time step, visible focus, contrast on charts |

---

## 4. User Stories

### US1 — Operator inspects surge after `/run-adcirc`

**As** an operator, **I want** to open a web view of my analysis/forecast water field with CO-OPS stations, **so that** I can scrub time and trust the same numbers as Grapher PNGs.

**AC:**

- Given golden `ec95d_gfs_5d_*` fieldpack  
- When I open Path A or B  
- Then water layer + stations render; scrubbing time updates field  
- And station Newport series matches offline `{name}_water.png` within floating tolerance  

### US2 — Scientist explores wind like a weather site

**As** a coastal scientist, **I want** animated wind tracers over the domain, **so that** I can see wind structure without opening a GIF sequence.

**AC:**

- Given fort.74 or post wind in pack  
- When I enable Wind layer + tracers  
- Then particles advect with u/v; play advances time  
- And I can switch to speed fill or barbs without reload  

### US3 — Click-anywhere sample

**As** a user, **I want** to click any wet node or map point and see a timeseries, **so that** I am not limited to pre-listed stations.

**AC:**

- When I click the map  
- Then nearest node (or triangle-interpolated) series opens in the chart panel  
- And meta shows node index + lon/lat + depth  

### US4 — Layer composition

**As** a user, **I want** to toggle water, mesh wire, stations, and precip independently, **so that** I can compose views like professional weather UIs.

**AC:**

- Four layers independently toggle + opacity  
- Basemap remains underneath  
- State survives refresh via URL hash/query  

### US5 — Extensibility for new NetCDF

**As** a developer, **I want** to add a new product (e.g. fort.64 pressure) by writing an adapter class and meta entry, **so that** I do not reimplement station stencil or map chrome.

**AC:**

- New adapter registers field in pack  
- Default scalar renderer shows colormap  
- Station extraction reuses `Reader.initializeClosestNodes` path  

### US6 — Twin parity of philosophy

**As** suite maintainer, **I want** coastal viz to follow CloudVision’s fieldpack + Path A/B split, **so that** dual-suite operators share mental model.

**AC:**

- Docs cite twin contracts  
- Export lives next to run products  
- Skill stays thin; roadmap in handoffs  

---

## 5. Technical Guidelines

1. **Simulation / fieldpack is SoT for display** — basemap is context only.  
2. **Adapters, not monoliths** — Python export adapters mirror `*Reader`; JS renderers mirror Grapher blocks.  
3. **Coords and units first** — wrong lon/lat or unlabeled datums are hard fails.  
4. **Composition over deep inheritance** — wrap shared `Reader` / shared `MeshGeometry` (same as offline).  
5. **Default surge only** — preserve 2026-07-25 post strip; runup stays offline/future.  
6. **Copy patterns from twin, not twin code blindly** — wind particles yes; cubed-sphere solver no.  
7. **Quality modes** — `interactive` | `balanced` | `fidelity` (display LOD only).  
8. **Offline Grapher remains law for publication** — web does not need pixel-identical matplotlib, but **series and max/swath semantics** must match.  
9. **No API keys in git** — Static Maps key currently in `MapGenerator.py` is a scar; web must not repeat.  
10. **Handoffs own roadmap** — skills own operators.

### Direction / vector fidelity (carry from Grapher)

- Model wind direction: `atan2(-v, u)` convention as in `Grapher.vectorDirection`  
- CO-OPS wind “from” direction: apply documented +90° alignment when comparing  
- Label whether vectors are meteorological “from” or oceanographic “to”

### Colormap defaults (start from Grapher, make configurable)

| Field | Default range (hint) | Notes |
|-------|----------------------|-------|
| Wind speed | 0–20 m/s | Grapher fixed |
| Rain rate | 0–5 mm/h | convert units carefully |
| Rain accum | 0–500 mm | sum semantics |
| Elevation/bathy | −15–10 m | fort.14 negate depth |
| Water ζ | auto ± symmetric or auto percentile | avoid hardcode that clips surge |
| SWH | auto or 0–8 m | domain dependent |

---

## 6. Proposed Design

### 6.1 System architecture

```text
                    ┌─────────────────────────────────────┐
                    │  ADCIRC / SWAN / MetGet / fort.*    │
                    │  (+ optional live Obs APIs)         │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │  post/export (Python)                 │
                    │  FieldAdapters = *Reader Lego         │
                    │  ObsAdapters = GetBuoy*               │
                    │  → adcirc-fieldpack/v0                 │
                    └─────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
     Path A: ops SPA          Path B: richamp-web      Path C: Grapher PNG
     products/web/            MapLibre + layers        (existing, print)
     offline fieldpack        wind particles
                              click sample
```

### 6.2 `adcirc-fieldpack/v0` contract

```text
fieldpack/
  meta.json
  mesh/
    nodes.f32.bin          # N×3 lon, lat, elev_m (elev = -depth if from fort.14)
    triangles.u32.bin      # M×3 indices
    mask_tri.u8.bin        # optional; 1=draw
  fields/
    water_zeta.f16.bin     # T×N
    wind_u.f16.bin         # T×N or T×ny×nx
    wind_v.f16.bin
    rain_rate.f16.bin      # T×ny×nx structured
    ...
  grids/
    gfs_lon.f32.bin
    gfs_lat.f32.bin
  stations/
    catalog.json           # groups NOS/NDBC/USGS/ASSET
    series/
      water.json           # or .f32.bin + index
      wind.json
      obs_water.json
  derived/                 # optional
    water_max.f16.bin      # N
    rain_accum.f16.bin
```

#### `meta.json` (conceptual)

```json
{
  "schema": "adcirc-fieldpack/v0",
  "run_id": "ec95d_gfs_5d_2026072512",
  "phases": [
    {"name": "analysis", "time_range": ["…", "…"]},
    {"name": "forecast", "time_range": ["…", "…"]}
  ],
  "times_utc": ["2026-07-19T12:00:00Z", "..."],
  "crs": "EPSG:4326",
  "vertical_datum": "model_native",
  "vertical_datum_note": "CO-OPS may be MSL; label both; skill later",
  "mesh": {
    "n_nodes": 123456,
    "n_triangles": 234567,
    "source": "fort.14",
    "paths": {
      "nodes": "mesh/nodes.f32.bin",
      "triangles": "mesh/triangles.u32.bin"
    }
  },
  "fields": [
    {
      "name": "water_zeta",
      "long_name": "water surface elevation",
      "units": "m",
      "dims": ["time", "node"],
      "role": "scalar",
      "grid": "unstructured",
      "path": "fields/water_zeta.f16.bin",
      "dtype": "f16",
      "cmap_hint": "balance",
      "range_hint": null
    },
    {
      "name": "wind",
      "components": ["wind_u", "wind_v"],
      "units": "m/s",
      "role": "vector",
      "grid": "unstructured",
      "dtype": "f16"
    }
  ],
  "stations": {
    "catalog": "stations/catalog.json",
    "series": {
      "water": "stations/series/water.json",
      "obs_water": "stations/series/obs_water.json"
    }
  },
  "bookmarks": [
    {"id": "RHODE_ISLAND", "bbox": [-71.9, 41.1, -71.0, 41.9]},
    {"id": "NAPATREE", "bbox": [/* from MAP_BACKGROUND_BOUNDS */]}
  ],
  "modes": {"waves": false},
  "provenance": {
    "exporter": "export_fieldpack.py",
    "source_files": ["analysis/fort.63.nc", "ec95d_run/fort.14"]
  }
}
```

**Agnosticism rule:** UI iterates `fields[]`. Unknown scalars still plot. Unknown vectors need u/v component pairing in meta.

### 6.3 Python export architecture (Lego)

```text
post/export/
  __init__.py
  pack_writer.py          # schema writer, dtype helpers
  mesh_adapter.py         # Fort14Reader → mesh bins
  field_adapters/
    base.py               # FieldAdapter protocol
    water_fort63.py       # wraps Fort63Reader / Reader
    wind_fort74.py
    wind_gfs.py
    wind_post.py
    rain_gfs.py
    waves_swan.py
  station_export.py       # shared closest-node series dump
  obs_adapters/
    coops_water.py
    coops_wind.py
    ndbc_waves.py
    usgs_rain.py
  cli.py                  # export_fieldpack --rundir --outdir --products ...
```

**Protocol (sketch):**

```python
class FieldAdapter(Protocol):
    name: str
    role: Literal["scalar", "vector", "mesh_topo"]
    def available(self, rundir: Path) -> bool: ...
    def export(self, ctx: ExportContext) -> list[FieldMeta]: ...
```

Adding fort.64 pressure:

1. Implement `PressureFort64Adapter`  
2. Register in CLI product list  
3. Done — UI auto-lists scalar

### 6.4 Path A — ops SPA

```text
products/web/
  index.html
  app.js              # thin controller
  fieldpack/          # or sibling path
  vendor/             # maplibre optional; can be canvas-only for A1
```

**A1 MVP:** canvas/WebGL mesh colormap + time range + station chart (Chart.js or uPlot) — may skip full basemap tiles if offline.

**A2:** add MapLibre basemap + layer toggles.

### 6.5 Path B — interactive product architecture

```text
web/   (or richamp-support-web/)
  package.json
  index.html
  src/
    app/
      shell.js              # layout: map | sidebar | bottom chart | timebar
      state.js              # run, timeIndex, layers, selection, url sync
    data/
      fieldpack-loader.js   # meta + bin → typed arrays
      mesh-geometry.js
      sample.js             # nearest node / triangle interpolate
    layers/
      basemap.js
      water-mesh-layer.js   # WebGL tri colormap
      wind-particles.js     # pure + WebGL (port DNA from twin wind-viz-display)
      rain-grid-layer.js
      mesh-wire-layer.js
      stations-layer.js
      swath-layer.js
    ui/
      layer-panel.js
      time-transport.js
      chart-panel.js
      meta-drawer.js
      bookmark-menu.js
      mode-switch.js
    render/
      colormap.js
      quality.js            # interactive|balanced|fidelity
  tests/
    fieldpack-schema.test.js
    sample-node.test.js
    wind-particles-pure.test.js
```

#### Recommended stack (revised after Path B MVP)

| Piece | Choice | Why |
|-------|--------|-----|
| **Globe (primary)** | **Extend `threejs-shield-live-viz`** | MVP done; twin law; one shell |
| **2D (ORDER 8)** | MapLibre custom layer **or** Three orthographic map mode in same shell | Coastline ops; not a second product |
| Mesh overlay | WebGL tris from fieldpack mesh | Unstructured ADCIRC native |
| Charts | uPlot or Chart.js | Fast multi-series |
| Wind particles | Twin `wind-viz-display` DNA (display only) | Weather-site fidelity |
| Loader | Shared `fieldpack-loader.js` family | One decoder |
| State | URL query + small store | Deep links |

**Do not** start a greenfield MapLibre-only app before ORDER 4 (globe water).

### 6.6 Full UI catalog (menus, sliders, options, visualizations)

This is the explicit inventory so implementers do not invent scope ad hoc. **MVP** tags mark first ship slice; rest is extensible backlog inside the same shell.

#### 6.6.1 Shell layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Top bar: Case/Run · Phase · Mode · Share · Export · Help     │
├────────────┬─────────────────────────────────┬───────────────┤
│ Left rail  │           MAP                   │ Right drawer  │
│ Layers     │   basemap + overlays            │ Meta / Inspect│
│ Bookmarks  │   stations                      │ Node details  │
│ Modes      │                                 │ Field stats   │
├────────────┴─────────────────────────────────┴───────────────┤
│ Time transport  [<<] [Play] [>>]  ────●────────  speed  FPS  │
├──────────────────────────────────────────────────────────────┤
│ Bottom: Timeseries charts (station / click / multi-compare)  │
└──────────────────────────────────────────────────────────────┘
```

#### 6.6.2 Top bar

| Control | Options | MVP |
|---------|---------|-----|
| Case picker | list of local packs / path input | ✓ |
| Phase | analysis / forecast / all | ✓ |
| Mode | Multiphysics / Surge · Waves · Wind+Rain · Compare | ✓ multiphysics toggles |
| Basemap style | satellite · streets · dark · blank | ✓ 2 styles |
| Share | copy deep link | ✓ |
| Export | map PNG · chart PNG · (later GIF/MP4) | ✓ map PNG |
| Quality | interactive · balanced · fidelity | ✓ |

#### 6.6.3 Layer panel (each layer)

Common per-layer controls:

- Visibility toggle  
- Opacity slider (0–100%)  
- Expand: colormap select, min/max (auto / fixed), show colorbar  
- For vectors: display mode select  

| Layer | Visualizations | Controls | MVP |
|-------|----------------|----------|-----|
| **Basemap** | raster tiles | style | ✓ |
| **Water ζ** | mesh heatmap | cmap, range, show dry nodes? | ✓ |
| **Water max / swath** | static max field | opacity | ✓ |
| **Still water / tide water** | heatmap | compare diff mode | later |
| **Wind speed fill** | mesh or grid heatmap | range 0–20 default | ✓ one wind source |
| **Wind particles** | animated tracers | density, speed, trail length, zoom LOD | ✓ |
| **Wind arrows / barbs** | glyphs | spacing | later |
| **Wind streamlines** | static/dynamic | density | later |
| **Rain rate** | grid heatmap | mm/h conversion | ✓ if in pack |
| **Rain accumulation** | grid heatmap | sum window | later |
| **Mesh wire** | triangle edges | density LOD | ✓ |
| **Mesh bathy/topo** | tripcolor elev | cmap elev | ✓ |
| **Mesh nodes** | point cloud | size by depth optional | later |
| **SWH** | mesh heatmap | cmap, range | ✓ ORDER 7 (waves golden) |
| **MWD** | arrows / dir field | | ✓ ORDER 7 |
| **MWP / PWP** | heatmap | | ✓ ORDER 7 |
| **Radiation stress** | mag/dir | | ✓ ORDER 7 |
| **Stations NOS** | markers | filter by name | ✓ |
| **Stations NDBC** | markers | | when waves |
| **Stations USGS** | markers | | when rain |
| **ASSET / transect** | — | | **out of scope** (runup later) |
| **Track / shapefile** | storm track | | later |
| **Max inundation (MATLAB product)** | image georef or field | | later |
| **Obs-only markers** | when model missing | | later |

#### 6.6.4 Time transport

| Control | Behavior | MVP |
|---------|----------|-----|
| Play / Pause | advance timeIndex | ✓ |
| Step ±1 | keyboard ← → | ✓ |
| Scrubber | drag continuous | ✓ |
| Speed | 0.25×–8× | ✓ |
| Loop | on/off | ✓ |
| Jump to max | max of active scalar in viewport or domain | ✓ |
| FPS throttle | quality mode interaction | later |
| Time readout | ISO UTC + model hours | ✓ |
| Phase brackets | highlight analysis vs forecast | ✓ |

#### 6.6.5 Map interaction

| Action | Result | MVP |
|--------|--------|-----|
| Pan / zoom / rotate (optional disable rotate) | standard map | ✓ |
| Double-click zoom | | ✓ |
| Click empty map | sample nearest node; chart + inspect | ✓ |
| Click station | select station; chart model±obs | ✓ |
| Hover | tooltip value at time | ✓ |
| Box zoom | | later |
| Measure distance | | later |
| Bookmark fly-to | preset extents from meta | ✓ |
| North reset | | ✓ |

#### 6.6.6 Chart panel

| Chart | Content | MVP |
|-------|---------|-----|
| Single station water | model ζ ± CO-OPS | ✓ |
| Single station wind speed/dir | model ± obs | later |
| Click-point series | nearest node ζ (and multi-field tabs) | ✓ |
| Multi-station water | shared y-axis multipanel or overlay | ✓ |
| Rain station vs gauge | | later |
| Wave SWH vs NDBC | | ✓ when NDBC + waves |
| Runup Holman/Stockdon | | **out of scope** |
| Spectrum (directional) | | specialty |
| Cursor time marker | vertical line synced to transport | ✓ |
| Export CSV of series | | later |

#### 6.6.7 Meta / inspect drawer

| Field | Source |
|-------|--------|
| run_id, phases | meta |
| mesh node/tri counts | meta |
| selected node id, lon, lat, depth | mesh |
| field units, vertical datum note | meta |
| min/max at current time (viewport) | derived |
| source files | provenance |
| wind convention note | constants |
| pack schema version | meta |

#### 6.6.8 Compare & analysis tools (extensible)

| Tool | Description | Priority |
|------|-------------|----------|
| Model vs obs residual series | station skill prep | P1 |
| Analysis vs forecast stitch | continuous timeline | P1 |
| Still vs total water difference | three-water | P2 thesis |
| Diff two runs | DiffGrapher analog | P2 |
| Datum offset slider | temporary visual align MSL↔NAVD | P1 optional |
| Cross-section along polyline | sample mesh along path | P2 |
| Transect / runup profile | ASSET + Holman | **out of scope** (later handoff) |
| Threshold exceedance map | hours above X m | P2 |
| Particle trajectory (passive) | from wind or currents | P3 |

#### 6.6.9 Keyboard shortcuts (MVP set)

| Key | Action |
|-----|--------|
| Space | play/pause |
| ← / → | step time |
| `[` / `]` | cycle layers focus |
| `1–9` | toggle layer presets |
| `f` | jump to max |
| `r` | reset view bookmark |
| `?` | help |

### 6.7 Wind particles (port twin DNA, coastal domain)

From CloudVision `wind-viz-display.js` — **display only**:

- Animated particle tracers with trails  
- Density LOD by zoom  
- Density/speed sliders as multipliers  
- Optional streamlines/isobars later  

Coastal adaptation:

- Integrate particles on **map projection** (Mercator meters), not unit sphere  
- Sample u/v from unstructured mesh via triangle containing particle (or grid for GFS)  
- Reseed when particle leaves wet domain / viewport  
- Pure module `wind-particles-pure.js` for unit tests without WebGL  

### 6.8 Sampling algorithm (click / particles)

1. Project click lon/lat  
2. Find triangle containing point (spatial index: BVH or grid hash on load)  
3. Barycentric interpolate nodal field at timeIndex  
4. If outside mesh: show “dry / outside domain”  

Nearest-node fallback acceptable for MVP if index delayed — document error.

### 6.9 Dual entry from ops

| Entry | Action |
|-------|--------|
| After `/run-adcirc` post | optional `--export-web` writes fieldpack + Path A |
| Manual | `python -m post.export.cli --rundir … --outdir …` |
| ASGS | future hook beside `richamp_scale_and_subset` |

### 6.10 Architecture diagram (extensibility)

```text
                    FieldAdapter registry
                    ┌────────┬────────┬────────┐
                    │Fort63  │Fort74  │GFSRain │  …new
                    └────┬───┴───┬────┴───┬────┘
                         ▼       ▼        ▼
                      pack_writer → meta.fields[]
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ScalarLayer        VectorLayer        GridLayer
             (water,swh,…)      (wind particles)   (rain)
                    │                 │                 │
                    └──────────── Map shell ◄───────────┘
                                      │
                               Chart plugins
                          (station, click, multi)
```

---

## 7. Boilerplate / placeholders

### 7.1 Fieldpack loader (JS) — extend Path B, do not fork

```js
// Evolve: CloudVision/threejs-shield-live-viz/fieldpack-loader.js (ORDER 3)
const SCHEMAS = new Set([
  'gfdl-fieldpack/v0',
  'adcirc-fieldpack/v0',
  'suite-fieldpack/v0',
]);

export async function loadFieldpack(rootUrl) {
  const meta = await (await fetch(`${rootUrl}/meta.json`)).json();
  if (!SCHEMAS.has(meta.schema)) {
    throw new Error(`Unsupported schema: ${meta.schema}`);
  }
  // nest_curvilinear → existing ny*nx + plev path (MVP DONE)
  // adcirc_unstructured → mesh nodes/tris + getScalar(name, t) on node dim
  // regular_latlon → grid fields (rain)
  ...
}
```

### 7.2 Adapter registration (Python)

```python
# post/export/field_adapters/base.py
from typing import Protocol, List
from pathlib import Path

class FieldMeta(dict):
    """name, units, dims, role, grid, path, dtype, ..."""

class FieldAdapter(Protocol):
    name: str
    def available(self, rundir: Path) -> bool: ...
    def export(self, ctx) -> List[FieldMeta]: ...

REGISTRY: list[FieldAdapter] = []

def register(adapter: FieldAdapter):
    REGISTRY.append(adapter)
    return adapter
```

```python
# post/export/field_adapters/water_fort63.py
from Reader import Fort63Reader  # reuse proven Lego

@register
class WaterFort63Adapter:
    name = "water_zeta"
    def available(self, rundir):
        return (rundir / "fort.63.nc").exists()
    def export(self, ctx):
        # reuse Fort63Reader / Reader.getValues* paths
        # write fields/water_zeta.f16.bin
        # return [FieldMeta(...)]
        ...
```

### 7.3 Layer panel state (JS)

```js
const defaultLayers = [
  { id: 'basemap', type: 'basemap', visible: true, opacity: 1 },
  { id: 'water_zeta', type: 'scalar-mesh', field: 'water_zeta', visible: true, opacity: 0.85 },
  { id: 'mesh_wire', type: 'mesh-wire', visible: false, opacity: 0.4 },
  { id: 'mesh_bathy', type: 'scalar-mesh', field: 'bathymetry', visible: false, opacity: 0.7 },
  { id: 'wind', type: 'vector', field: 'wind', mode: 'particles', visible: false, opacity: 1 },
  { id: 'rain_rate', type: 'scalar-grid', field: 'rain_rate', visible: false, opacity: 0.7 },
  { id: 'stations_nos', type: 'stations', group: 'NOS', visible: true },
];
```

### 7.4 CLI sketch

```bash
python -m post.export.cli \
  --rundir ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/analysis \
  --mesh ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/ec95d_run/fort.14 \
  --stations OBS_STATIONS.json \
  --products water,mesh,stations,obs_water \
  --outdir ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/products/fieldpack \
  --also-path-a
```

---

## 8. Alternatives Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Keep static Google PNG + zoom CSS | Easy | Fake zoom; no real data LOD; key in repo | Reject for Path B |
| Leaflet + ImageOverlay of Grapher PNG frames | Fast demo | Not mesh-true; huge frame sets | Optional cheap demo only |
| Full Cesium 3D globe MVP | Impressive | Weak for RI shoreline workflow; heavy | Later optional |
| deck.gl only (no MapLibre) | Great mesh | Basemap story weaker alone | Maybe combine |
| **Extend Path B Three shell** | MVP done; one house | Unstructured mesh work | **Chosen presentation** |
| MapLibre-only second app | Fast 2D | Forks product / dual SoT | **Reject as primary**; OK as ORDER 8 view |
| Server-side WMS/tiles | Scales | Ops complexity early | Later if multi-user |
| Rewrite Readers in JS | Single language | Lose stencil fidelity | **Reject** — export in Python |
| Only improve matplotlib to HTML | Small | No interactivity north star | Print fallback only |
| Merge coastal into gnomonic **solver** tree | Shared files | Risk GOLD verify | **Reject** — Path B tree only |

---

## 9. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Path B MVP | **Foundation** | verify PASS; do not re-scaffold |
| Export language | Python reusing Reader | Stencil/time parse fidelity |
| Presentation | Extend Path B shell | One house |
| 2D | ORDER 8 view in shell | Coastline ops; same pack |
| Pack schema | `adcirc-fieldpack/v0` family of gfdl | Dual-suite mental model |
| Mesh display | True unstructured tris | Fidelity > pretty regrid |
| Wind hero viz | Particle tracers | User + twin DNA |
| Default mode | Surge | Matches stripped post |
| Runup | **Out of scope** ORDER 0–11 | Needs waves+runup golden run later |
| Deprecate this repo product surface | After G-DEPRECATE-READY (ORDER 11) | House absorbs interactive surge post |
| Roadmap | Handoffs ORDER 0–11 | Skills stay thin |
| Golden coastal | ec95d_gfs_5d_2026072512 | Live SUCCESS |

---

## 10. ORDER Plan (replaces old PR0–16 MapLibre-first list)

Canonical table lives in **handoff §5**. Summary:

| ORDER | Title | Gate |
|------:|-------|------|
| 0 | Law freeze | docs |
| 1 | Export skeleton | meta shape |
| 2 | Mesh + zeta | G-PACK |
| 3 | Loader unstructured | G-LOAD |
| 4 | Globe water | G-GLOBE |
| 5 | Stations + CO-OPS | G-STN |
| 6 | Click + time UX | G-CLICK |
| 7 | **Multiphysics:** wind + rain + **wave quantities** | G-MULTI |
| 8 | **2D finality** | G-2D |
| 9 | **Ida 36h SHiELD fieldpack integrate** (nest+tiles, PRMSL mb) + dual suite + wind bridge | G-FV3 / G-HOUSE |
| 10 | Deep links + thin ops + quality | G-OPS |
| 11 | **House finality** (polish, G-DEPRECATE-READY) | G-FINAL |

**Start:** ORDER 1–2 (export mesh+zeta; adapter registry ready for waves). Then 3–4 (Path B loader + globe).  
**Waves offline graphs:** `~/projects/richamp-support-floodwater/post_forecast/graphs/`.  
**Water graphs:** `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_forecast/graphs/`.  
**Wind graphs:** `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_wind/graphs/`.  
**Runup:** not in this table.

---

## 11. Open Questions

1. 2D = MapLibre custom layer vs Three ortho in Path B (prefer one shell)?  
2. Basemap tile provider / offline story for ORDER 8?  
3. Float16 ζ on Sandy-class extremes?  
4. One pack analysis+forecast stitch vs phase switch?  
5. Live CO-OPS in browser vs export-time only?  
6. When to rename Path B → `suite-live-viz`?  
7. Wind bridge: fort.22 NWS=6 vs OWI vs 306 first?  
8. Worker thread for large mesh decode?

---

## 12. References

### This repo

- `Reader.py`, `Grapher.py`, `generateGraphs.py`, `MapGenerator.py`  
- `MAP_BACKGROUND_BOUNDS.txt`, `OBS_STATIONS.json`  
- `notes/WIKI/what-we-use-and-need.md`  
- `notes/GROK/handoffs/2026-07-25-run-adcirc-gfs-post-handoff.md`  
- Golden: `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/`

### Twin (atmosphere)

- `CloudVision/notes/GROK/handoffs/2026-07-25-shield-fv3-viz-live-integrate-{plan,design,handoff}.md`  
- `CloudVision/threejs-cubed-sphere-gnomonic/wind-viz-display.js`  
- `SHiELD_OPS/post/view_3d.py`, `viewer_template.html`  
- `CloudVision/notes/GROK/ops/2026-07-25-research-synthesis-shield-postproc-pipeline.md`

### Index IDs (plan)

- Data D-*, Obs O-*, UI catalog §6.6, Extensibility I6, Invariants I7  

---

*Path B is the floor. FV3/GFS is the sky. Multiphysics coast (water·wind·rain·topo·waves) is the water. One house. Runup later.*
