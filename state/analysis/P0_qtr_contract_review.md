# P0 QTR diagnostic contract review — 2026-09-23

Verdict: **no BLOCKER or MAJOR algorithmic contradiction with the installed
source/binary audit**. Three small documentation corrections are listed below.
The proposed setup-only experiment is feasible subject to its final source,
target-image and measurement checks. This is a contract review, not approval
of implementation or upload and not evidence of executed GPIO operations.

Scope: read only the proposed contract, public record header, four diagnostic
config additions, current decision context and the earlier installed-source
audit. No implementation source, target operation or tests were executed.
Only this review file was added; shared code/config/contracts/ledgers were not
edited. Other agents are implementing and authoring independent tests.

## Reviewed snapshot

SHA-256 at review:

| File | SHA-256 |
|---|---|
| state/analysis/P0_qtr_contract.md | `5297038289635dc3b44d8e0f704b949efcc37752ea97ffc24d4023e33f823beb` |
| bench/p0_qtr/src/qtr_capture.h | `f11d4fc816155202389a50c499043c632a5867973ee94e59d2f8a725fbfcc745` |
| src/config.h | `b0115938d72162a8f765e372d71fe688bc5070b8462c209326f930acabc12ee3` |

The source basis is P0_qtr_bare_contract_audit_20260923.md, including the exact
installed GPIOA/B device exports, STM32 configure/read dispatch, SysTick clock
and core wrapper behavior. D-065 was proposed rather than present in the
DECISIONS.md snapshot initially read; the coordinator owns recording adoption.

## Documentation findings

1. **MINOR — scope “no interrupt masking” to application code**
   (contract:13–14). Installed `micros()` briefly masks/restores BASEPRI around
   its SysTick accumulator read. Literal prohibition of all interrupt masking
   conflicts with calling this installed clock. Specify no application-level
   masking and no whole-acquisition critical section; permit the already-audited
   internal clock implementation. No algorithm/test change is needed.
2. **MINOR — qualify “full 1500 us interval” as clock-reported timing**
   (contract:29–30,44–46). `micros()` is an integer floor conversion. A reported
   delta of 1500 can represent a true clock interval slightly below 1500 us,
   by less than one microsecond, before other physical/instrument uncertainties.
   The current threshold is coherent as a 1500 us Arduino-clock timeout and
   should remain distinct from an exact physical minimum. Add that quantization
   limitation instead of silently extending or changing the selected threshold.
3. **MINOR — repair record-layout wording** (contract:63).
   “24-byte header and20072-byte samples” should read “24-byte header + 200
   samples of 72 bytes = 14424 bytes.” Header arithmetic and static assertions
   themselves are consistent; this is not a layout defect.

## Checked contract details

