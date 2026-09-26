# D207 actual inhibited diagnostic and retrieved-byte review

Status: PASS for this single bounded inhibited diagnostic, its collection/retrieval integrity and the stated observed outcome. No open material finding. The observer completed successful begin and reached its planned 10000-epoch limit without a recorded callback or SETTLE failure, then deliberately aborted and obtained a callback-level inhibition acknowledgement. This does not establish an intermittent-fault cure, complete peripheral initialization, full robot WCET, measured pins, powered motion safety or a human phase gate.

This separate reviewer used local saved-file reads, hashes, strict JSON/base64 parsing, static source inspection and an independent little-endian unpacker written for the review. Neither the production decoder nor any other subject/oracle was imported or executed. No test, compiler, device, authentication, upload/reset, MCU read or cleanup was performed. Only this new final review file is owned. Earlier final reviews, failed attempts and other contributors' files remain preserved.

## Exact evidence

`RAW` means `state/analysis/P7_motor_const_run_raw`.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `RAW/native_invocation01.json` | 1204 | `60438286944f1486edafb0252a5dfc76c439b968f17c62c265fbe74b4026d0c8` |
| `RAW/native_inert_run01/inputs.json` | 18581 | `8a85e481dc14b2f68b7ba39575689649e579af05bb14b780aa7d3a47adcca7b3` |
| `RAW/native_inert_run01/result.json` | 58692 | `860338ea10ab47c5c8cef9942fa0fa084b35ae79f0bc833fbc3b0396d0dac409` |
| `RAW/native_inert_run01/final_checks.json` | 49963 | `d85afb00fbc8d26d5ae24f7f8d89a7a436598cc1050a1f42b9ac99740ff519c1` |
| `RAW/native_actual_closing01.json` | 37633 | `b936b2396b1eace5991402c5041a177e4dcdd435cf731c6888a6e93ee7937631` |
| `RAW/retrieved_inert_run01/0001-read-saved-results/stdout` | 27525 | `4a9355808c4136c067b37426cb5904c17eeb061f8f386cd541a6dd89d2bc065d` |
| `RAW/retrieved_inert_run01/decoded.json` | 81223 | `7d10f606290355cadfdc258b1ac3b2b2f587e0d652f309107957ec789092a01c` |

The clean reviewed HEAD was `676e3625830b64d99309d6d03fba05ca24ea99fe`. Scope remains 1875 bytes / `23c1fcf6ddb371d5e7c641bab67b78c927ac541b4090cc390942de90bd86f700`. Source is `4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`; run is `app-motor-const-4bc3a2e6-run01`; serial is `2629958581`. The accepted admission, source/host and field-map reviews remain the prerequisites already recorded for this scope.

## One-shot sequence and closure

The outer receipt records local check-only return zero in 1.3847728999098763 seconds, followed by exactly one execute call at `2026-09-26T14:33:37.617945+04:00`, returning zero in 280.34023530001286 seconds with empty outer stdout/stderr. The sequence is COMPLETED with one upload, one capture, null first error and empty closing/error lists. Its diagnostics exactly equal `final_checks.json`.

All thirteen transport owners were independently checked against their complete intent/result pairs. Their actual argv hashes, native argv hashes where applicable, Windows UTF-16 lengths, exact role timeouts, zero return codes and empty stderr agree with the seven declared command roles. Ordered dispatch is claim, push, three prerequisites, upload, three prerequisites, capture, three prerequisites. Role counts are claim/push/upload/capture once each and CLI-initialization/CLI-builtin-files/capabilities three times each. The adapter claim is verified, intent/stage readiness is true and action intent/dispatched sets are exactly upload and capture. Upload/capture stdout JSON objects equal the sequence's returned action envelopes, and the capture predecessor SHA-256 matches the canonical accepted upload envelope.

All 44 saved Git operations succeed without stderr: eleven HEAD reads, eleven committed-scope reads and twenty-two status checks. They retain the exact reviewed HEAD and scope. Tracked status stays clean; every later untracked status entry is confined to the claimed native evidence owner. All 160 recorded native input hashes independently match current files. The exact scope/provenance/source and host-freeze pins remain unchanged; the 302 native and 184 interpreter coordinator pins were rechecked after retrieval.

The three payloads in each prerequisite family are byte-identical. They retain expected Arduino UID/GID/boot, installed-file inventories and the exact staged adapter. Adapter claim reports no process conflict and 13914370048 available bytes. Capability source files match all 108 mapped source entries and 781200 bytes from the accepted D203 mapping; no extra mapped file appears. The 129-source-pin manifest and twelve provenance roles remain bound by the unchanged native inputs. All 58 native evidence files and their total 628773 logical bytes match the separate closing inventory. The closing audit is a data/transport audit; this review supplies the additional retrieved-content and firmware-semantics acceptance.

