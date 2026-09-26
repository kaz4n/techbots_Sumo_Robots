# D207 actual inhibited diagnostic

26 September 2026. Collection and offline decoding succeeded. The inhibited
observer reached its planned 10000-epoch limit without a recorded callback or
SETTLE failure, and its final halt reported a callback-level inhibition
acknowledgement. This is not a pin measurement. Independent actual-result review
`b562488423fce03712e0156deba21f52fddc826f096c70dcb1736d78aee71937`
is final PASS for this bounded attempt and its stated evidence limits.

The reviewed clean HEAD was `676e3625830b64d99309d6d03fba05ca24ea99fe`.
Local check-only returned zero in 1.385 seconds, followed by the single admitted
execution at 14:33:37 Dubai. Execution returned zero in 280.340 seconds with
empty stdout/stderr. The caller recorded COMPLETED, no first or closing errors,
13 transports, one upload and one conditional capture. No automatic retry ran.

The current static/default diagnostic has MATCH=0, MOTORS_ALLOWED=0 and probe=1.
Its source digest is
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`;
the packaged sketch is 95368 bytes, SHA256
`f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7`.
This supersedes D201 as the latest verified flashed diagnostic. Pins, grants,
the 150 us SETTLE deadline and 4096-poll bound remain unchanged.

The uploader reports UPLOADED with one successful, reaped child and no timeout.
Capture reports COLLECTED with all 26 reads, totaling 727128 requested bytes.
All four before/after loader and sketch comparisons passed. It retained the
declared 30-second pre-sample wait and 2-second sample gap. Each of the six
first/second SRAM region pairs has matching reported hashes; coherence remains
UNPROVEN. Matching bytes alone do not establish initialization or loop success.

| Local evidence under `P7_motor_const_run_raw/` | Bytes | SHA256 |
|---|---:|---|
| `native_invocation01.json` | 1204 | `60438286944f1486edafb0252a5dfc76c439b968f17c62c265fbe74b4026d0c8` |
| `native_inert_run01/inputs.json` | 18581 | `8a85e481dc14b2f68b7ba39575689649e579af05bb14b780aa7d3a47adcca7b3` |
| `native_inert_run01/result.json` | 58692 | `860338ea10ab47c5c8cef9942fa0fa084b35ae79f0bc833fbc3b0396d0dac409` |
| `native_inert_run01/final_checks.json` | 49963 | `d85afb00fbc8d26d5ae24f7f8d89a7a436598cc1050a1f42b9ac99740ff519c1` |

The saved remote upload result is 1903 bytes / `c0e9d53fb5171e58412eb4515e63b1dbb0068d6a81fe5a9e68e587bcc8496a02`;
the capture result is 7100 bytes / `9b879b418ad996a371e184b107b29617ce8cad0c189b7bbbb1427e34f80a1fd0`.
The prepared file-only retrieval binds those two files and the twelve captured
SRAM files, 18035 bytes total. It preserves the accepted reader core and helper,
changes only its PINS assignment and makes no new MCU read, reset or upload.
Independent review preceded its single execution and offline decoding.

## Retrieved bytes and observed application behavior

Final retrieval preparation review `c7eafdb3` admitted the exact file-only
reader. It ran once at 14:41:49 Dubai, returned zero in 0.435 seconds with
empty stderr, verified all fourteen file hashes and repeated all fourteen
reads at closing with unchanged identity. The packet is 27525 bytes, SHA256
`4a9355808c4136c067b37426cb5904c17eeb061f8f386cd541a6dd89d2bc065d`.
The unchanged reviewed decoder received that explicit packet hash and returned
zero. Its `decoded.json` is 81223 bytes, SHA256
`7d10f606290355cadfdc258b1ac3b2b2f587e0d652f309107957ec789092a01c`.
Status is DECODED with no decode error; all six decoded region pairs are equal.
Coherence remains UNPROVEN.

The observer reports FROZEN / EPOCH_LIMIT, with begin_called, begin_finished,
begin_ok, before_abort_valid, abort_called, abort_returned and
last_step_returned true. It made 1470524 polls and reached 10000 epochs.
Immediately before its planned abort, Runtime was RUNNING with fault NONE,
zero missed releases, and maximum_execution_us=519. The final pre-abort
transaction and previous-tick receipt have token 10000, zero duties, motor
enable false and a measured 500 us execution. Its robot outputs retain ui_state=BOOT
with go/motion_permitted false and no recorded contract or escape fault.

Runtime initialization_complete remains false. This is separate from a
successful begin: all peripheral/service setup grants are absent in this
diagnostic, so full sensor and match readiness were not exercised.

After the deliberate Runner::freeze -> Runtime::abort path, Runtime reports
FAULT / TRANSACTION and MotorGate reports STOPPED. These are the implementation's
planned terminal mechanism after EPOCH_LIMIT, not evidence of a preceding
callback failure. The final HALT receipt is attempted, fresh and timing-valid,
with inhibition_confirmed=true, started_us=10426813 and completed_us=10427029
(216 us). The gate is halted, unarmed and initialized, with last_token=10000.

The internal native SETTLE report has current SUCCESS, elapsed_us=116,
poll_index=10, fresh_mask=7 and valid=7. It has no lifetime first failure;
the absent first-failure storage is zero, with reason NONE and valid=0.
The trace's current callback is the successful final HALT SETTLE at application
10000, from 10426906 to 10427027 (121 us including its callback wrapper).
The 116 us inner SETTLE value is not a run-wide maximum.

Trace has_failure=false and timing_fault=false. Its finite 64-call prefix
contains eleven setup and 53 application calls, ending during application 9;
all stored calls returned successfully. Overflow=true and rejected=59953
explicitly retain the missing later call-history count. Clock reads total
1680566. Current and lifetime-first-failure slots remain separate from that
truncated prefix; this is not a complete per-call history.

Compared with D201, this finite attempt passed begin and reached its limit,
where D201 retained SETUP_FAILED with first FINAL_DEADLINE at 154 us. This is
a useful current result, not proof that intermittent failures are eliminated.
The observed 519 us maximum is below the 800 us requirement, but an inhibited,
ungranted diagnostic is not full-source robot WCET qualification. Live
RAM/stack, sensors, powered output behavior, physical gates and match readiness
remain unqualified.

Native owners are consumed. Collection success does not prove SETTLE repair,
physical safety, motor operation, WCET, live RAM/stack margins or a phase gate.
Historical D195 and D201 failures remain intact.
