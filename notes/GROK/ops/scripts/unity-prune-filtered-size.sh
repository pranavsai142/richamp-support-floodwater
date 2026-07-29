#!/usr/bin/env bash
# unity-prune-filtered-size.sh
#
# Atmospheric-twin / coastal prune technique for fast filtered size checks
# on Unity ADCIRC trees: skip PE*/pe* processor dirs and all *.nc files,
# then sum remaining file bytes.
#
# Usage (on a tree already available locally / on the archive volume):
#   ./unity-prune-filtered-size.sh /path/to/AdcircManualRuns
#   ./unity-prune-filtered-size.sh /path/to/dir --label ManualRuns
#
# Do NOT use bare `du -sh` on multi-TB ManualRuns-class trees as the primary
# size method — this prune walk is the supported measurement.

set -euo pipefail

TARGET=""
LABEL=""

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \?//'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    -*)
      echo "Unknown flag: $1" >&2
      usage
      ;;
    *)
      if [[ -z "$TARGET" ]]; then
        TARGET="$1"
      else
        echo "Unexpected argument: $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "ERROR: pass a directory or file path." >&2
  usage
fi

if [[ -z "$LABEL" ]]; then
  LABEL=$(basename "$TARGET")
fi

if [[ ! -e "$TARGET" ]]; then
  printf "%s\tMISSING\n" "$LABEL"
  exit 2
fi

if [[ -f "$TARGET" ]]; then
  case "$TARGET" in
    *.nc)
      printf "%s\t0.00\tGiB\t(file is .nc, pruned)\n" "$LABEL"
      ;;
    *)
      bytes=$(stat -c%s "$TARGET" 2>/dev/null || stat -f%z "$TARGET" 2>/dev/null || echo 0)
      awk -v b="$bytes" -v l="$LABEL" 'BEGIN{printf "%s\t%.2f\tGiB\t(file)\n", l, b/1024/1024/1024}'
      ;;
  esac
  exit 0
fi

# Directory: prune PE*/pe* and *.nc (GNU find %s; Unity is Linux)
if ! bytes=$(find "$TARGET" \
  \( -type d \( -name 'PE*' -o -name 'pe*' \) -prune \) -o \
  \( -type f -name '*.nc' -prune \) -o \
  -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END{print s+0}'); then
  echo "ERROR: find failed on $TARGET" >&2
  exit 3
fi

awk -v b="$bytes" -v l="$LABEL" 'BEGIN{printf "%s\t%.2f\tGiB\n", l, b/1024/1024/1024}'
