# 2026-07-25 — Handoff: richamp-support-web / suite house viz  
## Full scientific fidelity · Path B foundation · ORDER 0–11 · ORDER 9 = real SHiELD/FV3 (Ida 36h)

**Status:** durable single source of truth for the **house visualization initiative**  
**Spirit:** `/fabel-open-ended` — index every product class, preserve twin contracts, no invented fields  
**Bar:** **same scientific integrity as offline `richamp-support-floodwater`**, plus modern interactive fidelity (globe + 2D, fieldpack SoT, verify harnesses)

| Companion | Role |
|-----------|------|
| `2026-07-25-richamp-support-web-plan.md` | Compact index + gates |
| `2026-07-25-richamp-support-web-design.md` | UI catalog, FRs, adapters |
| Twin Path B | `~/projects/CloudVision/threejs-shield-live-viz/` |
| Atmos law | `~/projects/SHiELD_OPS/post/FIELDPACK_V0.md` |
| Coastal ops | `2026-07-25-run-adcirc-gfs-post-handoff.md` |

---

## 1. One-screen status

| Item | State |
|------|--------|
| **Product name (working)** | **richamp-support-web** = coastal multiphysics export + layers into the **unified house shell** (not a forever-forked MapLibre app) |
| **House** | One fieldpack family + one live viz (Path B lineage) for **FV3/GFS-class atmosphere** and **ADCIRC+SWAN coast** |
| **Path B (shield-fv3-viz)** | **MVP DONE** — load real fieldpack, nest PRMSL animate, globe cube tiles, verify PASS |
| **Canonical atmos data** | Ida **36h** SUCCESS: `~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z/` |
| **Coastal multiphysics offline** | Water + **waves** vetted; wind/rain/topo in same Grapher spirit |
| **Coastal fieldpack export** | Not started — ORDER 1–2 |
| **Runup / Holman / transect** | **OUT OF SCOPE** this ladder |
| **Grapher** | Print fallback; interactive SoT ends at G-DEPRECATE-READY (ORDER 11) |

**Human tester bar (ORDER 11 done):**  
One browser shell. Load **Ida 36h fieldpack** and/or **coastal multiphysics pack**. Globe + 2D. Scrub real times. Toggle water · wind · rain · topo · **wave quantities** · atmos PRMSL/TMP/…. Stations + click sample. Units from meta. **No invented coordinates or fields.** No Grapher required.

---

## 2. North star — scientific house, not a demo map

### What “full scientific integrity” means here

Offline RICHAMP earned fidelity over years. The web house must **not** lower that bar for interactivity.

| Integrity rule | Offline (floodwater) | House web (this initiative) |
|----------------|----------------------|-----------------------------|
| SoT for display | NetCDF / fort products | **Fieldpack** built from those products |
| Geometry | Real fort.14 tris / real GFS grid | Same connectivity / lon-lat — **no free paint** |
| Time | Coldstart-parsed model time | `times_utc` from export; stream-aware scrub (hourly vs 3h) |
| Stations | Closest-node stencil + thresholds | Same Readers → series in pack |
| Obs | CO-OPS product API, NDBC, USGS | Export-time or live; **not dead ERDDAP mat** |
| Units / conventions | Grapher wind dir, ζ m, SWH m, … | meta.units; **PRMSL is mb not Pa** |
| Multiphysics | One `generateGraphs` pass | One pack / one layer registry |
| Verify | Graphs exist / ops green | **Node verify + visual gates** |
| Extensibility | `*Reader` Lego | `FieldAdapter` + `meta.fields[]` |

**Modern fidelity (added by house, not instead of science):**

- Globe + 2D views, same pack  
- Time play / scrub / deep link  
- Wind particle tracers (display DNA from twin)  
- Click-anywhere sample on unstructured mesh  
- Quality modes (explicit LOD only — never silent decimation of science arrays)  
- Dual-suite under one shell (atmos + coast)

### Dual suite physics

