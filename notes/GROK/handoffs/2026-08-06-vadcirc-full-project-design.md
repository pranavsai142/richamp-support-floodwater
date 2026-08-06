# Design: **vadcirc** — ADCIRC (+SWAN) carefully onto VRAM

**Date:** 2026-08-06 (revised)  
**Plan:** `2026-08-06-vadcirc-full-project-plan.md`  
**Rule:** Identity first. Efficiency second. Meshes/post/ops last.

---

## 1. Overview / Motivation

### 1.1 What we are building

**vadcirc** is a port of **ADCIRC’s numerical core** (and later **SWAN couple**) so that hydrodynamic (and wave) work runs **in VRAM**, with results that match a CPU reference **identically** at each expansion of scope.

### 1.2 What we are not building (as the MVP)

- A ricv1- or MetGet-shaped product milestone  
- A fieldpack / house viz program  
- A “close enough for coastal skill” tolerance ladder as the first bar  

Those can hang off vadcirc **after** the solver is trustworthy.

### 1.3 Why VRAM

Keep large arrays (η, u, v, COEF, residuals, wet masks, later SWAN spectra) **resident on device** to exploit bandwidth and avoid host thrash — **only valuable if answers stay correct**.

---

## 2. Goals & Non-Goals

### Goals

| ID | Goal |
|----|------|
| G0 | **MVP-HW:** compile + run hello-world ADCIRC; **GPU ≡ CPU** outputs |
| G1 | Expand device coverage **one capability at a time**, each with identity gate |
| G2 | Efficiency: residency, layout, profiled bandwidth/wall — after identity |
| G3 | Path to **padcswan-class** (ADCIRC+SWAN) under same discipline |
| G4 | Keep mainline `padcirc`/`padcswan` builds as external truth/oracle as needed |

### Non-goals (early)

| ID | Non-goal |
|----|----------|
| NG1 | ricv1/science-mesh performance as first milestone |
| NG2 | postprocess, fieldpack, house as first milestone |
| NG3 | Loose ζ tolerances instead of identity for kernel slices |
| NG4 | Speed-first refactors that change numerics silently |

---

## 3. Definition of “identical”

### Preferred (slice-level and early full-run)

**Bit-for-bit** match of:

- elevation field dumps (or fort.63)  
- velocity if enabled  
- station series if present  

between:

1. **Device path** (CUDA/Metal kernels), and  
2. **Host path using the same kernel code compiled for CPU** (or a single-rank deterministic port of the same algorithm),

on fixed fort.14/15, fixed compiler flags, fixed FP model.

### Against mainline padcirc

Also required, but may be a **second gate**:

- Match padcirc on the same hello-world when options are frozen (ILump, ITMAX, CONVCR, single rank if comparing to non-MPI device).  
- If padcirc MPI reductions differ in bit pattern, document: **identity is vs vadcirc-CPU twin first**; **padcirc agreement** is bit-identical when single-rank or within a published exact policy.

**Never:** ship a slice that is “faster” and only “1e-3 m close” without an identity gate for that slice.

---

## 4. True MVP: Hello-world identity (MVP-HW)

### 4.1 Inputs

- Smallest valid ADCIRC mesh + fort.15 that:
  - runs coldstart IHOT=0  
  - advances ≥1 (preferably many) timesteps  
  - writes elevation product (fort.63.nc or raw binary dump for easier bit-diff)  
- May use kit `smoke-seeds/ec95d_run` **only as convenience** — any tiny mesh is fine. Mesh name is not the goal.

### 4.2 Acceptance criteria

- [ ] `vadcirc` (device) **compiles**  
- [ ] `vadcirc --cpu` or `vadcirc_cpu` **compiles** (same numerics, host)  
- [ ] Both run the hello-world case to completion  
- [ ] `cmp` / hash of output fields **equal**  
- [ ] Documented command line in `vadcirc/README.md`  

### 4.3 Out of MVP-HW

Met, hotstart, SWAN, multi-GPU, ops skill, fieldpack.

---

## 5. Incremental port program (after MVP-HW)

Each slice **S_k**:

| Step | Action |
|------|--------|
| 1 | Identify one code region in mainline (`gwce.F` / `itpackv.F` / …) |
| 2 | Port to device (or move more of the already-identical loop onto VRAM) |
| 3 | Re-run hello-world (and growing suite); **identity still holds** |
| 4 | Profile efficiency; optimize without breaking identity |
| 5 | Commit + research note scar if any |

### Suggested capability order (physics, not meshes)

| Slice | Content | Identity surface |
|-------|---------|------------------|
| **HW** | Minimal time loop on device/host twin | full field dump |
| **S1** | ELL SpMV | matvec checksum / full if already full-step |
| **S2** | Entire JCG | fort.63 or ETAS dump |
| **S3** | GWCE RHS assemble | same |
| **S4** | GWCE LHS assemble + rebuild on NCCHANGE | same |
| **S5** | Wet/dry | same — high care |
| **S6** | Momentum residual + 2×2 | same |
| **S7** | Longer RNDAY + netCDF fort.63 path | same |
| **S8** | Minimal met (NWS as needed) | same |
| **S9** | Hotstart read/write | same |
| **S10+** | **SWAN / padcswan couple** on a **minimal** wave case | HS/DIR or couple fields + water identity |

