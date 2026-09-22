# B13 logical menu validation — 2026-09-23 Asia/Dubai

Public contract3563a8f and D-058 preceded implementation and independent tests.
Worker owned countdown.cpp only; root owned interface/config/spec/ledgers. Frozen
source SHA25634558f66b118c8298c0138d62ba4b98437864007935c08fcd9969507c3f1761b.
Independent author owns new component and locked Lifecycle-composition tests,
using specifications and headers only, never implementation cpp. Separate reused
read-only review: ../reviews/P1_menu_codex.md; not a full phase gate.

Menu implements logical selection/intents with fixed storage and bounded work,
qualification-time duration anchors, release-before-long priority and explicit
rearming. Largest new function29 lines. Its source passed strict C++17 syntax-only
compilation with Werror/noexceptions/nortti and diff-check. Existing countdown
component bodies remain unchanged. MODE_SHORT_MS=600 only centralizes B13 text;
original B16 defaults are unchanged and TUNING_LOG distinguishes this from tuning.

Normal and ASan/UBSan runs both PASS776 cases/12,231,614 assertions, no failure
or skip, exit0. Commands and raw outputs: P1_menu_host_20260923.txt and
P1_menu_sanitize_20260923.txt. tools/test_host.sh configured/built and ran CTest
(1/1 PASS); the direct binary reported the totals above. The sanitizer cache
uses -fsanitize=address,undefined -fno-omit-frame-pointer. No implementation fix
was needed. Independent final reproduction is recorded in the scoped review.

Exact23-file
maps in P1_menu_inert_proposed.json were independently reconstructed and compared
byte-for-byte to source before explicit reviewer approval and manifest refresh.
Only config.h/countdown.h/countdown.cpp differ from f38488d; other20 files remain
unchanged. Approval is source inertness only, not target execution.

First tooling run is preserved in P1_menu_tooling_20260923.txt:116 checks ran in
38.818s, one failure/exit1. The sole failure is the exact config declaration set:
its explicit non-B16 specification dictionary did not include the precommitted
MODE_SHORT_MS=600 addition. The independent author updated only that unlocked
dictionary entry; existing exact-name/type/value checks then cover it while all
76 B16 checks and other assertions remain intact. The reviewer inspected this
bounded contract update. No behavior implementation, locked assertion or unknown-
constant allowance is changed; keep the failed receipt alongside the rerun.
The rerun P1_menu_tooling_run2_20260923.txt passes116 checks in39.634s, exit0.

New tests:25 component cases and11 locked real-Lifecycle composition cases;
author report P1_menu_test_author.md. They use specifications/public headers,
not implementation cpp. No existing locked case changed. Running-mode capture
in the composition harness is not production Robot evidence.

No board action occurs in this batch. The latest actual compile98c436a4 predates
D-057/Menu sources. The previous inert matrix remains the last uploaded image;
host tests and source review cannot transfer its measurements to newer code.
Full Robot/running-mode capture, UI service execution/availability, A1 electrical
decoding, real MotorGate and target timing remain separate pending work. No
existing locked test or human phase gate is modified or inferred.
