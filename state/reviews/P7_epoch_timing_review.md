# D229 completed-epoch timing distribution independent review

Date: 27 September 2026, Asia/Dubai. Reviewer: fresh-context review-only agent.
Decision: **FINAL PASS for the scoped source and host evidence. No material
blocker.** This is not target RAM/timing acceptance or P2.2 qualification.

Reviewed isolated worktree `sumox-timing-p99-20260927`, branch
`codex/timing-p99-20260927`, at base
`004dc7cff534896a851901f9d7d0ba6066cae060`. Only this new review was written by
the reviewer. No production/test repair, commit, main-worktree mutation, board
contact, compile, upload or motor action was performed. The focused successful
suite was examined rather than rerun without a concrete concern. All four agent
slots were occupied, so no further review delegation was possible.

## Correctness and integration

- `N - floor(N/100)` is exactly `ceil(99*N/100)` without overflowing a uint32
  intermediate. Empty observations are distinguished from an actual zero-us
  sample. The first cumulative bin reaching the rank gives the correct integral
  p99; the 800-us exclusive boundary produces an explicit overflow tail. A small
  overflow tail does not incorrectly prevent an exact lower p99.
- Starting from the private zero-initialized state, every retained observation
  increments samples and exactly one bin or overflow. No individual counter can
  exceed samples. At UINT32_MAX samples, later observations cannot wrap a bin,
  overflow or sample counter. Rejections saturate explicitly; retained count,
  maximum and endpoint freeze while all-observed maximum and endpoint advance.
  SATURATED cannot be confused with an exact percentile for all observations.
- The uint64 cumulative sum safely covers all 800 uint32 bins plus overflow.
  A total differing from samples forces INCONSISTENT and overrides ordinary or
  saturated status. `p99_us` is valid only with retained_status EXACT, as both
  the source and contract state. This sum check intentionally does not establish
  coherent external acquisition or validate arbitrary corrupted metadata.
- `Runtime::completeEpoch` adds the observation only after successful
  `Transaction::finishAfter` and Runtime completion-clock acceptance, alongside
  the existing admitted-epoch counter. The unchanged transaction path validates
  S, decision/application ordering and C before producing the unsigned duration.
  Failed/incomplete transactions, pre-release polling and stale terminal calls
  cannot reach the observation. A completed admitted transaction remains in the
  population if subsequent stop bookkeeping faults, matching the contract.
- No new clock, scheduling, motor, recorder or wire-format operation is added.
  The fixed owner is appended to Runtime, and public access is const. Observation
  has bounded scalar work with no loop, division, allocation or I/O; summary has
  an explicit maximum 800-bin scan and is not called by the runtime hot path.
  The positive/bounded-range static assertion limits the diagnostic RAM budget.
  The only config addition is the diagnostic range; existing values are intact.

## Evidence independently reconciled

The reviewer read the new implementation/tests/runner, Runtime and Transaction
integration, unchanged fixture/allocation probes, contract and validation,
original failure artifacts and final closure. Current AGENTS, progress/handoff,
D051 and the original P2.2 requirement were checked. Today is the scheduled
27 September first-drive date; no human gate is inferred from the calendar.
The legacy referenced REVIEW_GATE.md is absent in this checkout; this scoped
fresh-context review follows the explicit delegated brief and existing rules.

All **173** successful-run input pins match the current files byte-for-byte,
and saved before/after pins agree. All **38** files bound by closure05 match
their recorded lengths and SHA-256 values. Existing `.gitattributes` and
STORAGE_LOG content remains an exact prefix; their changes append evidence
preservation/storage entries. `git diff --check` passed during this review.

The saved successful host run reports **16/16 cases and 316/316 assertions**,
with C++17/O1/warnings-as-errors, exceptions/RTTI disabled, UBSan/no-recovery,
heap wrappers, MATCH=0 and MOTORS_ALLOWED=0. All seven command return codes are
zero and all stderr files are empty. The tests use independent sorted-sample
rank oracles, overflow endpoints, wrap anchors, coherent near-limit seeded
states, rejection saturation, inconsistent sums and the actual Runtime fixture.
Three unchanged probes exercise actual Runtime allocation/cleanup behavior.

The failed Git-path run and original 15/16-case fixture run remain preserved.
Production input pins are identical across all three runs. Comparing the saved
original test to its replacement confirms the repair schedules a genuinely due
QTR frame and strengthens failure prerequisites to REQUIRE; it does not weaken
the asserted histogram outcome. The separate final-reporting KeyError is also
retained and repaired by POSIX path normalization in closure05.

Frozen principal evidence:

| File | SHA-256 |
|---|---|
| src/app/epoch_timing.h | 46960d854f19f863e737422937616223d3c961be35b20502c1d05b92b1be7c05 |
| state/analysis/P7_epoch_timing_contract.md | 42a98d99b1037366baf385b059e93ab7be9342cf8417fe0d362e7944c9cf49d7 |
| state/analysis/P7_epoch_timing_validation.md | bc79979de46dd8294e49a031a047fd2e50252bfa149995db32fc2f2c4e023a89 |
| state/analysis/P7_epoch_timing_raw/repaired_fixture03/result.json | 77e5f0cff21ce113341b58c42c3d50d206c6a46cf04f9b7c72991866eb9ec12f |
| state/analysis/P7_epoch_timing_raw/closure05.json | 29bd59ca8ddc404a484ffb81f293a438bc9e0748132d6f0a3798df1210cd439e |

## Acceptance boundary and next action

Accept the reviewed source and host evidence for coordinator-controlled
integration. Preserve the saved pins and failures when committing; no extra
source repair is requested. The coordinator records D229 in the main ledger.

The population is the object's lifetime prefix of admitted S..C completions,
not a five-minute window. Raw modular anchors do not prove elapsed duration,
continuity, all-sensor liveness or a coherent capture. Work before S, observer
cost, completion bookkeeping after C, failed/idle polls and the outer loop are
excluded. Original P2.2 still requires worst case and p99 over five minutes with
all sensors live, under 800 us, and later evidence must include full-loop cost.

Saved host sizes establish Data/Distribution 3236 bytes, Summary 44 bytes, and
Runtime growth from 166648 to 169888 bytes: **3240 bytes including host padding**.
They do not establish target layout, RAM fit, instruction cost or stack margin.
The added owner requires a fresh source-bound target build/layout and coherent
acquisition before any native timing claim; historical image addresses are not
reusable. No target or physical acceptance, specific motor-run authorization,
recorder delivery result, phase gate or release approval follows from this pass.
