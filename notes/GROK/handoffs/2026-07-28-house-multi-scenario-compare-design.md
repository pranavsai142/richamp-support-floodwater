# Design — House multi-scenario compare + parametric pack (revised 2026-07-28)

**Status:** revises and **supersedes for integration scope**  
`2026-07-27-parametric-full-house-integration-design.md`  
**Inventory SoT:** `notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md`  
**Golden dual campaign:**  
`/Volumes/Pranav's Hard Drive/adcirc-local-smoke/{ec95d_lee_param_20230909,ec95d_lee_gfs_20230909}`  
**Shell:** `~/projects/CloudVision/threejs-shield-live-viz/`

---

## 1. Overview / Motivation

Parametric forcing is **done** as a real ADCIRC campaign (Lee). The house integration package must now:

1. Map **actual parametric case files** into fieldpack products (not hypothetical Milton paths).  
2. Treat Lee **param + GFS twins** as the first dual golden.  
3. Implement comparison as a **generic multi-scenario capability** — GFS vs parametric vs obs is only the first example. The product law is: **any house scenario/pack can be compared with any other** (and with obs), on shared time and comparable fields.

Today the shell loads **one pack at a time**. That is fine for inspection. Compare mode is additive: **N slots** (start with 2), each bound to a catalog entry / pack URL, with absolute-time scrub and field pairing.

---

## 2. Goals & Non-Goals

### Goals

| ID | Goal |
|----|------|
| G1 | Export Lee parametric case → honest `adcirc-fieldpack/v0` (water, param wind, track, stations/obs). |
| G2 | Export Lee GFS twin → pack with honest GFS wind labels. |
| G3 | Catalog cards for both + atmos Ida still in `packs.json`. |
| G4 | **Compare mode (v0):** two slots, absolute-time align, overlay or split series. |
| G5 | Compare API is **family-agnostic** — not `if (gfs && parametric)`. |
| G6 | Parametric pack shows driving track by default. |
| G7 | Obs series participate as a first-class compare participant (not only “background”). |
| G8 | **Residuals are first-class and composable through ≥4th order** — not a one-shot A−B toggle. Any residual can itself be a residual operand. |

### Non-Goals

- Shipping `richamp.wnd` / multi-GB fort.22 in the pack  
- Hardcoding only Lee or only GFS↔param  
- Pixel-perfect regrid of 565×625 PWM onto 0.25° GFS for v0 (station + ζ mesh compares first)  
- Second SPA  
- Claiming higher-order residuals “add physics” when linear (document algebra; still ship the presentation tree)  

---

## 3. Real parametric product set (contract from golden)

### 3.1 Required for a “parametric forced scenario” pack

| Product | Source file(s) on Lee golden | Pack representation |
|---------|------------------------------|----------------------|
| Mesh | `forecast/fort.14` | `mesh/*` |
| Water ζ | `forecast/fort.63.nc` | `water_zeta`, stream `adcirc` |
| Maxele | `forecast/maxele.63.nc` | `water_max` / native maxele |
| Parametric wind | `met_pwm/lee_parametric_wind.nc` | `param_wind_*` **or** wind fields with `source.family=parametric`, stream `parametric` |
| Driving track | `met_pwm/track.richamp` + `lee_best_track.trk` | `tracks/drive_track.json` |
| Stations + obs water | fort.63 + CO-OPS | `stations/*` |
| Scenario meta | `run_manifest.json` | `meta.scenario`, `modes.wind=parametric_nws6` |
| Rain (optional) | `met_pwm/RICHAMP_rain.nc` | rain fields if adapter |
| Analysis ζ (optional) | `analysis/fort.63.nc` | second phase pack or dual stream |

### 3.2 Explicitly **not** pack inputs (keep on disk only)

| File | Why |
|------|-----|
| `met_pwm/richamp.wnd` (~2.2 G) | raw; nc is display form |
| `forecast/fort.22` (~2.2 G) | drive met; already summarized in nc |
| PE* trees | junk |
| windgfdl binary / logs | ops only |

### 3.3 GFS twin pack (same storm, different met)

| Product | Source |
|---------|--------|
| Water / mesh | `ec95d_lee_gfs_20230909/forecast/*` |
| GFS wind | `post_wind/gfs_wind.nc` (217×157×155) |
| No drive track required | `modes.track=false` |
| `modes.wind` | `gfs_nws6_fort22` |

