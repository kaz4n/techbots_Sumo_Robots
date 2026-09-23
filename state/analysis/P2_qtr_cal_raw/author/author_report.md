# D089 independent test author receipt

2026-09-23. This is a reused agent, not a fresh-context review: it previously
implemented D085 native QTR, D086 ADC pair and D087 core routing. For D089 it read
the frozen D089/D085/D088/MotorGate contracts, relevant BEHAVIOR sections and public
headers/config only. It did not inspect D089 implementation CPP bodies, did not
derive assertions from prior CPP knowledge, and made no production/header/config,
old-test, board or commit changes. Tooling copies production bytes opaquely for
compilation; that is not implementation inspection by the test author.

## Delivered assertions

- test_qtr_cal.cpp: raw qualification/threshold adjacency, all-eight-stage atomic
  publication, white maximum/black minimum reduction with distinct sensor banks,
  one-unit gap, censored-black lower bounds, censored-white/separation rejection,
  original-bank preservation, equality deadline, replay/nonfresh/token/time order,
  pre-request acquisition, source spacing/sequence/wrap, context cancellation,
  native/malformed faults, exact formatter/capacity boundaries and version exhaustion.
- test_qtr_cal_handover.cpp: actual adapter->Robot boot ambiguity/raw preparation,
  genuine menu navigation/eight service requests->Calibration->bank, cached
  reclassification, distinct confirmation, new version handover, later classifier,
  fresh neutral rearming, STOP/fault cancellation and source-era boundaries.
- test_qtr_cal_motor_gate.cpp: the actual full pipeline through MotorGate callback
  writes. RAW/capture/handover/hold remain inhibited; a later fresh START receives
  the complete5100ms hold, followed by enabled/nonzero writes only in the enabled
  host target and immediate STOP inhibition. These callbacks have no native backend.
- test_qtr_cal_display.cpp: independent literal pixels for every sensor/color,
  every progress count, terminal icons, fault/battery preservation, hidden overlay
  rules, invalid fields and exact owner-report mapping.

The unit Protocol helper supplies public eligible-result records for isolated
owner checks. The Pipeline helper instead consumes actual Robot results, actual
service intents and actual MotorGate receipts; it never edits Robot results to
start its eight capture batches. Synthetic intervals are not electrical evidence.
Version exhaustion uses coordinator-authorized const_cast on a nonconst owner's
public const-reference bank: an injected boundary state, not reachable-history proof.

The source-era cases derive from the explicit review-disposition amendment, not
the reviewer's implementation or reproducer. They cover unseen cached frames
after full wrap and half-range-minus-one/equality for owner/Robot prior-source
age and Robot handover age. The reviewer found the original issue; these tests
were added after its contract amendment and are regression evidence.

## Commands and results

Strict compile command (four C++ test units):

```
wsl bash -lc 'cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots && g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS -I src -I host/third_party -fsyntax-only tests/test_qtr_cal.cpp tests/test_qtr_cal_handover.cpp tests/test_qtr_cal_motor_gate.cpp tests/test_qtr_cal_display.cpp'
```

Final strict syntax passes with empty diagnostics in syntax_final.txt. Initial
failed diagnostics remain in syntax_initial.txt (unsupported doctest REQUIRE
under no-exceptions mode) and syntax_all.txt (missing initializer_list include).
Assertions were preserved: fatal preconditions now CHECK then explicitly return;
the missing standard include was added. Intermediate successful checks remain.

```
wsl python3 -m unittest tests.tooling.test_qtr_cal -v
```

Four methods passed in27.436s after tooling-only entry points were renamed .cc
to avoid the repository's recursive tests/*.cpp executable glob. They check actual
probe setup/10000loops under MATCH/MOTORS_ALLOWED0 and1, maximum supported batch256,
full pipeline CONFIRM2/batch1 and CONFIRM3/batch32, and the original full P0 config
suite under temporary exact D088+D089 registry additions. Old test files remain
unchanged. Original three-method run passed in28.467s; targeted registry passed
in0.159s. A final new extrema/export case prompted another focused run of the two
variant methods; both passed in20.501s, including the final31-case profile suites.
Their raw results are appended to the same aggregate receipt.

tooling_runs.jsonl contains actual command arrays, return codes and complete
stdout/stderr from every compiler/executable/config child, including reruns. It is
one aggregate raw receipt, not manufactured summaries or per-case files. Parent
unittest timing above is copied from observed tool output. source_hashes.json
identifies delivered author files.

Coordinator's first enabled-host failure is preserved in ../host_initial.txt.
The fixture's default raw opponent mask0 incorrectly asserted the four active-low
MZ80 inputs. BEHAVIOR B5 and config OPP_ACTIVE_LOW_MASK=0x78 specify inactive levels;
the fixture now sets that value. The original6000us post-GO nonzero-write assertion
was retained. This was a test-input correction, not a production or timing fix.

Normal/sanitizer full-host, target compile, staged-source identity and fresh review
are coordinator-owned evidence. The final extrema case was explicitly announced
before the implementation commit and requires their incremental inclusion.
No allocation instrumentation, physical color separation, full-loop WCET, optical
visibility, ADC/window accuracy, hardware ownership or human-gate pass is claimed.
