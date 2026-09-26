# D207 saved-result retrieval preparation review

Date: 2026-09-26, Asia/Dubai. Reviewer: independent review-only agent.
Disposition: PASS for one execution of the exact file-only retrieval intent
identified below. No open material finding. Actual retrieval, decoding and
native application-result acceptance remain separate work.

This review used local file reads, hashes, JSON parsing, shell-argument parsing,
AST literal extraction and in-memory decompression/comparison only. It did not
import or execute the reader, helper, caller, interpreter or tests, and made no
device, compiler, upload, reset or MCU-read call. Only this new review is owned;
all earlier reviews and evidence remain unchanged.

## Fixed inputs

Paths below are relative to `state/analysis/P7_motor_const_run_raw/` unless
otherwise specified.

| Input | Bytes | SHA-256 |
|---|---:|---|
| `retrieval01_readonly.py` | 4330 | `c04b13aecadc1b10fa92a7c0293c7993d8ecf0cf13a140baf439998b9091a935` |
| `retrieval01_intent.json` | 22792 | `be2690956319fb1d567e56d2f2468bf8408a36c0e9dc7f3dd1a3fc937889f276` |
| `native_inert_run01/result.json` | 58692 | `860338ea10ab47c5c8cef9942fa0fa084b35ae79f0bc833fbc3b0396d0dac409` |
| `native_inert_run01/inputs.json` | 18581 | `8a85e481dc14b2f68b7ba39575689649e579af05bb14b780aa7d3a47adcca7b3` |
| `native_invocation01.json` | 1204 | `60438286944f1486edafb0252a5dfc76c439b968f17c62c265fbe74b4026d0c8` |
| Historical D201 `retrieved_inert_run01/0001-read-saved-results/intent.json`, under `P7_motor_settle_run_raw` | 21181 | `dcfda9ad1475ff3a7b634f1f5200b765447b90810dededd75e0b82e0532d40fb` |
| `state/reviews/P7_motor_const_interpreter_review.md` | 10684 | `f4fd1bc852c7a4bdeef294950397b6f6a962a11ec96f847b38c1818ff6bacbba` |
| `state/reviews/P7_motor_const_run_admission_review.md` | 9553 | `3f0357cd3e8bd5d00edd29200e75875d0f8cc2f81391fcda8bf276277d3053e2` |

All six explicit intent input records match current bytes and hashes. The
eleven scope bindings at `23c1fcf6ddb371d5e7c641bab67b78c927ac541b4090cc390942de90bd86f700`
and all 160 native input hashes also remain exact. The native input record
binds clean reviewed HEAD `676e3625830b64d99309d6d03fba05ca24ea99fe`, current
source `4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`
and run `app-motor-const-4bc3a2e6-run01`.

## Exact template projection and effects

I extracted the actual Python program and compressed-helper argument from both
intent argv arrays without executing either. The current program equals the
4330-byte local reader. Replacing precisely the historical program's second
line, the single `PINS` assignment, reproduces every current byte. The first
`EXPECTED` line, all remaining reader bytes and the full compressed helper
token are unchanged. The reader core is 1310 bytes, SHA-256
`49494df4594ab7c176145c1f3ae1bc63e9c971b0b9f1e0da3e2b60431eca4e5f`.
The decompressed helper is 33321 bytes, SHA-256
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.

The outer argv retains the fixed ADB executable, serial `2629958581`, `shell -T`
and `/usr/bin/python3 -I -B -c`. I independently recomputed 17574 Windows UTF-16
command units including NUL. The outer timeout remains 75 seconds and the
reader's alarm remains 60 seconds. There is no retry or alternate path in the
reader. The future transport must preserve its original intent, result and raw
streams under the fresh `retrieved_inert_run01/0001-read-saved-results` owner.
The local `retrieved_inert_run01` directory was absent at review time.

`EXPECTED` equals both the historical admitted identity and the current native
scope/input identity: nonroot Arduino uid/gid 1000, home `/home/arduino`, Linux
aarch64 release `6.16.7-g0dd6551ae96b`, Python 3.13.5, boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. The helper is loaded into the private
`read_only_result_helper` module after its digest check; its guarded historical
`main` is not invoked. The reader calls only identity and logical-file reads,
not the helper's other action/dispatch functions.

The operation opens a read-only, no-follow root descriptor, checks identity,
reads the fourteen literal files with exact size/hash checks, rereads all
fourteen for closing checks and checks identity again. Descriptor-relative
directory traversal refuses invalid paths/symlinks and checks directory
identities on opening and closing. Regular-file reads use no-follow/nonblocking
read-only descriptors, bounded limit-plus-one reads, matching stat/fstat
identities before and after, and exact lengths. Boot identity comes from a
bounded read of the kernel boot-id file. This is Linux saved-file retrieval;
there is no MCU address access, reset, upload, compiler, sudo or remote file
mutation in the executed call path.

## Pins independently derived from actual receipts

I reconstructed the pin list directly from the actual native result: first the
upload and capture envelopes' `remote_result_path`, `full_result_bytes` and
`full_result_sha256`, then the capture snapshot rows in original order. The
snapshot list equals read rows 7 through 18 exactly. Joining each snapshot's
fixed basename to the current capture-result parent produces precisely the
intent and AST `PINS` values. No pin derives from a historical SRAM value or
guessed future result. All fourteen paths are unique and remain beneath the
current upload/capture owners.

