# D118 default-app run01 actual evidence review

Verdict: **PASS_SCOPED_ACTUAL_LOAD_PROGRESS_AND_RETAINED_HEAP_REVIEW**.
2026-09-24. No open BLOCKER, MAJOR or MINOR finding in the reviewed actual
evidence. This is continued separate same-model review, not a human phase gate.

The exact default/MATCH0/MOTORS_ALLOWED0 app loaded and its sampled Runtime epoch
counter advanced. Both full flash comparisons and the selected resident extension
support that narrow conclusion. Native output setup remains the previously
reviewed inhibited EN LOW/zero-PWM/timer implementation; electrical outputs were
not measured by this capture. Optional grants remain false.

## Evidence and independent checks

- Consumed run `app-default-e820c0e1-run01`, ADB serial `2629958581`, software
  commit `9b4afcb22823ce48cb20cb4cb951cd55229ac1f2`. The durable upload attempt
  matches the exact run/approval/review hashes and source e820c0e1. All five saved
  prelaunch Git checks returned that commit. Current local HEAD still matched at
  this review; no further run was performed by the reviewer.
- Fresh checked build `10f172276dcb46edab7c991b8cf03e3f` reproduced the pinned
  ELF8379f152 and ZSKc60443cd. One recorded upload returned0 without timeout or
  error at00:32:09.878684Z. The ordinary uploader's flash/reset behavior was
  part of the reviewed upload; no later recovery/reset/restore is recorded.
- The coordinator records one guarded upload and one passive capture. Capture
  returned0, status CAPTURED, no top-level errors. Archived `capture.json` equals
  the coordinator's captured JSON output; its stderr file is empty.
- All **183 archived files,1,809,179 bytes**, match their independently recomputed
  SHA256/length and the archive's exact filename set. Command stdout/stderr and
  every raw memory file also match the collector's individual receipts.
- Actual scope was **58 reads,62 commands,1,404,304 requested bytes**, below the
  maximum62/66/1,405,088 purpose plan and64/80/2MiB hard ceilings. Collector
  duration was **422.7765316039986 seconds**, below600. Recorded command timeouts
  were positive and at most30 seconds. Exact metadata argv, read-only
  dump_image/shutdown argv, purpose order and literal address/extent checks pass.
- Both complete263680-byte loader flash sweeps match the pinned loader ELF's
  physical PT_LOAD bytes; both complete176048-byte sketch sweeps match the pinned
  ZSK. No prefix-only identity substitution or blind loader-BIN comparison was
  used. Exactly one resident `sketch` node was validated. List/descriptor/node
  brackets agree, and BSS, Runtime, node and prefix extents fit their validated
  used allocations in both heap snapshots.

The offline auditor completed **744 checks on its first execution**. It performs
no subprocess, network, ADB, MCU, upload or collector action. It reuses unchanged
pure identity/heap/decoder helpers and separately walks literal heap headers,
rebuilds the canonical metadata digest, checks allocation accounting and decodes
the prefix integer fields directly with little-endian struct operations.

Evidence: `state/analysis/P2_app_default_probe_raw/actual_reviewer/audit1.json`,
SHA256 `bb6b0c41df0b36a1089458dacde300c13f75cca265c4411e38cb142a5a2f542d`.
Auditor `audit_actual.py` SHA256
`c0a273802ad13674f18649f2181cf0a9819565891b4bcca1d9943e6871386e6b`.
Archive receipt SHA256
`9cfab46ecbd331ad5a0ba0739903ccddc89e158116f2959e1d203eeb1686c503`.

## Re-derived observations and limits

Both Runtime prefixes encode RUNNING/fault NONE, initialization_complete0,
service_passes0 and missed_releases0. Epochs advance **212505 to292059**. Both
retain maximum_execution_us513. Both Transaction prefixes encode ACQUIRING/
fault NONE. Their timing fields differ and contain live intermediate/stale
combinations; they are retained literally and are not interpreted as coherent
finished transactions. The strict decoder reproduces RUNNING_COUNTER_ADVANCED
and transaction_fault_sampled=false with no sample-format errors.

Both heap decodes and the independent chunk walk agree: **4500 free payload
bytes**, **4364 largest free payload bytes**,257512 used payload bytes and132
overhead bytes in the262144-byte LLEXT pool. Canonical metadata SHA256 is
`5e406fe62ebead95647f01ba3c2f580a5abbe2d67c81914bf5574c76a1135833` in both
samples. Whole pool snapshots differ because payload bytes are live; matching
allocator metadata is the supported consistency result.

These observations do not measure the historical eight-byte transient loader
margin, stack headroom, total-system free RAM, atomic state, calibrated timing,
full800us WCET, sensor/UART behavior, powered motors, pin voltages or assembled
robot acceptance. Stored513us is a sampled firmware field, not a new full timing
qualification. No PINMAP, STAND/RING or human gate is supplied.

Upload and capture attempts remain consumed. The app remains loaded and may
continue inhibited native ticks after the finite observation; this is not a
terminal firmware test. Only owned offline auditor/results and this review were
written. No implementation, established test, firmware/config/grant, live run
record, approval or prospective review was edited.
