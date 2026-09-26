# D239 actual identified recorder delivery review

27 September 2026, Dubai. Separate Codex reviewer with reused context. Reviewed
saved native evidence and recomputed local hashes, wire/CSV content and CRC only;
no reviewer test suite, native command, upload, reset or passive capture. This
report is the sole reviewer edit for this actual-delivery scope.

**PASS: complete identified synthetic recorder delivery. No material finding.**
The received original envelope, 5001 frames, eight events and END pass with
SEALED lifecycle and NONE_REPORTED loss. Hardware acceptance remains false.

## Bound attempt and retained evidence

Native HEAD `1b2af246cd88e6207e846ee340f8c4e46a5bb980`, attempt
`354cf1586a9648d88cb9dad105a6c992`, session `3840709944287840472`, source
`3d9306d7b804a68d6e7c2764171077526fbe14074b4564ea2e071ffd5a8e839b`.
Profile is recorder.ino, static/default, MATCH=0/MOTORS_ALLOWED=0, fixed ADB
2629958581 and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.

Durable owner is
`state/analysis/P7_recorder_delivery_raw/recorder-354cf1586a9648d8`.
Independently compared all 266 original native-owner files, 3611765 bytes, with
the MAIN copies: exact equality. Rechecked the unchanged native HEAD, all 145
input hashes against both current native-worktree files and historical Git blobs,
and all 110 staged files. Compile evidence remains accepted by
`P7_recorder_repeat_compile_actual_review.md`; its 55376-byte package is
`3a1bbd2f277edb4617cafe0b4404c4753f1ad9141cb8d107cb07ed33bf24e724`.
The source is the accepted six-store recorder, with this new generated session.

The capture child is
`run/capture/20260927_023111_mode1_aade46387dca4a4d801fd6ca9202f250`.

| Evidence relative to owner/capture | Bytes | SHA256 |
|---|---:|---|
| run/result.json | 22270 | `0542e44fc7e3675121947feb949b774365db836b48372b12e4061ab92a12d8e0` |
| capture/wire.txt | 607508 | `492ac281e94c9254b0e970eed2e90a71d968b4b6a1b8a46865cb5f8daceb83bb` |
| capture/capture.json | 41183 | `4e2bbe5f72b38d76cfc7d3270d78db60532a961726f3993eefadcd03f1e3a6d8` |
| capture/manifest.json | 871 | `6fa1ce145fe847865d20a84fb9e7ed4bd8adb74ec5e4b66c2ee9a22537ef8702` |
| capture/validation.json | 1855 | `877008ff7bc6e0483a7950bb5f6475e17ca0434f6840d62761b0dfb79022b026` |
| run/receive_2/stdout | 851706 | `99a4794ca1294d5d8c352566a2b474b32f995c8be9db751d7bf0779faaf1a203` |

## Actual ordering and closure

The retained upload admission passes before reception/upload. The receive
connection is observed at 22:31:11.606118 UTC, before the single uploader starts
at 22:31:13.835788 and finishes at 22:31:24.066166 on 26 September UTC. The
receiver's claim, connection and terminal share the expected boot, ticket and
process/socket identity. Terminal END_OBSERVED at 22:37:08.391294 reports exactly
607508 bytes after 356.822542255 seconds, inside its 900-second deadline.
The outer process closed zero in the recorded 375.741 seconds. TCP connection
still does not establish router registration; the complete delivered bytes do
establish this attempt's transport result.

Upload is UPLOADED, attempts=1, child reaped/exit0/not timed out, first_error=null
and postcheck_errors=[]. The upload payload's five helper bodies exactly match
the pinned inputs; raw/package/export bindings match the checked compile
artifacts. Admission and post-run artifact/loader/layout records equal the
compile record and all three artifact postchecks pass. Closing source maps and
artifact-source identity also remain exact.

All 45 coordinator transport receipts exit zero with empty stderr and remain
within the command bound. All eleven checked child executions across compilation
and run closing are COMPLETED/reaped/exit0/not timed out. Four receiver-command
receipts are reaped/exit0 with exact raw byte lengths, empty stderr, no first or
secondary error. Final run status is DELIVERED; first_error=null, closing_errors=[]
and receiver_cleanup_errors=[]. Compile's nine closing checks remain PASS.

## Independent byte and recording checks

Decoded all 10029 retained transport base64 records and compared their complete
concatenation byte-for-byte with wire.txt. It starts with the original received
60-byte version-1 envelope for this exact session/epoch70, origin1, 25Hz,
capacities5001/4096 and counts5001/8. Every subsequent record has the expected
session; SH/SR/FH/EH each occur once, FR5001 and ER8. The single final END reports
CRC32 1933962482, exactly recomputed over all preceding wire bytes. No bytes were
inserted, repaired or discarded for acceptance.

Removing only the protocol tag/session columns reconstructs every published
summary/frame/event CSV byte exactly. Recomputed validation with the pinned
read-only validator equals saved validation.json, including raw_hex/numeric
agreement, CSV hashes/counts, format_integrity=PASS and consistency=PASS.
Manifest source, compiled HEAD, config hash and target match the admitted image;
metadata expected/observed/session are identical and rejected_session is null.

All loss fields and incomplete/overrun indicators are zero, go_seen=1, phase=3,
mode=1, frame/event counts5001/8. Frame ordinals are contiguous, pack_status zero,
both duties zero, and coverage spans 0 through 200000ms at the accepted 40ms
cadence. Summary records 194901 timed ticks and maximum315us; no frame exceeds
315us. Event types/details/values match the declared synthetic scenario, with
elapsed times 0, 0, 4500000, 5100000, 5100000, 5200001, 5202001 and 200000000us.
The countdown completion and full recording endpoint are not early.

## Evidence boundary

This closes this identified synthetic delivery attempt. It does not turn the
synthetic input stream into physical sensor evidence, establish full ordinary
application WCET/initialized RAM, grant motor permission or pass a human phase
gate. The 315us value describes recorded completed synthetic ticks. The generic
CSV report correctly keeps transport_verified/common_attempt_verified false
and declared provenance separate; the additional actual packet review above
supplies the bounded transport/attempt reconciliation. The caller's separate
framing_clean field remains UNKNOWN and is not relabeled.

The earlier D237 missing-envelope failure and D238 passive observations remain
valid historical evidence. This success proves neither the earlier loss
boundary nor a router-registration cause. No extra ABI extraction or passive MCU
capture is necessary to validate this already complete received packet.
