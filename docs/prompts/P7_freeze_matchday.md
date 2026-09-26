# P7: Freeze, runbook, dress rehearsal

**Goal:** a tagged, frozen firmware and a team that runs a match on autopilot.
**Load:** AGENTS.md, docs/PLAN.md sections 3, 5, 6.

## Tasks
7.1 At the freeze, use the reviewed D241 static production MATCH/Immediate/M1
compile-only route. Run
`python -I -B tools/compile_match_static.py --check-only --profile match --motors-allowed 1 --attempt TOKEN --reviewed-head FULL_HEAD`,
then replace only `--check-only` with `--execute` after admission. Use a fresh
owner and record the source commit and accepted artifact/layout result in
PROGRESS.md. See the [D241 contract](../../state/analysis/P7_match_static_contract.md)
for exact scope and owner requirements. The legacy dynamic build path remains
separate. Tag v1.0 only after the required validation and release conditions;
a date alone is not acceptance. Upload requires a qualified precompiled path
and fresh, identified STAND OK or RING OK for that motor-capable run. Selecting
MATCH/M1 or passing compilation grants no permission to upload or operate.

7.2 Write docs/RUNBOOK.md (print it):
- **Night before:** charge both packs; weigh; footprint check; screws and threadlocker; clean tires.
- **At the pit:** power on; confirm READY and battery at or above VBAT_WARN_V on the matrix; apply the radio policy from the organizer answer (default: Wi-Fi off for matches); SENSOR_VIEW check (hand in front of each of the 7 sensors, each QTR over a white card).
- **Mode card:** docs/PLAN.md section 6.4.
- **At the ring:** place behind the line, not touching it; select the mode; wait for the whistle; press and release START; step back beyond 30 cm; hands off.
- **Between rounds:** note what the opponent did; choose the mode; battery check; loose-parts check (every detached part is a warning).
- **Timeout** (one per match, 2 minutes): battery swap procedure, practiced.
- **After the match:** dump the log when a laptop is available.
- **Failure playbook:** does not start; resets; sensor stuck; low battery; tire debris; referee restart.
7.3 **Dress rehearsal** (Friday 2 October): three best-of-three sets against the box using the exact runbook and timings. Fix the runbook, not the code, for procedural slips.
7.4 **Kit list:** both packs charged, charger, spare fuses, spare MZ80 and QTR, spare IBT-2, zip ties, threadlocker, tire wipes, multimeter, laptop with the repo, printed runbook and mode card, scouting sheet.

## Current software evidence — 27 September 2026

D239's complete inhibited synthetic delivery is accepted: 5,001 frames and eight
events with the exact opening envelope, session and checksum, and no reported
loss. [Actual evidence](../../state/analysis/P7_recorder_repeat_delivery_actual_validation.md)
retains the earlier failed attempts; it supplies no physical robot qualification.

D240's commissioning delivery caller and D241's production static compile,
qualified deploy and paired delivery tools are host-tested and reviewed. The
current D241 target compile-only check and artifact/layout validation passed;
see [actual evidence](../../state/analysis/P7_match_static_actual_validation.md).
Production deployment uses `tools/deploy_match_static.py`; fresh identified
production delivery uses `tools/run_match_identified_delivery.py`. Commissioning
uses `tools/run_app_identified_delivery.py`. All take `--check-only --scope
RELATIVE_JSON --reviewed-head FULL_HEAD` for local admission; see the
[runbook](../RUNBOOK.md#release-owner-tooling) for execution boundaries.

The paired route requires a fresh session in the exact compiled image and
qualified dump grants, arms the receiver before one qualified upload, and keeps
unchanged envelope/session/CRC/CSV acceptance. Failure consumes the session;
reset does not renew it or preserve RAM logs. Default absent grants cannot
support an operational app dump. Physical setup, calibrated controls/display,
actual timing/RAM, safe stop/restart, rehearsal and human gates remain open.
The runbook is still NOT OPERATOR-READY.

## Exit gate (GATE P7)
- [ ] v1.0 tagged, hash recorded, runbook printed, rehearsal done
- [ ] Human writes `GATE P7 PASS`
