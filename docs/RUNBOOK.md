<!-- Prepares the original P7 operator workflow and release prerequisites. -->
<!-- Keeps current software limits separate from future physical operation. -->
<!-- Review against P7, PLAN, current UI sources and linked acceptance packets. -->
# Match-day runbook

**Preparation draft updated through D219/D221 actual results, 26 September 2026. NOT OPERATOR-READY.** Print only
after the release owner fills and verifies the release record below. Writing
this runbook supplies no deployment, motor-run permission or human phase gate.

Use the [mode card](MODE_CARD.md) and [rehearsal/scouting sheets](REHEARSAL_SCOUTING.md)
with this document. The competition is Saturday 3 October; the planned dress
rehearsal is Friday 2 October. All times below are Asia/Dubai.

## Release prerequisites — currently open

The checked-in app maps explicit `config.h` declarations into its setup grants;
all remain disabled, with mounting and button windows unconfigured. D180 prepares
that mapping without enabling any hardware. It cannot provide this operator
workflow as shipped. D138 defines
a blinking **R** and an exact battery-threshold pixel for qualified IDLE samples;
their software validation is recorded in the [readiness packet](../state/analysis/P7_readiness_validation.md).
The native matrix's startup/ownership and physical visibility remain unqualified.
A mode number/arrow alone is not readiness; the battery bar is not numeric voltage.

