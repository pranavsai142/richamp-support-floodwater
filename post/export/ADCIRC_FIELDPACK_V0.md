# adcirc-fieldpack/v0

Binary field pack for ADCIRC(+SWAN) run output → the suite live viz.

Sister contract to **`gfdl-fieldpack/v0`** (`~/projects/SHiELD_OPS/post/FIELDPACK_V0.md`).
Same family, same binary law, same `meta.fields[]` agnosticism — different
geometry (`adcirc_unstructured` instead of `nest_curvilinear`). One loader,
one verifier, one shell.

## Export

```bash
export PYTHONPATH=~/projects/richamp-support-floodwater
CASE=~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512
python -m post.export.cli \
  --rundir   $CASE/forecast \
  --mesh     $CASE/forecast/fort.14 \
  --case     $CASE \
  --products mesh,water,stations,obs_water \
  --outdir   $CASE/products/fieldpack
```

Exit: `0` ok · `2` missing inputs · `3` write failure (mirrors the twin).

`--list-products` prints the registry. `--path KEY=PATH` overrides where a
product is read from (e.g. `--path wind_gfs=$CASE/post_wind/gfs_wind.nc`).

Parametric (Lee-class) additions: `--products …,wind_parametric,track`,
`--wind-stride N` (explicit spatial stride for the 565×625 PWM basin grid —
recorded on every field row and in `meta.fidelity.decimation`, never silent),
`--default-utc ISO` (scenario hint the shell opens on). The driving track is
exported from the same files that fed PWM (`lee_best_track.trk` /
`track.richamp`); `richamp.wnd` and `fort.22` (~2.2 G drive met) never enter
the pack.

## Layout

```
fieldpack/
  meta.json
  mesh/
    nodes.f32.bin          # (N,3) float32 LE — lon, lat, elev_m (= −depth)
    triangles.u32.bin      # (M,3) uint32 LE — 0-based fort.14 connectivity
  fields/
    water_zeta.f16.bin     # (T,N) float16 LE, m
    water_max.f16.bin      # (N,)  float16 LE, m — swath = max over time
    bathymetry.f32.bin     # (N,)  float32 LE, m
    wind_u.f16.bin …       # (T,N) unstructured or (T,ny,nx) gridded
    wave_swh.f16.bin …
  grids/
    <grid_id>_lon.f32.bin  # (nx,) float32 LE — regular lat/lon products
    <grid_id>_lat.f32.bin  # (ny,)
  stations/
    catalog.json
    series/*.json
  tracks/                  # driving-track products (parametric scenarios)
    catalog.json
    drive_track.json       # BEST/ATCF fixes: times_utc, lon, lat, vmax_kt, mslp_mb, rmw_nm
    pwm_track.json         # track.richamp geometry (heading, vmax m/s, RMW km)
```

Row-major C order, little-endian throughout.

## NaN law (differs from the twin — deliberately)

The atmospheric twin writes `NaN/Inf → 0`. **Coastal packs must not.** An
ADCIRC dry node is not `0.0 m` of water; zeroing it paints a flat wet sheet
over dry land. Coastal scalars are written with `nan_policy="preserve"`:

| Value | Meaning |
|-------|---------|
| finite | model value |
| `NaN` | dry node / outside product domain / no data |

`_FillValue = -99999` from ADCIRC is normalised to `NaN` on write. Renderers
must skip `NaN` (no colour, no contribution to auto range), and samplers must
report *dry*, not zero.

## dtypes

| Data | dtype | Why |
|------|-------|-----|
| Mesh coords + elevation | `float32` | geometry is never approximated |
| Triangles | `uint32` | 0-based indices |
| Time-varying scalars (ζ, SWH, wind, rain) | `float16` | 2 bytes × T × N; ~1 mm at ζ ≈ 1 m, ~4 mm at 4 m |
| Deep bathymetry as a *field* | `float32` | float16 ulp is 4 m near −8000 m |

float16 saturates at 65504 — far above any coastal scalar in these packs. The
writer raises rather than silently clipping if a field ever exceeds it.

## meta.json

