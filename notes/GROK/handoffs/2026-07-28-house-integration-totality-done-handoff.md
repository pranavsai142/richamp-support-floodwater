# 2026-07-28 — Handoff: house integration totality — DONE

**Status:** the house integration package shipped in one push — Lee dual
fieldpacks, honest parametric inspect (track on by default), **generic
multi-scenario compare**, and a **recursive residual engine through 4th
order**, all behind harness gates.
**Law it implements:** `2026-07-28-house-multi-scenario-compare-handoff.md` +
`…-design.md` (unchanged — this handoff reports completion, not revision).
**Working index:** `2026-07-28-house-integration-totality-worknotes.md`
(Fabel index F1–F14 + quiz answers + fixture facts).

---

## 1. One-screen status

| Item | State |
|------|-------|
| Lee param fieldpack | **Exported** — `$CASE_P/products/fieldpack` (71 MB), verify_pack + verify-fieldpack PASS |
| Lee GFS twin fieldpack | **Exported** — `$CASE_G/products/fieldpack` (46 MB), both verifiers PASS |
| `wind_parametric` adapter | **Shipped** — stream `parametric`, honest PWM long_names, explicit `--wind-stride` |
| `track_export` | **Shipped** — ATCF BEST + `track.richamp` → `tracks/drive_track.json` + `pwm_track.json` (55 fixes each, positions cross-checked) |
| `meta.scenario` / `meta.roles` / `modes.wind` string / `modes.track` | **Shipped** (cli) — family parametric/gfs from run_manifest |
| Catalog + preset | **Shipped** — `data/packs.json` cards + `compare_presets` w/ full R1–R4 residual tree |
| Track layer + default_utc snap + inventory met-family | **Shipped** — G-LEE-PARAM/G-LEE-GFS PASS |
| Compare mode (N slots, UTC master, obs peer) | **Shipped** — G-COMPARE-PRESET/TIME/STN PASS |
| Residual engine R0–R4 (`suite-residual.js`, pure) | **Shipped** — 27/27 unit tests + G-RES-R1…R4 PASS |
| Mesh residual map (fingerprint-gated) | **Shipped** — G-RES-MAP PASS (±0.34 m ζ met-family signal at 09-16 06Z) |
| Regressions | test-suite-modules 20/20 · coast G-GLOBE…G-FINAL · G-FV3 · G-HOUSE (4 packs) all PASS |

Human bar: open `http://127.0.0.1:3412/?preset=lee-met-family` → both Lee packs
load, chart shows param + GFS + obs + R1s + R2 at Newport, scrub is absolute
UTC, drawer explains R1 vs R2, map select paints ζ_param−ζ_GFS on the mesh.
No Grapher, no path typing, no NetCDF in the browser.

---

## 2. What shipped (by tree)

### `richamp-support-floodwater/post/export/`

| File | Change |
|------|--------|
| `field_adapters/wind_parametric.py` | **new** — owi2wind nc (216×565×625) on stream/grid `parametric`; PWM/windgfdl long_names; Pa→mb guard; `--wind-stride N` spatial subsample recorded per field row + fidelity (never silent); registered via one import line (G-EXT) |
| `track_export.py` | **new** — ATCF parser (dedupe radii rows; lat `122N`→12.2; vmax kt, mslp mb, RMW nm) + `track.richamp` parser (heading, vmax m/s, RMW km); −999 → JSON null; refuses insane coords; writes `tracks/` + catalog |
| `pack_writer.py` | `add_tracks()` (allow_nan=False on track JSON) |
| `cli.py` | `track` core product · `--wind-stride` · `--default-utc` · `meta.scenario{storm, met{family,wind_mode,source}, default_utc}` · `meta.roles` (role→field, first-present-wins) · `modes.wind` keeps the manifest string · `modes.track` |
| `ADCIRC_FIELDPACK_V0.md` | layout + meta docs for `tracks/`, `scenario`, `roles`, stride flags |

### `CloudVision/threejs-shield-live-viz/`

