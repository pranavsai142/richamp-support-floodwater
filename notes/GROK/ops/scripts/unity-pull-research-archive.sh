#!/usr/bin/env bash
# unity-pull-research-archive.sh
#
# Pull terabyte-scale research trees from Unity HPC (UMass) onto an external drive.
# Designed to run unattended inside tmux; fully resumable — re-run the same command
# after a drop/reboot and it continues where it left off.
#
# Usage:
#   ./unity-pull-research-archive.sh "/Volumes/Pranav's Hard Drive"
#   ./unity-pull-research-archive.sh DEST --dry-run
#   ./unity-pull-research-archive.sh DEST --only home
#   ./unity-pull-research-archive.sh DEST --only home,work
#   ./unity-pull-research-archive.sh DEST --only manual
#
# Recommended sequence:
#   1) --only home,work     (~210G, no ADCIRC filters)
#   2) --only manual        (entire AdcircManualRuns with PE* + *.nc filtered)
#
# --only manual:
#   Pulls ALL of AdcircManualRuns with the same filter everywhere:
#     --exclude PE*/ pe*/   (processor dirs)
#     --exclude *.nc        (ALL netCDF — including fort.68.nc)
#   Measured filtered ManualRuns ~550 GiB; full project filtered ~754 GiB.
#   At ~1.5–2 MB/s rsync via login this is multi-day — prefer Globus for bulk.
#
# Layout on DEST:
#   DEST/unity-archive/
#     home/…  work/…  project/…/AdcircManualRuns/  logs/  manifests/

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Remote host must be supplied by operator env; no cluster hostname is stored in-repo.
REMOTE_USER_HOST="${UNITY_HOST:-}"
if [[ -z "$REMOTE_USER_HOST" ]]; then
  echo "UNITY_HOST is unset. This archive tool is offline unless you set UNITY_HOST yourself." >&2
  echo "Day-to-day work uses the volume archive under unity-archive/ (bootstrap / t1), not a remote login." >&2
  exit 1
fi
ARCHIVE_NAME="unity-archive"

# Prefer modern Homebrew rsync (macOS stock is ancient 2.6.9).
if [[ -x /opt/homebrew/bin/rsync ]]; then
  RSYNC=/opt/homebrew/bin/rsync
elif [[ -x /usr/local/bin/rsync ]]; then
  RSYNC=/usr/local/bin/rsync
else
  RSYNC=$(command -v rsync)
fi

# SSH: keep long transfers alive; reuse one connection for speed.
SSH_OPTS=(
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=120
  -o TCPKeepAlive=yes
  -o Compression=no
  -o ControlMaster=auto
  -o ControlPath="${HOME}/.ssh/cm-%r@%h:%p"
  -o ControlPersist=4h
)

# Optional bandwidth cap in KB/s (empty = unlimited). Example: 80000 ≈ 80 MB/s
BWLIMIT="${BWLIMIT:-}"

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
DEST_ROOT=""
DRY_RUN=0
ONLY=""

usage() {
  sed -n '2,25p' "$0" | sed 's/^# \?//'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --only) ONLY="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    -*)
      echo "Unknown flag: $1" >&2
      usage
      ;;
    *)
      if [[ -z "$DEST_ROOT" ]]; then
        DEST_ROOT="$1"
      else
        echo "Unexpected argument: $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

if [[ -z "$DEST_ROOT" ]]; then
  echo "ERROR: pass the external drive mount path." >&2
  echo "Example: $0 /Volumes/ResearchBackup" >&2
  echo "" >&2
  echo "Currently mounted volumes:" >&2
  ls -1 /Volumes 2>/dev/null || true
  exit 1
fi

# Strip trailing slash
DEST_ROOT="${DEST_ROOT%/}"

if [[ ! -d "$DEST_ROOT" ]]; then
  echo "ERROR: destination does not exist: $DEST_ROOT" >&2
  echo "Plug in the drive and wait for it to appear under /Volumes/..." >&2
  ls -1 /Volumes 2>/dev/null || true
  exit 1
fi

