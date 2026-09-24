# D128 P4 reactive profile independent review

Status: PASS for D128 software admission/routing and inert build integration.
No material findings or open D128 blocker. The new locked oracle
`tests/locked/test_reactive_profile_safety.cc` SHA256
`0e26c02edb244d7c8b42d69ea337a6bfe5209206f482edbb453e259f531295ff`
is accepted in this scoped review; all 38 prior locked files remain exact.

Reviewer is separate from implementation and public-oracle authors, same model
family. Review owns only this report and its adjacent `_raw` directory. Scope is
D128 admission/GO routing and inert build integration. SC-AO exact target-loss
timing evidence and physical P4 acceptance remain outside this slice.

The private five-case oracle derives expected behavior from the adopted D128
contract and existing public interfaces/fixtures, before reading the D128 route
implementation. It covers all six modes, six effective bearings at ordinary and
wrapped full-hold GO, post-GO three-observation qualification, empty Search entry
continuity, raw/effective separation, edge priority and STOP, and configured actual
Runtime hold plus service-only inhibition. Its runner compares default/B4/all P3
object layouts to pre-D128 c58aeae0 and expects profile1 to add no instance storage.
No execution occurred before the independent private freeze.

Static preflight finds no material issue in the current scoped source. In
`src/core/fsm_robot.cpp:324`, P4 follows the unchanged ordinary match-menu START
admission. The existing permission/edge/escape-exit branches at line 450 precede
the profile GO branch at line 479. That branch cancels stale motion once, starts
actual Search with the effective mask, and keeps `normal_active_` true so line
603 does not erase an empty GO scan on the following observation. The profile
excludes both opener start and execution while retaining `checkStall()` at line
120. All downstream Governor, source, receipt, Gate and Runtime code is unchanged.

The wrapper uses actual NativeSources/UnoQPort/Runtime with empty SetupGrants.
`tools/app_build_policy.py:99` requires default startup and exact inert P4 flags;
`tools/board_tool.py:296` rejects upload before board I/O because no upload key was
added. The flags helper extraction retains the old profile-specific strings.

A pre-execution private-draft correction uses BEHAVIOR B0's FC bit1 (mask2),
instead of the initial draft's mask1, for singleton centered expectations.
The initial draft/freeze are retained and no implementation/public tests changed.

After the public freeze at 2026-09-24 04:06:56 UTC and the root's execution notice,
both private targets passed on their first execution: five cases, 64,487 M0 and
63,037 M1 assertions, zero failures/skips. These are synthetic host transactions
using actual Robot/Transaction/Gate/Runtime owners and configured synthetic button
windows in an isolated copied fixture. The repository config was unchanged.
See `_raw/private_validation.json`, `tests.log`, `private_freeze.json` and the
preserved initial pre-execution private draft.

Object-layout probes against pre-D128 c58aeae0 passed. Sizes below are host bytes,
ordered Robot / RobotResult / Transaction / Runtime; prior and current match:

| Profile | Bytes |
|---|---|
| Default, P3 drive, P4 reactive | 2640 / 400 / 162616 / 166624 |
| B4 stand | 2696 / 424 / 162696 / 166704 |
| P3 turn | 2800 / 440 / 162816 / 166824 |
| P3 stopping | 2744 / 440 / 162760 / 166768 |

The accepted public oracle was read after private freeze. Its 34 ordinary and 35
configured cases cover all 128 masks across all six modes, real Gate PWM order
and quantization, contact/low-voltage caps, exact synthetic loss boundaries,
DEFEND, complete stall/re-flank and third-stall ALL_IN, every white pattern,
escape exit, STOP, source/receipt failures, duplicates and configured Runtime
service-only retention. These assertions support software behavior, not a timing
measurement from physical sensors/motors.

Independent `_raw/final_bindings.json` verifies all 499 frozen source/oracle/build
files, all 38 established locked raw hashes, Git-filtered identity against
c58aeae0, the private freeze, and all 100 default / 101 reactive staged files.
The initial binding diagnostic incorrectly compared Windows CRLF bytes directly
to Git LF blobs for 19 native-port fixture files. It is preserved; the corrected
check separately retains exact raw-hash equality and configured Git-filtered blob
identity. No tracked source, public oracle or locked test changed for that check.

Actual compile-only receipts bind reactive source `9ddaa2aa...`, ELF
`01e39e39...`, exact C/C++ inert profile flags and default startup. The ELF account
retains normal arbitration and stall symbols and reports no opener symbols.
Default source `43d16734...` produces the same ELF `21b28ee3...`, ZSK image and
loader estimate as D126. Conditional pristine-pool models are peak/free
255632/6512 bytes for reactive and 262128/16 bytes for default. They establish
neither successful live loading nor measured free memory or WCET. Controlled
tooling receipts show 135 methods plus two registry checks PASS, first execution.

Public receipts and archived `LastTest.log` files independently inspected:

| Run | Result |
|---|---|
| Full normal regression | 12/12 targets PASS, including all established profiles |
| Reactive M0/M1 normal and ASan/UBSan | 34 cases each; 164726 / 157452 assertions |
| Configured Runtime M0/M1 normal and ASan/UBSan | 35 cases each; 241856 / 234582 assertions |

All public runs passed on first execution, with zero failed/skipped cases. No
production/public-oracle changes followed freeze. The reviewer source-binding
check was repeated after these receipts; all 499 frozen files and target bindings
still match. Private execution also observed no source changes.

No hardware actions, inferred measurements, human gates or motor authorization.
SC-AO exact stimulus/decision/applied timing instrumentation remains the next
bounded software task. Physical acquisition/push/loss/edge/stall trials and actual
load/free-memory/WCET qualification remain pending. The existing default loader
model's 16-byte free span is retained evidence, not a runtime readiness claim.
