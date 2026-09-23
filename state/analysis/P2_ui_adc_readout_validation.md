# D114 pinned readout and single-run guard: software acceptance

IMPLEMENTED / HOST-TESTED / SCOPED-REVIEW-PASS,2026-09-24 Asia/Dubai.
No MCU upload/reset/readout has occurred at this checkpoint. Firmware target
evidence remains F139 and P2_ui_adc_probe_firmware_validation.md.

Capture first/final sourcef4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444
passes42 independent frozen methods and42 private reviewer methods, zero skips.
The author used public schema and opaque target bytes, not implementation bodies.
Final tests02b14721; all original failures and two explicitly reviewed fixture
corrections remain under P2_ui_adc_probe_raw/author_capture. Production capture
code never changed to obtain a pass. The corrections preserve actual loader
bytes, delegated symlink guards, supported command order and public call
preconditions; they do not relax locked tests or hide hardware failures.

Exact byte decoder retains raw Report/Capture evidence, requires equal complete
Runner blobs for frozen status, and keeps COMPLETE128/FAULT/nonterminal/invalid
distinct. The collector verifies installed tools and full deployed flash before
and after two Runner reads with identical descriptors. Raw ET_REL st_value0 maps
to BSS+0. Full9893-byte BSS and9892-byte Runner extents must fit SRAM. Only the
fixed22-read/588016-byte/26-command sequence is admitted, under unchanged hard
limits; redundant larger ceilings are source-reviewed, not falsely exercised
through unsupported command replays. Physical acceptance is always false.

Guard first/final1aa109a2ed068ed4d21dc442aa9195b516f8df264c5a04a0b71a75949cb5d8e8
and boardd1fda9649a30679ed9282d3b03e7a244f8c21ea51b3ded2ad6f7a83c4fb9fcc7
pass22 independent controlled methods. Original21pass/1 mocked-stage-basename
failure and the sole approved fixture correction are retained; production stayed
unchanged. The author previously reviewed old board code, but did not read the
new guard body. A different context reviewed the actual guard/diff; that context
implemented capture and is not claimed independent of capture. Capture reviewer
is separately independent of capture implementation/test authors. All are reused
same-model contexts; these are scoped software reviews, not human phase gates.

Prior145 policy methods pass on the changed board helper, exit0,50.727s; exact
argv/UTC/status/output in P2_app_build_raw/ui_adc_guard_prior145.*. Adding only
bench/ui_adc_probe exact396bcc45 to the inert manifest preserves all eight prior
values. The affected probe17 and guard22 tests pass again (39total), exit0:
P2_app_build_raw/ui_adc_manifest39.*. Generic probe upload remains refused without
the exact run option; compile-only plus that option refuses before transport.

Fresh checked compile/source/two-artifact identities and eleven approved files
bind the eventual run. Exclusive fsynced attempt precedes one finite120s upload;
nonzero/timeout/uncertain launch consumes it, preserving actual outcome. There
is no reset/retry/capture in the guard. Missing records explicitly refuse.
The manifest entry alone does not authorize upload or manufacture hardware facts.

Separate reviews: state/reviews/P2_ui_adc_capture_review.md and
state/reviews/P2_ui_adc_run_review.md. Exact snapshots, hashes, original failures,
private results and guard AST comparison are retained in the raw subfolders.
Installed loader inputs were copied read-only with exact hashes. Two prior target
artifacts were placed/hash-checked in a fresh board Linux input directory; neither
operation touches the MCU. Tool transfer is separately recorded.

Next is P2_ui_adc_probe_run01_plan.md: commit this completed software, final bound
run review, one identified upload and one passive collection, then actual evidence
review. Bare ADC readings cannot prove physical buttons, calibrated clock/voltage,
SC-A/SC-AJ closure, full-app timing, sensors/motors or a phase gate.
