# Codex handoff

## Current resume point — 2026-09-22 Asia/Dubai

**RESUMED by the human on 2026-09-22 at22:07 Asia/Dubai.**
Host implementation resumes; no hardware connection is assumed from this request.
Latest seven approvals are persisted as D-040 through D-046. Resumed B8 SEARCH
under D-041/D-042 is now HOST-TESTED with scoped separate review PASS. Next:
B11 re-flank under D-040/D-043, then D-045/D-046 arbitration and D-044 head-on.
Read analysis/P1_reflank_contract.md and the saved contract audits.

Latest completed batch: re-flank d78e95d, head-on0171741, lifecycle144e897 and
relative-turn precision/fault fix47ac972. Contracts were committed first.
609 cases/11,983,801 assertions pass normal+ASan/UBSan;48/48 scripts pass.
Reused separate scoped review PASS, exact23-file manifests refreshed. See
analysis/P1_reflank_headon_validation.md and reviews/P1_reflank_headon_codex.md.
31 NEW locked cases are now established; prior locked files unchanged.
SC-AF shared side history and SC-R inhibited recovery were explicitly approved
as D-047/D-048 in1dfaa7d; integration remains pending. Established locked tests
stay unchanged; inspect their component scopes before implementing the new policy.
Next eligible task: D-045/D-046 normal-perception production routing/qualification,
per analysis/P1_normal_perception_contract.md. Full Escape needs the two specific
pushed-out/replanning decisions now presented in P1_escape_remaining_contract.md.
No answers inferred. Check disk space before more builds: C: briefly reached0;
one verified untracked sanitizer object was removed, all evidence restored, and
about594MB was subsequently available. Raw results/source/tests remained intact.

Active implementation is **P1 host development under D-016**; P0 hardware
acceptance and every human phase gate remain pending. The dated sections below
are preserved history, not current phase instructions. No target compilation,
upload/reset, motor run or physical measurement has occurred. Origin is configured
and retained; no publication. User reports MPU6050; exact breakout/interface is
unverified. Hardware work is deferred until connection details/setup are available.

Earlier SEARCH snapshot fc5a9f5:540 cases/11,937,972 assertions normal+ASan/UBSan,
reused separate read-only scoped review PASS. Exact evidence:
analysis/P1_search_validation.md and its linked review. B14 tick statistics
remain complete at component scope (contract118f9cc). Countdown
lifecycle remains eligible after the newly unblocked SEARCH/re-flank work;
read analysis/P1_countdown_lifecycle_audit.md before its eventual contract.
Full Robot/scripts, other B14 integration and all later phases remain unfinished.
This continuation made actual software progress, not an impasse or goal completion.

D-039 already records/applies the user's one-case locked STOP amendment. All
other established locked tests remain protected. No human gates are simulated.
SC-Y/Z/AA/AB/AC/AD/AE are now resolved by D-040 through D-046. Older physical/
escape/WAIT choices remain in analysis/spec_conflicts.md. Do not reask approved
questions or infer approval of other choices. New reviewer creation hit the tool thread
limit; scoped reviews use an existing separate read-only context and are not a
fresh complete phase gate. Resume through docs/prompts/CODEX_RESUME.md.

## Historical recovery and checkpoints

Objective: implement the supplied SumoX-26 plan under R1-R11, preserving human gates.
Recovered 2026-09-22 at 17:00 Asia/Dubai: fresh planning kit, P0 active, no gates,
no source/tool scaffold, no existing Git repository. Original 30 files inspected
and preserved in local baseline `52b935e`; no remote configured or publication.

## Sources loaded in full
AGENTS.md, CLAUDE.md, README.md, CODEX_START_HERE.md; all four .claude/agents roles;
state/{PROGRESS,DECISIONS,FACTS,TUNING_LOG}.md; docs/{PLAN,HARDWARE,BEHAVIOR,CODEX_HANDOFF_REVIEW}.md;
docs/prompts/{CODEX_KICKOFF,00_KICKOFF,RESUME,REVIEW_GATE,P0_recon_toolchain,P1_core_logic,P2_hal_bench,P3_first_drive,P4_hunt_push,P5_openers,P6_judge_pack,P7_freeze_matchday}.md.
No nested AGENTS.md or ancestor rules files found. Session-supplied bootstrap
catalog points to a missing repo-local skill; installed bootstrap-harness was
inspected and is scoped to maintaining its imported suite, not this firmware.
No suite migration or global configuration change is needed.

