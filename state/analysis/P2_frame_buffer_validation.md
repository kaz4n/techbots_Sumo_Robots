# Offline B8 frame storage validation

2026-09-23 Asia/Dubai. D-068 scheduling interpretation and D-069 public contract
committed7f446a9 before implementation/independent tests. IMPLEMENTED, HOST-TESTED,
SCRIPT-TESTED, fresh same-model REVIEWED. P0/P1 and B8/P2 gates remain pending.

Adds fixed latest-frame storage in hal/recorder_frames.* and explicit host CMake
source inclusion.25 new spec/header-derived cases were independently authored
without implementation reads. No core/application/locked test or B16 value changed.
No clock, I/O, heap, hardware instance, cadence or lifecycle integration exists.

Actual WSL CMake3.28.3/g++13.3/C++17/doctest2.4.12 validation:
- Normal configure/build exit0;920cases and17033806assertions pass,0fail/skip,
  ctest total4.01s.
- ASan/UBSan configure/build exit0;same920/17033806,0fail/skip,18.11s;no diagnostics.
- Full controlled Python tooling317tests pass123.052s,exit0. These are script
  substitutes/source checks, not board builds. They preserve compile-only and
  upload/source-guard semantics with the reviewed five-entry manifest refresh.
- Fresh reviewer independently reproduced25cases/3267838assertions in each
  binary and8 config checks; scope/result in reviews/P2_frame_buffer_codex.md.

Exact argv,timestamps,statuses and byte-preserved stdout/stderr are in
P2_frame_validation_raw/ with SHA256 manifest. Initial compile fixture mismatch
and initial config allowlist omission are preserved in P2_frame_failure_analysis.md
and first-run raw receipts; each resolved on its first repair. No assertions
were weakened or existing locked tests amended. Git diff --check passes.

Host ABI sizeof receipt P2_frame_host_size_20260923.json: StoredFrame26B,
FrameBuffer260064B, EventBuffer32784B, combined292848B. Payload alone292794B
already exceeds installed262144-byte LLEXT pool; SC-AH records this deployment
blocker. This host measurement is not target layout, allocated/free RAM or WCET.
No LOG_HZ change; all76 B16 defaults retained. New200000ms window derives from
B15 and10001 capacity conservatively includes start/final endpoint.

Manifest proposal records every file/hash; review approved only existing five
keys. No board commands, upload/reset, motion, external hardware connection,
transport/dump, MCU memory fit, full-loop timing, B8 acceptance or human phase
pass occurred. MCU remains the earlier measured inert QTR image.

Next eligible storage unit requires an adopted attempt-owner contract from
P2_recorder_composition_proposal.md, especially new-START epoch splitting, delayed
final frames, explicit reset preservation and exhaustion-token semantics.