| File | Change |
|------|--------|
| `suite-residual.js` | **new pure module** — ResidualNode graph: SourceRef `pack|obs|residual`, ops `sub`/`abs_sub`, computed order (1+max of operands), cycle rejection (self + transitive, incl. node replacement), NaN propagation, UTC-nearest alignment (45-min tolerance, binary search), `window_mean` reduce, per-ref station override, pedigree expressions, `evaluateSeries` + `evaluateField` + `meshCapable` |
| `test-residual.js` | **new** — 27 pure checks: R1→R5 composition, orders, cycles, NaN, unequal clocks (6-vs-7-step miniature of 216-vs-217), window anomaly ≈ 0-mean, cross-station R4 hand-check, pure-sub identity + abs_sub breaking it, mesh-domain eval + obs refusal |
| `suite-shell.js` | track layer (polyline + fixes, default on for parametric) · default_utc snap on load · scenario inventory + meta drawer rows · **compare mode**: N slots, merged-UTC master timeline, obs peer, role binding (`meta.roles`), residual build UI + pedigree drawer, preset load, deep links (`?preset=`, `mode=compare`, `cslots`, `res=<tree>`, `t_utc`, `cstation`, `crole`, `rvis`), mesh residual map (fingerprint-gated, symmetric range, colorbar takeover), test hooks `_compare*` |
| `fieldpack-loader.js` | soft-loads `tracks/` into `pack.getTracks()` |
| `suite-chart.js` | untouched — already multi-trace (the DiffGrapher analog) |
| `index.html` | compare panel (preset/slots/role/map/obs/residual list/build row), `suite-residual.js` script |
| `data/packs.json` | Lee cards (id, storm, met_family, default_utc, compare_group) + `compare_presets.lee-met-family` with residual tree R1_po/R1_go/R1_pg/R2_err/R3_err_anom/R4_cross_stn (stations 83=Newport, 103=New London) |
| `verify-shell.js` | **new gates** G-LEE-PARAM, G-LEE-GFS, G-COMPARE-PRESET (incl. deep-link round trip), G-COMPARE-TIME, G-COMPARE-STN, G-RES-R1…R4, G-RES-MAP; G-HOUSE hardened (layer-contribution pixel diff for legitimately-neutral fields; per-pack shots); browser closed on failure (leak starved later runs) |
| `serve.py` | `request_queue_size=128` + HTTP/1.1 keep-alive — the 5-deep socket backlog dropped one of the (now 8) parallel script loads (`missing: SuiteChart` boot flake) |

---

## 3. The Lee residual tree (live in the preset)

```text
R0: ζ_param (slot A) · ζ_gfs (slot B) · obs (CO-OPS, peer series)
R1_po = param − obs          R1_go = GFS − obs          R1_pg = param − GFS
R2_err = R1_po − R1_go       # error superiority; ≡ R1_pg under pure sub —
                             # kept as its own node, drawer documents the identity
R3_err_anom = R2_err − mean(R2_err)          # window_mean reduce
R4_cross_stn = R3@Newport − R3@NewLondon     # per-ref station override
```

Measured on the golden (station 83, forecast window):
`max |R2_err − R1_pg| = 7.6e-17` over 72 samples (identity, documented in the
pedigree drawer, node **not** deleted); R3 mean ≈ 1e-17 (anomaly law); R4
sample = R3@83 − R3@103 exactly; a fresh 4th-order node composes at runtime
and `R_cycle` self-reference is refused. Wind residual (GFS−param at Newport,
grid-sampled): finite mid-storm, **NaN at 2023-09-18T00** where the 216-step
parametric clock has no sample inside tolerance — the 216-vs-217 law enforced,
never a fake 0.

---

## 4. Gate table (evidence: `$VIZ/shots/`, commands in §5)

| Gate | Result | Evidence |
|------|--------|----------|
| verify_pack (both Lee) | PASS | fort.14 counts match; node coords ≤3.8e-06°; ζ within float16 tol (1.95e-03 m) |
| verify-fieldpack.js (both Lee) | PASS | streams adcirc 72 + parametric 216 / gfs 217; units on all fields; `modes.runup=false` |
| G-LEE-PARAM | PASS | family=parametric; no long_name says GFS; track on by default (55 fixes); default_utc → idx 23 gap 0.00 h; stride 3 explicit |
| G-LEE-GFS | PASS | family=gfs; honest GFS labels; no invented track (inventory ✗); shared coldstart |
| G-COMPARE-PRESET | PASS | one deep link loads both packs; R1×3+R2+R3+R4 orders computed; deep-link round trip restores 7 nodes + UTC + station |
| G-COMPARE-TIME | PASS | UTC scrub; slots resolve 0-min gap; wind role merges 216+217 → 217 UTC steps |
| G-COMPARE-STN | PASS | 2 model series + obs (711 finite) + distinct colors; 18k trace px |
| G-RES-R1 | PASS | hand-checked model−obs sample; NaN across unequal clocks (1 NaN of 217) |
| G-RES-R2 | PASS | order 2; identity ≤7.6e-17 documented; pedigree drawer shows tree; R2 on chart |
| G-RES-R3 | PASS | order 3; anomaly mean ≈ 0; chartable |
| G-RES-R4 | PASS | order 4; cross-station hand-check; runtime composition; cycle rejected |
| G-RES-MAP | PASS | 31 435-node ζ_param−ζ_gfs map, symmetric ±0.34 m, colorbar names the residual, obs-fed node refused |
| test-residual.js | PASS 27/27 | pure: composition/NaN/cycles/window/station/identity/mesh |
| test-suite-modules.js | PASS 20/20 | no regression |
| coast set G-GLOBE/STN/CLICK/MULTI/2D/EXT/OPS/FINAL | PASS | no regression on ec95d GFS 5d |
| G-FV3 | PASS | Ida atmos unregressed |
| G-HOUSE | PASS | all four packs (Ida + 3 coastal) swap live, no stale layers |

