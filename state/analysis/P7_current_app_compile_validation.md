# D185 current-app compile-only host validation

STATUS: IMPLEMENTED / HOST-TESTED / REVIEWED; no D185 native attempt.
Source/scopes freeze: commit6c938ada, final_freeze.json. Final caller aed3fbf4,
main oracle9caf2709 and supplement462e2466; both actual manifests have115 exact
current file pins (104 source files plus11 dependencies/caller/contract).
App source37a2099f; all setup declarations remain disabled.

Final retained validation used Python3 -B on WSL, with controlled endpoints and
RAM fixtures. Main27methods PASS36.333s; supplement7methods PASS10.229s; both
processes exit0/no timeout. The actual argv/stdout/stderr/source/oracle hashes
are in P7_current_app_compile_raw/durable_final/test_final_main.json and
 test_final_errors.json. SHA256 respectively:
6bf5c9c90196a3ad4d14f7bb4e89335747da0a9677905f47801cbf04ee89e3f8
49823ae62f6ab8fe8edb8c433aafc720666c4e87b1c6216bf1c83a3c8dab1038.
These are script tests, not current board compilation or hardware qualification.

The separate reused-context same-model review has no open finding; it is not a
fresh-context/cross-model phase-gate review. See
../reviews/P7_current_app_compile_review.md, SHA256
94fff07d2b563a323bbd95b806e04b3e87c69d12a7b98e17bc9a419e61b00e3f.
One closed MINOR added the plain ADB ancestry check before hashing. Frozen
executor and wait/reap body pins remain unchanged.

Original main failures (empty synthetic artifact hash map) and supplemental
fixture failures are retained in test_run01.json/supplement_run01.json and Git.
Independent author/reviewer adjudicated only the new fixture corrections;
assertions and all established/locked tests remain unchanged. Main test_run02
passes the preceding source; the durable_final receipts validate final source.

Real C: ENOSPC interrupted receipt retention. test_run03.json remains zero bytes,
and no result is inferred. A later observed27+7PASS RAM-first run lost its raw
receipt availability before recovery; test_run04.json/supplement_run02.json are
zero-byte failed Windows copies. Do not use that run as retained raw evidence.
A recovery helper SyntaxError occurred before filesystem mutation. The final
rerun above fsynced evidence to /home/ubuntu/sumox-d185-recovery-20260925/;
separate review read/hash-checked it. Exact bytes were restored to durable_final
and the review path after space recovered. Its original checkpoint.json records
the earlier pending state and is retained unchanged; this closure supersedes it.

Current free space/source/manifest pins and absent owners were rechecked at
closure. No native D185 operation, staging claim, upload/reset, binary download
or motor authorization is established. No source/config/pin/locked-test change
occurred in this evidence-restoration task. All physical/human gates, original
static full-app IO fault, RAM/stack/WCET qualification remain pending.

Next: on a clean committed reviewed HEAD, invoke --check-only for bench, then
one --execute with its prescribed isolated pycache path; the caller rechecks
fresh board identity/prerequisites and >=128MiB local/>=1GiB board space. Close,
review and commit bench evidence before the separate match profile. A claimed
owner consumes its attempt even on failure. MATCH here is compile-only; no
upload/reset permission. Review actual artifact identity before reusing any
historical file-derived accounting. Existing denied cleanup paths stay intact.

## Actual bench/default compile after host closure

Reviewed34eb56ba, native session90473 exit0, 25Sep16:47:46-16:53:53Dubai.
One query and one compiler,227transports, all7independent closing checks PASS.
Outcome native_bench01/result.json is COMPILE_CHECKED; build6d9e48f8b648469787bc8623ae05d163.
Compact exact receipt/command and comparison are in bench01_binding/ beneath
P7_current_app_compile_raw. RawELF72a8bfcd/package5b400268 match D139 exactly;
debugELFccc8990a differs. Same pinned loader permits reusing file-derived model:
592B deficit and61resolved imports, under historical assumptions. No fresh ABI,
live RAM/stack/WCET or physical acceptance follows. Compiler reported177100B
program/257848Bglobals/4296Bremaining and low-memory warning. No upload/reset;
D184's halted isolated diagnostic remains the last image. Bench owner consumed.

Separate reused-context actual review b02287cf PASS/no material findings;
see ../reviews/P7_current_app_bench_actual_review.md. It confirms227transports,
ten successful reaped child processes,115pins and103staged/remote source hashes.

## Actual MATCH/Immediate compile

Reviewed80c059f7, native session52257 exit0, 25Sep16:58:24-17:02:33Dubai.
One query/compiler,21transports, all7independent closing checks PASS. Existing
canonical source was accepted by exact filename/hash comparison without push.
Outcome native_match01/result.json is COMPILE_CHECKED; build1fcc7d57d66848cd9ea604297538e125.
Compact exact receipt/command and comparison are in match01_binding/. RawELF
cb5fbb53/package004d51bf match D138 exactly; debugELF2245bacd differs. Same pinned
loader permits reusing existing conditional byte-derived model:261280B peak in
262144B,864B span/860B largest payload,62resolved imports. These are not observed
live RAM/stack or WCET results and not fresh debug ABI queries. Compiler reports
174972B program/256440B globals/5704Bremaining plus low-memory warning. No upload
or reset; the last MCU image is still the halted D184 isolated diagnostic.
Both D185 caller owners are consumed. Current source, config and locked tests
were not changed by either compilation. Exact bytes eliminate duplicate binary
downloads while fresh receipts bind current source/profile/dependencies/artifacts.

Separate reused-context actual MATCH review20ea1645 PASS/no material findings;
see ../reviews/P7_current_app_match_actual_review.md. Both current target builds
are now separately reviewed. No phase/human/physical gate is authored.