### 3.4 Wind_Inp / domain (verified)

```text
2023-09-09 00Z start · 216 hours · lon −101…−49 · lat 4…51 · 1/12°
→ 565 × 625 · fort.22 P in Pascals
```

---

## 4. Multi-scenario compare architecture (moonshot → v0)

### 4.1 Principle

> **Compare is a relationship between loaded sources, not a special met pair.**

Sources that can fill a slot:

| Slot source type | Examples |
|------------------|----------|
| Coastal fieldpack | Lee param, Lee GFS, ec95d GFS 5d, ricv1, … |
| Atmos fieldpack | Ida 36h SHiELD |
| Obs series | stations already inside a pack, or live/export-time CO-OPS |
| Derived | **residual nodes** (R1–R4+) — composable A−B on aligned samples; residual of residual |

**Anything vs anything** means:

- Same suite or cross-suite when fields are comparable (e.g. surface wind family, ζ vs ζ).  
- UI never assumes “left=GFS, right=param.” User assigns packs and fields to slots.  
- Lee dual is the **acceptance golden**, not the only code path.  
- **Any residual is itself a slot source** and can enter another residual (orders stack).

### 4.2 Catalog (`packs.json` / `scenarios.json`)

```json
{
  "packs": [
    {
      "id": "lee-param-ec95d",
      "label": "Lee AL13 — parametric PWM · ec95d",
      "url": "./data/coast-lee-param",
      "suite": "coast",
      "storm": { "name": "Lee", "basin": "AL", "number": "13", "year": 2023 },
      "met_family": "parametric",
      "default_utc": "2023-09-16T00:00:00Z",
      "compare_group": "lee-ec95d-20230909"
    },
    {
      "id": "lee-gfs-ec95d",
      "label": "Lee AL13 — GFS MetGet · ec95d",
      "url": "./data/coast-lee-gfs",
      "suite": "coast",
      "storm": { "name": "Lee", "basin": "AL", "number": "13", "year": 2023 },
      "met_family": "gfs",
      "default_utc": "2023-09-16T00:00:00Z",
      "compare_group": "lee-ec95d-20230909"
    }
  ],
  "compare_presets": [
    {
      "id": "lee-met-family",
      "label": "Lee: parametric vs GFS (same mesh/clocks)",
      "slots": ["lee-param-ec95d", "lee-gfs-ec95d"],
      "default_field": "water_zeta",
      "include_obs": true
    }
  ]
}
```

`compare_group` is a **hint** for presets (same storm/mesh/clocks). The engine does not require it.

### 4.3 Residual hierarchy (mandatory — not optional chrome)

Offline analog: `DiffGrapher` already co-plots **Forecast + Diff (+ Tide/obs)** — multi-trace residual thinking. The house must **generalize and deepen** that, not stop at one A−B map.

#### Orders (R0 … R4+)

| Order | Name | Definition | Lee dual example (ζ at a station) |
|------:|------|------------|-----------------------------------|
| **R0** | Raw | Field from a pack or obs series | ζ_param, ζ_gfs, ζ_obs |
| **R1** | First residual | `X − Y` on UTC-aligned samples | ζ_param−ζ_obs, ζ_gfs−ζ_obs, ζ_param−ζ_gfs |
| **R2** | Residual of residuals | `R1_a − R1_b` (or residual(R1, R0)) | (ζ_param−ζ_obs) − (ζ_gfs−ζ_obs) → **error superiority** series |
| **R3** | Third-order | residual involving an R2 and another source | e.g. R2_water vs R2_wind skill, or R2 − analysis_bias reference |
| **R4** | Fourth-order | residual of R3s / windowed skill residual | e.g. R3_window_A − R3_window_B; multi-station composite residual residual |

**Linear algebra note (document in UI, do not “hide”):**  
`(A−obs) − (B−obs) = A−B`. R2 error-diff is **algebraically** R1 model-model for pure subtraction — still ship it as an **explicit residual node** with pedigree labels (“param error − GFS error”) because operators think in error space, and future ops (normalized residual, abs residual, skill score) break the identity.

**Non-linear / non-trivial higher orders (must be supported as ops grow):**

