# D120 B4 integration review

Date: 2026-09-24, Asia/Dubai. Separate same-model context; production and tests
are read-only. This report covers the adopted software contract, implementation,
frozen independent oracles and completed executable evidence. It grants no upload, powered run,
physical acceptance or human phase gate.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the bounded D120 software integration
and compile-only route. Two contract ambiguities were resolved before oracle
freeze, as recorded below. No production repair was required by the C++ tests.

## Contract preflight

Reviewed AGENTS.md, current P2 progress, D051/D075/D119/D120, P2 B4/B7, the D120
contract/public conditional headers, existing Robot lifecycle/escape/request
pipeline, Governor, MotorGate, Transaction and D103 service-reset owners.
The contract/header adoption is `f4a300c5`, following completed D119 `1c387810`.
This is the scheduled Thursday24 September bench-preparation period; no schedule
or human gate is inferred from software progress.

- Profile1 is a compiler-wide fixed identity, forbidden with MATCH and default
  off. Its additive public fields and governor enum preserve profile0 layout and
  old enum values. OPENER carries explicitly scoped bench meaning; future CSV
  evidence requires the build/profile sidecar because CSV bytes alone do not
  identify this profile.
- Actual Runtime/Transaction/Robot/Governor/MotorGate and real receipts retain
  authority. No synthetic input, initialization, permission or patched result is
  allowed. The existing full hold, source admission and R1/R4/R5/R6 remain.
- The finite sequence uses an electrical STAND_DUTY cap after compensation and
  normal slew. BRAKE enables zero duty; COAST inhibits both sides. Edge escape
  keeps its existing caps and wins over sequence advancement/completion/gaps.
- Completion inhibits immediately in OPENER and requests Lifecycle STOP on the
  next distinct admitted tick. Successful escape exit inhibits immediately in
  EDGE_ESCAPE and follows the same real STOP ownership. Active/faulted escape
  is not prematurely stopped by sequence cancellation.
- A prefreeze ambiguity about sequence-FAULT UI state was raised and resolved:
  SCRIPT_RESULT retains existing immediate ui_state STOPPED finalization;
  Lifecycle itself reaches STOP on the next distinct tick. Only natural COMPLETE
  retains OPENER on its first terminal observation. The contract now names this
  distinction explicitly.
- The owner `stand_stopping` flag is explicitly latched until reset after
  completion/fault/escape exit. Earlier explicit STOP/source cancellation need
  not set it. Existing qualified STOP and independent contract faults retain
  their higher priority and immediate inhibition.
- Additive Sequence::interrupt is a clock-free owner cancellation, active-only
  for STOP/EDGE. Its rejection is passive. Robot publication must suppress old
  helper pulses on later escape/STOP/duplicate observations without inventing
  a new helper event or changing a previous terminal reason.
- Profile1 refuses D103 at Transaction and Runtime. The actual eligible reset
  history, not only ineligible early calls, must prove the boundary. Full owner
  reset reconstructs the same profile and normal BOOT/hold sequence.
- The named wrapper has empty grants, actual native owners and M0/MATCH0 only.
  Its literal compile-only route adds the profile flag to every C/C++ unit.
  Existing routes, upload allowlists and established locked tests stay intact.

## Implementation review

- `src/core/fsm_stand.cpp:12` preserves permission/STOP, existing escape, then
  sequence priority. Edge at GO can prevent helper start while still latching
  owner interruption; active/faulted escape persists. Successful escape exit and
  natural COMPLETE inhibit on the current observation and latch the actual
  next-tick lifecycle request in `src/core/fsm_robot.cpp:324`. Sequence FAULT
  retains SCRIPT_RESULT and existing immediate STOPPED UI finalization.
- `src/core/fsm_stand.cpp:55` copies helper state without replaying old fresh or
  changed pulses after rejected interruption. Duplicate observations use the
  established Robot cache and clear action pulses. STOP/source/receipt failures
  cancel the active helper; its terminal reason cannot be overwritten later.
- `src/core/governor.cpp:31` gives regular script drive the final electrical
  STAND_DUTY cap after compensation. Existing slew and reversal behavior remain;
  BRAKE and COAST use the actual final output/Gate path. Opponent/contact data
  does not switch this profile into ordinary combat or stall recovery.
- `src/app/transaction_service.cpp:30` refuses D103 without mutation;
  `src/app/runtime_service.cpp:134` and `:151` refuse observation/application of
  the reset. An optional local grant can still put Runtime in STOP_OBSERVING;
  the contract requires no pending/fresh/service-only reset publication, not a
  blanket prohibition on that existing Runtime state.
- Default0 conditionals preserve the existing public object layout and enum
  values, and the config diff changes no established tunable. The new profile
  accepts only 0/1 and rejects MATCH. The dedicated host targets compile all
  participating units with one profile identity; existing targets stay profile0.
- `bench/motor_direction/motor_direction.ino:10` statically requires profile1,
  MATCH0 and M0. Its actual native owners use `SetupGrants{}` and no dump port.
  Unchanged MotorGate computes enable through `MOTORS_ALLOWED != 0`; this build
  cannot request a high EN/nonzero motor write through that path. This is source
  reasoning about an unexecuted target, not physical output measurement.
- The literal `bench/motor_direction` route has exact C/C++ flags
  `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1`, checked default FQBN and the
  existing pinned build checks. Immediate/MATCH/upload attempts fail before
  board work; other routes reject the extra flag. No upload allowlist changed.

