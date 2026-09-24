<!-- Reviews the D137 operator-document drafts against the original P7 scope. -->
<!-- Separates accurate preparation from operational release and human gates. -->
<!-- Evidence is local source inspection, document hashes and link checks only. -->
# P7 operator-document review

2026-09-24, Asia/Dubai. **PASS for D137 software-document preparation only.**
This is a separate, reused-context, same-model scoped review. It is not a fresh
phase-gate review, human approval, operator-readiness verdict or motor permission.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed final drafts.

Two root-identified draft findings were corrected by the document author and
independently checked here before this verdict:

- **MAJOR, resolved:** the initial `docs/REHEARSAL_SCOUTING.md:9` and `:21`
  described authorization by practice session. The final text at lines 9–12,
  52–60 requires fresh authorization bound to each specific run, target, firmware
  and scope, with a separate run/approval reference for each retry. The round
  table preserves those references. `docs/RUNBOOK.md:26` agrees.
- **MINOR, resolved:** initial `docs/RUNBOOK.md:57` could imply tagging merely
  upon reaching the freeze. Final lines 59–60 require satisfied release conditions
  and expressly reject the date alone as authorization, matching the corrected
  `docs/prompts/P7_freeze_matchday.md:8` build-only/release distinction.

The original READY/battery-on-matrix requirement is **still unmet**, not silently
replaced by an external meter: `docs/RUNBOOK.md:25,47`, `docs/MODE_CARD.md:61`,
`state/analysis/P7_software_acceptance_packet.md:30` and open SC-AP at
`state/analysis/spec_conflicts.md:731` say so explicitly. This remains an
operational acceptance blocker outside the deliberately limited draft verdict.

## Scope and evidence checked

Scheduling baseline: `3fb74135`; prior software closure: `0faf2e6d`. The review
covers the three operator drafts, corrected P7 prompt, P7 acceptance packet,
pending gate request and SC-AP clarification. The packet's final validation
paragraph intentionally remains in preparation until the parent records this
review and its final receipt.

| Requirement | Checked content and source |
|---|---|
| Original P7.2 workflow | `RUNBOOK.md:67–152` retains night-before charging/weight/footprint/fasteners/tires, pit checks, mode selection, placement/START/withdrawal, between-round checks, timed swap, capture and all six failure cases. Operational steps are conditional on the release prerequisites, not instructions to operate the present empty-grant app. |
| Original P7.4 inventory | `RUNBOOK.md:154–162` retains both packs, charger, fuses, MZ80/QTR/IBT-2 spares, zip ties, threadlocker, wipes, multimeter, laptop, printed runbook/card and scouting sheets. All possession/packing boxes remain blank. |
| Original P7.3 rehearsal | `REHEARSAL_SCOUTING.md:6–12,50–76,94–112` plans three best-of-three sets on 2 October, preserves unused/failed/retried attempts and actual timing, and leaves every result and completion field blank. Procedural slips update the runbook; defects do not bypass the code freeze. No rehearsal, printing or tag is asserted. |
| PLAN 6.4 choices and round rules | `MODE_CARD.md:10–40` preserves the seven opponent categories, round-two change/keep rule and round-three counter-selection rule, organizer permission and fixed SIDESTEP_R contingency. ARC/WAIT require both availability and physical acceptance; IDs remain 1–6. `REHEARSAL_SCOUTING.md:114–135` retains the six scouting fields and between-round notes. |
| Schedule and gates | `RUNBOOK.md:57–63`, packet lines 63–67 and the pending request retain the actual 28 September P3 cut, conditional P6 eligibility, 1 October 21:00 freeze, 2 October rehearsal and 3 October competition. No date supplies a gate or release. |
| Current input and display limits | `src/app/app.ino:20`, `src/app/runtime.h:36`, `src/config.h:105,206,246,250,265` and `src/hal/ui_display.cpp:44,96,112,163` support empty grants, unconfigured button windows, 10.8 V warning value, mode glyphs, dim unavailable sensors and a coarse/unknown battery bar. No literal READY or numeric voltage measurement is invented. |
| Current menu and start semantics | `src/core/countdown.h:267` and BEHAVIOR B3/B13 support qualified release, short/dead/long MODE intervals, service ordering, preserved mode capture and the 5.1-second completed-release hold. The card conditions all controls on physical qualification and does not claim that logical BOTH tests prove its electrical decoding. |
| STOP, rearm and capture | D103's service contract and `src/app/runtime_service.cpp:168` preserve permanently inhibited service-only reset. The drafts require a separately verified full rearm procedure and qualified dump route; they do not promise RAM-log survival across reset, a pack swap or another attempt. D090 receive-first capture and retained partial/loss evidence match `tools/README.md:259`. |
| Deployment and prior evidence | The prompt's `tools/flash.sh app --match --compile-only` maps through the existing wrapper. `tools/board_tool.py:460` still refuses generic motor-capable upload. The packet describes 1584-byte conditional MATCH loader span and 62 file-inspected imports, not default fit, live RAM/WCET, deployment or physical acceptance. |
| Pending gate request | `state/reviews/P7_gate_request.md:3–37` claims none of the complete P7 exits and requires real evidence, fresh independent review and the human's gate entry. It does not assign or manufacture a gate verdict. |

The companion [local receipt](P7_operator_docs_review_receipt.json) records final
document and supporting-source hashes, local link/fragment check counts, and
the exact scope limits. All relative file targets and Markdown fragments resolve.
`git diff --check` reported no whitespace errors; Git's CRLF normalization notices
are not a failed check. No board/network access, build, test-suite execution,
upload, reset, motor run, source/test edit or ledger edit was performed by this
review. Only this report and its compact receipt were written.

## Verdict

**PASS — preparation drafts are accurate and reviewable.** Release, SC-AP
operational resolution, all required physical acceptance, actual printing and
rehearsal, genuinely fresh gate review and human `GATE P7 PASS` remain pending.
