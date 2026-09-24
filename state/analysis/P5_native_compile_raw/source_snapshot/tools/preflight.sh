#!/usr/bin/env bash
# Collects read-only board software inventory through strict SSH.
# Leaves firmware, motor outputs and board configuration untouched.
# Verified with controlled SSH substitutes; hardware evidence requires a real run.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec python3 "$repo/tools/board_tool.py" preflight "$@"
