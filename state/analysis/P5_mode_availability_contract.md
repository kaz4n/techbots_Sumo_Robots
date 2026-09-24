# D134: P5 optional-mode availability contract

ADOPTED under D051 and the user's hardware-at-end scheduling direction,
2026-09-24. P4 software review passed in39791703; actual P4 acceptance remains
pending. Active software work advances to P5. This does not grant a human gate
or hardware/motor permission. The independently reviewed proposal is retained
in cf35d0a8 and P5_mode_availability_draft_review.md.

## Purpose and existing behavior

P5's exit criterion permits optional ARC and WAIT to pass or be removed from
the mode list (`docs/prompts/P5_openers.md:25`). PLAN's end-28-September scope
cut retains SIDESTEP and DIRECT and drops ARC/WAIT (`docs/PLAN.md:78`). Today is
24 September; this proposal supplies the bounded removal mechanism without
applying that future disposition or inferring physical acceptance.

All six opener implementations already exist. `Menu::cycle` currently visits
all six (`src/core/countdown.cpp:367`), and reset uses MODE_DEFAULT. Robot has
no caller-supplied mode field or public setter: legacy and explicit button
observations reach the same private Menu. The running mode is captured at the
accepted START release (`src/core/fsm_robot.cpp:317,364`), retained through the
hold, and dispatched at GO (`:517,542`). The existing P4 reactive profile skips
openers; this proposal does not change that profile.

## Configuration and public interface

Add only these two dimensionless availability switches to `src/config.h`:

```cpp
inline constexpr std::uint32_t MODE_ARC_ENABLED = 1U; // availability: 0 or 1
inline constexpr std::uint32_t MODE_WAIT_ENABLED = 1U; // availability: 0 or 1
```

Their names are an explicit units-name exception for boolean availability.
Both defaults remain 1U, MODE_DEFAULT remains 1U, and the existing B16 set of
76 values remains unchanged. ARC_R and ARC_L are enabled or disabled together;
WAIT is independent. No bitmask, build profile, runtime setter, persistent
setting, enum renumbering or new stored state is introduced.

Expose this small constexpr query immediately after Mode in `src/core/types.h`:

```cpp
constexpr bool modeAvailable(Mode mode);
```

It returns true for SIDESTEP_R=1, SIDESTEP_L=2 and DIRECT=3; for ARC_R=4 and
ARC_L=5 it returns MODE_ARC_ENABLED == 1U; for WAIT=6 it returns
MODE_WAIT_ENABLED == 1U. Every other enum value returns false. This is an
execution-availability query, not a historical mode-ID validator.

`types.h:6` already includes config.h, and config.h includes only `<cstdint>`
(`src/config.h:5`); config.h must not include types.h. Defining the query here
adds no include cycle or new header dependency. Put compile-time checks after
the enum/query: both switches must be <=1U; MODE_DEFAULT must be in 1..6 before
its conversion to Mode and the resulting mode must be available. Reject a
disabled default at compile time; do not silently replace it. The existing
countdown range assertion may remain. Source-literal validation below catches
large integer narrowing before these typed checks.

## Runtime admission and unchanged identities

- Match-menu short presses advance to the next available numeric ID, wrapping
  after 6, with at most six candidate probes. The four configurations cycle
  1,2,3,4,5,6; 1,2,3,6; 1,2,3,4,5; or 1,2,3. Mandatory 1..3 guarantee progress.
  Keep the original one-step branch when both switches are 1 if that avoids
  default-build overhead. Service order, gestures, debounce, duplicate-source
  handling, START routing, STOP, hold anchoring and release capture are unchanged.
- Menu construction/reset and Robot construction/reset retain MODE_DEFAULT.
  Selection remains read-only externally. Do not add an input selector or a test
  setter. Changing a switch requires rebuilding; there is no mid-attempt change.