| Key | Meaning |
|-----|---------|
| `schema` | `"adcirc-fieldpack/v0"` |
| `run_id` | run / case id (from `run_manifest.json` when present) |
| `grid_type` | `"adcirc_unstructured"` |
| `crs` | `"EPSG:4326"` |
| `vertical_datum` / `_note` | model-native; CO-OPS obs are MSL — both labelled, never silently shifted |
| `dims` | `{node, triangle, time}` |
| `times_utc` | default stream's ISO-8601 Z list |
| `time_streams` | **per-clock** `{id: {n, times_utc, source}}` |
| `default_time_stream` | which stream `times_utc` mirrors |
| `mesh` | counts, ranges, bin paths, source file |
| `grids` | regular lat/lon grids for gridded products |
| `fields[]` | one row per product (below) |
| `stations` | catalog + series paths |
| `bookmarks` | offline `*_AXIS` extents that intersect this mesh |
| `modes` | `{water, mesh, wind, rain, waves, track, runup:false}` — `wind` keeps the manifest's honest string (`parametric_nws6` / `gfs_nws6_fort22`) when wind shipped |
| `scenario` | `{storm{name,basin,number,year}, met{family, wind_mode, source}, default_utc}` — met.family is the honesty line: parametric wind must never read as GFS |
| `roles` | compare bindings, e.g. `{water_surface: "water_zeta", wind_10m_u: "wind_u", …}` — the house compare binds by role, never by hardcoded field name |
| `tracks` | `{catalog, items{id: path}, n}` when a driving track shipped |
| `provenance` | exporter, source files, run manifest |
| `fidelity` | decimation ("none", or the explicit `--wind-stride` record), nan policy, adapters that ran |

### Field row (mirrors the twin, plus coastal keys)

```json
{
  "name": "water_zeta",
  "long_name": "water surface elevation above geoid",
  "units": "m",
  "dims": ["time", "node"],
  "shape": [120, 31435],
  "path": "fields/water_zeta.f16.bin",
  "dtype": "float16",
  "endian": "little",
  "role": "scalar",
  "grid": "unstructured",
  "stream": "adcirc",
  "min": -7.19921875,
  "max": 6.17578125,
  "n_nonfinite": 844,
  "nan_means": "dry / no data",
  "cmap_hint": "balance",
  "source": "forecast/fort.63.nc"
}
```

`role`: `scalar` · `vector` · `series`. `grid`: `unstructured` (node dim) or a
key in `meta.grids` (ny/nx dims). Vectors carry `components: [u, v]` and a
`convention` string instead of a `path`.

**Agnosticism rule:** the UI iterates `fields[]`. An unknown scalar still plots
with a default colormap; an unknown vector needs only its component pair.

## Time streams

A coastal run mixes clocks exactly like the atmosphere does (hourly PRMSL vs
~3-hourly 3D):

| Stream | Typical source | Typical cadence |
|--------|----------------|-----------------|
| `adcirc` | `fort.63.nc`, `fort.74.nc` | model output interval (1 h on ec95d) |
| `gfs` | `gfs_wind.nc`, rain | 15 min–1 h |
| `post` | `RICHAMP_wind.nc` | 15 min |
| `swan` | `swan_*.63.nc` | wave output interval |

Every field declares its `stream`. **Never force one clock onto another
stream's field** — map scrubbers per stream and interpolate index by time, not
by position.

## Semantics carried from the offline stack

| Product | Rule |
|---------|------|
| Swath / max | `max` over time (`water_max`), not the last frame |
| Rain accumulation | `sum` over time |
| Mesh elevation | `elev_m = −depth` (fort.14 col 4) |
| Wind direction | `atan2(-v, u)` → degrees, +360 if negative (`Grapher.vectorDirection`) |
| CO-OPS wind "from" | documented +90° alignment when comparing |
| RICHAMP post wind | `spd` (m/s) + `dir` (**meteorological, direction coming from**) |
| Station stencil | `Reader.initializeClosestNodes` — never reimplemented in JS |
| Coldstart / times | `Reader.getNetcdfProperties` (`seconds since` for FORT, `minutes since` for GFS/POST) |

## Sources

