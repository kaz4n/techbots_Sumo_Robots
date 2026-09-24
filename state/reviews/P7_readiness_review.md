<!-- Reviews D138 against the adopted informational-readiness contract. -->
<!-- Keeps a current software snapshot separate from motor and physical authority. -->
<!-- Tests-first source review and source-bound receipts; no board or motor action. -->
# D138 informational readiness software review

2026-09-24 Asia/Dubai. Separate fresh-context, same-model reviewer. Scope: baseline
`54a688e9` through the unchanged first D138 production implementation `d19f8964`,
final host freeze `0fe188b7` (687 inputs), and the bound operator-document updates.
Adopted contract SHA-256:
`568bc27719e32d397dfcfe7130558e952b53f0f651430a89c6b8d6a66b00904a`.
This is not a cross-model review, human phase gate or physical acceptance.

## Findings

**No open BLOCKER, MAJOR or MINOR.**

Three issues in the new, unaccepted test draft were corrected separately by its
spec-only author, with original sources and first failures preserved:

- `test_readiness.cc:57`: typed byte-array fills replace aggregate `memset`
  rejected by `-Werror=class-memaccess`. All sentinel values/assertions remain.
- `test_readiness_runtime.cc:206-207`: parentheses preserve the complete existing
  disjunction while avoiding doctest's forbidden expression decomposition.
- The low-marker case assumed a filtered warning delay. Source and B14 review
  established that `power_inputs.cpp:194-198` supplies accepted voltage unchanged,
  while the baseline `fsm_robot.cpp:936-940` immediately raises LOW_BATTERY in
  IDLE. Only governor compensation is filtered (`governor.cpp:68-78`). The final
  case requires the correct warning and explicit IDLE/valid/raw9000 preconditions,
  preserving marker/no-R/zero-output checks. Pure renderer cases separately test
  contradictory voltage/latch inputs. No firmware or established test changed.

Original evidence: `normal_first`, `configured_first` and `configured_retry1`
receipts/logs under `analysis/P7_readiness_raw/`. The last failed execution passed
30 of 31 cases per M0/M1; the corrected source passes every case below.

## Source and behavior review

Read the independent new tests before the frozen implementation diff. Actual
Buttons arming and the existing `allow_start` expression are observed without
resampling, independent debouncing or new control authority. The Lifecycle tail
extraction preserves statement order. Current presses, replay, menu changes,
passive/exhausted calls and reset cannot retain eligibility. All designated
bench/evidence profiles suppress it.

Runtime binds the metadata at the original post-application, pre-C point to a
fresh DECIDED transaction, nonzero matching token and genuinely consumed valid
receipt. R additionally needs actual MotorGate NONE, zero/disabled inhibited
IDLE, current qualifying sources and ordinary M1. Service-only/reset/cancelled
contexts cannot become match readiness. The existing observed clock is reused;
no clock call, native write order, recorder encoding, grant or transport changes.

The renderer remains configuration-independent and default-unbound compatible.
The original float comparison changes row 6 column 12 only; the literal R uses
its defined 3x5 region and even blink pages with all-clear inputs. Battery-bar,
fault, invalid, service/calibration and non-IDLE priorities remain intact.
Existing START/hold/governor/MotorGate behavior is unchanged.

## Host evidence reviewed

The reviewer inspected command receipts, raw logs and complete test summaries,
then independently rehashed them. All builds used one compiler and owned scratch.

| Check | Result |
|---|---|
| Ordinary M0/M1 | 20 cases / 22,118 assertions each, PASS |
| Full ordinary/profile suite | All 22 CTest targets PASS, including 1,519 main cases and 187 enabled-Gate cases |
| Configured M0/M1 | 29 public + 2 private cases each; 104,489 / 104,854 assertions, PASS |
| Ordinary ASan/UBSan M0/M1 | 20 cases each, PASS |
| Configured ASan/UBSan M0/M1 | 31 cases each, PASS |

