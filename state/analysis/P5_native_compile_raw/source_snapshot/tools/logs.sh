#!/usr/bin/env bash
# Receives router Monitor output through SSH without sending MCU input.
# Provides a read-only P0 transport whose board round trip remains pending.
# Tested with a controlled SSH substitute in tests/tooling/.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec python3 "$repo/tools/board_tool.py" logs "$@"
