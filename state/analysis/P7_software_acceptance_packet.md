<!-- Maps original P7 deliverables to evidence and outstanding release work. -->
<!-- Prevents draft procedures and scheduled dates from becoming false acceptance. -->
<!-- Checked through separate document review and local source/link verification. -->
# P7 operator-document preparation

Current status, 26 September 2026 (D216): the core/HAL/runtime and operator
preparation are implemented, but the connected hardware is the UNO Q alone.
D212's ordinary M0 application was uploaded and independently reviewed. Two
passive samples reported RUNNING/NONE, maximum execution 477 us and no missed
releases, with initialization false and all grants absent. This does not measure
initialized worst-case timing or verify sensors/motors. D214's B4 M0 compile
completed with a checked 82,912-byte package; it was not uploaded.

Use [D212 actual validation](P7_ordinary_app_run_actual_validation.md),
[D214 actual validation](P7_b4_app_compile_actual_validation.md), and the
[current completion audit](P7_completion_audit_20260926.md). Fresh B4 file-only
ABI is independently accepted. The fixed recorder decoder passed 20 tests on
each host platform; it preserves raw bytes and every loss field, with capture
origin and coherence still unproven. File-only B4 entry inspection is next.
Native UART delivery, log-preserving reset/restart qualification, live RAM/stack/timing, wiring/calibration, physical trials, printed
team materials and human gates remain open. The dated evidence below describes
historical preparation; its earlier pending-upload statements are superseded
by this paragraph, not retroactively changed into acceptance.


Updated 2026-09-26 Asia/Dubai through actual D190. D137 prepares operator documents;
D138 adds P7.2 informational READY/battery software; D180-D183 provide the
setup and deployment tooling. D184/D185 add actual isolated diagnostic and
current-app compilation evidence; D186-D190 add a checked static full-app
diagnostic and successful four-epoch inhibited observation. **P7 release acceptance is pending.** P6 remains
deferred; actual P0-P5 criteria and human gates have not been replaced by assumptions.

| Original task | Current deliverable | Required completion evidence |
|---|---|---|
| 7.1 Freeze/release | Build-only example corrected to `tools/flash.sh app --match --compile-only` | Validated source/config and checked artifacts; actual freeze/release conditions; recorded release commit and v1.0 tag. No tag exists by virtue of this packet. |
| 7.2 Runbook | [Draft runbook](../../docs/RUNBOOK.md) and [mode card](../../docs/MODE_CARD.md) written and scoped-reviewed | Qualified operational procedures, team review and actual printed copies. |
| 7.3 Dress rehearsal | [Blank rehearsal/scouting sheets](../../docs/REHEARSAL_SCOUTING.md) written and scoped-reviewed | Three real best-of-three sets on2October, exact timings and procedural observations; no blank cell is a pass. |
| 7.4 Kit | Inventory in the runbook | Team records actual packed items; no purchase or possession inferred. |
| Exit gate | [Filled pending request](../reviews/P7_gate_request.md) | Required evidence, genuinely fresh independent gate review with no open BLOCKER, human `GATE P7 PASS`. |

Use the original [P7 prompt](../../docs/prompts/P7_freeze_matchday.md) and
[PLAN](../../docs/PLAN.md) sections3/5/6. D014 organizer answers remain pending;
orientation, mode-change, radio and restart policies cannot be presented as
confirmed organizer rulings. The mode-selection guide is the kit's proposed
strategy, not measured matchup performance.

