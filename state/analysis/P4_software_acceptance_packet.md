<!-- Maps P4 requirements to existing software and retained evidence. -->
<!-- Keeps software verification separate from physical trials and human gates. -->
<!-- Source and receipt inspection only; no tests or hardware operations for this packet. -->
# P4 software acceptance packet

Snapshot: 2026-09-24, Asia/Dubai. **Every physical P4.1-4.7 metric remains pending.**
The user's hardware-at-end direction advances software work under D128; it does
not create GATE P3/P4, tuning evidence or permission to run motors. The trial
requirements remain [P4_hunt_push.md](../../docs/prompts/P4_hunt_push.md).

## Software evidence available now

- **D128 implemented, host-tested, target-compiled and scoped review PASS.**
  [Validation](P4_reactive_profile_validation.md) and
  [independent review](../reviews/P4_reactive_profile_review.md) bind all 12 normal
  host targets, reactive M0/M1 normal/sanitized and configured-button tests, and
  checked inert builds. Non-edge GO visibly enters actual SEARCH; subsequent
  observations use normal reactive arbitration. Openers do not execute. Edges
  retain priority. The actual reactive ELF is `01e39e39...` for staged source
  `9ddaa2aa...`; exact bytes, manifests and receipt are under
  [P4_reactive_profile_raw/reactive_test](P4_reactive_profile_raw/reactive_test/).
  The loader model gives 6512 bytes free for that inert profile, not measured
  live RAM or stack. Default app modeled headroom remains only 16 bytes.
- **D129 implemented and host-tested; native validation pending.**
  [Validation](P4_timing_evidence_validation.md) binds all14 normal targets,
  30-case M0/M1 normal/sanitizer,32-case configured normal/sanitizer,
  149 tooling and2 registry checks. The reproduced chronology defect is fixed;
  the unchanged40-assertion reproducer and eight further private cases pass.
  [Separate scoped review](../reviews/P4_timing_evidence_review.md) records the
  final disposition. Original interrupted runs, first tooling failure and its
  independently adjudicated unaccepted-oracle correction are retained.
  No D129 target compile/fit claim: the latest
  [board inventory](P4_timing_evidence_raw/resume_adb_inventory.json) found none.
- **D130 analyzer is proposed only.**
  [P4_loss_analysis_contract.md](P4_loss_analysis_contract.md) is a draft;
  `tools/analyze_target_loss.py` does not exist at this snapshot. Existing
  [validate_csv_bundle.py](../../tools/validate_csv_bundle.py) checks local bundle
  structure, owner consistency and declared provenance, not P4 timing acceptance
  or physical origin.

## Requirement-to-evidence map

The tests below are existing software checks; none substitutes for the physical
success counts in the last column. D128's validation above supplies the retained
regression execution evidence.

