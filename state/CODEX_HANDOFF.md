# Codex handoff - 26 September 2026, Asia/Dubai

## Current result

D195 longer inhibited observation reproduced a native SETTLE callback failure at
application 921. Read [actual validation](analysis/P7_app_motor_observe_actual_validation.md)
and its linked raw evidence/review. The latest flashed image is D193 source
3a08ddeb/static/default/MATCH0/MOTORS_ALLOWED0/probe1, raw BIN f1df5e7f and
package85b05c56. D190's earlier four-epoch observation remains historical.

At clean reviewed HEAD10be3126, check-only and execute returned0. One upload,
one capture,13transports,26reads727152B and four complete flash comparisons
passed. The 30-second pre-sample and2-second separation waits completed. All six
SRAM pairs are byte-identical; coherence is still UNPROVEN. One subsequent
file-only query verified14saved files18017B with closing rereads. Nothing was
downloaded from the MCU during that file retrieval.

Observer FROZEN/CALLBACK_FAILURE at921epochs/115539polls. First failure is
APPLY/SETTLE returnedfalse with154us outer span. Trace preserves64successful
prefix calls and5485omitted calls, plus first_failure/current. Saved pre-abort
runtime is RUNNING/NONE, but the motor receipt is invalid/IO. Final explicit
abort produced runtime/transaction faults; final HALT/SETTLE also failed and
inhibition_confirmed=false. Software did not confirm inhibition. Zero requests
and MOTORS_ALLOWED0 do not substitute for electrical measurements.

The completed instrumented transaction/stored maximum is859us, above the800us
target for that sample; this is not production WCET. A successful SETUP/SETTLE
also spans154us, so the outer durations do not identify the internal150us timeout
branch. Original fault cause remains open; no safety limit has been relaxed.

## Exact next task

D197 probe-only internal SETTLE report is implemented and hostvalidated:
sourcef1ee755a/header2eced554, separate28Bcurrent/first_failure, explicitvalidity,
existing150us/4096pollbounds/nativecalls preserved. FiveindependentmethodsPASS,
21scenariosx3exactoriginal0/current0/current1transcripts; productionprobe0
preprocessedbody/symbolsexact. Locked76cases217020assertionsPASS;140pinsstable,
no temporaryremnants, reviewbe2ff77ePASS. Read P7_motor_settle_probe_validation.md.
Two harness-only failures are preserved; no assertion or firmware repair occurred.

D198 fresh fixed compile-tool hostvalidation/review PASS: contractc0b35281 and
launcherb98a5f54,102Linux/81WindowsPASS21coveredplatformskips,167pinsstable,
review50a276b9. Originalnewfixture/admissionobserver failures are preserved;
corrections changed neither assertions norproductionguards. New129pinmanifest
aa314548 binds source117cc0e7/108stagedfiles780479B; readonlyadmission1c6c5ca3
verified same-boot identity, installed pins and unused owners before execution.
D198 actual compile now passes at clean reviewed HEAD18c1135c: one query, one
compiler, 238 transports and all eight closing checks. Result9b7f0c44 and
artifact receipte18384c1 bind ELF6091f27d/debugdc610650/packagee4000781 (95520B).
All129 source pins remain exact; app-motor-settle-static01 is consumed.
See analysis/P7_motor_settle_compile_actual_validation.md and its actual review.
D199 file-only ABI reader passes66 Linux/64 Windows methods with two skips
covered on Linux,192 frozen inputs exact and review076a9742 PASS. Its actual
native_abi_static01 now succeeds atclean23f0aeba: result230ef847/ABI069ed01b,
localeb68ef2e, four file children0 and all13remote+localclosingchecks PASS.
Actualreviewa7c3993a verifies143localpins/23groups/11windows and the separate
28B/align4 report at0x2003d3e8, all11fieldpairs/ninereasons. ABIowner consumed.
Next derive fixed entry ranges from that rawsymboltable and inspect publication
instructions. Actual report contents and failure branch remain unknown; D195
is still flashed. See analysis/P7_motor_settle_abi_actual_validation.md.
D200 clarifiedcleanupcontract6cb02590 is adopted; exactrecipe6afeea1b/wrapper
13f33327 are prepared, independenthosttests/source-review/staging stillpending.
Read-onlyinventorye95ebed4 binds three D195 scratch copies2399768B/dev34inode1172.
No new root04 staging/authentication/deletion has occurred; oldscopes consumed.

