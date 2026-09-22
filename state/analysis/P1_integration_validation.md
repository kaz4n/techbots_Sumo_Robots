# Approved countdown/edge integration validation — 2026-09-22

Authority: D-019 (after-debounce hold) and D-020 (persistent/all-white edge guard).
Development remains P1 host-only under D-016. No board is connected.

Implementation: `countdown::Controller` updates logical Buttons before Gate and
anchors the full hold to completed release qualification. `edge::Guard` requires
escape for persistent white after permission and latches all-white inhibition
until reset; ordinary escape clears only with black plus script completion.
These are pure components; the full Robot FSM and MotorGate do not yet exist.

| Command / check | Observed result | Evidence |
|---|---|---|
| `wsl -d Ubuntu -- g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -Wconversion -fno-exceptions -fno-rtti -fsyntax-only src/core/countdown.cpp src/core/edge.cpp` | exit 0 | coordinator strict syntax check |
| `wsl -d Ubuntu -- bash tools/test_host.sh` (fresh reviewer) | exit 0; CTest 1/1; 97 cases, 5,214,158 assertions, all pass; no skips | P1_integration_core_tests.txt |
| `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2` | exit 0; existing ASan/UBSan configuration rebuilt new sources/tests | sanitizer build |
| `wsl -d Ubuntu -- ctest --test-dir build/host-sanitize --output-on-failure` | exit 0; same 97 cases/assertions; no diagnostics | P1_integration_sanitizer_tests.txt |
| `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` | exit 0; 46/46 pass in 14.817 s | P1_integration_tool_tests.txt |
| `git diff --exit-code dd81fd3 -- tests/locked/test_countdown.cpp tests/locked/test_edge_classifier.cpp` | exit 0; existing locked files byte-unchanged | locked-test preservation |
| `git diff --check` | exit 0 | source and evidence whitespace check |

New independent tests: 10 Controller cases plus 10 Guard/composition cases. The
Controller property adds 10,000 streams with seed `0xD0195100`; all 16 line masks
are tested through a test-owned 1 kHz Controller -> Guard -> Governor sequence.
The author read specs/headers, never implementation `.cpp`. See
P1_integration_test_author.md. No failed behavior assertion or weakened test.

Fresh separate-context read-only reviewer `/root/p1_integration_review`: scoped
PASS, no BLOCKER/MAJOR/MINOR; this is not cross-model or a full phase-gate review.
Its exact 13-file inert snapshot review approved refreshed hashes before the
manifest edit. Coordinator local staging/hash calculation matched both:

- matrix: `6f97c7466d8a01766d4640552aafd6bf897314bbc3a77c7c6028aac92e251a8a`
- timing: `088009162cc2a4bcc60c1bc7d92097751ef32bd71ae7b49958be8e59eeca64b2`

No transport was invoked for hashing. Compile-only/upload guards are unchanged;
F-061's Immediate matrix restriction remains. No config/default/pin change.

Status: IMPLEMENTED / HOST-TESTED / scoped REVIEW PASS. Full B3 services, escape
motion/replanning, positive push-through, complete Robot/app/HAL integration,
target compilation, physical timing and human phase gates remain pending.
The motion-veto test uses a logical request's inhibit flag; it is not an observed
motor EN/PWM write or physical R1/R5 proof. No upload, reset or motor run occurred.