## Workflow mapping
D-015 is the narrow authority for implementation. Native collaboration is available
with four total concurrent contexts. Fact checkers own G1/G2, G3/G4, G5/G6 analysis
files separately; coordinator alone allocates FACTS IDs and edits state ledgers,
config and build interfaces. Test-author derives future behavior tests from specs
and headers, never implementation. Reviewer uses a fresh context, read-only;
label it separate-context Codex review, not cross-model review. Log-analyst only
proposes changes from real data. Legacy Claude tool names/front matter are briefs.

## Environment and dependencies
Windows 10.0.26200, PowerShell 7.6.6, timezone Arabian Standard Time (UTC+04),
Git 2.52.0.windows.1, CMake 4.2.1, Python 3.13.11, OpenSSH 9.5p2/LibreSSL 3.8.2,
Git Bash 5.2.37. Codex CLI exposes `exec` and `review`; native delegation used.
Initial free C: space 1.66 GB. No compiler, rsync, adb or arduino-cli on Windows PATH.
WSL distributions exist; runtime checks are recorded in analysis/environment.md.
No SSH target, board core/library inventory, verified upload port, IMU model,
rulebook, organizer replies, PINMAP OK, or physical setup supplied yet.
Seeded facts are planning provenance, not installed-version/hardware checks.

## Resume and deadline rules
Read CODEX_RESUME.md, this file, PROGRESS, DECISIONS, FACTS, execution checklist,
open conflicts/reviews and P0 before work. See CODEX_EXECUTION.md for exact next task.
P0 cannot close without board round trip, startup measurements, PINMAP OK, review,
and the human gate. D-016 now permits P1 host development before that acceptance;
protected behavior decisions and all hardware gates remain pending.
All deadlines use Asia/Dubai: P3 scope cut after 28 September; P6 requires P4 by
30 September; freeze 1 October at 21:00; rehearsal 2 October; competition 3 October.
Current date is the plan's P0 day; no scope cut or freeze applies yet.

## Recovered disconnected session — 2026-09-22

P0 remains active, no gates passed. D-015 already recorded the requested role
migration; it was retained without creating a duplicate ADR. Recovered edits
were reviewed and completed in local commits:
- `7968434`: scaffold correction and inert diagnostics. B16 has 76 defaults,
  not the previously claimed 77; the extra FC bearing-table row was removed.
  Delayed-call seconds accounting repaired; independent synthetic tests added.
- `720791d`: staging/build/receive-only log tools and regression evidence.
  Compile-only never issues upload/reset/start; P0 upload eligibility binds the
  complete staged source to independently reviewed inert SHA-256 snapshots.
  Changed sources fail closed. No motor-upload authorization mechanism is enabled.

Validation: WSL g++/CMake CTest **1/1**, full Python tooling/config/real-sketch
synthetic suite **32/32**, both exit 0. Raw results are in
analysis/P0_{host,tool}_tests_recovery.txt. Review details and initial failures
are preserved in reviews/P0_recovery_codex.md and analysis/P0_scaffold_audit.md.
No locked tests were changed, behavior implemented, or core defaults tuned.

The user now identifies the IMU as **MPU6050**, and says connection/setup details
are not currently available. Research is updated in P0_G6 and FACTS F-056–F-060.
The model is human-reported; the breakout/electrical interface is still unknown.
Candidate library read-error handling and I2C timeout paths need resolution
before a safe driver can be adopted. No board packages were installed.