| Atmosphere (twin) | Coast (sister) |
|-------------------|----------------|
| **FV3** dycore family — **operational GFS is FV3**; local full fidelity = **SHiELD** | **ADCIRC (+SWAN)** |
| PRMSL, TMP, OMG, Q, winds, precip, nest + globe tiles | ζ, wind, rain, topo, **SWH/MWD/periods/rads** |
| CloudVision + SHiELD_OPS | This repo export → house shell |
| Path B fieldpack **already live** | Coastal fieldpack **to build** |

MetGet GFS for ADCIRC forcing and SHiELD/FV3 products are the **same atmospheric side of the house**. ORDER 9 bridges wind into ADCIRC; viz shows both packs.

### Architecture

```text
                    THE HOUSE (scientific viz)
┌──────────────────────────────────────────────────────────────────┐
│ suite-run/ (or dual golden roots)                                  │
│   atm/   products/fieldpack/   gfdl-fieldpack/v0   ← Ida 36h       │
│   coast/ products/fieldpack/   adcirc-fieldpack/v0  ← multiphysics  │
│   bridge/  FV3/GFS-class wind → fort.22 / OWI / 306                │
└────────────────────────────┬─────────────────────────────────────┘
                             │  shared envelope: meta.fields[] · f16/f32 LE
              ┌──────────────┴──────────────┐
              ▼                             ▼
   suite-live-viz (Path B)            ops Path A (thin)
   GLOBE = presentation north star    maps PNGs / view3d / offline HTML
   2D = first-class scientific view
   field-agnostic layers + verify
```

**Deprecation trajectory:** after ORDER 11, interactive inspection lives in the house; this repo keeps Readers + export + `/run-adcirc`; Grapher becomes optional print — not the product SoT.

---

## 3. Fabel-style product index (full coastal + atmos scope)

### I1 — Coastal model products (IN SCOPE)

| ID | Product | Source | Fidelity notes |
|----|---------|--------|----------------|
| D-WAT | Water surface ζ | fort.63.nc | Unstructured node; full time; dry/wet as model |
| D-WIND-F | ADCIRC wind | fort.74.nc | u/v; dir convention parity Grapher |
| D-WIND-G | GFS wind | MetGet/GFS nc | structured or interp to stations |
| D-WIND-P | POST/RICHAMP wind | post wind nc | high-res when present |
| D-RAIN | Precip | GFS/MetGet rain | rate + accumulation semantics (sum) |
| D-MESH | Bathymetry / mesh | fort.14 | real tris; elev = −depth as offline |
| D-SWH | Sig. wave height | swan_HS.63.nc | **first-class** |
| D-MWD | Mean wave dir | swan_DIR.63.nc | first-class |
| D-MWP/PWP | Periods | swan TM*/TPS | first-class |
| D-RAD | Radiation stress | rads.64.nc | mag/dir first-class |
| D-MAX | Swaths | max over time | max along time, not last frame |

### I2 — Coastal obs (IN SCOPE)

| ID | Source | Use |
|----|--------|-----|
| O-NOS | CO-OPS product API | water / wind stations |
| O-NDBC | NDBC | wave obs when waves on |
| O-USGS | NWIS | rain gauges |

### I3 — Atmosphere products (IN SCOPE — Path B / ORDER 9)

| ID | Product | Stream | Notes |
|----|---------|--------|-------|
| A-PRMSL | Sea-level pressure | surface hourly | **mb**, ~1000; mean ≪200 ⇒ unit bug |
| A-TMP | Temperature | volume ~3h | plev scrub |
| A-OMG | Omega | volume ~3h | Pa/s |
| A-Q | Specific humidity | volume ~3h | kg/kg — **not** cloud water |
| A-GLOBE | PRMSL on cube faces | tiles 1–6 | full Earth C96, not nest-only |
| A-NEST | High-res nest | tile7 / nest pack | Gulf/SE US for Ida |

