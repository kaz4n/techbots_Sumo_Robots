<!-- Supplies blank records for the original P7 rehearsal and PLAN scouting. -->
<!-- Preserves actual outcomes and procedural corrections without inventing trials. -->
<!-- Review against P7, PLAN 6.4, RUNBOOK and the acceptance packets. -->
# Rehearsal and scouting sheets

**D137 preparation draft. No rehearsal or physical result is recorded here.**
Planned rehearsal: Friday 2 October 2026, three best-of-three sets against the
box, using the exact approved [runbook](RUNBOOK.md) and [mode card](MODE_CARD.md).
This sheet authorizes no hardware setup or motor run. Close the runbook's release
prerequisites. Obtain fresh RING OK for **each specific powered practice attempt**,
bound to its run ID, target, firmware and scope. Approval is never reusable across
attempts, firmware changes or sessions; record a separate reference for every retry.

## Session identification

| Field | Actual entry |
|---|---|
| Date, location and ring conditions | ____________________ |
| Operator / scout / timekeeper / safety owner | ____________________ |
| Release commit/config hash and deployed artifact receipt | ____________________ |
| Runbook and mode-card revision; available modes | ____________________ |
| Approved test box and physical setup | ____________________ |
| Target and scope identity to bind in each individual run/approval record | ____________________ |
| Readiness, physical acceptance and full rearm procedure references | ____________________ |
| Organizer/radio procedure and rehearsal referee | ____________________ |
| Starting pack IDs/voltages; measurement method | ____________________ |
| Log/video location and actual clock/timing method | ____________________ |

## Before the first set

- [ ] Release prerequisites reviewed; all missing entries resolved for this run.
- [ ] Actual weight/footprint, screws, retained parts and tires checked.
- [ ] Both packs and kit inventoried; power isolation and safe retrieval rehearsed.
- [ ] Actual battery/readiness, seven opponent channels and four QTRs checked.
- [ ] Operator selects each included mode within 5 s and reads it at arm's length;
  record the measurement below. This checkbox alone is not P5 acceptance.
- [ ] Referee/whistle, placement, >30 cm withdrawal and hands-off sequence agreed.
- [ ] Stop, same-boot evidence access, capture and full next-round rearming reviewed
  as separate procedures. D103 service reset is not rearming.

| Included mode ID | Selection time (s) | Read at arm's length? | Evidence / issue |
|---|---|---|---|
| ____ | ____ | ____ | ____________________ |
| ____ | ____ | ____ | ____________________ |
| ____ | ____ | ____ | ____________________ |
| ____ | ____ | ____ | ____________________ |
| ____ | ____ | ____ | ____________________ |
| ____ | ____ | ____ | ____________________ |

## Three best-of-three sets

Record each scheduled round and its individual approval reference in order. A set ends when one side has two wins;
mark an unused third round NOT PLAYED and give the reason. Preserve failed,
aborted and restarted attempts separately rather than replacing their results.
For each retry, add a new row with a new run ID and fresh RING OK reference,
linked to the original attempt; do not overwrite its row or reuse its approval.
Record observed times with their method; stopwatch/video timing is not the
calibrated MCU timing evidence required by the acceptance packets.

| Set / round | Run ID / RING OK reference | Mode / box behavior | Pack / V | Start / end / elapsed | Result or NOT PLAYED | Log / video / issue ID |
|---|---|---|---|---|---|---|
| 1 / 1 | __________ | __________ | ______ | __________ | __________ | __________ |
| 1 / 2 | __________ | __________ | ______ | __________ | __________ | __________ |
| 1 / 3 | __________ | __________ | ______ | __________ | __________ | __________ |
| 2 / 1 | __________ | __________ | ______ | __________ | __________ | __________ |
| 2 / 2 | __________ | __________ | ______ | __________ | __________ | __________ |
| 2 / 3 | __________ | __________ | ______ | __________ | __________ | __________ |
| 3 / 1 | __________ | __________ | ______ | __________ | __________ | __________ |
| 3 / 2 | __________ | __________ | ______ | __________ | __________ | __________ |
| 3 / 3 | __________ | __________ | ______ | __________ | __________ | __________ |

| Set | Score / outcome | Between-round checks and rearm completed? | Procedure corrections |
|---|---|---|---|
| 1 | __________ | ____________________ | ____________________ |
| 2 | __________ | ____________________ | ____________________ |
| 3 | __________ | ____________________ | ____________________ |

## Timeout / battery-swap rehearsal

Original plan: one timeout per match, two minutes; apply the confirmed referee
timing rule. Test the approved physical procedure, not a new wiring sequence.
Any actual power interruption may lose uncaptured RAM logs.

| Item | Actual entry |
|---|---|
| Set/round, timeout requested and referee timer start | ____________________ |
| Safe stop / retrieval / power isolation completed | ____________________ |
| Removed pack / replacement pack / measured voltage | ____________________ |
| Pack secured; approved full rearm and readiness completed | ____________________ |
| Returned to referee / total elapsed / within allowance? | ____________________ |
| Log captured before interruption, or NOT CAPTURED and reason | ____________________ |
| Procedural issue and runbook correction | ____________________ |

## Procedural findings and closure

Correct the runbook for procedural slips. A software/hardware defect is a
separate issue; do not disguise it as an operator mistake or bypass the code
freeze. After 1 October 21:00, only config changes with TUNING_LOG evidence are
allowed under the original schedule.

| Issue ID / attempt | What actually happened | Evidence | Runbook correction / other issue owner | Recheck result |
|---|---|---|---|---|
| __________ | ____________________ | __________ | ____________________ | __________ |
| __________ | ____________________ | __________ | ____________________ | __________ |
| __________ | ____________________ | __________ | ____________________ | __________ |

Actual rehearsal completion/date: ____________________
Team review/remaining issues: ____________________
Printed final runbook/card revision: ____________________
Human gate record in PROGRESS, if later supplied: ____________________

Blank fields or a completed worksheet do not themselves establish GATE P7.

## Opponent scouting — one line per team

The person not operating scouts earlier matches. Write observations, and mark
unknowns rather than inferring sensor capabilities from appearance. Use the mode
card only among the release's accepted modes and within organizer permissions.

| Team / match watched | Opening move | Speed | Wedge height relative to ours | Observed sensor coverage | Edge behavior | Evidence / candidate mode |
|---|---|---|---|---|---|---|
| __________ | __________ | ______ | __________ | __________ | __________ | __________ |
| __________ | __________ | ______ | __________ | __________ | __________ | __________ |
| __________ | __________ | ______ | __________ | __________ | __________ | __________ |
| __________ | __________ | ______ | __________ | __________ | __________ | __________ |
| __________ | __________ | ______ | __________ | __________ | __________ | __________ |
| __________ | __________ | ______ | __________ | __________ | __________ | __________ |

## Between-round scouting note

| Opponent / round | Our mode / result | Their actual opening / change | Next allowed mode and reason | Battery / loose parts / log status |
|---|---|---|---|---|
| __________ | __________ | ____________________ | ____________________ | ____________________ |
| __________ | __________ | ____________________ | ____________________ | ____________________ |
| __________ | __________ | ____________________ | ____________________ | ____________________ |

Sources: [P7 prompt](prompts/P7_freeze_matchday.md),
[PLAN schedule](PLAN.md#3-schedule-and-gates),
[PLAN scouting and selection](PLAN.md#64-mode-selection-guide-print-this-card-for-match-day).
Keep completed records, original logs/videos and any tuning evidence in the
existing state/log workflow; these blank preparation sheets create no new gate.