No SSH/USB board contact, target compile, upload, reset, motor run, physical
timing, or ring test occurred. Matrix scrolling/RAM counters are partial P0
artifacts; the printed-counter round trip is blocked by SC-I (Monitor vs R3/R4).
Hardware assumptions do not supply PINMAP OK, STAND OK, RING OK or GATE P0 PASS.

Next action is the read-only board inventory once an SSH target becomes available;
see CODEX_EXECUTION for the remaining dependencies and P0_gate_request for unmet
exit criteria. No further phase is eligible without the actual P0 gate. Resume
from this checkpoint, not the earlier IN PROGRESS scaffold notes. Work is stopped
at the saved hardware/decision boundary, not running in the background.

## Manual-check preparation follow-up — 2026-09-22

User asked what must be checked manually and requested continued work. Commit
`98d4524` adds `tools/preflight.sh`, which reads a fixed software inventory over
strict SSH and emits JSON with real command statuses. It neither configures nor
probes firmware/sensors. The new `--startup default|immediate` permits inert
bench builds independent of MATCH; motor guards/source hashes remain enforced.

Full tooling suite now **45/45 passed, exit 0**, with a separate fresh-context
read-only review PASS in reviews/P0_preflight_codex.md. No firmware/config/locked
tests changed, so the previously verified host scaffold is not a newly measured
board result. No board connection, target build/upload or physical test occurred.

New fact F-061: official manual warns about accessing the matrix before Linux
startup completes. Immediate matrix uploads are blocked until the installed
loader's ownership behavior is verified; compile-only is allowed. The boot logo
is not sketch entry, and even a SUMO marker has display delay. This remains an
open hardware/API dependency in addition to SC-I's printed-counter conflict.

The human-facing sequence is docs/P0_MANUAL_CHECKLIST.md; the blank worksheet is
state/analysis/P0_MEASUREMENTS_TEMPLATE.md, explicitly not evidence. Next: obtain
the first inventory/isolation/SSH/breakout reply, run read-only preflight when
possible, then guide the specific approved physical measurements. P0 remains
active and no gates or motor permissions have been supplied.

## Offline implementation continuation — 2026-09-22 17:53 Asia/Dubai

The user's latest instruction explicitly requests commencing work with no hardware
connected. D-016 records a narrow P1 host-development scheduling exception. Earlier
statements that all P1 development must wait are superseded only for this scope.
No hardware test is marked passed, no human gate is authored, and no protected
behavior recommendation is approved. Active implementation: P1 host only; P0
hardware acceptance still pending. Initial contracts cover B0 logical values,
B3 countdown permission, B4.1 classification and B5.1 debounce; they do not
implement ADC decoding, MotorGate, full B3 services, escape or the complete FSM.
Remaining interfaces will be added with resolved semantics, not stubbed as working.

## Reviewed P1 component checkpoint — 2026-09-22 18:10 Asia/Dubai

User explicitly approved governor option A and tick-order option A. D-017/D-018
and the visible B6/B2 amendments are in `01a61e6`; these decisions supersede the
earlier statements that those two questions are pending, and approve nothing else.

Completed local implementation commits:
- `c61a5e2`, `72f7eb6`, `cad7096`: standalone interfaces first, including separation
  of button qualification from the undecided countdown timestamp anchor.
- `f2b2279`: governor interface and VBAT_FILTER_MS=1000 from the existing B6
  one-second filter rule; all 76 B16 defaults unchanged.
- `a37b1c5`: countdown Gate and logical Buttons plus initial locked tests/helper.
- `e30d4c2`: B4.1 classifier plus initial locked tests.
- `2c2f55e`: B5.1 debounce and seven B5.2 front-table rows with independent tests.
- `0742bd9`: approved B6 electrical governor and 29 regression cases.
- `7cddb1a`: aggregate evidence, scoped review and updated inert-source hashes.

Independent test author read specifications and public headers, no implementation
`.cpp`. Final host: **77 cases, 3,457,564 assertions, all pass, no skips**; separate
ASan/UBSan build passed the same suite. Full tooling suite: **46/46**, exit 0.
See `analysis/P1_validation.md`, raw P1_*_tests.txt, and P1_test_author.md.
New locked files were established in the above commits; do not edit them without
a human-approved ADR. No established locked predicate was weakened.

