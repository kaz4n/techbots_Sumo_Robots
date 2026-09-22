# Ordered opponent fusion — 2026-09-22

Initial status: IMPLEMENTED; the final actual results are recorded below.
P1 host development under D-016; no new protected policy decision. Contracts
committed first30b16d5. Root owns public interfaces/state; worker owns only
opp_fusion.cpp; separate author owns only new test_opp_pipeline.cpp/report.

Flow: electrical debounce -> unsuppressed stuck qualification/removal -> one
contact-cue observation -> phantom filtering with pre-arbitration state/edge ->
effective bearing/memory. Caller selects the final state, then commits the same
cue/effective mask once. Legacy Contact::step composes both split methods and
retains its existing contract. Invalid/unavailable yaw never becomes fresh world
bearing; relative perception remains available. No new config/pin/HAL changes.

Public protocol handles duplicate timestamp observation without re-counting or
replaying event pulses. Commitment consumes the observation; missing/repeated
commit is invalid zero and clears contact. Replacing an uncommitted observation
clears its old latch. These checks are software protocol defenses, not proof that
the physical inputs were freshly sampled. No state selection or motor permission
is granted by this component.

Worker strict C++17 syntax check: reported exit0 with -Wall/-Wextra/-Wpedantic/
-Werror/-Wconversion and no exceptions/RTTI. Root diff inspection found only
the planned Contact split/Fusion composition and internal finite-evidence guard.
Normal/sanitizer/script results and final review will be recorded below.

Review arrangement: a new reviewer spawn and revival of the prior scoped reviewer
were rejected by the collaboration tool's agent thread limit. The existing
p1_next_task_audit explorer was reused as a separate read-only reviewer. It has
not authored source/tests. Label this reused independent context accurately; it
is not a newly fresh context, cross-model review or a full phase-gate review.
Contract/pre-test source inspection reports no BLOCKER/MAJOR; final verdict pending.

Coordinator validation completed:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1,
  P1_pipeline_build.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit0,
  P1_pipeline_sanitizer_build.txt.
- `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0,
  **444 cases / 10,442,964 assertions**, zero failures/skips and no ASan/UBSan
  diagnostics, P1_pipeline_sanitizer.txt.
-25 new independent pipeline cases; all existing Contact/component/locked tests
  unchanged and passing. Includes all128 masks and10000 mirrored observations
  with explicit mask coverage checks, exact contact sample counts, duplicate/
  missing commitment, filter ordering, history/reset/wrap and governor composition.
No failed production test or repeated repair attempt occurred in this batch.

Final reused separate read-only review PASS, no open finding; independent full
host run agrees444 cases/10,442,964 assertions. Report ../reviews/P1_pipeline_codex.md
records actual context limitation and exact approved23-file hashes. After their
manifest refresh, `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling
-v` passed48/48, exit0, P1_pipeline_tools.txt. This is controlled script evidence,
not a board build. All76 B16 defaults, existing locked tests and hardware remain
unchanged. No target compile/upload/reset/motor run, measurement or human gate.

Implementation commit a54f177; public interface30b16d5. Next unblocked P1 work is
the fully specified B4.2 row subset described in P1_escape_row_contract_audit.md;
full Escape selection/replanning and Robot remain separate unfinished requirements.
