#!/usr/bin/env bash
# Configures, compiles and runs the local C++17 tests.
# Keeps host checks independent of board access.
# Validated with the P0 doctest smoke test and failure propagation.
set -euo pipefail
if (($#)); then echo 'Usage: tools/test_host.sh' >&2; exit 2; fi
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cmake -S "$repo/host" -B "$repo/build/host" -DCMAKE_BUILD_TYPE=Debug
cmake --build "$repo/build/host" --parallel 2
ctest --test-dir "$repo/build/host" --output-on-failure
