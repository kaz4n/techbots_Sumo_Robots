# User-requested pause - 2026-09-24T08:19:12.690758+04:00

**PAUSED. Do not continue until the user resumes.** Active software phase P4
under D128. Latest completed and validated implementation is D128 `3985da16`.
D129 contract/public-interface commit is `ca076b46`; the following saved draft
is NOT BUILT, NOT TESTED, NOT REVIEWED, and is not physical acceptance.

## Exact stopping point

D129 SC-AO bounded P4-only source-to-applied loss trace is partially implemented.
Read `P4_timing_evidence_contract.md` and `P4_timing_evidence_options.md`.
Default-off SUMOX_TIMING_EVIDENCE requires SUMOX_P4_REACTIVE. Its conditional
source window, event10 metadata, batch26, full-token receipt matching and inert
reactive_timing wrapper are drafted. Existing motion, pins, grants and default
recorder rate/retention are intended unchanged, but compatibility is unverified.

Saved source: src/config.h and src/core/types.h (contract commit); current
src/core/fsm.h, fsm_robot.cpp, fsm_timing.cpp, logframe.h, logframe.cpp;
src/app/runtime_inputs.cpp; tools/board_tool.py and app_build_policy.py;
bench/reactive_timing/reactive_timing.ino and README.md; host/CMakeLists.txt.
Raw runners in P4_timing_evidence_raw are prepared, UNEXECUTED. No freeze.json
exists. CMake references the not-yet-authored new tests, so do not treat this WIP
as buildable. The pause_manifest.json binds the draft and verifies all39 prior
locked source files unchanged. No new locked oracle has been established.

## First actions after explicit resume

1. Reload root AGENTS, handoff/execution, latest progress/decisions/facts/findings,
   active P4 prompt and D129 contract; inspect Git status and actual Dubai time.
2. Resume independent public test author (role/context p3_test_author) to write
   tests/p4_timing_fixture.h, tests/test_timing_evidence.cc,
   tests/locked/test_timing_evidence_safety.cc,
   tests/tooling/test_reactive_timing.py and analysis/P4_timing_evidence_test_plan.md.
   NONE of those files was written at pause. Author from specs/public headers and
   previous public fixtures only, no implementation .cpp reads. Freeze before execution.
3. Resume implementation owner p3_turn_impl for final draft inspection, function
   limits and integration checks (no new functionality). Root owns shared headers,
   config/build/Runtime projection and ledgers. Worker owns fsm implementation,
   codec, wrapper and exact build policy; nobody edits established locked tests.
4. Separate read-only reviewer p3_surface_map has authored NO D129 review/probes.
   It reviewed contract and emission bound only. Review the pending concern:
   during OBSERVING, can a backdated current TickTiming start plus a source window
   that remains after the candidate anchor survive a timing-only invalid prior
   receipt and yield misleading qualified evidence? Actual Runtime chronology is
   checked, but direct malformed caller behavior requires review/test. This is an
   OPEN QUESTION, not a reproduced finding. Also inspect token-exhaustion path.
5. Freeze independent expectations and production; run relevant new M0/M1,
   configured, sanitizer and existing host targets/tooling. Archive every actual
   failure and command; do not weaken tests. Then checked inert target builds and
   source/loader accounting, including unchanged app and uninstrumented D128.
   Prepared compile_target.py supports app, reactive_test, reactive_timing and an
   isolated synthetic configured-button overlay. No runner has been executed.
6. After passing separate review, document/commit D129 as a completed slice.
   Following P4 task is offline loss-trace analyzer with unchanged CSV validator
   and hash-bound rereads. P5 abort trace/native memory feasibility is separate.

## Settled clarifications

- Legacy line/sensor callers can qualify only if they additionally supply fresh
  valid explicit tick timing and opponent_read. No forced explicit LineEvidence.
- Current exclusions precede source pair; only otherwise-valid onset with lost
  preceding approach eligibility emits pair then EXCLUDED_NO_APPROACH.
- packEvent stays enum-only; validEventMetadata/appendEvent enforce TIMING metadata.
- Actual M0 Gate zeros cannot arm. Explicitly synthetic positive receipts may
  exercise Robot trace under M0; only HEADER motor bit differs, never hardware proof.
- Exhaustion receives prior receipt first, then closes an active trace once as
  INTERRUPTED_STOP_FAULT. No success may be retroactively canceled.
- Bound26: conservative legacy22 + at most4trace; HEADER exclusive of active
  candidate/receipt, terminal closure no replay. EventInput in-memory padding must
  be measured, not inferred from8-byte wire records.

## Evidence and limits at pause

No D129 host test, compiler invocation, upload, MCU reset/run or motor action.
Read-only ADB inventory at08:15:59Dubai listed device2629958581; this does not
verify firmware state or supply permission. All39 established locked hashes
match the pre-task baseline. Last actual MCU image remains historical D118;
its old run claims are consumed. Physical acceptance/human gates remain pending.

All three workers were interrupted and returned checkpoint-only summaries.
No build/test/tool session remains running and no work continues in background.
User explicitly requested this pause. Last known C: free178663424bytes; recheck
before artifacts. Use WSL /dev/shm builds and archive evidence in the same
invocation. Preserve progress bytes by append only. No push/tag/history rewrite.