The uploaded artifact remains the accepted static/default-startup diagnostic, MATCH=0, MOTORS_ALLOWED=0 and SUMOX_MOTOR_FAULT_PROBE=1. Packaged sketch is 95368 bytes / `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7`; raw sketch is 95352 bytes / `76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3`. Pins, setup grants, 150 us deadline, 4096-poll bound and observation limits are unchanged. No motion authorization follows.

## Collection and saved-file retrieval

The upload child is successful, reaped and not timed out. Upload elapsed is 12.767898703998071 seconds. Capture is COLLECTED with exactly 26 ordered reads and 727128 requested bytes; every name/address/width/indexed basename matches the fixed plan. Twelve snapshot rows exactly equal reads 7 through 18. All four native whole-image comparison flags are true, and all seven corresponding before/after flash-chunk digests match. Capture elapsed is 251.21928558399668 seconds, below its 600-second bound. The initial wait is 30.000404480000725 seconds; the sample gap is 2.0003971219994128 seconds, ordered within the capture interval after successful initial flash brackets.

These full-flash comparison conclusions come from the reviewed native capture path and its saved report. The local retrieval deliberately excludes flash-chunk bodies; this review does not claim a second independent local whole-flash reconstruction.

The separately reviewed file-only retrieval intent is 22792 bytes / `be2690956319fb1d567e56d2f2468bf8408a36c0e9dc7f3dd1a3fc937889f276`; its preparation review is 10235 bytes / `c7eafdb31059e6948b58285a23c2aa12929ea95181a22cb80df1b76669e8cd3b`. The actual saved intent equals those exact bytes. One call at `2026-09-26T14:41:49.292990+04:00` returned zero in 0.43468149995896965 seconds with empty stderr, no changed inputs and a 75-second bound. All intent pins and review hashes match.

The packet has exactly the five expected keys and status FILE_ONLY_RESULTS_VERIFIED; complete before/after identities equal the admitted identity. Fourteen unique files were retrieved and all fourteen closing rereads succeeded. Their paths, lengths and hashes equal the literal reviewed pin list. Canonical base64 decoding independently verifies every body: 1903 upload-result bytes, 7100 capture-result bytes and 9032 SRAM bytes, totaling 18035 bytes. Full upload/capture reports equal the action-envelope report data, with the upload's preserved stdout/stderr fields restored. The upload stdout is 1368 bytes and stderr empty. No returned/outward error is hidden by a durable unattributed result.

The full result hashes are upload `c0e9d53fb5171e58412eb4515e63b1dbb0068d6a81fe5a9e68e587bcc8496a02` and capture `9b879b418ad996a371e184b107b29617ce8cad0c189b7bbbb1427e34f80a1fd0`. All receipt identities, statuses, counts, error shapes and nested fixed fields agree with the native envelopes and decoded output. Original bytes remain intact. This retrieval made no fresh MCU read, reset or upload.

## Independent raw decoding

The selected current field map remains 16755 bytes / `ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709`; corrected interpreter remains 31259 bytes / `d96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab`. Their source/host review is unchanged. The coordinator used the explicit retrieved packet hash for the offline decoder; the saved output is DECODED with no structural error and coherence UNPROVEN.

Without invoking that implementation, the reviewer independently unpacked every selected field from all twelve raw bodies using explicit little-endian scalar formats, the reviewed observed offsets, nested aliases and fixed arrays. All 2034 scalar leaves match the saved decoded windows, including all 64 trace slots per sample, booleans, floating values, nested pre-abort state and every reserved/loss field. Binary booleans and finite floats were checked. Every verified-file record and both full receipts match their original bodies. All six first/second region pairs are independently byte-identical as well as equal after decoding. This repeated equality does not prove atomic publication or cross-window coherence.

## Observed firmware behavior and its limits

Both reports show observer phase 4/FROZEN and reason 6/EPOCH_LIMIT. Begin called/finished/ok, before-abort-valid, abort-called/returned and last-step-returned are true. Poll count is 1470524, below the unchanged 10000000-poll bound. The before-abort runtime is phase 1/RUNNING, fault 0/NONE, fresh true, epochs 10000, service passes zero, missed releases zero and maximum_execution_us 519.

