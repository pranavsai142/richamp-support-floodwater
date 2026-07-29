# Thesis source inventory — cite keys, claims, external pointers

**Gap:** `thesis/runupthesis.tex` ends with `\bibliographystyle{uriapa}\bibliography{references}` but **`thesis/references.bib` is not in the repository**. This page reconstructs primary sources so the wiki can stand without the PDF bibliography.

**Key count:** 139 unique `\cite{...}` keys across `thesis/*.tex` (extracted 2026-07-23).  
**Policy:** Primary scientific / product sources resolved with DOI or official URL where verifiable. Obscure keys, local photo captions, news, and secondary web pages may be **UNRESOLVED** — silent omission fails audit; explicit UNRESOLVED is success.

Companion: [thesis-wave-runup-crescendo.md](thesis-wave-runup-crescendo.md) · [thesis-technical-grade.md](thesis-technical-grade.md).

---

## 1. Missing bibliography (structural finding)

| Item | Status |
|------|--------|
| `thesis/references.bib` | **ABSENT** |
| `thesis/runupthesis.tex` bibliography hook | Present (`\bibliography{references}`) |
| `\nocite{*}` | Present — would dump full bib if file existed |
| PDF bibliography | May exist inside `PranavRevisedThesisAug6.pdf` / `RevisionHistoryPranavThesis.pdf` only |

---

## 2. Primary scientific sources (resolved or best-effort)

