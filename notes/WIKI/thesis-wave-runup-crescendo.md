# Thesis crescendo — Semi-Empirical Prediction of Wave Runup during Nor'easters in New England

**Peak scientific artifact of this suite.**  
Source of truth: `thesis/*.tex` (MS thesis, URI Oceanography — Pranav Sai; committee Ginis, Hara, Pizzo, S. Grilli, A. Grilli, Oakley).  
LaTeX entry: `thesis/runupthesis.tex` · PDF snapshot: `thesis/PranavRevisedThesisAug6.pdf`.  
**`thesis/references.bib` is absent** from the tree; cite keys are inventoried and externally sourced in [thesis-source-inventory.md](thesis-source-inventory.md). Technical grade: [thesis-technical-grade.md](thesis-technical-grade.md) (**~9.5 / A** on thesis science; repo-bib archival scored separately — see revision note there).

**Ops map:** construct runs → [how-to-construct-an-adcirc-run.md](how-to-construct-an-adcirc-run.md) · re-run kit → [adcirc-swan-rerun-kit.md](adcirc-swan-rerun-kit.md) · triage → [what-we-use-and-need.md](what-we-use-and-need.md).

---

## 1. One-sentence science

Predict **extreme wave runup** \(R_{2\%}\) (and TWL relative to **NAVD88**) at **Napatree Point** for the **Dec 2022** and **Dec 2023** nor’easters by combining **numerically modeled setup** (ADCIRC+SWAN) with **empirically modeled swash** (modified Stockdon 2006) in a **semi-empirical** pipeline, then validate against five transect lines (field) and USGS **TWL&CC**. Foreshore slope β_f (also written \(\beta_f\)) is a first-class input (mesh / LiDAR / observed).

---

## 2. Problem and motivation

| Theme | Thesis claim (from intro/abstract) |
|-------|-------------------------------------|
| Hazard | Storms drive coastal change; **surge + wave runup** dominate damage in New England |
| Definition | Runup = max shoreline oscillations from waves; operational statistic is **\(R_{2\%}\)** (2% exceedance of runup maxima) |
| Components | Stillwater (tides + surge) + **setup** + **swash** → TWL |
| Gap | Phase-averaged models (ADCIRC+SWAN) resolve setup via radiation stress, **not** individual-wave swash/runup |
| Contribution | Semi-empirical: keep Stockdon **swash** param; replace empirical **setup** with SWAN-coupled setup; add \(\eta_{still}\) for NAVD88 frame |
| Site | Napatree Point, RI — 1.1 mi barrier spit, dissipative sandy morphology, Oakley et al. storm surveys |

```
η = η_tide + η_surge + η_setup          (eq:etaall)
TWL / R2%_NAVD88 ≈ 1.1·(S/2) + η        (modified form; η = η_setup + η_still)
```

---

## 3. Site and storms

### Napatree Point

- Southwestern tip of Rhode Island; separates Little Narragansett Bay from Block Island Sound.
- Complex nearshore bathymetry (reefs, sandspits); storm-driven morphodynamics (1815 / 1938 hurricanes; fastest-moving RI landform post-1938).
- **Five cross-shore survey transects** (numbered 1–5, east→west / right→left on maps).
- Field program: Oakley et al. RTK-GPS profiles; pre/post nor’easter surveys; overwash visual indicators.

### December 2022 nor’easter (Winter Storm Elliot)

| Quantity | Thesis value |
|----------|--------------|
| Central pressure (min) | 963 mbar |
| RI gusts | 69 mph (111 kph) |
| Block Island buoy \(H_s\) | **6.45 m** |
| Surge (tide gauges) | ~1 m |
| Simulation window | **20–25 Dec 2022** (5-day forecast after 14-day tidal spin-up) |
| Sea-level offset (NAVD88) | **0.113 m** |

### December 2023 nor’easter

