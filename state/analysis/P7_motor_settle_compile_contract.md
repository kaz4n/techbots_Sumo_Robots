# D198 fixed native-settle diagnostic compilation

26 September 2026. Prepare one new compile-only launcher for the unchanged
app_motor_observe sketch with the D197 diagnostic HAL/header. Preserve its
static/default/MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1 profile. This is
the next diagnostic image, not production static adoption or a timing-limit
repair. D197 source/host review must close before a native compile is admitted.
This contract creates no actual manifest, owner, compiler invocation or upload.

Add only `tools/compile_motor_settle_probe.py` for execution. Derive its bytes
from the reviewed D193 launcher exactly as below; do not modify any historical
launcher, policy, remote helper, oracle, receipt or consumed owner. No new
transport/process framework, CLI mode, build policy or firmware change is part
of D198. All new source bodies and tests must be frozen and independently reviewed
before native use. The immutable D193 behavior is the baseline, including its
pre-read descriptor/special-file repair; do not return to its earlier draft.

## Fixed source identities and exact launcher derivation

| Input | Bytes | SHA256 |
|---|---:|---|
| tools/compile_app_motor_observe.py | 7583 | 70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827 |
| state/analysis/P7_app_motor_observe_compile_contract.md | 10919 | 0301726f47c0c438a7984ddd232f81c4891c511651ba81a986b15f5ef91dbfb4 |
| tools/compile_app_motor_fault.py | 29802 | cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a |
| tools/app_motor_fault_static_policy.py | 8262 | 3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270 |
| tools/app_motor_fault_compile_remote.py | 6891 | 1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2 |
| state/analysis/P7_motor_settle_probe_contract.md | 12585 | 3346b11970814ce7703c48f56cb38405449453964bb79d1740d5a49e78610f7c |

Starting from the exact7583-byte launcher, apply only these ordered byte
substitutions. Require the old literal's occurrence count at every step; preserve
all other bytes and line endings. The first row changes a comment only.

| Old literal | New literal | Count |
|---|---|---:|
| D193 | D198 | 1 |
| tools/compile_app_motor_observe.py | tools/compile_motor_settle_probe.py | 1 |
| P7_app_motor_observe_compile_contract.md | P7_motor_settle_compile_contract.md | 1 |
| P7_app_motor_observe_compile_raw | P7_motor_settle_compile_raw | 1 |
| app-motor-observe-static | app-motor-settle-static | 3 |
| _sumox_d193_observe_compile | _sumox_d198_settle_compile | 1 |
| 29904 | 29889 | 1 |
| 830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884 | 9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c | 1 |
| 6897 | 6895 | 1 |
| f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c | dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160 | 1 |

The exact resulting new launcher is7570 bytes, SHA256
`b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62`.
This identity was computed using byte transformations only, without importing
or executing a launcher. It is not evidence of a build or validated behavior.

The new launcher still reads the same three original D188 source paths and
checks their exact ORIGINALS entries above. D193's launcher/contract are retained
derivation evidence; no extra runtime dependency or HARD_PINS entry for them is
added. All inherited hard pins remain unchanged, including the original caller,
adapter, remote helper, D185 caller, executor, support, installed baselines and
static metadata/artifact validators.

## Exact private source projections

The new launcher's project_caller(raw) applies this ordered table to the exact
original tools/compile_app_motor_fault.py bytes, not to a previously projected
caller. Preserve the unchanged original source file and self.code snapshots.

| Old literal | New literal | Count |
|---|---|---:|
| CALLER = 'tools/compile_app_motor_fault.py' | CALLER = 'tools/compile_motor_settle_probe.py' | 1 |
| P7_app_motor_fault_compile_contract.md | P7_motor_settle_compile_contract.md | 1 |
| P7_app_motor_fault_compile_raw | P7_motor_settle_compile_raw | 1 |
| app-motor-fault-static | app-motor-settle-static | 6 |
| 'app_motor_fault.ino' | 'app_motor_observe.ino' | 1 |
| bench/app_motor_fault | bench/app_motor_observe | 4 |
| 'app_motor_fault' | 'app_motor_observe' | 2 |
| '/app_motor_fault' | '/app_motor_observe' | 1 |
| STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS | STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS | 1 |
| self.code[ADAPTER] | project_adapter(self.code[ADAPTER]) | 2 |
| self.code[REMOTE_HELPER] | project_remote(self.code[REMOTE_HELPER]) | 2 |