| Requirement | Actual implementation and relevant tests | Remaining physical check / dependency |
|---|---|---|
| **4.1 Acquire and push** | [fsm_robot.cpp](../../src/core/fsm_robot.cpp) routes actual Search, normal perception, contact and Governor; [fsm.cpp](../../src/core/fsm.cpp) implements Search and steering. Existing `tests/test_search.cpp`, `test_normal_perception.cpp`, `test_opp_memory_contact.cpp`, `test_governor.cpp`; D128 profile tests cover all modes/masks and post-GO qualification. | Ten random box placements including sides/rear: at least 9/10 acquired within 3 s of GO, at least 8/10 pushed out with robot staying in. No acquisition or push result measured. |
| **4.2 Lost target** | NormalPerception front-loss brake and immediate Governor zero exist. [fsm_timing.cpp](../../src/core/fsm_timing.cpp), actual Runtime source projection and [reactive_timing wrapper](../../bench/reactive_timing/README.md) add D129 trace without changing motion. `tests/test_normal_perception.cpp` and `test_governor.cpp` cover loss/brake semantics; D129 receipts above have limited current status. | Ten genuine ATTACK approaches, sideways string removal: 10/10 brake and stay in. At current `OPP_CLEAR_MS=30`, observed interval must meet 35000 us bound. D129 target qualification and proposed offline analysis remain dependencies. `ATTACK_APPROACH_DUTY=0.60` is an unchanged default, not a measured safe maximum. |
| **4.3 Defend** | `DefendTurn` in `fsm.cpp`, `runDefend()` in `fsm_robot.cpp`; `tests/test_defend_turn.cpp` and `test_robot_ambiguous_defend.cpp` cover capture, target priority, fallback and bounded ambiguity. | Face targets at each side's 90 and 135 degrees within `DEFEND_TIMEOUT_MS=800`, 8/8. Host deadline checks do not establish physical facing accuracy. |
| **4.4 Push-through** | [edge.cpp](../../src/core/edge.cpp) enforces `EDGE_PUSH_THROUGH_MS==0` by static assertion; `tests/locked/test_edge_guard.cpp` and other locked edge tests prove the existing immediate-escape behavior. | **Positive push-through is not implemented. Keep 0.** A bounded implementation and independent safety verification are required before the prompt's 20 ms tuning steps can even compile. Later physical tuning requires 4.1 still passing with zero self-exits; never exceed 100 ms. Do not remove the guard merely to tune. |
| **4.5 Stall/re-flank** | [stall.cpp](../../src/core/stall.cpp), `checkStall()` using applied duties, `Reflank` and limiter in `fsm.cpp`; `tests/test_stall_detector.cpp`, `test_reflank.cpp`, `test_reflank_limiter.cpp`, plus D128 actual-owner scenarios. Contact/centering and edge safety remain prerequisites; ALL_IN suppresses stall only. | With tethered immovable box, start REFLANK within `STALL_MS+200=1200` ms, reach its side 8/10, never exceed `REFLANK_MAX_PER_10S=2`. Inspect 4.1 logs for false triggers. Stall remains an inference without encoders; `STALL_USE_IMU=0` unchanged. |
| **4.6 Spectators** | `PhantomFilter` in [opp_fusion.cpp](../../src/core/opp_fusion.cpp), `PHANTOM_SET` recording in `fsm_robot.cpp`; `tests/test_opp_filters.cpp`, `test_imu_provenance.cpp`, `test_robot_events.cpp`. | Person 30 cm beyond border, no box: twenty 60 s runs, zero exits and actual phantom events. Qualification needs the real chase/edge/no-contact and valid-heading conditions; no event must be fabricated to satisfy the trial. |
| **4.7 Stuck sensor** | `StuckFilter` masks latched faulty bits until reset; Robot publishes `OPPONENT_STUCK`. Existing `tests/test_opp_filters.cpp`, `test_imu_provenance.cpp`, `test_robot_events.cpp`. | Card 5 cm before one side sensor: observe real fault indication, ignored bit and hunting with others. Diagnosis requires continuous detection for at least `OPP_STUCK_MS=5000` and valid accumulated-heading span strictly greater than 360 degrees; stationary detection alone is insufficient. |

## Conditions for a later hardware session

The prompt requires actual P3 acceptance, a roughly 20 x 20 cm matte-black
2.5-3 kg test box and fresh `RING OK` for the session. Motor-capable runs still
need their specific human authorization; these inert wrappers and host M1
fixtures provide none. Current button windows remain unconfigured
(`BUTTON_WINDOWS_CONFIGURED=0`), wrappers use empty SetupGrants, and neither
reactive wrapper has a motor-capable upload key. Physical calibration, source
readiness, wiring/motor safety and a reviewed runnable artifact must be resolved
through the existing owners before a real trial.

Actual loaded RAM/stack and full-source tick WCET under 800 us remain pending.
Native recorder delivery/ownership/framing and throughput qualification also
remain separate; see [transport validation](P2_recorder_transport_validation.md)
and [FIFO validation](P2_dump_fifo_validation.md). Preserve original bundles,
build/config identities, loss fields and trial outcomes in the existing evidence
workflow; name actual logs and tuning changes in `state/TUNING_LOG.md`.

D129 measures source acquisition to matched applied-zero receipt, interval
`[A-E, A-S]`. It does not measure the physical removal instant, first PWM edge,
mechanical rest or staying in the ring. Its one candidate cannot be replaced by
a favorable retry. M0/no prior actual positive approach cannot supply a qualified
trial; missing tails, interruptions and losses are not passing measurements.
Periodic 25 Hz frames alone cannot prove the 35 ms limit.

No P4 gate is declared. The prompt still requires all seven physical checks,
safety-auditor PASS, review with no open BLOCKER and the human's `GATE P4 PASS`.
P6 eligibility uses the **actual** gate date by 30 September, with the stronger
28 September P3 scope-cut rule retained from [PLAN.md](../../docs/PLAN.md).
Software scheduling or this packet does not satisfy either gate.
