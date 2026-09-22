# Fresh full-core P1 safety and gate-readiness review

Review date: 2026-09-23, Asia/Dubai. This is a genuinely fresh same-model Codex
review context, separate from implementation, independent test authoring and the
reused scoped Robot reviewer. It is not a cross-model review or human acceptance.
The reviewer changed no implementation, test, configuration or shared ledger.

Scope: all current `src/core` implementation modules and public interfaces,
`src/config.h`, the inert P1 app entry, independent component/Robot test coverage,
`docs/ARCHITECTURE.md`, AGENTS R1-R11, BEHAVIOR B0-B16 and accepted amendments
through D-061 (including the 99bd3c8 QTR timing clarification), P1 task/exit
criteria and REVIEW_GATE. D-015/D-016/D-051 and current state ledgers were read.
P1 software work is authorized while P0 acceptance remains pending. The actual
date precedes the 28 September scope-cut decision and 1 October code freeze.

## Findings

No open BLOCKER, MAJOR or MINOR remains in the reviewed software scope. The
initial static pass identified no production safety bypass. Runtime exposed the
policy/expectation gap below; D-061's replacement source, the deadline correction
and final metadata checks now pass the 895-case normal/sanitizer suites and this
reviewer's direct independent reproduction. Actual inert target compilation and
the final controlled tooling suite also passed. This is a software review PASS,
not a human phase gate or physical acceptance.

Findings encountered and their dispositions:

- [MAJOR, coverage; resolved]
  `src/core/fsm_robot.cpp:664`: the B14 QTR warning table row initially had no
  Robot assertion for its continuous actual-pivot/white qualification, strict
  timeout or rearming. The new independent `tests/test_robot_qtr_warning.cpp`
  adds four cases: 1499999/1500000/1500001 us and wrap; enabled, strictly opposing
  actual duties; black/nonpivot reset and subsequent episode; no suppression of
  Escape. The clarification at 99bd3c8 explicitly anchors the interval at the
  first fresh joint observation, without inventing earlier white evidence from
  `applied_us`. No original expected predicate was weakened.
  All four cases pass in the independently read run3 receipt.
- [MINOR, documentation; resolved]
  `docs/ARCHITECTURE.md:109`: the initial graph claimed DEFEND_TURN exited on B7
  turn completion. `DefendTurn::step` retains terminal zero until a current target
  exit or the separate 800 ms deadline. The coordinator corrected the graph and
  added the explicit terminal-zero explanation; both were reread.

- [MAJOR, policy/expectation gap; resolved]
  `src/core/fsm_robot.cpp:539`: initial full execution produced 875/876 passing
  cases and seven assertions failing the new stream property's blanket
  `contract_faults==0` expectation. The first independent diagnostic trace is
  stream212: t5164000/opponent0, then t5364000/effective opponent0x38, line0,
  healthy yaw269 and battery11.7. D-026 correctly provides no bearing for a first
  bilateral-side conflict, so the original required-bearing DefendTurn entry
  rejected and Robot safely inhibited with SCRIPT_START. That behavior followed
  D-060's invalid-required-context policy; this was not an R1/R5/R6 motor bypass.
  The test expectation was broader than that original ambiguity policy. The
  coordinator selected D-061 under D-051 to replace only legitimate unknown
  bearing handling with a zero-demand wait bounded by the existing DEFEND
  deadline, while retaining malformed-context faults. The contract was committed
  as 34c48d0 before dependent changes. Narrow source review of the replacement
  `runDefend`/`finishDefend` path passed: age advances before later capture and
  remains authoritative after capture; front/clear routing and edge/STOP/reset
  clear pending history. No same-tick recursive arbitration was added. Independent
  regressions and the unchanged 10000-stream property pass in the 892-case
  run3 receipt. Original failure
  evidence is retained in `state/analysis/P1_robot_host_20260923_run2.txt` and
  `P1_robot_failure_trace_20260923.txt`; no locked predicate was amended.

- [MAJOR, D-061 deadline anchor; resolved]
  `src/core/fsm_robot.cpp:513`: on actual Escape exit, `routeNormal(true,true)`
  selects DEFEND_TURN but the forced-brake return precedes `runDefend`, where
  pending age is first captured. With legitimate unknown bearing, D-061 says
  the first such admitted observation starts the 800 ms interval. The current
  source instead starts it on the next nondeferred observation; sparse calls can
  extend the wait arbitrarily after DEFEND entry. The new Escape-preemption test
  checks old-history clearing, but not exact expiry from its new exit/entry
  observation. Recommended resolution: anchor pending zero-wait when DEFEND is
  first selected, while preserving D-060's deferred motion, and independently
  test its exact deadline after Escape exit, including a delayed next call.
  The coordinator moved initial capture into `routeNormal`, immediately after
  state selection and before the forced-brake return; `runDefend` only advances
  the captured interval. This source fix at SHA-256 206D3D1D... was independently
  reread and meets the committed contract without changing motion deferral.
  Independent tests now cover exit+799999/800000 and first sparse calls at
  800000/800001/1500000 us, including wrap. Those pass in run3. Their source
  is `tests/test_robot_ambiguous_defend.cpp`, SHA-256 19B8308B... .

