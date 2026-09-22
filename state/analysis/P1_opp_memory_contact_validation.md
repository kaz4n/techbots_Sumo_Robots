# Bearing memory and contact validation - 2026-09-22

P1 host-only. Contracts/accepted D-026/27/28: 290c13b; implementation: c578911.
Worker owned only opp_fusion.cpp and preserved existing frontView/Debouncer.
Independent author owned only new tests/report and read no implementation.cpp.

Commands and actual results:

- WSL g++ C++17 isolated object compile with -Wall -Wextra -Wpedantic,
  -Wconversion -Wsign-conversion -Werror -fno-exceptions -fno-rtti: exit 0.
- `wsl -d Ubuntu -- bash tools/test_host.sh`, then direct host binary: exit 0,
  **212 cases / 6,089,047 assertions**, zero failures/skips. Raw receipt:
  P1_opp_memory_contact_tests.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, then its
  direct binary: build/run exit 0, same 212 cases/6,089,047 assertions; no
  ASan/UBSan diagnostics. Receipt: P1_opp_memory_contact_sanitizer.txt.
- After independent complete-source/hash review, refresh manifest and run
  `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v`:
  **48/48**, exit 0. Receipt: P1_opp_memory_contact_tools.txt. Controlled command
  substitutes only, including compile-only/match and inert source guards.
- `git diff --check`: exit 0. No existing locked test changed.

Thirty new cases cover all 128 masks with/without history, group priority,
conflicts, rising-side memory/ties/clock wrap, world-angle extremes/invalid data,
exact contact counts and pattern resets, Euclidean impact boundaries, all 256
state bytes, target/centering/state loss, re-entry, and low-voltage governor
eligibility. A fixed-seed 10,000-observation mirror test adds finite/bounded
angle and contact evidence. This is not the full Robot R1/R5 property proof.

Separate read-only scoped review PASS, no open findings:
reviews/P1_opp_memory_contact_codex.md. Same reviewer context as earlier scoped
reviews; not cross-model or a fresh full P1 gate. Inert hashes bind only this
17-file-per-sketch snapshot and remain subject to change review.

No target compile, hardware operation or physical measurement. Phantom/stuck,
remaining scripts/stall/FSM and full target-loss braking still need integration.
D-028 explicitly resolves overflow policy; no recorder buffer is implemented.
All prior approvals remain valid within scope. Next: B5.5/B5.6 contracts/tests.