| Op | Why order deepens |
|----|-------------------|
| `sub` | base residual |
| `abs_sub` | \|A−B\| — R2 of abs errors ≠ abs(A−B) in general structure of multi-series |
| `norm_sub` | (A−B)/scale or (A−obs)/σ — R2 of norms is not R1 |
| `skill` | 1 − RMSE_A/RMSE_ref style at stations (order ≥2 product) |
| `window` | residual of residuals over a time window (order +1) |

v0 ships **`sub` + recursive composition** through R4. v1 adds abs/norm/skill/window.

#### Residual node (first-class source)

```text
ResidualNode {
  id: "R2_err_sup_zeta"
  order: 2                    // computed depth of tree
  op: "sub"                   // later: abs_sub | norm_sub | skill | …
  left: SourceRef             // pack field | obs | ResidualNode id
  right: SourceRef
  role: "water_surface"       // inherited / declared
  domain: "station" | "mesh_node" | "grid"
  alignment: "utc_nearest"
  label: "param err − GFS err (ζ)"
  pedigree: ["lee-param/water_zeta", "obs", "lee-gfs/water_zeta"]  // for drawer
  units: same as operands (or derived)
  nan_policy: "propagate"     // NaN if either side dry/missing — never invent 0 residual
}
```

**Composition law:** a `SourceRef` is either:

1. `{ kind: "pack", packId, field|role }`  
2. `{ kind: "obs", stationKey, product }`  
3. `{ kind: "residual", residualId }`  ← **this is what enables R2–R4**

Max composition depth **≥ 4**. Soft UI warn beyond 4; hard fail only on cycles.

#### Residual alignment rules

| Domain | Align by | Required for residual |
|--------|----------|------------------------|
| Station series | station key + role + UTC | always (primary v0) |
| Mesh node field | **same mesh fingerprint** (node count + lon/lat hash) + UTC | Lee dual ζ residual map |
| Gridded field | same grid id **or** explicit regrid (not v0) | station wind residual first |

**NaN:** residual is NaN if either operand is NaN at that sample (dry ≠ 0 residual).

#### Residual UI (not a single button)

1. **Build residual** — pick left source, right source, op → creates ResidualNode, appears as a new series/slot.  
2. **Stack** — residual of two residuals (R2+).  
3. **Pedigree drawer** — show expression tree (e.g. `(param−obs)−(gfs−obs)`).  
4. **Chart** — multi-series: R0s + R1s + R2s… (colors by order).  
5. **Map** — residual field for mesh-domain R1+ when fingerprint allows.  
6. **Presets** — Lee package predefines residual tree (below), still editable.

#### Lee dual residual preset (acceptance tree)

```text
R0_p  = lee-param / water_zeta
R0_g  = lee-gfs   / water_zeta
R0_o  = obs water @ station

R1_po = R0_p − R0_o     # param error
R1_go = R0_g − R0_o     # GFS error
R1_pg = R0_p − R0_g     # model-model

R2_err = R1_po − R1_go  # error superiority (label as such; = R1_pg for pure sub)

R3_ex  = R2_err − R1_pg_ref   # optional: vs reference residual (identity check → ~0 for sub)
         OR residual(R2_err, window_mean(R2_err))  # anomaly of error-diff

R4_ex  = residual(R3_stationA, R3_stationB)   # cross-station residual of R3
         OR residual(R2_err_t0t1, R2_err_t1t2) # windowed residual residual
```

Gates must exercise **at least R0, R1, R2** on Lee; R3/R4 structure present and unit-tested even if presets are thin.

#### First-party analog map

| Analog | Port | Do not port |
|--------|------|-------------|
| `DiffGrapher` Forecast+Diff(+Tide) multi-trace | multi-series residual chart | matplotlib files |
| Offline model vs obs at stations | R1 model−obs | inventing obs in browser without pack/export |
| Same-mesh dual Lee | R1/R2 mesh residual maps | packing fort.22 |
| Stream-aware UTC scrub (suite already) | residual alignment | shared index residual |

### 4.4 Compare session model (shell)

```text
CompareSession {
  slots: [
    { id: "A", kind: "pack"|"obs"|"residual", ref, label, color },
    { id: "B", ... },
    // N slots; residuals appear as slots too
  ]
  residual_nodes: { [id]: ResidualNode }   // full tree, order ≤4+
  master_time_utc: ISO string               // absolute clock — not index
  field_role_default: "water_surface"
  view: "single" | "split" | "overlay-series" | "residual-map" | "residual-tree"
  obs: { enabled, stationKey }
}
```

