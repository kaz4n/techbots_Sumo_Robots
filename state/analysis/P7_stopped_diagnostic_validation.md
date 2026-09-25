# D161 actual stopped-state diagnosis

One passive observation at reviewed HEAD1d455be7, 25 September 2026 05:00 Dubai.
The sole ADB command returned0 with empty transport stderr; OpenOCD returned0,
reaped without timeout. Identity and all five remote pins passed before/after;
all independent host source/stage/HEAD/module/ADB checks passed. Exact command
and raw streams are in P7_static_startup_raw/stopped_diagnostic01/intent.json and
invocation.json. Source71507fd8; command27577 UTF16 units. No reset or upload.

Both coordinator and separate same-model reviewer reconstructed the exact
BEFORE/TRANSACTION/INPUT/AFTER labels, contiguous addresses and188 words/752B.
parsed.json retains the reconstructed bytes/hashes and typed D149 fields.
Review: ../reviews/P7_stopped_diagnostic_actual_review.md (c323dc88), scoped PASS.
Both runtime brackets and transaction prefix equal both D160 samples. Ten
coordinator continuity/token/wrap-safe time-order checks pass. This is sampled
prefix stability, not atomicity or uninterrupted MCU/image continuity.

Observed: Robot contract bitmap0x0110 (APPLICATION_CONTRACT + LINE_CONTRACT),
MotorGate IO3, escape fault0. Robot token3/UI STOPPED and zero/disabled commands.
Current application token3 is consumed but invalid; preceding input receipt
also invalid, token2. Previous duration546us and current transaction495us are
valid timing fields, not valid motor acknowledgements or WCET measurements.
D160 max790us remains only a sampled maximum. Missing setup grants independently
prevent initialization; their absence alone would normally leave BOOT.

The failed receipt explains the APPLICATION_CONTRACT path (fsm_robot.cpp:179-195).
MotorGate IO can originate from EN LOW, one of four PWM-zero writes, settle,
or cleanup (motors.cpp:64-80,146-165). UnoQPort stores no first failing callback,
return status or latency, and cleanup changes its masks; this capture cannot
identify the original operation or prove the150us settle bound is too short.
The host native fixture advances simulated time mainly during UIF polling,
so its deadline149/150/151 tests are not native timing evidence. Keep the limit,
existing tests and original failing receipts unchanged.

D161 scope is consumed. Next development task: prepare the smallest inert
MotorGate callback diagnostic using the real native adapter and existing M0
bench path, retaining first-failure operation and bounded timing without changing
production motion policy or limits. Obtain separate scoped review/host checks,
then identify any new bare-board upload explicitly. Do not rerun D160/D161 or
infer physical, production-static, memory, WCET or human-gate acceptance.