The pre-abort transaction is phase 1/IDLE, fault NONE, decision made/finished/timing valid, token 10000 and execution 500 us (`10426265` to `10426765`). Its applied receipt is consumed, fault-free and valid with motor enable false and both duties zero; the retained previous tick separately carries completed/duration-valid timing for the same token. The robot outputs retain `ui_state=0/BOOT`, not core IDLE. Countdown go and motion permission are false; contract and escape faults are zero. Application transaction IDLE is distinct from the core UI state.

Runtime `initialization_complete` is false. Source `Runner::begin` passes `app::SetupGrants{}`; the peripheral/service grants remain absent. `Runtime::project` requires the granted source readiness, valid ADC/buttons/opponents and line conditions before latching full initialization. Successful MotorGate/runtime begin and repeated inhibited epochs therefore do not establish initialized sensors or match readiness. The core remaining BOOT is consistent with this boundary.

The saved pre-abort snapshot is taken before `Runner::freeze` changes trace context to HALT and calls `Runtime::abort`. Source inspection confirms that abort intentionally routes through Runtime fault TRANSACTION, Transaction fault ABORTED and MotorGate halt. Consequently the current live windows show Runtime phase 3/FAULT and fault 4/TRANSACTION; Transaction phase 4/FAULT and fault 6/ABORTED; Gate fault 6/STOPPED. These terminal codes do not overwrite the prior RUNNING/no-fault snapshot or indicate that a callback failure caused the stop. The current applied-valid acknowledgement is withdrawn by the abort path as required.

The halt receipt is fresh, attempted, timing-valid and `inhibition_confirmed=true`, started at 10426813 us and completed at 10427029 us, a 216 us interval. Gate is initialized, began, halted and unarmed, with hold-complete false and last token 10000. Transaction and gate halt receipts agree. The flag is the native callback acknowledgement defined in `motors.h`; it is not a voltage/pin measurement or powered motor test.

SETTLE current is present, reason 1/SUCCESS, elapsed 116 us, poll index 10, fresh mask 7 and validity 7; all reserved fields are zero. There is no lifetime first failure: has_failure is zero and the absent first-failure sample is zero/NONE with validity zero. Independently checked annotations correctly mark current CONSISTENT with all three values available, first failure ABSENT/UNAVAILABLE, and no issues. The 116 us value belongs to the most recent final-HALT SETTLE, not initial setup and not a run-wide maximum.

The trace current call is HALT stage 2, SETTLE operation 4, application 10000, invoked/completed/returned/timing-valid, from 10426906 to 10427027 us: 121 us including the wrapper, distinct from the 116 us internal probe. The retained initial-setup SETTLE call also returned true; its wrapper interval is 102 us. No false-return or trace timing fault is recorded, and the lifetime first-failure slot is absent/zero.

The trace retains exactly 64 completed calls: eleven setup and 53 application calls, ending during application 9. Every stored call is invoked, completed, returned true and timing-valid; all requested enable levels are low and all stored PWM pulses zero. Overflow is true, rejected is 59953 and clock_reads is 1680566. Thus 60017 completed calls are accounted for by prefix plus rejected count, but 59953 later call records are unavailable. Current and first-failure latches are maintained separately by the inspected trace source. This is explicitly not a complete per-call history, and the overflow is not erased or reclassified as zero loss.

## Comparison and disposition

The retained D201 decoded evidence shows SETUP_FAILED, unsuccessful begin, zero epochs and first FINAL_DEADLINE at 154 us/poll 5/fresh 7, followed by a separate later current success at 132 us. D207 instead reached its fixed epoch limit and retained no lifetime SETTLE failure. That is a successful finite observation of the current image, not proof that all intermittent failures are eliminated or a statistical timing claim. The observed 519 us maximum applies to this inhibited run with absent peripheral grants; it is not full-source robot WCET qualification. Live RAM/stack, sensor readiness, physical outputs and phase gates remain unqualified.

The coordinator's actual-validation prose was reviewed. Two requested wording corrections were applied before closure: output `ui_state` is BOOT rather than IDLE, and halt inhibition is explicitly a callback acknowledgement rather than a pin measurement. No source, raw evidence, test or native retry changed. No material disagreement remains.

Accept this one consumed native attempt and its one consumed saved-file retrieval. D207 is now the latest verified flashed inhibited diagnostic; D195/D201 failures remain evidence. No second diagnostic attempt, cleanup, motion-capable upload or changed safety threshold is authorized by this review. Further ordinary-application preparation requires its own defined scope. Coherence remains UNPROVEN, and no human physical/competition gate is passed here.

Final review; STOPPED WRITES after recording this file's external hash.
