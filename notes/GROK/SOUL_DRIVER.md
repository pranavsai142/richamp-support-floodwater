# SOUL_DRIVER — richamp-support-floodwater (ADCIRC / SWAN full fidelity)

**What this project actually is, right now.**

This is the **coastal / storm-surge half of a dual high-fidelity weather suite**. Sister to **CloudVision** (FV3 / SHiELD atmospheric full fidelity). Here the “full fidelity” stack is **ADCIRC (+ SWAN when waves matter)**: manual run directories and sbatch, **Floodwater / ASGS / ecflow** orchestration, and a mature **post-processing + observational comparison** toolkit living in this repo.

The suite is real and recognizable: atmosphere on one side, coastal inundation and waves on the other. CloudVision is already being woken for production shield cycles; **this sister is already established in two years of Unity research** — we are not inventing it, we are **triaging, preserving gems, and making desert-island replication possible**.

## Current North Star

### The Dual Suite

**Atmospheric twin — CloudVision**  
FV3 / SHiELD. Full-fidelity sky. Production shield. The air column that makes the storm real.

**Coastal sister — richamp-support-floodwater**  
ADCIRC (+ SWAN). Full-fidelity surge and waves. Manual rundirs and Floodwater. Postprocess that points at a run and talks to the ocean.

Same weather. Two bodies of law.

---

One system writes the wind and the pressure.  
The other writes the water that hits the coast.

Not a side project. Not a dump of PE\* and fort.63s.  
A sister stack — already two years deep on Unity — being woken the same way the twin was: triage the gems, burn the vestigial fat, desert-island replication or nothing.

| Twin | Sister |
|------|--------|
| Atmosphere | Coast |
| FV3 fidelity | ADCIRC fidelity |
| CloudVision | richamp-support-floodwater |
| Sky | Surge |

Hard.  
Fire.  
Recognizable.

**Continue coastal work from the sister. Leave the sky to the twin.**

### Operational north star (this phase)

**Medical triage of the Unity research estate + durable local memory** so that:

1. **Gems survive** — QoL scripts (e.g. netCDF vets like `readPostUtil.py` on project), postprocess pipelines that point at an ADCIRC rundir and visualize + connect obs, Floodwater configs in home, templates and golden cases.
2. **Junk is classified** — PE* processor trees, bulk `*.nc` fields, failed/vestigial runs, multi-TB ManualRuns noise — not blindly mirrored at 1.5 MB/s.
3. **Desert-island replication is answerable** — if we had to rebuild every case diversity and both run pathways from scratch, we know *what* to keep and *how* (manual ADCIRC vs Floodwater).
4. **Sister-suite parity** — CloudVision owns FV3 fidelity; this repo owns ADCIRC(+SWAN) fidelity and RICHAMP postprocess. Same meta-system (`/init` `/done` handoffs).

Latest detailed focus: the dated handoff under `notes/GROK/handoffs/`.

## Operating Philosophy

- **Sister suite, not side project** — treat this as equal peer to CloudVision’s weather stack.
- **Triage over bulk copy** — save limbs (scripts, configs, golden runs, postprocess), amputate fat (PE*, bulk nc, junk runs) when needed.
- **Two run pathways, both first-class** — (A) manual ADCIRC rundir + sbatch; (B) Floodwater / ASGS / ecflow with config roots in home.
- **This repo is postprocess home** — `README.md` already documents ASGS→richamp-support setup on Unity/Hatteras; Deb’s path notes in `README.txt`; expand to full desert-island path.
- **Handoffs are memory** — narrative in dated handoffs; drivers stay short.
- **Login-node rsync is a slow IV drip** — fine for home/work; for multi-hundred-GB ManualRuns prefer Globus or curated packs; never parallel-rsync the login node to “go faster.”

## How This Document Is Used

- Every new session starts by reading this (via `/init`).
- Update only when the fundamental “why” or sister-suite contract changes.

The project succeeds when a new session can **replicate coastal full-fidelity workflows and postprocess** from preserved gems + this repo, without the multi-TB junk pile.