## Oracle and host evidence

No implementation execution by this reviewer occurred before the independent
oracle freeze at 2026-09-24T05:14:46.6546014+04:00. Exact copies and manifest are
in `state/analysis/P2_stand_integration_raw/oracle/`: ordinary `.cc` hash
`5bb173442360103dc2a270737e192356078c2381bdeaada4fcadd021672e9e59`, new locked
`.cc` hash `4546df243377a915693a52d347ab9e3f0877ad504bf9d087f8667b824425ff1b`,
contract `d34c096e1b3f1fca47feadf7f5862893aced8fefffc57f396c0c965482b9168f`.
The test author used public specifications/headers and existing fixtures, not
implementation source. This is independent context, not a different model.

The 18 unconditional cases exercise actual Transaction/Gate behavior: full hold
and adjacent/wrapped time, all twelve rows, compensated duty cap/slew/reversal,
BRAKE/COAST, opponents, explicit STOP at every row and exact completion, edge
at GO/final boundary/gap, persistent edge fault and successful escape exit,
source/receipt failure, script gap fault, duplicate admission, helper interrupt
immutability, eligible Transaction D103 refusal and Runtime flags. A nineteenth
configured case drives the genuine post-STOP Runtime MODE gesture.

Reviewed coordinator records under `state/analysis/P2_stand_integration_raw/`:

| Evidence | Result |
| --- | --- |
| `coordinator/normal.json` and `.txt` | All four CTest targets passed. Before/after/current hashes agree. |
| `coordinator/sanitize_build/LastTest.log` | Main 1496 cases / 50418546 assertions; Gate 187 / 4536952; stand M0 18 / 200690; stand M1 18 / 200641. All passed, zero failed/skipped. |
| Sanitizer `flags.make`, `link.txt`, run/archive records | Actual ASan/UBSan compilation and linking verified for all four targets; return codes zero. |
| `configured/summary.json` and direct outputs | Each M0/M1 normal and ASan/UBSan run passed all 19 cases; M0 207591 assertions, M1 207542. |
| `coordinator/policy_repaired.json` and `.txt` | 54 methods passed: nine new route checks plus 45 prior policy/tool checks. |
| `reviewer/profile_compilation.json` | Nine bounded header checks passed: five permitted profiles, four intended compile refusals. |
| `reviewer/final_evidence.json` | Nine frozen public files still exact; each host record's 51 before/after/current source hashes match; established locked tests unchanged from D119. |

The normal transient LastTest file was lost to WSL shutdown before its separate
archive. Normal four-target success is retained in complete command/status/output;
the case/assertion counts above come from the preserved sanitizer log only.
Configured runs changed exactly three A1-window lines in an isolated copy;
production values and oracle bytes stayed exact. This does not establish physical
A1 thresholds. Original policy failures and oracles were preserved; the only
repairs renamed a shadowed fixture factory and supplied the legacy import path,
without changing assertions or production behavior. No full suite was rerun by
this reviewer.

## Target evidence

`reviewer/check_target_evidence.py` independently rehashed both final local ELFs,
all 94 staged source files for each target, checked receipt source hashes and
flags, and reproduced the established conditional loader accounting. Results are
in `reviewer/target_evidence.json`; original checked receipts/artifacts are under
`coordinator/app/` and `coordinator/motor_direction/`.

| Build | Verified identity and conditional footprint |
| --- | --- |
| Default app/M0 | Source `ef1efc59643db29e091ced56e594afcab17e3dd2d259da8ab06af902e78b5779`, receipt `9afff71f2bbf4378bd745477d76b85cd`; ELF `8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257`, ZSK `c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5`, loader `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` are byte-identical to D119. ELF 176048 bytes; copied payload 257280; conditional peak 262136/free span 8. |
| Dedicated motor_direction/M0 | Source `24fe6356ad830da9d0b85bfb39995a7753719fa1d26d53ea58702088aeb1c482`, receipt `8ef4cd1181ec4554bda17bcfb06f2d44`; ELF `50cace032b98014382f191a654781e6d7b12794d80b2b87b4b9a441805f9388d`, 153392 bytes; copied payload 244360; conditional peak 248576/free span 13568. |

Both compile-only receipts returned zero with the expected pinned checks and no
external sketch libraries. The bench final ELF retains stand route/sequence,
omits ordinary routeNormal/checkStall, and has exactly one strong loopHook.
Its undefined imports are a subset of the unchanged default ELF's imports under
the same loader. Thus the default loadable footprint is unchanged, and the new
bench footprint is evaluated against the existing pinned model. The free spans
are conditional pristine-pool model outputs, not measured loaded RAM, stack or
WCET. Compiler low-memory warnings are preserved. No reviewer board action,
upload, MCU read/write/reset, UART action or new run claim occurred.

## Verdict

PASS for the adopted D120 software integration, frozen host expectations and
literal checked compile-only route. No material finding remains in this scope.
Review modifications are limited to this report and private reviewer evidence.

Physical B4 direction/brake/coast, source qualification, pin/electrical acceptance,
powered kill latency, full-source WCET/stack and a fresh specifically authorized
motor run remain unqualified. B7's separate reversal/governor issue and native
dump prerequisites are unchanged. This review passes no human phase gate and
does not authorize upload or motors. The next action is the coordinator's local
evidence/state commit; physical acceptance remains a separate human-owned step.
