#!/usr/bin/env bash
# unity-pull-surgical-gems.sh
#
# Size-bounded desert-island pack for ADCIRC(+SWAN) re-run + Floodwater stand-up.
# Research-backed (2026-07-23): whole ManualRuns soft-exclude FAILS (488–664 GiB residual).
# Strategy = TIERED ALLOWLIST, not "almost everything minus PE*".
#
# Tiers (default = bootstrap):
#   bootstrap  ~8–12 GiB  — MINIMUM functioning coastal system:
#                           binaries (padcirc/padcswan/adcprep), BOTH meshes (v18+ricv1),
#                           templates, v18RunTemplate + v18SandyRun + DebV18Run,
#                           Floodwater configs, work wind seed. No bulk deliverables.
#   t0         ~5–7 GiB   — binaries + floodwater + templates/meshes only (no full scenario)
#   t1         ~20–26 GiB — bootstrap-ish + ecflow_configs + full wind libs + all allowlist scenarios
#   t2         <50 GiB    — t1 + stripped asgs + thesis inputs + side tools
#   deliverables ~25–35 GiB — FINAL RICHAMP/graphs only (layer C). Raw field nc excluded so
#                           these cannot be regenerated without re-running. Prefer
#                           work/.../out + post_output + case graphs; full RICHAMP* packs
#                           are ~42G alone — use --only for specific packs if needed.
#
# Measured 2026-07-23 (Unity, filtered):
#   binaries ~39M | meshes 613M (englandv18+ricv1+navd88) | Ricv1Meshes 313M
#   templates w/ fort.221/222 stripped ~few hundred MB each (FloodwaterRunTemplate was 2.9G unfiltered)
#   v18RunTemplate 0.71G | v18SandyRun 4.2G | DebV18Run 2.5G (re-run filter)
#   work wind 1.5G | project scenario_files 5.6G | work out 23G | post_output 3.2G
#   project RICHAMP* packs 42G total | ScenarioRuns RICHAMP+graphs ~4G
#
# NEVER: ecflow_output, PE*, raw fort.63/64 field dumps, ScratchCopy mega, work v18Runs
#
# Usage:
#   ./unity-pull-surgical-gems.sh DEST --tier bootstrap
#   ./unity-pull-surgical-gems.sh DEST --tier t0|t1|t2|deliverables
#   ./unity-pull-surgical-gems.sh DEST --only project-binaries,home-floodwater
#   ./unity-pull-surgical-gems.sh DEST --dry-run
#
# Layout: DEST/unity-archive/surgical/{home,work,project}/

set -euo pipefail

# Remote host must be supplied by operator env; no cluster hostname is stored in-repo.
REMOTE_USER_HOST="${UNITY_HOST:-}"
if [[ -z "$REMOTE_USER_HOST" ]]; then
  echo "UNITY_HOST is unset. This archive tool is offline unless you set UNITY_HOST yourself." >&2
  echo "Day-to-day work uses the volume archive under unity-archive/ (bootstrap / t1), not a remote login." >&2
  exit 1
fi
ARCHIVE_NAME="unity-archive"
SURGICAL_NAME="surgical"
RP="/project/pi_iginis_uri_edu/pranav_sai_uri_edu"
RH="/home/pranav_sai_uri_edu"
RW="/work/pi_iginis_uri_edu/pranav_sai_uri_edu"

if [[ -x /opt/homebrew/bin/rsync ]]; then
  RSYNC=/opt/homebrew/bin/rsync
elif [[ -x /usr/local/bin/rsync ]]; then
  RSYNC=/usr/local/bin/rsync
else
  RSYNC=$(command -v rsync)
fi

SSH_OPTS=(
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=120
  -o TCPKeepAlive=yes
  -o Compression=no
  -o ControlMaster=auto
  -o ControlPath="${HOME}/.ssh/cm-%r@%h:%p"
  -o ControlPersist=4h
)

DEST_ROOT=""
DRY_RUN=0
ONLY=""
TIER="bootstrap"