The separate scoped reviewer subsequently found a MINOR CONTACT metadata
validation gap: impossible close-cue/FC-only and impact/off-center payloads were
accepted. The revised `logframe.cpp` at DAEE8D7F... was independently reread here:
it accepts centered front rows 2/3/5/6/7 only, and a close-cue flag only for 5/7.
This changes evidence validation, not motion or the legacy generic event codec.
Its new independent literal table covers all eight front patterns, three cue
combinations and all 16 side/rear combinations, plus rejection accounting.
Those three cases pass in run4 and this reviewer's direct reproduction.

## Safety and deterministic-work trace

- **R1:** `countdown::Controller` qualifies the release before `Gate::step`
  captures its time. Gate retains the complete 5100000 us default hold; MODE and
  STOP dominate the GO boundary. `Robot::runLifecycle` selects the gated state
  before motion, `prepareFinalRequest` inhibits every nonmoving/gated/faulted
  state, and `commitAndGovern` emits zero/disabled when inhibited. Actual Robot
  locked tests cover pre-GO boundaries, cancellation/STOP, boot/reset and wrap.
  No GPIO write exists in the core or inert app; this proves logical requested
  output, not real MOTOR_EN/PWM or an organizer's activation interpretation.
- **R2/R3:** the reviewed core has no clock, Arduino, Bridge, serial, network or
  Linux I/O dependency and accepts no transport command. The P1 app calls one
  default BOOT transaction in setup and has an empty loop. `MOTORS_ALLOWED==0`
  is compile-time required. Future HAL/recorder paths remain outside this proof.
- **R4:** loops have fixed sensor/metadata bounds or explicit 3/4-phase limits;
  the rolling limiter is bounded by its fixed configured capacity. No heap,
  exceptions, RTTI, blocking wait or input-dependent unbounded loop was found.
  Finite validation and widened arithmetic protect duty math; timers use
  unsigned deltas or bounded accumulated ages. Consecutive distinct timestamps
  must be less than one uint32 wrap apart. Immediate duplicate timestamps ignore
  changed input/STOP by the explicit public transaction contract and must not be
  reapplied as a fresh tick. None of this measures whole-robot WCET below 800 us.
- **R5:** `Robot::runEscape` precedes all opener/re-flank/normal routing. The
  classifier supplies the sole line mask; fresh persistent white at GO selects
  Escape before an opener. Three/four-white and exhausted replacements inhibit
  until reset. Ordinary exit requires all black and row completion; the exit
  tick brakes. New-bit replanning uses the captured entry-phase pivot direction,
  with at most one replacement per observation. Explicit STOP/contract failure
  closes permission before all motion. Push-through remains disabled and a
  compile-time assertion rejects enabling its unimplemented option.
- **R6:** `prepareFinalRequest` validates the final request, Fusion commits
  contact once to the selected state, then Governor runs once. Voltage
  compensation precedes final cap and slew; braking, reversal and reductions
  take immediate effect. Full duty requires current centered ATTACK contact.
  Front loss brakes on the clearing observation, including residual side/rear
  routing. Stall and pushed-out predicates consume matching actual application
  receipts, not requested duty. ALL_IN suppresses stall only; edge, loss, contact
  and caps remain authoritative. No direct output bypass was found.
- **Evidence:** prior application receipts require matching identity, bounded
  timestamp, finite duty, prior permission and sign/magnitude compatible with
  the request. Missing application inhibits; missing duration only marks timing
  incomplete. Frames use matched actual settings with explicit invalid/clamped
  status; events have bounded metadata/capacity and separate loss counters.
  Synthetic host receipts are not physical application or timing measurements.

## Table and property coverage disposition

The coverage judgment concerns implemented pure decision behavior, not physical
HAL acquisition, matrix rendering, services, recorder transport or DRIVE_TEST.

