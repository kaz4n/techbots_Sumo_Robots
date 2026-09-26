# D201 actual inhibited SETTLE observation review

Reviewed 2026-09-26, after the single native attempt at clean HEAD
`ff35c83e6d21d299dac14eb6fc5570d173a7772d`.

Disposition: **PASS_ACTUAL_EVIDENCE_REVIEW; OBSERVED_SETUP_FAILURE**. The upload,
capture, retrieval and selected-field interpretation have no open material
integrity finding. The application did not initialize: the observer is FROZEN /
SETUP_FAILED before any epoch. This is useful negative runtime evidence, not
runtime acceptance, a motor grant, an electrical measurement or a phase gate.

## Scope and evidence identity

This is a separate actual-result review following the already frozen caller,
remote, scope and interpreter reviews. I made only local read/hash/JSON/Base64
and independent ABI-unpacking checks. I did not import or execute the subject,
run tests, access the board, issue ADB/OpenOCD commands, reset, retry, clean up,
change firmware, or alter prior reviews. Only this new review file is owned.

Run: `app-motor-settle-117cc0e7-run01`; firmware source digest
`117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`.
Board `2629958581`, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.
The exact admitted identity is arduino / uid 1000 / gid 1000 / home
`/home/arduino`, Linux `6.16.7-g0dd6551ae96b`, aarch64, Python 3.13.5.

