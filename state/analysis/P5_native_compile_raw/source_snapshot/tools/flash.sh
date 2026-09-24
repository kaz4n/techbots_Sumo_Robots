#!/usr/bin/env bash
# Stages a sketch and compiles it on the UNO Q over SSH.
# Keeps compile-only separate from any upload or reset.
# Tested with controlled SSH/rsync substitutes in tests/tooling/.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec python3 "$repo/tools/board_tool.py" flash "$@"
