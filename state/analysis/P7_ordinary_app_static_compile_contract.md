# D208 proposed ordinary-app static compile-only contract

26 September 2026. **Unadopted proposal** under D051 software continuation.
The coordinator accepted the D207 actual review at commit 5172dd9a. Its final
review is pinned below. Formal D208 adoption and independent contract review
must precede implementation. This document and companion
state/analysis/P7_ordinary_app_static_compile_raw/compile_derivation01.json contain requirements and data calculations only.

Prepare one current ordinary src/app/app.ino compilation with static linking,
default startup, MATCH=0, MOTORS_ALLOWED=0 and probe=0. Preserve every production
and configuration byte and every zero setup grant. D207 diagnostic acceptance
does not establish an ordinary-app artifact or runtime result. No upload, reset,
MCU read, installation, source repair, motor permission or gate is granted.

## Fixed baseline and permitted executable

After adoption, add only tools/compile_ordinary_app_static.py as the production tooling executable.
Preserve all historical sources, tests, receipts and consumed owners. Retain
D203's bootstrap and privately project the same three original D188 inputs.
This is not a metadata-only port: exactly six caller seams change ordinary
source selection, mapping, digest cross-check and ownership.

| Input | Bytes | SHA256 |
|---|---:|---|
| tools/compile_motor_const.py | 7557 | 957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247 |
| tools/compile_app_motor_fault.py | 29802 | cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a |
| tools/app_motor_fault_static_policy.py | 8262 | 3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270 |
| tools/app_motor_fault_compile_remote.py | 6891 | 1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2 |
| state/analysis/P7_current_app_compile_raw/compile_current_app.py | 29311 | aed3fbf4db5c962761affd5a3e2e52b1002feaaefe4e44f9f34df6ec78ba5ede |
| tools/match_deploy.py | 26266 | 3acacad6e95aff1012e9d0d1f8ef60905c026ebe865569fdb71384abd607d2a9 |
| state/analysis/P7_motor_const_compile_contract.md | 11305 | 318a6267f29a5837d6afe7197d6f86d88230886f1dd8ea0bb1af0345a4c75174 |
| state/analysis/P7_motor_settle_compile_contract.md | 14344 | c0b352810c41c8b3744acdd1c15bc4b21ecb76bc15d76d4fedea4fdde37dc756 |
| state/analysis/P7_app_motor_fault_compile_contract.md | 11098 | 204e0d3a8299972e545c1fffb92785955d78690fe87133e990018081eaf47826 |
| state/analysis/P7_app_motor_fault_static_contract.md | 5465 | 21b572bf9f3ec105814f7421fee2447e6c12551ba2a61f53d994b9b1abd57688 |
| state/analysis/P7_current_app_compile_contract.md | 9021 | 2f2c90d58913c208aadef126733e465d4bf6de249b5065147e2ff870391174d4 |

Accepted predecessor reviews:

| Review | Bytes | SHA256 |
|---|---:|---|
| state/reviews/P7_motor_const_compile_review.md | 19413 | c68852ff788e3c862e0d2c83cbbff23e9e53e69f77a4d3b4d7b3906619bcc9d1 |
| state/reviews/P7_motor_const_compile_actual_review.md | 10135 | 9c3e8cfe07ae33cac8d4a91f74127c33d3929e299bd5da339934943d784f21df |
| state/reviews/P7_current_app_compile_review.md | 9581 | 94fff07d2b563a323bbd95b806e04b3e87c69d12a7b98e17bc9a419e61b00e3f |
| state/reviews/P7_app_motor_fault_static_final_review.md | 2088 | 1bc4b4db5a497222026abdb33d7d3136caaf9a5c0d1d873f7aa65324f13dd76e |
| state/reviews/P7_motor_const_run_actual_review.md | 14825 | b562488423fce03712e0156deba21f52fddc826f096c70dcb1736d78aee71937 |

The companion pins all 150 current inputs, including 105 current source
files, original runtime dependencies, historical tests and these reviews.
It records ordered metadata substitutions, intermediate identities and old
function spans. Every baseline must match before projection. D203's original
Windows full-stamp failure remains preserved with its unknown-cause disposition;
it does not permit relaxed guards.

