#!/usr/bin/env bash
# Launch (or attach) a tmux session that runs the Unity archive pull.
#
# Usage:
#   ./unity-pull-tmux.sh /Volumes/YourDriveName
#   ./unity-pull-tmux.sh /Volumes/YourDriveName --only work,project

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PULL="${SCRIPT_DIR}/unity-pull-research-archive.sh"
SESSION="unity-pull"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /Volumes/YourDrive [extra args for pull script...]" >&2
  echo "Mounted volumes:" >&2
  ls -1 /Volumes 2>/dev/null || true
  exit 1
fi

DEST="$1"
shift
EXTRA=("$@")

if [[ ! -d "$DEST" ]]; then
  echo "ERROR: $DEST not mounted yet. Plug the drive in first." >&2
  ls -1 /Volumes 2>/dev/null || true
  exit 1
fi

chmod +x "$PULL"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' already exists."
  echo
  echo "This does NOT start a second copy — it only attaches to the existing pane."
  echo "Before relaunching a new pull, stop the old session if the job is done/dead:"
  echo "  tmux kill-session -t $SESSION"
  echo "  ./unity-pull-status.sh \"$DEST\""
  echo
  echo "Attaching now (Ctrl-b then d to detach)..."
  exec tmux attach -t "$SESSION"
fi

# Prefer a modern bash if present (script is written for bash; macOS /bin/bash is 3.2).
if [[ -x /opt/homebrew/bin/bash ]]; then
  BASH_BIN=/opt/homebrew/bin/bash
elif [[ -x /usr/local/bin/bash ]]; then
  BASH_BIN=/usr/local/bin/bash
else
  BASH_BIN=/bin/bash
fi

# Keep Mac awake; remain in shell after finish so the pane stays readable.
# Always print the pull exit code so a silent death is obvious.
tmux new-session -d -s "$SESSION" \
  "caffeinate -dims $(printf '%q ' "$BASH_BIN" "$PULL" "$DEST" "${EXTRA[@]}") ; ec=\$?; echo; echo \"=== pull finished (exit=\$ec) — scroll up / check logs ===\"; exec $BASH_BIN"

echo "Started tmux session: $SESSION"
echo "  Attach:  tmux attach -t $SESSION"
echo "  Detach:  Ctrl-b then d"
echo "  Status:  ./unity-pull-status.sh \"$DEST\""
echo "  Kill:    tmux kill-session -t $SESSION"
echo ""
echo "Attaching now..."
exec tmux attach -t "$SESSION"
