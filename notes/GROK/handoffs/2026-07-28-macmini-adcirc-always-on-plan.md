# Plan — Mac mini always-on `/run-adcirc` host (2026-07-28)

## Intent

Make **pranavs-mac-mini** (Tailscale) the leave-on machine for manual ADCIRC(+SWAN)
runs and RICHAMP postprocess, with the same `/run-adcirc` skill contracts as the M3
laptop. Stage a **curated transfer pack** on the external drive for physical or
rsync transfer to the mini’s SSD.

## Constraints (probed)

1. Mini is **Intel x86_64** (i7-8700B, 12 threads, 64 GB RAM) — **not** Apple Silicon.  
2. Laptop ADCIRC binaries are **arm64** — will not execute on mini → **rebuild**.  
3. Mini system disk ~12 GiB free; **`/Volumes/ssd` ~1.3 TiB free** is the work home.  
4. Mini currently lacks Homebrew, gfortran, MPI, netCDF, Docker, pipenv, ADCIRC, and this repo.  
5. Parametric `windgfdl` is Linux ELF → Docker still required for S3p (later).

## Deliverables

| # | Deliverable |
|---|-------------|
| 1 | Kit on external drive: `…/macmini-adcirc-kit/` (~1.6 GiB) |
| 2 | Bootstrap script: brew + cmake build padcirc/adcprep/padcswan + pipenv + tide_fac |
| 3 | Mesh/template seeds: ricv1, ec95d, v18RunTemplate inputs, ec95d smoke |
| 4 | Secrets: MetGet `setApiKey.sh` |
| 5 | Durable plan + design + done handoff |
| 6 | DEV_NOTES next-focus points at mini bring-up |

## Non-goals (this slice)

- Actually finishing bootstrap *on* the mini (user transfers kit first)  
- Full 32 GiB surgical re-copy (optional second rsync)  
- Continuous ½ h analysis daemon (after first proven smoke)  
- Floodwater/ecflow pathway B as primary

## Success

Agent on mini after kit + bootstrap can run:

`/run-adcirc ec95d latest gfs`

with native x86_64 padcirc, MetGet fort.22, and stripped post graphs — same checklist as laptop.