## Exact profile and fresh owners

- PROJECT app.ino; FQBN arduino:zephyr:unoq:link_mode=static; startup default.
- Flags exactly -DMATCH=0 -DMOTORS_ALLOWED=0 in both C and C++ properties. Do not append a probe
  or alternate-profile define. Preserve the inherited discovery property.
- SUMOX_MOTOR_FAULT_PROBE stays at the pinned config's zero default. All checked-in
  auxiliary profile macros and all 17 APP_GRANT declarations stay zero.
  Preserve the ordinary setup/loop and configuredSetupGrants mapping.
- ATTEMPT ordinary-app-static01; RAW state/analysis/P7_ordinary_app_static_compile_raw.
- Manifest RAW/inputs_static.json; schema ordinary-app-static-inputs-v1.
- Local output RAW/native_static01 and its exact isolated pycache child.
  Stage owner build/stage/ordinary-app-static01 contains child app.
- Remote owner /home/arduino/sumox26_codex_build/ordinary-app-static01 retains
  commands, build and artifacts children.
- Canonical source /home/arduino/sumox26_codex_build/<source_sha256>/app.
- Check, intent, compile-outcome and artifact schemas use ordinary-app-static.
  Overall success remains COMPILE_CHECKED; remote success ARTIFACTS_CHECKED;
  adapter layout success STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS.

Any claimed, partial, failed or uncertain attempt owner is consumed. No automatic
retry, deletion or reuse. Historical current-app, fault, observe, settle and const
owners/artifacts cannot substitute. Existing canonical source reuse requires its
plain ancestry, exact single app child and complete source/hash/directory equality;
it never permits repair. Local proposed launcher/output/stage absence was observed
during this proposal. Remote absence, current boot and identity remain unobserved
for this new operation and require fresh admission.

## Public interface and bootstrap

Preserve parse_request(argv), project_caller(raw), project_adapter(raw),
project_remote(raw), read_original(relative, *, root=ROOT), load_caller(*,
root=ROOT), main(argv), and returned CompileDiagnostic. Preserve all lifecycle
method names/signatures, including source_names(self) and
source_mapping(self, code, names). The optional root remains a fixture seam.
Accept exactly --check-only|--execute --reviewed-head <40lowerhex>; validate
types/order/count/head before loading and require Python -B. No new CLI mode.

Keep the eleven D203 launcher function bodies recorded in the companion exact:
require, parse_request, _verify, _project, project_adapter, project_remote,
_stamp, _plain_chain, _read_handle, read_original and main. Permitted additional
changes are comments, identity/projection tables, project_caller with bounded
count-checked transformation helper(s), and load_caller's private module name
and explicit pin extension. No generic policy/framework or projection cache.

Retain full ancestry and one-link .py checks, symlink/reparse/special-file
refusal, O_NOFOLLOW/O_NONBLOCK where supported, immediate descriptor validation
before reads, 65536-byte source maximum/65537-byte read, all same-API stamps,
original Windows cross-API ctime exception only and primary-over-close errors.
Do not transplant the separate ABI executable-mode exception.

Verify all three originals and all three complete projections before private
caller execution. Keep original caller __file__, false historical main guard,
injected project_adapter/project_remote and fresh private ModuleType named
_sumox_d208_ordinary_app_static_compile. Do not register modules globally,
instantiate owners, read sources or dispatch during import. Preserve original
self.code snapshots and all inherited HARD_PINS. Extend original caller/remote
pins exactly as D203 and add the pinned tools/match_deploy.py. REQUIRED remains
the existing union with HARD_PINS, using the new launcher/contract identities.
Only its app_source_hash helper may be called; no match-deploy qualification,
main, upload or other operational entrypoint.

## Caller metadata table and six semantic seams

Project the exact original D188 caller. Apply these nine ordered substitutions,
requiring each original count:

