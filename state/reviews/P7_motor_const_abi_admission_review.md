# D204 fixed file-only ABI admission review

26 September 2026, Asia/Dubai. Separate same-model reviewer, reusing the
completed contract/source/host review context. This review owns only this new
file. The source/host review remains unchanged and immutable. No subject import,
test, compiler, device transport, check-only, native tool or cleanup operation
was performed by this reviewer.

**PASS for the fixed D204 scope and its prerequisites. No open material
finding.** After this review is adopted and all inputs are committed to a clean
reviewed HEAD, the coordinator may perform the prescribed local check-only
followed by at most one file-only execute attempt, preserving every use-time
guard and first failure. This is scope acceptance, not an actual ABI result.

## Bound inputs and unchanged limits

The fixed scope `P7_motor_const_compile_raw/abi_native_scope01.json` is 2758
bytes, SHA256
`6b7fba9d3bc9b3757ee4f93cc63d0fc6057684e16607167eb378751d53aaf1e1`.
All eight bound input byte counts and digests were independently rehashed and
match. These bind the adopted contract, exact actual reader, current compile
manifest/result/artifacts, completed host closure, immutable source/host review
and accepted D203 actual compile review.

The immutable source/host review is 16839 bytes,
`ae662c11ca21d5ebcbb2d0865d35ce8eb068a498e6107e18692d6273209120b4`;
the accepted compile review is 10135 bytes,
`9c3e8cfe07ae33cac8d4a91f74127c33d3929e299bd5da339934943d784f21df`.
All 238 coordinator-freeze inputs independently rehash unchanged at this
admission check. Host acceptance remains 71 Linux passes and 69 Windows passes
with two inherited skips covered by Linux. No implementation, oracle or
historical test change occurred between host closure and scope inspection.

Every numerical bound equals the previously reviewed D199 scope: four file
children, 223 GDB expressions, 23 subjects plus terminal bool, eleven Runner
windows, 60-second child deadline, five-second reap, 400-second transport,
1 MiB per child stream, 8 MiB reply, 30000 UTF-16 command units and 128 MiB
local free-space minimum. The reader implements these unchanged bounds; this
scope does not introduce a new configurable execution interface.

The admitted source is
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`,
serial `2629958581`, expected boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Current artifact bindings and saved
build/export paths agree with `app-motor-const-static01`. The profile remains
the accepted static/default app_motor_observe diagnostic with MATCH0,
MOTORS_ALLOWED0 and SUMOX_MOTOR_FAULT_PROBE1. No compile, upload, reset or
current MCU contents are implied by the manifest or saved artifact packet.

## Ownership and admission at use

The new local owner
`state/analysis/P7_motor_const_compile_raw/native_abi_static01` is currently
absent, independently checked with lexists semantics. The remote scope is
`/home/arduino/sumox26_codex_build/app-motor-const-abi-static01`, distinct from
the checked build owner and every consumed predecessor. Its current absence
has not been observed by this reviewer and must pass the existing embedded
execute-time check. The file-only reader checks that scope but does not create
it. A partial or failed local attempt is consumed; no retry, repair, historical
owner reuse or cleanup is authorized by this review.

No additional board-admission transport is required by the adopted contract.
Source inspection confirms execute's unchanged remote preamble checks UID1000,
arduino user, expected boot, CLI digest, inherited file-size limits, plain
remote ancestry and recognized conflicting processes. It then refuses an
existing remote scope and checks hashes plus stable file identities for all
twelve remote pins before any file child runs: the eight exact D203 artifacts,
readelf, GDB, installed loader and TLS source.

The only four file children are readelf version, GDB version, complete
`readelf -hSWs` on the current raw ELF and guarded GDB on the corresponding
debug ELF. GDB retains no-autoload and no-function-call settings. There is
no inferior attach/run, MCU memory access or configurable command channel.
The report/Runner addresses and helper symbol presence must be observed anew;
neither historical addresses nor mandatory candidate helper symbols enter
this scope.

Remote closure rechecks all twelve file hashes/identity stamps and the final
UID/boot identity, producing thirteen required PASS rows. Local closure
independently rechecks the reviewed HEAD, restricted working-tree state,
current source/manifest and input pins. Existing first-error precedence,
raw-before-parse retention and evidence-write failure behavior remain intact.
The scope's historical-file bindings do not substitute for these use-time
checks or prove present board identity.

## Execution and evidence boundary

This review does not assert that HEAD is already clean or committed; the
coordinator must finish acceptance/state updates, commit them, cease other
writers and provide that exact 40-lowercase-hex reviewed HEAD to the fixed
CLI under Python-B. Check-only performs local preparation without claiming an
owner or contacting the board. Only after it succeeds may the one admitted
execute claim its fresh owner and invoke the file-only transport.

Retain raw result.json, abi.json when valid, local_result.json, invocation
streams, command receipts and all first errors. After execution, a separate
actual-evidence review must reconcile the complete symbol/layout answers,
all four child records, thirteen remote closing checks, independent local
closure and exact source/tool/artifact identities. Future entry ranges can
only follow accepted observations from that new artifact set.

D201 remains the latest flashed image. No SETTLE repair, instruction-removal
claim, target timing benefit, WCET, hardware acceptance, motor-run permission
or human phase gate follows from this admission review.
