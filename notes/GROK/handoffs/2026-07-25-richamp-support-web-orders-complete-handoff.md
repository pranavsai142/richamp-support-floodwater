# 2026-07-25 — Handoff: richamp-support-web / suite house viz — ORDER 0–11 COMPLETE

**Supersedes for status:** `2026-07-25-richamp-support-web-handoff.md` (still the law for *why*)
**Bar met:** scientific integrity ≥ offline RICHAMP, plus interactive fidelity
**Shape:** coastal multiphysics export **into the existing Path B shell** — no second SPA, no second sacred JSON

---

## 1. One-screen status

| Item | State |
|------|-------|
| Coastal export `adcirc-fieldpack/v0` | **Shipped** — `post/export/`, contract doc, adapter registry, two verifiers |
| Loader family | **Shipped** — one `fieldpack-loader.js` loads gfdl + adcirc; atmos path unchanged |
| Suite shell | **Shipped** — Path B evolved in place: globe ↔ 2D, layers, stations, click sample, particles, deep links, quality modes |
| Atmos (Ida 36h) | **Verified, no regression** — nest PRMSL + 6 cube tiles, 0..35, PRMSL mb |
| Dual suite | **Verified** — both schemas render in one shell, swap live, no stale state |
| Wind bridge | **Shipped and exercised** — SHiELD 10 m winds → OWI WIN/PRE / fort.22, NWS 6 ≡ 306 settled |
| Waves | **Code complete, spatially unexercised** — raw `swan_*.nc` is on an unmounted drive (§6) |
| Runup | Out of scope, and the verifier fails any pack that turns it on |
| Grapher | Print only — G-DEPRECATE-READY met for interactive inspection |

**Human tester bar:** open one page, pick either suite, scrub real times, toggle
layers, click a station or any mesh point, read units from meta, share the URL.
No Grapher, no matplotlib, no NetCDF in the browser.

---

## 2. Gate table (every line reproducible from the commands in §4)

| Gate | Result | Evidence |
|------|--------|----------|
| **G-PACK** | PASS | fort.14 counts match (31 435 nodes / 58 369 tris); node coords match fort.63 to 3.8e-06°; ζ matches fort.63 to **1.95e-03 m** (float16 tolerance); dry-node counts preserved exactly |
| **G-LOAD** | PASS | `verify-fieldpack.js` on the coastal pack **and** on Ida 36h (no atmos regression; now also checks the 6 cube tiles) |
| **G-GLOBE** | PASS | 2.07 % coloured pixels; scrub changes the render; rendered vertices are the pack mesh, `max |Δ| = 0` over 31 435 nodes |
| **G-STN** | PASS | 29 markers (NOS/NDBC/USGS), 13 with data; model + model@node + obs + prediction on one chart; inspect panel names the stencil |
| **G-CLICK** | PASS | wet node → triangle weights + bed elev + series; outside the domain reports "no value", never 0 |
| **G-MULTI** | PASS (wind; waves = gap) | GFS wind u/v/speed + surface pressure; particles advect on the real field; **every off-clock field maps by timestamp — t0 → GFS index 145, 0 min error** |
| **G-2D** | PASS | 45.7 % coloured; time, field and all 12 layer visibilities preserved across globe ↔ 2D ↔ globe |
| **G-FV3** | PASS | PRMSL **mb** 978.7–1027.7, 36 times, 6 cube tiles, 3D stream coarser (12 vs 36) |
| **G-HOUSE** | PASS | both schemas load in one shell; swapping back leaves no stale layer |
| **G-OPS** | PASS | deep link round-trips time, field, view, layers, station, centre/zoom; skills stay operator-thin |
| **G-FINAL** | PASS | quality modes change wire stride 6→2→1 while the science array stays 31 435 values; snapshot PNG; drawer clears the colorbar |
| **G-EXT** | PASS | `maxele.py` = **one file + one import line**; three fields the shell has never heard of plot with their own units and long names |
| **G-DEPRECATE-READY** | Met for interactive inspection | see §5 |

Pure-module tests: **20/20** (`node test-suite-modules.js`) — index build 8 ms for
58 369 triangles, barycentric == mean-of-vertices at a centroid, dry vertex
refuses to blend, series uses fixed weights across time.

Parity: **all six adapters read exactly the variables `Reader.py` reads**; 7 offline
PNG families covered, 6 wave families are gaps (§6).

---

## 3. What shipped

### `richamp-support-floodwater/post/export/` (new)