| Quantity | Thesis value |
|----------|--------------|
| Central pressure (min) | 981 mbar |
| RI winds | up to 68 mph |
| Block Island buoy \(H_s\) | **8.96 m** (Sandy-class; Sandy cited 9.48 m) |
| Simulation window | **15–20 Dec 2023** |
| Sea-level offset | **0.152 m** |

---

## 4. Physical decomposition (what the three parallel runs are for)

This is the **scientific reason** the operational suite runs three waters in parallel (see ops docs):

| Water product | Physics included | How isolated in thesis |
|---------------|------------------|-------------------------|
| \(\eta_{tide}\) | Tides only | ADCIRC harmonics, no wind |
| \(\eta_{still}\) | Tides + storm surge | Standalone ADCIRC (no wave coupling) |
| \(\eta\) | Tides + surge + **wave setup** | Coupled ADCIRC+SWAN |
| \(\eta_{surge}\) | Wind-driven surge | \(\eta_{still} - \eta_{tide}\) |
| \(\eta_{setup}\) | Wave setup | \(\eta - \eta_{still}\) (**full − stillwater**) |

**Operational note:** SWAN “setup as a separate NetCDF” was never reliable in practice → **parallel runs + differencing** are the method of record for dissecting tides / surge / setup. That design is not an accident; it is the thesis water budget.

---

## 5. Literature spine (review reverse-engineered)

### 5.1 Setup and radiation stress

Cross-shore setup balance (Longuet-Higgins):

\[
\frac{\partial\eta}{\partial x} = -\frac{1}{\rho g h}\frac{\partial S_{xx}}{\partial x}
\]

Historical motivation: ~3 ft water-level difference Narragansett Pier vs Newport in **1938** (Fairchild / setup experiments).

### 5.2 Swash bands and Iribarren

- Incident swash: gravity-wave band (~0.05–0.5? thesis uses f > 0.05 Hz incident; f < 0.05 Hz infragravity — check Stockdon convention).
- Infragravity / surfbeat: group-forced, longer period.
- Iribarren / surf similarity:

\[
\xi_0 = \frac{\beta_f}{\sqrt{H_s / L_0}}
\]

### 5.3 Stockdon et al. (2006a) core formulas

Extreme runup relative to stillwater:

\[
R_{2\%} = 1.1\left(\langle\eta\rangle + \frac{S}{2}\right),\quad S=4\sigma=\sqrt{S_{inc}^2 + S_{ig}^2}
\]

Parameterizations:

| Term | Formula |
|------|---------|
| Setup \(\langle\eta\rangle\) | \(0.35\,\beta_f\,(H_0 L_0)^{1/2}\) |
| Incident swash \(S_{inc}\) | \(0.75\,\beta_f\,(H_0 L_0)^{1/2}\) |
| Infragravity swash \(S_{ig}\) | \(0.06\,(H_0 L_0)^{1/2}\) (no \(\beta_f\)) |
| Combined | \(R_{2\%}=1.1\big(0.35\beta_f(H_0L_0)^{1/2} + \tfrac{1}{2}[H_0L_0(0.563\beta_f^2+0.004)]^{1/2}\big)\) |

Deepwater reverse-shoaling (linear theory): \(L_0 = g T_p^2/(2\pi)\), \(H_0 = H_s\sqrt{c_g/c_{g0}}\).

### 5.4 Why not pure numerical runup

- SWAN is **phase-averaged** (wave-action density); does not resolve bores → shoreline surge.
- Phase-resolving options (FUNWAVE/Boussinesq, SWASH, BOSZ, XBeach rollers) exist but are not the national-scale operational path used here.
- Semi-empirical path matches **USGS TWL&CC** (NWPS/SWAN waves + Stockdon).

---

## 6. Methodology (chapter reverse-engineered)

### 6.1 Model configuration

