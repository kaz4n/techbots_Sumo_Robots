<!-- Reviews the D138 informational readiness proposal against actual owners. -->
<!-- Prevents display metadata from overstating button arming or motor permission. -->
<!-- Read-only source and specification inspection; no build or hardware execution. -->
# D138 readiness contract design review

2026-09-24 Asia/Dubai. Separate reused-context, same-model design review; not a
fresh phase-gate review or physical acceptance. Initial proposal SHA-256:
`ef36ca16c9e8a0d90bd1841af51f8f1628323300df914aed64afba6f0c996a1e`.

**Final verdict: PASS for adoption of the revised design; no open findings.**
Revised proposal SHA-256:
`568bc27719e32d397dfcfe7130558e952b53f0f651430a89c6b8d6a66b00904a`.

## Initial findings, resolved before adoption

- **MAJOR:** `state/analysis/P7_readiness_contract.md:46–61` combines actual
  `allow_start` with D087's `start_ready` but calls the result a qualified neutral
  point where START is available. These are distinct from current button arming.
  `src/core/fsm_buttons.cpp:48–58,83–87` keeps initial neutral qualification armed
  until restart/fault. In contrast, `src/core/countdown.cpp:43–77` disarms actual
  START on qualified MODE/BOTH and rearms only after a qualified NONE transition.
  After leaving services with a long MODE hold, the first fresh NONE observation
  can meet the proposed predicate while the controller still has stable MODE and
  is unarmed. An immediate START then need not generate an accepted release.
  Before test freeze, either explicitly define route-only informational status
  without claiming current qualified START readiness, or observe the existing
  controller's actual neutral/armed state through read-only accessors. Do not
  add another debounce machine or alter accepted control behavior. Also define
  whether the stated one-step menu-transition suppression includes short mode
  cycling as well as service toggles.
- **MINOR:** `state/analysis/P7_readiness_contract.md:95,108–110` says M0 cannot
  display READY, but the exact pure-renderer rule has no M0 condition. Specify
  whether this is an actual Runtime guarantee or a renderer compile-time rule.
  Recommended minimal interpretation: Runtime M0 always supplies false;
  independently supplied pure DisplaySample values still follow the exact pixel
  rule. The test author must not have to guess between these interpretations.

## Design otherwise supported

The existing post-application projection is inside the current DECIDED
transaction before C (`runtime.cpp:344–346`, `runtime_inputs.cpp:display`,
`transaction.cpp:89–110`). Existing receipt/inhibited-IDLE predicates and the
already observed clock can qualify a current snapshot without another clock call,
control gate, timestamp refresh or hardware owner. The proposal correctly does
not call it completed timing or measured electrical inhibition.

Row 6 column 12 is unused in ordinary match-mode views; the R region is the
existing right-side fault-glyph region. Restricting the extension to bound IDLE
match views and drawing R only with zero faults preserves mode, battery-bar,
service/calibration and fault priority. Default-false sample fields preserve
the established complete-frame tests in `tests/test_ui_display.cpp`,
`tests/test_display_channels.cpp` and `tests/test_qtr_cal_display.cpp` without
rewriting their expectations. Float equality/adjacency, invalid input and blink
wrap expectations are explicit and finite.

The terminal-frame limitation is honestly stated: a last R can remain physically
visible after a later failure; no new fault-path submission or throttle bypass is
promised. A live-blink procedure still needs optical/timing qualification and
does not authorize motors. The native normal-startup/exclusive-owner requirement
in `ui_matrix_unoq.h` and MATCH Immediate deployment requirement remain expressly
unresolved. Empty grants, physical button/battery qualification, rearming,
transport and SC-AP are not inferred from this host-implementable feature.

Appending metadata can change object layouts, so the required new layout account
and source-bound target compilation are appropriate; the prior 1584-byte span
cannot prove fit. No implementation, test, header, build configuration, ledger,
board or network action was performed for this review.

## Resolution and final disposition

The coordinator revised the proposal before adoption or independent oracle freeze:

- Lines 27–32 define observational `neutralStartArmed()` accessors on the actual
  Buttons owner, forwarded by Controller/Lifecycle. The predicate includes existing
  initialized, armed, unpressed, stable-NONE and candidate-NONE state. Lines 53–57
  require that real post-step observation as well as actual allow_start and D087
  qualification. This resolves the MAJOR without adding debounce state or changing
  motion behavior. Implementation ownership now includes countdown.cpp.
- Lines 68–71 explicitly suppress every current selection change or menu toggle,
  including a short match-mode cycle. Both service transitions and ordinary
  selection have an actionable one-step rule.
- Lines 105–107 explicitly put M0 inhibition in Runtime and keep the pure renderer
  configuration-independent, resolving the MINOR test-oracle ambiguity.
- Lines 168–175 distinguish actual representable integer ADC values straddling
  the voltage threshold from exact float equality/adjacency in pure renderer tests.
  This preserves the real input owner's raw-to-voltage relation.

**PASS — revised contract is actionable and minimally scoped.** No open BLOCKER,
MAJOR or MINOR remains. This approves the design for independent tests and
implementation, not completed software, a native working display, physical
readiness, deployment, motor authorization or a human phase gate. Only this
review file was written; no compiler or tests were executed.