No `richamp.wnd` / `fort.22` anywhere under either `products/fieldpack` (find = 0).

---

## 5. Reproduce

```bash
CASE_P="/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_param_20230909"
CASE_G="/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_gfs_20230909"
VIZ=~/projects/CloudVision/threejs-shield-live-viz
cd ~/projects/richamp-support-floodwater

# export (param: honest wind + track + stride; twin: gfs)
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir "$CASE_P/forecast" --mesh "$CASE_P/forecast/fort.14" --case "$CASE_P" \
  --products mesh,water,maxele,wind_parametric,track,stations,obs_water \
  --wind-stride 3 --default-utc 2023-09-16T00:00:00Z \
  --temp-dir "$CASE_P/products/_export_temp" --outdir "$CASE_P/products/fieldpack"
PYTHONPATH=. pipenv run python -m post.export.cli \
  --rundir "$CASE_G/forecast" --mesh "$CASE_G/forecast/fort.14" --case "$CASE_G" \
  --products mesh,water,maxele,wind,stations,obs_water \
  --path wind_gfs="$CASE_G/post_wind/gfs_wind.nc" --default-utc 2023-09-16T00:00:00Z \
  --temp-dir "$CASE_G/products/_export_temp" --outdir "$CASE_G/products/fieldpack"
PYTHONPATH=. pipenv run python -m post.export.verify_pack "$CASE_P/products/fieldpack" \
  --source-check --rundir "$CASE_P/forecast" --mesh "$CASE_P/forecast/fort.14"   # + twin

# stage + serve
ln -sfn "$CASE_P/products/fieldpack" $VIZ/data/coast-lee-param
ln -sfn "$CASE_G/products/fieldpack" $VIZ/data/coast-lee-gfs
cd $VIZ && ./serve.py 3412 &

# gates
node verify-fieldpack.js ./data/coast-lee-param --require-fields water_zeta
node verify-fieldpack.js ./data/coast-lee-gfs --require-fields water_zeta
node test-suite-modules.js && node test-residual.js
node verify-shell.js --pack ./data/coast-lee-param --gate G-LEE-PARAM --out shots
node verify-shell.js --pack ./data/coast-lee-gfs --gate G-LEE-GFS --out shots
node verify-shell.js --gate G-COMPARE-PRESET --gate G-COMPARE-TIME \
  --gate G-COMPARE-STN --gate G-RES-R1 --gate G-RES-R2 --gate G-RES-R3 \
  --gate G-RES-R4 --gate G-RES-MAP --out shots
node verify-shell.js --gate G-HOUSE --out shots

# open
open "http://127.0.0.1:3412/?preset=lee-met-family"
```

---

## 6. Findings worth keeping

1. **The 216-vs-217 mismatch produced the best NaN proof for free.** The GFS
   wind clock has one stamp (09-18 00Z) past the parametric clock's end; a
   wind residual there is NaN by tolerance, mid-storm it is finite. The gate
   pins exactly that sample.
2. **Auto-symmetric ranges make "peak time" the *worst* moment for saturation
   checks.** Jumping to field max shrinks everything else toward the diverging
   midpoint (near-white). G-HOUSE now proves render by hiding the data layer
   and diffing pixels — hue-independent — while keeping the colored-pixel
   number as the headline.
