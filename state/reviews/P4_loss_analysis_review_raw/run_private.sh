#!/usr/bin/env bash
# Runs the frozen D130 private oracle and retains the exact Python exit code.
# Avoids shell command-string interpolation across PowerShell and WSL.
# Result is verified by the coordinator alongside source and oracle hashes.
set -u
cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots || exit 90
raw=state/reviews/P4_loss_analysis_review_raw
export TMPDIR=/dev/shm
export PYTHONDONTWRITEBYTECODE=1
python3 "$raw/private_probes.py" > "$raw/private_linux.log" 2>&1
status=$?
printf '%s\n' "$status" > "$raw/private_linux.exit"
cat "$raw/private_linux.log"
exit "$status"
