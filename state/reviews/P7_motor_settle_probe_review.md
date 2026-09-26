# D197 native SETTLE observation review

Date: 2026-09-26. Separate same-model reviewer with reused context; local source, contract, oracle and saved-receipt inspection only. No test/compiler invocation, subject import or device action by this reviewer. Only this review was written.

**PASS for the scoped host implementation and controlled validation. No material source or evidence gap remains within D197.** This adds diagnostic branch observation; it neither identifies the D195 native failure's internal cause nor repairs it. Target compilation, retention, ABI/instruction observation and a separately admitted capture remain pending.

## Frozen source and publication

Reviewed contract: `state/analysis/P7_motor_settle_probe_contract.md`, 12,585 bytes / `3346b11970814ce7703c48f56cb38405449453964bb79d1740d5a49e78610f7c`.

| Source | Bytes | SHA-256 |
|---|---:|---|
| `src/hal/motor_port_unoq.cpp` | 19185 | `f1ee755a7bddec38e86545f4c5e5457b3ed5e5f1bdd7f5cf368cc77f91664f5e` |
| `src/hal/motor_settle_probe.h` | 2366 | `2eced554fce20ff938daf44866ee0bad6d99fa28e377af762bb0f037376b75a8` |

All 12 contract starting-point pins were independently checked, using the original committed cpp for its historical pin. The ten existing UnoQPort functions other than `settle` remain text-exact; the diff preserves the other existing native helpers. Config, UnoQPort declaration, Trace, Runner, sketch and locked fixtures remain unchanged. The 150-us and 4,096-poll guards, their comparisons and compound short-circuit ordering are preserved.

The probe is conditional on the existing inert selection. Probe0 excludes the header dependency, diagnostic storage, accessor and helpers. Its return/elapsed macros expand to the original expressions without evaluated diagnostic arguments or empty statements. Independent source-text expansion matched the historical SETTLE body apart from whitespace, and the recorded real-preprocessor comparison also passed.

Probe1 retains each existing unsigned elapsed result once, without new clocks or register observations. The reasons distinguish the existing null/precondition/initial-bank/poll-deadline/poll-bank/final-deadline/poll-limit exits and success. Invalid observations are zero; INITIAL_BANK does not turn the existing start timestamp into an elapsed value. POLL_BANK and POLL_LIMIT retain the earlier loop-top sample; the limit sample reports executed index 4,095, not 4,096. Fresh masks come from the original accumulated flags.

The header's enum, standard-layout assertions, member offsets and 4-byte alignment implement the prescribed 12-byte sample and 28-byte report. One internal ordinary aggregate `settle_probe_report{}` supplies static zero/NONE initialization. Publication explicitly copies all six sample fields through a volatile-qualified reference to that same ordinary object, then sets the corresponding presence flag. Reserved bytes stay zero. Current is replaced at every completed return; the first non-success sample is copied only while `has_failure == 0`, with its flag written after its fields. No later return, factory/accessor call or cleanup clears that slot. The accessor returns the same const reference without mutation, allocation or I/O. New functions are bounded and the SETTLE definition is 33 source lines.

Volatile publication provides observable RAM stores even when application code never calls the accessor. It does not make the report atomic, guarantee a linker-retained accessor, or establish the target address/instruction sequence. Host presence and layout checks must not substitute for the separate optimized target ABI/entry observation.

## Independent oracle and actual outcomes

The original independent freeze was recorded before its author read/imported the new source or executed a test. Final tests retain the unchanged C++ scenario source and all original assertions:

| Oracle | SHA-256 |
|---|---|
| `tests/native_motor_settle_probe_cases.cc` | `0ad263b07585c431edd5199c99f18b775befe6a6be7e95235973dd1e3bc7c93c` |
| `tests/tooling/test_motor_settle_probe.py` | `29c6cac3d837263d7e1a90b2a677dade79915e02970cea53e839933ec502a183` |
| `independent_test_freeze03.json` | `bbf917aaf7479fd0de55259a4e6c229257961e04a11221d0369e6ec9a022370a` |
| `coordinator_freeze03.json` | `07da9bfae646c55940ec5951fb63a40066e0838c85edb89000e14e4c3b45b31b` |