### I4 — Explicit OUT OF SCOPE (this ladder)

| Excluded | Reopen when |
|----------|-------------|
| Runup Holman/Stockdon, ASSET transect, OpenTopo bathy for runup, TWLCC | Dedicated waves+runup golden + later handoff |
| JS FV3 dycore as weather SoT | Never for production display |
| Invented lon/lat or synthetic storms for “pretty demos” | Never |
| Multi-tenant SaaS / auth productization | Later ops |

### I5 — Spatial / temporal integrity

- CRS: model lon/lat (display lon −180..180 where twin does)  
- Coastal: fort.14 connectivity sacred  
- Atmos: real `grid_lont`/`grid_latt` / fregrid / cube tiles from export  
- Time: multiple streams may differ (surface hourly vs 3D 3-hourly) — **map scrubbers per field dims**, don’t force one clock blindly  
- Swath = max; rain accum = sum (Grapher semantics)

### I6 — Extensibility (Lego)

```text
New netCDF/product → FieldAdapter (wrap Reader) → pack field row
                  → default Scalar/Vector/Grid layer
                  → no chrome rewrite (G-EXT)
```

Same composition pattern as `Fort63Reader` / `WaveReader` / `GFSRainReader`.

### I7 — UI surfaces (scientific, weather-site)

Full catalog in design §6.6. Minimum for integrity:

- Layer stack: on/off, opacity, colormap, range, colorbar, units  
- Time: play/pause/step/scrub/speed; stream-aware  
- Globe + 2D toggle, bookmarks  
- Stations + model±obs series  
- Click sample (nearest node / triangle interp)  
- Meta drawer: run_id, units, datum notes, node id, dims, source files  
- Modes: multiphysics toggles (not runup)

---

## 4. Path B / shield-fv3-viz — preserved emphasis (house law)

Do **not** dilute these when adding coast:

1. **Fieldpack is display SoT** — prefer pack over re-parsing NetCDF in the browser.  
2. **`meta.fields[]` field-agnostic** — iterate; don’t hardcode only PRMSL forever.  
3. **Binary law** — f16 LE fields, f32 LE coords, row-major.  
4. **Loader + `verify-fieldpack.js`** — PASS required.  
5. **Globe presentation spine** — nest overlay + full cube tiles when present.  
6. **No `fv3-solver.js` as production weather** — dycore stays separate.  
7. **Units/coords hard fails** — PRMSL mb trap permanent.  
8. **Sister modular stages** — read → productize → viz (floodwater pattern).  
9. **Dual path house** — Path B globe + Path A 2D/maps/view3d ops.  
10. **Skills thin** — `/fv3-viz`, `/run-adcirc`, `/run-shield` operators; roadmap here.

---

## 5. Sacred fieldpack family

```text
fieldpack/
  meta.json
  coords/ | mesh/ | tiles/
  fields/*.f16.bin
  stations/          # coastal
```

**Allowlist:** `gfdl-fieldpack/v0` | `adcirc-fieldpack/v0` | `suite-fieldpack/v0`  
**grid_type:** `nest_curvilinear` | `regular_latlon` | `adcirc_unstructured` | (+ cube tiles as documented in meta)

Coastal mesh block + nodal `zeta`/`swh`/… as previously designed. Twin field rows stay law for atmos.

---

## 6. Golden cases (open these, don’t invent)

### A — Atmosphere: Ida 36h SHiELD/FV3 (**ORDER 9 contract**)

```text
RUN=~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z
# SUCCESS stamp present
# Sim window ~2021-08-29 00Z + 36h hourly surface
```

