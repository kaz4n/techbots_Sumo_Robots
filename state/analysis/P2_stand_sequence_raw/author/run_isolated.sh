#!/usr/bin/env bash
# Runs the frozen D119 oracle in isolated normal and sanitizer host executables.
# Preserves commands and results without reading or changing implementation text.
# Authorized after the amended oracle freeze; never targets or contacts hardware.
set -uo pipefail
repo="$1"
evidence="$repo/state/analysis/P2_stand_sequence_raw/author"
exec > >(tee "$evidence/first_execution.log") 2>&1
set -x
date --iso-8601=seconds
g++ --version
df -h /dev/shm
findmnt -no OPTIONS /dev/shm
sha256sum "$repo/tests/test_stand_sequence.cpp" \
  "$repo/src/core/stand_sequence.cpp" "$repo/src/core/stand_sequence.h" \
  "$repo/src/config.h" "$repo/host/third_party/doctest.h" \
  "$evidence/stand_sequence_main.cpp" "$evidence/run_isolated.sh"
build="$(mktemp -d /dev/shm/d119-author-XXXXXX)"
printf '%s\n' "$build" > "$evidence/isolated_build_path.txt"
flags=(-std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti
       -DDOCTEST_CONFIG_NO_EXCEPTIONS -I "$repo/src" -isystem "$repo/host/third_party")
sources=("$repo/tests/test_stand_sequence.cpp" "$repo/src/core/stand_sequence.cpp"
         "$evidence/stand_sequence_main.cpp")
g++ "${flags[@]}" -O0 "${sources[@]}" -o "$build/normal" \
  > "$evidence/normal_compile.txt" 2>&1
normal_compile=$?
cat "$evidence/normal_compile.txt"
normal_run=NOT_RUN
if [[ $normal_compile == 0 ]]; then
  sha256sum "$build/normal"
  "$build/normal" --no-colors=true > "$evidence/normal_run.txt" 2>&1
  normal_run=$?
  cat "$evidence/normal_run.txt"
fi
g++ "${flags[@]}" -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
  "${sources[@]}" -o "$build/sanitized" > "$evidence/sanitizer_compile.txt" 2>&1
sanitizer_compile=$?
cat "$evidence/sanitizer_compile.txt"
sanitizer_run=NOT_RUN
if [[ $sanitizer_compile == 0 ]]; then
  sha256sum "$build/sanitized"
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
    "$build/sanitized" --no-colors=true > "$evidence/sanitizer_run.txt" 2>&1
  sanitizer_run=$?
  cat "$evidence/sanitizer_run.txt"
fi
printf 'normal_compile=%s\nnormal_run=%s\nsanitizer_compile=%s\nsanitizer_run=%s\n' \
  "$normal_compile" "$normal_run" "$sanitizer_compile" "$sanitizer_run" \
  | tee "$evidence/execution_status.txt"
sha256sum "$repo/tests/test_stand_sequence.cpp" "$repo/src/core/stand_sequence.cpp"
date --iso-8601=seconds
[[ $normal_compile == 0 && $normal_run == 0 && $sanitizer_compile == 0 && $sanitizer_run == 0 ]]
