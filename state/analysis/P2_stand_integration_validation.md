# D120 real B4 controller integration validation

2026-09-24 Asia/Dubai. P2 software, D051/D075; contract adoption f4a300c5.
No human phase gate, physical acceptance, upload or motor-run authority follows.

## Change and authority

The immutable compiler-wide B4 profile routes the D119 finite twelve-row sequence
through actual Robot/Transaction/Governor/MotorGate. Full hold, current source and
actual receipt checks remain; STOP and existing escape preempt. Final regular
sequence duty is capped at0.25 after compensation; brake is enabled zero and
coast disables shared EN. Completion/escape exit inhibits immediately, then the
next distinct observation enters actual Lifecycle STOP. D103 service reset is
unavailable. No ordinary combat routing or contact authorization is created.

Default profile0 behavior/layout is preserved. The separate motor_direction
wrapper requires profile1/MATCH0/M0, with empty native grants and no dump port.
The literal checked route is compile-only; no inert upload allowlist entry changed.
OPENER in this profile means the bench script; future persisted evidence requires
its build/profile sidecar. Existing CSV/state enum and old locked tests are intact.

## Independent expectations and host evidence

Separate test-author context read public headers/specifications and prior fixtures,
not implementation.cpp. Before first execution it froze integration oracle
5bb17344 and new locked safety oracle4546df24 against contractd34c096e. Exact
copies/manifests are in P2_stand_integration_raw/oracle. Two prefreeze clarifications
state first SCRIPT_RESULT fault UI STOPPED and the until-reset stand_stopping latch.
No established locked case was changed.

- Full normal CMake/CTest: all4targets passed, including unchanged main/Gate targets
  and18new cases each in profile1/M0 and profile1/M1. Actual command, complete build
  output/status and before/after source hashes: raw/coordinator/normal.json/.txt.
  WSL auto-shutdown removed the transient normal build before its separate
  LastTest archive; do not infer assertion counts from that unavailable file.
- Full ASan/UBSan: main1496cases/50418546assertions, Gate187/4536952,
  stand M0 18/200690 and M1 18/200641; all passed,0failed/skipped. Actual
  LastTest.log, flags.make, link.txt and CMakeCache retained in raw/coordinator/
  sanitize_build. Sanitizer instrumentation/link flags were checked explicitly.
- Configured synthetic A1 overlay:19cases each, normal and ASan/UBSan, both M0/M1;
  M0 207591 assertions and M1 207542, no failures/skips. Only three isolated config
  lines changed; production/source/oracle hashes unchanged. Direct binary outputs,
  exact commands/statuses, overlay diff, compiler/link flags and executable hashes:
  raw/configured. This is fixture evidence, not a measured A1 profile.
- 54script/policy methods passed, including9new route cases and45unchanged prior
  app/motor-stand/recorder cases. Original failures preserved: launcher omitted
  legacy test_tools import path; new coordinator-authored factory name shadowed a
  local variable. PYTHONPATH and factory rename repaired these harness issues;
  no expected condition or production source was changed to obtain this pass.
- Separate reviewer private compiler probes:9/9 accepted/rejected profile checks.

No production repair was required by any C++ test. The independent review is
separate same-model Codex review, not cross-model or human gate review.

## Board-side build evidence

Default/M0 compile-only returned0, sourceef1efc59, checked receipt9afff71f. Final
ELF8379f152, ZSKc60443cd and loader39d4a4fd are byte-identical to D119/D118.
176048byte ELF;257280byte copied payload; retained conditional loader model
262136/262144,8byte free span. This preserves the previous narrow margin and
does not supply a fresh loaded-RAM/WCET measurement. Full checked receipts,
source manifest, pulled final ELF and local accounting: raw/coordinator/app.

Dedicated motor_direction compile-only returned0, source24fe6356, receipt8ef4cd11,
finalELF50cace03,153392bytes. Copied payload244360; conditional pristine loader
peak248576/free13568. Actual stand sequence/routing symbols are retained;
routeNormal/checkStall are absent. Strong empty loopHook remains; used imports
are a subset of the unchanged default under the same loader. The separate reviewer
rehashed both94-file stages against current sources and independently reproduced
both loader accounts (raw/reviewer/target_evidence.json). Compiler low-memory
warnings are retained. This is target compilation/model evidence, not a board run.
No MCU upload/read/write/reset, UART action, new run claim or native grant was used.
Last observed MCU remains the historical consumed D118 default/M0 run.

## Limits and next action

This task implements and verifies directional-controller software. Physical B4
still needs sensors/source qualification, PINMAP/electrical acceptance and a fresh
identified STAND OK run with motor-capable firmware. Bare-board compile success
does not establish direction, brake/coast physics, PWM frequency or kill latency.
B7 full-reversal/R6 conflict, full-source WCET/stack and native dump prerequisites
remain separate. P2 and all earlier human gates remain pending.

Scoped separate review PASS with no open material findings:
state/reviews/P2_stand_integration_review.md. The raw artifact index records
146files/1401981bytes, including original failures. Its initial overbroad guard
also recorded a failure because the independent author created two C++ test files
during a Python-only policy run; all original hashes were unchanged. The repaired
guard admits only those exact added paths for that run and preserves all others.
The current
session performed two Linux builds only; previous run claims remain consumed.
