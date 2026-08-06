# Research summary: vadcirc (revised goals)

**Date:** 2026-08-06  
**Design/plan/handoff:** `notes/GROK/handoffs/2026-08-06-vadcirc-full-project-*.md`

## Project goal (corrected)

Port **ADCIRC (+SWAN)** to **VRAM** carefully, properly, accurately, efficiently.  
**Not** mesh demos (ricv1), **not** post/fieldpack-first.

## True MVP

Hello-world ADCIRC: **compile + run + identical GPU vs CPU results.**  
Then incremental capability ports under **identity**, then efficiency.

## LA map (still valid)

| Piece | Role |
|-------|------|
| GWCE | ELLPACK `COEF` + `JCG` (ITPACK) + FE assemble |
| Momentum | residual + 2×2 |
| Wet/dry | mask FSM; `NCCHANGE` rebuilds A |
| SWAN | later couple; same identity discipline |

Evidence: `adcirc/src/{gwce.F,itpackv.F,timestep.F,momentum.F,wetdry.F,couple2swan.F}`.

## Strategy

1. Dual backend (CPU twin ≡ CUDA)  
2. Identity gate every slice  
3. Efficiency = residency + bandwidth after identity  
4. SWAN after ADCIRC core identity  
5. Ops/post optional last  

## First implement

**HW0–HW2** hello-world identity only.