**Time law:** scrubber drives **UTC**. Each slot/residual maps to nearest samples on its leaves. No shared index (GFS 217 vs param 216 is fine).

**Space law (v0):**

| Compare kind | Method |
|--------------|--------|
| Station series | Same station key; multi-line chart (R0…R4 + obs) |
| Mesh scalar (ζ) | Same mesh fingerprint → residual field at matched UTC |
| Gridded wind | Station wind residual first; full grid residual later (regrid) |
| Track | Draw each pack’s track if present (param has track; GFS may not) |
| Residual stack | Pedigree tree always available; map uses highest mesh-capable residual selected |

### 4.5 UI surfaces (v0)

1. **Mode toggle:** Inspect (1 pack) · Compare (N slots + residual tree).  
2. **Slot pickers:** catalog packs, obs, **and residual nodes**.  
3. **Field / role pairing:** bind by `meta.roles` (fallback same field name).  
4. **Chart:** multi-series for any selected sources including R1–R4 (`SuiteChart.plot` already takes a list of traces).  
5. **Build residual:** left/right/op → new node; allow left/right to be residuals.  
6. **Globe/2D:** primary field or selected residual map; pedigree in meta drawer.  
7. **Deep link:** slots + residual tree encoding + `t_utc` + station + obs.

### 4.6 Why not special-case GFS vs parametric

| Special-case trap | Generic design |
|-------------------|----------------|
| `if met===gfs && other===param` | slots = packs[]; compare_fields registry by **role** (`water_surface`, `wind_10m`, …) |
| Hardcoded field names | role → field name map in meta (`roles.water_surface = "water_zeta"`) |
| Only two packs | N slots (UI starts at 2) |
| Only coast | atmos packs can fill slots when roles match |

Lee dual proves: same `storm` + same `coldstart` + same mesh → best residual maps. Different storms still compare at stations/obs.

### 4.7 Field roles (light schema)

Add optional `meta.roles`:

```json
"roles": {
  "water_surface": "water_zeta",
  "water_max": "water_max",
  "wind_10m_u": "param_wind_u",
  "wind_10m_v": "param_wind_v",
  "wind_10m_speed": "param_wind_speed"
}
```

GFS pack maps the same roles to `wind_u` / `wind_v` / `wind_speed`. Compare binds by **role**, falling back to identical field names.

---

## 5. Technical requirements

### Parametric / dual export

| ID | Requirement |
|----|-------------|
| FR-P1 | Export Lee param pack from real paths in inventory research. |
| FR-P2 | `meta.scenario.met.family = "parametric"`; never label GFS. |
| FR-P3 | Track from `track.richamp` / best track → `tracks/drive_track.json`; default visible. |
| FR-P4 | Wind from `lee_parametric_wind.nc` (216×565×625); stride/subset policy if needed for browser. |
| FR-P5 | Export Lee GFS twin with `family=gfs` and `gfs_wind.nc`. |
| FR-P6 | Both packs share `coldstart_utc` / storm block for compare_group. |

### Generic compare

| ID | Requirement |
|----|-------------|
| FR-C1 | User can assign any two catalog packs to slots A/B. |
| FR-C2 | Master scrub is absolute UTC; each slot samples its own stream. |
| FR-C3 | Station chart supports ≥2 model series + obs. |
| FR-C4 | Residual nodes are first-class; **recursive** composition through **order ≥ 4**. |
| FR-C5 | R1 mesh residual when mesh fingerprint matches; station residual always when keys align. |
| FR-C6 | NaN residual when either side NaN — never invent 0. |
| FR-C7 | Residual pedigree (expression tree) in drawer; labels distinguish error-space R2 from raw R1 even if algebraically equal under pure `sub`. |
| FR-C8 | Compare presets are data (`compare_presets` + `residual_presets`), not code branches. |
| FR-C9 | Deep links restore compare session **including residual tree**. |
| FR-C10 | Gates: G-COMPARE-STN, G-COMPARE-TIME, G-COMPARE-SWAP, **G-RES-R1**, **G-RES-R2**, **G-RES-R3**, **G-RES-R4** (structure + NaN policy; Lee preset for R0–R2 full, R3–R4 unit/structure). |

### Non-functional

