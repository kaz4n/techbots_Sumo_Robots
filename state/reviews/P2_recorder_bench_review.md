# D091 inert recorder bench: fresh independent review

## Verdict

**PASS for the exact inert source, compiled artifact and bounded capture helper.
No open BLOCKER, MAJOR or MINOR finding.**

This is a fresh separate same-model review, not a cross-model review or human
phase gate. The reviewer edited only this report and its adjacent
`P2_recorder_bench_review_raw/` evidence. No implementation, test, configuration
or protected-test edit was made by the reviewer. No MCU command, upload, reset,
attach, capture, motor command or board-service action was run by the reviewer.
September 23 remains before the PLAN scope-cut and code-freeze dates. D051/D075
permit this bounded P2 software work; D091 defines the inert experiment.

## Findings and dispositions

- MINOR, resolved before final review: `tools/recorder_capture.py:99` now requires
  FROZEN to have a SEALED source and a checksum row count equal to retained frames
  plus events. The additive independent test rejects inconsistent terminal fields
  while retaining partial FAILED reports and all explicit loss information.
- Retracted layout concern, not a production defect: the coordinator and reviewer
  initially inferred ELF `st_value` from GNU nm's displayed address. Actual readelf
  reports `recorderDiagnostics` at section-relative `0x28928`, while nm displays
  `0x37a58` after adding `.bss` VMA `0xf130`. The existing parser was correct;
  no subtraction or source repair was applied. Actual-symbol replay and six new
  literal layout tests close this concern. See `layout_review.json`.
- Reviewer helper corrections are preserved in `review_execution_notes.md`.
  They did not change production code or weaken assertions.

## Source behavior

`bench/recorder_inert/recorder_inert.ino:5` reaches only the native bench begin/poll
wrapper. Runner uses real supplied clock readings, at most one tick per poll,
explicit skipped slots/lateness, qualified synthetic START, the actual Robot,
inert MotorGate callbacks and AttemptRecorder. There is no timestamp fast-forward
or catch-up loop. Recording stops only after at least 200,000,000 MCU microseconds
from the accepted release; final deferred data seals before bounded row-at-a-time
CRC processing. First failures persist, late/invalid chronology fails closed,
and terminal native polling is inert. Counts, status bytes, loss, source identity
and timing feedback survive publication. The inputs are explicitly synthetic.

Every configured motor callback is the Runner's inert callback. Nonzero PWM and
enabled EN are counted and rejected; no native MotorGate backend is constructed
or initialized by the reachable bench path. No native motor, QTR, opponent,
ADC, IMU, matrix or UART initialization, Bridge begin/update, Monitor/RX parser,
post-setup heap allocation, delay or unbounded per-tick work is reachable.
Existing core/HAL files, B16 values and locked tests were unchanged in this task.

The native wrapper samples privileged Thread-mode PSP only after checking the
actual current-thread metadata address and SRAM region. It publishes 296 bytes
with odd/even sequence markers and barriers, then freezes. Stack faults invalidate
stack evidence without inventing a watermark. Installed F113 evidence and actual
imports establish the nonzero current-thread API `0x08011ae1`; the zero stack-space
export is never imported or called. Sample locations do not measure historical
high-water, interrupt stack use or complete application WCET.

## Capture and allocator review

The decoder matches the pinned primary heap.h/heap.c layout: small 16-bit chunk
fields, 80-byte metadata chunk, 15 bucket heads and the reserved end marker. The
forward chain, left links, reciprocal circular free lists, coalescing, bucket
membership and complete payload/overhead accounting are all bounded and checked.
Canonical metadata hashing excludes live payload and inactive padding. Both full
snapshots are preserved and validated before reporting sampled consistency.

Capture verifies pinned tools/config/loader/ELF/ZSK bytes, deployed flash identity,
bounded LLEXT traversal and the exact diagnostic symbol before interpreting private
RAM. Only fixed MEM-AP reads and readelf/version commands are admitted. Limits are
48 reads, 2 MiB total, 16 KiB per RAM read, 64 commands, 600 seconds overall and
30 seconds per command. Failed attempted reads consume budgets. Partial files,
exact commands, timestamps, exit or timeout outcomes and failure information are
retained. The old p0_capture guards and MEM-AP configuration remain unchanged.
No CLI address/size/command input, Cortex target, reset/write or service command
is introduced. CAPTURED describes evidence collection, not experiment acceptance.

## Reproduced evidence

- Independent Runner harness: 11 cases and 1,464,342 assertions in each normal
  and ASan/UBSan build, all pass without skips. The source snapshot is unchanged.
- Offline heap suite: 28 methods pass, including all 15 buckets, 32,757 normal
  chunks, maximal free-list traversal, malformed metadata and payload-only changes.
- Final capture/upload run: 44 methods pass in 0.353 seconds: 39 capture methods
  and five controlled upload-boundary methods. The latter mock all transport;
  their printed upload messages are test output, not an MCU operation.