usage() {
  sed -n '2,32p' "$0" | sed 's/^# \?//'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --only) ONLY="${2:-}"; shift 2 ;;
    --tier) TIER="${2:-t1}"; shift 2 ;;
    -h|--help) usage ;;
    -*)
      echo "Unknown flag: $1" >&2
      usage
      ;;
    *)
      if [[ -z "$DEST_ROOT" ]]; then DEST_ROOT="$1"; else usage; fi
      shift
      ;;
  esac
done

[[ -n "$DEST_ROOT" ]] || { echo "ERROR: pass DEST drive path" >&2; usage; }
DEST_ROOT="${DEST_ROOT%/}"
[[ -d "$DEST_ROOT" ]] || { echo "ERROR: DEST missing: $DEST_ROOT" >&2; exit 1; }

case "$TIER" in
  bootstrap|t0|t1|t2|deliverables) ;;
  *) echo "ERROR: --tier must be bootstrap|t0|t1|t2|deliverables" >&2; exit 1 ;;
esac

ARCHIVE_ROOT="${DEST_ROOT}/${ARCHIVE_NAME}"
SURGICAL_ROOT="${ARCHIVE_ROOT}/${SURGICAL_NAME}"
LOG_DIR="${ARCHIVE_ROOT}/logs"
MANIFEST_DIR="${ARCHIVE_ROOT}/manifests/surgical"
mkdir -p "$SURGICAL_ROOT" "$LOG_DIR" "$MANIFEST_DIR"

STAMP=$(date +%Y%m%d-%H%M%S)
MASTER_LOG="${LOG_DIR}/surgical-${STAMP}.log"
STATUS_FILE="${MANIFEST_DIR}/status.txt"

log() { echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*" | tee -a "$MASTER_LOG"; }

# Tier membership when --only is empty
tier_allows() {
  local pack="$1"
  # Explicit --only always wins
  if [[ -n "$ONLY" ]]; then
    local IFS=','
    for tok in $ONLY; do
      [[ "$tok" == "$pack" ]] && return 0
    done
    return 1
  fi
  # Packs tagged with min tier via case
  case "$pack" in
    # --- core always (t0 + bootstrap + t1 + t2) ---
    project-binaries|project-buildinfo|\
    home-floodwater|project-floodwater|\
    home-asgs-files|home-scripts|home-confs|\
    project-meshes|project-ricv1-meshes|\
    project-templates|project-manual-meshes|project-manual-readme|\
    project-qol)
      [[ "$TIER" == "deliverables" ]] && return 1
      return 0
      ;;
    # --- bootstrap: v18 wired cases + work wind only (functioning system) ---
    project-scenario-v18RunTemplate|project-scenario-v18SandyRun|project-scenario-DebV18Run|\
    work-scenario-wind)
      [[ "$TIER" == "t0" || "$TIER" == "deliverables" ]] && return 1
      return 0
      ;;
    # --- t1+: full wind lib + all allowlisted scenarios + ecflow ---
    home-ecflow-configs|\
    project-scenario-files|\
    project-scenario-*|project-named-run-*|\
    project-build-intel-slim)
      if [[ "$TIER" == "t0" || "$TIER" == "bootstrap" || "$TIER" == "deliverables" ]]; then
        # bootstrap already matched specific v18 scenarios above
        case "$pack" in
          project-scenario-v18RunTemplate|project-scenario-v18SandyRun|project-scenario-DebV18Run|work-scenario-wind)
            return 0 ;;
        esac
        return 1
      fi
      return 0
      ;;
    # --- T2: ASGS stand-up + thesis + side tools + backup build ---
    home-asgs|home-parametric-wind|home-funwave|home-richamp-unity|\
    project-thesis-*|project-build-cg)
      [[ "$TIER" == "t2" ]] || return 1
      return 0
      ;;
    # --- deliverables: final RICHAMP products + graphs ---
    # Prefer out + post_output + per-case graphs (~30G). Full RICHAMP* packs (~42G)
    # only when tier=deliverables with project-richamp-packs (optional bulk).
    work-scenario-out|project-post-output|\
    project-deliverable-*|project-named-deliverable-*)
      [[ "$TIER" == "deliverables" || "$TIER" == "t2" ]] || return 1
      return 0
      ;;
    project-richamp-packs)
      # 42G total — only explicit deliverables tier (not auto on t2)
      [[ "$TIER" == "deliverables" ]] || return 1
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