Every earlier native owner is consumed, including D193static01, D194ABI01/02 and
entry01, D195run01 and D196root03. Never rerun historical launchers or repin their
manifests. Any changed firmware needs new checked artifacts and observed ABI/
entry before a separately reviewed inhibited scope. Do not reuse old addresses.
No native process or local execution session remains active at this checkpoint.

D194 actual ABI02resulta5e67635/ABIdfc34596 and entry61c7b090/e195fdeb establish
the D193 layout/instructions only. Original ABI01 GDB syntax failure remains
preserved. Windows executable-stat0111 exception is narrowly reviewed and all
other identity checks remain. D195 preparation8acf1b13/fieldmapb96b6a3e and
reviews98e0a956/ac506885/5a7944ed bind its91LinuxPASS and48WindowsPASS with43
explicit Linux-only skips; these do not automatically validate changed source.

The full objective remains active. analysis/P7_completion_audit_20260926.md
lists production memory/loading, operational commissioning, recorder lifecycle
and release dependencies. The current ordinary app static compile is a useful
next task after fault localization; historical static evidence is not a current
source build. D185 dynamic profiles retain their modeled memory blockers.

Existing app.ino already binds operational B4; missing work is profile/build/
deploy admission (analysis/P7_b4_profile_scope_followup.md), not another entry.
B4 terminalSTOP cannot use the current IDLE-only UART dump. Use separately bound
retained-RAM capture first or define/review a new policy; do not enable local
reset silently. Motor-capable execution requires fresh STAND OK or RING OK.

## Cleanup and authentication

D191 and D196 exact authenticated cleanup invocations completed once and are
consumed. D196 result321e6e5c removed exactly three D190 scratch copies2399736B
and their empty directory; original files unchanged, all mutations UID1000,
permanent privilege drop successful. Actual review0131ea59PASS. New D195 upload
scratch, if present, requires fresh observation and a separate exact binding.
Never reuse root03. Staged sources/results remain useful provenance.

User-supplied authentication was passed through stdin, never retained in files
or argv. Do not repeat/store it. Those scopes grant no general privileged access.
Earlier CLEANUP DONE clicks did not run commands; preserve original refusals.

## Boundaries and schedule

Active phase P7 software/release preparation under D051/D075/D122/D137. P0-P5
physical/human acceptance and P7 release remain open; P6 is conditional. No
STAND/RING/PINMAP or human phase gate exists. Sensor/electrical acceptance,
actual RAM/stack/WCET, D121 B7/R6, native UART dump lifecycle and SC-AP release
remain open. Header IO stays3.3V. Connection alone creates no acceptance.

Actual P3 not passed by end28Sep invokes reactive+SIDESTEP/DIRECT+recorder and
drops ARC/WAIT/P6 polish. P6 also needs actual P4 by30Sep. Freeze1Oct21:00Dubai,
rehearsal2Oct, competition3Oct. Scheduled dates create no gate.

## Storage and resumption

The user restored over21GB C: space; recheck before large jobs. Keep unique raw
receipts/source/hash-based reproduction, avoid duplicate firmware/debug/source
snapshots and bytecode, run heavy builds serially. Preserve board originals and
every prior policy-denied cleanup target listed in STORAGE_LOG.md, including
old85.48MB hostoutputs, both motor-fault stages, build/stage/app,2Binput.wire and
37historical stagefolders. No alternate deletion route or paging/disk changes.

Read AGENTS.md fully, docs/prompts/CODEX_RESUME.md, CODEX_EXECUTION.md and latest
PROGRESS/DECISIONS/FACTS/TUNING_LOG. Preserve user work; bounded local commits,
no remote push/history rewriting. PROGRESS is append-only with legacy bytes:
first140971B SHA256
1dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77.
Historical checkpoints remain in Git; this is the current next action.
