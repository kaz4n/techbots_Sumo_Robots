# D203 fixed compile of constant motor metadata

26 September 2026. Proposed under D051 after D202 source and host review
f7b8a116464ac0590aa93dc19a66db0d4f4cebe4eed717a5a4f67780c75021ae.
Adoption is recorded separately in DECISIONS.md before implementation. This
document prepares a new compile-only scope; it creates no executable launcher,
actual manifest, native owner, compiler invocation, transport or upload.

D202 changed only the expected-metadata calculation region in motor_port_unoq.cpp.
Host evidence preserves the initial carrier-zero fixture failure and the
unchanged historical D197 symbol-inventory failure, with their explicit review
dispositions. Neither failure is erased or relabeled. Target division removal,
memory changes and runtime benefit remain unobserved. D201 remains the latest
flashed image and its SETUP_FAILED result remains unchanged.

## Exact inherited baseline

The entire D198 contract below is normative, except for the exact metadata
substitutions and source identity stated here. All implementation bytes outside
those substitutions remain unchanged. In particular, inherit its sections
"Public API and unchanged bootstrap", "Fresh fixed ownership, manifest and
staged source", "Inherited compile lifecycle and evidence boundaries", and
"Independent controlled validation". Their source, descriptor, ancestry, owner,
manifest, clean-HEAD, resource, process, artifact, TLS, first-error and closing
checks are not relaxed. Historical files and consumed owners remain untouched.

| Input | Bytes | SHA256 |
|---|---:|---|
| tools/compile_motor_settle_probe.py | 7570 | b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62 |
| state/analysis/P7_motor_settle_compile_contract.md | 14344 | c0b352810c41c8b3744acdd1c15bc4b21ecb76bc15d76d4fedea4fdde37dc756 |
| tools/compile_app_motor_fault.py | 29802 | cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a |
| tools/app_motor_fault_static_policy.py | 8262 | 3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270 |
| tools/app_motor_fault_compile_remote.py | 6891 | 1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2 |
| src/hal/motor_port_unoq.cpp | 19906 | fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b |

## Only new executable and its exact derivation

Add only tools/compile_motor_const.py. Starting from the pinned 7570-byte D198
launcher, apply these ordered byte substitutions, requiring the exact old-byte
count at every step. Preserve line endings and all other bytes. The first row
changes only the existing test-description comment.

| Old literal | New literal | Count |
|---|---|---:|
| D198 | D203 | 1 |
| tools/compile_motor_settle_probe.py | tools/compile_motor_const.py | 1 |
| P7_motor_settle_compile_contract.md | P7_motor_const_compile_contract.md | 1 |
| P7_motor_settle_compile_raw | P7_motor_const_compile_raw | 1 |
| app-motor-settle-static | app-motor-const-static | 3 |
| _sumox_d198_settle_compile | _sumox_d203_const_compile | 1 |
| 29889 | 29874 | 1 |
| 9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c | bda40e969dc48d4194f1c391c013cf0853e1fb39dee780a94f4754412d59f41a | 1 |
| 6895 | 6893 | 1 |
| dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160 | 914d4d11057c8982154fbcd80fbea485977cf4952fad045625ca88271052040a | 1 |

Result: exactly 7557 bytes, SHA256
957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247.
This identity is derived as data, without importing or executing any launcher.
Do not add runtime dependencies or HARD_PINS for the historical D198 launcher
or contract; they remain derivation evidence. The three original runtime inputs,
their ORIGINALS entries, all inherited hard pins and self.code snapshots stay
exact. No new CLI, policy, dispatch path, cache or source transformation is added.

## Exact private projections

Apply D198's caller table to the original compile_app_motor_fault.py, replacing
only its new-side launcher, contract, raw path and attempt-prefix literals with
the D203 values above. Thus the four changed destinations are respectively
CALLER = 'tools/compile_motor_const.py', P7_motor_const_compile_contract.md,
P7_motor_const_compile_raw and app-motor-const-static. Their original counts
remain 1, 1, 1 and 6. All seven other caller replacements remain exact.

The adapter's two replacements and resulting bytes remain identical to D198.
Its project, seven aliases and STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS
success label do not change. Preserve all metadata, artifact, native-TLS,
package and export validators. Remote projection still has four ordered steps:

1. app-motor-fault-static01 to app-motor-const-static01, once.
2. Quoted 'app_motor_fault.ino' to 'app_motor_observe.ino', once.
3. app-motor-fault-static-artifacts-v1 to app-motor-const-static-artifacts-v1, once.
4. Original adapter SHA3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270
   to projected SHAe3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d, once.

| Projected source | Bytes | SHA256 |
|---|---:|---|
| caller | 29874 | bda40e969dc48d4194f1c391c013cf0853e1fb39dee780a94f4754412d59f41a |
| adapter | 8266 | e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d |
| remote | 6893 | 914d4d11057c8982154fbcd80fbea485977cf4952fad045625ca88271052040a |

