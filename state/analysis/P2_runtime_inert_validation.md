# D104 bare-board actual Runtime probe

2026-09-23 Asia/Dubai. IMPLEMENTED/HOST-TESTED/TARGET-COMPILED. The separately
reviewed final source is2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5.
No sensor/pin/physical/phase approval follows. User freshly confirmed bare UNO Q
and authorized testing; only a reviewed no-pin inert run is in scope.

## Implemented and independently checked

The probe uses one actual Runtime, checked inert Gate callbacks, empty Source,
ADC and Dump ports, and all false SetupGrants. It runs200s of actual micros,
requires200000 completed actual epochs/zero misses, then freezes genuine
Runtime RUNNING/Robot BOOT/recorder EMPTY. It never invents STOP, time, sensor
freshness or motor receipts. Counter, deadline and clock failures remain explicit.
Stack measurements sample PSP at callbacks only and are not historical watermarks.

Frozen author tests:18cases/5,301,218assertions normal+ASan/UBSan, three unsafe
macro profiles refused. Final separate reviewer suite21cases/5,901,690assertions
normal+ASan/UBSan. Its real closing-deadline finding D104-R1 was corrected once
and its unchanged regression passed; original failure and initial image retained.
Full existing host suite passed in isolated reviewer workspace; D103 core/Runtime
implementation is unchanged. See review/raw and root_failure_analysis.md.

Exact app/probe filename binding preserves the84 effective build recipes and
all old app guards. Default/MATCH=0/MOTORS_ALLOWED=0 only for this probe; invalid
modes fail before transport even for compile-only. A new source key is limited
to this probe. Upload checks the returned checked build directory and both
reviewed ELF and package hashes; compilation, source or byte mismatch prevents
upload. No app/motor upload path was opened. Original seven keys are unchanged.

Coordinator guard tests plus75established policy tests,24opaque spec-derived
new decoder methods and39unchanged oldcapture methods:148PASS, exact receipt
P2_app_build_raw/d104_policy_upload_final.json/.txt. Decoder author did not read
the Python implementation but had prior C++ runner context; fresh reviewer
separately examines capture guard and final target. No cross-model claim.

## Exact target

Checked default compile receipt360b0e9f766643f98b29c6f6d68b9656 exits0.
91sources/79objects/3ELFs/package/constructors/retained imports/ABI and source
maps pass actual-target audit and independent reviewer. 86shared files are
byte-identical to D103. Final ELF8be8768a... and packageeb1d2b5b...124996bytes;
complete hashes in target_capture_pins.json. Payload233120B, modeledpeak236968B,
span25176B/largest25172B in262144B pool. Conditional model is not observed load.

Diagnostics232B/BSSoffset166624; Runner166584B; Runtime166304B; reserved main
stack32768B. No native peripheral owner/call retained. Empty strong loop hook
avoids core background Bridge servicing. All target evidence is retained under
P2_runtime_inert_raw/target_2bd817c4 and target_sources_2bd817c4, plus ABI/auditor
scripts. Initial1cd2f6cc source/target remains superseded, never uploaded.

## Capture and pending run

The separate runtime_capture.py preserves old D091 entry and immutable helpers.
Exact tool/config/loader/helper/artifact hashes precede private RAM. Fixed MEM-AP
reads only,48reads/2MiB/16KiB-RAM/64commands/600s/30s-per-command hard limits;
precomputed maximum48reads/914080bytes with at most3extensionnodes. One-node
actual expectation46reads/913688bytes is a budget, not a measurement yet.
Two identical terminal diagnostics and unchanged descriptor/heap metadata are
required. Pure decoder preserves failures and wraps and emits ordered acceptance
reasons. CAPTURED and acceptance.passed are independent.

Final capture/upload review and identified run record must precede execution.
No D104 upload/reset/read has occurred as of this software checkpoint. Current
MCU remains D0911502e948. Physical sensor/motor/WCET, full-app load, D103 active
reset, native UART, calibrated clock and every human gate remain pending.

Final scoped review PASS:109independent policy/decoder +9capture guards;
final_approval.json binds source/ELF/package/capture/boardguard/orchestrator/manifest.
Identified run is approved within the user-authorized bare-board scope, pending
commit and execution. No open D104 source/capture BLOCKER or MAJOR.

## Actual identified board run and capture

Software/runrecord1fa2a01 preceded the one upload. Fresh checkedcompile receipt
49aaf6a759164599850e6407ad22092d reproduced both reviewed hashes. Uploadexit0
at18:56:06UTC. Capture began after227seconds without reupload/reset, exited0.
Deployed loader/sketch identities, relocatedBSS and all raw hashes verified.
50commands/46MEM-APreads/913688bytes,275.400s; each command within its bound.

Actual FROZEN/NONE, RuntimeRUNNING/RobotBOOT/recorderEMPTY:200001epochs,
zero missedreleases, elapsed200000311us by MCUclock, maximum actualS..C269us,
maximum bracketedRunner285us. Token200001 and all callback counts consistent.
Zero enabled/nonzero/invalid requests; all31absence bits set and initialization
false. These are checked inert callback values, not electrical waveforms.

Both terminal diagnostics identical, sequence4; both full pool images also
identical. Current pool free payload28668B, largest25172B, used233348B,
overhead128B (total262144). This agrees with the model's largest remaining
span; temporary loader allocation has been freed. SampledPSP headroom30952B
within reserved32768B, delta64,35374939samples matching actual clock callbacks.
This is sampled callback-site headroom, not historical stack watermark.

Pure decoder acceptance PASS with no reasons. Actual evidence and coordinator
recheck: raw/runtime_run1, capture_run1_manifest.json and runtime_summary.json.
This succeeds only for the exact absent-source probe; it does not establish
full app load, live sensor fault/timeout800us over5minutes, calibrated time,
D103 reset, native UART, motors or physical/EXPLAINED/human phase gates.

Independent actual-run review PASS:149rawmanifestfiles,91committedsources,
exactdeployedbytes,232B literaldiagnostics,46fixedreads/50commands and independently
walkedheapfreerings allverified. No open finding; see actual_run review receipt.