Separate peer reviewer found no BLOCKER/MAJOR/MINOR in this scope. The tool refused
a new reviewer thread, so the prior P0 reviewer context was reused read-only:
**not a fresh P1 gate review and not cross-model review**. Exact complete staged
inert-source hashes were independently reviewed before refresh; compile-only and
motor-upload guards remain intact. F-061 still blocks Immediate matrix uploads.

Full P1 is unfinished despite exceeding 60 cases: other module interfaces,
complete FSM/table coverage, true R1 motor-write tests, R5/openers/escape properties,
target compilation, fresh full gate review, EXPLAINED OK and human gates remain.
No hardware operation or performance measurement occurred; no target compile
is claimed. `docs/ARCHITECTURE.md` describes actual standalone components only.

Next: receive the pending SC-J release-anchor and SC-D2 edge-policy decisions,
record each explicitly, then define/test the affected integration contract.
SC-K gates full B3 services; SC-M gates forward escape duty; other fusion,
acquisition, ALL_IN and recorder conflicts remain separate. Keep P0 manual work
pending until the board is available. Active work remains P1 host-only under D-016;
no phase has passed, no motor receipt exists, and nothing is published remotely.

## D-019/D-020/D-021 continuation — 2026-09-22

The user approved after-debounce anchoring, persistent/all-white inhibition, and
reuse of 0.80 for forward escape. These are accepted in D-019/20/21 and visibly
amend B2/B3/B4/B6. Do not re-request these decisions or treat earlier pending
entries as current. Both-held STOP/ADC, other B3 services and unrelated conflicts
remain pending.

- `fb82971`: D-019/D-020 specifications and interfaces before implementation.
- `e08b9a0`: Controller composes Buttons then Gate at qualification time; delayed
  qualification never backdates the complete 5.1-second hold. Ten new locked cases.
- `6ab4d2c`: Guard handles persistent white and all-white inhibition until reset.
  Ten new locked cases include a logical Controller -> Guard -> Governor harness.
- `79d2f6f`: D-021 forward contracts and existing 70% ratio centralized in config.
- `5595b57`: forward demand builder and EDGE_FORWARD governor cap; nine new tests.

Final host and ASan/UBSan: **106/106 cases, 5,220,784 assertions**, no failures or
skips. Full tooling suite **47/47**, exit 0. See P1_forward_validation.md and raw
P1_forward_*_tests.txt; the intermediate 97-case evidence is preserved separately.
An 8.6 ms Windows/WSL build timestamp warning was recorded; all modified source
files compiled/linked and final host/sanitizer execution passed. No WCET inference.

Independent test author again read specs/public headers only. Existing locked
files were preserved; newly committed integration/guard tests are now locked too.
A genuinely fresh separate reviewer checked the integration, then reviewed D-021
in the same read-only context; both scoped reports PASS, no findings. Neither is
a full phase gate or cross-model review. Exact inert source manifests were updated
only after independent source/hash review; all flash guards remain unchanged.

Forward bias means requested `(0.56, 0.80)` or its mirror, with 0.80 final cap.
Compensation, per-side caps and slew may alter the output ratio; the tests/docs
state this explicitly. Timed segments, heading hold and physical trajectory are
not implemented or measured by this helper. Guard inhibition is a logical veto;
actual app/MotorGate wiring remains absent.

Next: resolve SC-N motion semantics before timed/heading-held segments and SC-K
before full countdown services, then add interfaces and independent tests. Full
P1 core/Robot table coverage, target compile, fresh full gate review, EXPLAINED OK
and human gate are still missing. Real MotorGate write-boundary checks belong to
later HAL work and cannot replace P1 core-output proofs. P0 acceptance remains
hardware-pending; no board operation, tuning run, motor authorization or gate pass.

## Reviewed motion/services/perception continuation - 2026-09-22