| Required before using the workflow | Current boundary / evidence owner |
|---|---|
| Identified runnable release and deployment | D221 loaded the fixed B4 motor-disabled application on the bare board. D219 captured retained memory and exported an EMPTY recorder (zero frame/event rows), with complete loader/sketch comparisons before and after the reads. All setup grants remain absent. This does not qualify an operational robot release, native UART delivery, initialized timing or live memory. Record the source/config/artifact and qualified deployment using the [current P7 packet](../state/analysis/P7_software_acceptance_packet.md). |
| Hardware and usable controls | PINMAP/electrical qualification, calibrated battery reading, actual sensors, distinct button levels including BOTH, visible display and source setup remain required. [P2 packet](../state/analysis/P2_software_acceptance_packet.md) lists the missing evidence. |
| Original P7 display criterion | Qualify D138's live blinking R and battery-threshold pixel on the actual release matrix, including native startup/ownership, calibrated input, visibility and failure behavior; see [open SC-AP](../state/analysis/spec_conflicts.md). An external meter does not replace this criterion. |
| Motion and opener acceptance | Resolve the real starts, stopping/edge, combat and opener criteria in the [P3](../state/analysis/P3_software_acceptance_packet.md), [P4](../state/analysis/P4_software_acceptance_packet.md) and [P5](../state/analysis/P5_software_acceptance_packet.md) packets. Each powered practice attempt needs fresh STAND OK or RING OK bound to that specific run, target, firmware and scope; never reuse it for another attempt. |
| Safe stop, retrieval and next-round rearming | Verify a physical procedure for this release. D103's optional local service reset is disabled by default and retains motor inhibition; it **does not rearm a match**. Do not substitute it for a restart procedure. |
| Log preservation and extraction | Verify native ownership, framing and the actual inhibited IDLE dump route. These remain [blocked prerequisites](../state/analysis/P2_native_dump_prerequisite_followup.md). A reboot, battery swap or later match is not a log-preservation procedure. |
| Organizer decisions | Record answers to [PLAN §5](PLAN.md#5-questions-for-the-organizers-send-today): orientation, mode changes, radios, arena, activation timing, scale and blade. D-014 remains pending. No pre-angled placement or between-round mode-change permission is assumed. |
| Release acceptance | Actual loaded RAM/stack, full-source timing, physical results, independent review and required human gates remain separate from software tests. |

Source basis: [app entry](../src/app/app.ino), [setup grants](../src/app/runtime.h),
[config](../src/config.h), [UI renderer](../src/hal/ui_display.cpp),
[D103 service contract](../state/analysis/P2_service_reset_contract.md).

## Release record

Complete this against the actual approved release, then print all three documents.

| Field | Verified value / evidence / owner |
|---|---|
| Release commit, tag and date | ____________________ |
| Config hash; enabled modes and default | ____________________ |
| Build receipt, final artifact identity and actual deployment receipt | ____________________ |
| PINMAP, physical acceptance and human gate records | ____________________ |
| Operator-visible readiness check, including inhibited IDLE confirmation | ____________________ |
| SC-AP disposition and original matrix READY/voltage acceptance evidence | ____________________ |
| Calibrated battery method and current VBAT_WARN_V | ____________________ |
| Physical stop, power isolation, safe retrieval and full rearm procedure | ____________________ |
| Same-boot evidence service/dump procedure and preservation limits | ____________________ |
| Organizer answers and verified match radio-disable procedure | ____________________ |
| Operator, scout and release owner | ____________________ |

Current configuration uses `VBAT_WARN_V = 10.8 V`, default mode 1, and enables
ARC and WAIT. These values must be rechecked against the printed release.

The [schedule](PLAN.md#3-schedule-and-gates) freezes code on Thursday 1 October
at 21:00; afterward only config values change, each with TUNING_LOG evidence.
Record the actual v1.0 tag and commit at the freeze only after the release
conditions are satisfied; the date alone does not authorize a release tag.
If P3 has not passed by the end of 28 September, apply the documented
scope decision: SIDESTEP/DIRECT plus reactive core and recorder; remove ARC,
WAIT and P6. P6 otherwise requires an actual P4 pass by 30 September.

## Operator workflow — after release prerequisites are closed

### Night before

- [ ] Charge both packs using the team's approved charging procedure; label them.
- [ ] Weigh the complete robot and record the actual reading. Project target:
  2,950 g within 20 g; confirm the organizer's weigh-in rule and scale separately.
- [ ] Check the complete footprint in the 199 × 199 mm project check square,
  including attached blade, sensors and wires.
- [ ] Check screws, existing threadlocker and retained parts; clean the tires.
- [ ] Pack the inventory below and print the verified runbook, mode card and sheets.

### At the pit

1. With motors inhibited, use the verified power-on procedure. Confirm the release
   identity and the recorded readiness check. Release the buttons and observe the
   right-hand R alternate on/off and return on (nominally 500 ms per page).
   A frozen R, boot logo or mode glyph alone is insufficient. R reports a current
   inhibited, qualified start context; it does not authorize motor operation.
2. Check the rightmost pixel of the row immediately above the battery bar:
   bright means the accepted voltage is at/above VBAT_WARN_V (currently 10.8 V),
   dim means below, and off means unavailable in the qualified IDLE display.
   Require the bright marker and live R using the calibrated release input.
   The coarse bar and absence of a low-battery icon do not establish the threshold.
3. Apply the recorded organizer radio policy and verify the approved disable
   procedure. The plan's default is Wi-Fi off during matches; Bluetooth treatment
   and the organizer's answer still need recording. No radio controls robot motion.
4. Enter SENSOR_VIEW with motors inhibited. Present a hand to each of the seven
   opponent sensors individually and check its verified display mapping. Present a
   white card to each QTR, then confirm its normal black-surface indication.
   A dim unavailable marker or a failed channel stops the readiness check.
5. Return to the match-mode view. Select and confirm an enabled, physically accepted
   mode using the card; complete the actual UI check at arm's length.

### At the ring

1. Follow the referee's placement instruction. Place behind the start line without
   touching it; use only an organizer-approved orientation.
2. Confirm the selected mode and completed readiness check. Leave services before
   attempting a match START. Do not change modes if the organizer prohibits it.
3. Wait for the whistle. Press and release START once, then step back beyond 30 cm
   and keep hands off. Keep the robot still during its countdown calibration.
4. The current software holds outputs inhibited for 5.1 seconds **after release
   debounce completes**. Do not shorten the hold or infer its measurement from a
   countdown glyph. Follow referee instructions if the start must be cancelled.

### Between rounds

1. Wait for the referee and use the verified stop/retrieval procedure before handling.
2. The scout records the opponent's actual opening and result. Choose the next
   allowed mode using the card's round rule.
3. Check battery, tire debris and loose parts; every detached part is a warning
   under the original plan. Record the issue rather than concealing it.
4. Preserve/dump the attempt if the verified route and time permit. Otherwise mark
   it NOT CAPTURED; do not promise recovery after a power cycle or another attempt.
5. Use the release's verified **full rearm** procedure before another round, then
   repeat readiness and mode confirmation. D103 service access cannot perform this.

### Timeout and battery swap

The original P7 plan allows one timeout per match, two minutes. Confirm the
organizer/referee procedure before relying on it, and rehearse the complete swap.

1. Request the timeout and start the timer at the referee's indicated point.
2. Stop, retrieve and isolate power using the verified release procedure.
3. Exchange the pack using the team's verified connector/isolation sequence and
   secure it with the existing restraint. This document supplies no new wiring.
4. Power on through the verified full rearm procedure. Recheck battery, readiness,
   sensors and selected mode before returning to the referee.
5. Record elapsed time and any uncaptured log. A pack swap can lose volatile evidence;
   safety takes priority over retaining it. Do not skip checks to meet the timeout.

### After the match

When a laptop and the qualified inhibited IDLE route are available, capture the
log before any reset/power-off that could lose it. Start the receive-only capture
before the local LOG_DUMP action using the existing
[capture instructions](../tools/README.md#idle-recorder-capture-d090). Retain the
original wire/CSV files, manifests, validation and loss status, including partial
or failed captures. A TCP connection alone does not qualify the native transport.
If no safe qualified dump is available, record NOT CAPTURED and the reason.

## Failure playbook

| Observation | Operator response |
|---|---|
| Does not start | Keep inhibited; check readiness, match/service selection, accepted button input and faults. Boot-held START is not a new press/release. Do not bypass the hold or repeatedly press buttons to force motion. |
| Resets unexpectedly | Stop the trial/round and follow the referee and safe isolation procedure. Record symptoms, battery and any available reset evidence; obtain a fault disposition before reuse. Do not assume the recorder survived. |
| Sensor stuck or unavailable | Do not start another round. Check obstruction and the existing physical acceptance procedure with the hardware owner. Do not hide the fault by changing thresholds or masks without evidence. |
| Low or unknown battery | Do not start another round. Use the approved timeout/swap procedure if permitted; recheck with the calibrated method. |
| Tire debris | Inhibit and safely retrieve before cleaning; repeat the tire and loose-parts check. |
| Referee restart | Wait for the referee, safely inhibit/retrieve and follow the verified full rearm procedure. Reconfirm mode/readiness and use a fresh START/release. Do not use service reset as rearming or assume reset preserves logs. |

## Packing inventory

Tick items actually owned and packed; this is an inventory, not a purchase list.

- [ ] Both packs charged and labelled; charger.
- [ ] Spare fuses; spare MZ80 and QTR; spare IBT-2.
- [ ] Zip ties; threadlocker; tire wipes; multimeter.
- [ ] Laptop with the repository and required connection equipment.
- [ ] Printed verified runbook, mode card and rehearsal/scouting sheets.

Original scope: [P7 prompt](prompts/P7_freeze_matchday.md),
[PLAN §3/§5/§6](PLAN.md), [hardware checks](HARDWARE.md#9-hardware-verification-checklist-feeds-p2).
Completed preparation is not GATE P7: the actual tag/hash, printed documents,
rehearsal, review and human `GATE P7 PASS` still need evidence.