| Topic | Assessment |
|---|---|
| Exact pins and readiness | Config `{2,4,7,8}` agrees with named D2/D4/D7/D8, GPIOB/PB3, GPIOA/PA12, GPIOB/PB2 and GPIOB/PB4. Checking both ports before any pin call is appropriate. Final ELF must still prove the adapter and relocations. |
| Charge lower bound | Measuring from after the last HIGH write removes per-pin charge-start ambiguity for the minimum. With working monotonic floor-quantized clock, a reported delta of at least 11 us implies true clock elapsed greater than 10 us: if `m(t)=floor(t/us)`, `m(t1)-m(t0)>=11` gives `t1-t0>10 us`. This is a sound diagnostic quantization margin, not voltage/oscillator calibration. It also avoids the installed `delayMicroseconds(10)->k_busy_wait(9)` issue. |
| Finite charge guard | At most 4096 clock calls, with successful equality on the final call winning, is clear. No-progress clock produces explicit failure. This does not bound an API that never returns or scheduler starvation, which the contract states. |
| Sequential release | The observation epoch after all four mode transitions gives every released input at least the common measured observation duration, subject to quantization. Earlier pins have additional release skew. The contract explicitly retains that limitation and does not claim production discharge timestamps. |
| Four reads per pass | Reading all four pins, even previously LOW pins, establishes a consistent diagnostic polling cost and meets the requested genuine GPIO timeout exercise. Sticky first-LOW evidence is distinct from the level of later reads. |
| End-pass timestamp and late LOW | A first LOW detected in a pass is deliberately timestamped after all four reads. A pass crossing the deadline can therefore report a late first LOW and a DEADLINE with timeout_mask zero. This is internally consistent diagnostic evidence; it is not a sensor threshold-crossing timestamp. |
| Deadline precedence | For valid passes, recording LOW observations first and then checking deadline before ALL_LOW resolves ties and overshoot explicitly. “DEADLINE” means the loop ended at/after its clock threshold; it does not imply that all four inputs timed out. `timeout_mask` retains that separate meaning. |
| Finite observation guard | At most 4096 complete passes bounds the number of reads to 16384 per sample. Deadline/ALL_LOW on the final allowed pass precedes POLL_GUARD. Whether a real sample reaches the deadline within that count remains a measured result; guard exhaustion cannot be reported as success. |
| Pull-up separation | The pull-up dataset is separately labeled diagnostic-only, preserves every observed early LOW, and requires low_mask zero plus full timeout evidence for stimulus qualification. The neutral dataset imposes no timeout expectation. No sensor or SC-B inference is permitted. |
| Cleanup | Exactly one INPUT attempt on all four pins on every post-configuration exit matches the installed path that clears the pull configuration. `cleanup_calls` correctly means attempted calls, not native success. No expectation of a LOW floating read is imposed. |
| Native error masking | BAD_LEVEL is useful defensive/host-test coverage for an abnormal public API return. The installed Arduino digitalRead can only produce LOW/HIGH and masks native negative errors to LOW; BAD_LEVEL must never be described as detecting those native errors. The source audit and cleanup wording preserve this limit. |
| Frozen completion | Publishing a whole sample before completed, retaining a fault sample, and keeping complete zero on faults are coherent. Complete one means all acquisitions finished, while the decoder separately rejects failed pull-up stimulus. A raw capture must remain available after that rejection. |
| Decoder | Mode order, outcome/deadline consistency, complementary masks, first-LOW sentinels, count bounds, cleanup attempts and elapsed arithmetic provide meaningful corruption checks. The normal stage durations telescope from total start through final cleanup, so their exact sum is appropriate when the implementation uses the specified shared boundaries. |
| Layout | QtrSample has 18 32-bit fields including the four-element array, or 72 bytes; QtrCapture has 24-byte header + 200 × 72 = 14424 bytes. This fits the existing 16384-byte per-read cap. Actual target offsets/endianness remain subject to ELF review. |
| R4 / phase limits | Setup-only collection and empty loop do not conceal a claim of 1 kHz compatibility. The 1500 us observation plus overhead still exceeds the production execution budget. Gates, real QTR hardware and freshness semantics remain unproved. |

## Next action and verification limits

Coordinator should correct the three wording points while recording D-065,
then implement and test the stated algorithm. Retain the original reviewed
snapshot hash above so any later semantic change is identifiable. The independent
test author should specifically retain late LOW/deadline-zero-mask, exact final
guard-call success, all-four cleanup after charge failure, and aborted BAD_LEVEL
passes with all four reads completed.

No runtime verdict is supplied here. Final review still needs actual source,
independent test results, exact target imports/constructors/hooks and pin
ownership, binary/source manifests, and any separately authorized measured
record. No production behavior, hardware measurement, PINMAP approval, motor
authority or human phase gate follows from this contract review.

## Resolution — subsequent read-only check

All three documentation findings are resolved in the contract with SHA-256
`e2b8dcecec05a93911ee7e73342bda12002c3254fea3d97d25b59aedf31afc92`:
it now specifies application interrupt masking, qualifies the 1500 us window
with sub-microsecond clock quantization uncertainty, and states 200 samples of
72 bytes. Native digitalRead error masking is also explicit. The coordinator
identified commit `db8728b` for the quantization clarification; the live document
hash above is the inspected evidence, without attributing every later wording
change to that commit. The original snapshot and findings remain above.

The clarified cleanup policy additionally attempts INPUT on all four pins for
every started sample, even an overhead-clock failure before output configuration.
That is consistent with the installed neutral-input path and provides a defined
final attempt after such a failure. The readiness-failure path still performs
no pin calls. No new contract finding follows. **No open BLOCKER, MAJOR or MINOR
contract finding remains in this reviewed scope.** Implementation and exact
target binary review are separate.
