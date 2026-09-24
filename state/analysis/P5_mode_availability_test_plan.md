# D134 independent mode-availability oracle plan

Prepared 2026-09-24 against adopted `P5_mode_availability_contract.md` and its
public interface commit `27bc075a`. No production implementation body, including
`board_tool.py`, was read. No test was imported, compiled or executed by this
author. Root freezes these source bytes before implementation execution.

## Sources and interpretation

- `docs/BEHAVIOR.md` B7, B12 O1-O4, D033/D034/D055, B13 and B15.
- `docs/prompts/P5_openers.md`, including the explicit D034 qualification wording;
  `docs/PLAN.md` sections3/6 and the D134 adopted contract.
- Public `types.h`, `countdown.h`, `openers.h`, `fsm.h`, `motion.h`, `logframe.h`,
  `motors.h`, `ui_display.h`, `config.h`; existing public test fixtures and tests.
- `P2_button_routing_contract.md` bounds explicit source/decision continuity to
  5000us. Fresh admitted ButtonEvidence therefore fills gaps at 5000us while
  retaining the prior held button until the requested new edge. These are logical
  qualified inputs; no configured ADC window or physical decoder claim is needed.
- `P2_matrix_contract.md` supplies independent literal digit/icon pixels;
  `P1_robot_event_contract_audit.md` adopted D060 metadata supplies START_RELEASE
  and GO details1..6. Disabled execution choices remain valid historical IDs.

The independent mode-list oracle is the literal mandatory IDs1/2/3, optional
pair4/5 and independent6; it never derives expectations from modeAvailable.
MODE_DEFAULT is tested as the selected configured default rather than assuming1
in configured variants. Current source defaults remain the separately asserted
literal1 values in the existing config registry.

## New C++ sources and coverage

`tests/test_mode_availability.cc`: **16 cases**:

1. Compile-time query use plus all256 underlying enum byte values.
2. Two complete numeric menu cycles, wrap and reset, including timestamp wrap.
3. Exact599999/600000/999999/1000000us first-release durations and a sub-debounce
   MODE pulse; first NONE on the long deadline never toggles the service menu.
4. Actual Robot legacy/explicit qualified menu cycles; all4 service items and
   return to the retained match mode; construction/reset default.
5. Every available choice captured only at accepted START release, kept through
   the full hold and GO, with real MotorGate application receipts.
6. All invalid Flank IDs, including each disabled ARC mirror, replace an active
   SIDESTEP with latched INVALID/zero; later target/time observations cannot
   revive it; reset and mandatory restart remain possible.
7. Enabled mirrored pivots retain front-ignore behavior and exact B7 timed
   transition at100000us SIDESTEP/160000us ARC, including timestamp wrap.
8. Disabled WAIT refuses starts and every7-bit cue/mask with no phase/cue/timeout
   pulse, zero INVALID motion and brake, across reset and wrapped start time.
9. Enabled WAIT inclusive300ms approach cue starts its complete RIGHT pivot,
  250ms traverse and110-degree timed turn-in; terminal SEARCH/brake at the exact
   boundaries preserves D055.
10. Actual DIRECT front exit uses TRACK twice then ATTACK on its third centered
    observation, without contact and under the unchanged0.30/0.60 governor caps.
11. Actual available flank mirrors ignore front in PIVOT, then hand over on the
    same TRAVERSE-entry observation through the existing centered qualification.
12. Actual DIRECT side/rear exits select DEFEND_TURN; a genuine countdown front
    snapshot whose raw disappearance has completed30ms clear selects SEARCH.
13. Actual enabled WAIT ordered cue produces a full pivot before front handover.
14. All4 service START intents cannot capture/start a match; DRIVE_TEST remains
    unavailable in these ordinary-profile targets.
15. Actual Robot duplicate timestamps ignore altered input and cannot replay
    mode changes/events or cause a repeated MotorGate application.
16. Literal glyph pixels, frame mode byte, event metadata/encoding and decoded
    event validation preserve all6 historical IDs in every reduced build.

`tests/locked/test_mode_availability_safety.cc`: **4 new cases**:

- R1 every available mode, both logical source modes and ordinary/wrapped clocks:
  no EN/PWM/nonzero receipt before5100000us from accepted release, including the
 5000000us nominal-hold boundary and5099999us; GO at5100000us only.
