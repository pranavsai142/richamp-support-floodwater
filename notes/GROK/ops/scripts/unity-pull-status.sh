#!/usr/bin/env bash
# Show whether a Unity archive pull is running, and how to stop it safely.
set -euo pipefail

SESSION="unity-pull"
if [[ $# -ge 1 ]]; then
  DEST="$1"
else
  DEST="/Volumes/Pranav's Hard Drive"
fi
LOG_DIR="${DEST}/unity-archive/logs"

echo "=== tmux session: ${SESSION} ==="
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "EXISTS"
  tmux list-sessions | grep "^${SESSION}:" || true
  echo
  echo "--- last 25 lines of pane ---"
  tmux capture-pane -t "$SESSION" -p 2>/dev/null | tail -25
else
  echo "NOT RUNNING (no tmux session)"
fi

echo
echo "=== rsync / caffeinate / pull processes ==="
# shellcheck disable=SC2009
if ps aux | grep -E '[r]sync.*(unity-archive|pranav_sai)|[c]affeinate -dims.*(unity-pull|research-archive)|[u]nity-pull-research-archive'; then
  :
else
  echo "(none - no active copy)"
fi

echo
echo "=== latest log ==="
if [[ -f "${LOG_DIR}/pull-latest.log" ]]; then
  echo "file: ${LOG_DIR}/pull-latest.log"
  tail -30 "${LOG_DIR}/pull-latest.log"
else
  echo "(no pull-latest.log yet at ${LOG_DIR})"
fi

echo
echo "=== status file ==="
if [[ -f "${LOG_DIR}/status.txt" ]]; then
  cat "${LOG_DIR}/status.txt"
else
  echo "(none)"
fi

echo
echo "=== safe stop (only if you want to kill the job) ==="
echo "  tmux kill-session -t ${SESSION}"
echo "  pkill -f 'rsync.*unity-archive' || true"
echo
echo "=== relaunch after stop ==="
echo "  cd /Users/pranav/projects/CloudVision/notes/GROK/ops/scripts"
printf '  ./unity-pull-tmux.sh %q --only home,work\n' "$DEST"