| Old literal | New literal | Count |
|---|---|---:|
| CALLER = 'tools/compile_app_motor_fault.py' | CALLER = 'tools/compile_ordinary_app_static.py' | 1 |
| P7_app_motor_fault_compile_contract.md | P7_ordinary_app_static_compile_contract.md | 1 |
| P7_app_motor_fault_compile_raw | P7_ordinary_app_static_compile_raw | 1 |
| app-motor-fault-static | ordinary-app-static | 6 |
| 'app_motor_fault.ino' | 'app.ino' | 1 |
| -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1 | -DMATCH=0 -DMOTORS_ALLOWED=0 | 1 |
| STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS | STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS | 1 |
| self.code[ADAPTER] | project_adapter(self.code[ADAPTER]) | 2 |
| self.code[REMOTE_HELPER] | project_remote(self.code[REMOTE_HELPER]) | 2 |

The resulting intermediate is 29819 bytes /
402fea3fdb0f2b1af99dff3f4a80afebf63529ae05466958b957ac1bd6038275. **It is incomplete for this scope.**
Then transform exactly the six whole method spans recorded in the companion
by name/signature/length/hash. Each old span must match exactly once. All bytes
outside those spans after the metadata table stay exact. Existing unrelated
checks inside the spans also remain. Freeze final caller/launcher identities
after implementation and before host execution; no future body hash is guessed.

1. **source_names:** traverse only self.root/src, retaining the inherited stack,
   plain ancestry/type checks, portable relative paths and 1024-entry/512-file
   bounds. Include all ordinary files in the manifest inventory, including
   unmapped .gitkeep files. No bench input. This is D185's src-only scope.
2. **source_mapping:** replace diagnostic bench/Trace mapping with the ordinary
   destination rules below, consuming checked code snapshots and the exact
   src-only name set. Return the same destination-hash dictionary and digest.
3. **__init__:** change only stage_path's child to app. Preserve counters,
   ownership flags, deferred source/boot/manifest state, borrowed methods and
   output/build/artifact paths.
4. **admission:** preserve strict manifest schemas/types/keys, immutable
   re-admission snapshot, every input hash and inherited hard pin, checked wait,
   source-size bound, mapping/manifest digest equality and executor boot checks.
   Change canonical sketch child to /app. Privately load the checked pinned
   match_deploy bytes through the existing local module seam and require the
   real app_source_hash(self.root) return to equal both snapshot-mapping digest
   and manifest source_sha256 on every admission. A fixed return, copied digest
   or mocked success cannot satisfy the actual admission requirement.
5. **source_admission:** change only expected owner-child list to ['app'].
   Preserve source_attempted timing, checked_source_set, exact equality,
   exclusive creation, directory setup and strict reply/first-error behavior.
6. **stage:** use self.board.stage('app', attempt=ATTEMPT). Preserve fresh owner
   and free-space checks, exact returned path, expected_stage dictionary and
   board.source_hash equality, exact staged-directory set, repeated local checks,
   staged_files evidence, command-owner creation/identity, source admission,
   checked per-file pushes and final source closure.

Ordinary mapping must match the pinned match_deploy.app_source_hash:

- src/config.h and every src/core or src/hal file retain their paths.
- Under src/app, a first component src maps to the sketch-local src/... path.
  Reject reserved local config.h, core, hal or app entries, including lexically
  present empty or linked reserved entries; mapped-file collision alone is
  insufficient.
- Other src/app .c/.cc/.cpp/.h/.hpp files map under src/app/<tail>. Other top-level
  files except .gitkeep retain their basename. Ignore other unmapped files in
  staging while retaining them in the checked source manifest.
- Require app.ino; reject sketch.yaml/sketch.yml/sketch.json. Reject unsafe or
  reserved relative paths, duplicate/case-folded destinations, more than 512
  mapped files and more than 4MiB mapped bytes.
- Hash sorted destinations using the pinned helper's sorted(mapped, key=Path)
  order, feeding UTF-8 destination, NUL, then exact bytes. Real helper,
  independent source_mapping and later board.source_hash(stage) must agree.