Each original length/hash must match before projection, each occurrence count
during projection and each final length/hash afterward. Keep projected adapter
hash coupling in the compressed remote payload. Verify all three originals and
all three projections before private caller execution. The private ModuleType
name becomes _sumox_d203_const_compile; its original caller __file__, injected
projection seams, false historical main guard, HARD_PINS extension and REQUIRED
union remain unchanged. No global module registration or import-time source
reading, class instantiation, owner creation or native dispatch is permitted.

## Fresh scope and source identity

Keep bench/app_motor_observe, project app_motor_observe.ino, static link mode,
default startup and exactly -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1.
FQBN remains arduino:zephyr:unoq:link_mode=static. Only metadata/owners change:

- RAW: state/analysis/P7_motor_const_compile_raw.
- Manifest: RAW/inputs_static.json; schema app-motor-const-static-inputs-v1.
- Output: RAW/native_static01, with its prescribed pycache child.
- ATTEMPT: app-motor-const-static01.
- Local stage owner: build/stage/app-motor-const-static01; child app_motor_observe.
- Remote owner: /home/arduino/sumox26_codex_build/app-motor-const-static01,
  retaining build and artifacts children.
- Canonical source: /home/arduino/sumox26_codex_build/<source_sha256>/app_motor_observe.

Check, intent, compile-outcome and artifact schemas use app-motor-const-static.
Any claimed, partial, failed or uncertain new owner consumes this attempt; no
automatic retry. Existing D188/D193/D198 identities and owners cannot substitute
for this scope. The old adapter status and artifact filenames remain unchanged.

The later actual manifest must contain exactly projected REQUIRED union the
current ordinary files under src, bench/app_motor_observe and bench/motor_fault/src,
with inherited plain-file, case, path, source-count, total-size and mapping checks.
No actual manifest is produced by this contract. D198 input manifest
aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 is evidence only.
Data-only comparison found the same 110 source inventory names, with only
src/hal/motor_port_unoq.cpp changed. Current inventory totals 782068 bytes;
the unchanged diagnostic mapping yields 108 destinations totaling 781200 bytes.
Its sorted UTF-8 destination-plus-NUL-plus-exact-content digest is
4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2.
This is the diagnostic source_mapping digest, not ordinary app_source_hash.
Substituting only the pinned ff35c83e predecessor motor cpp in memory reproduces
D198's 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da.
Revalidate the exact current inventory, mapping and digest during later manifest
preparation and admission; this calculation does not prove staging or board state.

## Independent host validation and later native admission

Freeze the independent oracle before implementation review or execution. Its
author derives the ten-step launcher and private projection identities from
this contract and pinned baselines without reading the new implementation.
Keep the implementer separate. Retain the complete corrected D198 suites:

| Historical oracle | Bytes | SHA256 |
|---|---:|---|
| tests/tooling/test_motor_settle_compile.py | 11340 | 71371f9361ef20ae0a64feb156e10e24e22722b1b31d8d426816d69bd6db962a |
| tests/tooling/test_motor_settle_compile_remote.py | 3412 | b2da457db6da3d01412dd300d495f075a8631294c75627f66b91dc1ee9fbd2e7 |

Preserve all 65 caller and 37 remote methods and underlying D193/D188 assertions
through independently counted/hash-checked private metadata fixture projections.
Keep old fault and observe owner negative cases, and add consumed settle owner
negatives; do not globally rewrite away historical refusal coverage. Preserve
the already corrected claim/stage fixture ordering, descriptor/special-file
checks, covered Windows skips and original failure evidence. Add exact launcher
reconstruction and unchanged-outside-transforms checks; original/projected byte
pin refusal; unchanged adapter; new owner/schema/manifest identity; current
source inclusion/drift/digest and consumed-owner refusal checks. The existing
inventory fixture may calculate its current mapping dynamically. No fixed old
source count or hash may substitute for verifying the actual set.

Run both host platforms serially with Python-B and exclusive saved receipts.
All endpoints remain synthetic: no actual compiler, transport, board call or
native sleep. Preserve first failures before any independently adjudicated
fixture repair. Never edit an old oracle, relax assertions or manufacture PASS.

Only after source, oracle, host-result and independent review closure may the
coordinator prepare a fresh exact manifest and admit one compile-only attempt.
Retain fresh CLI/board/boot/dependency identities, clean committed reviewed HEAD,
local read-only check-only, exclusive owners and durable intent. Recheck at
least 128 MiB local and 1 GiB board free space and all inherited memory/process
bounds. Keep one properties query/60 s, one compiler/jobs1/720 s, reap5 s,
30000 UTF-16 command bound and all eight-file artifact/installed loader/TLS/
source closing checks. No retry, package install, firmware/config repair,
upload, reset or MCU memory read is authorized here.

After accepted new artifacts, a separate file-only ABI/entry task must observe
the actual report/global layouts and initialization, inspect the candidate
helper emission for removed runtime division dispatches and compare code/storage
changes. Do not reuse D199 addresses or assume functions remain emitted. A later
inhibited runtime attempt needs its own fresh bound scope and review. Compilation
or removed instructions prove neither a timing improvement, root cause, WCET,
live RAM/stack, physical behavior, motor permission nor a human phase gate.