# Refuse to write onto the nearly-full system volume by accident.
if [[ "$DEST_ROOT" == /Users/* || "$DEST_ROOT" == /System/* || "$DEST_ROOT" == / ]]; then
  echo "ERROR: refusing to use system path as archive dest: $DEST_ROOT" >&2
  echo "Point this at your external drive, e.g. /Volumes/YourDrive" >&2
  exit 1
fi

# macOS TCC: Terminal/iTerm/tmux often get "Operation not permitted" on
# removable volumes until Full Disk Access (or Files and Folders → Removable
# Volumes) is granted. Probe before we waste time on SSH.
tcc_hint() {
  cat <<'EOF' >&2

macOS blocked write access to this external drive (TCC privacy).

Fix (2 minutes):
  1. System Settings → Privacy & Security → Full Disk Access
  2. Click +, add these (enable the toggle for each):
       - Terminal.app   (or iTerm if you use that)
       - /bin/bash
       - Optionally: the Grok / Cursor app if you launch scripts from there
  3. Quit Terminal fully (Cmd-Q) and reopen
  4. Re-run with the path QUOTED (this volume has a space + apostrophe):

       ./unity-pull-tmux.sh "/Volumes/Pranav's Hard Drive" --only home,work

Also works: System Settings → Privacy & Security → Files and Folders
  → Terminal → enable "Removable Volumes".

EOF
}

probe="$DEST_ROOT/.unity-pull-write-probe-$$"
if ! mkdir -p "$DEST_ROOT/.unity-pull-probe-dir-$$" 2>/dev/null; then
  echo "ERROR: cannot create directories on: $DEST_ROOT" >&2
  echo "       (mkdir → Operation not permitted is almost always macOS privacy)" >&2
  tcc_hint
  exit 1
fi
rmdir "$DEST_ROOT/.unity-pull-probe-dir-$$" 2>/dev/null || true
if ! touch "$probe" 2>/dev/null; then
  echo "ERROR: cannot write files on: $DEST_ROOT" >&2
  tcc_hint
  exit 1
fi
rm -f "$probe"

ARCHIVE_ROOT="${DEST_ROOT}/${ARCHIVE_NAME}"
LOG_DIR="${ARCHIVE_ROOT}/logs"
MANIFEST_DIR="${ARCHIVE_ROOT}/manifests"
if ! mkdir -p "$LOG_DIR" "$MANIFEST_DIR"; then
  echo "ERROR: mkdir failed under $ARCHIVE_ROOT" >&2
  tcc_hint
  exit 1
fi

STAMP=$(date +%Y%m%d-%H%M%S)
MASTER_LOG="${LOG_DIR}/pull-${STAMP}.log"
LATEST_LOG="${LOG_DIR}/pull-latest.log"
STATUS_FILE="${LOG_DIR}/status.txt"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
exec > >(tee -a "$MASTER_LOG" | tee "$LATEST_LOG") 2>&1

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
die() { log "FATAL: $*"; exit 1; }

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
log "=== Unity research archive pull ==="
log "remote:      $REMOTE_USER_HOST"
log "dest:        $ARCHIVE_ROOT"

# NOTE: never pipe rsync --version into `head` under `set -o pipefail`.
# macOS /bin/bash 3.2 gets SIGPIPE (exit 141) and the whole script dies
# silently right after the banner — which is what killed the first launch.
RSYNC_VER_LINE=$($RSYNC --version 2>&1 | sed -n '1p') || true
# Match "rsync version N" only — not "protocol version 32" later on the line.
RSYNC_MAJOR=$(printf '%s\n' "$RSYNC_VER_LINE" | sed -n 's/.*rsync  *version \([0-9][0-9]*\).*/\1/p')
[[ -n "${RSYNC_MAJOR:-}" ]] || RSYNC_MAJOR=0

log "rsync:       $RSYNC ($RSYNC_VER_LINE)"
log "dry_run:     $DRY_RUN"
log "bwlimit:     ${BWLIMIT:-unlimited}"
log "only:        ${ONLY:-all}"
log "log:         $MASTER_LOG"

if [[ "$RSYNC_MAJOR" -lt 3 ]]; then
  log "WARNING: macOS stock rsync is ancient and slow for TB transfers."
  log "  Install a modern rsync once, then re-run:"
  log "    brew install rsync"
  log "Continuing with stock rsync for now..."
fi

# Ensure ControlPath directory exists
mkdir -p "${HOME}/.ssh"

log "Checking SSH to Unity..."
# Prefer non-interactive (keys). If that fails (Duo/MFA), fall back to interactive
# so a first login in this tmux pane can unlock the rest of the transfer.
if ssh "${SSH_OPTS[@]}" -o ConnectTimeout=30 -o BatchMode=yes \
     "$REMOTE_USER_HOST" 'echo ok && hostname && whoami'; then
  log "SSH: BatchMode OK"
elif ssh "${SSH_OPTS[@]}" -o ConnectTimeout=60 \
     "$REMOTE_USER_HOST" 'echo ok && hostname && whoami'; then
  log "SSH: interactive login OK (ControlMaster will reuse this session)"
else
  die "SSH failed. Fix keys/MFA/VPN first: ssh $REMOTE_USER_HOST"
fi

# Free space on destination (macOS df)
FREE_KB=$(df -k "$DEST_ROOT" | awk 'NR==2 {print $4}')
FREE_GB=$((FREE_KB / 1024 / 1024))
log "Destination free space: ~${FREE_GB} GiB"
if [[ "$FREE_GB" -lt 100 ]]; then
  log "WARNING: less than 100 GiB free on dest — you said TB scale. Confirm drive size."
fi

# ---------------------------------------------------------------------------
# Source table: short_name | remote_path | local_relpath
# Full /project tree is intentionally NOT a default source (multi-TB).
# Use --only manual for AdcircManualRuns with the ScenarioRuns filter policy.
# ---------------------------------------------------------------------------
REMOTE_MANUAL="/project/pi_iginis_uri_edu/pranav_sai_uri_edu/AdcircManualRuns"
LOCAL_MANUAL="project/pi_iginis_uri_edu/pranav_sai_uri_edu/AdcircManualRuns"

# shellcheck disable=SC2034
SOURCES=(
  "home|/home/pranav_sai_uri_edu|home/pranav_sai_uri_edu"
  "work|/work/pi_iginis_uri_edu/pranav_sai_uri_edu|work/pi_iginis_uri_edu/pranav_sai_uri_edu"
)

should_run() {
  local name="$1"
  # No --only → home + work only (safe default; never full project).
  if [[ -z "$ONLY" ]]; then
    [[ "$name" == home || "$name" == work ]] && return 0
    return 1
  fi
  # comma-separated allowlist
  [[ ",${ONLY}," == *",${name},"* ]] && return 0
  return 1
}

# ---------------------------------------------------------------------------
# Remote size estimate (best effort; can be slow on huge trees — optional)
# ---------------------------------------------------------------------------
estimate_sizes() {
  log "Estimating remote sizes (du -sh; may take a while on huge trees)..."
  for entry in "${SOURCES[@]}"; do
    IFS='|' read -r name rpath lrel <<<"$entry"
    should_run "$name" || continue
    log "  du -sh $rpath ..."
    # timeout-friendly: du can take hours on multi-TB; show what we can
    if out=$(ssh "${SSH_OPTS[@]}" "$REMOTE_USER_HOST" "du -sh '$rpath' 2>/dev/null" || true); then
      log "  $name: ${out:-unknown}"
    fi
  done
}

# Uncomment next line if you want size estimates before transfer (can be slow):
# estimate_sizes

# ---------------------------------------------------------------------------
# rsync one tree
# ---------------------------------------------------------------------------
# Excludes: skip pure cache / junk that is easy to regenerate and often huge.
# Keep everything research-relevant. Edit if you need caches too.
EXCLUDES=(
  --exclude '.cache/'
  --exclude '.Trash/'
  --exclude '.local/share/Trash/'
  --exclude '**/__pycache__/'
  --exclude '**/.ipynb_checkpoints/'
  --exclude '**/*.tmp'
  --exclude '**/.DS_Store'
  # Uncomment if conda envs live in home and you reinstall instead of archive:
  # --exclude 'miniconda3/'
  # --exclude 'anaconda3/'
  # --exclude '.conda/pkgs/'
)

# rsync_one NAME REMOTE_PATH LOCAL_RELPATH [extra rsync excludes...]
rsync_one() {
  local name="$1" rpath="$2" lrel="$3"
  shift 3
  local -a extra_excludes=("$@")

  local local_path="${ARCHIVE_ROOT}/${lrel}"
  local dir_log="${LOG_DIR}/rsync-${name}-${STAMP}.log"
  local done_marker="${MANIFEST_DIR}/${name}.done"
  local start_marker="${MANIFEST_DIR}/${name}.started"

  mkdir -p "$local_path"

  log "----------------------------------------------------------------"
  log "START tree: $name"
  log "  remote: ${REMOTE_USER_HOST}:${rpath}/"
  log "  local:  ${local_path}/"
  log "  log:    ${dir_log}"
  if [[ ${#extra_excludes[@]} -gt 0 ]]; then
    log "  extra excludes: ${extra_excludes[*]}"
  else
    log "  extra excludes: (none — full tree minus base junk excludes)"
  fi
  date +%s > "$start_marker"
  echo "running $name $(date -Iseconds)" > "$STATUS_FILE"

  # Build rsync args compatible with v2 and v3.
  # Resume strategy: --partial + --partial-dir keeps incomplete files so a
  # re-run continues. Do NOT add --append / --append-verify: rsync 3.4+
  # rejects combining those with --partial-dir (error we hit on first real run).
  local -a args=(
    -a
    --partial
    --partial-dir=".rsync-partial"
    -e "ssh ${SSH_OPTS[*]}"
  )

  # Archival pull: never --delete. Safe to re-run forever; only adds/updates.

  if [[ "$RSYNC_MAJOR" -ge 3 ]]; then
    args+=(-h --info=progress2 --stats --human-readable)
  else
    args+=(--progress --stats)
  fi

  if [[ -n "$BWLIMIT" ]]; then
    args+=(--bwlimit="$BWLIMIT")
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    args+=(--dry-run)
  fi

  args+=("${EXCLUDES[@]}")
  if [[ ${#extra_excludes[@]} -gt 0 ]]; then
    args+=("${extra_excludes[@]}")
  fi

  # Trailing slashes: copy CONTENTS of remote dir into local_path
  set +e
  "$RSYNC" "${args[@]}" \
    "${REMOTE_USER_HOST}:${rpath}/" \
    "${local_path}/" \
    2>&1 | tee -a "$dir_log"
  local rc=${PIPESTATUS[0]}
  set -e

  if [[ $rc -eq 0 ]]; then
    log "OK tree: $name (exit 0)"
    if [[ "$DRY_RUN" -eq 0 ]]; then
      {
        echo "name=$name"
        echo "remote=${rpath}"
        echo "local=${local_path}"
        echo "finished=$(date -Iseconds)"
        echo "rsync_rc=0"
        echo "extra_excludes=${extra_excludes[*]:-}"
      } > "$done_marker"
      # Local size snapshot
      du -sh "$local_path" > "${MANIFEST_DIR}/${name}.local-size.txt" 2>/dev/null || true
    fi
  else
    log "FAIL tree: $name (rsync exit $rc) — re-run the same script to resume"
    echo "failed $name rc=$rc $(date -Iseconds)" > "$STATUS_FILE"
    return "$rc"
  fi
}

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
FAILED=0
RAN=0

run_named() {
  local name="$1"
  shift
  if ! should_run "$name"; then
    log "SKIP $name (not selected by --only ${ONLY:-<default home,work>})"
    return 0
  fi
  RAN=$((RAN + 1))
  if ! rsync_one "$name" "$@"; then
    FAILED=$((FAILED + 1))
    log "Continuing with remaining trees after failure of $name..."
  fi
}

for entry in "${SOURCES[@]}"; do
  IFS='|' read -r name rpath lrel <<<"$entry"
  run_named "$name" "$rpath" "$lrel"
done

# --- AdcircManualRuns (filter PE* + ALL *.nc everywhere) -------------------
run_named "manual" \
  "$REMOTE_MANUAL" \
  "$LOCAL_MANUAL" \
  --exclude 'PE*/' \
  --exclude 'pe*/' \
  --exclude '*.nc'

log "================================================================"
if [[ "$RAN" -eq 0 ]]; then
  die "No trees selected. --only was: ${ONLY:-<empty>}"
fi

if [[ "$FAILED" -gt 0 ]]; then
  log "DONE WITH ERRORS: $FAILED of $RAN trees failed. Re-run the identical command to resume."
  echo "partial_fail count=$FAILED $(date -Iseconds)" > "$STATUS_FILE"
  exit 2
fi

log "ALL OK: $RAN tree(s) copied into $ARCHIVE_ROOT"
echo "ok $(date -Iseconds)" > "$STATUS_FILE"

if [[ "$DRY_RUN" -eq 0 ]]; then
  log "Local archive summary:"
  du -sh "$ARCHIVE_ROOT"/* 2>/dev/null || true
  log "Manifests: $MANIFEST_DIR"
  log "Logs:      $LOG_DIR"
fi

log "Re-run the same command anytime to resume / catch new files."
exit 0
