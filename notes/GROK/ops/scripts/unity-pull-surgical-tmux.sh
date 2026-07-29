#!/usr/bin/env bash
# Launch surgical gem pull inside tmux session unity-surgical
set -euo pipefail
DEST="${1:?pass DEST e.g. /Volumes/Pranav\'s Hard Drive}"
shift || true
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSION="unity-surgical"
GEMS="${SCRIPT_DIR}/unity-pull-surgical-gems.sh"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session $SESSION already exists. Attach: tmux attach -t $SESSION"
  echo "Kill first if stale: tmux kill-session -t $SESSION"
  exit 1
fi

# Write a one-shot runner so apostrophes/spaces in DEST never break tmux quoting
RUNNER="${TMPDIR:-/tmp}/unity-surgical-run-$$.sh"
{
  echo '#!/usr/bin/env bash'
  echo 'set -euo pipefail'
  printf 'DEST=%q\n' "$DEST"
  printf 'GEMS=%q\n' "$GEMS"
  echo 'EXTRA=()'
  for a in "$@"; do
    printf 'EXTRA+=(%q)\n' "$a"
  done
  cat <<'EOS'
set +u
if [[ ${#EXTRA[@]} -gt 0 ]]; then
  caffeinate -dims "$GEMS" "$DEST" "${EXTRA[@]}"
else
  caffeinate -dims "$GEMS" "$DEST"
fi
ec=$?
echo
echo "=== surgical pull finished (exit=$ec) ==="
echo "Scroll up for log; shell stays open."
exec bash
EOS
} > "$RUNNER"
chmod +x "$RUNNER"

# remain-on-exit so a quick failure is still inspectable
tmux new-session -d -s "$SESSION" "$RUNNER" || {
  echo "tmux new-session failed; running in background nohup instead"
  nohup "$RUNNER" > "${DEST}/unity-archive/logs/surgical-nohup.out" 2>&1 &
  echo "PID $!"
  exit 0
}
tmux set-option -t "$SESSION" remain-on-exit on 2>/dev/null || true
echo "Started tmux session: $SESSION"
echo "  attach: tmux attach -t $SESSION"
echo "  DEST:   $DEST"
echo "  runner: $RUNNER"
echo "  extras: $*"
echo "  tip:    prefer --tier t0 first (binaries+configs), then --tier t1"