| ID | Requirement |
|----|-------------|
| NFR-1 | Memory: two coastal packs + Ida must remain usable on laptop; wind stride OK. |
| NFR-2 | No second SPA; extend suite-shell. |
| NFR-3 | Fieldpack remains display SoT per slot. |

---

## 6. User stories

### US-1 — Load parametric Lee alone

**As** a modeler, **I select** “Lee parametric” and see ζ, PWM wind, track, stations/obs.

### US-2 — Compare Lee parametric vs GFS

**As** a scientist, **I open** preset “Lee: parametric vs GFS”, scrub to 2023-09-16, and see both ζ series at Newport + obs.

### US-3 — Compare anything

**As** a suite user, **I put** Ida atmos in slot A and a coastal pack in slot B only if I choose comparable fields — or two coastal packs from different storms at the same station — without a code path named “gfsParamCompare”.

### US-4 — Obs as peer

**As** a validator, **I toggle** obs on the multi-series chart as a peer series, not only a separate offline PNG.

### US-5 — Residual stack through 4th order

**As** a scientist, **I build** param−obs and GFS−obs (R1), then their difference (R2 error superiority), then residual of that against a window or third reference (R3), then cross-station or cross-window residual (R4), **so that** higher-order residual structure is real, not a single “diff” button.

**AC:** residual tree depth ≥4 supported; Lee preset creates R0–R2; G-RES-R3/R4 pass structure tests; chart can show R0+R1+R2 together; NaN dry policy holds.

---

## 7. Technical guidelines

1. **Fieldpack SoT per pack slot** — no live NetCDF in browser.  
2. **Roles over hardcodes** for compare bindings.  
3. **UTC master clock** for multi-pack time **and residual alignment**.  
4. **Parametric ⇒ track on** in inspect mode.  
5. **Honest met.family** in meta.  
6. **Presets are data.**  
7. **Residuals are sources** — recursive; order ≥4; pedigree required.  
8. **NaN propagates in residuals** — dry ≠ zero error.  
9. **Same-mesh residual maps only when fingerprint matches** (Lee dual: same fort.14).  
10. **Document linear identities** (R2 error-diff = R1 model-model under pure sub) without deleting the node.  
11. **ec95d skill is process-grade** — UI may still compare; docs say so.  
12. **Do not ship multi-GB wnd/fort.22.**  
13. **Skills stay thin** — point at this design + inventory.

---

## 8. Proposed implementation phases

### Phase 1 — Dual fieldpacks + catalog (no compare UI yet)

- Export both Lee cases (`post.export.cli`).  
- `wind_parametric` adapter or path+label honesty.  
- `track_export` from track.richamp / best trk.  
- Stage `./data/coast-lee-param` + `coast-lee-gfs`; enrich packs.json.  
- Gates: G-LOAD both; inventory shows met family.

### Phase 2 — Inspect completeness

- Track layer; default_utc near NE impact (2023-09-16).  
- Param wind particles on parametric pack.

### Phase 3 — Compare v0 + residual engine (generic)

- CompareSession + **ResidualNode graph** (recursive to order 4).  
- Dual (N) pack load; UTC scrub.  
- Multi-series station chart: R0s + obs + built residuals (`SuiteChart.plot` multi-trace).  
- Lee preset: R0_p, R0_g, R0_o, R1_po, R1_go, R1_pg, R2_err.  
- Gates G-COMPARE-* + **G-RES-R1/R2** (and R3/R4 structure tests).

### Phase 4 — Residual maps + deeper orders

- Node-wise mesh residual for R1+ when fingerprint matches.  
- R3/R4 presets (window residual residual, cross-station).  
- Optional abs/norm ops.  
- Pedigree drawer polish.

### Phase 5 — Moonshot stretch

- N>2 packs; atmos↔coast role pairing; shareable compare URLs with residual tree; export residual fieldpack as derived product.

---

## 9. Boilerplate

### Export param

```bash
CASE="/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_param_20230909"
REPO=~/projects/richamp-support-floodwater
cd $REPO
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir "$CASE/forecast" --mesh "$CASE/forecast/fort.14" --case "$CASE" \
  --products mesh,water,maxele,wind_parametric,track,stations,obs_water \
  --path wind_parametric="$CASE/met_pwm/lee_parametric_wind.nc" \
  --path track_source="$CASE/met_pwm/lee_best_track.trk" \
  --outdir "$CASE/products/fieldpack"
```