| Item | Choice |
|------|--------|
| Models | **ADCIRC+SWAN** coupled (padcswan-class) |
| Mesh | HSOFS-adapted, Caribbean→Nova Scotia; RI refined with RIGIS LiDAR / NOAA 30 m DEM (Ullman lineage) |
| Napatree resolution | ~**30 m** (≈4 nodes across ~150 m spit width) |
| Vertical datum | **NAVD88** + sea-level offset |
| Met | **GFS** via **MetGet** |
| Spin-up | 14-day tidal from rest → 5-day storm forecast |
| Output | NetCDF, **30-min** temporal resolution |
| Compute | Unity / MGHPCC |

### 6.2 Wave sampling for Stockdon inputs

Stockdon field waves were at **7–20 m** depth. Thesis evaluates three offshore samples **normal to each transect**:

| Sample | Approx. depth | Rationale |
|--------|---------------|-----------|
| **7 m** | ~7 m | Stockdon lower bound; closest match to TWL&CC \(H_s/T_p\) in practice |
| **20 m** | ~20 m | Stockdon upper bound / documented TWL&CC extraction depth |
| **9 km offshore** | ~**40 m** | Local \(H_s\) maximum; little \(S_{bottom}/S_{breaking}\) |

Wave-location choice changes predicted TWL by **≤ ~0.5 m**.

**Caveat:** Storm \(H_s\) at Napatree (table max ~5 m) **exceeds** Stockdon calibration bulk (avg 1.5 m, max ~4 m) → formula applied outside original envelope.

### 6.3 \(\beta_f\) handling

| Source | Definition |
|--------|------------|
| Thesis mesh procedure | Interpolate mesh elev every 1 m along transect; waterline = most shoreward wet node; slope between waterline and adjacent landward point (timescale-varying) |
| Stockdon classic | Average slope over region \(\pm 2\sigma\) around mean water level |
| TWL&CC | MHW → dune toe from LiDAR beach morphology (post-Sandy 2013 at Napatree) |
| 2023 field | Observed foreshore slope \(\beta_{f,obs}\) (avg ~0.09 vs mesh ~0.05) |

Mesh \(\beta_f\) and TWL&CC slopes often agree; **observed 2023 slopes diverge 14–61%**, especially higher dunes at T1–T2 not in outdated topo.

### 6.4 Modified \(R_{2\%}\) relative to NAVD88 (the fork)

Three successive modifications:

1. **Add stillwater for datum:**  
   \(R_{2\%,\mathrm{NAVD88}} = 1.1(\langle\eta\rangle + S/2) + \eta_{still}\)

2. **Replace empirical setup with SWAN setup:**  
   \(R_{2\%,\mathrm{NAVD88}} = 1.1(\eta_{setup} + S/2) + \eta_{still}\)

3. **Move numerical setup outside the 1.1 factor** (non-Gaussian correction kept on swash only):  
   \[
   R_{2\%,\mathrm{NAVD88}} = 1.1\left(\frac{S}{2}\right) + \eta,\qquad \eta=\eta_{setup}+\eta_{still}
   \]

This is the **headline method** of the thesis.

### 6.5 Validation design

| Layer | Data |
|-------|------|
| Wind | GFS vs CO-OPS Providence / Quonset (+ Newport 2023) |
| Water level | ADCIRC \(\eta,\eta_{still},\eta_{tide}\) vs CO-OPS Providence, Newport, Quonset, New London + USGS **Watch Hill Cove** |
| Waves | SWAN \(H_s,T_p\) vs **NDBC Block Island** (~50 m) |
| Bathymetry | Mesh profiles vs **GEBCO** 15″ DEM |
| Topography | Mesh vs USGS **3DEP** 1 m DEM + beach-morphology LiDAR |
| Runup / impact | Five Oakley transects: **2022 runup elev**; **2023 dune crest + overwash yes/no** |
| Operational peer | USGS **TWL&CC** API/viewer (sites 1401-class / OKX region; two Napatree forecast points) |

---

## 7. Headline results

