# Claude prompt — House integration package (totality)

**Use:** copy everything inside the fenced block below into Claude (or equivalent).  
**Save output as:** `notes/GROK/handoffs/YYYY-MM-DD-house-integration-totality-handoff.md` (+ code).  
**Law docs:** `2026-07-28-house-multi-scenario-compare-*` + inventory research.

---

```
You are Claude (or the implementing agent), positioned as the model that can complete
ambitious, long-running technical implementations in one strong push for this dual-suite
weather project.

Your mission is a **totality implementation of the house integration package**:

1. Export real **Lee dual** coastal fieldpacks (parametric + GFS twins).
2. Stage them in the suite live viz catalog.
3. Honest parametric wind + driving track in inspect mode.
4. **Generic multi-scenario compare** (anything vs anything — not a GFS↔param special page).
5. **Recursive residuals through 4th order (R0–R4)** as first-class sources.
6. Verify with the project's harnesses; leave a rich handoff + light driver updates.

You will work in two sibling trees:
- Coastal / postprocess: ~/projects/richamp-support-floodwater
- House shell (Path B):   ~/projects/CloudVision/threejs-shield-live-viz

Lee dual fixtures (external drive — must exist):
- "/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_param_20230909"
- "/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_gfs_20230909"
- Campaign note: ".../adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md"

If the volume is unmounted, stop and report — do not invent synthetic storms.

═══════════════════════════════════════════════════════════════════════════════
IMMEDIATE INSTRUCTIONS (do not skip)
═══════════════════════════════════════════════════════════════════════════════

1. **Internalize before any code.** Read the mandatory list in order. Do not skim.
2. **Fabel-open-ended discipline:** after reading, write (in your working notes / todo)
   an explicit **index** of first-party analogs and "planned vs current" before editing.
   Categories must include at least: fieldpack products, shell surfaces, compare slots,
   residual tree, Lee fixtures, harnesses, invariants.
3. **Quiz yourself** (answer from sources before coding). If you cannot, re-read.
4. **Smallest change that preserves contracts.** One shell, one loader family, one
   fieldpack schema allowlist. No second SPA. No NetCDF in the browser.
5. After each phase: run the verification matrix items for that phase. Evidence over vibes.
6. At end: dated handoff with **Invariants** + **Anti-patterns** sections; light DEV_NOTES.

Quiz (must answer from sources):

Q1. What is display SoT in the house? What must never enter the browser as science arrays?
Q2. Where are the Lee param wind nc and track files, and what shapes/dims does the wind nc have?
Q3. Why must residual R2 "error superiority" still exist as a node if under pure `sub` it
    equals R1 model−model?
Q4. How does the shell scrub time across streams today (index vs timestamp)?
Q5. Name the twelve house invariants from the ORDER 0–11 complete handoff.
Q6. What is G-EXT? What files change when adding a new product?
Q7. What must NOT be packed (richamp.wnd / fort.22) and why?
Q8. What does "anything vs anything" mean for compare implementation (slots vs hardcode)?

═══════════════════════════════════════════════════════════════════════════════
NORTH STAR
═══════════════════════════════════════════════════════════════════════════════

From SOUL_DRIVER (verbatim spirit):

> One system writes the wind and the pressure.
> The other writes the water that hits the coast.

Dual suite: CloudVision (FV3/SHiELD) + richamp-support-floodwater (ADCIRC+SWAN).
This work is the **scientific house** where both sides (and multiple coastal scenarios)
are inspected and compared without Grapher as interactive SoT.

**House integration totality "finished" means a human can:**

1. Open suite live viz; pick **Lee parametric** from the dropdown; scrub real times;
   see ζ, honest parametric wind (not labeled GFS), **driving track on by default**,
   stations + obs; units from meta.
2. Pick **Lee GFS twin**; same mesh/clocks; honest GFS wind labels; no fake track.
3. Enter **Compare mode**; load a **preset** "Lee: parametric vs GFS + obs" without
   typing paths; scrub by **absolute UTC** (not shared index — param 216 vs GFS 217 times).
4. See multi-series station chart: both models + obs.
5. Build / load residual tree:
   - R1: param−obs, GFS−obs, param−GFS
   - R2: (param−obs)−(GFS−obs) error superiority
   - R3/R4: at least structure + one preset path (window anomaly and/or cross-station)
6. Residual **pedigree** visible; NaN dry nodes never become 0 residual.
7. Same machinery works for **any two catalog packs** (and obs) — Lee is the golden
   preset, not a special `if (gfs && parametric)` branch.
8. All gates below pass with commands/screenshots as evidence.
9. Ida atmos pack still loads (G-HOUSE / G-FV3 not regressed).

The mesh residual map, wind stride, and higher residual ops may be incomplete only if
explicitly documented as residual gaps with harnesses still green for required gates.

═══════════════════════════════════════════════════════════════════════════════
MANDATORY READS (strict order)
═══════════════════════════════════════════════════════════════════════════════

**Drivers & law**

1. notes/GROK/SOUL_DRIVER.md
2. notes/GROK/DEV_NOTES.md
3. notes/GROK/handoffs/2026-07-28-house-multi-scenario-compare-handoff.md   ← **integration law**
4. notes/GROK/handoffs/2026-07-28-house-multi-scenario-compare-design.md   ← full design + R0–R4
5. notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md  ← real file map
6. "/Volumes/Pranav's Hard Drive/adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md"

**House already shipped (ORDER 0–11)**

7. notes/GROK/handoffs/2026-07-25-richamp-support-web-orders-complete-handoff.md
   (invariants §7, anti-patterns §8, gates, reproduce commands)
8. post/export/ADCIRC_FIELDPACK_V0.md
9. post/export/cli.py, context.py, pack_writer.py
10. post/export/field_adapters/{base.py,wind_gfs.py,__init__.py,water_fort63.py}
11. CloudVision/threejs-shield-live-viz/{README.md,suite-shell.js,fieldpack-loader.js,
    suite-chart.js,verify-shell.js,verify-fieldpack.js,data/packs.json}

**Analogs for compare / residual**

12. DiffGrapher.py (Forecast + Diff + Tide multi-trace — residual thinking offline)
13. notes/GROK/research/2026-07-27-parametric-wind-pipeline.md (PWM domain / owi2wind schema)
14. notes/GROK/research/2026-07-27-house-scenario-catalog-and-tracks.md (packs.json thin today)

Do **not** re-run ADCIRC or windgfdl. Fixtures exist. Export + shell only.

═══════════════════════════════════════════════════════════════════════════════
FABEL INDEX (produce this before code; keep it updated)
═══════════════════════════════════════════════════════════════════════════════

After reads, materialize an index like:

| ID | Element | First-party location | Planned | Current |
|----|---------|----------------------|---------|---------|
| F1 | fieldpack export mesh+ζ | post/export | Lee both cases | works for GFS-ish cases |
| F2 | wind_gfs adapter | field_adapters/wind_gfs.py | honest GFS twin | exists |
| F3 | wind_parametric | NEW adapter | param nc + family | **missing** |
| F4 | track export | NEW track_export.py | drive_track.json | **missing** |
| F5 | meta.scenario + roles | pack_writer / cli | from run_manifest | partial run_id only |
| F6 | packs.json catalog | data/packs.json | Lee cards + preset | Ida + coast-ec95d only |
| F7 | loadPack single | suite-shell.js | keep | done |
| F8 | track layer | suite-shell | polyline | **missing** |
| F9 | CompareSession N slots | suite-shell | generic | **missing** (1 pack) |
| F10 | SuiteChart multi-trace | suite-chart.js plot([]) | R0–R4 series | **already multi-trace** |
| F11 | ResidualNode graph R0–R4 | NEW pure module + shell | recursive | **missing** |
| F12 | Lee residual preset | packs.json compare_presets | R0–R2 full | **missing** |
| F13 | Harnesses | verify-fieldpack / verify-shell / test-suite-modules | extend gates | baseline ORDER 11 |
| F14 | DiffGrapher analog | DiffGrapher.py | multi-series residual | offline only |

Reference this index in every phase commit message / handoff.

═══════════════════════════════════════════════════════════════════════════════
CURRENT STATE (honest)
═══════════════════════════════════════════════════════════════════════════════

**Solid**
- ORDER 0–11 house: adcirc-fieldpack/v0 + gfdl-fieldpack/v0; suite shell globe↔2D;
  stations, click sample, particles, deep links, quality modes; gates PASS historically.
- Stream-aware time: timestamp match, not index share.
- SuiteChart already accepts multiple traces (model + obs pattern).
- Lee dual ADCIRC campaigns complete; inventory documented.
- owi2wind parametric nc: dims time=216, lat=565, lon=625; vars wind_u, wind_v, PSFC, lon, lat.
- fort.22 pressure Pa verified; do not pack fort.22 / richamp.wnd (~2.2G each).

**Missing (your job)**
- Lee fieldpack exports
- wind_parametric adapter (honest labels; clone wind_gfs pattern)
- track_export → tracks/drive_track.json from track.richamp / lee_best_track.trk
- meta.scenario + meta.roles
- catalog enrichment + compare_presets with residual tree
- track layer in shell
- Compare mode + ResidualNode engine (R0–R4)
- New gates G-LEE-*, G-COMPARE-*, G-RES-R1…R4
- Handoff documenting completion

**Out of scope / do not**
- Second SPA or MapLibre fork
- Reimplement windgfdl; re-run Lee ADCIRC
- Runup
- Silent science decimation
- Roadmap dumps into /run-adcirc skill (thin pointers only if needed)
- Hardcoded `if (gfs && parametric)` compare page

═══════════════════════════════════════════════════════════════════════════════
CORE CONTRACTS (never break)
═══════════════════════════════════════════════════════════════════════════════

From orders-complete handoff + residual design:

1. Fieldpack is display SoT — no NetCDF in browser; no free-painted geometry.
2. NaN = dry / no data — never draw as 0; residual NaN if either side NaN.
3. Coordinates from the run (fort.14 / product grids) — never invent lon/lat.
4. Every field has a time stream; scrub by timestamp, never shared index.
5. Units in meta → colorbar; missing units fail verify.
6. Swath = max over time; rain accum = sum.
7. Wind direction atan2(-v, u) once in shell.
8. Decimation explicit + recorded (stride/subset); quality modes = display LOD only.
9. modes.runup = false (verifier fails if true).
10. Stencils from Reader.py — not reimplemented in JS for science.
11. One shell, one loader, one schema allowlist — **G-EXT: new product = adapter + import line**.
12. Honest met.family — parametric wind never labeled GFS (var names collide with GFS nc).
13. Residuals are sources: SourceRef = pack | obs | residualId; depth ≥ 4; pedigree required.
14. Under pure sub, document R2 error-diff ≡ R1 model-model; **keep both nodes**.
15. Same-mesh residual maps only when mesh fingerprint matches (Lee dual does).
16. Catalog is an index; pack meta wins on conflict after load.

Wind convention string on vectors; pressure_surface naming (not fake PRMSL/MSL).

═══════════════════════════════════════════════════════════════════════════════
LEE FIXTURE PATHS (authoritative)
═══════════════════════════════════════════════════════════════════════════════

CASE_P="/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_param_20230909"
CASE_G="/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_gfs_20230909"
REPO=~/projects/richamp-support-floodwater
VIZ=~/projects/CloudVision/threejs-shield-live-viz

Param pack inputs:
  $CASE_P/forecast/{fort.14,fort.63.nc,maxele.63.nc}
  $CASE_P/met_pwm/lee_parametric_wind.nc
  $CASE_P/met_pwm/lee_best_track.trk
  $CASE_P/met_pwm/track.richamp
  $CASE_P/run_manifest.json
  optional: $CASE_P/met_pwm/RICHAMP_rain.nc

GFS twin inputs:
  $CASE_G/forecast/{fort.14,fort.63.nc,maxele.63.nc}
  $CASE_G/post_wind/gfs_wind.nc
  $CASE_G/run_manifest.json

Shared clocks: coldstart 2023-09-09 00Z → forecast end 2023-09-18 00Z; mesh ec95d.
default_utc hint: 2023-09-16T00:00:00Z (NE impact).

═══════════════════════════════════════════════════════════════════════════════
PLAN TO COMPLETION (dependency order)
═══════════════════════════════════════════════════════════════════════════════

Use todo_write. After each phase, run that phase's gates. Do not start Phase 3
until Phase 1 packs G-LOAD.

### Phase 0 — Index + environment
- Produce Fabel index (table above).
- Confirm external volume + cases + existing verify commands work on current Ida/ec95d if present.
- List adapters via: `PYTHONPATH=. pipenv run python -m post.export.cli --list-products`

### Phase 1 — Export adapters + Lee packs
Implement:
- `post/export/field_adapters/wind_parametric.py` (@register; clone wind_gfs; stream "parametric";
  long_names say parametric/PWM; grid id parametric; path resolve + --path wind_parametric=).
  Prefer field names that roles can map: either param_wind_* OR wind_* with meta.scenario.met.family
  and meta.roles.wind_10m_* — **roles required either way**.
- `post/export/track_export.py` — parse track.richamp and/or ATCF-like best track →
  fieldpack/tracks/drive_track.json + tracks/catalog.json
  (lon, lat, times_utc, optional vmax/mslp; crs EPSG:4326; source path recorded).
- CLI products: wind_parametric, track; wire meta.scenario from run_manifest
  (storm, met.family, modes.wind string, default_utc if present).
- meta.roles at minimum:
  water_surface, water_max, wind_10m_u, wind_10m_v, wind_10m_speed
- Optional rain if easy; not blocking.
- **Do not** ingest richamp.wnd or fort.22 into the pack.
- Size: if browser pack too large for param wind, explicit --wind-stride (or reuse post-stride
  pattern) recorded in meta.fidelity — never silent.

Export both cases to:
  $CASE_P/products/fieldpack
  $CASE_G/products/fieldpack

Verify:
  PYTHONPATH=. pipenv run python -m post.export.verify_pack ...
  node $VIZ/verify-fieldpack.js $CASE_P/products/fieldpack --require-fields water_zeta
  node $VIZ/verify-fieldpack.js $CASE_G/products/fieldpack --require-fields water_zeta

### Phase 2 — Stage catalog + inspect completeness
- Symlink/stage:
  ln -sfn $CASE_P/products/fieldpack $VIZ/data/coast-lee-param
  ln -sfn $CASE_G/products/fieldpack $VIZ/data/coast-lee-gfs
- Enrich data/packs.json: ids, labels, suite, met_family, default_utc, compare_group,
  compare_presets (Lee) + residual tree from design doc.
- Shell: apply default_utc → nearest master-stream index on load.
- Track layer (globe + 2D polyline); **default on** when scenario.met.family=parametric
  or modes.track / tracks present.
- Inventory rail: met family, track ✓/✗, wind family.
- G-LEE-PARAM / G-LEE-GFS via verify-shell extensions or documented manual+node checks.
- G-HOUSE still passes with Ida + a coastal pack.

### Phase 3 — Compare mode + residual engine (totality core)
Implement pure residual module (prefer testable without WebGL), e.g.
  residual-graph.js or suite-residual.js:
  - ResidualNode { id, order, op, left, right, label, pedigree, domain }
  - SourceRef: pack field/role | obs | residualId
  - op v0: "sub" (required); optional stubs for abs_sub later
  - evaluate at station series and (if fingerprint ok) mesh node field at UTC
  - max depth ≥ 4; reject cycles; compute order from tree depth
  - NaN policy: propagate

Shell:
  - Compare mode vs Inspect mode
  - N slots (UI min 2): each binds pack URL or residual or obs
  - Master scrub = UTC; each leaf maps nearest sample
  - Multi-series chart via SuiteChart.plot([...R0, R1, R2, obs...])
  - Build residual UI: left/right/op → node
  - Pedigree in drawer
  - Deep link restores slots + residual tree + t_utc + station
  - Lee preset loads both packs + residual tree R0–R2 (R3/R4 structure ok if preset partial)

Gates:
  G-COMPARE-STN, G-COMPARE-TIME, G-COMPARE-PRESET
  G-RES-R1, G-RES-R2 (full on Lee)
  G-RES-R3, G-RES-R4 (structure + unit tests; one integration path preferred)

### Phase 4 — Mesh residual map + polish
- Mesh fingerprint (node count + hash of coords)
- Residual map layer for R1+ when fingerprints match (Lee dual)
- R3/R4 preset examples: window_mean anomaly; cross-station residual
- Wind residual at stations if roles present
- Screenshots in $VIZ/shots/

### Phase 5 — Close the loop
- Full verification matrix
- Dated handoff: what shipped, gates, residual examples, gaps
- Light notes/GROK/DEV_NOTES.md Next Focus
- Optional thin pointer in suite README for Lee presets
- Do not bloat /run-adcirc skill

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS & GOTCHAS
═══════════════════════════════════════════════════════════════════════════════

- Parametric wind nc **same var names** as GFS — honesty is meta/roles/long_name only.
- BEST track was used for PWM (not OFCL merge with late RMW=0) — export that track.
- No NHC shapefiles on this golden — track.richamp / best trk only.
- Wind grids differ (565×625 vs 157×155) — station residual first; no silent regrid.
- Same fort.14 family on Lee dual → mesh residual OK after fingerprint.
- tempDir trailing slash rules are for generateGraphs offline — export uses --temp-dir clean.
- Reader GFS format for minutes-since-1990 owi2wind files (wind_gfs path already does).
- Docker/windgfdl scars are historical — do not re-enter.
- ec95d station skill is process-grade — still compare; do not claim coastal accuracy.
- Prefer pipenv in REPO for Python; node for VIZ verifies.
- serve.py threading server for large packs.

═══════════════════════════════════════════════════════════════════════════════
VERIFICATION MATRIX (ruthless)
═══════════════════════════════════════════════════════════════════════════════

Export / pack
- [ ] verify_pack exit 0 both Lee packs
- [ ] verify-fieldpack.js PASS both; require water_zeta
- [ ] Param pack meta: scenario.met.family=parametric (or equivalent honest marker);
      modes.wind reflects parametric; track product present
- [ ] GFS pack: family=gfs; no false track requirement
- [ ] No richamp.wnd / fort.22 inside fieldpack tree
- [ ] Units present on all fields

Shell inspect
- [ ] packs.json lists both Lees + Ida
- [ ] Load param: track visible by default; wind not labeled GFS in UI/meta
- [ ] default_utc lands near 2023-09-16 (nearest snap)
- [ ] G-HOUSE: swap atmos ↔ coast without stale layers
- [ ] Existing gates still green where applicable:
      node test-suite-modules.js
      node verify-shell.js --pack ... --gate G-GLOBE --gate G-STN --gate G-CLICK
      --gate G-MULTI --gate G-2D --gate G-OPS --gate G-FINAL --out shots
      (extend verify-shell with new gates rather than "eyeball only")

Compare + residual
- [ ] G-COMPARE-PRESET: one click / deep link loads Lee dual
- [ ] G-COMPARE-TIME: UTC scrub; series align within one step
- [ ] G-COMPARE-STN: ≥2 models + obs traces on SuiteChart
- [ ] G-RES-R1: param−obs and GFS−obs; NaN if dry
- [ ] G-RES-R2: residual of R1s; pedigree shows tree; chart can show R2
- [ ] G-RES-R3: construct residual(R2, …) without crash; order===3
- [ ] G-RES-R4: construct residual(R3, …) without crash; order===4
- [ ] Pure unit tests for residual-graph (no browser) covering composition + NaN + cycle reject
- [ ] Deep link round-trip compare session

Human tester bar
- [ ] Sit down, open Lee preset, scrub NE impact day, explain R1 vs R2 in the drawer
  without opening Grapher
- [ ] Drop a third arbitrary catalog pack into a slot later without code change
  (catalog-only) — compare still works if roles exist

═══════════════════════════════════════════════════════════════════════════════
ANTI-PATTERNS / PROCESS RULES
═══════════════════════════════════════════════════════════════════════════════

- Do not invent lon/lat, storms, or obs.
- Do not label parametric as GFS.
- Do not pack multi-GB drive met.
- Do not share time indices across packs/streams.
- Do not zero dry nodes or dry residuals.
- Do not implement only GFS↔param hardcode.
- Do not ship a single Diff button without R2–R4 composition.
- Do not delete R2 because algebraically equal under pure sub.
- Do not reimplement Reader stencils in JS for science.
- Do not start a second SPA.
- Do not claim pass without harness output.
- Future handoffs **must** include Invariants + Anti-patterns sections.
- Prefer smallest PR-sized commits mentally; totality delivery OK if verified.

═══════════════════════════════════════════════════════════════════════════════
OUTPUT EXPECTATIONS
═══════════════════════════════════════════════════════════════════════════════

1. Working code in REPO post/export + VIZ shell/loader/tests as needed.
2. Both Lee fieldpacks on disk under cases' products/fieldpack + staged in VIZ data/.
3. Extended verify-shell / pure residual tests.
4. Dated handoff:
   notes/GROK/handoffs/YYYY-MM-DD-house-integration-totality-done-handoff.md
   with: one-screen status, what shipped, residual tree example, gate table + evidence,
   open gaps, invariants, anti-patterns, next start.
5. Light update notes/GROK/DEV_NOTES.md Next Focus.
6. Short user-facing summary: how to serve and open the Lee compare preset.

Begin with the mandatory reads and the Fabel index. Then Phase 0–1.
Do not ask permission between phases unless blocked by missing volume or harness failure.
If blocked, report the exact path and gate that failed with command output.
```

---

## Usage note

1. Confirm external drive is mounted (`ec95d_lee_param_20230909` and `ec95d_lee_gfs_20230909` visible).  
2. Paste the fenced prompt into Claude (or run in an agent session with both repos available).  
3. Expect multi-phase work: export → catalog/track → compare+R0–R4 → mesh residual polish → handoff.  
4. Success artifact: dated **done** handoff + green gate table, not just “UI looks good.”

**Suggested output handoff name:**  
`notes/GROK/handoffs/2026-07-28-house-integration-totality-done-handoff.md` (date as completed).

**Law references for the implementer (already inside the prompt):**  
- `2026-07-28-house-multi-scenario-compare-handoff.md`  
- `2026-07-28-house-multi-scenario-compare-design.md`  
- `2026-07-28-parametric-scenario-file-inventory.md`  