### Export GFS twin

```bash
CASEG="/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_gfs_20230909"
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir "$CASEG/forecast" --mesh "$CASEG/forecast/fort.14" --case "$CASEG" \
  --products mesh,water,maxele,wind,stations,obs_water \
  --path wind_gfs="$CASEG/post_wind/gfs_wind.nc" \
  --outdir "$CASEG/products/fieldpack"
```

### Catalog preset + residual tree

```json
"compare_presets": [{
  "id": "lee-met-family",
  "slots": ["lee-param-ec95d", "lee-gfs-ec95d"],
  "default_field_role": "water_surface",
  "include_obs": true,
  "residuals": [
    { "id": "R1_po", "order": 1, "op": "sub",
      "left": { "kind": "pack", "packId": "lee-param-ec95d", "role": "water_surface" },
      "right": { "kind": "obs", "product": "water" },
      "label": "param − obs" },
    { "id": "R1_go", "order": 1, "op": "sub",
      "left": { "kind": "pack", "packId": "lee-gfs-ec95d", "role": "water_surface" },
      "right": { "kind": "obs", "product": "water" },
      "label": "GFS − obs" },
    { "id": "R1_pg", "order": 1, "op": "sub",
      "left": { "kind": "pack", "packId": "lee-param-ec95d", "role": "water_surface" },
      "right": { "kind": "pack", "packId": "lee-gfs-ec95d", "role": "water_surface" },
      "label": "param − GFS" },
    { "id": "R2_err", "order": 2, "op": "sub",
      "left": { "kind": "residual", "residualId": "R1_po" },
      "right": { "kind": "residual", "residualId": "R1_go" },
      "label": "param err − GFS err" },
    { "id": "R3_err_anom", "order": 3, "op": "sub",
      "left": { "kind": "residual", "residualId": "R2_err" },
      "right": { "kind": "residual", "residualId": "R2_err", "reduce": "window_mean" },
      "label": "R2 anomaly vs window mean" },
    { "id": "R4_cross_stn", "order": 4, "op": "sub",
      "left": { "kind": "residual", "residualId": "R3_err_anom", "station": "A" },
      "right": { "kind": "residual", "residualId": "R3_err_anom", "station": "B" },
      "label": "R3 residual across stations" }
  ]
}]
```

---

## 10. Alternatives considered

| Alt | Why not |
|-----|---------|
| Only toggle met inside one pack | Forces inventing dual met in one run; loses real dual ζ response |
| Hardcoded GFS-vs-param page | Fails “anything vs anything”; one-off |
| Server-side regrid always | Heavy; station/ζ-first is enough for v0 |
| Diff only offline PNGs | Abandons house interactive bar |

---

## 11. Key decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fixture | Lee dual campaign (real paths) | Parametric is done |
| Compare abstraction | N slots + roles + UTC | Generalizes beyond GFS/param |
| Track source | best track + track.richamp | Golden has no NHC shp |
| Wind in pack | owi2wind nc only | Size + schema |
| Residual law | Recursive ResidualNode, order ≥4; R0–R2 Lee gates; DiffGrapher multi-trace analog | Single A−B button is incomplete |
| Linear identity | Document R2 error-diff = R1 model-model under pure `sub`; keep both nodes | Deleting R2 “because algebra” loses operator language |
| Presets | catalog JSON + residual trees | Data not code |

---

## 12. Open questions

1. Prefixed `param_wind_*` vs role-mapped `wind_*` with family in meta — either OK if roles exist.  
2. Load two full 185 M-class winds — may need stride on param wind for browser.  
3. Whether analysis-phase ζ is a third pack slot or a stream inside one pack.  
4. Mesh fingerprint for residual safety (node count + hash of lon/lat).  
5. Default max UI depth (4) vs hard engine limit.  
6. When to add `abs_sub` / `norm_sub` / `skill` (needed for non-trivial R3/R4 beyond linear identities).  

---

## 13. References

- Inventory research (this revision’s foundation)  
- Lee dual campaign md on external smoke root  
- Suite shell packs.json / loadPack  
- Prior full integration design 2026-07-27 (scenario catalog still valid; compare expanded here)  
- Orders-complete house law (fieldpack SoT, gates)  