| File | Role |
|------|------|
| `pack_writer.py` | binary law, meta assembly, **NaN policy**, float16 range guard |
| `context.py` | run inputs; time parse + stencil come from `Reader.py`, not reimplemented |
| `mesh_adapter.py` | fort.14 → `mesh/nodes.f32.bin` + `triangles.u32.bin` + bathymetry |
| `field_adapters/` | `water_fort63` · `wind_fort74` · `wind_gfs` · `wind_post` · `rain_gfs` · `waves_swan` · `maxele` |
| `station_export.py` | model series via the offline Readers; obs via `GetBuoy*` |
| `bookmarks.py` | the offline `*_AXIS` extents, as bboxes |
| `cli.py` | `--products`, `--path KEY=PATH`, `--post-stride`, exit 0/2/3 |
| `verify_pack.py` | structure **+ cross-check against the raw fort.14 / fort.63** |
| `parity_check.py` | adapter variables vs `Reader.py`; pack coverage vs offline PNG families |
| `wind_bridge.py` | SHiELD/FV3 → OWI WIN/PRE / fort.22 |
| `ADCIRC_FIELDPACK_V0.md` | the contract |

### `CloudVision/threejs-shield-live-viz/` (evolved, not forked)

`suite-shell.js` (app) · `suite-colormaps.js` · `suite-mesh-sample.js` ·
`wind-particles-pure.js` · `suite-chart.js` · extended `fieldpack-loader.js` and
`verify-fieldpack.js` · `verify-shell.js` (headless gate harness) ·
`test-suite-modules.js` · `serve.py` · `vendor/three.min.js` (offline).

---

## 4. Reproduce

```bash
CASE=~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512
RUN=~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z
VIZ=~/projects/CloudVision/threejs-shield-live-viz

# export + gates
cd ~/projects/richamp-support-floodwater
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir $CASE/forecast --mesh $CASE/forecast/fort.14 --case $CASE \
  --products mesh,water,wind,rain,waves,maxele,stations,obs_water \
  --temp-dir $CASE/products/_export_temp --outdir $CASE/products/fieldpack
PYTHONPATH=. pipenv run python -m post.export.verify_pack $CASE/products/fieldpack \
  --source-check --rundir $CASE/forecast --mesh $CASE/forecast/fort.14
PYTHONPATH=. pipenv run python -m post.export.parity_check $CASE/products/fieldpack \
  --graphs $CASE/post_forecast/graphs --graphs $CASE/post_wind/graphs \
  --graphs ./post_forecast/graphs

# shell + gates
cd $VIZ
rsync -a --delete $RUN/products/fieldpack/ ./data/fieldpack/
ln -sfn $CASE/products/fieldpack ./data/coast-ec95d
./serve.py 3412 &
node verify-fieldpack.js ./data/coast-ec95d --require-fields water_zeta
node verify-fieldpack.js ./data/fieldpack --require-fields TMP,OMG,Q --require-plev 31
node test-suite-modules.js
npm install --no-save puppeteer   # once
node verify-shell.js --pack ./data/coast-ec95d \
  --gate G-GLOBE --gate G-STN --gate G-CLICK --gate G-MULTI --gate G-2D \
  --gate G-EXT --gate G-OPS --gate G-FINAL --out shots
node verify-shell.js --pack ./data/fieldpack --gate G-FV3 --out shots
node verify-shell.js --gate G-HOUSE --out shots

# wind bridge
PYTHONPATH=. pipenv run python -m post.export.wind_bridge \
  --shield $RUN/history/atmos_sos.nest02.tile7.nc \
  --grid ~/projects/SHiELD_OPS/ic/global_nest_Ida/grid_spec.nest02.tile7.nc \
  --out $CASE/met_shield --stem ida_nest --format owi
```

Screenshots from the gate runs live in `$VIZ/shots/`.

---

## 5. Findings worth keeping

### 5.1 The offline temp files collide (real, pre-existing)

