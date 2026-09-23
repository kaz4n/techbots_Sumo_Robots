# D088 independent author test handoff

Objective: derive renderer, actual Robot mapping and actual native adapter tests
from the frozen D088 contract/public interfaces; preserve failures and hardware
qualification boundaries. Production implementation CPP was not read to choose
expectations. Native source bytes were hashed and compiled opaquely.

Owned files: tests/test_ui_display.cpp, tests/tooling/test_ui_matrix_native.py,
tests/fixtures/ui_matrix_native/**, and this author evidence directory. No prior
test, locked test, source/header/config/build file or hardware path was changed.

Final results:
- Renderer and actual Robot mapping:15cases,1521100assertions PASS in the normal
  root build. Exact evidence display_focused_final.txt; test unit rebuild command
  output display_build_02.txt and strict syntax display_syntax_final.txt.
- Native adapter:15Python methods,866successful isolated native process scenarios
  across normal and ASan+UBSan variants.866 counts both variants together.
- Capture wrapper:8pure Python methods PASS; no board API/helper execution.
- Combined tooling23methods PASS8.275s: native_and_capture_final.txt. Native
  compilation and every subprocess have separate JSON receipts and source hashes.
- All new test/fixture files use LF. Exact hashes final_test_manifest.json.

Coverage: all6modes/normal states, BOOT/STOPPED/DRIVE_TEST, all service displays,
8192sensor-view combinations, all127fault masks with page boundaries, exact
countdown seconds/margin/future/wrap cases, threshold-adjacent battery floats,
unknown payload rules, enum/mask/battery rejects, full104byte overwrite and guard
bytes. Actual Robot exercises preGO validated/missing/malformed/explicit/retained
IMU, real countdown anchor, real four-service menu and fresh-result availability.
Native tests exercise constructor/destructor silence, exclusive lifetime ownership,
failed/repeated begin, null/not-ready device, CONTROL/IPSR rejection and privileged
CONTROL2 acceptance, every104byte invalid location before/during throttle, first
submit/exact40000us/wrap/no catch-up, initial blank and exact PRIMASK restoration.
Capture fixtures exercise40byte little-endian telemetry identity/status/all12scenes,
uint32 modular advance, bounded reads/deadline, unique hashed initial dump, and
extension identity-field consistency.

Preserved failures and corrections:
- display_syntax_01.txt: unsupported two-argument CAPTURE, class-memaccess warning,
  enum/integer conditional warning. Corrected in this new test only; syntax02pass.
- Root initial host run used the first invalid-frame expectation with right E.
  D088 did not explicitly specify that region; root clarified right region blank.
  New fixture follows that explicit clarification, without production change.
- display_focused_01.txt: one new retained-IMU fixture incorrectly used20ms silence
  as source-age limit. D084 contract lines32-50 and public config explicitly set
  inclusive2000us. Changed only new timestamps21000/21001 to3000/3001 against the
 1000us source; final15cases pass. Reviewer independently observed same mismatch.

Limitations: these are host software checks with controlled native symbols. No
physical sensors, GPIO, matrix output, board upload, optical check, native clock,
IRQ timing, full tick WCET, phase gate or motor authorization follows. Root and
separate reviewer own final whole-suite sanitizer/target/runtime closure. The
capture test freezes the wrapper hash used; target metadata may be repinned only
by the owner with its separate evidence. Next action: root/reviewer final checks
on frozen test files and exact target source identity.
