# Codex handoff

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
