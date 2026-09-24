# D126 finite P3 stopping-trial scoped review

Date: 2026-09-24. Reviewer: separate same-model reviewer, independent of the
implementation and public test author. Earlier read-only exploration and D125
review are disclosed; the reviewer authored no D126 implementation or public
oracle. D125 evidence remains immutable.

Status: PASS for the bounded D126 software slice. No open BLOCKER or material
source finding. All 493 frozen files and 37 established locked files match.
The new safety oracle is accepted unchanged at SHA-256 prefix `01213382`
(full digest in the public freeze). This is not physical acceptance or GATE P3.

Scope: adopted D126 contract/public interfaces in `2a553830`, finite actual
Straight/Brake routing, conditional Governor cap, existing escape, Lifecycle,
MotorGate and Runtime boundaries, default-profile isolation and checked inert
compile-only tooling. Reviewer edits are confined to this report and
`P3_stop_trial_review_raw/`, plus isolated temporary host fixtures. No hardware
action is performed by this reviewer.

## Contract and source trace

- SC-AN retains the original border-to-front rest measurement and supplements
  it with independently measured maximum outward excursion in the same
  first-white/reference/direction coordinates as R_room. No conversion offset,
  distance inference or SEARCH_DUTY_MAX change follows from this software.
- The exclusive profile admits the existing selected DRIVE_TEST local service
  through classified-line readiness and actual full Lifecycle hold. It does
  not select Search, openers, combat or stall executors; perception remains real.
- Straight captures match heading and uses actual IMU availability. The report
  preserves pre-Governor requests separately from real applied duty receipts.
  STOP_TRIAL_FORWARD adds only a conditional final electrical cap; compensation,
  immediate cap reduction/brake and acceleration slew retain their ordering.
- Observed Straight DONE starts a full 500 ms Brake interval and records
  NO_EDGE_TIMEOUT. COMPLETE inhibits immediately before next-tick Lifecycle
  STOP. This terminal label is explicitly invalid stopping-distance evidence.
- Actual escape evaluation precedes trial routing. Edge at GO prevents start;
  edge during either primitive interrupts permanently, while owner stopping
  waits for actual successful escape exit. Reset-only faults retain inhibition.
- Late faults and token exhaustion publish inhibited outputs and cancel active
  trial history; duplicate observations clear fresh/phase-change pulses.
- D103 may reconstruct the Robot and clear the report; retained recorder data
  does not serialize the new report. Native Gate STOP and service-only input
  projection still prevent another motion attempt.
- New fields and governor enum/cap are conditional. Existing default, B4, D123
  and D125 layouts are unchanged; the 37 established locked files remain exact.
- The native wrapper uses empty SetupGrants and asserts exclusive profile1,
  MATCH0 and M0. The checked route requires the exact inert C/C++ flag tuple,
  default startup and compile-only operation, with no upload allowlist entry.

## Independent verification

`P3_stop_trial_review_raw/private_freeze.json` binds four independently written
checks before execution: delayed approach completion/brake across wrap;
24 combinations of edge mask and before/at/after primitive deadline; immediate
cap reduction from a previously full centered-contact Governor request; and an
actual configured Runtime timeout followed by D103 reconstruction and 5,200
inhibited service ticks. The private fixture overlays selected duty 0.70 and
known synthetic button windows only. Actual execution occurred only after the
root's public-freeze notice, recorded in `execution_authorization.json`.
Both M0 and M1 pass all four cases and 36,170 assertions on the first run.
Production source hashes remained unchanged during execution.

Header-only probes compare Robot / RobotResult / Transaction / Runtime with
accepted D125 (`f39c9929`), respectively:

| Established profile | Before and after, bytes |
|---|---|
| Default | 2,640 / 400 / 162,616 / 166,624 |
| B4 | 2,696 / 424 / 162,696 / 166,704 |
| D123 DRIVE_TEST | 2,640 / 400 / 162,616 / 166,624 |
| D125 turn trial | 2,800 / 440 / 162,816 / 166,824 |

These are host object layouts. They establish no additional default storage
from this change, independently supported by the identical default target image.

## Bound public and target evidence

`P3_stop_trial_review_raw/evidence_bindings.json` records PASS for 899 checks,
including public/private freeze identities, current production source, all
protected files, actual test summaries, staged target source and ELF hashes,
checked compiler properties and a fresh evaluation of the retained conditional
loader model. Public runs and target compilation were performed by the root;
private execution and evidence binding were performed by this reviewer.

| Verification | Result |
|---|---|
| Full normal regression | All 10 targets PASS: main 1,519 cases; Gate 187; B4 18 each; D123 27 each; D125 28 each; D126 30 each |
| Focused D126 normal and ASan/UBSan | M0/M1, 30 cases each; 269,698 / 262,866 assertions |
| Configured Runtime normal and ASan/UBSan | M0/M1, 31 cases each; 382,601 / 375,772 assertions |
| Duties 0.40 / 0.50 / 0.60 / 0.70 overlays | M0/M1, 30 cases each PASS per duty; default 0.30 covered above |
| Controlled tooling / registry | 121 / 2 methods PASS |

All these D126 runs pass on their first execution; no oracle or production fix
was needed. The public suite covers actual local admission/full hold and wrap,
all opponent masks, positive heading correction, real IMU loss/recovery, selected
electrical caps, exact callback/receipt behavior, full escape before STOP,
persistent faults, STOP/source/receipt rejection, duplicate handling, zero-time
presence flags, recorder semantics and configured Runtime service-only recovery.
Token-exhaustion cancellation is traced in source; no practical exhaustive
token run is claimed.

Checked native receipts bind default source `f1d1292d` (100 staged files) and
stopping source `9fd0f6ed` (101). Default ELF `21b28ee3`, packed sketch and loader
are byte-identical to D125. Stopping ELF `b4f15bfe` contains routeStopTrial and
omits routeNormal/checkStall/startOpener; the strong empty loopHook remains.
Exact checked flags are MATCH0/M0 and the stopping profile only, with default
startup. No upload was performed and no new upload allowlist entry exists.

The independently recomputed conditional pristine-pool peak/free spans are
262,128 / 16 bytes for default and 250,232 / 11,912 for stopping distance. The
model does not qualify live RAM, stack or WCET; the inherited default headroom
limitation is retained, not resolved by this slice.

## Limits

Host observations and checked target compilation do not prove stopping distance,
ring survival, settling, electrical/pin acceptance, safe start placement, live
RAM/stack margin or 800 us WCET. No motors, upload, reset, human phase gate or
production cap change is authorized by this review. Physical measurements and
an evidence-backed human tuning approval remain separate.

Next action: root may record and commit scoped D126 software acceptance and
protect the accepted new oracle. Physical three-runs-per-duty measurements and
compatible measured peak/R_room evidence remain pending.
