# D135 independent review — PASS within software scope

2026-09-24. Separate fresh-context same-model Codex; not cross-model.
Contract `2aa0ac2e`; production `2d924f1f`; draft corrections `94a7bb5d`.
Findings: no open BLOCKER, MAJOR or MINOR in this reviewed D135 scope.

- Source PASS: actual predicate/route, full 64-bit receipt ownership, chronology,
  classification priority, one candidate, all append attempts and loss handling.
- Integrity PASS: 656 frozen inputs and 42 existing protected files unchanged.
  Original oracles, first failures and narrow correction evidence are preserved.
- Host PASS: all 20 targets; public 40/private 13 per M0/M1. Configured public 42
  and private 13 per profile PASS; both matrices also pass ASan/UBSan.
- Tooling PASS: new 18 methods, admission 74 and prior regression 296.
- Layout PASS: 72 legacy size/alignment pairs versus `d6a8319e`; P5 measured
  separately. Original precompile harness failure and exact placeholder fix retained.
- Eight isolated fault probes PASS under ASan/UBSan: route/state/token, tag/owner/
  phase loss and both exhaustion paths. All modified-copy hashes reproduced.
- Native compile/policy and conditional model fit PASS for inert P5/M0 only:
  ELF `9583f94d`, modeled free 1328 bytes, 61 used imports resolved; 44 artifacts
  and report rehashed. DWARF confirms Pending 88, Tick 200 and Runtime 166424.

Verdict: **PASS for D135 software evidence and the new safety-test candidate**.
Default-app 32-byte modeled deficit remains independently open. Live load/free
RAM/stack, 800us WCET, source/clock qualification, extraction and physical 10/10
trials remain unproved. No motor-run authority, hardware acceptance or gate follows.
This reviewer ran no compiler/test or board/network/motor operation; root ran checks.

Evidence: [source](P5_abort_timing_review_raw/source_review_preexecution.md), [receipts](P5_abort_timing_review_raw/host_native_receipt_review.md), [final hash binding](P5_abort_timing_review_raw/final_receipt_review.json).
Original chronology: [preserved checkpoint](P5_abort_timing_review_raw/review_pre_final_checkpoint.md).
Next: record scoped closure; continue separately authorized offline work.
