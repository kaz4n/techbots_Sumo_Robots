# P7: Freeze, runbook, dress rehearsal

**Goal:** a tagged, frozen firmware and a team that runs a match on autopilot.
**Load:** AGENTS.md, docs/PLAN.md sections 3, 5, 6.

## Tasks
7.1 Tag v1.0 at the freeze. Build the match firmware (`tools/flash.sh app --match`) and record its commit hash in PROGRESS.md.
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

## Exit gate (GATE P7)
- [ ] v1.0 tagged, hash recorded, runbook printed, rehearsal done
- [ ] Human writes `GATE P7 PASS`