| Cite key(s) | Resolved citation / product | DOI or official URL | Confidence | Notes |
|-------------|----------------------------|---------------------|------------|-------|
| `stockdon` | Stockdon, H.F., Holman, R.A., Howd, P.A., Sallenger, A.H. (2006). Empirical parameterization of setup, swash, and runup. *Coastal Engineering* 53, 573–588. | [10.1016/j.coastaleng.2005.12.005](https://doi.org/10.1016/j.coastaleng.2005.12.005) | **high** | Core \(R_{2\%}\) formula |
| `stockdondata` | Stockdon, H.F. & Holman, R.A. (2011). Observations of wave runup, setup, and swash on natural beaches. USGS Data Series 602. | [10.3133/ds602](https://doi.org/10.3133/ds602) | **high** | Companion dataset to 2006a |
| `stockdon2006swan` | Stockdon, H.F. et al. (2007). A simple model for the spatially-variable coastal response to hurricanes. *Marine Geology* 238, 1–20. | [10.1016/j.margeo.2006.11.004](https://doi.org/10.1016/j.margeo.2006.11.004) | **high** | Delft3D/SWAN + empirical runup for hurricanes |
| `stockdonsetup` | Stockdon, H.F. et al. (2014). Evaluation of wave runup predictions from numerical and parametric models. *Coastal Engineering* 92, 1–11. | [10.1016/j.coastaleng.2014.06.004](https://doi.org/10.1016/j.coastaleng.2014.06.004) | **high** | XBeach/SLOSH+SWAN numerical vs param |
| `holman` | Holman, R.A. & Sallenger, A.H. (1985). Setup and swash on a natural beach. *JGR* 90(C1), 945–953. | [10.1029/JC090iC01p00945](https://doi.org/10.1029/JC090iC01p00945) | **high** | Tide-dependent coeffs |
| `hunt` | Hunt, I.A. (1959). Design of seawalls and breakwaters. *J. Waterways & Harbors Div.* 85(WW3), 123–152. | [10.1061/JWHEAU.0000129](https://doi.org/10.1061/JWHEAU.0000129) | **high** | Linear Iribarren runup |
| `battjessurf` / `battjes` | Battjes, J.A. (1974). Surf similarity. *Proc. 14th ICCE*, ASCE, 466–480. | [10.9753/icce.v14.26](https://doi.org/10.9753/icce.v14.26) | **high** | Iribarren / surf similarity |
| `longuethiggens` | Longuet-Higgins, M.S. & Stewart, R.W. (1964). Radiation stresses in water waves… *Deep-Sea Research* 11, 529–562. | [10.1016/0011-7471(64)90001-4](https://doi.org/10.1016/0011-7471(64)90001-4) | **high** | Radiation stress synthesis |
| `longuetbreaking` | Longuet-Higgins, M.S. & Stewart, R.W. (1962). Radiation stress and mass transport… surf beats. *JFM* 13, 481–504. | [10.1017/S0022112062000877](https://doi.org/10.1017/S0022112062000877) | **high** | Setup / surfbeat under breaking |
| `sallenger` | Sallenger, A.H. (2000). Storm impact scale for barrier islands. *J. Coastal Research* 16(3), 890–895. | [journals.flvc.org/jcr/article/view/80902](https://journals.flvc.org/jcr/article/view/80902) | **high** | Collision/overwash/inundation; no clean Crossref DOI verified |
| `runupreview` | Gomes da Silva, P. et al. (2020). On the prediction of runup, setup and swash on beaches. *Earth-Science Reviews* 204, 103148. | [10.1016/j.earscirev.2020.103148](https://doi.org/10.1016/j.earscirev.2020.103148) | **high** | Major modern runup review |
| `kobayashimaru` | Kobayashi cluster (1989 swash; 1987 NSWE; 1998 probability) — key is multi-paper / joke name | e.g. [10.1029/JC094iC01p00951](https://doi.org/10.1029/JC094iC01p00951) | **med** | **Ambiguous** — do not invent single DOI |
| `park` | Park, H. & Cox, D.T. (2016). Empirical wave run-up formula for wave, storm surge and berm width. *Coastal Engineering* 115, 67–78. | [10.1016/j.coastaleng.2015.10.006](https://doi.org/10.1016/j.coastaleng.2015.10.006) | **high** | High-surge Stockdon improvement |
| `setupvalidation` | Stephens, S.A., Coco, G., Bryan, K.R. (2011). Numerical simulations of wave setup over barred beach profiles… *J. Waterway Port Coastal Ocean Eng.* 137(4). | [10.1061/(ASCE)WW.1943-5460.0000076](https://doi.org/10.1061/(ASCE)WW.1943-5460.0000076) | **high** | Thesis Fig. StephensSetup |
| `bowen` | Bowen, A.J., Inman, D.L., Simmons, V.P. (1968). Wave set-down and set-up. *JGR* 73(8), 2569–2577. | [10.1029/JB073i008p02569](https://doi.org/10.1029/JB073i008p02569) | **high** | Flume residual height at shoreline |
| `raubenheimer` | Raubenheimer, B., Guza, R.T., Elgar, S. (2001). Field observations of wave-driven setdown and setup. *JGR* 106(C3), 4629–4638. | [10.1029/2000JC000572](https://doi.org/10.1029/2000JC000572) | **high** | Setup underprediction near shore |
| `portugal` | Vousdoukas, M.I., Wziatek, D., Almeida, L.P. (2012). Coastal vulnerability assessment based on video wave run-up… *Ocean Dynamics* 62, 123–137. | [10.1007/s10236-011-0480-x](https://doi.org/10.1007/s10236-011-0480-x) | **high** | Direction-aware / Portugal param |
| `guza` | Thornton, E.B. & Guza, R.T. (1983). Transformation of wave height distribution. *JGR* 88(C10), 5925–5938. | [10.1029/JC088iC10p05925](https://doi.org/10.1029/JC088iC10p05925) | **high** | Breaking wave height model |
| `runupbigwaves` | Senechal, N. et al. (2011). Wave runup during extreme storm conditions. *JGR Oceans* 116, C07032. | [10.1029/2010JC006819](https://doi.org/10.1029/2010JC006819) | **high** | Beyond Stockdon calibration |
| `infragravityparameterization` | Gomes da Silva et al. (2018). Infragravity swash parameterization on beaches. *Coastal Engineering* 136, 41–55. | [10.1016/j.coastaleng.2018.02.002](https://doi.org/10.1016/j.coastaleng.2018.02.002) | **high** | IG swash param |
| `incidentswashparameterization` | Gomes da Silva et al. (2019). Wave reflection and saturation… incident swash. *Coastal Engineering* 153, 103540. | [10.1016/j.coastaleng.2019.103540](https://doi.org/10.1016/j.coastaleng.2019.103540) | **high** | Incident-band companion |
| `iribarren` | Iribarren, C.R. & Nogales, C. (1949). Protection des ports… | classic | high | Harbor oscillations / surf similarity namesake |
| `munk` | Munk, W.H. (1949). Surf beats. *Eos / Trans. AGU* | classic | high | Infragravity |
| `adcirc` | Luettich, R.A., Westerink, J.J., Scheffner, N.W. (1992). ADCIRC DRP-92-6; + 2004 theory PDF | [adcirc.org](https://adcirc.org/) · [DTIC ADA261608](https://apps.dtic.mil/sti/pdfs/ADA261608.pdf) | **high** | Model lineage |
| `adcircswanmodel` | Dietrich, J.C. et al. (2011). Modeling hurricane waves and storm surge using integrally-coupled SWAN+ADCIRC. *Coastal Engineering* 58, 45–65. | [10.1016/j.coastaleng.2010.08.001](https://doi.org/10.1016/j.coastaleng.2010.08.001) | **high** | Tight coupling |
| `adcircswanperf` | Dietrich, J.C. et al. (2012). Performance of unstructured-mesh SWAN+ADCIRC. *J. Sci. Comput.* 52, 468–497. | [10.1007/s10915-011-9555-6](https://doi.org/10.1007/s10915-011-9555-6) | **high** | Scalability |
| `adcircmanual` | ADCIRC User’s Manual (v53 living) | [adcirc.org users manual](https://adcirc.org/home/documentation/users-manual-v53/) | **high** | Input file contracts |
| `swan` / `booijswan` | Booij, N., Ris, R.C., Holthuijsen, L.H. (1999). A third-generation wave model for coastal regions… *JGR* 104(C4), 7649–7666. | [10.1029/98JC02622](https://doi.org/10.1029/98JC02622) | **high** | SWAN |
| `swanmanual` | SWAN User Manual, TU Delft | [swanmodel.sourceforge.io](https://swanmodel.sourceforge.io/) | **high** | Physics switches |
| `usgstwl` / `usgstwlapi` / `usgsrunupapi` | USGS Total Water Level and Coastal Change (TWL&CC) forecast + API | [TWL viewer](https://coastal.er.usgs.gov/hurricanes/research/twlviewer/) · [API docs](https://coastal.er.usgs.gov/hurricanes/research/twlviewer/apidocumentation.html) · Stockdon et al. 2023 [10.1038/s43247-023-00817-2](https://doi.org/10.1038/s43247-023-00817-2) | **high** | Operational peer |
| `usgssloshrunup` | USGS national hurricane coastal-change / TWL methods (SLOSH-class surge + Stockdon runup) | Stockdon 2023 DOI above; OFR series e.g. [OFR 2012–1084](https://pubs.usgs.gov/of/2012/1084/) | med–high | Product family |
| `usgssloshatlantic` | Doran et al. (2013). National Assessment… Mid-Atlantic Coast. USGS OFR 2013–1131. | [pubs.usgs.gov/of/2013/1131](https://pubs.usgs.gov/of/2013/1131/) | **high** | Atlantic assessment |
| `usgsbeachslope` | Farris & Weber (2024). Beach foreshore slope East Coast US. USGS data release. | [10.5066/P13FC6SW](https://doi.org/10.5066/P13FC6SW) | **high** | East Coast slopes |
| `beachmorphology` | Doran et al. Lidar-derived Beach Morphology (dune crest/toe/shoreline). USGS data release. | [10.5066/F7GF0S0Z](https://doi.org/10.5066/F7GF0S0Z) | **high** | National morphology product |
| `nwpsncep` | NCEP Nearshore Wave Prediction System (NWPS) | [polar.ncep.noaa.gov/nwps](https://polar.ncep.noaa.gov/nwps/) | **high** | Operational SWAN nest |
| `estofs` / `stofs` | ESTOFS → STOFS surge/tide forecast | [polar.ncep.noaa.gov/estofs](https://polar.ncep.noaa.gov/estofs/) | **high** | Water-level forcing family |
| `nwsgrid` / HSOFS | Hurricane Surge On-Demand Forecast System mesh (`hsofs.14`) | [ADCIRC grids](https://adcirc.org/products/grids/) · wiki param tables | med | No single mesh DOI |
| `metget` | MetGet (Water Institute / Cobell et al.) met retrieval for hydro models | [github.com/waterinstitute/MetGet](https://github.com/waterinstitute/MetGet) | med | No journal DOI confirmed |
| `gfs` | NOAA Global Forecast System | [NCEI GFS](https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast) | **high** | Wind/pressure |
| `coops` | NOAA CO-OPS Tides and Currents | [tidesandcurrents.noaa.gov](https://tidesandcurrents.noaa.gov/) | **high** | Providence, Newport, Quonset, New London |
| `ndbc` | NDBC/CDIP **44097** Block Island, RI | [ndbc.noaa.gov/station_page.php?station=44097](https://www.ndbc.noaa.gov/station_page.php?station=44097) | **high** | \(H_s\), \(T_p\) validation |
| `usgstide` | USGS 411838071513000 Watch Hill Cove Tide Gage | [waterdata.usgs.gov …411838071513000](https://waterdata.usgs.gov/monitoring-location/411838071513000/) | **high** | Near-Napatree WL |
| `3dep` / `whatis3dep` / `3depdocs` / `lidarexplorer` | USGS 3D Elevation Program + LidarExplorer | [3DEP](https://www.usgs.gov/3d-elevation-program) · [LidarExplorer](https://apps.nationalmap.gov/lidar-explorer/) | **high** | 1 m DEM |
| `gebco` | GEBCO gridded bathymetry (versioned; cite year DOI) | [gebco.net](https://www.gebco.net/) | **high** | Offshore bathy check |
| `vdatum` / `vdatumweb` / `vdatumimplement` | NOAA VDatum | [vdatum.noaa.gov](https://vdatum.noaa.gov/) | **high** | Datum transforms |
| `ullman` | Ullman RI mesh refinement collaborator (GSO/CRC reports); no standalone mesh paper found | Shaw et al. 2016 related [10.3390/jmse4040085](https://doi.org/10.3390/jmse4040085) | **low–med** | **UNRESOLVED as sole Ullman paper** |
| `oakley` | Oakley, B.A. (2021). Storm driven migration of the Napatree Barrier… *Geosciences* 11(8), 330. | [10.3390/geosciences11080330](https://doi.org/10.3390/geosciences11080330) | **high** | Core Napatree peer paper |
| `oakley2024` | Intended Oakley 2024 Napatree product | **UNRESOLVED** | — | No clear 2024 journal match this pass |
| `oakleybean` | Bean, E., Oakley, B., Killingbeck, K. Documenting storm impacts… Napatree (conference/abstract) | Semantic Scholar record (no journal DOI) | med | Field 2023 overwash source class |
| `oakleylhts` | Last High-Tide Swash / shoreline proxy (Oakley LHTS usage) | **UNRESOLVED** as distinct product | — | May live inside Oakley 2021 methods |
| `changeuricmc` / `napatreemanagement` | RI CRMC Beach SAMP; Watch Hill Conservancy Napatree management | [crmc.ri.gov/sampbeach](https://www.crmc.ri.gov/sampbeach/index.html) · [watchhillconservancy.org/napatree](https://thewatchhillconservancy.org/napatree/napatree-resources/) | med–high | Policy/management |
| `noaastormsum7dec2022` | WPC Storm Summary **7**, Winter Storm Elliott (Dec 2022 event archive storm24) | [stormsum_7.html](https://www.wpc.ncep.noaa.gov/storm_summaries/2022/storm24/stormsum_7.html) | **high** | Summary number, not calendar date |
| `noaastormsum4dec2022` | WPC Storm Summary **4**, same Elliott event | [stormsum_4.html](https://www.wpc.ncep.noaa.gov/storm_summaries/2022/storm24/stormsum_4.html) | **high** | |
| `noaastormsum2dec2023` | WPC Storm Summary **2**, Dec 2023 coastal low (storm28) | [stormsum_2.html](https://www.wpc.ncep.noaa.gov/storm_summaries/2023/storm28/stormsum_2.html) | **high** | |
| `grilli` / `grilli1989` / `grilli2001` / `grillibreaking` | S. Grilli et al. Boussinesq / breaking / FUNWAVE lineage | multiple DOIs | high | Committee expertise |
| `xbeachdiss` / `xbeachprediction` / `xbeachprediction2` / `xbeachcoastalhazard` | XBeach model papers (Roelvink et al.; dissipation & runup) | coastal-engineering literature | high | Phase-avg runup competitor |
| `svendsen` / `surfaceroller` | Svendsen surface-roller theory | classic coastal eng | high | |
| `boussinesq` / `peregrine` / `nwogu` | Boussinesq model lineage | classics | high | |
| `slosh` | NOAA SLOSH | [nhc.noaa.gov/surge](https://www.nhc.noaa.gov/surge/) | high | |
| `swashrunup` / `boszrunup` | SWASH / BOSZ phase-resolving runup studies | literature | med | |
| `ferc2022` | FERC / grid outage impacts from winter storm | ferc.gov | med | Socioeconomic |
| `ecori` | ecoRI News beach restoration costs | ecori.org | low–med | Journalism |
| `rihs38` / `rimonthly` / `westerlysun` | RI historical society / monthly / newspapers — 1938 narrative | local archives | med | Historical anecdote class |
| `scijinks` | NASA SciJinks nor’easter education page | scijinks.gov | low | Pedagogy |
| `runupwiki` / `stillwiki` / `swashwiki` / `surfbeatwiki` / `shallowwiki` / `swashmetawiki` | Wikipedia / CoastalWiki class | wiki | low | Conceptual only |

---

## 3. Full key list (139) — resolution status

Keys extracted from tex; status is coarse: **R** = resolved above or clearly mapable product; **U** = unresolved / needs PDF bib or local archive.

```
3dep R | 3depdocs R | adcirc R | adcircmanual R | adcircswanmodel R | adcircswanperf R
armycorps U | austrailianerror U | battjes R | battjessurf R | beachmorphology R
booijswan R | boszrunup U | boussinesq R | bowen R | changeuricmc U
coastpilot U | coops R | datumcomparison U | datumimplementation U | ecori U
estofs R | eurotop U | fairchild U | femaovertop U | femasetup U | ferc2022 U
gebco R | gfs R | grilli R | grilli1989 R | grilli2001 R | grillibreaking R
guza R | holman R | hunt R | incidentswashparameterization U
infragravity U | infragravityparameterization U | iribarren R | jerseymhw U
kobayashi U | kobayashimaru U | lidar2021 R | lidarexplorer R | lidarsandy R
longuetbreaking U | longuethiggens R | metget U | mhwcrmc U | mhwinvention U
mississippimsw U | moretti U | motivdatum U | munk R | napatree1936photo U
napatreeforeword U | napatreegeography U | napatreeheadphoto U | napatreelagoon U
napatreelagoonphoto U | napatreemanagement U | napatreeoffshorephoto U
napatreestartusgs U | napatreestorm U | navier R | ndbc R | netherlandsrunup U
noaachart R | noaastormsum2dec2023 R | noaastormsum4dec2022 R | noaastormsum7dec2022 R
nwogu R | nwpsncep R | nwsgrid R | oakley U | oakley2024 U | oakleybean U
oakleylagoon U | oakleylhts U | park U | perchedrunup U | peregrine R
polishoperationalrunup U | portugal U | raubenheimer R | rihs38 U | rimonthly U
runupbigwaves U | runupcamera1 U | runupcamera2 U | runupcanada U | runupitaly U
runupreview U | runuprocky U | runupwiki R | sallenger R | scijinks R
sealevelrisebarriers U | setupvalidation U | shallowwiki R | shockbouss U
slosh R | smitshock U | stillwiki R | stockdon R | stockdon2006swan U
stockdondata U | stockdonsetup U | stofs R | stokes R | surfaceroller U
surfbeatwiki R | svendsen U | swan R | swanmanual R | swashmetawiki R
swashrunup U | swashwiki R | twlerror U | ullman U | usaceshoreline U
usgsbeachslope R | usgsrunupapi R | usgssloshatlantic U | usgssloshrunup R
usgstide R | usgstwl R | usgstwlapi R | vdatum R | vdatumimplement R
vdatumweb R | wdym U | westerlysun U | whatis3dep R | xbeachcoastalhazard U
xbeachdiss U | xbeachprediction U | xbeachprediction2 U
```

**Rough tallies:** ~55–65 high/med-resolved product or classic DOI class; remaining historical photos, local reports, secondary papers, and wiki/news marked U pending PDF bibliography recovery.

---

## 4. Factual claim inventory (primary science — not anecdotes)

| # | Claim | Where | External anchor |
|---|-------|-------|-----------------|
| C1 | \(R_{2\%}=1.1(\langle\eta\rangle+S/2)\) with Stockdon setup/swash params | review, methods | stockdon DOI |
| C2 | Semi-empirical: numerical setup + empirical swash | abstract, methods | thesis method; USGS TWL&CC peer |
| C3 | Modified form \(R_{2\%,NAVD88}=1.1(S/2)+\eta\) | methods eqs | derived; literature support claimed via usgssloshrunup |
| C4 | Setup isolated by coupled − standalone ADCIRC | methods | adcircswanmodel physics |
| C5 | Wave samples at 7 m, 20 m, 9 km | methods, findings | Stockdon 7–20 m field depths |
| C6 | Mesh ~30 m at Napatree; ~4 nodes across spit | methods, conclusion | mesh geometry claim |
| C7 | 2022 obs runup 3.82/3.37/3.4/3.84/3.11 m; pred 3.07/3.26/3.23/3.24/3.01 m; underest 3.2–21.7% | abstract | field oakley* |
| C8 | 2023 dune 6.04/4.81/4.02/3.92/3.22 m; overwash obs T2–5, pred only T5 | abstract | oakleybean |
| C9 | Block Island \(H_s\) 6.45 m (2022), ~9 m class (2023) | intro, findings | ndbc |
| C10 | Numerical setup generally lower than Stockdon setup | findings | stockdon + setupvalidation class |
| C11 | R2% may understate max observed runup | conclusion | definitional honesty |
| C12 | Sea-level offsets 0.113 m (2022), 0.152 m (2023) | methods | coops / VDatum class |
| C13 | GFS via MetGet drives winds | methods | gfs, metget |
| C14 | TWL&CC uses NWPS/SWAN + Stockdon; MHW–dune-toe slope | methods | usgs* keys |

---

## 5. Spot-check protocol (for verifiers)

Pick 5 random keys from `review.tex` / `methods.tex` and confirm each appears in §2 or §3 with R or U — **not silently missing**. Example set:

1. `stockdon` → R (DOI)  
2. `adcircswanmodel` → R (Dietrich 2011 DOI)  
3. `usgstwlapi` → R (USGS product)  
4. `setupvalidation` → U (named Stephens 2011; no DOI recovered)  
5. `ullman` → U (mesh refinement attribution)

Log: see implementer scratch `cite_spotcheck.md`.

---

## 6. How to restore a real `.bib` later (non-goal now)

1. Extract bibliography pages from `PranavRevisedThesisAug6.pdf` if present.  
2. Or recover from Overleaf / committee PDF / URI thesis archive.  
3. Map keys 1:1; prefer DOI-bearing entries for stockdon/adcircswan/usgs products first.

---

*Inventory is durable wiki memory, not a substitute for a peer-reviewed reference list.*