Data-only transcription found 105 source files/764405 bytes and 104 destinations/
764405 bytes; only src/app/.gitkeep is unmapped. Calculated digest:
9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.
This is not an invocation of the helper or an actual staging/admission result.
Future host checks and manifest preparation must execute the real pinned helper
and cross-check this value. The companion gives every input and destination pin.
With unchanged source, the exact prospective manifest is the 105-name source set
union the 20 required tooling/contract names, totaling 125. Count alone is never
substituted for exact set equality. Do not reuse a diagnostic or old app digest.

## Adapter and remote projections

Apply exactly three metadata substitutions to the original adapter:

| Old literal | New literal | Count |
|---|---|---:|
| 'app_motor_fault.ino' | 'app.ino' | 1 |
| -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1 | -DMATCH=0 -DMOTORS_ALLOWED=0 | 1 |
| STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS | STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS | 1 |

Data-derived expectation: 8219 bytes / d1a78ad713d0550ed52805a6751640823a31ce4e96edafc3c058a7587c5e4863.
All seven aliases now map app.ino plus each suffix to itself:
.elf, _debug.elf, _temp.elf, .bin, .bin-zsk.bin, .elf-zsk.bin, .map.
Retain identical artifact byte objects, complete legacy report and isolated
return maps. Identity aliases and reference replacements do not bypass checks.
Keep the exact 84-property/24-project/5-flag occurrence checks, even though the
project and flag replacements are identities. All private snapshot imports,
metadata/library/path/recipe validators, native TLS/ELF/package/layout checks
and exported-flat/build-package equality remain unchanged.

Apply exactly five metadata substitutions to the original remote:

| Old literal | New literal | Count |
|---|---|---:|
| app-motor-fault-static01 | ordinary-app-static01 | 1 |
| 'app_motor_fault.ino' | 'app.ino' | 1 |
| -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1 | -DMATCH=0 -DMOTORS_ALLOWED=0 | 1 |
| app-motor-fault-static-artifacts-v1 | ordinary-app-static-artifacts-v1 | 1 |
| 3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270 | d1a78ad713d0550ed52805a6751640823a31ce4e96edafc3c058a7587c5e4863 | 1 |

Data-derived expectation: 6845 bytes / 71c189ea3c354b7ccb969b35ae3f1a92a517380735059d00ff4c735b45cf4389.
Keep bundle hash/compressed-source coupling, all descriptor/root/regular/size/
link/identity checks, seven build files plus exported flat package, installed
loader/TLS pins, first-error precedence, independent postchecks and close handling.
Original files and self.code remain original bytes. These expected projection
hashes are byte calculations, not observed implementation or execution results.

## Preserved bounded lifecycle

Outside the explicit delta, D188/D193/D198 behavior remains normative: clean
committed reviewed HEAD, exact current input/tool/CLI/board/boot identities,
local read-only check-only, exclusive owners and durable intent. Execute requires
its selected output/pycache prefix. No owner, stage or native action in check-only.

Keep exactly one expanded-properties query/60s and one compiler/jobs1/720s,
5s reap, 30000 UTF-16 command bound, at least 128MiB local and 1GiB board free,
and all inherited child-output/memory/conflict/UID limits. Preserve CLI
initialization and builtin prerequisites, precompile installed pins/override
checks, metadata checks and every closing check. Do not fix a historical
transport count: current source count determines checked file pushes.

Preserve eight-file artifact observation, all native TLS/package/export checks,
installed loader/TLS closing identities, local and remote source closure, raw
query/compiler/transport receipts and independent finalization errors. Compiler
exit zero alone cannot yield COMPILE_CHECKED. No retries, package install,
generic policy/config/source change, upload/reset or MCU access are allowed.
Preserve initial failures; repairs require separate independent adjudication.

Only after contract adoption, source/oracle/host closure and independent review
may the coordinator prepare an actual manifest/scope, admit fresh resources/
identity/owners, commit a clean reviewed head, run local check-only, then execute
once. This proposal makes no device call and grants no ordinary runtime action.

## Independent acceptance requirements

The independent author must freeze from this contract and pinned historical
fixtures before reading/hashing/importing/executing the new launcher. Keep old
oracles untouched; declare counted/hash-checked fixture projections, exact method
names/counts, platform selection and each ordinary-profile semantic adaptation.