| Field | File | Reader |
|-------|------|--------|
| mesh, `bathymetry` | `fort.14` | `Fort14Reader.readMeshElevations` |
| `water_zeta`, `water_max` | `fort.63.nc` | `Reader` (`water`) |
| `wind_u/v` (ADCIRC) | `fort.74.nc` | `Reader` (`fort`) |
| `wind_u/v` (GFS) | `gfs_wind.nc` | `Reader` (`gfs`) |
| `wind_u/v` (parametric PWM) | `*_parametric_wind.nc` (owi2wind) | `Reader` (`gfs` — same minutes-since-1990 schema; honesty lives in stream `parametric` + long_names, never the var names) |
| `tracks/*` | `*.trk` (ATCF BEST) + `track.richamp` | `track_export` parsers |
| `wind_spd/dir` (RICHAMP) | `RICHAMP_wind.nc` `Main/` | `Reader` (`post`) |
| `rain_rate`, `rain_accum` | GFS/MetGet rain nc | `Reader` (`rain`) |
| `wave_swh` | `swan_HS.63.nc` | `Reader` (`swh`) |
| `wave_mwd` | `swan_DIR.63.nc` | `Reader` (`mwd`) |
| `wave_mwp` | `swan_TMM10.63.nc` | `Reader` (`mwp`) |
| `wave_pwp` | `swan_TPS.63.nc` | `Reader` (`pwp`) |
| `wave_radstress_x/y` | `rads.64.nc` | `Reader` (`rad`) |

## Stations

`stations/series/` carries up to four series per station, deliberately kept
distinct rather than merged:

| Key | What it is |
|-----|-----------|
| `water` | `Reader.generateDataFilesWithInterpolation` — the offline series, from a **shared** support cloud built out of every station's stencil |
| `water_node` | the station's own closest node, straight from `fort.63.nc`, no interpolation |
| `obs_water` | CO-OPS verified water level (MSL) |
| `obs_water_prediction` | CO-OPS tidal prediction (fills a forecast window with no verified data yet) |

Why both model series: on a coarse mesh most stations have an **empty** stencil
at the reader's threshold, and `generateDataFilesWithInterpolation` then
interpolates them from the shared cloud — which can reach hundreds of km. On
ec95d that moves Fort Myers (19.6 km from its nearest node) by ~0.45 m and New
London (6.0 km) by ~0.39 m relative to their own nodes. The pack carries both
and `catalog.json` records `node_distance_km` and `stencil_n`, so the reader can
see which number they are looking at. Neither series is a correction of the
other; both are real model output.

## Verify

```bash
# Python — structure + cross-check against the raw fort.14 / fort.63
python -m post.export.verify_pack $CASE/products/fieldpack \
  --source-check --rundir $CASE/forecast --mesh $CASE/forecast/fort.14

# Python — product coverage vs the offline PNG families, and adapter
# variable names vs Reader.py (catches silent renames)
python -m post.export.parity_check $CASE/products/fieldpack \
  --graphs $CASE/post_forecast/graphs --graphs $CASE/post_wind/graphs

# Node — the same loader the browser uses
node ~/projects/CloudVision/threejs-shield-live-viz/verify-fieldpack.js \
  $CASE/products/fieldpack
```

## Wind bridge (ORDER 9)

`post/export/wind_bridge.py` turns SHiELD/FV3 surface output into ADCIRC met
forcing — `UGRD10m` / `VGRD10m` / `PRMSL` → Oceanweather WIN/PRE (or a NWS=6
`fort.22`), byte-compatible with what MetGet writes.

```bash
python -m post.export.wind_bridge \
  --shield $RUN/history/atmos_sos.nest02.tile7.nc \
  --grid   $OPS/ic/global_nest_Ida/grid_spec.nest02.tile7.nc \
  --out    $CASE/met_shield --stem shield_nest --format owi
```

`NWS=6` and `NWS=306` take the **same** met files: ADCIRC's 300-series prefix
means "coupled to SWAN", and the trailing digits are the met type. Adding waves
changes the fort.15 number, not the wind bridge.

The nest is curvilinear and OWI needs a regular grid, so the bridge resamples
(nearest source cell) and writes the cell counts, the fill values used outside
the nest footprint, and the target grid into `wind_bridge_manifest.json`.

## Out of scope (this ladder)

Runup (Holman/Stockdon), ASSET transects, OpenTopo runup bathymetry, TWLCC.
`modes.runup` is always `false`; the verifier fails the pack if it is not.

## Adding a product (G-EXT)

1. `post/export/field_adapters/my_thing.py` — `@register` a class with
   `name`, `products`, `available(ctx)`, `export(ctx)`.
2. Import it in `field_adapters/__init__.py`.
3. Done. `meta.fields[]` grows; the shell renders it with the default scalar or
   vector layer; no chrome edit.
