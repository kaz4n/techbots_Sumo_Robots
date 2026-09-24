# D119 finite B4 request sequence validation

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED. This is the pure sequence slice,
not an integrated directional controller, powered B4 acceptance or B7 test.
Contract/public interface were adopted in `bf2c4524`. No existing Robot,
MotorGate, governor, HAL, application, upload policy or locked test changed.

`src/core/stand_sequence.cpp` implements twelve finite rows: left forward,
brake/coast, left reverse, brake/coast, then the corresponding right rows.
The new config defaults are 500 ms per row and 0.25 nominal duty. Exact observed
phase anchors preserve brake/coast intervals. STOP/edge cancellation, invalid
clock order and excessive gaps produce permanent zero-request terminal states.
There is no motor permission, I/O, sensor synthesis or application receipt.

## Independent expectations and results

Separate same-model contexts authored the implementation and tests. The test
author used only the contract/public header, never the implementation body.
Original oracle 65351127 froze before execution. Review of installed doctest
identified unsupported fatal assertions under the existing no-exceptions flags.
The unexecuted original, literal diff and preservation proof are retained; the
amendment keeps all twelve prerequisite expressions and 49 CHECK expressions,
evaluates each prerequisite once, and explicitly aborts if its CHECK fails.
Single-argument CAPTURE was already correct in the frozen original; the reviewer
had initially observed an earlier authoring draft.

Amended oracle `5e03938c09337d2dc6ce419b1030ef0e7b9d75f110df858219814cce3122c026`
froze at 04:56:28+04 before any implementation execution. Source
`8dfc2dcbdc74a01002ae117fd5649d0388bcf452d63a2ca5ab84990c6a899a94` passed its
first runs unchanged. No expectation or implementation repair followed execution.

| Validation actually run | Result |
|---|---|
| Independent isolated normal and ASan/UBSan | Each 18 cases / 246,080 assertions; compile/run0 |
| Full normal host suite |1,496 main / 50,418,546 assertions; 187 Gate / 4,536,952 assertions; 0 fail/skip |
| Full ASan/UBSan host suite | Same counts, 0 fail/skip, instrumented compile/link flags retained |
| Private reviewer config/clock profiles |12/12: 9 invalid configs rejected, 3 valid custom profiles pass |
| Canonical config-registry wrapper |2 methods pass, including the unchanged 18-check registry and legacy wrong-value probes |

The first config-registry launch used noncanonical `tooling` imports, creating
another copy of `tests.tooling` modules; its patches did not reach the inner
registry. Original failure output remains. Correcting only the launch import
passed unchanged source/tests. This was not a firmware defect or relaxed check.

Commands, statuses, hashes and times are under `P2_stand_sequence_raw/author`,
`coordinator` and `reviewer`. `run_host.py` records the actual canonical host
command and existing sanitizer build command. Both LastTest logs plus sanitizer
compile/link flags are archived. Source/oracle hashes remained unchanged.

## Exact target compilation, no upload

D119's recorded validation extension admitted one checked default/M0 app
compile-only build on UNO Q Linux via explicit ADB 2629958581. The existing
`python tools/board_tool.py flash app --compile-only` returned0; fresh receipt
`e72172eec9c649e7b785c42d7c570ad9`, source
`62e382043ee632c7048b94427de382b41f06130d66416c2ac0edf8f148c4c647`.
The resulting 13,244-byte stand_sequence object and its exact compile command
were observed in completed Linux build files. No MCU operation was performed.

Checked final app ELF 8379f152, ZSK c60443cd and loader 39d4a4fd match D118 exactly;
full hashes and archived checked receipts are in coordinator/app_build_archive.json.
The final app remains 176,048 bytes with 257,280 bytes reported static payload. The
unused sequence contributes no retained app bytes. This preserves the earlier
conditional loading calculation; it adds no free-heap, stack or WCET measurement.
The compiler's low-memory warning remains. New future references to this helper
will change that footprint and require another exact check.

Separate review: `state/reviews/P2_stand_sequence_review.md`. This is a scoped
same-model review, not cross-model review or a human phase gate.

## Resume point and limits

Adopt the actual B4 Robot/Runtime integration next under D051/D075: immutable
bench profile, genuine qualified full hold and source/edge handling, explicit
final cap, true Lifecycle STOP, shared-EN coast, and actual MotorGate receipts.
Preserve default production and P3 DRIVE_TEST behavior; never patch a RobotResult
to inject requests. The existing inhibition-only stand bench remains unchanged.

Current last-observed MCU remains the consumed D118 e820c0e1/M0 run. No new
upload, reset, UART operation, sensor grant or powered trial occurred. Native
dump prerequisites, physical sensor/electrical acceptance, B7/R6 conflict and
all human phase gates remain open. Resume files were condensed; their historical
snapshots remain in Git at fbfb0f2e, and PROGRESS history remains append-only.