### 7.1 Forcing skill (qualitative)

- GFS winds: good agreement at CO-OPS (Newport 2023 gap from sensor failure).
- ADCIRC water levels: better at RI CO-OPS; **Watch Hill peak errors ~0.5 m**.
- SWAN waves at Block Island:
  - 2022: pred \(H_s\) max ~7 m vs obs **6.45 m**; \(T_p\) 10–12.5 s vs obs max 11.98 s
  - 2023: pred \(H_s\) max **8.96 m** vs obs **9.47 m**; \(T_p\) 15.32 vs 16.67 s
- Mesh topo: **under-represents dune crests by 1–4 m** vs 1 m DEM / morphology; water-level swaths **overpredict inundation**.

### 7.2 Setup: numerical vs empirical

Numerically differenced \(\eta_{setup}\) is **generally lower** than Stockdon-parameterized setup and TWL&CC setup (consistent with known Stockdon setup high-bias / nearshore asymptotic setup literature: Bowen, Raubenheimer, Stephens).

### 7.3 December 2022 — observed vs predicted runup (abstract)

| Transect | Observed runup (m NAVD88) | Predicted (m) | Underestimation |
|----------|---------------------------|---------------|-----------------|
| 1 | 3.82 | 3.07 | ~20% |
| 2 | 3.37 | 3.26 | ~3% |
| 3 | 3.40 | 3.23 | ~5% |
| 4 | 3.84 | 3.24 | ~16% |
| 5 | 3.11 | 3.01 | ~3% |

**Abstract band: underestimation 3.2–21.7%.**  
Findings (9 km waves): T2/T3/T5 diffs **0.16 / 0.20 / 0.05 m**; T1/T4 **0.82 / 0.63 m**.

### 7.4 December 2023 — overwash skill

| Transect | Obs dune crest (m) | Pred runup (m, abstract) | Overwash observed? | Overwash predicted? |
|----------|--------------------|--------------------------|--------------------|---------------------|
| 1 | 6.04 | 3.19 | No | No |
| 2 | 4.81 | 3.45 | **Yes** | No (−1.36 m) |
| 3 | 4.02 | 3.44 | **Yes** | No (−0.58 m) |
| 4 | 3.92 | 3.46 | **Yes** | No (−0.46 m) |
| 5 | 3.22 | 3.37 | **Yes** | **Yes** (at 20 m / 9 km; 7 m under by 0.22 m) |

**Headline: overwash observed at transects 2–5; predicted only at transect 5.**

### 7.5 Comparison to TWL&CC

- Wave params from TWL&CC align best with SWAN at **7 m**, despite docs saying **20 m** extraction.
- TWL/runup generally within published Stockdon uncertainty bands; 2022 TWL&CC mean water level weaker vs obs/ADCIRC.

---

## 8. Stated limitations (do not sand these off)

1. **Mesh ~30 m vs meter-scale dunes** — wrong crest heights → false overwash on mesh topo; \(\beta_f\) pollution.
2. **Static mesh** — no dune erosion / sandbar migration during storm.
3. **\(R_{2\%}\) vs max observed runup** — 2022 field is closer to **maximum runup**, not a probabilistic \(R_{2\%}\) PDF → expected under-prediction of extremes.
4. **Stockdon envelope** — storm \(H_s\) above calibration bulk.
5. **Outdated LiDAR/morphology** (esp. 2013 post-Sandy) vs 2022–23 reality at Napatree.
6. **Watch Hill / New London** water-level skill weaker than open RI stations.
7. **No continuous shoreline timeseries** (video / wet-dry sensors) for true observed \(R_{2\%}\).

---

## 9. Bridge to this repo (ops cousins — no false equivalence)

