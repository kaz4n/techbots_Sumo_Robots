#!/usr/bin/env bash
# Executes author checks with literal shell variables and captures process status.
# Every C++ compile/run also retains its own structured command receipt.
# This script performs host-only work and never invokes a board transport.
set -u
receipt=state/analysis/P2_calibration_presence_raw/author
label=${1:?run label required}
date -u --iso-8601=seconds > "$receipt/$label.started"
printf '%s\n' 'python3 tests/tooling/test_calibration_presence.py' > "$receipt/$label.command"
python3 tests/tooling/test_calibration_presence.py > "$receipt/$label.stdout" 2> "$receipt/$label.stderr"
code=$?
printf '%s\n' "$code" > "$receipt/$label.exit"
date -u --iso-8601=seconds > "$receipt/$label.finished"
cat "$receipt/$label.stdout" "$receipt/$label.stderr"
exit "$code"
