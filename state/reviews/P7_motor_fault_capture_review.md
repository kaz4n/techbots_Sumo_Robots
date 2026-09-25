# D176 motor-fault capture source review

Scope: fresh-context, same-model, read-only review of the +262/-12 capture change in commit b1619ccd against D-176 and `state/analysis/P7_motor_fault_capture_contract.md` (SHA256 cb3a6dddb559abfdbf2f9e66f8dc547c7d3f90e84ce0fa5981d5b98225facb22).
Reviewed source: `state/analysis/P7_static_startup_raw/capture_remote.py`, SHA256 **96fb89356e985316856622e43c0186a50da517a6c96fe5e1e15baea8ae407aa4**.
Real traversal dependency: `tools/runtime_capture.py`, SHA256 a4d58b3cbac8b0a3cf96ce6d4f53bc17e935b9aee9bc1c09809ee20ea806fdae; inspected `find_bss` and its actual `p0_capture.ram_range` dependency.

- **MAJOR — state/analysis/P7_static_startup_raw/capture_remote.py:515:** The diagnostic API inherits finalization without a final deadline check. Successful gathering below 600 seconds followed by final file/identity checks crossing 600 seconds still reaches `COLLECTED`: `timestamp` accepts a finite increasing clock, and `complete` checks only counts/flags. After attempting every independent final check, record diagnostic budget expiry before deciding status; retain any earlier error.
- **MAJOR — state/analysis/P7_static_startup_raw/capture_remote.py:373:** The inherited default executor retains neither the child outcome nor a primary wait exception before stream teardown. A nonzero/timed-out result followed by flush/fsync/close failure is reported only as that cleanup error, losing the subprocess result; context cleanup can also replace a thrown wait error. Preserve the child outcome/primary exception before cleanup and record cleanup failures separately while retaining raw files.

Other inspected properties conform at source level: fixed detached bindings and fresh descriptor ownership; before-flash guard; exact flash/list/node/snapshot regions; eight-byte BSS alignment; real bounded traversal; immediate ordered raw relocation comparison; two same-address snapshots with checked separation; 24-command/593424-byte prelaunch ceilings including failed attempts; independent final checks; explicit UNPROVEN coherence; unchanged static run01/run02 admission and module constants.
Tests: not executed, as explicitly required for this review; independent D176 tests were still being authored. No native calls, source edits, imports, snapshots, compiler/cache generation or commits were performed. Only this short report was written. No runtime, physical, motor-run or phase-gate acceptance is inferred.

Verdict: **FAIL — two MAJOR findings remain open; no BLOCKER identified.**