Freeze/receipt paths are under `state/analysis/P7_motor_settle_probe_raw/`. I independently rehashed all 140 final coordinator pins: no mismatch. Subject hashes in all final command receipts agree with the reviewed source. Saved stdout/stderr hashes agree with each outer invocation receipt, including both preserved failures.

Final `probe_corrected_linux02` exited 0: all five methods passed without skips, 8.986 seconds of unittest execution / 16.808 seconds outer elapsed. Its 86 command receipts include only the four intended negative-compilation exits; these now reach the absent accessor and all three original inert configuration guards.

The 21 fresh-process scenarios run against the frozen original, current probe0 and current probe1: 63 successful scenario executions. I checked every trio of receipt lengths/hashes for equality. The oracle compares full transcript bytes in RAM and rejects fixture trace truncation; compact hashes are retained, rather than all transcript bodies. It compares bool results, complete ordered fixture calls, forwarded original clock values, native object size, mapped register bytes and relevant final fixture state. The two exhaustion transcripts each exceed 513 KB and still participate in exact comparison.

Coverage includes all eight return outcomes, each compound-precondition position, initial and per-poll bank failures, 149/150/151 final boundaries, unsigned clock wrap, loop-top timeout, a frozen clock through 4,096 polls, zero/partial fresh masks and last-sample validity. Probe1 independently checks the complete report bytes, zero defaults/reserved fields, enum/layout constants, stable const accessor, no allocation and first-failure retention across later failure, success, repeated factory calls, actual MotorGate failed-apply cleanup and final/repeated halt. Preprocessed probe0 equality, original/probe0 defined-symbol equality and probe1-only report/accessor presence passed.

The separate unchanged locked native driver also exited 0: both selected disabled and host-only-enabled methods passed, each running all 38 cases without skips, totaling 76 case executions and 217,020 assertions. This was the two full contract suites, not a claim that every metadata variant in that driver ran. These tests use synthetic Linux register mappings and UBSan; they provide no physical motor or target timing evidence.

## Preserved fixture failures

1. `probe_first_linux01` stopped at `link-original` with zero methods run: the new harness omitted `src/core/opp_fusion.cpp`, which defines the unchanged `opp_fusion::frontView` referenced by unchanged MotorGate code. Current probe implementation had not compiled. The sole first repair added that unchanged translation unit to all three variants' shared link inputs and pinned its hash. Original oracle `8d8f9e82...` and failure were preserved at `c7fa1679`.
2. `probe_corrected_linux01` passed the differential, preprocessor, symbol and protected-file methods but failed its exclusion fixture. The probe0-only header correctly declared no `motors` namespace, so the compiler rejected that namespace before mentioning the requested accessor. The sole second repair included unchanged `hal/motor_port_unoq.h` in the accessor-use snippet, supplying the real namespace while retaining every assertion. Oracle `451762cf...` and this failure were preserved at `a0ccf86d`. The three inert guard checks were reached and passed only in the final corrected run.

Both repairs were independently adjudicated against the actual errors and narrow diffs. Neither changes product source, expected report values, contract requirements or an old/locked test. C++ scenario bytes and implementation hashes stayed fixed through all attempts.

## Compact receipt anchors

| Relative receipt | SHA-256 |
|---|---|
| `probe_first_linux01/result.json` | `b131a115807c5e06bc56858558642501fa2b39d04f12c1e2cc155765f0a84234` |
| `probe_corrected_linux01/result.json` | `ae783c6c147753efb902e20d53d2a9386c6cf462c9a650b325c54f11a90b2cd5` |
| `probe_corrected_linux02/result.json` | `f74eb20c0d6117d000d0cc67f0f170862c9fd147662a382b91b45fddda51ad1f` |
| `probe_corrected_linux02/stdout` | `1050eedc1099069848cd39bebbc9325b49c1cae38e6fc8983e7bc70182222552` |
| `probe_corrected_linux02/stderr` | `c0f473e43bf3bd11223c80d4bd18e2eb8acb5508cd5648450c09bccc5a75d44d` |
| `locked_first_linux01/result.json` | `e9381334ca077df0613a0a28654fa08e20167b6ca0806eb98fddfa525a696678` |

Later target work needs fresh source/artifact/ABI/report-window bindings and ownership. Instrumentation can perturb timing even with unchanged native-call counts. No limit relaxation, native-cause diagnosis, production-static adoption, WCET qualification, physical acceptance, motor permission or phase gate follows from this host PASS.
