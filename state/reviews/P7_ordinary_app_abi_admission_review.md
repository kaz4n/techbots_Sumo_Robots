# D209 fixed file-only ABI admission review

26 September 2026, Asia/Dubai. Separate admission decision by the same-model
reviewer, reusing the completed preparation/source/host review context and the
D204 admission model. Only this new review is owned. No subject import,
check-only, test, compiler, device transport or cleanup was executed by this
reviewer; inspection was limited to local source, JSON, AST, hashes and paths.

**FINAL ADMISSION PASS. No open material finding.** After adoption and a clean
committed reviewed HEAD, the coordinator may perform the prescribed local
check-only, then at most one fixed file-only execute attempt if it succeeds.
All admission-at-use and closing guards remain mandatory. This is conditional
scope acceptance, not a current board observation or an actual ABI result.

## Exact scope and current evidence

`state/analysis/P7_ordinary_app_static_compile_raw/abi_native_scope01.json`
is 3318 bytes, SHA-256
`e34576f4691259dd89cd3a7bacfe88b47886e8e52be5427338c85d0f9bf2f196`.
Its ten input byte counts and hashes independently match: adopted contract,
actual reader, compile manifest/result/artifacts, host closure, immutable
source/host review, accepted D208 actual review, coordinator freeze and revised
implementation receipt. All 159 coordinator pins and all 125 current manifest
file hashes independently match. The scope JSON was parsed with duplicate-key
refusal. No mutable validation document substitutes for these inputs.

The source/host review remains 8934 bytes,
`f3e72aca3a84f9c9a268fb2af0d731c95213f0f024a64bcab84517de2774b53a`.
The actual reader remains 44449 bytes,
`f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d`.
The accepted D208 actual review remains 14982 bytes,
`8cd383e47ab78db74141c0100aedb134afaeac60195555c8eac3b529e1de9865`.
Host acceptance is unchanged: Linux66 PASS, Windows64 PASS/two planned skips
covered by the same Linux method IDs. The three pre-execution findings,
preserved version01 files and bounded revision02 corrections remain recorded;
admission neither erases them nor requires another suite.

The source identity is
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`,
serial `2629958581`, expected boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Manifest and successful compile outcome
agree. The profile is ordinary `app.ino`, static linking, MATCH0 and
MOTORS_ALLOWED0; the current source retains probe0 and all seventeen setup
grants zero. It contains no diagnostic Runner/SETTLE owner. Build and export
bindings point to `ordinary-app-static01`; the eight artifact records, seven
identity aliases, loader/TLS identities and complete validator packet remain
those accepted under D208. These saved records do not prove present remote
file identity and do not imply this ordinary image was flashed.

## Fixed operation and bounds

The scope agrees with the actual literal command table: four children, thirteen
type layouts including bool, six Runtime windows, 47 enum answers, 185 GDB
expressions, 92 markers and two ordinary objects. The children are readelf
version, GDB version, complete readelf headers/sections/symbols for the current
raw ELF and guarded GDB for its debug ELF. GDB retains no auto-load and no
function-call settings. The command table is fixed, with no attach/run or
target-memory command channel.

Bounds remain child60s/reap5s, transport400s, 1MiB per child stream, 8MiB reply,
30000 UTF-16 command units and 128MiB local free minimum. Local free space at
this inspection was 6512947200 bytes. The inherited preamble observes board
free space; this review does not add or claim a new board-space threshold.
The earlier stricter 360-second host-suite ceiling is unrelated to native
transport bounds.

The new local owner
`state/analysis/P7_ordinary_app_static_compile_raw/native_abi_static01` is absent
under lexists semantics; its existing ancestry has no symlink/reparse point.
The remote observation scope is
`/home/arduino/sumox26_codex_build/ordinary-app-abi-static01`, distinct from the
accepted build owner. Its present absence has not been observed by this
reviewer. Execute must check it at use; the file observer does not create that
remote scope. Any claimed local attempt is consumed even after failure.

No separate board observer is required. The retained execute preamble checks
UID1000/arduino, expected boot, CLI digest, inherited file-size limits, plain
remote ancestry and recognized conflicting processes. Before a child starts,
it refuses an existing remote scope and checks all twelve file hashes with
stable before/after identities: eight artifacts, readelf, GDB, loader and TLS
source. These remote checks retain their reviewed implementation; local
descriptor hardening is not being claimed as a new remote descriptor guard.

Remote closure repeats all twelve file hash/identity checks and the final
UID/boot check, requiring thirteen PASS rows. Local closure independently
rechecks reviewed HEAD, allowed working-tree state, source/manifest and input
pins. Hardened bootstrap/local reads, exclusive owner, raw-before-summary
retention, primary-error precedence and evidence-write failure behavior remain
as accepted in the immutable source/host review.

## Conditions and result boundary

This review does not claim HEAD is already committed or clean. The coordinator
must commit acceptance and exact reviewed assets, stop other writers, retain
the 40-lowercase-hex HEAD and invoke the fixed CLI with Python-B. Check-only is
local and does not claim an owner. Only successful check-only permits the one
execute. No retry, repair, historical owner reuse, compile, upload, reset,
privileged action or cleanup follows from this admission.

Retain invocation/transport streams, intents, raw result, ABI summary when
valid, local closure and every first error. Separate actual review must
reconcile the four child records, all thirteen closing checks, source/tool/
artifact identities, complete layout/enum/window answers, both unique objects
inside initialized BSS with alignment/nonoverlap, and independent local
closure. Actual coordinates and later entry ranges must follow those observed
answers; historical diagnostic addresses are not admissible substitutes.

The ordinary continuous loop supplies no terminal snapshot, final inhibition
or atomic/coherent collection semantics. D207 remains the last verified
flashed image. No live RAM, runtime behavior, timing/WCET, physical acceptance,
motor permission or human phase gate follows. This review is sealed after
final byte/hash reporting; reviewer writes stop.
