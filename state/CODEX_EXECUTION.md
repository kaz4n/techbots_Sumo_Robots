# Execution checklist - 2026-09-23 09:26 Asia/Dubai

PROGRESS.md is authoritative. Full goal ACTIVE/incomplete; no human gate passed.
D075 explicitly permits P2 software preparation while hardware is untested.

| Existing task | Verified status/evidence | Remaining |
|---|---|---|
| P0 verification/toolchain/diagnostics | Installed/source/actual inert results | Optical/cold-start/pin/electrical acceptance and gate |
| P1 core | Full review/target evidence; current1030host tests pass | EXPLAINED OK and human GATE P1 PASS |
| P2 B4 MotorGate boundary | IMPLEMENTED1c45f72; host normal+sanitizer; target both modes; freshreviewPASS | Native checked Port, PWM settling/electrical/stand proof |
| P2 B8 offline storage/CSV | D069-D074 implemented/reviewed;25Hz;381currenttooltestsPASS | Live bounded IDLE transport, actual RAM/200s/no gaps |
| P2 B1 opponent inputs | NEXT software task | Installed checked GPIO audit, header contract, independent tests, compile |
| P2 B2/B3/B5/B6 | Unfinished | Real drivers; SC-A/B/I/AG dependencies |
| P2 integration/B7/P3-P7 | Unfinished | Full HAL/scheduler/WCET, acceptance and per-run permissions |

Latest validation: full1030cases/20982541assertions and separate active37cases/
3796846assertions pass normal+ASanUBSan;381toolsPASS. Probe source807b5768 compiled
on actual board Linux: default76220/31276B, enabled76692/31612B program/globals.
Evidence P2_motor_gate_validation.md/raw/failures and separate reviewer report.
These are not physical settings, fullfirmware RAM, phase gates or motor permission.

Next: B1 contract/audit; preserve raw polarity for Robot, explicit invalid reads,
fixed work and real evidence. New MotorGate tests are now locked. App stays inert,
last MCU imageQTR61d7a2d0 unchanged. No native MotorGate adapter or pin approval.
Original scope cuts/deadlines remain. No live jobs. Recheck disk; /dev/shm artifacts
are temporary. Resume software, not old blocked audits: user changed eligibility.