| Priority | Path | Role |
|----------|------|------|
| **1 — Path B pack (preferred)** | `$RUN/products/fieldpack/` | Web/globe SoT |
| | `meta.json` | **schema gfdl-fieldpack/v0 — read first** |
| | `coords/{lon,lat,plev}.f32.bin` | nest coords |
| | `fields/{PRMSL,TMP,OMG,Q}.f16.bin` | nest science |
| | `tiles/tile{1..6}/` | **full-Earth native C96 faces (PRMSL)** |
| **2 — Path A ops** | `$RUN/products/maps/` | PNG 2D |
| | `$RUN/products/view3d/` | pressure-level scrubber HTML |
| **3 — Raw if needed** | `history/atmos_sos.nest02.tile7.nc` | surface hourly (36) |
| | `history/atmos_sos.tile{1..6}.nc` | global tiles |
| | `history/atmos_3d_8xdaily.nest02.tile7.nc` | 3D ~3-hourly (12) |
| Grid | `~/projects/SHiELD_OPS/ic/global_nest_Ida/grid_spec*.nc` | lon/lat |

**Verified:** `node …/verify-fieldpack.js $RUN/products/fieldpack` → **PASS** (time=36, PRMSL mb band ok).

**Show Path B (working explorer):**

```bash
cd ~/projects/CloudVision/threejs-shield-live-viz
rsync -a --delete $RUN/products/fieldpack/ ./data/fieldpack/
python3 -m http.server 3412
# open http://127.0.0.1:3412/
# Play/Pause = full PRMSL timeseries; globe = 6 cube tiles; nest = high-res overlay
```

**One-shot re-post:**

```bash
~/projects/SHiELD_OPS/bin/post_fv3_viz.sh --path-b-only --open $RUN
# skill: /fv3-viz
```

**Integration tips (ORDER 9 — non-negotiable):**

- Contract: `gfdl-fieldpack/v0` — iterate `meta.fields[]`  
- **PRMSL units = mb (~1000), NOT Pa** — mean &lt;~200 ⇒ unit bug  
- Lon may be display (−180..180). Nest ≈ Gulf/SE US; **globe is full cube**, not nest-only  
- Time fidelity: surface hourly (PRMSL 0..35); 3D TMP/OMG/Q coarser (~12 steps) — **map scrubbers accordingly**  
- **Q = specific humidity (kg/kg)**, not cloud water. Clouds ≈ REFC / condensate (not always in pack)  
- Prefer fieldpack over re-parsing NetCDF in web  
- **Do NOT use** `threejs-cubed-sphere-gnomonic/fv3-solver.js` as SoT for production weather  
- Sister pattern: floodwater modular stages; dual path = globe (B) + 2D (A)

**Minimal success house viz v0 (atmos):**  
Load this fieldpack → render nest PRMSL + optional globe tiles → scrub/animate t=0..35 → units from meta → **don’t invent coordinates**.

### B — Coast water (+ wind offline graphs)

```text
CASE_W=~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/

# Water + mesh maps + station water (post_forecast)
$CASE_W/post_forecast/graphs/
  *_water.png  *_station_water.png  all_stations_water.png
  map_elevation.png  elevation.png  closest_points.png

# Wind station graphs (same case; post_wind)
$CASE_W/post_wind/graphs/          # and/or richamp_graphs/
  *_wind_speed.png  *_wind_direction.png

# Raw products for export
$CASE_W/analysis|forecast/fort.63.nc  fort.14 via ec95d_run/
```

### C — Coast waves (multiphysics vetted — graphs moved into this repo)

```text
# Offline reference PNGs (copied into git workspace for desert-island access)
~/projects/richamp-support-floodwater/post_forecast/
  graphs/*_wave_{swh,mwd,mwp,pwp,radstress_*}   # ~71 wave product PNGs
  postprocess.log  temp/

# Full padcswan run (raw swan_*.nc etc.) may still live on external drive if needed:
# "/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_gfs_1d_waves_noutgw_2026072512/"
#   forecast/swan_HS.63.nc, swan_DIR, periods, rads.64.nc, …
#   run_manifest: modes.waves=true, generate_runup=false, ntimes=24
```

---

## 7. ORDER ladder 0–11