should_run() {
  tier_allows "$1"
}

# Rundir re-run kit: keep control/mesh/scripts; drop products + bulk met grids
# fort.221/222 live in wind LIBRARY once, not N copies in every rundir.
# Also drops RICHAMP_* here — those come via --tier deliverables (layer C).
RERUN_EXCLUDES=(
  --exclude 'PE*/'
  --exclude 'pe*/'
  --exclude '*.nc'
  --exclude 'fort.63*'
  --exclude 'fort.64*'
  --exclude 'fort.73*'
  --exclude 'fort.74*'
  --exclude 'fort.80*'
  --exclude 'fort.221*'
  --exclude 'fort.222*'
  --exclude '*.wnd'
  --exclude '*.pre'
  --exclude 'swan_HS*'
  --exclude 'swan_DIR*'
  --exclude 'swan_TMM*'
  --exclude 'swan_TPS*'
  --exclude 'rads.64*'
  --exclude 'maxele*'
  --exclude 'maxwvel*'
  --exclude 'minpr*'
  --exclude 'maxrs*'
  --exclude 'RICHAMP_*'
  --exclude 'graphs/'
  --exclude '*_data_file.json'
  --exclude 'temp/'
  --exclude 'post_temp/'
  --exclude '**/__pycache__/'
  --exclude '**/*.o'
  --exclude '**/*.mod'
  --exclude '**/.DS_Store'
)

# Layer C: final postprocess only — no PE*, no raw field fort.63/swan dumps.
# KEEP RICHAMP_*.nc (subset products), graphs, Track, inundation plots.
DELIVERABLE_EXCLUDES=(
  --exclude 'PE*/'
  --exclude 'pe*/'
  --exclude 'fort.63*'
  --exclude 'fort.64*'
  --exclude 'fort.73*'
  --exclude 'fort.74*'
  --exclude 'fort.80*'
  --exclude 'fort.67*'
  --exclude 'fort.68*'
  --exclude 'swan_HS*'
  --exclude 'swan_DIR*'
  --exclude 'swan_TMM*'
  --exclude 'swan_TPS*'
  --exclude 'rads.64*'
  --exclude 'maxele*'
  --exclude 'maxwvel*'
  --exclude 'minpr*'
  --exclude 'maxrs*'
  --exclude 'fort.221*'
  --exclude 'fort.222*'
  --exclude '*_data_file.json'
  --exclude '**/__pycache__/'
  --exclude '**/.DS_Store'
)

# When pulling deliverables from a rundir tree, include only product-like paths
DELIVERABLE_INCLUDES=(
  --include '*/'
  --include 'RICHAMP_*'
  --include 'graphs/***'
  --include 'Track.*'
  --include '*max_inundation*'
  --include 'uri_post*'
  --include 'properties/***'
  --exclude '*'
)

# Allowlisted ScenarioRuns (diversity without ScratchCopy mega-trees)
# Bootstrap uses only v18RunTemplate + v18SandyRun + DebV18Run
SCENARIO_ALLOWLIST=(
  v18RunTemplate
  v18SandyRun
  DebV18Run
  SandyManualRun
  SandyClosedManualRun
  1938ManualRun
  1938ClosedManualRun
  RamManualRun6
  ParametricDebbyManualRun
  FloodwaterRunTemplate
  SeaLevelRunTemplate
  ClosedBarrierRunTemplate
)

# Named top-level ManualRuns (outside ScenarioRuns) — same diversity
NAMED_RUNS_ALLOWLIST=(
  SandyManualRun
  1938ManualRun
  1938_Deb
  1938_Floodwater
  DebRICV1Sample
  RamManualRun
  RamManualRunWaves
)

