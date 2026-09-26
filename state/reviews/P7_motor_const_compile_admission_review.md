# D203 compile admission and fixed-scope review

26 September 2026, Asia/Dubai. Separate same-model review context, reused after
the completed D203 host review. Reviewer owns only this file. All checks below
are read-only inspection, saved-command decoding, hashing and data-only source
mapping; the reviewer made no subject import, test/compiler/device call,
cleanup or other file edit. The earlier host review remains byte-exact.

**PASS for the saved fresh read-only admission, current manifest and bounded
compile-only scope. No open material finding.** A clean committed reviewed
HEAD and successful local check-only are still required before the coordinator
uses the fresh attempt once. No new target compilation or artifacts are proved
by this preparation review.

## Reviewed evidence identities

| Evidence | Bytes | SHA256 |
|---|---:|---|
| `analysis/P7_motor_const_compile_raw/admission01.json` | 29735 | `dc082eac69bbd86a35c10636b3015580f6faf8c7553aa7833b8c033b897d5514` |
| `analysis/P7_motor_const_compile_raw/inputs_static.json` | 13559 | `1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95` |
| `analysis/P7_motor_const_compile_raw/native_scope01.json` | 2983 | `c08195d7be2d78e2de19f6a1fe75776fc38c1dab5a16daafa21801378d17d07d` |
| `reviews/P7_motor_const_compile_review.md` | 19413 | `c68852ff788e3c862e0d2c83cbbff23e9e53e69f77a4d3b4d7b3906619bcc9d1` |

All 129 current manifest hashes and all ten explicit scope lengths/hashes were
independently checked with no mismatch. The complete 196-file host input freeze
was also rechecked unchanged. The host verdict remains scoped: Linux 107 PASS;
accepted Windows 85 PASS with 22 skips covered on Linux. Its first Windows
caller FAIL and unknown cause remain preserved; neither this admission nor
the subsequent isolated suite rewrites that historical result.

## Actual admission command and observation review

The saved admission records exactly two ADB transports to serial `2629958581`,
both exit 0 with empty stderr. Their executable is the fixed local ADB binary;
its currently recomputed SHA256 remains
`e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982`.
Both argv vectors select `shell -T` and `/usr/bin/python3 -I -B -c` with the
saved program. Recorded command lengths are 12770 and 2493 UTF-16 units,
below the existing 30000-unit bound.

Independently decoding shell quoting as data shows the first program is exactly
the previously reviewed 10224-byte observer
`12794a70c417dbc2b816557a5817ee9738a55f8d8f8a88a2eb83960d50c5387d`.
The second program is byte-equal to D198 admission02's saved closing program
after precisely one `app-motor-settle-static01` to
`app-motor-const-static01` replacement. No new action or relaxed condition is
hidden in the framing. The observer retains its 45-second alarm; the closing
program retains its 60-second alarm. Both read filesystem/process/identity
information and invoke no CLI/compiler/uploader or MCU operation.

The first result's complete identity matches the observer's expected identity:
UID/GID 1000, user arduino, home `/home/arduino`, Linux
`6.16.7-g0dd6551ae96b`, aarch64, Python 3.13.5 and boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Beginning and closing identity and
credential records agree. UID/GID four-tuples and real/effective/saved triples
are all 1000; inherited file-size limits remain unlimited.

All 28 expected installed file names, hashes, regular-file modes and byte sizes
match the observer packet. Each saved identity has the complete seven fields
and the recorded size agrees with its byte count. Corrected installed-hardlink
handling remains intact: GCC/G++ have link count 2 and ld has 4, all retained
inside before/open/read/after stamp checks. This does not change the launcher's
separate one-link source-file requirement.

The first observation sees 164 processes, no conflicts and no departed-PID
ambiguity. The separate closing observation again reports no conflicts, the
same UID/user/boot, matching CLI hash and permanent UID/GID triples. The new
remote owner is absent initially, at first-program closing and in the separate
closing program. The recorded ancestry checks pass.

Resource observations are root free 2,935,283,712 bytes, home free
13,936,066,560 bytes and tmp free 1,921,687,552 bytes. The separate closing home
free count matches. MemAvailable is 3,227,119,616 bytes. Local closing free space
is 17,731,530,752 bytes. These exceed the scope's 1-GiB board and 128-MiB local
minima at observation time; they are not future guarantees or MCU free-RAM
measurements. Local pre/post records preserve all 196 pins and show both new
local owners absent.

## Current manifest and mapping review

The manifest schema is exactly `app-motor-const-static-inputs-v1`, with the
observed boot above and source digest
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`.
The reviewer independently reconstructed the exact projected REQUIRED set of
19 dependencies and enumerated the current source roots. Their union exactly
equals all 129 manifest names: no missing, extra or historical-owner substitute.
All inherited runtime dependencies retain their original hashes; derivation-only
D198 launcher/contract files are not introduced as runtime dependencies.

Independent current enumeration yields 110 source files totaling 782068 bytes.
The unchanged mapping yields 108 unique destinations totaling 781200 bytes;
every destination/hash matches `manifest_preparation01.json` and the sorted
destination-plus-NUL-plus-content digest equals the manifest digest above.
The observer sketch, its support files, canonical shared motor-fault trace
files, current app/core/HAL/config sources and settle header map as specified.
Main app.ino is not substituted for the diagnostic entry.

Comparing all source inventory pins against the historical D198 manifest finds
exactly one changed source: `src/hal/motor_port_unoq.cpp`, current 19906 bytes /
`fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b`.
This is the already reviewed D202 compile-time metadata region change. No pin,
configuration, probe header, observer entry, locked test or other firmware
source change is admitted here. The original D198 source digest `117cc0e7...`
is not adopted as the current identity.

The preparation receipt records local manifest admission only: no prepare,
claim, stage or native execution. Independent current filesystem checks confirm
`build/stage/app-motor-const-static01` and
`analysis/P7_motor_const_compile_raw/native_static01` remain absent.

## Fixed next operation and limits

The ten-file scope binds the exact launcher, contract, D197/D202 contracts and
D202 acceptance evidence, current manifest, fresh admission, host closing
receipt and immutable host review. Its profile remains
`arduino:zephyr:unoq:link_mode=static`, default startup and exactly
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`.
Attempt `app-motor-const-static01` owns the new RAW/native_static01 output,
build/stage owner and `/home/arduino/sumox26_codex_build/app-motor-const-static01`
remote owner. The diagnostic child basename remains app_motor_observe.

The allowed operation is exactly one compile-only attempt after clean reviewed
HEAD and local check-only admission, with one properties query/60 seconds and
one compiler/jobs1/720 seconds, five-second reap and all inherited source,
identity, process, artifact/package/TLS and independent final checks. Claimed,
failed, partial or uncertain ownership consumes the attempt. No retry, package
installation, source repair, upload/reset, MCU memory read or motor operation
is included. The executable rechecks prerequisites at use; this dated
read-only observation cannot replace them.

No old artifact address/layout, D199 report address or emitted helper symbol
is adopted. A successful later compilation needs separately inspected actual
artifacts and fresh file-only ABI/entry evidence. This review proves neither
target division removal nor timing benefit, failure cause, WCET, stack/RAM,
physical behavior, motor-run permission or human phase acceptance.
