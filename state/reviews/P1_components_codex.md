# P1 standalone components — scoped peer review

2026-09-22, Asia/Dubai. **PASS** for this software scope, with no open BLOCKER,
MAJOR or MINOR findings. This is not a P1 phase gate.

Reviewer: separate read-only Codex context `/root/preflight_review`. A request to
spawn a new review context hit the tool's agent-thread limit; the prior P0 reviewer
received a new bounded brief. It authored none of these implementations or tests,
but this is explicitly a **reused context, not fresh P1 gate review or cross-model
review**. A genuinely fresh full review is still required at the eventual gate.
The coordinator transcribed this record from the reviewer's returned report.

## Reviewed scope and evidence

Diff from baseline `2c6e95d`: B0 types; separate countdown Gate and Buttons; B4.1
classifier; B5.1 debouncer and seven B5.2 front rows; D-017 governor; independent
tests; D-016/17/18 and updated architecture. The reviewer inspected actual source,
tests and contracts, then ran `tools/test_host.sh`: **exit 0**, CTest **1/1**,
doctest **77/77 cases**, **3,457,564/3,457,564 assertions**, **0 skipped**.
Raw result copied to `state/analysis/P1_core_tests.txt`.

- Fixed storage and bounded loops; no allocation, clock reads, hardware I/O or
  new global execution paths. Elapsed time uses unsigned subtraction.
- Boot-held START does not create a press; reset restores the qualification
  state. Gate hold, cancellation, STOP latch and wrap boundaries pass. Buttons
  exposes both timestamps without choosing the unresolved integration anchor.
- White levels persist, channel confirmation is independent, and opponent
  debounce counts saturate. Front rows match B5.2; `close=false` is not proof of
  far range and no-target bearing is explicitly meaningless.
- Governor compensates before final caps/slew; reductions, inhibit and braking
  are immediate. Reversal outputs zero before opposite acceleration. Full ATTACK
  duty requires centered AND contact. Double intermediates bound finite extremes.
- Initial test creation used unchanged predicates after build compatibility fixes;
  no established locked test was weakened. Independent test author did not read
  implementation `.cpp` files; see `analysis/P1_test_author.md`.

## Exact inert source snapshot review

All 13 staged files were inspected. The reviewer independently emulated the
staged hash mapping and verified it against the old baseline manifests before
approving these new hashes. The coordinator then used `board_tool.stage` and
`source_hash` locally and obtained identical results; no transport was invoked.

| Sketch | Approved source SHA-256 |
|---|---|
| `bench/p0_matrix` | `bf7722dc33b9d3557894b83bd9a6e98c223a6fb014981cb2127a7e3e651dbe5b` |
| `bench/p0_timing` | `62e5781dcd9f07a8b6285a6065d194c3f990423a243eee521d7280909d2a0ec3` |

The review approves manifest refresh for these exact inert sources only. Changed
sources still fail closed; Immediate matrix upload remains blocked by F-061.
It supplies no upload, motor-run, physical setup or human gate authorization.

## Remaining limitations

Button-to-Gate timing, other B3 services, full FSM/R5 escape arbitration,
target-loss brake integration, edge forward-cap choice, HAL/MotorGate, target
compilation and complete robot timing remain pending. The numerical 60-case P1
criterion alone does not satisfy missing table coverage or exit evidence.
No board contact, upload, reset or motor run occurred during review.