The native upload/capture envelopes equal their corresponding saved transport
stdout JSON. Both have `report_origin=returned`, matching run/source identities,
null first error and empty postcheck errors; both transport return codes are
zero with empty stderr. The upload status is `UPLOADED`; capture is `COLLECTED`.
The enclosing sequence is `COMPLETED`, with one upload, one capture and thirteen
recorded transports. The outer receipt records check-only zero and execute zero
at the reviewed HEAD, with execution elapsed 280.3402353 seconds.

For path expansion in the following table, `U` is
`/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-upload`
and `C` is the corresponding `app-motor-const-4bc3a2e6-run01-capture` directory.
Every listed digest is the complete fixed digest, not a prefix.

| File | Bytes | SHA-256 |
|---|---:|---|
| `U/upload_result.json` | 1903 | `c0e9d53fb5171e58412eb4515e63b1dbb0068d6a81fe5a9e68e587bcc8496a02` |
| `C/capture_result.json` | 7100 | `9b879b418ad996a371e184b107b29617ce8cad0c189b7bbbb1427e34f80a1fd0` |
| `C/07-first.trace.bin` | 2128 | `4d0b02805f5442e1ff13e49788e8b5c3c1bc187d4017362619c349eeb0e1386e` |
| `C/08-first.report.bin` | 1168 | `036bedcf262e13f3f9863b244832ee7bc60a0c8400821f957c57630dd25f3f9d` |
| `C/09-first.runtime.bin` | 600 | `90fe58fa81ac28d8e71f6e1a5735d88d7abb616e9af8b6c433d62b6a7172e8f4` |
| `C/10-first.transaction.bin` | 504 | `140c4fb57b89069864d119135812a14312ca52780d4375fd50c852151e3c67bd` |
| `C/11-first.settle.bin` | 28 | `8630eb32a862922c03f5838a966758ddcbd8817966be05139ec748581e0787d5` |
| `C/12-first.gate.bin` | 88 | `d6ae3cfc721075c591b6afb0dd1de3a58632921e9c743d0f845d971b75592e1f` |
| `C/13-second.trace.bin` | 2128 | `4d0b02805f5442e1ff13e49788e8b5c3c1bc187d4017362619c349eeb0e1386e` |
| `C/14-second.report.bin` | 1168 | `036bedcf262e13f3f9863b244832ee7bc60a0c8400821f957c57630dd25f3f9d` |
| `C/15-second.runtime.bin` | 600 | `90fe58fa81ac28d8e71f6e1a5735d88d7abb616e9af8b6c433d62b6a7172e8f4` |
| `C/16-second.transaction.bin` | 504 | `140c4fb57b89069864d119135812a14312ca52780d4375fd50c852151e3c67bd` |
| `C/17-second.settle.bin` | 28 | `8630eb32a862922c03f5838a966758ddcbd8817966be05139ec748581e0787d5` |
| `C/18-second.gate.bin` | 88 | `d6ae3cfc721075c591b6afb0dd1de3a58632921e9c743d0f845d971b75592e1f` |

The saved-file total is 18035 bytes: 9003 receipt bytes and 9032 SRAM bytes.
Each six-window sample totals 4516 bytes. Their addresses and widths match the
current accepted map: trace 536951180/2128, report 537119696/1168, runtime
537117984/600, transaction 537115448/504, SETTLE 537121768/28, gate
536953520/88. The map is 16755 bytes /
`ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709`.
The separate live-previous window remains excluded.

I independently rebuilt the complete 26-row capture plan and checked every
name, address, width and index-prefixed filename. It totals 727128 requested
bytes, with 263680-byte loader spans and 95368-byte packaged-sketch spans.
All four native flash comparison flags are true; corresponding before/after
chunk digests match. Recorded capture elapsed is 251.219285584 seconds; waits
are 30.000404480 and 2.000397122 seconds. These checks establish linkage and
collection representation, not a fresh local whole-flash comparison: the
retrieval deliberately includes no flash-chunk bodies.

## Failure boundaries and disposition

The fixed reader emits `FILE_ONLY_RESULTS_VERIFIED` only after all fourteen
initial reads, all fourteen closing rereads and the final identity check.
An absent, altered, oversized, replaced or unreadable pinned file, identity
change or timeout must fail; this review admits no repair, pin replacement,
second retrieval attempt or fresh MCU sample. A failed transport's partial raw
stdout/stderr remains evidence and is not accepted as a verified packet.

The reader does not interpret the saved native statuses and never promotes an
application outcome. Later decoding must use the actual retrieved packet hash
and the accepted current map/interpreter. Preserve original receipts, first
errors and partial-prefix status if the packet contradicts the present complete
envelope; do not coerce a failed capture to complete because some windows exist.
The corrected interpreter's DECODED/PARTIAL/REJECTED distinctions and fixed
UNPROVEN coherence remain in force. Identical declared pair hashes do not yet
constitute independently retrieved raw-byte equality or atomic publication.

The exact intent is admitted for one nonprivileged saved-file retrieval. This
PASS does not accept any observer phase, begin result, epoch count, SETTLE
remedy, HALT/inhibition result, timing benefit, WCET, physical fact or phase gate.
Those require the actual retrieved bytes and a separate actual-result review.

Final review. STOPPED WRITES after recording the external byte count and hash.