Current production enters `runtime.begin(app::configuredSetupGrants())` through
the [D180 config binding](P7_setup_binding_validation.md). All17 declarations
remain disabled; mounting, dump origin and button windows remain unconfigured.
Both current main-app profiles are [TARGET-COMPILED under D185](P7_current_app_compile_validation.md):
bench/default build6d9e48f8 and MATCH/Immediate build1fcc7d57 bind source37a2099f.
Neither was uploaded. Runtime and physical qualification remain pending, and
compilation does not resolve the default loader-model deficit described below.
The D138 display uses a live blinking R and an exact threshold pixel; current
validation and its boundaries are in the [readiness packet](P7_readiness_validation.md).
It is not a numeric battery reading or physical acceptance. Native matrix
startup/ownership, calibrated input and visibility still need qualification.
Optional stopped-service reset does not rearm a match. Native recorder delivery
and a log-preserving next-round workflow remain unqualified. Draft procedures
must surface these gaps rather than instruct an operator to bypass them.
The original READY/battery-on-matrix criterion remains open as
[SC-AP](spec_conflicts.md#sc-ap-p7-operational-readiness-versus-current-displayrearmdump-open-d137).
An external calibrated method in a draft field is not automatic acceptance of a
replacement criterion. D138 explicitly selects the R/threshold-pixel meaning;
it leaves actual matrix acceptance, rearming and log preservation open.

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
original failures. Its [MATCH qualification](P5_match_native_validation.md) is
historical. The later [D138 MATCH build](P7_readiness_native_validation.md) also
establishes target compilation and conditional file-based loader/import checks
only. D185 separately binds the current source to byte-identical raw/package
artifacts for each profile; its debug ELFs differ. This supports reuse of the
existing same-loader file-derived models only: default592B deficit and MATCH
conditional864B span/860B largest payload. It does not establish fresh ABI,
live RAM/stack, full-source worst-case timing, physical trials, a qualified
release deployment or motor authorization.

No board build/upload/reset or firmware/config/test change was needed for the
completed D137 documentation task. D138 validation is recorded separately.
`--match` is a build configuration. D182/D183's explicit precompiled
[deployment route](P7_match_deploy_validation.md) is HOST-TESTED / REVIEWED;
unscoped generic MATCH upload remains refused. Actual use requires a current
source-bound build, target/artifact qualification and fresh identified human
STAND OK or RING OK. No actual scope, permission or deployment was created by
these host checks. See [tool usage](../../tools/README.md); do not run a command
merely to re-create retained evidence.

Schedule stays unchanged: absent actual P3 gate by end28September, cut to reactive
plus SIDESTEP/DIRECT and recorder; P6 needs actual P4 by30September and no stronger
cut. Freeze1October21:00Dubai, rehearsal2October, competition3October. No code or
release claim follows automatically from any date. After freeze only permitted
config values with tuning evidence; other code work needs an explicit human exception.

## Completed software-document validation

The initial D137 preparation drafts and safe build-only example are complete. The
[separate scoped review](../reviews/P7_operator_docs_review.md) passes with no
open findings; it is a reused same-model context, not the fresh phase-gate review.
Its [receipt](../reviews/P7_operator_docs_review_receipt.json) freezes those
historical documents and source references. D138 edits to the runbook/mode card
have a separate [review](../reviews/P7_readiness_review.md). Root independently checked52relative links and
9fragments, all43protected source hashes, the original PROGRESS byte prefix and
no src/host/tests/tools changes from0faf2e6d; see
[local receipt](P7_document_validation.json). `git diff --check` exited0.

No firmware or tool tests were repeated for that D137 prose-only change, and no new
target build, upload/reset, hardware measurement or tuning was performed. The
root-identified session-authorization and date-only tag wording were corrected
before final review. SC-AP and all actual release criteria remain open.

D138 software validation and its separate scoped review are complete; see the
readiness packet. D139's single unchanged default/M0 compilation passed, but the
ordered pristine-loader model has a 592-byte deficit. Its negative qualification
evidence and separate review are complete, with one release-fit BLOCKER. Read
[P7_default_qualification_validation.md](P7_default_qualification_validation.md)
and [the scoped review](../reviews/P7_default_qualification_review.md). This
historical dynamic/default image remains unqualified; the deficit was not fixed
by treating static linking as the production choice.

Later static/default/M0 preparation reached an actual [D160 inert upload and
capture](P7_static_startup_run02_actual_validation.md). Both runtime samples were
STOPPED; [D161 diagnosis](P7_stopped_diagnostic_validation.md) recorded application/
line contract faults and an invalid motor receipt, without establishing their
native cause. The [D184 isolated diagnostic run](P7_motor_fault_run01_validation.md)
used the D179 caller once: four inhibited applications and41callbacks completed,
then the Gate was halted. This dynamic/default/M0 probe did not reproduce or
resolve the static full-app failure. Its run scope and both D185 compile owners
are consumed; they must not be reused.

The [D186 full-app trace](P7_app_motor_fault_validation.md),
[D187 static adapter](P7_app_motor_fault_static_validation.md) and
[D188 compile-only workflow](P7_app_motor_fault_compile_validation.md) are
HOST-TESTED / REVIEWED. The diagnostic follows the actual Runtime -> Transaction
-> Robot -> MotorGate path with empty setup grants and inhibited outputs.
D188 subsequently completed target compilation and actual ABI/entry audits.
After D191's exact authenticated scratch cleanup, [D190 run02](P7_app_motor_fault_run02_validation.md)
uploaded that static/default/M0 image and observed four completed application
epochs/41successful callbacks, then an explicit inhibited halt. All four flash
brackets passed; saved raw fields were independently decoded. The historical
IO fault did not recur and remains unresolved. These scopes are consumed.
Follow [CODEX_HANDOFF](../CODEX_HANDOFF.md); do not reuse old capture addresses,
decoders or native owners, or infer static production adoption. D192 longer
observation is separate host preparation. Live RAM/stack/WCET and physical
qualification remain open.

The [26September completion audit](P7_completion_audit_20260926.md) also identifies
a missing operational commissioning route: existing B4/P3/P4/P5 wrappers are
inhibited-only with empty grants and no dump port. Software preparation of a
proper configured entry/profile/deployment path may proceed; physical grants and
specific motor-run authorization remain prerequisites for execution.

Other dependent release work remains: obtain the real prerequisites in the linked
acceptance packets and resolve SC-AP against the qualified release, then validate
the actual runbook workflow. Native dump work first needs the specified privileged
read-only holder evidence and reviewed quiescence/cancel/reopen plan. Do not
rerun unchanged host matrices, repeat denied cleanup, deploy the current draft,
enable setup grants from assumptions, or fabricate P6 eligibility/release gates.