The final warning-case correction is wholly inside the configured-button branch.
Four preserved preprocessing commands prove byte-identical ordinary M0/M1
translation before/after; the full 683-input run therefore remains applicable.
Final configured and sanitizer receipts bind all 687 current inputs unchanged.

The two private public-fixture probes were frozen at SHA-256
`9d835d130a686afd3698dba62461b4964ee7206c5b0b001e6d2649396a0b1138`
before execution. The actual matrix callback verifies current receipt identity
while completion C/duration evidence is still absent. A subsequent injected
terminal clock failure confirms that the last submitted R can remain without
another submission. Both cases pass normal/sanitizer M0/M1. No private production
access shim or new test framework was added. See
`P7_readiness_review_raw/host_receipt_check.json`.

## Native artifact and final binding

Independently rehashed 75 native evidence files plus 5 dependencies, all 102
staged source files, the checked ELF, all 687 frozen current inputs and all 43
protected files. The single checked MATCH1/MOTORS_ALLOWED1/Immediate compile
uses `--jobs 1` and returns 0. Source `fcddbd8e`, ELF `cb5fbb53` and all 62 used
imports bind to the recorded current loader. All 16 queried target sizes/
alignments and 72 queried legacy member offsets match prior MATCH. The three
new bools occupy existing padding; Runtime remains 166,304 bytes.

Independent allocation arithmetic confirms peak 261,280 bytes in the assumed
262,144-byte pristine pool: 864-byte remaining span, 860-byte largest payload.
The model assumes its documented persistent-peek/alignment and allocation
premises. It is not measured live RAM, default/M0 fit, stack or loading evidence.
See `P7_readiness_review_raw/native_binding_check.json` and native report
SHA-256 `97aa4eee4314e474389de95158ad7c44901a4a3b03198ed5cc34d539030e4c8e`.

Final coordinator binding SHA-256:
`2241442e3bef1cb159665f66cc313639d1d17c0bb72248bffcac8b46ddcc28a0`.
The review independently verifies its five passing receipt hashes, eight document
hashes and exact eleven-path code-change list. The saved 140,971-byte historical
PROGRESS prefix is byte-identical; the entire Git baseline prefix is preserved
after newline normalization. The initial raw Git-prefix probe rejected existing
mixed CRLF bytes; that audit-method correction is recorded without ledger edits.

RUNBOOK/MODE_CARD retain a conditional post-qualification workflow requiring
live R alternation plus the bright accepted-voltage marker. The final validation
packet correctly separates current software evidence from native/physical
acceptance. Root's closure receipt records 82 local links / 9 fragments checked.
Reviewed principal document hashes:

- RUNBOOK: `efc83ab8df03bc2b610eb372d3150e344746cf42778dc63da848c99c0656f6be`.
- MODE_CARD: `35930ae3371b81ad67e38b723faa51c40c7a0631ccc17b7cd37149ad3e571437`.
- Readiness validation: `82b4d4578c8a4f4a9cd05b4f69e50203821de1ee1d29cb82020ddb04153faf9a`.

All reviewed document hashes and raw-evidence bindings are retained in
`P7_readiness_review_raw/final_receipt.json`.

## Verdict and limits

**PASS for the scoped D138 software change and its documented evidence.**
No open finding remains. Only this review and its small probes/receipts were
written by the reviewer; no implementation, configuration, established test or
ledger was edited. The reviewer performed no compiler, board/network, upload,
reset, MCU or motor operation.

R is a decision/application snapshot before C, not completed timing, future
health, electrical inhibition or motor permission. A frozen frame cannot prove
continuing blink. Native matrix normal-startup/exclusive ownership versus MATCH
Immediate, calibrated voltage, optics/failure visibility, full rearming/dump,
loaded RAM/stack/WCET, physical acceptance and human gates remain pending. The
separate default-profile qualification and later work are outside this verdict.