`Fort63Reader` and `Fort14Reader` both write `ADCIRC_Nodes.json` and
`ADCIRC_Station_To_Node_Distances.json` into the same temp dir, so whichever
runs last clobbers the other. In the golden `post_forecast` run this left four
stations (Newport, South Padre, Aransas, Key West) with an **all-NaN** water
series. Exporting into a clean temp dir gives those four real values, and nine
of thirteen stations match the offline numbers bit-for-bit with identical node
indices. Not fixed here (it is the print path's own file layout), but the export
now always uses `--temp-dir` of its own.

### 5.2 Station interpolation reaches across the basin

`generateDataFilesWithInterpolation` builds **one shared** support cloud from
every station's stencil. On a coarse mesh most stencils are empty, so a station
is interpolated from *other stations'* nodes: Fort Myers (19.6 km from its node)
lands 0.45 m from its own node's series, New London (6.0 km) 0.39 m. The pack
therefore carries `water` (offline parity) **and** `water_node` (that station's
own node, exact to 0.000e+00 vs `fort.63.nc`), with `node_distance_km` in the
catalog. The chart draws both.

### 5.3 `NWS = 306` is not a different met format

ADCIRC's 300-series prefix means "coupled to SWAN"; the trailing digits are the
met type. `306 = 6 + SWAN`. The wind bridge is the same for both — adding waves
changes the fort.15 number, not the forcing files. This closes the open item
"wind bridge format first: 306 vs OWI vs NWS=6".

### 5.4 ADCIRC's own peak beats the swath

`water_max` (max over the written snapshots) peaks at 6.176 m; `zeta_max` from
`maxele.63.nc` (max over every internal timestep) peaks at 6.239 m. The 6.3 cm
gap is what the hourly output interval misses. Both are in the pack.

### 5.5 Two shell bugs the gates caught (not review, not luck)

* the coastal camera mapped ECEF (Z-up) onto a Y-up orbit triple and pointed at
  the far side of the planet — G-GLOBE failed at 0.00 % coloured pixels;
* the particle stepper read a layer-record flag instead of `obj.visible`, so
  tracers never advected — G-MULTI caught it with a 0.00000 → 0.00000 delta.

---

## 6. Gaps, stated plainly

| Gap | Why | What unblocks it |
|-----|-----|------------------|
| **Wave spatial fields unexercised** | no `swan_*.nc` / `rads.64.nc` anywhere on this machine — the padcswan golden is on the unmounted external drive | mount `"/Volumes/Pranav's Hard Drive"`, then `--products waves --path wave_swh=…`; the adapter, field names, swath, radiation-stress vector and station path are written and variable-parity-checked, but no wave byte has passed through them |
| **Rain unexercised** | this case has no rain product (`gfs_wind.nc` carries PSFC, not precipitation) | any MetGet/GFS rain netCDF; `rain_accum` is `sum` over time per Grapher |
| **`fort.74` unexercised** | ADCIRC did not write it for this run | a run with `NOUTGW`/wind output enabled |
| **RICHAMP post wind not exported** | 6.1 GB, ~30 m grid; refuses to ship silently thinned | `--post-stride N` (records the stride in `meta.fidelity.decimation` and on the field row) |
| **2D basemap imagery** | the offline PNGs are pre-flipped for `imshow(extent=[lon_min,lon_max,lat_max,lat_min])`; orientation not yet confirmed against a landmark | verify one PNG against a known coastline, then drop into `data/basemaps/` with `basemaps.json`; the loader path is already wired |
| **Obs window** | CO-OPS verified water only exists up to now; a future forecast window falls back to tidal predictions (labelled separately on the chart) | nothing — this is correct behaviour |

---

## 7. Invariants (do not break)

1. **Fieldpack is the display source of truth.** No NetCDF in the browser, no free-painted geometry.
2. **`NaN` is dry / no data.** Discarded in the shader, skipped by auto ranges, breaks chart lines, reported as "dry" by the sampler. Never 0.
3. **Coordinates come from the run.** fort.14 connectivity and node lon/lat; nest `grid_lont`/`grid_latt`. The writer refuses non-finite coords; the bridge refuses to run without a grid_spec.
4. **Every field declares its stream and scrubs on it.** Timestamp matching, never index sharing.
5. **PRMSL is mb.** Verifier fails outside 800–1200; the GFS adapter converts and says so if a product hands over Pa.
6. **Units live in meta and reach the colorbar.** A field with no units fails the verifier.
7. **Swath = max over time; rain accumulation = sum.** Not the last frame.
8. **Wind direction is `atan2(-v, u)`**, once, in the shell; vectors carry their convention string.
9. **Decimation is explicit and recorded.** Quality modes touch display only; `--post-stride` is opt-in and written into the pack.
10. **`modes.runup` is false** and the verifier fails a pack that says otherwise.
11. **Stencils come from `Reader.py`.** Not reimplemented in JS, not reimplemented in the exporter.
12. **One shell, one loader, one schema allowlist.** New product = adapter + import line.

---

## 8. Anti-patterns (earned, not theoretical)

- Inventing lon/lat or fields "for the demo"
- PRMSL as Pa; naming `PSFC` "MSL" (caught and renamed `pressure_surface`)
- Zeroing dry nodes — a flat wet sheet over dry land
- Sharing a time index across streams (would have put GFS 6 days off at t=0)
- Nest-as-planet when cube tiles exist
- A gridded met field painted over the water it forces
- Claiming parity without diffing against the offline numbers
- "Looks good" without a gate; every visual claim here has a screenshot and a
  pixel-or-data assertion behind it
- Roadmap in skills — `/run-adcirc` gained 24 lines (S9e), `/fv3-viz` gained a
  suite-shell + wind-bridge block, nothing else

---

## 9. Next start

1. Mount the external drive → export the padcswan waves golden → re-run
   `parity_check` and expect 13/13 families covered, then `--gate G-MULTI`.
2. Confirm basemap PNG orientation, drop into `data/basemaps/`, and the 2D view
   gets its offline-matching context layer.
3. Run the wind bridge output through an actual ADCIRC run (`NWS=6`) and compare
   the resulting ζ to the MetGet-forced golden — that closes the suite loop.
4. Optional: rename the Path B tree to `suite-live-viz` (it now serves both
   suites; only the directory name still says shield).
5. Residual model−obs series and threshold-exceedance maps are the next natural
   analysis tools; the chart panel and layer registry already take them.

---

*One system writes the wind and the pressure. The other writes the water that hits the coast. One fieldpack family, one shell, and every claim behind a gate.*
