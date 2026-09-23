# D088 matrix review

2026-09-23, fresh-context separate same-model reviewer. Baseline d899668; reviewed
contract8fd11dd/implementation385c46c plus source/target receipts. Reviewer owns this report and
P2_matrix_raw/review only; no implementation, ledger, test, registry or MCU action.
The scope is B3/B13/B14 display software and the user-authorized inert bare-board
diagnostic. Today is Wednesday23September; original PLAN section3 schedules P0/P1.
D051/D075 permit this P2 software work without closing any human phase gate.

## Findings

No open BLOCKER, MAJOR or MINOR finding within the reviewed scope.

Two draft independent fixtures were corrected against the prior contracts:
INVALID draws left E, cross, top markers and unknown battery, without a right
fault glyph; D084's existing retained-heading bound is2000us, not20000us. The
initial root pixel failures and reviewer display_added_cases failure are retained.
No established or locked test was changed or weakened. The reviewer approval
helper's initial bench-local path mistake is separately recorded and was fixed
before issuing approval; it did not touch production source.

## Verdict

PASS for the D088 renderer, actual native adapter, diagnostic mapping and exact
normal-startup inert diagnostic source. No gate pass or optical acceptance follows.
Exact six-key source approval is P2_matrix_raw/review/approved_inert_sources.json.
bench/ui_matrix is approved only with MATCH=0, MOTORS_ALLOWED=0 and normal startup;
the coordinator must pass upload-tool regression before the authorized run.

## Source and safety review

- ui_display fully overwrites104 pixels, bounds enum/mask/finite battery inputs,
  preserves5..1 through the100ms margin, never displays GO, and separates unknown
  sensor/battery indications from measured zero. Mode/service/STOP/BOOT priority,
  literal mirrored icons, all fault masks and battery thresholds match D088.
- displaySample uses actual paired Robot input/result, current mode selection,
  release anchor and declared freshness. The only core behavior addition is
  diagnostic imu_available derived from resolved input and heading admission;
  it does not grant motion or alter arbitration. Real Robot tests cover pre-GO,
  missing/malformed/retained IMU, countdown, duplicate result and menu routing.
- UnoQMatrix has no constructor/destructor I/O, is noncopyable, and enforces one
  lifetime owner. Grant/context/device-readiness checks precede native mutations.
  Faulted instances stay faulted; failed acquisition does not consume ownership.
  Every104-byte submission is validated before cadence, including throttled calls.
  First output is immediate; later output is one submission at or after40000us,
  including wrap. No catch-up loop, heap, retained frame pointer, Bridge, text,
  scrolling, matrixEnd or post-setup matrixBegin occurs in this adapter.
- Both blank initialization and frame writes save PRIMASK, disable IRQs, call the
  actual fixed native copy, DMB, then restore the exact saved mask. Context and
  frame validation occur outside that section. Kernel device readiness is not
  timer/display success, so INIT/SUBMITTED remain explicitly UNCONFIRMED.
- The bench setup calls only this matrix begin; loop calls micros, the synthetic
  scene/renderer and submit, then updates RAM counters. No external acquisition,
  GPIO/PWM motor operation, MotorGate or motion request is reached. All five old
  inert sketches are unchanged against d899668. New shared code introduces no
  native global initializer. board_tool adds only this exact-source-gated inert
  name and explicitly rejects its Immediate upload.

## Evidence

- Reviewer clean local CMake build and full normal CTest:2/2 PASS,7.16s, including
  unchanged locked and enabled-MotorGate suites. After two additional tests were
  frozen, focused D088 rerun:15cases,1521100assertions PASS. Receipts are host_final,
  build_frozen and display_frozen under review/.
- Coordinator final frozen full normal and ASan/UBSan suites also pass2/2:
 1224main cases/24475290assertions plus38enabled-MotorGate cases/3843482assertions.
  The coordinator's new five upload methods pass44.006s and unchanged25tools plus
  two staging methods pass. Their direct receipts were inspected by the reviewer.
  Registry adoption equals the six-key approval. Later tool/CMake LF normalization
  preserves their previously reviewed canonical Git blobs; approved current file
  hashes and unchanged six firmware maps are recorded in approval_normalization.json.
