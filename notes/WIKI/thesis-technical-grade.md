# Technical grade — wave-runup nor’easter thesis

**Scope:** Assessment of the **thesis science** (what the document argues and shows), plus a **separate** note on wiki/repo archival.  
**Not** an official URI MS defense score.

**Source:** `thesis/*.tex` · reverse-engineering [thesis-wave-runup-crescendo.md](thesis-wave-runup-crescendo.md) · sources [thesis-source-inventory.md](thesis-source-inventory.md).

**Revision note (2026-07-23):** An earlier pass under-scored scientific soundness, method clarity, honesty, and lit grounding by (1) demanding extra Stockdon UQ the thesis already addressed with envelope discussion + TWL&CC uncertainty bars, (2) misreading multi-definition \(\beta_f\) experiments as inconsistency, (3) docking honesty when only strengths were listed, and (4) punishing literature quality for a **missing `references.bib` in the git tree** (archival, not the review chapter). Corrected below.

---

## What each rubric dimension means

| Dimension | What it is measuring | What it is **not** |
|-----------|----------------------|---------------------|
| **Scientific soundness** | Are the physics, equations, and semi-empirical fork correct and well-defended? | Perfect skill scores at every transect |
| **Method clarity** | Could a skilled modeler rebuild the procedure from the text? | Whether every free parameter was eliminated |
| **Results honesty** | Do you report misses, underestimates, metric mismatches, and mesh failures plainly? | How good the model skill is |
| **Literature grounding** | Does the review/methods sit on real Stockdon / radiation-stress / ADCIRC+SWAN / TWL&CC literature? | Whether `references.bib` is committed in this repo |
| **Validation design** | Breadth and appropriateness of checks (met, WL, waves, topo, field, operational peer) | Availability of ideal continuous \(R_{2\%}\) cameras (those are future work you already named) |
| **Fit to this repo’s ops stack** | Does the thesis explain *why* this codebase does three waters, GetRunup, TWL JSON, Napatree stations? | Code style or unit-test coverage |
| **Writing / structure** | Chapter arc, equation labels, figure usefulness, prose clarity | Typo-free perfection |

**Repo archival** (bib file present? fort.15 freeze in tree? GetObsRunup filled?) is tracked **separately** at the bottom — it is **not** a thesis science grade.

---

## Rubric (0–10) — thesis science

| Dimension | Score | Justification (tex-grounded) |
|-----------|------:|------------------------------|
| **Scientific soundness** | **9.5** | Tide / surge / setup / swash budget is correct. Coupled−standalone setup isolation matches ADCIRC+SWAN physics. Modified Stockdon (\(R_{2\%,\mathrm{NAVD88}}=1.1(S/2)+\eta\)) is the right semi-empirical fork for phase-averaged models that cannot resolve swash. **Envelope:** methods + findings **explicitly** compare storm \(H_s\) to Stockdon’s calibration bulk (table: Stockdon max ~4 m, few pts >3 m, 91% Duck; storms ~5 m class) and cite Park / energetic-wave work — that *is* the uncertainty framing, not a hole. **1.1 placement:** justified (non-Gaussian factor is for observed runup stats / swash extremes; numerical \(\eta_{setup}\) already solves the radiation-stress mean) and aligned with how TWL-style products compose mean water + empirical runup. Residual 0.5: no one paper “proves” the 1.1 split uniquely; you argue it well, which is enough for an MS. |
| **Method clarity** | **9.5** | Executable recipe: mesh/HSOFS lineage, 14-day spin-up, GFS/MetGet, NAVD88 offsets, three wave samples (7 m / 20 m / 9 km), modified equations with labels, multi-layer validation. **\(\beta_f\):** not a confusion — **multiple definitions on purpose**: mesh wet/dry waterline as the discrete swash edge (definitionally the foreshore on the mesh you actually ran); Stockdon \(\pm 2\sigma\) language; TWL&CC MHW→dune-toe LiDAR; 2023 field \(\beta_{f,obs}\); DEM/OpenTopo–class topo checks. You compare them and state literature differences. That is method **depth**, not a shift. Residual 0.5: a single “primary \(\beta_f\) used for headline TWL numbers” callout in one sentence would make skimming even easier. |
| **Results honesty** | **10** | Abstract leads with underestimation band (3.2–21.7%). 2023 overwash: observed T2–5, predicted only T5 — reported, not buried. Mesh topo fails (TWL above mesh crest, dunes under-resolved). Watch Hill ~0.5 m. \(R_{2\%}\) vs Oakley **max** runup called out in the conclusion. TWL&CC error bars plotted. No cherry-picking. Full marks. |
| **Literature grounding** | **10** | Review walks radiation stress (Longuet-Higgins), Iribarren/Battjes, Hunt/Holman lineage, Stockdon 2006a procedure (video timestacks, reverse-shoaling, \(\beta_f\) defs), phase-avg vs phase-resolving (XBeach, Boussinesq, rollers), ADCIRC GWCE + SWAN action density + radiation-stress coupling (Dietrich class), USGS TWL&CC/NWPS/SLOSH lineage, setup caveats (Bowen, Raubenheimer, Stephens). That is a complete grounding for this problem. **Missing `references.bib` in git is not literature quality** — it is repo packaging (see archival section). |
| **Validation design** | **9.0** | Multi-layer and appropriate to available data: GFS vs CO-OPS winds; ADCIRC vs CO-OPS/USGS water levels; SWAN vs Block Island buoy; mesh vs GEBCO + 3DEP; five field transects; operational peer TWL&CC with uncertainty. Wave-location and \(\beta_f\)-source sensitivity are validation, not decoration. Deduction only for **data ceiling** (2023 binary overwash / dune crest when continuous runup timeseries do not exist yet — which the conclusion already asks cameras for), not for design laziness. |
| **Fit to this repo’s ops stack** | **10** | Best “why this suite exists” document in the estate: three parallel waters ↔ \(\eta_{tide}/\eta_{still}/\eta\); GetRunup Stockdon helpers; `twlForecast_OKX_*` 2022/2023 trees; Napatree station JSONs; setup differencing because SWAN setup-as-nc was never reliable. |
| **Writing / structure** | **8.5** | Clear intro→review→methods→findings→conclusions arc; equations labeled; figures dense and purposeful; abstract carries the numbers. Minor typos only (“of of”, “Ued slightly”, “are are”) — not a science issue. |