| ORDER | Name | Deliverable | Scientific gate |
|------:|------|-------------|-----------------|
| **0** | Law | This handoff; fidelity bar; Path B preserved | `/init` points here |
| **1** | Export skeleton | `post/export/`, `ADCIRC_FIELDPACK_V0.md`, FieldAdapter registry | meta envelope twin-compatible |
| **2** | Mesh + water | fort.14 + fort.63 → pack | G-PACK: counts, ζ finite, times_utc |
| **3** | Loader family | Path B allowlist + unstructured mesh | G-LOAD verify PASS on coastal pack |
| **4** | Globe water | ζ on Path B shell | G-GLOBE human + units |
| **5** | Stations + CO-OPS | series integrity vs offline graphs | G-STN |
| **6** | Click + time UX | triangle/node sample; play/scrub | G-CLICK |
| **7** | **Multiphysics coast** | wind + rain + **waves** (SWH/DIR/periods/rads) from waves golden | G-MULTI vs Grapher product set |
| **8** | **2D finality** | scientific 2D view same pack; bookmarks; colorbars | G-2D |
| **9** | **House atmos integrate** | **§6.A Ida 36h contract** — nest+tiles+scrub; dual-suite ready; wind bridge design/start | G-HOUSE / G-FV3 |
| **10** | Deep links + ops thin | URL state; `/run-adcirc` + `/fv3-viz` pointers only | G-OPS |
| **11** | **House finality** | polish, quality modes, residual model±obs optional, G-DEPRECATE-READY | interactive multiphysics + FV3 without Grapher/matplotlib |

### ORDER 9 expanded (FV3 / SHiELD — in scope now)

ORDER 9 is not a vague “bridge later.” It is **scientific integration against real SHiELD/FV3 output**:

1. Treat `$RUN/products/fieldpack/` (Ida 36h) as **canonical atmos contract**.  
2. House shell loads it without inventing fields (Path B already proves v0).  
3. Ensure coastal pack + atmos pack can coexist under suite shell (layer registry / case picker).  
4. Document/implement **wind bridge recipe**: SHiELD/FV3 (GFS-class) surface winds → ADCIRC fort.22 / OWI / 306 (waves golden used NWS=306 — align deliberately).  
5. Gates: verify-fieldpack PASS; human play PRMSL 0..35; globe tiles visible; nest overlay; units mb; no dycore SoT.

Optional companion ops (not instead of fieldpack): `maps/`, `view3d/`, `post_fv3_viz.sh`.

### Success gates (suite)

