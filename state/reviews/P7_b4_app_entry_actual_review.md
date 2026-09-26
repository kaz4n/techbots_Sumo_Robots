# D217 B4 actual file-entry review

FINAL PASS, 2026-09-26. Same-model reviewer with reused context, separate from implementation and oracle authors; not human or cross-model acceptance. Review is based on saved actual native bytes, source and accepted D215 layouts, not synthetic fixture interpretation. No reviewer subject imports, tests, device calls or reruns occurred.

## Actual provenance and closure

The single invocation used clean reviewed HEAD `327e5de312b20648a04ee31825c9b63f98d8f93d`. Check-only returned zero in 1.5339345 seconds; execute returned zero in 7.534691 seconds. The reviewed native driver retained its cosmetic `d217-abi-native-invocations-v1` schema while invoking the correct entry launcher/owners. Both outer streams reconcile with their exact base64 and hashes; no first error, closing error, drift or retry is recorded.

Evidence paths are relative to `state/analysis/P7_b4_app_compile_raw/`; sizes are bytes and hashes are SHA-256.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `entry_native_invocations01.json` | 3808 | f62cd8fa37b2283ac8ecb83748614f867238ef50eac306dbaadbffd9cfdce389 |
| `native_entry_static01/inputs.json` | 26671 | e6c3e515f8158b11dcdf6dc3b64117eb643022640f985db43fa9647680d66b85 |
| `native_entry_static01/result.json` | 693504 | e8b63a2a76a1d9ed680f5a6f4159b033bbae9812f567f57a9901493a5d375462 |
| `native_entry_static01/entry.json` | 21582 | a7a7561835e69367d6d94575534ced47ca1573d87bc27da9dad58e782a8136d3 |
| `native_entry_static01/local_result.json` | 277 | 5a1ae408603e6e9dff01f1c115d777a7c767dc00229bac838002a29ec6ecaefd |
| `entry_native_closing01.json` | 7553 | 917fe83501acdff8d8f7f7e8391d3917c972c58b024c286adf361ea4a35c4035 |

Independently rehashed all 175 prerequisite working files and compared every byte against the reviewed HEAD blobs; all match. The 169 coordinator files, 15 scope inputs and 154 native hash-only local pins also match. The accepted source/host review `8054c937...` remains immutable, including the preserved original zero-test fixture failure and bounded repair.

Decoded the exact transported program as data: 13785 bytes / `b440eede7e9ec6bc601256ff1253b6bb7fdf69e8e15346dfa53dcbb6d3e0afb4`, matching the admitted program and 5457 UTF-16 units including NUL. AST-literal command and ordered pin tables match the input record and actual results. The sole transport returned zero; its saved stdout strictly parses to the saved result and stderr is empty. The four children are exactly readelf version, GDB version, readelf headers/sections/symbols/initializer bytes, and the fixed file-only GDB disassembly. Each returned zero, was reaped, had no timeout and empty stderr; 60-second child/5-second reap/1 MiB stream bounds, 400-second transport and 500-second outer bound are retained. Their stdout sizes are 283, 281, 141273 and 369493 bytes. All eight native files and all child stream pins match the closing receipt.

The 12 exact remote file closing rows plus board identity occur in the actual transported pin insertion order and all pass. Board identity is UID1000/arduino, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, no conflicts, and 13871202304 free bytes. Local closure passes, reports one transport and no first error. No compiler, upload, reset, MCU read, privilege operation or firmware modification occurred.

## Actual ranges and focused interpretation

Independently reconstructed all 64 marker-delimited raw blocks and checked every recorded block hash, range, alias and contiguous 2/4-byte opcode extent: 77 aliases, 10488 selected bytes and 3703 disassembly rows. Literal-pool rows are included in that count; it is not an executed-instruction count. All 2037 symbol indices, including the unnamed row zero and hexadecimal Runtime size, are present; every selected raw alias row matches the fixed binding. This is complete extraction/geometry coverage of the selected ranges. Detailed semantic reassessment here focuses on startup, the four changed functions and the connected M0 transact path; it does not reclassify every unselected callee or manufacture a closed call graph.