- Actual target readelf symbol/section transcripts replay successfully through
  read_layout: BSS 173,892 bytes, diagnostic offset 166,184, size 296.

`review_runs.jsonl`, `runner_runs.jsonl`, `final_capture_upload.txt`,
`layout_review.json` and `final_approval.json` retain these results and final hashes.
The initial 61-method combined run predates the final additive capture tests;
the final capture run supersedes that capture count. No failed test was hidden.

## Exact source and ELF approval

All 74 board-retrieved source hashes match current physical and staged bytes,
and the independently recomputed aggregate is:

`1502e9484068921fe3f96adef402e12fc85a00093b544e4a6c0dee165476b583`

Only `bench/recorder_inert`, default startup, MATCH=0/MOTORS_ALLOWED=0 is approved
by this source review. The exact already-compiled artifacts are:

- Final ELF: `eff3e050072b41d888c343ea57c4d966069882892a7dc50bb0224946a26a798d`.
- Upload ZSK: `0448e3ac5a5409bdfd08226f42f0d74c66dbe85d7bfd2ffb27a76acc3a7bfd2a`.

All three actual ELFs have the strong empty `__loopHook` at `0xa034`. Actual main
calls it through the relocation at `0xe2fc`. Eleven startup entries were inspected:
storage initialization, Runner construction, passive Bridge state, serial buffer
semaphore initialization and destructor registration; no peripheral begin or RPC
execution. Variant initialization is empty, and loader/sketch static-thread lists
are empty. The 43 inspected native and 42 AEABI exports are nonzero; supplemental
fmod/sqrt imports are nonzero. Reachable runtime paths, not mere absence of symbols,
establish inertness: unused native/Bridge/allocator functions remain linked.

`source_target_check.json`, `target_startup_excerpts.txt` and root target/link
receipts preserve this inspection. Final capture path/ELF/ZSK pins match those
artifacts exactly. `final_approval.json` supersedes the source-only approval's
provisional capture note. Any rebuilt or changed artifact needs renewed identity
verification before relying on this exact-artifact result.

## Limits and next action

The compile reports 146,072 program bytes and 236,660 global bytes with a low-memory
warning. Those are not actual loaded free RAM or a transient loader peak. No real
200-second execution, allocator observation, physical B8, UART transfer, complete
800-us tick, application integration or human gate is established by this review.
The coordinator may proceed with the separately identified exact inert run and
the now-reviewed bounded capture, preserving every failure and observed loss.
SC-AJ clock qualification, assembled sensors/motors, transport preparation and
remaining P2 integration remain separate pending work.

## Readback retry addendum: fixed flash chunks

The first actual capture, performed by the coordinator, failed closed on its
single 263,680-byte loader read after the unchanged 30-second command deadline.
The 94,208-byte partial file and complete timeout receipt remain in runtime_run1.
Flash identity stayed false; no recorder diagnostic or allocator result was read.
This was a readback throughput failure, not a measured recorder failure or success.

The reviewed follow-up modifies only the new capture helper's flash subdivision.
It reads five loader and three sketch chunks, each at most 65,536 bytes, with
exact indexed labels, addresses and final sizes of 1,536 and 15,000 bytes. It
compares all reconstructed loader bytes to the pinned ELF load image, then all
sketch bytes to the pinned ZSK, before granting private RAM read authority. A
previous true flag is cleared first. Incomplete, wrong or failed chunks remain
failures, and attempted reads remain charged. Legacy whole-span labels stay exact
for API compatibility; production verification uses the indexed chunks only.

All original limits remain unchanged: 48 reads, 2 MiB, 16 KiB per RAM read,
64 commands, 600 seconds total and 30 seconds per command. The normal one-sketch
capture needs 47 reads. Extra loaded extensions may exhaust the guard and must
fail explicitly; the retry does not gain a larger budget. Firmware, artifact
pins, old p0_capture/config, heap decoder and all original 39 capture tests are
byte-identical to the prior review.

Independent rerun: **50/50 methods pass in 0.824 seconds**, including 11 new
flash methods. They verify exact chunk ranges, every chunk's first/last byte,
partial/failure handling, stale-flag revocation, RAM gating, read/byte limits and
no retries of a failed purpose. The initial 49-method run had one new test with
an incorrect package-equality assumption; that failed receipt is preserved.
The corrected test explicitly checks the known pinned package byte255 versus ELF
byte0 at offset260287, reports that difference, and still rejects deployed flash
matching the package rather than the ELF at that byte. No older test changed.

**PASS for the exact revised helper**
`fd1932acc3f78ce68fb833f54b1e1ce72ab97aeb3942cc53dad27acb45dc6e25`.
`P2_recorder_bench_review_raw/capture_chunked_approval.json` is the exact delta
approval; `chunked_capture_initial.txt` and `chunked_capture_final.txt` preserve
the failure and final reproduction. The same identified inert firmware may be
read again through this helper without upload, reset or daemon action. The
original source/ELF review remains valid. Runtime/physical/human gates remain
outside this approval.
