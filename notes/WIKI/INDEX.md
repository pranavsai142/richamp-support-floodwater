# Project Wiki — Living Documentation

Mental models for the **ADCIRC (+SWAN) full-fidelity** side of the dual weather suite (sister: **CloudVision** / FV3).

## Scientific crescendo (read last — peak of the suite story)

| Page | Topic |
|------|--------|
| **[thesis-wave-runup-crescendo.md](thesis-wave-runup-crescendo.md)** | **★ Scientific crest** — reverse-engineered MS thesis: Napatree runup, Dec 2022/2023 nor’easters, modified Stockdon + ADCIRC+SWAN, headline numbers, limitations, bridge to `GetRunup` / TWL JSON |
| [thesis-source-inventory.md](thesis-source-inventory.md) | Cite-key inventory (139 keys); external DOIs/URLs; missing `references.bib`; claim list |
| [thesis-technical-grade.md](thesis-technical-grade.md) | Structured technical grade (rubric, scores, strengths/weaknesses) — not a defense score |

**Ops → crest path:** construct a run → re-run kit (three waters) → postprocess tools → **thesis crest**.

## Operational pages

| Page | Topic |
|------|--------|
| [sister-suite-and-unity-map.md](sister-suite-and-unity-map.md) | CloudVision ↔ this repo; Unity home/work/project; manual vs Floodwater |
| [project-triage-rubric.md](project-triage-rubric.md) | Medical triage of Unity `/project` — P0–P3, filtered sizes, desert-island kit |
| [unity-project-triage-inventory.md](unity-project-triage-inventory.md) | **Live top-level inventory** — every project root entry, P0–P3, prune sizes, next actions |
| [what-we-use-and-need.md](what-we-use-and-need.md) | **Triage search model** — localGenerator vs richamp_scale_and_subset, side-tool families, wind library, home/work pull advice |
| [adcirc-swan-rerun-kit.md](adcirc-swan-rerun-kit.md) | **Research:** ADCIRC(+SWAN) input/binary matrix, size autopsy, T0/T1/T2 surgical tiers; three-water science |
| [how-to-construct-an-adcirc-run.md](how-to-construct-an-adcirc-run.md) | **Mental model:** fort.14/15, tides, wind/NWS, hotstarts, SWAN chaos, Dec22/Dec17 final boss |
| [parametric-wind-pipeline.md](parametric-wind-pipeline.md) | **NHC parametric / windgfdl:** track → PWM → richamp.wnd → owi2wind; fort.15 565×625 domain; house scenario + track |

**Bootstrap ready-to-run handoff:** `notes/GROK/handoffs/2026-07-23-bootstrap-ready-to-run-handoff.md` (+ design runbook sibling).  
**Parametric wind:** pipeline `2026-07-27-parametric-wind-pipeline.md` · **Lee file inventory** `2026-07-28-parametric-scenario-file-inventory.md` · **house multi-scenario compare (law)** `2026-07-28-house-multi-scenario-compare-*` · dual campaign on external `adcirc-local-smoke/LEE_DUAL_CAMPAIGN.md`.

## Repo root (already established)

- `README.md` — ASGS → richamp-support postprocess setup (Hatteras & Unity)
- `README.txt` — Deb’s Unity notes (`INP.txt`, `sbatch runmu` / `runW`)
- `thesis/*.tex` — source LaTeX for the scientific crest
- `GetRunup.py`, `RUNUP_*_STATIONS.json`, `twlForecast_OKX_*` — operational cousins of the thesis pipeline

## Memory system

- Session memory: `notes/GROK/handoffs/`
- Drivers: `notes/GROK/SOUL_DRIVER.md`, `DEV_NOTES.md`
- Start sessions with `/init` in this repo

---

*Living docs. Update when something would have saved a day.*