- `Flank::start(..., Mode)` accepts only available SIDESTEP/ARC modes. A disabled
  ARC request must reset any old script, return false, and latch the existing
  INVALID exit/phase and zero INVALID motion until reset/restart, exactly like
  its current invalid-mode path (`src/core/openers.cpp:65`). DIRECT/WAIT remain
  invalid arguments to Flank. Its existing finite-heading checks still apply.
- `Wait::start(...)` must likewise reset and reject disabled WAIT with false,
  WaitPhase::INVALID, Exit::INVALID, zero INVALID motion and brake, using its
  existing invalid-start path (`src/core/openers.cpp:219`). No cue, phase or
  timeout pulse may create activity after rejection. Enabled WAIT retains
  D055's complete SIDESTEP_R; mandatory SIDESTEP is always available.
- At `Robot::startOpener`, after its existing cancellation, check availability
  before dispatch. A rejected mode must invoke no opener, leave it inactive,
  and use existing SCRIPT_START fault/final inhibition and zero-duty behavior.
  Do not substitute another strategy. Ordinary input cannot inject a disabled
  mode; direct public opener calls must still enforce their own admission.
- Keep Mode IDs 1..6, existing glyphs, event/frame values, CSV semantics and
  historical validators intact, even in reduced-mode builds. An unavailable
  optional ID remains a valid recorded/display identity. Do not replace those
  validators with modeAvailable. No new availability event or recorder field.
- No B7 primitive, IMU fallback, phase duration, mirror definition, opponent
  qualification, edge/governor/contact/stall ordering or motor authority changes.
  No runtime allocation, I/O, clock, added object storage or unbounded loop.

Update the public comments in countdown.h and openers.h to state these rules;
keep existing start/step signatures and layouts. Robot's public interface is
unchanged. The helper definition itself is available for independent tests.

## Raw staged admission and historical compatibility

Add `validate_mode_availability_config(path)` in tools/board_tool.py, returning
normally on acceptance and raising an identified ValueError on rejection.
Call it on the actual copied `staged_src/config.h` before further staging or
build/remote operations, alongside the unchanged D132 push-through validation.
Reuse the small lexical rules where practical; do not build a preprocessor.
Any shared-lexer adjustment must retain every adopted D132 acceptance/rejection.

Apply malformed-text, source-splice and digraph rejection before the legacy
both-absent return, including direct validator calls. After comment/quoted-literal
masking, count active occurrences of each switch
identifier before removing directives. If neither identifier occurs, accept
the config as pre-feature source. This is compatibility with historical source,
not inferred fallback definitions: new core code unconditionally requires both
symbols and therefore cannot compile without them. Existing exact source/hash
approvals still decide upload, including D133's immutable P0 fixtures. Add no
second historical hash allowlist or changed production approval.

If either identifier occurs, require exactly one occurrence of each, each as
an unconditional canonical `inline constexpr std::uint32_t` declaration whose
initializer is only `0U`, `0u`, `1U` or `1u`, followed by `;`. Require exactly
one corresponding MODE_DEFAULT declaration with canonical decimal 1..6 and
U/u suffix, and reject a default disabled by these values. Accept ordinary
spacing/comments between tokens. Reject extra references, duplicate/missing
partners, alternate types, signs, hex, leading zeroes, expressions, macros,
conditional declarations and oversized numeric tokens before integer conversion.
Do not evaluate conditional branches: even a declaration in `#if 0` is present
and unsupported, not an absent legacy switch. Comment/string lookalikes are
not declarations. Physical line splices (including CRLF and horizontal-space
extensions) and code-level `%:` directives remain rejected under D132 rules.
Read/copy/Unicode/malformed-literal failures remain identified errors, not raw
exceptions. Parsing checks raw source before any native integer narrowing.

Keep canonical-config copying, local-shadow rejection, existing compiler flags,
source hashing and upload guards unchanged. The two new defaults enter the
existing `test_p0_config.BEHAVIOR_EXTRA_DEFAULTS` dictionary as literal1
expectations under D134. Retain the B16 count76, D096_DEFAULTS, all existing
assertion bodies and the current wrapper chain. Add independent copied-config
rejection of each new shipped default drifting to0 or2; no extra wrapper.
Do not edit a locked test.

