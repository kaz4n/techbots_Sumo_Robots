# P1 independent START routing test author

Date: 2026-09-23, Asia/Dubai. P1 host-only under D-016.

Objective: protect public contract 322ecce and D-057 while preserving B3/R1,
D-019/D-024/D-035 behavior. Owned files are
`tests/locked/test_start_routing.cpp` and this report. Expectations derive from
BEHAVIOR, approved decisions, public countdown.h/config and established test
conventions. No core implementation cpp was inspected. No existing locked test,
header, config, build file or shared ledger was changed, and no build, hardware
operation or commit was performed by this author.

Twenty-four cases cover all combinations of selector before qualification and
at the qualified release, suppression without replay, a fresh qualified press to
rearm, boot-held START, short/interrupted debounce, and delayed release timestamps.
Literal 20 ms debounce and complete 5.1 s hold boundaries remain independent of
configuration-derived arithmetic. False preserves an accepted hold and READY;
it is neither cancellation nor an emergency inhibit.

Controller and Lifecycle default arguments are compared with explicit true over
ordinary release/calibration/GO/STOP traces. These are compatibility compositions,
supplemented by literal state/permission expectations in the boundary cases.
MODE/BOTH cancellation at the exact GO boundary, full logical BOTH qualification
and long hold, external STOP priority, reset and STOP retention remain exercised
while match routing is disabled. The input snapshot may expose a qualified START
on the same observation that STOP rejects its use; no service action is inferred.

Const snapshot reads, copied-return modification, repeated reads, duplicate step
timestamps, next-observation pulse clearing, reset emptiness, edge timestamps and
qualification timestamps are checked for both public compositions. Snapshot reads
do not resample input or turn a suppressed pulse into an accepted match release.

Lifecycle cases distinguish ignored NaN/infinite previous bias on suppressed
releases from diagnostic failure on a real new attempt. Existing calibration,
warning/snapshot windows and GO proceed with routing false; cancellation occurs
before the current service sample. Prior bias survives cancellation and a later
suppressed release. A second suppressed qualified release exactly at the original
GO time remains visible in buttonEvents while Gate emits only the original GO,
keeps its original release timestamp, and preserves the calibration mean/count.
Heading reset is a one-shot GO request. Post-GO STOP retains completed diagnostics.
Wrapped and delayed qualification streams exercise both Controller and Lifecycle.

Static handoff: 24 cases; longest test block is 32 lines; CHECK/CHECK_FALSE only;
no throwing checks, trailing whitespace or diff-check errors. Tests are frozen
for coordinator review and full normal/sanitizer validation. Runtime validation
is pending; preserve these independent expectations on failure. Once established,
the new locked cases inherit AGENTS human-approval protection.

Limits: logical inputs do not establish A1 electrical decoding, fresh physical
sensor data, actual HAL bias/heading application, MotorGate/EN/PWM writes, menu
service dispatch, full Robot arbitration, real-time performance or a phase gate.
No motor authorization is implied. Next action: coordinator builds/reviews and
records the measured test evidence before committing.