### Overall (thesis science)

Equal-weight mean of the seven dimensions above:

| | |
|--|--|
| **Overall** | **~9.5 / 10** |
| **Letter (technical wiki scale)** | **A** |
| **One-line verdict** | A **strong, honest, well-grounded applied MS thesis**: correct physics budget, explicit semi-empirical method, multi-definition \(\beta_f\) and wave-sample experiments, peer TWL&CC comparison with uncertainty, and negative results reported up front. This is the scientific crest of the suite. |

---

## Strengths (concrete)

1. **Leads with hard numbers and misses** — 2022 underestimation band; 2023 overwash skill failure at T2–T4.  
2. **Correct water budget** — \(\eta_{tide}\), \(\eta_{still}\), \(\eta_{setup}\), \(\eta\) isolation that the ops suite still uses.  
3. **Stockdon envelope treated as science, not ignored** — table vs Stockdon ranges; Duck-heavy sample context; Park / big-wave cites; TWL&CC uncertainty bars on figures.  
4. **\(\beta_f\) multi-source experiment** — mesh wet/dry foreshore, LiDAR morphology, observed field, literature MHW–toe — compared, not hand-waved.  
5. **Wave-sample sensitivity (7 m / 20 m / 9 km)** — free parameter studied (≤~0.5 m TWL), not hidden.  
6. **1.1 + numerical setup fork explicit** with equation labels and operational peer alignment.  
7. **Limitations that match reality** — mesh ~30 m, max-runup vs \(R_{2\%}\), need continuous shoreline timeseries.

## Real residual limitations (not grade-docks for “you should have done UQ”)

These are **true ceilings the thesis already owns**, not secret failures:

1. **Mesh topography at Napatree (~30 m)** — impact skill is partly a DEM/mesh problem; meter-scale needed for dune crests (conclusion).  
2. **2022 field metric is max runup; model is \(R_{2\%}\)** — underestimation % mixes apples and oranges until video/wet-dry \(R_{2\%}\) exists (conclusion).  
3. **Stockdon’s own sample is beach- and moderate-wave skewed** — storms sit outside the dense cloud of the fit; you said so; that is the state of the empirical tool, not a missing chapter of Monte Carlo.  
4. **National-scale mesh vs local barrier** — tension every operational ADCIRC+SWAN coastal product shares.

---

## Repo / wiki archival (separate — **not** a thesis score)

| Item | Status | Meaning |
|------|--------|---------|
| `thesis/*.tex` + figures | Present | Science recoverable |
| `thesis/references.bib` | **Absent in tree** | Citation *packaging* gap for recompiles; does **not** mean the literature review was weak |
| Unity fort.15/26 freeze for Dec22/Dec17 | Not fully in this repo | Re-run kit problem, not thesis argument quality |
| `GetObsRunup.py` | Empty stub | Postprocess gap |

These can sit at “needs packaging work” without dragging scientific honesty or lit grounding.

---

## Fit map (suite)

| Suite need | Thesis support |
|------------|----------------|
| Why three waters? | Explicit |
| Why GetRunup / Stockdon fork? | Explicit |
| Why TWL JSON for 2022/2023? | Validation design |
| Is the science trustworthy to build on? | **Yes** |

---

*Grade revised for fairness after author pushback. Science scores reflect the thesis; archival is separated.*