## P5.3 clarification: adopted D034 already controls the outcome

P5.3 currently says an abort hands over to ATTACK or DEFEND_TURN within one
tick (`docs/prompts/P5_openers.md:18`). D034 explicitly supersedes literal
ATTACK wording on all opener exits (`docs/BEHAVIOR.md:480`;
`state/DECISIONS.md:263`): the same observation requests normal current-
perception arbitration. Current front enters TRACK and must meet the existing
ATTACK_ENTER_TICKS consecutive centered observations before ATTACK; current
side/rear enters DEFEND_TURN, and no current target enters SEARCH. A countdown
snapshot alone never authorizes ATTACK.

Adopted P5.3 clarification: verify same-tick handover to that existing routing,
then the required centered qualification before ATTACK. Test phase-specific
abort conditions and existing precedence, including SIDESTEP/ARC PIVOT ignoring
front where specified. Do not create an immediate-ATTACK exemption. This is
alignment with an accepted decision, not a new combat policy. Physical 10/10
abort trials remain pending; host traces do not replace them.

## Independent regression contract before implementation execution

Freeze independently authored cases against these public interfaces and literal
expected values before first implementation execution. Required coverage:

1. All four switch combinations: complete Menu cycles, wrap, boot/reset default,
   service entry/cycle/return, and unchanged qualified MODE/START/STOP/hold rules.
   Defaults in enabled optional modes work; defaults selecting disabled ARC or
   WAIT fail compilation. IDs 0,7,255 are unavailable; 1..3 are always available.
2. Public Flank rejection of each disabled ARC mirror, including replacement of
   an already active mandatory script; subsequent calls stay INVALID/zero.
   Disabled WAIT rejects every start and stays INVALID/zero/brake without cue or
   motion. Enabled direct/flank/wait behavior and mirrors remain unchanged.
3. Actual Robot selection through legacy and explicit qualified buttons, mode
   capture at accepted release, retention through GO and reset. No disabled
   choice is reached. Verify P4 reactive and P3 service profiles keep their
   existing behavior. Review the internal dispatch guard without adding a
   production injection API solely to reach an otherwise impossible state.
4. Actual Robot D034 front abort -> TRACK -> qualified ATTACK, side/rear ->
   DEFEND_TURN, stale snapshot/no current target -> SEARCH; include same-tick
   edge/STOP precedence, no fabricated contact and unchanged governor limits.
   Retain enabled WAIT's D055 cue and complete SIDESTEP behavior.
5. Historical IDs 1..6 still display and round-trip through existing log/event
   validators under each reduced configuration. Default all-six legacy tests,
   original protected tests, and existing config defaults remain unchanged.
6. Direct validator and real stage-path cases for all four accepted pairs,
   lowercase suffix/formatting, all invalid forms above, overflow-width values,
   malformed Unicode/read failures and line-splice/digraph/comment/string cases.
   Test both-absent legacy acceptance, one-absent rejection, and compile failure
   of new core with both symbols absent. Exact D133 historical fixtures continue
   working with current tooling and unchanged approval/assertion data.
7. Independent source review checks bounded probes, public direct-entry checks,
   unchanged object layouts, no default behavioral drift and no new authority.
   Run appropriate normal/sanitizer configured and default host regressions,
   existing tooling admission regressions and config-registry checks after
   freeze. Check target fit through the established compile-only path; do not
   infer target RAM/timing improvement from disabling entries or host results.

The bounded implementation scope is config.h, core/types.h,
core/countdown.{h,cpp}, core/openers.{h,cpp}, core/fsm_robot.cpp and
tools/board_tool.py, with additive independent tests and matching B13/P5 wording.
It does not request a second framework, strategy, physical run or phase gate.
Root serializes shared interfaces/config/build/state; implementation, independent
spec/header-derived tests and read-only review have separate file owners.