D203's 69 caller and 38 remote/adapter methods are the baseline coverage
obligation. Preserve every applicable bootstrap, descriptor, private-load, pin,
CLI, ownership, staging, query/compiler, artifact, error and closure assertion.
Transpose only the changed profile/flags/project, src-only mapping, six seams,
helper pin, identity aliases and owner/schema/status/projection metadata.
The old exact metadata-only launcher test becomes exact metadata plus six-span
boundary verification; it cannot assert an unchanged caller or require benches.
Enumerate that adaptation explicitly rather than silently dropping a method.

Retain old fault, observe and settle negative owners/artifacts and add D203 const
owner/source/manifest/artifact refusal. Ordinary app.ino with two inhibited flags
is now positive. D187's former rejection of that pair must become coherent stale
diagnostic/probe-flag refusal, preserving the rejection assertions. Do not globally
rewrite old negative inputs into valid current ones. D185's MATCH/dynamic policy
remains historical and is never imported as a permitted new compile path.

Cover all 33 D187 adapter behavior methods for the actual ordinary projection,
including the methods outside D203's selected subset; report overlap explicitly.
The 27-method D185 oracle and seven error methods supply ordinary mapping/staging/
failure assertions. Reuse applicable semantics without claiming those historical
profile-specific whole suites prove this new caller. The new independent freeze
must list actual selections and additions; this proposal invents no total count.

Focused additional acceptance:

- Exact allowed byte/AST transformation boundary, unchanged bootstrap, mutation/
  missing/count/hash refusals, no import I/O/dispatch/module leakage, unchanged
  original paths/pins plus the single pinned match_deploy dependency.
- Real pinned app_source_hash on synthetic ordinary trees, agreement with the
  snapshot mapper and actual board.stage fixture, helper-pin/digest disagreement
  refusal and real re-admission. No success-only admission stub.
- Current 105/104 source/destination set and numeric digest; source/header/config/
  app drift refusal, no bench inclusion and unmapped-source manifest coverage.
- Nested support/sketch-local mapping; empty/linked reserved entries, duplicate/
  case collisions, missing app, overrides, path/special-file/reparse/symlink and
  existing count/size bounds.
- Exact app.ino/default/static/two-flag command; probe0 and all grants unchanged;
  one query/compiler, no upload; owner consumption, wrong child/extra directories
  and every stale source/owner/artifact negative.
- Seven identity aliases through the complete real validator; unchanged reference
  counts; TLS/ELF/package/export corruption refusals; primary-error precedence
  and complete independent finalization evidence.

Run future host suites serially with exclusive saved receipts on Linux and
Windows, -B/isolation, explicit bounded timeouts and exact input freezes.
Windows TEMP/TMP/TMPDIR must be dedicated before process startup; Linux fixtures
use uniquely owned /dev/shm storage. Controlled fixtures block real compiler,
board, transport and native sleeps. Cover Linux descriptor/filesystem cases
behind explicit Windows skips and report any actual uncovered limitation.
Preserve/adjudicate first failures before changes; no old-test edits, filtering
failed methods or weakened assertions.

## Evidence boundary and next action

Freeze observed future launcher and private caller identities after implementation;
they remain null in this unadopted companion now. Before any host test or native
use, the implementation must contain concrete original and final projected
byte-length/SHA256 checks for all three bodies. No runtime None, wildcard,
unchecked projection or skipped _verify is permitted. Seal a separate immutable
implementation identity receipt after six-seam construction. Its metadata may
be supplied to the independent oracle author without exposing the new body;
behavioral expectations remain contract-derived and the author must still freeze
before inspecting the implementation. Source review must verify that the concrete
checks match the sealed receipt and the permitted transformations.
Adapter/remote expected hashes above are
reproducible byte derivations only. Recheck every current pin before execution.

An accepted ordinary static compile would establish current file artifacts and
structural layout for this inhibited profile. Loading, live RAM/stack, ordinary
runtime/timing, recorder ownership/rearm, physical sensors/motors, motor permission
and human gates remain separate. Any later file-only ABI/entry query must derive
addresses from that actual ordinary ELF. Any runtime or deployment needs its own
fresh bound scope.
