<!-- Condenses PLAN 6.4 and the implemented mode and button interface. -->
<!-- Gives operators a printable selection aid without claiming readiness. -->
<!-- Review against config, types, countdown, UI renderer and P5 acceptance. -->
# Mode card

**D137/D138 preparation draft — not operator-ready.** Use only with the verified
[runbook](RUNBOOK.md). Release/config: ____________________
Enabled modes: ____________________ Default: ____________________

## Choose from the accepted, enabled modes

| Opponent behavior | Planned choice |
|---|---|
| Charges straight at the whistle | SIDESTEP either side, or WAIT if available |
| Waits or turns slowly to face | DIRECT, or ARC if available |
| Spins while scanning | DIRECT |
| Tracks well with side sensors | DIRECT; rely on re-flank |
| Lower/sharper wedge than ours | SIDESTEP or available ARC; never DIRECT |
| Barely moves | DIRECT |
| Unknown | SIDESTEP_R, current default |

**Round 2:** after a loss, change mode; after a win, keep it unless the opponent
visibly changes its opening. **Round 3:** choose the mode that counters what they
did in the round they won. These changes depend on organizer permission. If mode
changes are prohibited, PLAN's fallback is SIDESTEP_R for the day.

| ID | Mode | Matrix glyph | Opening |
|---|---|---|---|
| 1 | SIDESTEP_R | 1 + right arrow | Pivot away, short burst, turn in |
| 2 | SIDESTEP_L | 2 + left arrow | Mirrored sidestep |
| 3 | DIRECT | 3 + up arrow | Straight approach; push after qualified contact |
| 4 | ARC_R | 4 + right curve | Arc toward the opponent's rear |
| 5 | ARC_L | 5 + left curve | Mirrored arc |
| 6 | WAIT | 6 + pause | Wait up to 2 s; react to approach, otherwise hunt |

Current config: default **1**, ARC **enabled**, WAIT **enabled**. Availability is
not physical acceptance. Disabled optional modes are skipped without renumbering.
If the 28 September P3 scope cut applies, only modes 1–3 remain. Optional openers
must pass their required physical block or be removed; confirm the release card.
No pre-angled placement is assumed without the organizer's answer.

## Controls, once physically qualified

- In inhibited **IDLE**, release all buttons first. Short MODE advances once on
  qualified release: under 600 ms after MODE qualification. Holds of 600–999 ms
  do nothing. Hold MODE continuously for 1 s after qualification to toggle services;
  its release does not also advance. Debounce is currently 20 ms.
- Services enter **SENSOR_VIEW**, then short MODE cycles **QTR_CAL → DRIVE_TEST →
  LOG_DUMP → SENSOR_VIEW**. SENSOR_VIEW displays on selection. Long MODE returns
  to the retained match mode. Ordinary MATCH has no runnable DRIVE_TEST action.
- START press/release in match view requests the countdown; in services it requests
  that service. A boot-held START is not accepted. MODE during countdown cancels
  it without also changing the selected mode.
- Current hold: **5.1 s after completed release debounce**. Both-button STOP needs
  BOTH debounce and a complete 1 s hold; its electrical decoding remains unqualified
  in the current source. Use the runbook's verified physical stop procedure.

**READY display, after physical qualification:** release the buttons and observe
the right-hand R blink on/off/on, nominally 500 ms per page. A frozen R or mode
glyph alone is insufficient. The rightmost pixel just above the battery bar is
bright at/above 10.8 V, dim below, off when unavailable in qualified IDLE. Require
live R plus the bright marker. Neither is motor-run permission.

Dim sensor markers mean unavailable, not detected. The bottom row remains a
13-step battery bar (development scale 9.5–12.6 V); alternating pixels mean unknown.
The R can be withheld by a fault even when control permits an IMU fallback.
Native startup/ownership, calibrated voltage and visibility remain unqualified;
see [D138 software evidence](../state/analysis/P7_readiness_validation.md) and
[SC-AP](../state/analysis/spec_conflicts.md). A host image or external reading
does not replace physical acceptance of the original matrix criterion.
STOPPED remains inhibited; optional D103 evidence-service reset cannot rearm a match.

Sources: [PLAN §6.4](PLAN.md#64-mode-selection-guide-print-this-card-for-match-day),
[B13](BEHAVIOR.md#b13-modes-and-ui), [config](../src/config.h),
[mode IDs](../src/core/types.h), [gesture contract](../src/core/countdown.h),
[renderer](../src/hal/ui_display.cpp), [P5 acceptance](../state/analysis/P5_software_acceptance_packet.md).
