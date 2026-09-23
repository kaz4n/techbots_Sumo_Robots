# Explicit-library control correction

2026-09-23 Asia/Dubai. Initial experiment e6e7e84e7b5a4eeda78c094829685d45
preserves both actual compiler outputs, source/hash receipts and process exits.
The fixed0 branch passed (6172B program,208B memory), discovered SumoPolicyFixture
1.0.0 and reached the policy's explicit external-library rejection. The forced
literal1 branch exited1: analogReference.cpp could not include
Arduino_RouterBridge.h. Its discovery list contains the fixture and six Bridge
dependencies, but an unsuccessful compiler envelope is not accepted evidence.

The runner mistakenly forced discovery1 during normal compilation too. Pinned
installed platform.txt:108-111 uses the template
`-DARDUINO_LIBRARY_DISCOVERY_PHASE={build.library_discovery_phase}`; lines132/135
use it in normal C/C++ recipes. Pinned CLI preprocessor/gcc.go:38 temporarily sets
build.library_discovery_phase=1 for discovery; normal ResolveFQBN sets0 at
package_manager.go:386. The cached platform specification:143 independently
documents this distinction. All cited files are in P2_bridge_dependency_raw.

Correction: the control uses that exact stock template, changing only the
experiment command. Source fixture, pinned tools, explicit library root,
acceptance envelope, exact source hashes and library rejection remain unchanged.
Run only the corrected ordinary-control branch in a fresh isolated directory;
reuse the already successful fixed0 evidence without repeating its target build.
No production/locked test/installed package change, no upload or MCU action.
This corrects the experiment's control; it does not weaken its acceptance test.