rsync_path() {
  local name="$1"
  local rpath="$2"
  local lpath="$3"
  shift 3

  if ! should_run "$name"; then
    log "SKIP $name (tier=$TIER only=${ONLY:-all})"
    return 0
  fi

  mkdir -p "$lpath"
  local dir_log="${LOG_DIR}/surgical-${name}-${STAMP}.log"
  log "START $name"
  log "  remote: ${REMOTE_USER_HOST}:${rpath}"
  log "  local:  ${lpath}"

  local args=(
    -a
    --partial
    --partial-dir=.rsync-partial
    -e "ssh ${SSH_OPTS[*]}"
    -h
    --info=progress2
    --stats
    --human-readable
  )
  [[ "$DRY_RUN" -eq 1 ]] && args+=(--dry-run)
  args+=("$@")

  set +e
  "$RSYNC" "${args[@]}" \
    "${REMOTE_USER_HOST}:${rpath}/" \
    "${lpath}/" \
    2>&1 | tee -a "$dir_log" | tee -a "$MASTER_LOG"
  local rc=${PIPESTATUS[0]}
  set -e

  if [[ $rc -eq 0 ]]; then
    log "OK $name"
    echo "ok $name $(date -Iseconds)" >> "$STATUS_FILE"
    if [[ "$DRY_RUN" -eq 0 ]]; then
      du -sh "$lpath" > "${MANIFEST_DIR}/${name}.local-size.txt" 2>/dev/null || true
    fi
  else
    log "FAIL $name rc=$rc (re-run same command to resume)"
    echo "fail $name rc=$rc $(date -Iseconds)" >> "$STATUS_FILE"
    return "$rc"
  fi
}

