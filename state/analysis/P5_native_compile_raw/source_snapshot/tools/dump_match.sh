#!/usr/bin/env bash
# Receives a bounded IDLE log stream into a validated local CSV bundle.
# Has no firmware upload, reset or motion-command path.
# Independent tooling tests exercise offline and controlled transport failures.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$root/tools/dump_match.py" "$@"
