<!-- Maps original P7 deliverables to evidence and outstanding release work. -->
<!-- Prevents draft procedures and scheduled dates from becoming false acceptance. -->
<!-- Checked through separate document review and local source/link verification. -->
# P7 operator-document preparation

2026-09-24 Asia/Dubai. D137 advances only software-document preparation under the
user's software-first direction. **P7 release acceptance is pending.** P6 remains
deferred; actual P0-P5 criteria and human gates have not been replaced by assumptions.

| Original task | Current deliverable | Required completion evidence |
|---|---|---|
| 7.1 Freeze/release | Build-only example corrected to `tools/flash.sh app --match --compile-only` | Validated source/config and checked artifacts; actual freeze/release conditions; recorded release commit and v1.0 tag. No tag exists by virtue of this packet. |
| 7.2 Runbook | [Draft runbook](../../docs/RUNBOOK.md) and [mode card](../../docs/MODE_CARD.md) in preparation | Scoped document review, qualified operational procedures, team review and actual printed copies. |
| 7.3 Dress rehearsal | [Blank rehearsal/scouting sheets](../../docs/REHEARSAL_SCOUTING.md) in preparation | Three real best-of-three sets on2October, exact timings and procedural observations; no blank cell is a pass. |
| 7.4 Kit | Inventory in the runbook | Team records actual packed items; no purchase or possession inferred. |
| Exit gate | [Filled pending request](../reviews/P7_gate_request.md) | Required evidence, genuinely fresh independent gate review with no open BLOCKER, human `GATE P7 PASS`. |

Use the original [P7 prompt](../../docs/prompts/P7_freeze_matchday.md) and
[PLAN](../../docs/PLAN.md) sections3/5/6. D014 organizer answers remain pending;
orientation, mode-change, radio and restart policies cannot be presented as
confirmed organizer rulings. The mode-selection guide is the kit's proposed
strategy, not measured matchup performance.

Current production enters `runtime.begin(app::SetupGrants{})`; physical input,
matrix and dump grants default false and button windows are unconfigured. The
display projection does not establish literal READY or a numeric battery reading.
Optional stopped-service reset does not rearm a match. Native recorder delivery
and a log-preserving next-round workflow remain unqualified. Draft procedures
must surface these gaps rather than instruct an operator to bypass them.

Prior acceptance entry points:

- [P0 pending request](../reviews/P0_gate_request.md) and
  [P1 pending request](../reviews/P1_gate_request.md): physical prerequisites and
  explanation/human gate ownership.
- [P2 packet](P2_software_acceptance_packet.md): actual pins/electrical/sensors,
  buttons, motors, reversal/R6 conflict, live stack/WCET and recorder transport.
- [P3 packet](P3_software_acceptance_packet.md): starts, measured stopping/turning,
  edge escapes and solo reliability.
- [P4 packet](P4_software_acceptance_packet.md): actual acquisition, push, loss,
  spectators and re-flank trials.
- [P5 packet](P5_software_acceptance_packet.md): actual opener/UI/mirror/abort trials.
- [Native dump prerequisites](P2_native_dump_prerequisite_followup.md): unresolved
  ownership/framing/cancel/reopen; historical attempts are not a working delivery path.

P5 D136 closure0faf2e6d retains93public/19private/112legacy passing checks and all
original failures. [MATCH qualification](P5_match_native_validation.md) and its
independent review establish target compilation plus conditional file-based
loader/import checks only (1584Bspan,62imports). The default-build deficit remains
separate; unmodifiedD135default is not compiled. None is a release deployment,
full-source worst-case timing, physical trial or new motor authorization.

No board build/upload/reset or firmware/config/test change is needed for this
documentation task. `--match` is a build configuration. Any eventual motor-capable
upload/run needs a qualified path and fresh identified STAND OK or RING OK; current
generic tooling refuses that upload. Do not run the example merely to re-create
already-retained compile evidence.

Schedule stays unchanged: absent actual P3 gate by end28September, cut to reactive
plus SIDESTEP/DIRECT and recorder; P6 needs actual P4 by30September and no stronger
cut. Freeze1October21:00Dubai, rehearsal2October, competition3October. No code or
release claim follows automatically from any date. After freeze only permitted
config values with tuning evidence; other code work needs an explicit human exception.

Validation status: documents/review currently in preparation. The final source/link
check and separate scoped review will be appended here before software closure.
