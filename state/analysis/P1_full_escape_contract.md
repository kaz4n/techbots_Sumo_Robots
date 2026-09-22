# Full Escape public contract — 2026-09-22 Asia/Dubai

Objective: complete B4's production selection, continuation, replanning and
approved inhibited recovery around existing Guard/RowExecutor components.
This is P1 host work under D-016; no new hardware operation or gate.

Sources: BEHAVIOR B4/B6/B7/B8, D-020/021/023/044 and D-047..D-051;
separate audits P1_escape_remaining_contract.md and P1_full_escape_contract_review.md.
The former's pending-choice wording is historical; D-049/D-050 approved it.
D-054 now records the remaining lifecycle choices under D-051.

Committed interface is src/core/edge.h: explicit RowExecutor::startPushedOut,
EscapeSample/EscapeResult/EscapeFault and stateful Escape::step/reset. The full
header comments define payload consumption, priorities, exact replan accounting,
phase-boundary order, permission/fault behavior and inward-evidence pulses.
Caller owns genuinely fresh confirmed line samples, current fusion centering,
previous FINAL applied duties and shared D-047 opponent-side history. It cannot
use this component to bypass governor/MotorGate or claim QTR acquisition works.

Row pivots retain the B7 relative target through Turn::startRelative. Preparation
found an existing float-target precision problem: a RIGHT45 pivot from -1e-6F,
then healthy yaw40F, rounds its absolute target to45F and misses strict error<5.
The captured relative command has error4.9999990000000025 and should finish.
Add an independent NEW locked regression; preserve all established cases.
This repairs representation of the existing strict threshold, not a tuning change.

Implementation owner: worker, src/core/edge.cpp only. Root owns shared headers,
decisions/spec/build/state. Independent test-author owns new locked tests and
reads specifications/public headers, not implementation cpp. Separate reused
read-only reviewer checks frozen diff, tests and evidence; no full gate claimed.

Acceptance: all16 patterns, pushed-out precedence/duty boundaries/mirrors,
head-on shared-side capture/default, new-bit phase/direction boundaries,
persistent-white completion, third/fourth replacement, fault/reset/permission,
finite-context consumption, inward validity, wrap/delayed calls, low-voltage
governor inhibition and full unchanged suite + sanitizers. Test results pending.