Efficiency KPIs (per green slice): device mem residency, GB/s, wall ratio vs CPU twin, no host full-field copy per step.

---

## 6. Technical architecture

### 6.1 Dual path, one code

```text
                    ┌─ backend=cpu   (reference, bit-stable)
  vadcirc driver ────┤
                    └─ backend=cuda  (VRAM)  [metal later]
         same fort.14/15 → same dumps
```

Prefer **one kernel source** (CUDA compilable with host fallback, or pure C++ with CUDA/HIP ports) so “identical” is meaningful.

### 6.2 Mainline as spec

Read-only reference:

- `timestep.F` order: GWCE → wet/dry → momentum  
- `gwce.F`: ELL `COEF`, `JCG`, `NCCHANGE`  
- `itpackv.F`: matvec + CG  
- `momentum.F`, `wetdry.F`  
- later `couple2swan.F` / SWAN thirdparty  

Do **not** gut `adcirc/build/padcirc` production tree until vadcirc is proven; keep padcirc as external oracle.

### 6.3 Layout (repo)

```text
vadcirc/
  README.md                 # hello-world identity commands
  CMakeLists.txt
  host/                     # I/O, driver, fort.15 subset parser
  numerics/                 # shared CPU/GPU-callable numerics where possible
  device/                   # CUDA (and later Metal)
  cases/hello_world/        # frozen fort.14/15 + expected hashes
  tools/diff_fields.*       # bit compare
  docs/IDENTITY.md          # policy: bit-identical vs padcirc single-rank
```

### 6.4 Efficiency guidelines (after identity)

1. All active fields stay on device for N steps.  
2. Spool to host only at output interval.  
3. ELL layout matches ADCIRC `MNEI` padding first; measure CSR later.  
4. No “optimize” that changes association order without updating golden hashes.  
5. f64 for elevation solve unless an explicit identical f32 path is dual-gated.

---

## 7. User stories

### US-HW

**As** a developer, **I want** one hello-world that compiles and matches CPU≡GPU bit-for-bit, **so** I trust every later port.

**AC:** MVP-HW checklist green.

### US-S

**As** a developer, **I want** each new VRAM region to keep that identity, **so** accuracy never regresses for speed.

**AC:** slice PR includes identity job in CI or documented script.

### US-E

**As** a developer, **I want** residency and bandwidth numbers, **so** VRAM use is justified.

**AC:** after identity, profile note per slice.

### US-SWAN (later)

**As** a developer, **I want** the same discipline for ADCIRC+SWAN, **so** waves are ported carefully too.

**AC:** minimal wave case identity before larger meshes.

---

## 8. PR / implement DAG (identity-centric)

| ID | Title | Gate |
|----|-------|------|
| **HW0** | Scaffold `vadcirc/`, hello case, CPU twin runs | run completes |
| **HW1** | Device backend runs same case | run completes |
| **HW2** | **Identity** CPU twin ↔ device | bit-diff empty |
| **HW3** | Optional: match padcirc single-rank golden | documented |
| **S1** | Device ELL SpMV | identity holds |
| **S2** | Device full JCG | identity |
| **S3** | Device GWCE assemble | identity |
| **S4** | Device wet/dry | identity |
| **S5** | Device momentum | identity |
| **S6** | fort.63.nc path still identical | identity |
| **S7+** | Met, hotstart, … | identity each |
| **W1+** | SWAN couple slices | identity on mini wave case |
| **Ops** (optional late) | larger meshes, skill, fieldpack | not part of MVP |

**First sequential-implement:** **HW0–HW2** only.

---

## 9. Key decisions (revised)

| # | Decision |
|---|----------|
| D1 | MVP = **hello-world compile + run + identical CPU/GPU** |
| D2 | Growth = **port more of ADCIRC(+SWAN) to VRAM** under identity |
| D3 | **Not** mesh/post-first |
| D4 | Efficiency only after identity |
| D5 | padcirc remains production/oracle; vadcirc is the port vehicle |
| D6 | SWAN in long-term scope; after ADCIRC core identity |

---

## 10. Open questions

1. Single-rank padcirc vs multi-rank for golden identity — default **single-rank** for bit stability.  
2. Compiler FP flags for bit-stability (`-ffp-contract=off` etc.).  
3. CUDA vs Metal for first device backend (CUDA preferred if any NVIDIA host; Metal if Ultra-only).  
4. Minimal SWAN couple case choice when W1 starts.

---

## 11. References

- Mainline: `adcirc/src/{gwce.F,itpackv.F,timestep.F,momentum.F,wetdry.F,couple2swan.F}`  
- Plan / handoff: same date prefix in `notes/GROK/handoffs/`  
- Research LA map: `notes/GROK/research/2026-08-06-vadcirc-full-conversion-summary.md` (update: MVP ladder replaced by identity program)

---

## 12. Bottom line

**Done for “first milestone”:** hello-world ADCIRC, GPU and CPU, **identical results**.  
**Done for “project”:** progressive, identity-preserving movement of **ADCIRC then SWAN** into VRAM, efficient because state lives there — not because a coastal post stack was wired.