3. **socketserver's backlog of 5 is real.** Eight parallel script loads
   overflowed it intermittently (`ERR_SOCKET_NOT_CONNECTED` → "missing:
   SuiteChart"). `request_queue_size=128` + HTTP/1.1 keep-alive fixed it;
   waitLoaded reloads once as belt-and-braces.
4. **A verify harness that leaks its browser on failure cascades.** The first
   timeout left a SwiftShader render loop running; every later run then also
   timed out. `globalBrowser.close()` on the catch path.
5. **puppeteer serialises NaN → null**, and Node-side global `isFinite(null)`
   is `true`. NaN-ness must be judged in-page (`Number.isFinite`).
6. **RICHAMP_rain.nc on this golden has time=1** (single snapshot) — not a
   usable rate/accum series; rain stayed out of the pack (documented, not
   silent).
7. Lee dual `fort.14` files are **md5-identical**, so the mesh-fingerprint law
   (node count + triangle count + coord hash) is satisfiable exactly, and the
   residual map needs no regrid.

---

## 7. Invariants (all prior ones hold; these are added)

1. Fieldpack is display SoT; NaN = dry, never 0; coordinates from the run;
   per-stream timestamp scrub; units in meta; swath=max/rain=sum; wind dir
   `atan2(-v,u)` once; decimation explicit; `modes.runup=false`; stencils from
   Reader.py; one shell/loader/schema allowlist (orders-complete §7, 1–12).
2. **Honest met.family** — parametric wind is never labeled GFS; var names may
   collide, metadata may not (`scenario.met.family`, stream `parametric`,
   PWM long_names).
3. **Residuals are sources.** SourceRef = pack | obs | residual; order is
   computed from the tree (≥4 supported, soft-warn beyond); cycles hard-fail;
   NaN propagates; alignment is UTC-nearest within tolerance, never index.
4. **R2 error-diff stays a node** even where pure `sub` makes it ≡ R1
   model−model — the pedigree drawer documents the identity; `abs_sub` breaks it.
5. **Same-mesh residual maps only on fingerprint match**; obs-fed or reduce-fed
   nodes are station-series-only and the map select refuses them.
6. **Presets are data** (`compare_presets` in packs.json) — no
   `if (gfs && parametric)` code path anywhere; slots take any catalog pack.
7. **Catalog is an index; pack meta wins** (cards mirror, never override).
8. **Parametric ⇒ driving track on by default**, exported from the same files
   that fed PWM; multi-GB drive met (`richamp.wnd`, `fort.22`) never packs.

## 8. Anti-patterns (earned this session)

- Measuring "is data drawn" by colour saturation at the field's max hour
  (auto-symmetric ranges whiten the basin exactly then).
- Letting a failed harness leak its headless browser (cascading timeouts that
  look like app bugs).
- Judging NaN-ness across the puppeteer boundary (NaN→null; global
  `isFinite(null)===true`).
- Trusting a caller-declared residual order instead of computing it from the
  tree.
- Zeroing a residual where either operand is missing/dry (must stay NaN).
- Deleting R2 "because algebra" — or shipping one diff button and calling
  residuals done.
- Packing 2.2 G drive met because it was next to the nc.
- Silent wind decimation (stride is a CLI flag recorded per field row, or it
  does not happen).

---

## 9. Open gaps (stated plainly)

| Gap | Why | What unblocks |
|-----|-----|---------------|
| Rain product on Lee param | `RICHAMP_rain.nc` has a single time step on this golden | a rain nc with a real time axis; `rain_gfs`-style adapter path then applies |
| `abs_sub` beyond gates / `norm_sub` / `skill` ops | v0 ships `sub` + `abs_sub`; norm/skill were design-v1 | add ops to `SuiteResidual.OPS` + UI op select entries (engine already composes them) |
| Residual export as a derived fieldpack | Phase 5 stretch in the design | a small writer that snapshots `evaluateField` over time |
| Cross-suite (atmos↔coast) compare slots | roles exist only on coastal packs today | give the atmos exporter a `meta.roles` block |
| Wave spatial fields (pre-existing) | padcswan golden untouched this session | unchanged from orders-complete §6 |
| 2D basemap orientation (pre-existing) | unchanged | unchanged |
| Compare mode renders slot A's mesh only | by design for v0 (map = residual or A's field) | split/side-by-side view is a future surface |

## 10. Next start

1. `abs_sub`/`norm_sub`/`skill` ops + a preset showing a non-trivial R3 (the
   identity-breaking case) on the Lee golden.
2. Residual fieldpack export (derived product) for offline archival of an
   error-superiority field.
3. `meta.roles` on the atmos exporter → first cross-suite compare slot.
4. Waves golden (unchanged from orders-complete).

---

*Any pack against any pack against the water that was actually measured —
and the disagreement of disagreements is a first-class citizen, four orders
deep, with its pedigree on the drawer.*
