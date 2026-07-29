# 2026-07-28 — Handoff: House integration revised (parametric inventory + multi-scenario compare)

**Status:** design revised against **completed** Lee dual campaign  
**Supersedes for house integration intent:**  
`2026-07-27-parametric-full-house-integration-handoff.md` (keep for history; **this is the law**)  
**Design:** `2026-07-28-house-multi-scenario-compare-design.md`  
**Inventory:** `notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md`

---

## 1. One-screen status

| Item | State |
|------|--------|
| Parametric ADCIRC run | **DONE** — `ec95d_lee_param_20230909` |
| GFS twin (same clocks/mesh) | **DONE** — `ec95d_lee_gfs_20230909` |
| Campaign note | `…/adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md` |
| Real file inventory | **Captured** (research 2026-07-28) |
| House fieldpacks for Lee | **Not exported yet** |
| Multi-scenario compare in shell | **Designed (generic)** — not GFS/param-only |
| Track in golden | **track.richamp + BEST trk** (no NHC shp this run) |
| Wind house-ready nc | `met_pwm/lee_parametric_wind.nc` (216×565×625, ~185 M) |

---

## 2. What changed vs 2026-07-27 design

| Was (hypothesis) | Now (proven) |
|------------------|--------------|
| Milton-ish paths / generic stubs | **Lee dual** on external drive, fixed clocks 2023-09-09 → 09-18 |
| NHC Track.shp required | Optional — golden uses **BEST track + track.richamp** |
| Parametric wind “some nc” | **`lee_parametric_wind.nc`**: wind_u/v, PSFC, 565×625, 216 h |
| fort.22 domain theory | **Verified** Pa (~101000); ~2.2 G — do not pack |
| Compare = “GFS vs param later” | Compare = **generic multi-slot** anything vs anything; Lee is first preset |
| House before run | **Run before house** — fixtures exist |

---

## 3. Parametric scenario file map (house cares)

```text
CASE_P = …/ec95d_lee_param_20230909

Display / pack inputs:
  forecast/fort.14, fort.63.nc, maxele.63.nc
  met_pwm/lee_parametric_wind.nc      ← wind grid
  met_pwm/lee_best_track.trk          ← track source
  met_pwm/track.richamp               ← PWM geometry/time
  met_pwm/RICHAMP_rain.nc             ← optional rain
  run_manifest.json                   ← modes.wind=parametric_nws6
  post_* / graphs + temp JSON         ← offline parity / stations prep

Keep offline only:
  met_pwm/richamp.wnd (~2.2G)
  forecast/fort.22 (~2.2G)
```

GFS twin: `CASE_G=…/ec95d_lee_gfs_20230909` with `post_wind/gfs_wind.nc` (217×157×155), `modes.wind=gfs_nws6_fort22`, no track.

---

## 4. North star — multi-scenario compare + residual stack

**Moonshot (implementation law):**  
The house does not implement “GFS vs parametric.” It implements **N scenario slots + field roles + absolute UTC time + multi-series chart + a recursive residual graph**.  

**Residuals are not optional chrome.** They are first-class sources. Any residual can be an operand of another residual through **at least 4th order**:

| Order | Meaning | Lee example |
|------:|---------|-------------|
| R0 | raw field / obs | ζ_param, ζ_gfs, ζ_obs |
| R1 | first residual X−Y | param−obs, GFS−obs, param−GFS |
| R2 | residual of residuals | (param−obs)−(GFS−obs) error superiority |
| R3 | third-order | R2 anomaly vs window mean, or R2 vs third ref |
| R4 | fourth-order | cross-station / cross-window residual of R3 |

Analog: offline `DiffGrapher` already co-plots Forecast + Diff (+ Tide). House generalizes that into a **composable residual tree** with pedigree labels. Under pure subtraction R2 error-diff ≡ R1 model-model algebraically — **still ship both nodes** (operator language); non-linear ops (abs/norm/skill) make higher orders non-trivial.

GFS vs parametric vs obs for Lee is **one residual preset** on that machinery — not a special code path.

```text
packs.json ──► slots (packs | obs | residual nodes)
                 │
                 ├─ UTC scrub (not shared index)
                 ├─ bind by meta.roles
                 ├─ multi-series chart (R0…R4 + obs)
                 ├─ residual builder (left/right/op → ResidualNode)
                 └─ mesh residual map when fingerprint matches
```

---

## 5. Implement order (revised)

| Phase | Deliverable | Fixture |
|------:|-------------|---------|
| **1** | Export Lee param + Lee GFS fieldpacks; catalog cards | real cases above |
| **2** | Track layer + param wind honesty + default_utc | param pack |
| **3** | **Compare + residual engine** — N slots, UTC, multi-series, **R0–R4 ResidualNode graph**, Lee residual preset | both packs |
| **4** | Mesh residual maps + R3/R4 presets (window/cross-station); abs/norm ops | dual Lee |
| **5** | N packs / export residual fieldpack / stretch | any packs |

Do **not** invent Milton fixtures; use Lee dual.  
Do **not** ship a single “diff” button and call residuals done — **R2–R4 must be real composition**.

---

## 6. Next session start

```text
/init
Read:
  notes/GROK/handoffs/2026-07-28-house-multi-scenario-compare-handoff.md
  notes/GROK/handoffs/2026-07-28-house-multi-scenario-compare-design.md
  notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md

Phase 1: export both Lee fieldpacks from the paths in the inventory.
Stage under CloudVision/threejs-shield-live-viz/data/ and packs.json.
Compare UI only after both packs G-LOAD.
```

---

## 7. Gates (additions)

| Gate | Meaning |
|------|---------|
| G-LEE-PARAM | Param pack: ζ + param wind + track + scenario.met.family=parametric |
| G-LEE-GFS | GFS twin pack: ζ + gfs wind + family=gfs |
| G-COMPARE-STN | Two model series + obs on one station chart |
| G-COMPARE-TIME | Scrub by UTC; series stay aligned within 1 step |
| G-COMPARE-PRESET | Lee preset loads both packs without manual path entry |
| **G-RES-R1** | Build A−obs and B−obs; NaN propagates; chart shows R1 |
| **G-RES-R2** | Residual of two R1s (error superiority); pedigree drawer; Lee preset |
| **G-RES-R3** | Residual involving R2 (structure + unit test; preset optional) |
| **G-RES-R4** | Residual of R3s / cross-window or cross-station structure test |

---

## 8. Anti-patterns

- Building compare UI that only works for GFS↔param  
- Labeling parametric wind “GFS” because var names match  
- Packing richamp.wnd / fort.22  
- Assuming shared time index (216 vs 217)  
- Requiring NHC shapefiles when track.richamp exists  
- Treating ec95d station skill as coastal truth  
- **One A−B “diff” button and stopping** — residuals must compose to R3/R4  
- **Zeroing dry nodes in residual** (NaN must propagate)  
- **Deleting R2 because “it equals R1 algebraically”** under pure sub — keep pedigree  

---

## 9. Open items

- [ ] Export fieldpacks (Phase 1)  
- [ ] wind_parametric adapter vs path override + roles  
- [ ] track_export from best track / track.richamp  
- [ ] Compare + **residual engine** (R0–R4)  
- [ ] G-RES-R1…R4 gates  
- [ ] Wind stride for 185 M basin pack in browser  
- [ ] Optional NHC GIS if re-downloaded later  
- [ ] abs/norm/skill residual ops (non-trivial higher orders)  

---

*Parametric is real. Dual Lee is real. Compare is general. Residuals stack to fourth order. Wire the house to the files that already exist.*
