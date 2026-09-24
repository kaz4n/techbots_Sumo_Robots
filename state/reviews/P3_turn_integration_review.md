# D125 isolated P3 turn integration scoped review

Date: 2026-09-24. Reviewer: separate same-model review agent, independent of the
implementation and public test author. The reviewer previously performed
read-only surface exploration; no D124/D125 implementation or public oracle was
authored by this reviewer. This is a software review, not a human phase gate.

Status: PASS for the bounded D125 software slice. No open BLOCKER or material
source finding. The current 137-file freeze and all 36 established locked files
match; the new safety oracle is accepted at SHA-256
`7d6c5193` (full digest in the freeze). This is not physical acceptance or GATE P3.

Scope: D125 contract/public interfaces adopted in `ebe34983`, the implementation
diff following it, actual Robot/Transaction/Runtime/MotorGate seams, profile-only
storage, native wrapper and checked compile tooling. The reviewer may edit only
this report and `P3_turn_integration_review_raw/`; isolated temporary host build
fixtures do not modify production or public tests. No reviewer board operation,
upload, reset, MCU read/write or physical motor operation is performed.

## Preflight and source trace

- The adopted contract deliberately retains D124 duplicate-time semantics.
  Owner inhibition and stopping do not depend on the helper cancelling during
  the same timestamp; a deferred helper STOP remains an honest observation.
- START admission shares D123's existing local service selection, classified
  line readiness and full actual Lifecycle hold. Default and B4 entry policies
  remain selected by separate compiler-wide profiles.
- The trial route runs after actual escape evaluation. Edge at GO cannot start
  the helper. During an escape the interrupted helper cannot resume, and the
  owner does not latch STOP until successful escape exit. Existing reset-only
  escape faults remain inhibited in EDGE_ESCAPE.
- TURN and BRAKE pass through PIVOT Governor and actual MotorGate. COMPLETE
  immediately inhibits and latches stopping; the next distinct Lifecycle tick
  performs STOP. Timeout retains its primitive status and full observed brake.
- The publication path handles faults arising after routing and token
  exhaustion. Action pulses are cleared on duplicate Robot observations.
- D103 resets the reconstructed Robot's helper report, while retained recorder
  frame/event evidence remains separate. The contract explicitly says that the
  wire format does not serialize this helper report. Runtime service-only raw
  line admission and the permanently stopped native Gate still prohibit rearm.
- All added instance fields are conditional on the new profile. Existing
  default, B4 and D123 object layouts are independently unchanged.
- The wrapper uses empty SetupGrants and asserts profile1/MATCH0/M0 plus the
  absence of the other experimental profiles. Tooling accepts only the exact
  new C/C++ flag tuple, default startup and compile-only path.

The traced implementation is `src/core/fsm_turn_trial.cpp` and the conditional
Robot wiring in `fsm_robot.cpp`/`fsm.h`, with the relevant Menu, UI and MotorGate
extensions. Existing Runtime/Transaction source admission, D103 reconstruction,
helper and escape machinery are retained. No ordinary combat route is selected
by the turn profile. BRAKE remains an admitted zero-duty BRAKE request: the
physical Gate is enabled in M1 only while every permission check passes, and
remains disabled in M0. COMPLETE immediately inhibits both.

## Preserved failures and oracle correction

The first controlled tooling run contained one literal-wrapper assertion failure:
the same required profile/MATCH/MOTORS predicates were separated by two stronger
profile-exclusion predicates. Reordering the unchanged conjuncts satisfies the
frozen test without altering behavior or test expectations. The original failing
run is retained, and the corrected run passes all 107 methods. Registry tests
pass both methods.

The first private configured Runtime case and the public configured sanitizer
case independently exposed the same fixture prerequisite: traversing QTR_CAL
left the real D089 RAW-to-CONTROL neutral rearm pending. An immediate START was
correctly suppressed. The correction establishes 30 neutral ticks and asserts
actual classified-line/button readiness before a fresh START. All original
motion assertions remain; no production change was needed. This changes only
the new, previously unaccepted safety oracle, from `b90ab55d` to `7d6c5193`.
Original public and private source, freeze and failed execution receipts remain
available. `freeze_original.json` and current `freeze.json` differ at exactly
this one oracle; all other 136 entries match. The reviewer additionally tests
that an early START during rearm cannot be replayed automatically.

## Bound execution evidence

`P3_turn_integration_review_raw/evidence_bindings.json` records PASS for 526
checks. The verifier independently checks current source/oracle identities,
protected files, test receipts and actual local ELF hashes; it re-evaluates the
stored checked-build properties and retained conditional loader model. Public
test runs were performed by the root; private probes and layout comparisons
were executed by this reviewer against isolated copies.

| Verification | Result |
|---|---|
| Full normal host suite | 8 targets PASS: main 1,519 cases; Gate 187; B4 18 each; D123 27 each; D125 28 each |
| Focused D125 ASan/UBSan | M0/M1, 28 cases each PASS |
| Configured Runtime normal and ASan/UBSan after correction | M0/M1, 29 cases each PASS; 338,964 / 332,026 assertions |
| -90, -180 and +180 configuration overlays | M0/M1, 28 cases each PASS per angle |
| Independent private probes | M0/M1, 4 cases and 59,587 assertions each PASS |
| Tool policy / registry | 107 / 2 methods PASS |

Private probes cover delayed timeout with a full observed 500 ms brake interval,
twelve edge/deadline combinations, real Runtime completion and D103 reset with
5,200 subsequent inhibited service ticks, and rejection/no replay of START while
line rearm is pending. The initial private failure and corrected freeze are
preserved separately. No production source changed during private execution.

Header-only `sizeof` probes against the pre-D125 headers show identical sizes
for Robot / RobotResult / Transaction / Runtime, respectively:

| Established profile | Before and after, bytes |
|---|---|
| Default | 2,640 / 400 / 162,616 / 166,624 |
| B4 | 2,696 / 424 / 162,696 / 166,704 |
| D123 DRIVE_TEST | 2,640 / 400 / 162,616 / 166,624 |

These are host layout checks. Actual default target ELF, packed sketch and loader
also match D123 byte for byte. Checked M0 compile-only receipts bind 98 staged
default files (`5c7df067`, ELF `21b28ee3`) and 99 turn-profile files (`fcf43381`, ELF
`f41e2cb7`). The turn image contains its dedicated route and omits the ordinary
routeNormal/checkStall/startOpener symbols. Both use the strong empty loopHook.
The independently recomputed conditional pristine-pool loader peaks/free spans
are 262,128 / 16 bytes for default and 250,720 / 11,424 for turn accuracy. These
figures carry forward the loader model's limitations; they do not qualify live
RAM, stack headroom or execution timing.

## Limits

Host callbacks and layout checks do not establish physical angle accuracy,
settling, fallback timing, on-robot WCET, pin/electrical acceptance, successful
recorder transport, motor-run permission or GATE P3. The native wrapper remains
M0 with no source grants, and the new profile has no upload allowlist entry.
Only checked compilation ran on the board's Linux side; no MCU upload, reset or
physical operation followed. P3 stopping-table support is outside this slice.

Next action: root may record and commit this scoped software acceptance and lock
the accepted new oracle. Physical turn/fallback measurements and the human phase
gate remain separate.