Actual initializer bytes `01011008` at `0x081131e4` resolve to Thumb pointer `0x08100101`. Preinit and static-thread lists are empty at that address; the initializer interval ends at `0x081131e8`. Saved startup instructions copy 208 bytes from `0x08114310` to `[0x20013890,0x20013960)` and zero `[0x20013960,0x2003c718)`, 167352 bytes. This does not cover the additional 232 bytes of the allocated BSS section. Setup constructs 21 zero grant bytes, passes Runtime `0x20013960` to begin and ignores its Boolean return. Global initialization binds current motor/source/dump objects and calls their port getters/Runtime construction. Main continues loop/hook indefinitely. A separate same-model collaborator checked these saved startup groups without execution and found no discrepancy. External loader and memory-primitive interiors remain unselected.

The four enlarged functions reconcile with current source and the fresh D215 ABI:

- **Robot construction**, `[0x08102818,0x08102de4)`, 1484 bytes: direct zero/default stores initialize the B4 Sequence member at Robot offset1748, including phase/reason/segment, duties, freshness, time fields and started flag, followed by the three stand state flags at1776–1778. The current nested Runtime layout places Robot at288 and Sequence at2036, giving the same1748 offset. The call at `0x08102ba6` constructs RobotResult at Robot+1784. This is emitted construction, not a stand start/step or motor operation; absence of a separate Sequence constructor symbol is not absence of initialization.
- **RobotResult construction**, `[0x08102748,0x08102818)`, 208 bytes: initializes the added 16-byte stand report and false stand_stopping at16, then zero token at24, fresh at32, output duties at36/40 and motor/BOOT state at44/45. These current offsets match the accepted 424-byte layout. Its other default/array initialization remains distinct from runtime evidence, and nonzero menu/mode defaults are not actions.
- **Transaction::applyDecision**, `[0x08103158,0x0810327c)`, 292 bytes: supplies current time, timing and previous receipt before Robot::step, then copies 421 bytes into the 424-byte RobotResult container (the last declared field is at420; tail padding is not a missing field). Fresh/nonzero/strictly increasing token checks precede gate application. The gate result must be consumed with matching feedback token before recorder consume and publication of decision_made/recorded/DECIDED. Actual application uses the shifted fresh/token/report offsets and retains the identity-failure branches. Robot::step, recorder consume and strategy interiors are unselected.
- **MotorGate::apply**, `[0x0810ed4c,0x0810ee48)`, 252 bytes: reads fresh at32 and token at24, consumes a valid increasing token before initialization/fault checks, retains invalid-command and STOP inhibition paths, and accesses shifted outputs at36, motor-enable44, UI45 and lifecycle phase56. STOP clears armed/hold/release and records applied_valid only from inhibition plus a disabled request. Consumption alone does not prove application, a good fault status or physical inhibition. The validCommand interior remains unselected.

The connected selected `transact` body `[0x0810ece4,0x0810ed4c)` calls enable(false), issues four PWM callbacks with zero pulse arguments, then settles. On success it publishes applied_valid, motors_enabled=false and zero duty values; failures retain IO/inhibit paths. No enable(true) appears in this M0 body. This is evidence of the requested callback sequence, not a measured electrical or mechanical outcome.

## Acceptance boundary

No material mismatch was found. Accept D217's fixed file-only collection and the source-qualified selected instruction observations. D214 B4 artifacts remain compile-only; the existing D212 flashed firmware is unaffected. This does not prove a completed B4 sequence, whole-program behavior, physical inhibition, timing/WCET, free runtime RAM, captured recorder contents, atomic publication/coherence or a human phase gate. Runtime remains continuous; no diagnostic terminal/final-inhibition semantics are transferred. Unselected B4 helper interiors, source-only object details and external callees retain their prior limits.

Local read-only audit helpers initially used a nonexistent plaintext child-stream key, confused hash-only pins with size/hash records, and used a multiline whitespace expression that swallowed the empty symbol name's next row. Those checks refused without writes or target execution; base64 decoding, observed pin encoding and per-line symbol parsing resolved them. Root separately records its hash-only pin audit correction in the closing receipt. Neither changes original evidence or constitutes a native retry.
