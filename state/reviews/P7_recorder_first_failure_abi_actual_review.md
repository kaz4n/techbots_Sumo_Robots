# D233 actual file-only ABI review

FINAL PASS for the saved file-only observation and derived layout. No open
material finding. Reviewed 2026-09-27 independently from saved inputs, raw
command output, closure records and current source/Git bytes. The reviewer
performed no native action or test rerun and wrote only this report.

## Identity and evidence

Collector HEAD: `43a9ae9f1226c2659502ec6491887c7a32767a32`.
Historical compile HEAD: `ce4e69390d21d9a91231581a186be4a63213135e`.
Attempt: `07f19e32c483cebadecaa63f4d6d720f`.
Session: `572412568535289530`.
Source: `29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9`.
Owner: `state/analysis/P7_recorder_first_failure_raw/native_abi01`.

| Saved file | Bytes | SHA-256 |
| --- | ---: | --- |
| `inputs.json` | 59681 | `1b2cd25b717e3068bba5bdabd5b1ce145c564e84b152ac4557239895f72c3cd7` |
| `result.json` | 478020 | `2e0810c05cb4176983faf8fa53481019890c20e4a0f33c9c90fa024bbe3f1a0f` |
| `local_result.json` | 275 | `f4cca905a82288d95bf9327235122983b6432eafe74f080dd2c83d64b3e3f340` |
| `abi.json` | 235040 | `221717e2f45fa51a63a82def322e3c287047d9565b207ae1463142d674c0c7c2` |
| `root_closure01.json` | 1215 | `599a1d9282edfde65696fd0451a4cdbb6d0c32728cbee8e07715b03c6cd45182` |

All 156 local input pins independently match current bytes and exact collector
Git blobs. This retains the accepted 145 historical compile inputs, four closed
compile records and complete 110-file staging projection. The twelve remote
file pins recompute from those artifacts and fixed tools. In particular, the
55376-byte package remains
`b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584`.
The ELF, debug ELF, loader and TLS-source identities are bound separately.

## Actual execution and closure

The saved check-only output matches the corresponding input fields; execute
output matches local_result. Both root stderr files are empty. The sole ADB
transport uses fixed serial 2629958581, shell -T, 8781 command units and a
400-second bound. Its intent and result agree, return code is zero, and stderr
is empty. Decoding its actual compressed program reproduces the recorded
program SHA-256. Its raw stdout parses exactly to result.json.

All four saved argv arrays equal the source-derived queries: installed readelf
version, GDB version, readelf -hSWs for this recorder ELF, and offline GDB for
its debug ELF. The latter retains -nx/-nh/-batch, auto-load disabled and
may-call-functions off. Every child returned zero, was reaped, did not time
out, and kept empty stderr under the unchanged 60-second/5-second bounds.
Decoded stdout byte counts are respectively 283, 281, 94421 and 228776.

All twelve ordered remote file closing checks and board identity pass.
Identity records arduino/UID1000, expected boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, no conflicting process and the pinned
CLI hash. Local closure passes, first_error is null and transport_calls is one.
The recorded observation interval is 21:31:07.808898 to 21:31:10.630713 UTC
on 2026-09-26. Root's compact closure agrees with independent recomputation.

## Fresh layout and continuation

Reparsed all raw readelf/GDB output through the accepted strict parser and
independently reconciled the complete summary to abi.json. It contains nine
types, eleven windows, 64 fields and nine exact enum tables. No old target
address supplies a missing answer.

native_dump is 216 bytes at 536950928, wholly equal to the checked .data-copy
destination extent (source 135321464). Runner is 164192 bytes at 536951144,
inside the checked 164196-byte bss-zero interval ending at 537115340. Their
alignments are four and eight. The objects do not overlap. FailureRecord is
eight bytes/alignment one at native_dump offset205/address536951133. Its eight
one-byte fields occupy offsets0..7 in the exact source order. FailureSite and
CleanupDisposition values/widths match the D231 declarations.

The recomputed aligned, merged status ranges are (address, bytes):
(536950928,4), (536951128,16), (536951176,120), (537113272,504),
(537113856,40), (537115280,8): six ranges totaling692 bytes. All object,
window, member, scalar-width and nonoverlap checks pass.

Root may mechanically bind the accepted abi.json hash through the reviewed
--prepare-bindings path and commit the three absent-only capture bindings.
The reviewed passive caller may run only after delivery/receiver closure and
its existing clean collector-HEAD check. No extra source-review chain is
needed for those exact data bindings.

This action overlapped the receiver under the recorded D051 scheduling scope:
it observed closed files, with no MCU, UART, OpenOCD, build, upload, reset or
cleanup operation. It does not establish the currently loaded image or any
dynamic value, native failure cause, UART delivery, timing, physical evidence,
motor authority or phase gate. Full current-image comparisons and passive
snapshot acceptance remain the next separate observation.
