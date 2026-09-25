# D162/D163 host diagnostic and build-route validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED; target compile pending.

D162 adds an inert callback trace and four-sample runner around the real MotorGate.
The fixed trace retains the first failed callback through cleanup, including an
unfinished-call marker. The runner submits only disabled, zero-duty commands and
halts once. Default setup permission is false. MATCH or motor-capable compilation
is rejected. Native callbacks, production limits, config and locked tests are
unchanged. Source commit: 90e73959; contract/header committed in c8dfa1cc.

The independent test author derived 18 cases from the contract and public header,
without reading implementation bodies. Expectations were frozen in 874b51c2.
The first invocation failed during compilation because the test driver omitted
doctest's no-exception assertion flag. Commit 0c009360 adds that flag only; every
assertion and implementation byte remains unchanged. Preserve both receipts.

| Validation | Actual result | Evidence under P7_motor_fault_raw/ |
|---|---|---|
| Normal focused C++ suite | 18/18 cases, 2570/2570 assertions | focused_driver_repair.json |
| ASan/UBSan focused suite | 18/18 cases, 2570/2570 assertions | focused_driver_repair.json |
| Driver suite, including three unsafe build-flag combinations | 3/3 methods, exit 0 | focused_driver_repair.json |
| Existing full host suite, one compiler | 22/22 CTest targets, exit 0 | full_host.json |
| New and existing compile policy suites | 65/65 methods, exit 0 | policy_import_repair.json |

Focused command: `wsl -d Ubuntu -- env TMPDIR=/dev/shm python3 -B tests/tooling/test_motor_fault.py`.
It completed in 42.414 seconds. All 46 repaired-freeze inputs remain exact.
The full matrix used the CMake flags in tools/test_host.sh with `--parallel 1`
instead of its fixed two jobs, then ctest; all three commands and outputs are in
full_host.json. Observed g++ 13.3.0, CMake 3.28.3, Python 3.12.3.

D163 adds five exact literals in two existing tools, commit 0a95b230. The new bench
uses the existing checked compilation and artifact validators. Only default/M0
compile-only is admitted; upload, MATCH, Immediate, profile files and foreign
run options reject before target access. No upload manifest or old source binding
was changed. Historical probes deliberately reject the new tooling hashes.

The 13 new policy cases passed on their first invocation. Eleven legacy fixture
imports failed because the caller omitted PYTHONPATH; policy_first.json retains
those errors. With caller-only `PYTHONPATH=tests/tooling`, all 65 methods passed in
23.635 seconds. No test/source edit was needed; all ten policy-freeze pins match.

Separate same-model reviews inspect source and actual receipts, with no remaining
material findings: [D162](../reviews/P7_motor_fault_review.md) and
[D163](../reviews/P7_motor_fault_build_review.md). D162 began in a fresh context;
D163 reused that reviewer context. This is not cross-model or human gate review.

All compiler/fixture directories were RAM-backed and removed after results were
captured. A fresh check found zero sumox directories in /dev/shm. Retain compact
source, frozen inputs, original failures, final receipts and reviews; no extra
firmware binary or source snapshot is needed for these host claims.

Next: one identified target compile using explicit installed CLI/config/environment,
one compiler and a board-side process deadline/reap. D163 does not itself provide
those execution bounds. Do not inherit capture/upload file-size limits into a
compiler. No target compile/upload/reset occurred in D162/D163. The diagnostic
changes timing and cannot retroactively identify D160's original callback; setup
may still block inside unchanged native code. D160/D161 remain consumed. Native
startup, physical acceptance, WCET and human phase gates remain pending.
