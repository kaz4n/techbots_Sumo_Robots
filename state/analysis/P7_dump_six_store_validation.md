# D235 focused host validation

PASS, host03: 30 methods, no failures/errors/skips. The final source checkpoint
is 1b2af246cd88e6207e846ee340f8c4e46a5bb980, on base
77ee8a66efc593d34aa579a5c0625919aa8fa30c. Production changes exactly one
config literal, 8U to 6U. HAL header/cpp and all deadlines remain byte-identical.

Executed serially under WSL Ubuntu with the existing normal and ASan+UBSan
profiles: current native 12 methods / 166 fresh case processes, current FIFO
11 / 414, historical-eight selected 4 / 160, independent capacity model 1,
config positive/negative 2. Seven compile/syntax commands and 740 case
processes returned zero, with empty stderr. Their C++ assertions total
47575886. The config wrapper runs all 18 original assertions for the accepted
six and rejects only the old eight value in its negative control.

Both current C++ profiles produced identical stream outcomes:

| Stream | Payload bytes | Wire bytes | Calls | Independent checks |
|---|---:|---:|---:|---|
| Retained D116 | 532562 | 682967 | 130252 | Exact packet reassembly, expected session/epoch/origin, 5001 frames/8 events, receiver publication and CSV integrity/consistency PASS |
| Full raw capacity | 1148071 | 1496311 | 287225 | Exact packet reassembly, all 5001 frames/4096 events, raw values, row bounds and CRC |

The independent unrestricted bound remains 288575 calls for six against
300000; five needs 331091 and refuses. Observed FIFO queue maximum was five
for these host streams. None is measured target throughput. Invalid enum raw
stress rows intentionally do not claim valid Robot semantics.

Final exact archive: `P7_dump_six_store_raw/d235-host03.zip`, 554652 bytes,
SHA-256 a6706e4401c830c81629b1bafb39b5bb1843aa4552c5340aabc1c3a938ee9a5b.
Its 612 members (8902346 uncompressed bytes) were individually hashed and
read back before the WSL process exited. Member manifest and compact command
summary are alongside it. This archive is the accepted host receipt basis.

## Preserved earlier outcomes

Host01 passed config/native and all native FIFO/full-capacity assertions, but
both D116 receiver publication calls returned renameat2 EINVAL on /mnt/c.
No receiver code or assertion was changed. Archive `host01.zip`, 494868 bytes,
SHA-256 892c821adde3c078452ca912eac9bb2fb7f3afabcbf73dcb730bfcca94c01ae6,
retains all 447 members, including partial captures and error records. The
8856114 bytes of loose copies were removed only after every archive member
was verified. Its initial fixture header differed only in three inserted CRLF
line endings; host03 uses the final LF bytes required by repository attributes.

Host02 ran all 30 methods successfully with Linux RAM output, but that output
owner was absent when the next WSL invocation tried to archive it. The cause
is unproven. Its console-only receipt and failed compaction script are retained;
this run is not used as complete raw acceptance. Host03 corrected the evidence
sequence by archiving within the test process before exit. Existing fixture
cleanup released each owned build directory; no target files were touched.

## Limits and next action

Independent review must accept the current source, contract and host03 pins.
Root owns integration, its separately frozen compile-only check and any later
inhibited upload. No board action was executed here. This is a candidate for
the observed STORE_DEADLINE failure, not proof of a cure. The shared timeout
predicate still does not identify which deadline expired in D233. Cleanup
READBACK_FAILED remains open; abort behavior and its strict comparison were
not changed. Motor permission, physical acceptance and phase gates remain
unprovided.
