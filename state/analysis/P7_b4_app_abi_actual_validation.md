# B4 file-only ABI observed

D215 completed once at clean commit
`a68ab59e70e496c3b48764571f7f46bc1fee5a44`. Check-only returned zero in
0.527 seconds; execute returned zero in 2.725 seconds. The single transport
ran four bounded file-inspection children. All thirteen remote closing checks
and the independent local closing check passed. No B4 upload, reset or MCU
memory read occurred.

Independent actual review is FINAL PASS:
`state/reviews/P7_b4_app_abi_actual_review.md`, 5,715 bytes,
`c7fe6fe9b0629e65548e69eb7aa66a94cbda3bf9da5f5e13baeaa18be32902b6`.
It reconciles 21 complete layouts, 135 numeric answers, 156 markers and 2,037
contiguous ELF symbol entries, plus all 166 prerequisite files against both
current bytes and the native commit. The exact transported program is 24,363
bytes; the command uses 6,981 Windows UTF-16 units including NUL.

| Observed B4 item | Bytes | Address / offset |
|---|---:|---|
| Runtime object | 166,456 | 536951136 |
| Separate motor port | 40 | 537117592 |
| AttemptRecorder | 159,200 | 536954120; Runtime offset 2984 |
| FrameBuffer | 126,300 | Within the recorder |
| EventBuffer | 32,780 | Within the recorder |
| AttemptSummary | 96 | Within the recorder |
| TransactionReport | 528 | Runtime offset 162184 |
| Stand report | 16 | TransactionReport offset 24 |
| Stand stopping flag | 1 | TransactionReport offset 40 |

The fresh layout confirms 5,001 packed 25-byte frame slots, 1,251 status bytes,
4,096 eight-byte events and four-byte native indices. The recorder window is
disjoint from the other selected Runtime windows; stand fields are validated
inside the RobotResult container. These addresses belong only to this exact
compiled B4 image, which is not the currently flashed ordinary application.

Evidence is in `P7_b4_app_compile_raw/native_abi_static01`. The ABI summary is
293,222 bytes with hash `25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc`.
Root closure `abi_native_closing02.json` is 6,509 bytes with hash
`c505a725316584594f2db23dc9cb62875102bc8f403d6d20332d1bbb80ad7949`.
The original closure remains preserved: its decimal-only size regex omitted
the Runtime symbol whose size readelf printed in hexadecimal. The corrected
inventory checks every index 0 through 2036; raw ABI evidence is unchanged.

The native owner is consumed. Next, D216 binds a pure retained-record decoder
to a map transcribed from these observed layouts. File ABI acceptance does not
establish live contents, capture coherence, recorder completion, initialized
worst-case timing, live RAM, wiring, physical tests or a human phase gate.