| Specification | Observable coverage inspected |
|---|---|
| B1/B2/B3 | Actual BOOT/IDLE/countdown/script/normal/Escape/re-flank/STOP states and precedence; full hold and STOP tests; DRIVE_TEST deliberately unavailable in P1 |
| B4 table | All 16 masks in component and actual Robot cases; single/diagonal/head-on/rear/side rows; D-048 three/four-white faults; pushed-out priority; bounded replacements and exit; mirrored row demands |
| B5 table | All front rows and all 128 combinations; side/rear conflicts and unknown history; contact lifetime, phantom episodes and stuck filtering; GO keeps raw yaw history |
| B6 table | Every governor profile at low/nominal/high voltage; approach/contact eligibility; immediate brake/reversal/cap reduction; actual Robot contact and loss composition |
| B7-B12 | Primitive bounds/timeouts/fallback; SEARCH/DEFEND/re-flank selection and completion; six selected modes; DIRECT, mirrored SIDESTEP/ARC and ordered WAIT; current-perception exits and fresh centering |
| B13 modes | Six-mode cycle/accepted-release snapshot and all service intents; logical debounce/short/long/STOP priorities; physical buttons and glyphs remain HAL work |
| B14 faults | Missing IMU/fallback, raw-domain stuck history, low battery/watchdog episodes, supplied tick durations, and new actual-Robot QTR warning episodes |
| B15 | Codec/metadata, retained event capacity, actual-duty receipt events, frame cadence/loss, GO-through-final-stop timing and explicit incomplete evidence |
| B16 | Existing literal/default checks and no current config change; these values are development defaults, not ring tuning |

P1 property evidence includes existing 10000-stream R1 gate/controller tests,
10000 actual Robot streams, primitive/opener/escape mirror and finite-duty
properties, all-mask escape observations, and exact/wrapped boundary cases.
The actual Robot stream fixture uses seed 0x36a891d5, 8000 GO and 2000 STOP-before-GO
outcomes, 5000 wrapped holds and all 16 line masks. It is not exhaustive state-space
coverage. WAIT is explicitly right-sided by D-055 rather than a nonexistent
left-mode pair. Existing component suites remain relevant; their observations
are not relabeled as physical or full-Robot Cartesian-product proofs.

No established locked test has a working-tree modification at review time.
The historical D-039 single-case amendment is explicitly documented; new Robot
locked cases are additions. Test authors used public/specification contracts and
separate files; the reviewer did not change their assertions.

## Runtime, target evidence and gate disposition

Read actual `state/analysis/P1_robot_host_20260923_run3.txt`: 892/892 cases,
13765561/13765561 assertions, zero failed/skipped, direct executable and CTest
exit0. This covers the unchanged locked property, all four QTR cases and all
16 D-061 regressions. It precedes the later CONTACT validator tightening.
Final normal receipt `state/analysis/P1_robot_host_20260923_run4.txt`: 895/895
cases, 13765968/13765968 assertions, zero failed/skipped, CTest and direct run
exit0. The three added CONTACT metadata cases are included.

This reviewer independently executed the frozen `build/host/sumox26_tests` via
WSL and reproduced all 895 cases and 13765968 assertions, zero failed/skipped,
exit0. Own receipt: `state/analysis/P1_fresh_gate_runtime_20260923.txt`; binary
SHA-256 54CD91D0ECFB43A56DA9A1E1A828CD5B8A378443815BE948C3296C5228867E02.
The receipt retains an initial PowerShell capture-parameter error and the clean
buffered retry; the initial capture is not represented as a test result.

Read final `state/analysis/P1_robot_sanitize_20260923.txt`: build and direct run
exit0, 895/895 cases and 13765968 assertions, zero failed/skipped, no sanitizer
diagnostic. Recorded flags are `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`, with both sanitizers on the linker. This reviewer read
the actual receipt; the independent rerun above used the normal binary.

Read `state/analysis/P1_robot_target_app_20260923.txt`: actual board-side inert
app compile/link succeeded, exit0, source digest
`ce90f09dff02447b6197097d0e9d074bc5a0c11813f40a3d4eaa40750b699b91`,
MATCH=0, MOTORS_ALLOWED=0, STARTUP=default. Reported program storage is 125508
bytes, globals 61004 bytes and remaining RAM 201140 bytes. Sources were staged
to the board; the command explicitly reports compile-only with no firmware
upload. It did not start this firmware or test the future full HAL scheduler.

Read `state/analysis/P1_robot_tooling_20260923_final.txt`: 116 controlled tooling
tests passed in 39.167 s, exit0. This is the final reviewed 24-file staged-source
snapshot, not either earlier superseded manifest. Production implementation is
committed at 8692734 and metadata at 59376fe; the inert app/source hashes below
identify the reviewed entry independently of subsequent documentation commits.
All 22 recorded source hashes were recomputed after final validation and matched.