Adapter projection is exactly D193: replace quoted 'app_motor_fault.ino' with
'app_motor_observe.ino' once and STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS with
STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS once, in that order. Keep all seven
app.ino alias values,84-property/24-name/5-flag checks, private imports and full
D147/D142 TLS/artifact/package/export validation. The adapter's result label
remains OBSERVE because the sketch/project/profile are unchanged.

Remote projection applies only these four ordered replacements to the original
tools/app_motor_fault_compile_remote.py:

1. app-motor-fault-static01 -> app-motor-settle-static01, count1.
2. Quoted 'app_motor_fault.ino' -> 'app_motor_observe.ino', count1.
3. app-motor-fault-static-artifacts-v1 -> app-motor-settle-static-artifacts-v1,
   count1.
4. Original adapter SHA3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270
   -> projectede3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d,
   count1.

Require these exact final projection identities:

| Projected source | Bytes | SHA256 |
|---|---:|---|
| caller | 29889 | 9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c |
| adapter | 8266 | e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d |
| remote | 6895 | dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160 |

There is no additional projection of firmware or checked response bytes. Missing,
extra or changed occurrences fail. Original input hashes and lengths must match
before a projection, and projected hashes/lengths must match afterward. Keep the
remote compressed-source/source_sha pair and its projected adapter pin coupled;
the current file bytes in self.code and closing checks remain the originals.

## Public API and unchanged bootstrap

Preserve parse_request(argv), project_caller(raw), project_adapter(raw),
project_remote(raw), read_original(relative, *, root=ROOT),
load_caller(*, root=ROOT), and main(argv), including all helper behavior. The
optional root seam is for controlled host fixtures, not a native CLI option.
Import performs no source reads, owner creation or dispatch. main rejects an
invalid list/type/order/count/head and missing Python-B before loading; accepted
CLI is exactly --check-only|--execute --reviewed-head <40lowerhex>.

Keep ordinary full-ancestry checks, one-link files, symlink/reparse/special-file
refusals, O_NOFOLLOW/O_NONBLOCK when available, immediate descriptor validation
before fdopen/read,65537-byte read bound/65536-byte source maximum, before/after
path and descriptor stamps and primary-over-close errors. The original Windows
cross-API ctime exception remains exact; do not broaden it or transplant the
separate executable-mode ABI-reader fix into this .py bootstrap.

All three originals and all three projections are verified before private caller
execution. load_caller uses fresh ModuleType _sumox_d198_settle_compile, original
caller __file__, injected project_adapter/project_remote and false historical
__main__ guard. Do not register it globally or instantiate CompileDiagnostic
during import/loading. Return the original class and seams. Preserve HARD_PINS
extension with original caller/remote hashes and REQUIRED union HARD_PINS;
preserve every existing pin. No projection cache or extra dispatch is introduced.

## Fresh fixed ownership, manifest and staged source

