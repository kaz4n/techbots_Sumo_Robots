# Next-phase software map: P5

Read-only mapping on2026-09-24, while P4 validation finishes. This is not a
phase advance, implemented change or human gate.

Existing `src/core/openers.cpp` implements DIRECT, SIDESTEP mirrors, ARC mirrors
and WAIT. Actual Robot capture/dispatch and tests already exist; running mode is
captured at accepted START release, before GO (`fsm_robot.cpp:313,364,517,542,579`).
Legacy and explicit buttons both reach the same private Menu; RobotInput has no
mode selector. Mode identities remain1..6 (`types.h:13`). Six-mode display and
recording preserve those identities independently of physical qualification.

The real software gap is optional-mode removal: `countdown.cpp:367` always
cycles all six. P5 requires unaccepted optional ARC/WAIT removed from the mode
list, and PLAN's end28September scope cut can require that removal. Next bounded
task should provide configurable availability, retaining all six default choices
until an actual scope/acceptance disposition changes them. Mandatory SIDESTEP
mirrors and DIRECT stay available; preserve IDs and historical log readability.

Suggested contract points, not adopted yet:

- Availability in config.h; mandatory IDs1..3 and enabled MODE_DEFAULT required.
  Prefer ARC mirrors enabled/disabled together; WAIT separately. Bound raw config
  admission explicitly rather than relying on a narrowing conversion.
- Menu skips unavailable entries with at most six probes; service cycling,
  debounce, START/STOP and captured mode remain unchanged. No runtime storage.
- Public `Flank::start(mode)` and `Wait::start()` must reject a disabled strategy
  with their existing false/INVALID/zero behavior. A Robot dispatch check can use
  existing SCRIPT_START inhibition; no silent substitute strategy.
- Keep UI, frame/event validators and CSV semantics accepting historical IDs1..6.
  Add config registry coverage without changing B16's76 existing defaults or
  established locked tests.
- Clarify P5.3's ATTACK-or-DEFEND wording against approved D034: a front abort
  enters TRACK immediately and needs the existing centered observations before
  ATTACK. Test actual same-tick handover and subsequent qualification, not an
  invented direct ATTACK exemption.

Source map from the implementation context, with no edits or executions:
`countdown.h:245`, `countdown.cpp:367,482,484`, `fsm_buttons.cpp:60`,
`openers.cpp:64,219`, `ui_display.cpp:71,196`, `logframe.cpp:56,227`,
`recorder.cpp:71`, `test_p0_config.py:168,175` and the additive
`test_runtime_config_registry.py:52` pattern. Relevant existing tests include
`test_robot.cpp:182,200,217,429` and `test_ui_display.cpp:79`.

Static-box/charger success,10-degree physical mirror accuracy and operator
selection/readability remain physical trials. No P6 polish begins without its
actual gate-date eligibility. Keep the user-authorized hardware-at-end software
scheduling distinct from real P0-P5 acceptance.
