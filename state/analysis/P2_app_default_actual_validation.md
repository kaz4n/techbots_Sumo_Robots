# D118: unchanged motors-disabled app loaded on the bare UNO Q

**TARGET-COMPILED / UPLOADED / ACTUAL LOAD AND SAMPLED PROGRESS VERIFIED.**
Separate actual-evidence review passed744 checks. This closes the exact default
app load/retained-heap observation, not P2 physical acceptance or a human gate.

One run, `app-default-e820c0e1-run01`, used ADB board2629958581 and software
commit `9b4afcb22823ce48cb20cb4cb951cd55229ac1f2`. The user reported the board
connected alone. Default startup, MATCH0, MOTORS_ALLOWED0 and all optional setup
grants stayed unchanged. Existing native EN LOW/zero-PWM/timer setup was explicit
in the run review; no sensor/UART grant or nonzero motor request was introduced.

The fresh checked build `10f172276dcb46edab7c991b8cf03e3f` reproduced source
`e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69`,
ELF `8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257`
and ZSK `c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5`.
Each image file is176048 bytes. The compiler's low-memory warning is retained;
its static arithmetic is not used as a stack-space measurement.

The guarded upload returned0 once at04:32:09 Asia/Dubai. One passive capture
then ran for422.776532 seconds on the board's monotonic clock, returned0 and
reported CAPTURED/PRESENT/RUNNING_COUNTER_ADVANCED, with no collection or sample
format errors. Host and board wall clocks are separate instruments. The ordinary
uploader's flash/reset operation belongs to that one upload; no subsequent reset,
restore, retry, MCU write or extra MCU observation occurred.

## Actual observations

| Field | First sample | Second sample |
|---|---:|---:|
| Runtime phase / fault | RUNNING / NONE | RUNNING / NONE |
| Runtime epochs |212505|292059|
| Missed releases, stored counter |0|0|
| Maximum execution, stored MCU-clock us |513|513|
| Initialization complete |false|false|
| Transaction phase / fault |ACQUIRING / NONE|ACQUIRING / NONE|
| Free payload in262144-byte LLEXT pool |4500 bytes|4500 bytes|
| Largest free payload |4364 bytes|4364 bytes|
| Used payload / allocator overhead |257512 /132 bytes|257512 /132 bytes|

The epoch counter advanced79554. Initialization remains false with the optional
sources ungranted; this is expected restricted operation, not match readiness.
`raw_lines=true` denotes raw-line mode, not a physical line reading. Both
Transaction prefixes preserve live intermediate/stale combinations; they are
not coherent completed-transaction receipts. No sampled known Runtime or
Transaction fault was reported. This does not establish absence of every
transient fault or reset throughout the entire capture.

Both complete loader flash sweeps match the pinned loader ELF's PT_LOAD bytes;
both complete sketch sweeps match the pinned ZSK. One resident sketch node at
0x200138e4 references BSS/Runtime0x200299e0. Exact list/node/descriptor brackets
and allocation containment pass. The two pool payload snapshots differ, while
canonical allocator metadata agrees exactly. Post-load free payload does not
measure the historical eight-byte modeled loader margin, stack headroom or total
system RAM. Stored513us is not full-source800us WCET or calibrated timing.

Actual capture scope:58 memory reads,62 commands and1,404,304 requested bytes;
the single-node case is below the reviewed maximum62/66/1,405,088 plan. All child
commands completed within their at-most30-second bounds. The fixed600-second
collector limit was preserved. The capture ran only the four approved metadata
commands and read-only MEM-AP dumps; no UART, service or motion command was added.

## Evidence and review

`P2_app_default_probe_raw/` retains:

- `actual_build_receipt/` and `actual_build_archive.json`:20 checked-build files.
- `run01_upload_attempt.json`, `run01_upload_outcome.json`, `preparations/`:
  durable once-only claim, actual upload status, five exact prelaunch Git checks.
- `run01_capture_attempt.json`, `run01_execution_outcome.json`, stdout/stderr:
  one coordinator sequence, actual status and complete capture JSON.
- `actual_capture/` and `run01_file_archive.json`:183 original files,
  1,809,179 bytes, all independently rehashed. Copying these existing Linux files
  performed no additional MCU access. The one mid-run directory metadata check
  likewise read filenames only and made no readiness or success claim.
- `actual_summary.json`: concise literal samples and declared limits.
- `actual_reviewer/audit1.json`: first-run744-check offline audit, including a
  separate literal heap walk/prefix decoding as well as unchanged pure helpers.

The actual review is `state/reviews/P2_app_default_actual_review.md`, verdict
PASS_SCOPED_ACTUAL_LOAD_PROGRESS_AND_RETAINED_HEAP_REVIEW, with no open material
finding. It continued the separate fresh-context guard review using the same
model; it is not cross-model review or a human phase gate. Software host evidence
is separately detailed in `P2_app_default_probe_validation.md`.

The two reviewer preparation failures are preserved: a WSL read-only Git diff
timeout, then a Windows test-reader encoding mismatch. The approved correction
only made that fixture read explicitly UTF-8; all five coordinator probes then
passed. No production, locked test or expected behavior was changed.

## Current board and next task

The app remains loaded and may continue its inhibited native ticks. This was a
finite observation of a nonterminal app. Both upload and capture claims are
consumed: do not rerun the coordinator, reset or restore under this approval.
Firmware/config/grants and existing tests remain unchanged; no tuning occurred.

P2 remains active. Full sensor/button calibration, native dump ownership/framing
and delivery, stack/full live-source timing, powered B4/B7 tests and assembled
robot acceptance remain open. No PINMAP, STAND/RING, EXPLAINED OK or GATE Pn PASS
was inferred. The next unfinished distinct scope is the native-dump prerequisite
work described in `P2_native_dump_prerequisite_followup.md`: complete holder
visibility and supported quiescence/cancel/reopen evidence before any grant.
Its existing read-only audit does not authorize a privilege or UART operation.
Otherwise resume the named P2 physical benches when the relevant setup becomes
available; do not repeat an already consumed bare-board experiment as a substitute.