Project stays app_motor_observe.ino. FQBN stays
arduino:zephyr:unoq:link_mode=static; startup remains default; flags remain exactly
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`.

- RAW: state/analysis/P7_motor_settle_compile_raw.
- Manifest: RAW/inputs_static.json, schema app-motor-settle-static-inputs-v1.
- Local output: RAW/native_static01; its prescribed isolated pycache prefix is
  that exact output's pycache child.
- ATTEMPT: app-motor-settle-static01.
- Local stage owner: build/stage/app-motor-settle-static01, containing the
  unchanged child basename app_motor_observe.
- Remote owner: /home/arduino/sumox26_codex_build/app-motor-settle-static01,
  with the existing build and artifacts children.
- Canonical source: /home/arduino/sumox26_codex_build/<new_source_sha256>/app_motor_observe.

Check, intent, compile-outcome and artifact receipt schemas use the corresponding
app-motor-settle-static prefix. Do not relabel the unchanged adapter success
status or filenames. D188/D193 owners and artifacts remain untouched. Existing
historical owners do not substitute for new ownership; claimed, failed, partial
or uncertain D198 paths consume this attempt without automatic retry.

The exact future manifest files set is projected REQUIRED union every ordinary
file under src, bench/app_motor_observe and bench/motor_fault/src. It includes
the new launcher/this contract, original caller/remote/adapter and all inherited
dependencies. The existing source traversal includes
src/hal/motor_settle_probe.h and the changed src/hal/motor_port_unoq.cpp; the
unchanged mapping places both at the same src/hal paths in the sketch. No special
header staging rule is needed. Source-name/case/directory/plain-file checks,
512-file/1024-entry/4MiB bounds and source digest rules remain exact. Use the
completed, tested, reviewed D197 bytes in that later manifest, not a pending
implementation draft. There is no invented source digest or fixed historical
input-count substitution.

Retain the sketch's .ino/support mapping, allowed src/core/src/hal/src/app files,
src/config.h, and only the canonical motor_fault.h/.cpp shared trace copies.
No main-app .ino substitution or old app_motor_fault bench tree is admitted.
Fresh header/code pins change source identity; never reuse D193's old manifest
or source hash. Existing canonical source reuse still requires the exact full
source/directory/hash comparison and never permits repair or deletion.

## Inherited compile lifecycle and evidence boundaries

Keep the reviewed clean committed HEAD, exact CLI/board/dependency/hash checks,
fresh identity/boot, exclusive owners, durable intent and independent closing
checks. --check-only is local read-only admission: no owner/stage/board action.
--execute requires its selected output/pycache prefix and unchanged raw receipt
handling, one properties query and one compiler with jobs1. Query60s,
compiler720s and reap5s stay unchanged, as do the128MiB local and1GiB board free
space minima,30000UTF16 Windows command bound and original child/output limits.
No compiler retry, package install, boot change, source/configuration repair,
generic build-policy modification, upload/reset or MCU memory read is permitted.

Retain both local metadata validation and remote eight-file observation of
seven build artifacts plus exported flat package, exact installed loader/TLS
pins, full package equality/structure/native-TLS checks, all source postchecks,
first error and independent finalization failures. A successful compiler alone
is insufficient. Every required D188/D193 guard remains in force; only named
metadata and owners differ. D197's150us/4096 limits and probe0 safety behavior
are not modified here.

After a checked compile, a separate file-only ABI/entry task must observe the
new diagnostic report symbol, exact28-byte target layout and actual initialization/
store path. Do not reuse D194 runtime addresses merely because the sketch name
is unchanged, and do not claim ordinary host accessor tests prove target symbol
retention. Any later capture must bind this new image and report window with
fresh ownership. Compilation proves neither the settle failure's cause nor its
repair, live RAM/stack/WCET, production memory qualification, electrical behavior,
motor permission, physical acceptance or a human gate.

## Independent controlled validation

Freeze new oracles before their authors read the new launcher. Preserve and
privately reuse the D193 assertions with only checked metadata/fixture
projections and new tests for this delta. Historical inputs are:

| Oracle | Bytes | SHA256 |
|---|---:|---|
| tests/tooling/test_app_motor_observe_compile.py | 29767 | ae42938cace40745068421bf6e8e813295b12c16b376c93bd00b019b311b724d |
| tests/tooling/test_app_motor_observe_compile_remote.py | 8787 | 897ae6e468aaa619ff72fa03532278458a250cfc440add52fd8eff180d587413 |

Retain all59 caller and35 remote/adapter methods and all historical assertion
semantics, including the already reviewed Windows symlink privilege skip and
Linux descriptor fixtures. Keep original failures and fixture-repair history;
do not edit or weaken any old test. No new fixture repair is presumed by this
contract; retain and adjudicate any unexpected first failure before changes.

Add independent exact launcher reconstruction/count/hash and projected-byte
checks; unchanged adapter/project/status/source mapping; new header inclusion
and omission/drift refusal; fresh owner/schema/manifest/command identities; old
D188/D193 identities supplied as current packets rejected; unused new owners
required while old evidence remains untouched. Retain import/no-dispatch,
invalid CLI, strong bootstrap, private composition/HARD_PINS/REQUIRED/self.code,
actual projected remote/adapter, full artifact/TLS/export refusals, first-error/
closing behavior and realistic Windows command-size tests with zero native
dispatch. Run both host platforms serially after freeze and preserve actual
receipts plus input hashes. No host test may access the board or sleep natively.

Source/test/receipt review and D197 closure precede preparation of an actual
manifest and separately admitted single compile. No additional contract or
generic framework is needed to perform the bounded implementation above.