The software parts of P1's exit checklist are evidenced: more than 60 tests with
every locked test and the table/property coverage above; core compiles on the
board toolchain; this fresh full-core safety review has no open finding. Earlier
807-case results or older target builds were not used as proof of the new Robot.

Even with successful software checks, P1 cannot be human-closed: no current
EXPLAINED OK or GATE P1 PASS is recorded, and P0 acceptance remains pending.
The prepared 60-second explanation and corrected diagram support a future human
explanation check; they cannot substitute for one. No PINMAP OK, motor-run
authorization, physical gate/WCET/edge/contact test or P2 authority is inferred.
No hardware operation, upload, reset, motor run, local commit or remote publication
was performed by this reviewer.

## Reviewed source hashes (SHA-256)

These identify the source inspected, including uncommitted production additions.
The implementation freeze matched the coordinator's supplied Robot hashes.

| File | SHA-256 |
|---|---|
| src/core/countdown.cpp | 34558F66B118C8298C0138D62BA4B98437864007935C08FCD9969507C3F1761B |
| src/core/edge.cpp | B48DF54AD7708EC1776B30EDB107FBBED57557B4A218EE1258E42AAEC1E75835 |
| src/core/fsm.cpp | 9334BE82F508064E554A322AC7C11BE598DA73FF49D0CF80FD09DFBF94BC25CB |
| src/core/fsm_robot.cpp | 206D3D1DD82A3CB3BE0EEA2187FA1C703443620A5BF4CAF03D470E902CAB6DAA |
| src/core/governor.cpp | 249259D7230C5E0D033CF3FB3FF938B854A5A0629D22E83C81EEE45B29AD2D68 |
| src/core/logframe.cpp | DAEE8D7FE49D64E1F92102AD68C28817DAC15D2481D98DBB1F62D19DFE73AE32 |
| src/core/motion.cpp | C8F4286E42D964275C269B97DCA9E00B5D8D55524046A3ED63433AE0E9CB9656 |
| src/core/openers.cpp | D924761E1D4AF313530BA57F59949B217F0018915BD31811295D351DC65817B9 |
| src/core/opp_fusion.cpp | 97BB8ED35F3DDFC59A19692DA25452AEABF0E1643404F352D6F036BB53CB5BE2 |
| src/core/stall.cpp | 46E0F67EB3D3B820150D156EB2A1CAE2E074E44C56F98D6AB4B739C837229436 |
| src/core/countdown.h | 1AD9FE88B6A9E368626CCCF65701815BFCE2C8609C9526ED1DCC68FB72B5F9DA |
| src/core/edge.h | 1FB78C92FB46D661272A660A663EF0AAF3AFF416DD6E4B329607C0ABB9134389 |
| src/core/fsm.h | 4FFB1CCCAF44B21DD49A99892CADBBB6F7E21FC1F2CCCBBE11A406CABC6555B9 |
| src/core/governor.h | 48174995C9C420A47BDA8406774CA2241CB36366C476452AA20CA5169FEB5999 |
| src/core/logframe.h | 4CDE17409858BA5E85E610F866537F1687BCEA26BB9BB14B405235DD3345515B |
| src/core/motion.h | 1D8BAA81D23BC794562D9B3F695BA98EACD0A3FEDFC3AE0F0B6AD4923D66FB78 |
| src/core/openers.h | 4EF64DC3CDDEF2ECE35070CDA6D5099644D89935689289983E37B997F056A1BE |
| src/core/opp_fusion.h | 0AFD417533B1186E0A1A9E959655A2D0BAA40D04B119075E40E53D864ED25956 |
| src/core/stall.h | 88ACCBA473A43B04949A30696D968F3AAF308493EF00A9BA16AA40018765B9E3 |
| src/core/types.h | 28067A3E384F07ABDD115B686C22B24D9E2789C117B611548BA4570255177DD7 |
| src/config.h | E09EF8AA5FBC71A3D4F18F35D984B6F83F371946B5F3E2D5294E29659D8EAADA |
| src/app/app.ino | 0143E46AF3D46118955A5F6E7D2B8B543C649FA70A67E2B58178AB01EFC2DA50 |

## Verdict

**PASS — fresh full-core software safety review.** No open BLOCKER, MAJOR or
MINOR remains. Final normal and sanitizer suites pass 895 cases/13765968
assertions; independent normal reproduction, 116 tooling checks and actual inert
target compilation pass. **P1 human gate remains pending:** EXPLAINED OK and
GATE P1 PASS are absent, P0 acceptance is still pending, and physical HAL,
MotorGate, complete-loop timing and ring validation remain separate work.