| Gate | Meaning |
|------|---------|
| G-PACK | Coastal multiphysics-capable pack export |
| G-LOAD | Shared loader loads coastal + gfdl packs |
| G-GLOBE | Coastal water on globe |
| G-STN / G-CLICK | Stations + sample integrity |
| G-MULTI | Wind/rain/**waves** scientific layers |
| G-2D | 2D scientific view complete |
| **G-FV3 / G-HOUSE** | Ida 36h pack integrated; dual suite visible; bridge path clear |
| G-OPS | Thin skills |
| G-FINAL / G-DEPRECATE-READY | ORDER 11 |
| G-EXT | New product = adapter only |

---

## 8. Where code lives

| Concern | Location |
|---------|----------|
| Coastal multiphysics export | this repo `post/export/` (new) — Readers Lego |
| Grapher | print only |
| `/run-adcirc` | skill; thin pointer ORDER 10 |
| Atmos export / post | `SHiELD_OPS/post/`, `bin/post_fv3_viz.sh` |
| **House live viz** | `CloudVision/threejs-shield-live-viz/` **extend** |
| Loader + verify | Path B tree |
| `/fv3-viz` | twin skill for atmos post/open |
| Wind particles DNA | `wind-viz-display.js` (display only) |

---

## 9. Key decisions (locked)

| Decision | Choice |
|----------|--------|
| Fidelity bar | **≥ offline RICHAMP** for shared products; interactive is additive |
| Path B emphasis | **Preserved as house law** (§4) |
| FV3 / GFS | Same atmospheric family; SHiELD = local full-fidelity FV3; GFS is FV3-class |
| ORDER 9 data | **Ida 36h** run above — real products only |
| Coastal products | Multiphysics including **waves** |
| Runup | Out of scope this ladder |
| Presentation | Extend Path B globe; 2D ORDER 8 |
| Fieldpack | Twin envelope; no second religion |
| Deprecate interactive Grapher | After G-DEPRECATE-READY |

---

## 10. Anti-patterns

- Inventing fields or lon/lat for demos  
- PRMSL as Pa  
- Q as “clouds”  
- Nest-only globe when tiles exist  
- Forcing 3D volume clock onto hourly PRMSL (or vice versa) without mapping  
- JS dycore as production weather SoT  
- Second SPA / second sacred JSON  
- Water-only house forgetting wind/rain/**waves**  
- Runup sneaking in via meshExists  
- Silent science decimation  
- Roadmap dump into skills  
- Re-parsing all NetCDF in browser when fieldpack exists  

---

## 11. Open items

- [ ] Keep Ida 36h pack rsynced into Path B `data/fieldpack` for offline demos  
- [ ] Wave period naming: TMM10 vs TPS → mwp/pwp in meta  
- [ ] Wind bridge format first: 306 vs OWI vs NWS=6 (align with padcswan golden)  
- [ ] 2D implementation choice inside Path B  
- [ ] Rename Path B → `suite-live-viz` after dual packs load  

---

## 12. Next session start

1. `/init` → **this handoff**.  
2. Prove atmos floor:

```bash
RUN=~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z
node ~/projects/CloudVision/threejs-shield-live-viz/verify-fieldpack.js $RUN/products/fieldpack
# optional: rsync pack → Path B data/ && python3 -m http.server 3412
```

3. Prove coastal offline references:

```bash
ls ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_forecast/graphs | head
ls ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_wind/graphs | head
ls ~/projects/richamp-support-floodwater/post_forecast/graphs | head
```

4. **Implement ORDER 1–2** (export mesh+zeta; adapter registry multiphysics-ready).  
5. Do not start a greenfield web app that ignores Path B + Ida fieldpack.

**ORDER 1–2 prompt:**

```text
Implement ADCIRC fieldpack export (ORDER 1–2): mesh + zeta, twin-compatible
gfdl-fieldpack envelope, FieldAdapter registry sized for wind/rain/waves at ORDER 7.
ADCIRC_FIELDPACK_V0.md. Verify script. No runup. No new SPA — Path B remains house shell.
Read handoff §3–§7 first.
```

**ORDER 9 reminder prompt (when dual shell ready):**

```text
CloudVision house viz — integrate against real SHiELD/FV3 output (Ida 36h).
RUN=~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z
Fieldpack preferred; meta.fields[] agnostic; PRMSL mb; nest + tiles/tile1..6;
time 0..35 surface; 3D coarser; no dycore SoT; no invented coords.
Minimal success: load pack, nest PRMSL + globe tiles, scrub/animate, units from meta.
```

---

## 13. Artifact index

| What | Where |
|------|--------|
| This handoff | `notes/GROK/handoffs/2026-07-25-richamp-support-web-handoff.md` |
| Plan / design | same stem |
| Path B | `~/projects/CloudVision/threejs-shield-live-viz/` |
| Ida 36h pack | `~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z/products/fieldpack/` |
| FIELDPACK_V0 | `~/projects/SHiELD_OPS/post/FIELDPACK_V0.md` |
| Water graphs | `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_forecast/graphs/` |
| Wind graphs | `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_wind/graphs/` |
| Waves graphs | `~/projects/richamp-support-floodwater/post_forecast/graphs/` |

---

*Scientific integrity first. Fieldpack is the contract. Path B is the spine. Ida 36h is the atmos truth. Multiphysics coast including waves. Runup later. Build the house.*
