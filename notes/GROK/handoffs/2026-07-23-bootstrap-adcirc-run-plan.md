# Plan summary — Bootstrap → arbitrary ADCIRC(+SWAN) runs

**Goal:** After surgical `--tier bootstrap` archive is on disk, a new session can copy a wired case (or template), point binaries at Unity modules, sbatch spinup then storm, and postprocess with this git repo.

**In scope:** Manual pathway (A) from bootstrap pack; what is already present; what must be set up on Unity each time; how to vary a run.

**Out of scope:** Full Floodwater/ASGS production stand-up (needs t1/t2: ecflow_configs, asgs tree); pulling all deliverables; re-archiving multi-TB field nc.