Resumed clean683665b at18:42 Dubai; current day remains before scope-cut/freeze.
Active goal requests project completion with hardware deferred. Actual host tests
and reviews ran; hardware checks/audits/gates have not been fabricated or passed.
P1 host-only remains the active implementation track under D-016.

New accepted decisions D-022 throughD-028 record the user's explicit approvals:
bounded heading correction, duty-only voltage compensation, countdown services,
ALL_IN safety, deterministic bearing memory, bounded contact lifetime, explicit
first4096-events/overflow handling. Do not re-ask these. B3/B4/B5/B7/B11/B15 show
visible amendments; PLAN/HARDWARE and all76 B16 defaults remain unchanged.

Commits:

- `0caaadb`/`71d2545`: motion/codec public contracts and D-022/D-023.
- `40c8c9c`: Turn/Straight/Arc/Brake, 30 cases/two 10,000-sample properties.
- `ae3e9e7`: portable frame/event encoding, 19 independent byte-boundary cases.
- `5bfcf70`: D-024 service contract/config boundaries and D-025 ALL_IN policy.
- `3cee6ae`: Services plus 27 NEW locked tests; existing locked tests untouched.
- `290c13b`: D-026/27/28 plus public bearing/contact contracts.
- `c578911`: BearingMemory/Contact, 30 cases/10,000 mirrored samples.
- `ad764c1`: intermediate 182-case evidence and exact source-review snapshot.

Final host and ASan/UBSan:212/212 cases,6,089,047 assertions, zero failures/skips.
Raw P1_opp_memory_contact_tests.txt and _sanitizer.txt. Final source tooling run
is recorded separately in _tools.txt. Separate read-only review PASS, no open
findings; reused Codex review context, not cross-model or full phase-gate review.
Spec-only test author never opened implementation.cpp files. Implementation
workers owned disjoint files, coordinator alone edited interfaces/config/ledgers.

Reviewer caught maximum-duration missed expiry across uint32 wrap before tests;
fix accumulates successive unsigned deltas in uint64 and preserves accepted
range. It also caught PRNG low-bit path imbalance; tests now explicitly balance
healthy/fallback samples. One test compile failed CAPTURE macro syntax, fixed by
splitting diagnostic calls without altering assertions; original failure retained.
No unresolved failure or second unsuccessful repair was hidden.

Services remains an explicit caller-managed component: start on qualified
release, cancel on IDLE/STOPPED, supply genuinely new raw gyro observations,
apply accepted bias in HAL, reset heading at GO. Tests compose real components;
production Robot/MotorGate path does not yet exist. Contact is cleared outside
centered ATTACK; target-loss emergency braking still needs the FSM. D-025 ALL_IN
and D-028 ring overflow are approved policy, not implemented runtime machinery.
No recorder ring/cadence/dump is supplied by the25/8-byte pure codec.

Exact next task: B5.5/B5.6 phantom/stuck contracts and independent tests, then
remaining stall/re-flank, escape/openers and FSM integration/table coverage.
Open physical/buttons/acquisition and other behavior questions remain in
analysis/spec_conflicts.md. No target compile, board operation, motor permission,
PINMAP OK, EXPLAINED OK or human gate exists. Preserve fresh per-run approvals.
No remote publication, history rewrite or release tagging occurred.

Environment refresh at 2026-09-22 19:15:51 +04:00: Windows Git2.52.0.1,
Python3.13.11, CMake4.2.1, OpenSSH9.5; WSL g++13.3 verified this continuation.
An origin remote is now configured as https://github.com/kaz4n/techbots_Sumo_Robots.git.
Its creation was not part of this turn; preserve it. No fetch/push/publication
was performed. Earlier no-remote statements describe the original recovery.

## Continuation checkpoint — 2026-09-22 19:42 Asia/Dubai

P1 host-only under D-016 remains active; P0 hardware acceptance and every human
gate remain pending. Role migration D-015 already exists; do not duplicate it.
Actual date/time checked in PowerShell. Read AGENTS/CODEX_KICKOFF, active P1,
BEHAVIOR, latest state ledgers/conflicts, public contracts and relevant roles.
No relevant memory hit. Source versions/toolchain unchanged from previous refresh.

