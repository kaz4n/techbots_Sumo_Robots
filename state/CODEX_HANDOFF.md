# Codex handoff - 26 September 2026, Asia/Dubai

## Current board result

D201 completed and independently reviewed. Latest flashed image is D198 source
117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da,
static/default/MATCH0/MOTORS_ALLOWED0/probe1, package95520B/e4000781. Read
analysis/P7_motor_settle_run_validation.md and reviews/P7_motor_settle_actual_review.md.

At clean ff35c83e, check-only/execute0, one upload/one capture/13 transports,
26 reads727432B,30s+2s waits and four full flash comparisons passed. Native
resultfb529423; file-only14-file retrieval17954B/e32415b2; decoded4d8383c3.
Review690a4164 independently checked2034 scalar instances, all source/input
pins and six identical raw pairs. Coherence remains UNPROVEN.

Observer FROZEN/SETUP_FAILED, begin_ok=false, zero epochs and polls. The lifetime
first SETTLE failure is FINAL_DEADLINE7, elapsed154us, poll5, fresh7, valid7.
Current is SUCCESS1,132us,poll4,fresh7,valid7. Both samples present, reserved0.
All17 trace calls are SETUP/application0: firstSETTLEfalse index10/159us outer,
then EN-low/fourzeroPWMwrites/SETTLEtrue index16/137us outer. This is setup
inhibit cleanup, not HALT. Gate uninitialized/IO, runtime TRANSACTION fault;
both stored HALT receipts are unattempted with inhibition_confirmed=false.
No control epoch ran, so stored maximum0 is not a measured WCET. No safety
limit, pin, grant or configuration changed.

D195's distinct source3a08ddeb observation at921epochs remains historical;
its APPLY/SETTLE154us outer and failedHALT do not identify an internal branch.
D201 does not automatically explain that earlier run or prove physical cause.

## Exact next task

D202 is adopted in DECISIONS.md under D051. Contract:
analysis/P7_motor_expected_metadata_contract.md (6222B, SHA2abaae2995e1938e4c7f0dcef2522c9334d9550bd77d9da37727b47a7940a846).
Only replace the candidateRate/candidatePeriod calculation region in
src/hal/motor_port_unoq.cpp. Predecessor19185B/f1ee755a is available at ff35c83e.
Use exact original math in constexpr expectedRate/expectedPeriod and three
mandatory constexpr scalar results selected by the existing runtime functions.
All bytes outside this region, native observations/order/count, SETTLE body,
150us/4096 bounds, configuration and historical/locked tests stay unchanged.

The emitted predecessor has runtime64-bit division dispatches in candidateRate
(08110cca/08110cd8) and candidatePeriod(08110d0c), seen in saved D199 entry
result10d8a184 commands[3]. This supports investigating constant evaluation,
not a measured speedup. No new production edit or test execution had occurred
when this handoff was written. An independent oracle is being authored without
new-implementation access. Preserve its freeze before any test execution.

Run independent metadata/native transcript checks and unchanged locked suites,
serially, retaining first failures. Also run unchanged D197 oracle; its complete
symbol equality might expose legitimately removed immutable metadata storage.
Do not alter/filter that assertion or force artificial symbols. Record and
review any difference before proceeding. No target optimization benefit is
established until a new fixed compile, actual ABI/entry and separately reviewed
inhibited runtime attempt. All prior native owners are consumed; do not rerun
historical launchers, reset the MCU casually or repin old manifests.

## Evidence prerequisites already complete

D197 probe report implementation/host validation; D198 actual static compile;
D199 actual ABI and entry inspection; D200 exact stale-copy cleanup; D201 host
and actual collection are complete. Relevant analysis/reviews share the
P7_motor_settle prefix. Report is separate28B at2003d3e8 for this exact image;
never reuse that address for changed artifacts without fresh observation.
D201 host:99Linux native methods,56Windows/43coveredLinuxskips. Decoder first
failures retained b69cc011; three bounded implementation fixes and one portable
fixture correction pass67methods on each platform. No locked test was edited.

## Larger project work

Objective remains complete SumoX-26 software and release preparation. Active
phase P7; physical/human P0-P5 and P7 release remain open. See
analysis/P7_completion_audit_20260926.md. After native fault work, prepare the
current ordinary probe0 app static build from
analysis/P7_current_app_static_followup.md. Historical layouts are not current
production memory/stack or loading evidence. Existing ordinary app.ino already
binds Runtime/configured grants/native DumpPort; operational B4 needs profile/
build/deploy admission, not another entry. Its terminal STOP cannot use current
IDLE-only UART dumping; preserve reset refusal and use separately bound retained
RAM evidence or a reviewed new service policy. Native UART ownership/cancel/
reopen, recorder rearm, production WCET and SC-AP release still need work.

## Safety, cleanup and schedule

No STAND OK, RING OK, PINMAP OK or human phase gate exists. No motor-capable
flash/run. Header IO remains3.3V; D051/D075/D122/D137 permit software progress,
not manufactured physical facts. D121 B7/R6 remains protected.

D200 root04 completed once, precisely3 staleD195 copies2399768B removed and
retained originals verified; no retry. D201 may have produced fresh uploader
scratch: any next cleanup requires new exact observation/binding/use checks.
Credentials were stdin-only and are not retained. Never revisit prior denied
cleanup targets (old85.48MB hostbatch,37stagefolders, motor-fault stages,
build/stage/app and2Binput.wire), userfiles or Git history. C: had about20.5GB
free before D201; recheck before large work. Keep unique evidence, avoid duplicate
ELFs/source snapshots, use Python-B and one compiler at a time.

If actual P3 gate is absent by end28September, cut to reactive+SIDESTEP/DIRECT
and recorder; drop ARC/WAIT/P6. P6 also requires actual P4 by30September.
Freeze1October21:00Dubai, rehearsal2October, competition3October. Dates do not
create acceptance. Read AGENTS.md/CODEX_RESUME/CODEX_EXECUTION and latest state.
PROGRESS is binary-append-only: first140971B SHA256
1dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77.
No native process or execution session remains active at this checkpoint.
