# Full Escape, WAIT and contact preview — 2026-09-23 Asia/Dubai

P1 host work under D-016. Contracts were committed before source/test work:
5360c80/65b1635 (Escape/D-054),032eedb (WAIT/D-055),c39c8e7 (preview/D-056).
Base93489fe contains the earlier bare-board evidence, not these new components.

## Scope and independence

- edge.cpp: full selection/pushed-out/replanning wrapper, reset-only inhibition,
  fresh inward-exit evidence and relative-turn precision repair. Worker owned
  this file only. Independent author owns42 new locked Escape cases.
- openers.cpp: stationary WAIT, bounded ordered FC/flank cue, full SIDESTEP_R
  delegation and relative-turn precision repair. Coordinator implemented it;
  a separate spec/header-only author owns the new WAIT cases.
- opp_fusion.cpp: const contact candidate preview, preserving one final commit.
  Coordinator implemented it; a fresh independent context owns16 new cases.

Test authors read specifications/public headers, not implementation cpp.
The reused separate read-only Codex reviewer inspects source, tests and evidence;
this is neither cross-model review nor a fresh/full phase-gate review. See
../reviews/P1_escape_wait_codex.md and the three *_test_author.md reports.

## Preparation and findings

Strict g++ C++17 syntax-only compilation of edge/openers/opp_fusion passed exit0
with -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti and -Isrc.
git diff --check passed. No established locked test or config.h value changed.

Pre-build review caught34 unsupported REQUIRE calls in the new contact-preview
test file. Its author replaced them with CHECK, preserving every predicate.
None gates unsafe resource/index access; no early-return guard was necessary.
The project's exception-free policy/framework stayed unchanged. This was a
static compatibility finding, not a failed runtime test or weakened expectation.

## Actual validation

| Command / check | Result | Raw receipt |
|---|---|---|
| `wsl -d Ubuntu -- bash tools/test_host.sh` | Build/CTest exit0;1/1 registered executable passes | P1_escape_wait_host_20260923.txt |
| `wsl -d Ubuntu -- build/host/sumox26_tests` |716 cases/12,121,189 assertions pass;0 failed/0 skipped;exit0 | Same host receipt |
| `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, then sanitizer executable |716 cases/12,121,189 assertions pass;0 failed/0 skipped;both exit0 | P1_escape_wait_sanitize_20260923.txt |
| `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` |116 tests pass in39.233s;exit0 | P1_escape_wait_tooling_20260923.txt |

Sanitizer cache uses `-fsanitize=address,undefined -fno-omit-frame-pointer` and
matching sanitizer linker flags. Tests add42 Escape +33 WAIT +16 preview cases
to the previous625. There were no runtime failures or implementation repairs.
The static unsupported-macro finding above is retained rather than hidden.

The separate reviewer independently recomputed both exact23-file maps, compared
all staged bytes to current source, and approved the aggregate hashes explicitly.
Only then was tools/p0_inert_sources.json refreshed. Proposed/approved snapshot:
P1_escape_wait_inert_proposed.json. Six core files differ from93489fe; seventeen
staged files are unchanged. The full tooling suite passed after that refresh.
This approval concerns source inertness, not actual execution or a phase gate.

Actual target command:
`python tools/board_tool.py flash bench/p0_timing --compile-only`.
SUMO_TRANSPORT=adb, SUMO_ADB_SERIAL=2629958581, installed ADB32.0.0 executable,
SUMO_REMOTE_ROOT=/home/arduino/sumox26-build. Script verified pinned core1.0.0
before compiling arduino:zephyr:unoq on the board with its installed CLI1.5.1.
Result: TARGET-COMPILED, exit0; MATCH0/MOTORS_ALLOWED0/default startup;
source98c436a4a3debc5244d865dfc3ddd6cb46b96e2062bd29827e25766af98eb324.
The linker reports74,008 bytes program and33,964 bytes globals for this inert
sketch, not complete Robot resource usage. Raw command/output/timestamps:
P1_escape_wait_target_compile_20260923.txt. Compile-only issued no upload.

Separate reviewer independently reran the host script and released binary:
716 cases/12,121,189 assertions pass, exit0. Receipt:
P1_escape_wait_reviewer_host_20260923.txt. Review contains the scoped verdict and
retains the corrected macro finding; no full phase-gate acceptance is inferred.

Local implementation commits:66f76e4 Escape,6938c63 WAIT,990f287 contact preview.
No publication or tag. The validation/checkpoint commit follows these artifacts.

## Limits and next work

An explicit USB check returned device2629958581 and16847104KiB available in the
dedicated board build directory. The compile-only command built the new core
inside the existing inert timing sketch; no upload/reset/start command is issued.
The previously uploaded matrix image and its dated evidence remain unchanged.
The real app.ino and complete Robot do not yet exist. Host tests cannot establish QTR acquisition,
physical evasion, real MotorGate writes, target WCET, external wiring or a gate.
Complete Robot/state/history/event/UI integration is still unfinished. The next
contract uses P1_robot_interface_audit.md and the new B13 mode/menu audit; preserve
fresh observations, one final contact commit and one Governor step per tick.