Completed this continuation:
- Interfaces first:6e12422 (limiter),4acc9c1 (DIRECT),29779da (approved filters/
  detector),b1a8266 (EventBuffer). New human approvals D-029–D-032 accepted in
  their exact scopes and visibly appended to B5/B11. Never re-request them.
- 7ef428f: DIRECT request/exit executor;0838c64: stall Detector/ReflankLimiter;
  a5fb36b: PhantomFilter/StuckFilter;36767f7: EventBuffer retains first4096.
-101 new independent cases. All authors avoided implementation.cpp reads;
  workers owned disjoint implementation files, root serialized shared contracts.
- Final normal and ASan/UBSan:313 cases/8,149,851 assertions, zero fail/skip.
  Commands/raw receipts are in analysis/P1_filters_events_validation.md. Existing
  locked tests and76 B16 values unchanged. Only two explicitly text-specified
  config constants added (rolling window/capacity), logged in TUNING_LOG.
- Fresh separate Codex read-only scoped review PASS, not cross-model/full gate.
  One MINOR randomized mask coverage gap corrected and rerun: all128 masks now
  checked. Initial313-case receipts preserved. No open production/test failure.
- Exact21-file inert source snapshots separately reconstructed/reviewed; manifest
  refreshed only to approved hashes. Final tooling result is in validation.md.

Implemented policies remain component-scoped. Phantom consumes a chase's edge
once, retains contact history and holds one expiring marker; stuck candidates use
observed min/max continuous-yaw span and latched faults. Detector needs final
governed duties and actual contact/edge history. ALL_IN suppresses its result only.
DIRECT returns exit intents, not unconditional ATTACK permission. EventBuffer
does no clock/I/O or motion control; HAL later owns it, keeps frames recording and
marks incomplete dumps. No full recorder/scheduler or physical claim is made.

Exact next eligible task: B12 ARC_R/L public script contracts, independent tests
and implementation using existing motion primitives. Then remaining escape/
SIDESTEP/re-flank/Robot integration after specific protected decisions in
analysis/spec_conflicts.md. SC-R/S black-direction/pushed-out recovery, SC-T
simultaneous SIDESTEP exits and SC-U actual opener-to-FSM transitions remain
unapproved, alongside prior physical button/QTR/STOP/WAIT questions. No blanket
permission or assumed measurement resolves those. Finish other eligible P1 work.

No board connected/contacted, target compile, upload/reset, motor run, physical
measurement, PINMAP OK, EXPLAINED OK, human gate, remote push or release tag.
Human hardware testing remains deferred to project end under the active goal;
its absence is never a pass. Full P7 completion is still outstanding.

## Continuation checkpoint — 2026-09-22 Asia/Dubai

Supersedes the previous next-task/count statements. Implemented mirrored
SIDESTEP/ARC2071d4f, logical STOP6a3dc29, defensive turn4768eb5. Interfaces were
committed first. New70 independent cases; complete383 cases/9,121,864 assertions
pass normal and ASan/UBSan,48 script checks pass. Fresh separate scoped reviewer
PASS/no open finding; approved23-file inert snapshot refresh. Exact commands,
initial failure and review scope: analysis/P1_flank_stop_validation.md.

Human approvals through D-039 recorded. Only D-039's named established locked
case changed, exactly as proposed; new logical STOP cases now established too.
SC-J/T/U/V/W/X resolved. SC-Y re-flank completion and SC-Z SEARCH side mapping
pending. Next implement B9 steering/D-037 time-only arc, then B8 SEARCH and the
remaining escape/WAIT/re-flank/Robot. Preserve original phase/gate dependencies.
No board action or claimed physical result; P1 host development remains active.

## Latest software checkpoint — 2026-09-22 Asia/Dubai

