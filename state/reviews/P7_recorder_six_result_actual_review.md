# D238 actual passive result review

**PASS: identified passive observation, provenance and closure. D237 delivery
remains FAILED.** No material blocker found in the saved collection. The MCU
records SENT_UNCONFIRMED with no recorded native failure; this is not receiver
acceptance and does not identify the missing-envelope loss point.

Collector HEAD `d83305dafae4eb61553f1b408a984d4f972d3996` in isolated
`C:/Users/narut/AppData/Local/Temp/sumox-recorder-six-result-20260927` observed
historical compile HEAD `1b2af246cd88e6207e846ee340f8c4e46a5bb980`, attempt
`771c04943d4c4a759055d794fa4b706e`, session `8582740024591403637`, source
`289300a4be9547cd294dc1f753bbe17a429d16776c46467fec5417b1290f4ffc`.
The image is the accepted static/default MATCH=0/MOTORS_ALLOWED=0 recorder,
55376-byte package SHA256
`3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d`.
Durable evidence is MAIN `state/analysis/P7_recorder_six_result_raw/native_capture01`.
All 63 copied files, 559451 bytes, independently match the closed isolated owner.

## Provenance and collection checks

All 172 input hashes match actual files, including the fixed ADB binary and 171
files independently matched to the collector's Git blobs. Both capability
observations contain all 110 exact staged source hashes, the expected source
identity and the same 244062-byte adapter, SHA256
`17420e48ccb52cd78698a8de82090f183f7cacf4f90fe908e4c8c40b2c0fffd8`.
The adapter independently reproduces from the accepted helper and actual spec.

The fresh ABI is 235374 bytes, SHA256
`e91def801995ed67083dd01e0a433783c76c53c6556955c357ae1791afc3ba26`.
Recomputation from the saved four offline readelf/GDB command replies exactly
reproduces its layout and the mechanically bound capture spec. All four children
are reaped, return zero, have empty stderr and no timeout; all twelve closing
file checks, board-identity check and local closure pass. No old ABI addresses
substitute for this image. The native_dump object is 216 bytes within initialized
.data; runner is 164192 bytes within the validated initialized .bss interval.
The packet-start window is a fresh four-byte field at native_dump offset 160.

The actual plan contains 26 reads requesting 639504 bytes: complete 263680-byte
loader and 55376-byte sketch brackets before and after, plus two seven-range
SRAM snapshots of 696 bytes each. Every recorded name/address/length equals the
fresh plan. Both sketch hashes equal the accepted package hash. All loader
chunks have equal before/after hashes, and the source-bound collector reports
all four complete-image comparisons true. Full flash images remain at the
durable remote owner; the local packet retains their identified comparisons.

All ten transport receipts return zero with empty stderr. Exactly one capture
and one retrieval occur. The sequence is COMPLETED, capture COLLECTED, export
PASS; first_error is null, postcheck_errors, finish_errors, transport_errors,
local errors and prerequisite errors are empty. All 44 retained Git commands
return zero with empty stderr. Staging claim and dispatch closure are complete.
Retrieval identifies exactly the report and 14 raw status files, with fifteen
independent closing file checks. Every returned base64 body independently
matches its size/hash and exported local bytes. Board identities before/after
agree with target 2629958581 and boot 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8.

The capture report runs from 22:16:14.113798 to 22:19:29.085610 UTC on
2026-09-26, after the D237 receiver closed at 22:08:23.536399 UTC. The report's
elapsed interval is 194.971978 s; root's outer process closed zero in 204.585 s.
The inter-snapshot wait is 2.000393 s. Capture envelope, retrieval report,
export analysis and final diagnostics agree. Independent little-endian decoding
of all 65 fields from the raw ranges exactly reproduces both saved snapshots;
all 65 fields agree. Decode errors are empty. Coherence remains UNPROVEN because
the reads are non-atomic.

## Observed state and its limits

- Runner and Transfer both report SENT_UNCONFIRMED, failure/reason NONE.
  Transfer records 607508 bytes, 5001 frames, eight events, epoch 70 and CRC
  2865663826. Both stored session fields match the expected attempt.
- Native status is OK; initialized and attempted are true; active and poisoned
  are false. The first-failure record is eight zero bytes: site NONE, reason and
  cleanup_ownership are their NOT_INITIALIZED defaults, cleanup NOT_ATTEMPTED,
  ownership_evaluated=false, and all saved progress fields zero. There is no
  recorded native failure. cleanup_verified=false does not mean cleanup failed
  when no cleanup was attempted.
- Runner records 345350 epochs, zero missed releases, maximum completed execution
  482 us and maximum lateness 2 us. Synthetic callback enabled-EN, nonzero-PWM and
  invalid-call counters are zero. These do not qualify a physical full loop or
  motors. Transaction is IDLE, finished and timing-valid with fault NONE.
- packet_started_us=345766875 and last_poll_us=345776534 describe the last packet
  and terminal poll, separated by 9659 modular microseconds. This is a successful
  terminal state, not a retained deadline failure or an exact failing-clock sample.

The MCU byte count exceeds D237's actual retained 607448 bytes by exactly 60,
the length of the absent opening envelope. Its CRC equals the retained END CRC
and the earlier diagnostic prefix-plus-body calculation. This strengthens the
missing-envelope observation. It does not prove where loss occurred, router
registration, a stale decoder partial, or receipt of the absent bytes. Native
SENT_UNCONFIRMED is deliberately distinct from end-to-end confirmation; the
unchanged receiver's D237 BEGIN refusal remains correct.

## Principal receipt pins

- inputs.json, 19618 bytes:
  `59808b863765d9dcbbf0ef95d0e57ebf0b3ce92f01e802bf0aadd16915789f99`.
- capture_result.json, 12284 bytes:
  `aa584d4428e81a3c262ad5cdd9de2bee51850441dab84167a17b10e3e14947ae`.
- result.json, 78212 bytes:
  `df51e1e46741b97747c62c1a543d924f04650cb46c35a5dc33b8685b8cd83b34`.
- export.json, 9244 bytes:
  `67bba9d7e3795f9892651f5d040ee530cd20bc3da61f44b4f8ff312d81d8d58a`.
- final_checks.json, 55994 bytes:
  `a9ee67a32eb5bd8c1501025ef512af72ab9ffddd685f7cca0c4837ffe113e4a6`.
- Root's separate copy closure, 452 bytes:
  `7061e4998bb0e4f38bb037c35e6febb7dac5645e2f0a74bd641ba8844a3a03b7`.

No review blocker prevents root's separately identified follow-up on unchanged
accepted six-store source, after the exact stale-upload scratch cleanup and the
existing compile/upload/receiver guards. A fresh attempt/session is required;
the consumed D237 owner and its failed capture remain evidence. No decoder
restart, router change, parser relaxation, repaired acceptance or additional
source-review chain is implied. Outcome still requires its own actual receipt.

Reviewer performed local read-only evidence reconciliation and pure decoding,
no test rerun or native action, and wrote only this review. No physical acceptance,
motor permission, abort qualification or human phase gate follows.
