# D134 first host build failure

The first default11 full build configured successfully but stopped with compiler
exit2 at the new fixture's reset assignment. No CTest or private C++ case ran;
the completed compilation of earlier targets is not a test pass. Original source
expectations, manifests and full diagnostic are retained in425c8a97 and
`P5_mode_availability_raw/default11.{json,txt}`. Owned scratch was released after
recording the failure.

At `tests/fixtures/mode_availability_fixture.h:109`, `last = {};` did not convert
to `fsm::RobotResult` for its ordinary implicit copy/move assignment under g++13.3.
The independent author and reviewer separately inspected the public aggregate
and diagnostic. Both approved only `last = fsm::RobotResult{};`, giving the same
default reset request an explicit operand type. It retains declared enum/default
members and zero/false values. No production change, input timeline, assertion,
case or locked source was changed.

`fixture_correction.json` binds originala09d2abf and corrected9dfa39cd. Both frozen
manifests were updated only for that fixture; originals remain in425c8a97. The
strict C++17/no-exceptions syntax probe of both new test files passes, exit0,
with exact argv in `syntax_retry1.json` and empty diagnostic text. This proves
compilation of the corrected fixture, not its behavioral assertions.

The focused M0/M1 build then compiled successfully. Each binary passed19/20
cases; the only failing case was the new, unaccepted edge-preemption draft.
It incorrectly required every white mask to produce zero duty. Existing B4
instead commands forward escape for4/8/12 and pivots for5/10. Brake masks are
1/2/3/6/9;7/11/13/14/15 latch the approved inhibited fault. First-observation
EDGE_ESCAPE, mask and contact assertions passed. Full receipts, including all
failures, remain in `default11_focused.{json,txt}` and its LastTest log. CTest
returned8; private C++ execution did not occur after that failure.

Independent author and reviewer agreed on the literal B4 row correction before
another execution. D134 records the correction of this invented draft oracle;
the original remains in425c8a97 and was never accepted as established coverage.
Preserve the first-observation checks, use exact zero for brake/fault, check
moving signs/caps and B6 reversal/slew, and verify exact settled vectors with
actual M1 PWM/receipt and M0 inhibition. No production or prior41 protected
source changes are authorized by this correction. Execute focused tests after
the replacement is independently reviewed and bound, then the wider matrix.

Tooling admission passed60methods (26new,32prior push-literal,2registry), and
private Python passed8/8 on unchanged production500ce3c5. These do not imply
board compilation, upload or physical acceptance.
