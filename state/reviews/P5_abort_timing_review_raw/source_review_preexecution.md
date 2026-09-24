# D135 source review before first validation results

Scope: production diff after D134 host closure d6a8319e, adopted D135 contract,
previously frozen private13, public test transfer and checked build route. Same
fresh-context reviewer continued after the oracle freeze; no compiler run here.

## Findings and disposition

No open material implementation finding from this source pass. This is a source
review disposition, not a test, ABI, native-fit or physical acceptance result.

An unexecuted draft-oracle discrepancy is recorded without changing the oracle:
private_spec_probes.cc's prior-receipt/current-STOP case requires APPLIED to be
events[0]; tests/test_abort_runtime.cc:87 has a similar requirement. Existing
fsm_robot.cpp:181-196 may first emit FIRST_NONZERO_DUTY from the same prior
receipt. D135 requires receipt result before current-decision events, not before
other prior-receipt events. Preserve first execution and obtain separate author
adjudication before any narrowly scoped new-draft repair. This is not grounds to
reorder production or weaken an established protected test.

## Source evidence

| Obligation | Reviewed source and conclusion |
|---|---|
|Actual predicate before terminal mutation|openers.cpp:42-83 DIRECT captures current/snapshot/deadline cause before exit; 218-258 Flank captures phase after detectExit and before finish; terminal motion advancement captures pre-terminal phase; 326-368 WAIT clears old pulse and preserves delegated result.|
|Cause and mirrored phase table|openers.cpp detectExit/currentTarget and unchanged B12 phase progression agree with the adopted numeric table; logframe.cpp:226-267 validates it independently from motion evaluation. The frozen exhaustive numeric oracle remains the dynamic check.|
|Independent actual route observation|fsm_robot.cpp:578-618 captures evidence before exit tests, then marks only after the existing routeNormal(true). fsm_opener_timing.cpp:19-28 stores the current request token, not an emitted-cue success assumption.|
|Transient token scope|fsm.h:617-621 puts abort_token in conditional Tick. fsm_robot.cpp:134 clears Tick each admitted observation; exhaustion also clears Tick. This is the permitted current-tick route marker, not another cross-tick trace owner.|
|Same token and final state|fsm_opener_timing.cpp:67-73 checks route fact/token and final tick-selected state; shipped centered threshold3 gives TRACK; threshold1 accepts ATTACK only with centered production observation. No routing or threshold is changed.|
|Exact pending owner|fsm_robot.cpp:1038-1054 captures the exact result token/request/D/T into existing Pending and sets its tag only for same-token routed handover; failed tag closes INVALID_RECEIPT. No extra persistent timestamps/read interval/token are introduced.|
|Full token and actual duty acknowledgement|fsm_robot.cpp:169-177 retains uint64 equality, permission/sign/downward-quantization rules; fsm_opener_timing.cpp:30-45 requires coupled RECEIPT/tag, actual admitted receipt, duration/chronology, full equality and M1 enabled acknowledgement before APPLIED. M0 zero is allowed.|
|Coupled consume before replacement|receiveOpenerTiming clears tag and closes phase before receive clears pending.valid at fsm_robot.cpp:200. Missing pending still invokes it at161-167. The public pipeline always receives before final savePending.|
|Common-anchor source chronology|fsm_opener_timing.cpp:48-56 needs sampled fresh perception, valid prior complete chronology, explicit epoch/start and complete read interval within T..D below half-range. Runtime inputs resets projection first and only exposes actual source bounds after opponentsFresh (runtime_inputs.cpp:38-49,115-134).|
|Common-anchor receipt chronology|fsm_robot.cpp:211-230 orders pending T/D/A/C/current T/D under one unsigned anchor and checks execution==C-T. D135 also requires duration_valid, explicit mode, current valid start and admitted application. Actual A is emitted without capping elapsed time.|
|Trace classification priority|fsm_opener_timing.cpp:76-109 orders source invalidity, actual edge/escape fault, STOP/fault/lost permission, snapshot/natural then qualified handover validation. A captured cue is emitted before final preemption. No raw-white/contact/positive-duty policy is imported.|
|No replay or repair|publish acts only in WAITING; terminal paths close once. RECEIPT success/failure closes before current sampling. beginAttempt resets only at accepted START; reset clears state without a receipt. Immediate duplicate Robot calls clear pulses and do not consume.|
|Exhaustion/reset/tail|fsm_robot.cpp:1099-1144 receives prior pending before exhaustion diagnostics, then closes still-open post-GO trace as STOP_FAULT and returns no new valid token. Reset preserves monotonic token but creates no acknowledgement. Transaction abort uses existing recorder reset notification and halt, not a Robot tick.|
|Append and loss discipline|fsm_opener_timing.cpp emits every specified read/cue/handover append without short circuit. appendEvent/emit retain prefix and recording loss. HEADER follows START_RELEASE. P5 capacity remains21; P4 alone26. Public recording tests separately exercise synthetic loss propagation, correctly not claiming actual producer saturation.|
|Default/P4 noninterference|all new fields/pulses/owner calls are P5 conditional, new profile constant has no object storage, P4 codec branch remains exact, runtime projection ORs only the exclusive P5 guard. Minor brace/temporary-result refactoring leaves ordinary opener branches equivalent. Measured ABI/regressions remain required.|
|No motion authority or I/O|new core helpers only copy/compare fixed values and append bounded events. MotorGate/governor/source admission retain prior production paths. No new allocation, clock, remote interface or I/O was introduced.|
|Native wrapper and admission|opener_timing.ino uses NativeSources/UnoQPort/Runtime and empty SetupGrants. Exact exclusive M0/MATCH0 static guard, board_tool.py:443-465 rejects uploads/MATCH/Immediate before I/O, build_flags supplies literal P5 flag, app_build_policy.py:107-111 requires exact project/profile/default FQBN. Current wrapper has no source macro override; existing YAML/local-reserved-source and platform/build override rejection remain.|
|Host integration|CMakeLists.txt:243-264 uses the existing B4_HOST_SOURCES production objects/genuine motor_gate_main, six dedicated .cc test sources, M0/M1 P5-only definitions. Default/P4 sources gain only an inactive translation unit.|

## Boundaries of this review

Internal missing-route, wrong final-state, cue-token mismatch, lost or replaced
pending/tag, phase-tag mismatch and uint64 exhaustion are source-reviewed here.
They are not claimed dynamically covered by ordinary success. Frozen public APIs
have no legitimate setter for these faults; bounded isolated mutation testing
may strengthen the claim without changing production seams.

Source inspection establishes that current checked wrapper has no macro-local
override. It does not make arbitrary changed source immune to deliberate #undef
edits; checked artifacts must stay source/hash bound. No new generalized source
scanner or security claim is inferred from the ordinary build policy.

Later execution must distinguish plain profile tests from configured Runtime
tests guarded by APP_TEST_CONFIGURED_BUTTONS. Default/P4 layout and object-copy
costs require measured ABI output. Shared recording capacities/cadence are
unchanged; physical load, stack/static RAM/ELF/import/loader fit, actual clock
qualification, WCET and10/10 trials remain pending. D134 native fit results cannot
qualify this larger P5 artifact.

## Private runner

run_private.py adapts the established D134 linking approach. It accepts source,
build and unique label; verifies the exact original13 private source and original
expectations; reads existing target flags/link lines; removes exactly the six
public .cc test objects; retains genuine main and fsm_opener_timing; records all
retained object SHA256 hashes; compiles just the frozen private source, links and
runs M0 then M1 serially. It never rebuilds production implicitly or overwrites a
receipt label. This reviewer prepared but did not execute it.