- Reviewer final independent native/capture suite:23methods PASS in8.173s.
 15native methods execute the actual ui_matrix_unoq.cpp in866 separate processes
  across normal and ASan/UBSan variants. Native substitutes observe call order,
  privileged Thread admission (including CONTROL2), null/unready device, failed
  grants, owner lifetime, local fault latching, every invalid byte before cadence,
  unchanged caller data, wrap and PRIMASK0/1 preservation. Eight pure capture tests
  cover structure/status decoding, uint32 progress, bounded reads, deadlines and
  extension identity. All process records are in review/native/.
- Actual board Linux compile-only succeeded:80592B program,32244B compiler globals.
  Reviewer independently reproduced all six staged hashes and matched all61
  current source files to target e50c6da38bba5131e426d8c076e7aa7c8aad5961f60a6eb1387b1f2412aab6af.
  Three ELF identities,40native imports and42AEABI imports were checked; every
  required export was nonzero. The upload ELF is14023aa1e0b788edbbfe92e6b6b8aeed0afff6e0b329360af212c9df3688a7ab.
  Retained begin/submit code contains CONTROL/IPSR checks and matching PRIMASK
  save/restore register sequences with cpsid/DMB and no cpsie. Native relocation
  targets include the actual matrix APIs and counter_matrix readiness. Project
  initializers have no calls; initVariant is empty. See target_identity.json and
  target_excerpt.txt, plus the complete coordinator receipt they hash.
- Runtime wrapper was reviewed before use. Pinned loader/ELF/sketch hashes and
  fixed symbol/layout precede decoding. Unchanged p0_capture/p0_mem_read mechanics
  permit bounded MEM-AP reads with120s/16-read limits and no MCU memory write,
  reset or halt command. Two40-byte telemetry reads derive progress from the one
  aligned submission scalar; LLEXT list/node identity is rechecked afterward.
  The coordinator co-locates the wrapper with the pinned helper/config remotely.

## Runtime closure

Coordinator deployment/capture succeeded after review and tool tests, using the
one authorized normal-startup bare UNO Q run. Reviewer issued no MCU command and
independently audited the returned files offline. runtime_identity.json verifies
all9raw read hashes, all26raw stdout/stderr files from13successful commands,
exact copied capture report, deployed80592-byte sketch SHA256
6de9d536572132fc8f4fa1d7962aecf15a479da7564221df4512944db2066a69,
and263680-byte deployed loader hash e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2.
The loader matches the pinned ELF load-image expectation and prior pinned raw
capture; it is deliberately compared to ELF load bytes, preserving the known
single-byte difference from the packaged binary. This verifies this run's exact
loader/sketch identity, without qualifying inherited platform timing behavior.

The single sketch LLEXT node, list head/tail and BSS mapping remained stable.
BSS size7708bytes; uiBench is the40-byte structure at offset120. Raw snapshots
show initialization1, failures0, render status0 and submission status2. The one
aligned submissions scalar advanced3341->3418, a modular increase of77. The
board-monotonic interval bounds are3.000408848..3.145329966seconds; capture duration
106.208485173seconds, within the120s bound. Scene changed7->8. max_call_us37 is
only the bench's unqualified MCU-clock diagnostic for rendering/submission, not
interrupt-mask duration or full-tick WCET. Board UTC and Windows UTC differ by
about2seconds; no cross-host wall-clock ordering is inferred.

PASS remains limited to actual execution and unconfirmed frame submissions.
No optical image/orientation/brightness observation was supplied, and no further
board action was performed by this review.

## Limits and next action

This review has performed no MCU action. The coordinator's deployment/capture is
separately recorded as described above. A synthetic scene is not sensor
evidence; readback counters do not prove LED orientation, brightness or visibility.
The104-byte critical section is not scan-boundary atomic; old/new slots can share
one physical scan. IRQ-mask duration and interference with QTR/IMU/control timing
remain unmeasured. The caller must honor serialized exclusive boot ownership,
including NMI/HardFault and inherited animation, and forward-time assumptions.

Inherited Bridge constructors/loop hook remain in the artifact and are not newly
qualified for Linux independence or an800us control tick. SC-AJ/F091 and physical
pins/electrical/sensor/optical acceptance, app/service integration, full RAM/WCET,
motor-run authorization and every human phase gate remain separate. Carry the
verified software/runtime scope into the next active P2 task without converting
synthetic scenes or submission counters into physical acceptance.