Added D-036 front steering3f29fae and D-037 duration-only arc6e91778, contracts
d6bdff3 first. Normal+ASan/UBSan419 cases/10,226,416 assertions pass with no
fail/skip;48/48 scripts pass after reviewed23-file manifest refresh. Separate
read-only scoped review PASS/no open finding. Four unsupported REQUIRE macros
in a new unlocked test were caught before build and changed to CHECK with all
predicates preserved. Exact receipts/report: analysis/P1_steering_arc_validation.md.
No existing locked/config changes in this second batch, no hardware actions.

SC-Y re-flank completion/TURN_IN retention, SC-Z SEARCH side mapping, SC-AA
scan IMU-loss fallback and SC-AB unseen-side recency are pending distinct human
questions. Do not infer approval from elapsed time. Read the concrete public
contract recommendations in analysis/P1_search_reflank_contract_audit.md before
their dependent implementations. Continue eligible P1 composition/integration;
P0 hardware acceptance, every human gate and full P7 completion remain outstanding.

## Boundary checkpoint — 2026-09-22 Asia/Dubai

Fusion contract30b16d5 and implementation/tests a54f177 complete this bounded
task. It orders debounce/stuck/cue/phantom/effective bearing, then commits contact
against the final selected state without re-counting observations. Legacy API
tests remain unchanged. Normal+ASan/UBSan444 cases/10,442,964 assertions pass;
48/48 controlled scripts pass. Exact evidence: analysis/P1_pipeline_validation.md.
No open review finding. Collaboration refused a new reviewer thread; reused
p1_next_task_audit stayed read-only. Label that scoped review accurately, not
newly fresh/cross-model/full gate. Current23-file inert hashes reviewed/refreshed.

No existing locked test or config changed after c2d6bfa. The sole earlier locked
amendment remains D-039's exact approved case. All source changes are local,
without push/hardware connection/compile/upload/reset/motor run or physical claim.
Original P0-P7 scope and every human gate remain outstanding as applicable.

Exact next unblocked task: B4.2 table-row executor for fully specified single-front,
diagonal, rear and side rows. Read analysis/P1_escape_row_contract_audit.md; commit
public interfaces first, then independent spec-derived tests and bounded code.
It must not silently select unsupported head-on/three-white/pushed-out/replan
policies. Full Escape/Robot integration remains pending. Await the four already
presented SC-Y/Z/AA/AB decisions without re-asking or treating silence as approval.
Search/re-flank contract audit is saved; no hardware setup is assumed verified.

## Latest row checkpoint — 2026-09-22 Asia/Dubai

Contracts76e0360/c5e80b8 and implementation970e083 add nine specified B4.2 rows.
34 new locked cases are established.478 cases/11,897,401 assertions pass normal
and ASan/UBSan;48/48 controlled script checks pass. Reused separate read-only
review PASS/no finding; exact current23-file inert hashes reviewed/refreshed.
See analysis/P1_edge_rows_validation.md and reviews/P1_edge_rows_codex.md.
No established locked test or B16 value changed;45-degree side angle copies B4.2.
D-039 already records/applies the user's single-case STOP amendment; do not repeat.
No board action, measurement, target compile or human gate. Full P0-P7 stays open.
Next unblocked task: B9 centered qualification and immediate target-loss brake
composition; audit actual loss destination before full Robot integration. Pending
SC-Y/Z/AA/AB/AC and older protected choices remain unanswered, not approved.

## Qualification checkpoint — 2026-09-22 Asia/Dubai

Contractc0b3ad6 and implementation1950635 add the B9 centered-observation counter.
497cases/11,920,333assertions pass normal+ASan/UBSan,48/48 controlled scripts pass.
Reused separate read-only review PASS/no findings and exact23-file manifest review.
See analysis/P1_front_qualification_validation.md and its linked review. Established
locked tests/config unchanged. No hardware action, physical evidence or human gate.
SC-AD entry-count anchor and SC-AE loss-with-residual-target routing were asked
separately; no answer inferred. The counter selects neither behavior. Older
SC-Y/Z/AA/AB/AC and other listed choices remain pending. Next eligible task is
B14 tick statistics from supplied durations, per analysis/P1_fault_contract_audit.md.
