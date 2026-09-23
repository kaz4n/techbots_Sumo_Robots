# Offline B8 attempt-owner validation

2026-09-23 Asia/Dubai. D-070 contract/public headerd38c0eb preceded source and
independent tests. IMPLEMENTED/HOST-TESTED/SCRIPT-TESTED/REVIEWED only.
D-068 preparation scope remains separate from P0/P1 gates and P2 integration.

New recorder::AttemptRecorder owns the existing frame/event rings. A validated
new accepted START is the only clear boundary. Prior-frame/event prefix is
excluded from a new epoch; replay cannot erase evidence. Reset interrupts an
unfinished attempt without clearing data. One delayed stopping receipt seals
the attempt, with explicit missing/invalid/overflow/gap flags and source counters.
No motion, clock, cadence, heap, hardware, transport or app integration.

Ownership: worker implemented onlyrecorder.cpp without reading tests; independent
author derived49 newcases from frozen contract/public headers/specs without
implementation reads. Root owns header/contract/CMake/manifests/state. Separate
fresh same-model reviewer checked actual code/tests/receipts and reproduced
scoped cases; full verdict reviews/P2_attempt_recorder_codex.md.

Actual WSL g++13.3/CMake3.28.3 C++17/doctest2.4.12 validation:
- Normal configure/build/ctest exit0,969cases/17459867assertions,zero fail/skip;
  ctest3.43s.
- ASan/UBSan configure/build/ctest exit0,same969/17459867,zero fail/skip,17.31s;
  no sanitizer diagnostics.
- Controlled tooling317checks PASS124.657s,exit0. Source/staging substitutions,
  not target builds. Exact five-entry inert manifest refresh approved separately.
- Fresh reviewer scoped49cases/426061assertions pass normal+strictsanitizers.
- Tests include32 deterministic128-result attempts plus starts/tails and10000
  saturation arithmetic comparisons; boundaries,malformed data,tokenmax/zero,
  counter regressions and independent event4096/frame10001 behavior.

No source/test repair was needed for D-070. Its first builds/full runs pass.
Exact argv/timestamps/statuses/raw streams/SHA256 in P2_attempt_validation_raw/.
The separate memory-analysis command's first path failure is preserved in
P2_memory_offline_receipt_20260923.json, corrected at first retry in
P2_memory_readelf_retry1_20260923.json; fresh reviewer verified both.

Actual host ABI sizeof summary96B/owner292968B recorded with probe source and
commands in P2_attempt_host_size_20260923.json; not target layout/free RAM.
SC-AH default50Hz payload292794B exceeds262144B pool. The pinned size-tool audit
in P2_memory_budget_followup_20260923.md distinguishes RAM allocated sections
from upload-file size;25Hz remains only an explicitly conditional planning
candidate, not adopted. All76 B16 defaults remain; locked/core/app unchanged.

No board command, target compile, upload/reset, external hardware connection,
motor run, sensor assumption, complete-tick measurement, B8/P2 or human phase
gate occurred. Last known uploaded image is prior inert QTR61d7a2d0/default.
Next task: resolve SC-AH with a scoped candidate RAM budget/compile-only design
contract before changing LOG_HZ or integrating this owner. No production Bridge
transport, dump schema/caller, full HAL or target-fit claim is implemented.