Paths below are relative to `state/analysis/P7_motor_settle_run_raw/` unless
otherwise specified. SHA values are SHA-256 of exact file bytes.

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_inert_run01/result.json` | 58982 | `fb52942391a5d96c1370cd216fe97933e5d0454302be0754c0bcd4a21d4ec1bc` |
| `native_invocations01.json` | 586 | `c6558b2b64ff30e919c0da78fe1b8666c35249ae9dd011aed8072af58ffd633a` |
| `retrieved_inert_run01/0001-read-saved-results/stdout` | 27427 | `e32415b2ec6ea05f3056a68c116f71a2e502f9f815cfb7675d0a57c6b505860a` |
| `retrieved_inert_run01/decoded.json` | 80149 | `4d8383c3ceb7b0b02211e4933a1141e88d2bc65a336d3ffccd707d2040e6267e` |
| `decode_invocation01.json` | 417 | `18a029f9b53a4e1520318c6e83db07aa155c10fbc37558fab89a9623809a3336` |

The exact scope is 1880 bytes /
`1e1b1b589bfb7b0fa956829970dc49c5cc11d5a1c481496a051ed7688b749738`;
preparation is 10008 bytes /
`c37e9a78b10e08c4e90f2f47245a856ca8e2eee6d1027d96e766c7029b010084`.
I rehashed all 160 actual native input pins, all 11 scope pins, all 12 preparation
provenance pins, all 256 native coordinator-freeze pins and all 16 corrected
interpreter-freeze pins. All remain exact at review. These sets overlap; their
counts are not an assertion of that many distinct files. The prior source,
contracts, independent oracles, first host failures and bounded corrections
remain preserved. The scope remains the reviewed static/default-startup image,
MATCH=0, MOTORS_ALLOWED=0, probe=1, with empty application SetupGrants.

## Native lifecycle and file retrieval

The saved invocation receipts report check-only exit 0 and one execute completion
exit 0, both with empty output. The result is COMPLETED, upload_attempts=1,
capture_attempts=1, first_error=null and postcheck_errors=[]. The 13 transport
directories match their intents exactly: one adapter claim, one adapter push,
three each of CLI initialization, builtin-file check and capability check, one
upload and one capture. All have returncode 0 and empty stderr. Recomputed native
argv hashes/UTF-16 lengths and declared timeouts match the saved inputs. Upload
uses 29665 units / 195 seconds; capture uses 28702 units / 630 seconds. The 30000
unit command bound remains respected.

All 44 saved Git observations return successfully. HEAD remains the reviewed
commit, recorded scope bytes match, and status observations contain only the
new native owner paths after initially clean state. The saved final_checks is
exactly the result diagnostics. Staging claim/push readiness is complete; upload
and capture are the only dispatched actions. Local, prerequisite, transport and
finish error lists are empty. The capture-attempt predecessor digest matches
the canonical completed upload envelope; there is no fallback-origin report.

Upload status is UPLOADED, attempts=1, child reaped, returncode=0, timed_out=false.
Its saved full report is 1821 bytes /
`4ad36a019f84f4b5e17b43b64553d5f346bfff1c74433013b4857d5efbf1eba9`.
Capture status is COLLECTED; its full report is 7101 bytes /
`8e9f8417b6c4092294722b213c7a2278b2ae9212b22fbf742fbb1857e20ae773`.
Both exact retrieved reports agree with the native envelopes after the declared
stdout/stderr projection. Transport stdout JSON equals the corresponding saved
envelope, including source, run, result path, size/hash and error fields.

Capture records precisely the fixed 26-read sequence: five loader chunks then
two sketch chunks, six first SRAM windows, six second SRAM windows, two sketch
chunks then five loader chunks. The total requested size is 727432 bytes. Every
address, extent, name and index-prefixed filename matches the fixed plan. The
12 snapshot rows equal reads 7 through 18. Before/after corresponding flash
chunk hashes match and all four complete-span flash flags are true. Loader span
is 263680 bytes; packaged sketch span is 95520 bytes. The reader did not download
these flash bodies, so this review checks the native full-byte comparison
receipts and unchanged implementation, not a fresh local reconstruction of
whole-flash hashes. Capture elapsed time is 251.206309 seconds within its bound;
the recorded first-sample delay is 30.000397 seconds and sample separation delay
is 2.000407 seconds, preserving the requested 30/2-second waits.

The later saved-file reader exits 0, timed_out=false, stderr size 0. I inspected
its actual command without executing it. Its only data collection is fourteen
fixed logical file reads, the same fourteen closing rereads and before/after
identity checks. It contains no MCU read/reset/upload command. Its metadata
exactly matches the fourteen intent pins and admitted identity. Its reader core
hash is `49494df4594ab7c176145c1f3ae1bc63e9c971b0b9f1e0da3e2b60431eca4e5f`;
the decompressed private helper is 33321 bytes /
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
The packet reports FILE_ONLY_RESULTS_VERIFIED and closing_file_checks=14.
All Base64 encodings are canonical, every length/hash matches, paths are unique,
and both full identities match admission. The packet contains 17954 file bytes:
the two reports plus twelve SRAM windows totalling 9032 bytes.

## Independent selected-field reconstruction

The actual-file ABI map is
`state/analysis/P7_motor_settle_compile_raw/abi_static01_decode_fields.json`,
16346 bytes /
`0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd`.
Using standard-library little-endian unpacking independently of the interpreter,
I reconstructed every selected nested field, all 64 trace slots, current and
first-failure slots, and both probe samples in all twelve windows. All 2034
scalar instances equal the saved decoder output. Boolean bytes are canonical
and decoded floats finite. The six first/second raw window bodies are themselves
byte-identical, a stronger local comparison than selected-field equality alone.

The fixed interpreter CLI receipt reports exit 0 with empty output. Decoded
status is DECODED, decode_first_error=null, coherence=UNPROVEN; all six equality
flags are true. Probe annotations are PRESENT/CONSISTENT with no issues. These
are file interpretation results. Identical sequential reads do not create an
atomic multi-window snapshot or prove publication coherence.

The 28-byte probe body is exactly:

`8400000004000000010707009a000000050000000707070001010000`

| Probe slot | elapsed_us | zero-based poll_index | reason | fresh_mask | valid |
| --- | ---: | ---: | --- | ---: | ---: |
| current | 132 | 4 | SUCCESS (1) | 7 | 7 |
| first_failure | 154 | 5 | FINAL_DEADLINE (7) | 7 | 7 |

Both presence flags are 1; all sample/report reserved bytes are 0. The source
enum and native ABI observations agree on these values. Valid=7 marks elapsed,
poll and fresh fields available. The first failure remains preserved despite
the later successful current sample.

## Runtime outcome and trace ordering

Observer phase byte 4 is FROZEN; reason byte 1 is **SETUP_FAILED**, not
BEGIN_FAILED. Begin called/finished are true and begin_ok=false. Before-abort
snapshot valid, abort_called and abort_returned are true; last_step_returned is
false and polls=0. Both selected pre-abort runtime/transaction snapshots equal
their final standalone selected fields. Runtime is FAULT (3) / TRANSACTION (4),
initialization_complete=false, fresh=false, epochs=0 and service_passes=0.
Transaction is FAULT (4) / SETUP (1), with no decision or finished transaction,
invalid/zero timing, unconsumed application receipt and zero/invalid feedback.
The zero maximum_execution_us here means no recorded runtime epoch; it is not
a successful WCET measurement.

The trace retains all 17 completed callbacks: count=17, rejected=0,
overflow=false, timing_fault=false and clock_reads=34. Each retained call is
invoked/completed/timing-valid, stage SETUP (0), application 0. No retained call
requests enable high or nonzero PWM pulses. The source operation enum gives:

| Indices | Recorded operation and result |
| --- | --- |
| 0 | CONFIGURE_ENABLE, true |
| 1 | ENABLE low, true |
| 2-5 | CONFIGURE_PWM channels 0-3, all true |
| 6-9 | PWM channels 0-3, zero pulses, all true |
| 10 | SETTLE false, 427252 to 427411 us, outer span 159 us |
| 11 | ENABLE low, true |
| 12-15 | PWM channels 0-3, zero pulses, all true |
| 16 | SETTLE true, 427556 to 427693 us, outer span 137 us |

PWM periods are [3200, 250, 3200, 3200] cycles for each four-channel pass.
Call 10 is the only false result; trace first_failure equals call 10 and current
equals call 16. Calls are strictly ordered by the stored start/completion times.
Unused slots remain retained as data and are not interpreted as invoked calls.
There are no APPLY or HALT-stage callback records in this complete trace.

The final MotorGate has began_=true, initialized_=false, fault_=IO (3),
armed_=false, hold_complete_=false, release_us_=0 and last_token_=0. halted_ is
false. Both gate and transaction HaltResult fields remain default: attempted,
fresh, timing_valid and inhibition_confirmed are false, with zero timing/fault.
This is absence of a HALT receipt, not an observed failed HALT attempt.

The unchanged source explains the sequence without redefining evidence:
MotorGate::begin first configures low/zero outputs and calls settle. A false
settle sets IO, calls inhibit and returns false without initializing the gate.
inhibit independently writes enable low and all four zero PWM channels, then
settles; its later success does not clear the existing IO fault. The six cleanup
callbacks therefore remain in SETUP context. Transaction::initialize records
SETUP/FAULT and deliberately does not run another halt. Transaction::fail exits
when already faulted. Runtime::begin records TRANSACTION/FAULT; later observer
freeze changes trace context to HALT and calls Runtime::abort, whose terminal
fault guard returns without another transaction or motor operation. Thus the
abort flags do not imply HALT callbacks or confirmed physical inhibition, and
current SUCCESS must not be described as a successful runtime halt or recovery.

## Internal predicate and limits of the association

In the pinned native settle body, FINAL_DEADLINE is emitted only after admission,
initial bank validation, the poll-top deadline check, collection of all three
fresh update flags and the current bank validation. The final elapsed comparison
then rejects 154 us because success requires elapsed < 150 us. Poll index 5 is
inside the unchanged 4096-poll bound. This recorded branch is different from
POLL_DEADLINE, POLL_BANK or poll exhaustion; it does not report missing fresh
updates. Current SUCCESS records the corresponding final comparison succeeding
at 132 us / poll index 4. No extra clock or hardware read is introduced by the
probe publication; the native entry review and pinned source preserve the
150-us/4096 limits and native access sequence.

The standalone probe has no stage, epoch, application token or shared sequence
identifier. Its first-failure/current order is consistent with the independently
recorded two SETUP SETTLE callbacks and source cleanup path; the complete trace
and terminal reports support that interpretation. It remains a source-supported
association across sequentially read objects, not an automatic stage annotation
or atomicity guarantee. Outer 159/137-us callback spans and internal 154/132-us
spans use different measurement boundaries. Neither their difference nor this
one failure proves a physical cause, interrupt cause, timer frequency defect,
production timing distribution or sufficiency of any proposed optimization.

## Preserve the earlier result and next boundary

D195 source `3a08ddeb` and its actual review
`state/reviews/P7_app_motor_observe_actual_review.md` (10216 bytes /
`f8779db4dcd72c3a3552fd9ac2631520243bf38d9257026ed3ea7616870d9f2f`)
remain separate. That attempt began successfully and reached 921 epochs /
115539 polls, with first APPLY/SETTLE false at application 921, outer 154 us,
then HALT/SETTLE false, outer 153 us, and inhibition unconfirmed. Its 64-call
successful prefix and 5485 rejected calls do not reconstruct intervening calls;
its instrumented maximum execution was 859 us. D201 fails during setup before
any epoch. D201's new internal reason does not retroactively establish D195's
unobserved internal branch or erase the earlier result.

The bounded D201 collection and its review are complete; all one-shot native
owners are consumed. Preserve the exact result, raw packet, decoded fields,
original failures and frozen inputs. Further engineering may use this recorded
final-deadline branch as evidence, but any firmware change, compilation or new
diagnostic attempt requires its own explicit scope, independent checks and new
owners. This review provides no bound relaxation, retry, motor permission,
physical acceptance or human gate.
