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
and the human gate. Do not implement P1 strategy while P0 is pending.
All deadlines use Asia/Dubai: P3 scope cut after 28 September; P6 requires P4 by
30 September; freeze 1 October at 21:00; rehearsal 2 October; competition 3 October.
Current date is the plan's P0 day; no scope cut or freeze applies yet.