# rsync individual files into a directory
rsync_files_into() {
  local name="$1"
  local lpath="$2"
  shift 2
  # remaining: remote file paths (absolute on Unity)

  if ! should_run "$name"; then
    log "SKIP $name"
    return 0
  fi

  mkdir -p "$lpath"
  local dir_log="${LOG_DIR}/surgical-${name}-${STAMP}.log"
  log "START $name (files → $lpath)"

  local args=(
    -a
    --partial
    --partial-dir=.rsync-partial
    -e "ssh ${SSH_OPTS[*]}"
    -h
    --info=progress2
  )
  [[ "$DRY_RUN" -eq 1 ]] && args+=(--dry-run)

  set +e
  # shellcheck disable=SC2086
  "$RSYNC" "${args[@]}" \
    "${REMOTE_USER_HOST}:$1" \
    $([[ $# -gt 1 ]] && printf " ${REMOTE_USER_HOST}:%s" "${@:2}") \
    "${lpath}/" \
    2>&1 | tee -a "$dir_log" | tee -a "$MASTER_LOG"
  local rc=${PIPESTATUS[0]}
  set -e

  if [[ $rc -eq 0 ]]; then
    log "OK $name"
    echo "ok $name $(date -Iseconds)" >> "$STATUS_FILE"
  else
    log "FAIL $name rc=$rc"
    echo "fail $name rc=$rc $(date -Iseconds)" >> "$STATUS_FILE"
    return "$rc"
  fi
}

FAILED=0
run() {
  if ! "$@"; then
    FAILED=$((FAILED + 1))
    log "Continuing after failure..."
  fi
}

log "================================================================"
log "Surgical gem pull → $SURGICAL_ROOT"
log "TIER=$TIER  ONLY=${ONLY:-<tier packs>}  DRY_RUN=$DRY_RUN"
log "Ceilings: t0~8GiB  t1~25GiB  t2~50GiB  |  NEVER ecflow_output / PE* / field products"
log "================================================================"

HOME_GEMS_ROOT="${SURGICAL_ROOT}/home"
WORK_GEMS_ROOT="${SURGICAL_ROOT}/work"
PROJ="${SURGICAL_ROOT}/project"

# =========================================================================
# T0 — #1 BINARIES + CONFIGS + TEMPLATES/MESHES
# =========================================================================

# Critical: only the run executables (+ padcswan if present) + buildinfo
if should_run "project-binaries"; then
  mkdir -p "${PROJ}/adcirc-cg-custom-intel-unity/work"
  run rsync_path "project-binaries" \
    "${RP}/adcirc-cg-custom-intel-unity/work" \
    "${PROJ}/adcirc-cg-custom-intel-unity/work" \
    --include 'padcirc' \
    --include 'padcswan' \
    --include 'adcirc' \
    --include 'adcprep' \
    --include 'hstime' \
    --include 'aswip' \
    --include 'adcswan' \
    --exclude '*'
fi

# buildinfo + build scripts at tree root (tiny)
if should_run "project-buildinfo"; then
  mkdir -p "${PROJ}/adcirc-cg-custom-intel-unity"
  for f in adcirc.bin.buildinfo.json asgs-build.sh BUILD.md; do
    rsync -a -e "ssh ${SSH_OPTS[*]}" \
      "${REMOTE_USER_HOST}:${RP}/adcirc-cg-custom-intel-unity/${f}" \
      "${PROJ}/adcirc-cg-custom-intel-unity/" 2>/dev/null || true
  done
  log "OK project-buildinfo (best-effort)"
fi

run rsync_path "home-floodwater" \
  "${RH}/floodwater_files" \
  "${HOME_GEMS_ROOT}/floodwater_files"

run rsync_path "project-floodwater" \
  "${RP}/floodwater_files" \
  "${PROJ}/floodwater_files"

run rsync_path "home-asgs-files" \
  "${RH}/asgs_files" \
  "${HOME_GEMS_ROOT}/asgs_files"

run rsync_path "home-scripts" \
  "${RH}/scripts" \
  "${HOME_GEMS_ROOT}/scripts"

if should_run "home-confs"; then
  mkdir -p "${HOME_GEMS_ROOT}"
  for f in asgs-global.conf unity.h slurm_head_unity.h; do
    rsync -a -e "ssh ${SSH_OPTS[*]}" \
      "${REMOTE_USER_HOST}:${RH}/${f}" \
      "${HOME_GEMS_ROOT}/" 2>/dev/null || true
  done
  log "OK home-confs (best-effort)"
fi

run rsync_path "project-meshes" \
  "${RP}/meshes" \
  "${PROJ}/meshes"

run rsync_path "project-ricv1-meshes" \
  "${RP}/Ricv1Meshes" \
  "${PROJ}/Ricv1Meshes"

# Templates only (not whole ManualRuns)
for t in ManualRunTemplate RunTemplate FloodwaterRunTemplate; do
  run rsync_path "project-templates" \
    "${RP}/AdcircManualRuns/${t}" \
    "${PROJ}/AdcircManualRuns/${t}" \
    "${RERUN_EXCLUDES[@]}"
done

run rsync_path "project-manual-meshes" \
  "${RP}/AdcircManualRuns/meshes" \
  "${PROJ}/AdcircManualRuns/meshes"

if should_run "project-manual-readme"; then
  mkdir -p "${PROJ}/AdcircManualRuns"
  for f in README.txt Scenarios.txt; do
    rsync -a -e "ssh ${SSH_OPTS[*]}" \
      "${REMOTE_USER_HOST}:${RP}/AdcircManualRuns/${f}" \
      "${PROJ}/AdcircManualRuns/" 2>/dev/null || true
  done
  log "OK project-manual-readme (best-effort)"
fi

if should_run "project-qol"; then
  mkdir -p "${PROJ}"
  for f in readPostUtil.py readFortUtil.py Post_Nodes.json Post_Station_To_Node_Distances.json; do
    rsync -a -e "ssh ${SSH_OPTS[*]}" \
      "${REMOTE_USER_HOST}:${RP}/${f}" \
      "${PROJ}/" 2>/dev/null || true
  done
  log "OK project-qol (best-effort)"
fi

# =========================================================================
# T1 — WINDS + ECFLOW CONFIGS + ALLOWLISTED SCENARIOS
# =========================================================================

run rsync_path "home-ecflow-configs" \
  "${RH}/ecflow_configs" \
  "${HOME_GEMS_ROOT}/ecflow_configs"

# work wind library only (~1.5G) — NOT v18Runs 121G / out 23G
run rsync_path "work-scenario-wind" \
  "${RW}/scenario_files/wind" \
  "${WORK_GEMS_ROOT}/scenario_files/wind"

if [[ -z "$ONLY" ]] || [[ "$ONLY" == *work* ]]; then
  if [[ "$TIER" != "t0" ]]; then
    mkdir -p "${WORK_GEMS_ROOT}"
    for f in custom-intel-unity.state custom-intel-unity.state.new custom-intel-unity.state.old; do
      rsync -a -e "ssh ${SSH_OPTS[*]}" \
        "${REMOTE_USER_HOST}:${RW}/${f}" \
        "${WORK_GEMS_ROOT}/" 2>/dev/null || true
    done
    log "OK work profiles (best-effort)"
  fi
fi

# Project wind library (~5.6G) — KEEP .nc winds here intentionally
run rsync_path "project-scenario-files" \
  "${RP}/scenario_files" \
  "${PROJ}/scenario_files"

# Allowlisted ScenarioRuns only
for case in "${SCENARIO_ALLOWLIST[@]}"; do
  run rsync_path "project-scenario-${case}" \
    "${RP}/AdcircManualRuns/ScenarioRuns/${case}" \
    "${PROJ}/AdcircManualRuns/ScenarioRuns/${case}" \
    "${RERUN_EXCLUDES[@]}"
done

# Named top-level manual runs (not ScratchCopy)
for case in "${NAMED_RUNS_ALLOWLIST[@]}"; do
  run rsync_path "project-named-run-${case}" \
    "${RP}/AdcircManualRuns/${case}" \
    "${PROJ}/AdcircManualRuns/${case}" \
    "${RERUN_EXCLUDES[@]}"
done

# Slim intel source for rebuild (T1) — not object trees
run rsync_path "project-build-intel-slim" \
  "${RP}/adcirc-cg-custom-intel-unity" \
  "${PROJ}/adcirc-cg-custom-intel-unity" \
  --exclude '**/odir*/' \
  --exclude '**/*.o' \
  --exclude '**/*.mod' \
  --exclude '**/sandy_Deb/' \
  --exclude '**/.git/' \
  --exclude '**/work/PE*/'

# =========================================================================
# T2 — ASGS + THESIS INPUTS + SIDE TOOLS (optional)
# =========================================================================

run rsync_path "home-asgs" \
  "${RH}/projects/asgs" \
  "${HOME_GEMS_ROOT}/projects/asgs" \
  --exclude '.git/' \
  --exclude '**/work/PE*/' \
  --exclude '**/*.nc' \
  --exclude '**/odir*/' \
  --exclude '**/*.o'

run rsync_path "home-parametric-wind" \
  "${RH}/projects/parametric-wind-generation" \
  "${HOME_GEMS_ROOT}/projects/parametric-wind-generation" \
  --exclude '**/*.nc' \
  --exclude '**/temp/'

run rsync_path "home-funwave" \
  "${RH}/projects/FUNWAVE-TVD" \
  "${HOME_GEMS_ROOT}/projects/FUNWAVE-TVD" \
  --exclude '**/*.nc'

run rsync_path "home-richamp-unity" \
  "${RH}/projects/richamp-support-floodwater" \
  "${HOME_GEMS_ROOT}/projects/richamp-support-floodwater" \
  --exclude '.git/' \
  --exclude 'temp/' \
  --exclude 'post_temp/' \
  --exclude 'graphs/' \
  --exclude '*.nc' \
  --exclude '*_data_file.json' \
  --exclude 'twlForecast_*' \
  --exclude 'RICHAMP_*'

THESIS_BASE="${RP}/AdcircManualRuns/Aug29ScratchCopy/pranav_sai_uri_edu-runup"
for case in Dec172023RunupRun Dec222022RunupRun ErinRun; do
  run rsync_path "project-thesis-${case}" \
    "${THESIS_BASE}/${case}" \
    "${PROJ}/AdcircManualRuns/Aug29ScratchCopy/pranav_sai_uri_edu-runup/${case}" \
    "${RERUN_EXCLUDES[@]}"
done

run rsync_path "project-build-cg" \
  "${RP}/adcirc-cg" \
  "${PROJ}/adcirc-cg" \
  --exclude '**/odir*/' \
  --exclude '**/*.o' \
  --exclude '**/sandy_Deb/' \
  --exclude '**/work/PE*/'

# =========================================================================
# DELIVERABLES (layer C) — final RICHAMP products + graphs
# Required because raw field *.nc are NOT archived → cannot re-post without re-run
# =========================================================================

# Scenario post OUTDIRs (~23G measured) — primary consolidated delivery root
run rsync_path "work-scenario-out" \
  "${RW}/scenario_files/out" \
  "${WORK_GEMS_ROOT}/scenario_files/out" \
  "${DELIVERABLE_EXCLUDES[@]}"

run rsync_path "project-post-output" \
  "${RP}/post_output" \
  "${PROJ}/post_output" \
  "${DELIVERABLE_EXCLUDES[@]}"

if should_run "project-richamp-packs"; then
  for d in RICHAMP RICHAMPFilesHenri \
           RICHAMPFilesHenriAdvisory17_1ft RICHAMPFilesHenriAdvisory17_1m \
           RICHAMPFilesHenriAdvisory18_1m RICHAMPFilesHenriAdvisory19_1m \
           RICHAMPHenriAdvisory18-June23; do
    rsync -a --partial --partial-dir=.rsync-partial \
      -e "ssh ${SSH_OPTS[*]}" \
      "${DELIVERABLE_EXCLUDES[@]}" \
      "${REMOTE_USER_HOST}:${RP}/${d}/" \
      "${PROJ}/${d}/" 2>/dev/null || true
  done
  log "OK project-richamp-packs (best-effort)"
fi

# Final products colocated under allowlisted ScenarioRuns (RICHAMP_*, graphs/, Track)
for case in "${SCENARIO_ALLOWLIST[@]}"; do
  run rsync_path "project-deliverable-${case}" \
    "${RP}/AdcircManualRuns/ScenarioRuns/${case}" \
    "${PROJ}/AdcircManualRuns/ScenarioRuns/${case}" \
    "${DELIVERABLE_EXCLUDES[@]}" \
    "${DELIVERABLE_INCLUDES[@]}"
done

for case in "${NAMED_RUNS_ALLOWLIST[@]}"; do
  run rsync_path "project-named-deliverable-${case}" \
    "${RP}/AdcircManualRuns/${case}" \
    "${PROJ}/AdcircManualRuns/${case}" \
    "${DELIVERABLE_EXCLUDES[@]}" \
    "${DELIVERABLE_INCLUDES[@]}"
done

log "================================================================"
if [[ "$FAILED" -gt 0 ]]; then
  log "DONE WITH ERRORS: $FAILED packs failed. Re-run identical command to resume."
  echo "partial_fail count=$FAILED tier=$TIER $(date -Iseconds)" > "$STATUS_FILE"
  exit 2
fi
log "ALL REQUESTED PACKS OK → $SURGICAL_ROOT (tier=$TIER)"
echo "ok tier=$TIER $(date -Iseconds)" > "$STATUS_FILE"
du -sh "$SURGICAL_ROOT"/* 2>/dev/null | tee -a "$MASTER_LOG" || true
log "Skipped always: ecflow_output, work v18Runs/out, whole ManualRuns, PE*, fort.63/64/80/221/222 in kits, miniconda"
log "Re-run: same command resumes. Prefer --tier t0 first, then t1."
exit 0