- R5 every15 nonblack masks, every available mode, both first-GO and later-opener
  observations: same-observation EDGE_ESCAPE and initial zero physical PWM.
- Immediate STOP at a prospective GO/white/target tie; reset-only inhibition;
  separate genuine post-GO BOTH20ms qualification+1000ms hold with exact
  deadline-minus-one and deadline observations, retaining STOP over later white.
- **10000 fixed-seed bounded legacy streams**, seed0xd1345afe, randomized start
  timestamps/menu counts/sub-debounce START pulses and12 hold-time sensor samples:
  actual MotorGate never writes HIGH/nonzero PWM through5099999us. Explicit
  source paths are exercised by the deterministic cases above, avoiding millions
  of redundant admission samples in the property loop.

`tests/fixtures/mode_availability_fixture.h` owns no production selection API.
It uses actual Robot+MotorGate and the existing finite `app_test::Port` callbacks,
including quantized applied receipts. There is no synthetic receipt substitute.
No disabled-mode Robot injection is possible through its public interface:
the internal dispatch guard remains a separate source-review responsibility.

## New Python coverage

`tests/tooling/test_mode_availability.py`: **26 methods** (16 direct grammar,
6 real stage/flash,4 public-header/config-registry methods).

- All4 pairs and all6 defaults, literal0/1 and lowercase U/u, whitespace/comments;
  rejects disabled defaults, each missing partner/default, duplicates and active
  references, macros/conditionals even#if0, alternate declaration/type/initializer
  forms, signs/hex/leading zeros/non-ASCII numbers/suffixes, oversized literals
  including10000-digit inputs and unsigned-width aliases.
- Both-absent legacy acceptance, comments/quoted declaration lookalikes inactive,
  quoted text unable to supply a missing active partner, unrelated completed
  conditionals accepted; malformed quotes/comments, invalid UTF-8/read failures,
  splices and code-level digraphs reject before the legacy return.
- Splices cover LF/CRLF/horizontal whitespace and comments/quotes/directives.
  Digraph controls distinguish code from ordinary quoted/commented text.
- Existing D132 temporary-root fixture is composed without subclassing its
  TestCase, retaining independent new method count and actual opaque stage/flash
  behavior. App, P0 bench and reactive bench stage all admitted pairs/defaults
  byte-for-byte; the actual copied destination is validated exactly once.
- A deliberately corrupted staged config cannot borrow valid root admission;
  invalid mode values/defaults/partners refuse before board operations. Historical
  both-absent staged bytes still pass. Valid app/reactive compile-only flash mocks
  retain inert flags, source hash and exact config bytes for each pair.
- Copied public types.h plus current full config.h compile for all available
  defaults and reject disabled/default-out-of-range choices, switch2 and both
  missing symbols. This invokes host g++ only when root executes the frozen test.
  Tool compatibility with old source never becomes fallback definitions for new
  core. Oversized literals are tested in the parser before narrowing.
- Independent tests call the established config-registry assertion against
  copied configs and require its rejection of each new default drifting to0 or2.
  The only established-test edit is2 literal dictionary entries in
  `test_p0_config.py`; every assertion, original B16 count76 and wrapper remains.

Stage lexical failures retain D132-first validation/error identification. Direct
new-helper rejection requires identified mode admission. These tests do not
require relabeling shared malformed-text errors on stage/flash paths.

## Execution requirements and boundaries

Root owns CMake, copied-config runners and execution. Dedicated ordinary-profile
`mode_availability_m0_tests` / `mode_availability_m1_tests` compile the2 new .cc
files with the established B4_HOST_SOURCES, including actual Robot, MotorGate,
ui_display and logframe. Add `tests` and `host/third_party` includes if not inherited.
All other behavior profiles are0. No new macro, runtime setter or configured ADC
window is required. Compile4 separate source copies whose only availability
values are00/01/10/11; also exercise enabled optional MODE_DEFAULT variants.

Run normal/sanitized targets and Python under the established Linux g++ runner
after source freeze. Existing41 protected files remain unchanged; existing
all-six tests run in shipped11/default1 configuration. P4 reactive and P3 service
regressions remain independent root matrix targets, preserving their original
stimuli/assertions. Production-layout/bounded-loop/no-authority review and target
compile-only fit evidence are separate root/reviewer responsibilities.

Current date24September precedes the28September scope-cut deadline. This is
software preparation for the documented option, not a forced mode removal,
hardware measurement, motor authorization or human phase gate.
