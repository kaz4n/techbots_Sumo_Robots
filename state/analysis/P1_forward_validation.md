# D-021 forward demand validation — 2026-09-22

Human approval: "Approve A: reuse 0.80", recorded in D-021. P1 host work only;
hardware remains disconnected and no phase gate has passed.

Implemented `edge::forwardDemand` for straight/left/right bias and the governor's
EDGE_FORWARD cap profile. Base/final cap use unchanged EDGE_BACK_DUTY=0.80.
EDGE_FWD_INNER_RATIO=0.70 centralizes the already specified B4 request ratio;
all 76 B16 values remain unchanged. Unknown bias values return invalid zeros.

Commands and results (WSL Ubuntu, GNU C++ 13.3.0, doctest 2.4.12):
- Strict C++17 syntax compile of edge.cpp/governor.cpp with `-Wall -Wextra
  -Wpedantic -Werror -Wconversion -fno-exceptions -fno-rtti -fsyntax-only`: exit 0.
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit 0, CTest 1/1; **106 cases,
  5,220,784 assertions**, all pass, none skipped. P1_forward_core_tests.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit 0;
  all changed core sources and affected tests compiled/linked. Make emitted an
  8.6 ms Windows/WSL Makefile timestamp warning; the resulting executable includes
  the new cases. No source or predicate was changed to hide a failure.
- `wsl -d Ubuntu -- ctest --test-dir build/host-sanitize --output-on-failure`:
  exit 0, same **106 cases / 5,220,784 assertions**, no sanitizer diagnostics.
  P1_forward_sanitizer_tests.txt. Build flags remain ASan+UBSan from P1_validation.
- `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v`: exit 0,
  **47/47** in 15.307 s. P1_forward_tool_tests.txt. This uses controlled substitutes
  and is not target-build evidence.
- Local stage/source-hash calculation matched the independently reviewed hashes;
  no transport was invoked. Current manifest binds all 13 files per inert sketch.
- Existing locked files have no diff; new tests are a separate unlocked D-021
  file. `git diff --check`: exit 0.

Nine new independent cases cover the three requested demands, mirror symmetry,
253 invalid enum values, 9/11.1/12.6 V, cap independence from contact, slew,
brake/zero/inhibit/reversal, cap reductions and all-white guard inhibition. The
author read specs and headers, never implementation `.cpp`; see
P1_forward_test_author.md. There were no behavioral test failures.

Per-side compensation/saturation and slew can change the final wheel ratio. At
9 V, a settled `(0.56, 0.80)` request produces about `(0.69067, 0.80)`, not a
measured trajectory. This is explicitly documented and tested; it is not a new
ratio-preserving governor policy. Timed motion/heading hold and full escape/FSM
integration remain pending, as do target compilation, MotorGate and hardware proof.

Reviewed current hashes:
- matrix: `3666582d873075f87bbbccdac685bf525d45752ca6b1141c600ff37e3b184869`
- timing: `62c6ba59a931ab55bf866b2a7e75a25eacf7ed69c029020855d17044fb7211b4`

See reviews/P1_forward_codex.md for the separate review scope and limitations.
No board contact, upload, reset, motor run, measurement or gate approval occurred.
