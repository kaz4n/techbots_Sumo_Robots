# D176 finite diagnostic capture validation

IMPLEMENTED / HOST-TESTED, 25September2026 Asia/Dubai. No board operation.
Initial implementation b1619ccd/96fb8935; original independent38-method oracle
255ae4cc frozen01fb3d16 before execution. First38PASS4.247s. Contract author used
literal metadata/real find_bss and did not inspect/import subject or decoder.
Separate fresh-context same-model source review4eddcdb5 found twoMAJOR inherited
issues: expiry during final checks could report success, and stream cleanup could
mask prior child failure/outcome. Original FAIL report and source remain retained.

Independent supplemental8-method oracle initially223c17d8 frozen959c8fbf had one
unexecuted fixture instrumentation issue: observe/set clock before a deliberately
failing final read, not after it. Exact approved correction changed no assertion;
ready917595aa frozen53a7adb0. Baseline8methods reproduced34failing subcases in1.458s
against original96fb8935, receipt committed47458815. This was reproduction, not
an unsuccessful source repair. No established/locked assertions were modified.

First source repair7b7e8c69, SHA
95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e:
- Enforces total600s deadline after independent final checks.
- Preserves actual child outcome/primary exception before cleanup; independently
  attempts both streams' flush/fsync/close and retains later cleanup errors.

| Fixed-source suite | Result | unittest time |
|---|---|---|
| Independent finalization8methods, including30stream subcases |PASS|1.500s|
| Independent diagnostic38methods |PASS|4.040s|
| Unchanged legacy static collector46methods |PASS|2.757s|

Commands/exit statuses/output/times are in P7_motor_fault_raw/capture_first.json,
capture_finalization_first.json and capture_repair1.json; freezes accompany them.
All use WSL Python3.12.3 with Python-B, TMPDIR=/dev/shm and
PYTHONDONTWRITEBYTECODE=1. Fourteen final input pins unchanged. Root in-memory
syntax compilation passes; no new function exceeds60lines. All owned RAM scratch
was removed, verified in capture_closure.json. No hardware call, target build,
download, source/binary snapshot or consumed scope rerun.

Final review ../reviews/P7_motor_fault_capture_review_final.md SHA93ef66a7 PASS:
original fresh-context reviewer reused for repair; bothMAJORs closed/no new findings.
Reviewer inspected source and coordinator receipts, did not execute tests.

New collect_motor_fault reuses existing execution/evidence machinery and actual
bounded find_bss. Whole flash identity precedes RAM; 1/2/3-node traversal and
8-byteBSS alignment precede two2592B snapshots, followed by complete raw relocation
and flash comparisons. Successful maximum24reads/593424requestedB; malformed,
changed and failed reads stop collection and retain evidence. Tests exercise exact
sequence, region bounds, full node bytes, ownership, first-error/final checks,
599.999/600/601deadline, stream cleanup and offline valid/fault/malformed decoding.
COLLECTED means raw observations gathered with those checks; coherence UNPROVEN.
No lifecycle, motor permission, physical acceptance or gate follows.

D175 uploader remains source67eccbc5/e926b7ba. Old compile/ABI/static manifests keep
their historical whole-source pins; intentionally do not repin consumed scopes.
D160 remains the last upload. Next use the verified source-neutral
CompileOnce.transport/prerequisites primitives with a thin fresh scope, bounded
compact responses, conditional upload/capture and independent local closure.
See P7_motor_fault_capture_plan_notes.md; no rebuild or cloned framework needed.
