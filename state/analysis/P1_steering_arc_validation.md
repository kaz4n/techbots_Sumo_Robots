# Approved front steering and time-only arc — 2026-09-22

P1 host-only under D-016. D-036 defines front steering; D-037 defines time-only
re-flank arc defaults. Interfaces committed first in d6bdff3. Root owns fsm.cpp,
bounded worker owns only motion.cpp. Two independent authors read specs/public
headers, never implementation.cpp:17 front-row cases and19 TimedArc cases.

The request helper uses the current B5 front row, approved discrete pivot addition
and bounded ATTACK correction, explicit governor profiles and invalid-zero output.
TimedArc has no yaw target/input: it validates fixed inputs and completes by
caller-supplied elapsed time only. No config/default/pin changes; every existing
locked blob unchanged from dc42029. These helpers do not supply Robot transitions,
centered-count qualification, fresh contact lifetime or complete re-flank behavior.

Commands/results:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1;
  P1_steering_arc_build.txt.
- Separate reviewer independently ran the same script and host binary: exit0,
  **419 cases / 10,226,416 assertions**, zero failures/skips.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, then
  `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: both exit0, same419 cases
  and10,226,416 assertions, no ASan/UBSan diagnostics. Raw receipts:
  P1_steering_arc_sanitizer_build.txt and P1_steering_arc_sanitizer.txt.
- Strict g++ C++17 syntax checks for both changed production files: exit0,
  -Wall/-Wextra/-Wpedantic/-Werror/-Wconversion, no exceptions/RTTI.
- Tool versions reconfirmed: WSL Ubuntu g++13.3.0, CMake3.28.3, Python3.12.3.

Fresh separate scoped reviewer found one pre-build MAJOR: four REQUIRE predicates
in the new unlocked author file conflict with DOCTEST_CONFIG_NO_EXCEPTIONS. Author
changed only their macro to CHECK, retaining expressions/all subsequent checks.
No host flag or established test changed. First full build then passed; no repeated
failed repair attempts. Review verdict PASS, no open findings; full report at
../reviews/P1_steering_timed_arc_codex.md. Not cross-model or a full P1 gate.

Reviewer reconstructed both exact23-file inert trees and approved only the exact
source-manifest refresh. New scripts test receipt follows that refresh. Hardware,
target compilation, MotorGate writes, timing budget, PINMAP/EXPLAINED/human gates
remain pending. SC-Y/Z/AA/AB questions remain pending; other safe work may proceed.

After approved manifest refresh: `wsl -d Ubuntu -- python3 -m unittest discover
-s tests/tooling -v` passed48/48, exit0; P1_steering_arc_tools.txt. This is script
testing with controlled substitutes, not a successful target compile/upload.

Implementation commits:3f29fae (frontDemand),6e91778 (TimedArc), interfaces d6bdff3.