| Thesis concept | Repo artifact (cousin / partial) | Relationship |
|----------------|----------------------------------|--------------|
| Modified Stockdon \(R_{2\%}\) | **`GetRunup.py`** (`calculateStockdon*`, `calculateStockdonRunupNoSetup`, ADCIRC-setup + swash variants) | **Direct implementation cousin** — comments discuss setup outside 1.1 and swash-only addition |
| USGS TWL&CC peer forecast | **`twlForecast_OKX_140{1,2,3}_2022-12-20*`** and **`…2023-12-15*`** JSON trees (`waterLevels`, `site`, `forecast`, `region`) | **Same storms / OKX sites** used in thesis comparison |
| TWL fields | `twl`, `setup`, `runup`, `swash`, `incSwash`, `infragSwash`, `hs`, `pp`, `tideWindSetup` | Matches USGS API-style schema in `GetRunup.fetch_water_levels` |
| Five Napatree transects / stations | **`RUNUP_NAPATREE_STATIONS.json`**, `NAPATREE_*_STATIONS.json`, `RUNUP_OFFSHORE_STATIONS.json`, `NAPATREE_DEEP*_STATIONS.json` | Station geometry for graphs / extraction |
| Graphing Napatree runup | **`generateGraphs.py`**, **`Grapher.py`**, `test/Napatree_all_*.png` | Postprocess visualization path |
| Observed runup hook | **`GetObsRunup.py`** (currently empty stub), `RUNUP_OBS_STATIONS.json` | **Intended** obs path; not a complete shipped validator |
| Three-water dissection | ManualRuns Dec22/Dec17-class: tides / stillwater / full (see ops wiki) | **Same physical budget** as \(\eta_{tide}\), \(\eta_{still}\), \(\eta\) |
| Mesh topo limitation | ricv1 / HSOFS-family meshes under Unity; not re-derived here | Explains why postprocess uses high-res DEM cousins where available |

**Honest map:** thesis science is the **why**; `GetRunup` + TWL JSON + station files are the **how this repo operationalizes a sibling pipeline**. Do not claim every thesis figure regenerates from a single CLI without the Unity NetCDF case.

---

## 10. Reading order (ops → crest)

1. [how-to-construct-an-adcirc-run.md](how-to-construct-an-adcirc-run.md) — fort.14/15, NWS, SWAN, Dec22/Dec17  
2. [adcirc-swan-rerun-kit.md](adcirc-swan-rerun-kit.md) — what to archive to re-run; three parallel waters  
3. [what-we-use-and-need.md](what-we-use-and-need.md) — localGenerator vs Floodwater E2E  
4. **This page** — scientific crest (methods, numbers, limitations)  
5. [thesis-source-inventory.md](thesis-source-inventory.md) — cite keys + external pointers  
6. [thesis-technical-grade.md](thesis-technical-grade.md) — structured technical grade  

---

## 11. Chapter map (reverse-engineering index)

| Chapter file | Role | Must-remember content |
|--------------|------|------------------------|
| `abstract.tex` | Numbers + claim | 2022 underest 3.2–21.7%; 2023 overwash 2–5 vs pred only 5 |
| `introduction.tex` | Why + site + storms + ADCIRC+SWAN + Stockdon intent | η components; Napatree history; two nor’easters |
| `review.tex` | Physics + param lit | Setup eq; Iribarren; Stockdon forms; SWAN/ADCIRC equations; reverse-shoaling |
| `methods.tex` | Executable recipe | Mesh, GFS, offsets, 7/20 m / 9 km, modified R2% NAVD88, validation sources |
| `findings.tex` | Evidence | Wind/water/wave skill; slopes; setup comparison; runup timeseries; profiles |
| `conclusion.tex` | Limits + future | Mesh 30 m; R2% vs max; video sensors; nested phase-resolving |
| `acknowledgements.tex` | People | Committee + GSO; not science |
| `runupthesis.tex` | Scaffold | Chapters; `\bibliography{references}` **but no bib file in tree** |

---

*Living wiki. Prefer editing this page over re-paraphrasing the PDF when the science is stable.*
