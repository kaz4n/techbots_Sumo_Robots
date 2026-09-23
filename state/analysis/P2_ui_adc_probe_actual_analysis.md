# D114 actual bare-board A1 acquisition: independent analysis

The original RAM bytes confirm **COMPLETE**, fault **NONE**, with **128 admitted
raw samples**, contiguous sequences1..128 and **zero missed releases**. Both
9892-byte Runner snapshots are byte-identical and pass the public structural,
source-order, timing, phase/count, decoder-shape and summary-consistency checks.
Their common SHA256 is
`3d33a0ed00c6cdfb467aefa8c2f51ee8349482fba6c15fcca201ec2f189298a6`.

The independent parser was written against the public enabled ABI before the
actual run files were opened. It imports no production capture implementation or
test code. The original snapshots were decoded before their public report and
capture fields were compared with capture.json; every field agrees. The author
is a reused separate author context, not a fresh repository or cross-model review.
No board action was performed by this analyst.

## Actual observations

| Observation | Result |
|---|---:|
| Native setup | OK, ready1, shutdown NOT_ATTEMPTED |
| Setup callback calls/measured | 1 / 1 |
| Setup S..C | 957 MCU-clock us |
| Captured raw samples | 128 |
| Raw minimum / maximum | 2061 / 3984 |
| Raw mean / median | 3133.8671875 / 3057.5 |
| Reader source interval, minimum / maximum | 54 / 60 MCU-clock us |
| Read callback S..A, minimum / maximum | 59 / 65 MCU-clock us |
| Due-poll S..C, minimum / maximum | 63 / 70 MCU-clock us |
| Actual read callbacks / measured reads | 128 / 128 |
| RUNNING poll entries / measured due polls | 51398 / 128 |
| Early NOT_DUE entries | 51270 |
| Missed releases / counter saturation / clock fault | 0 / false / false |
| First captured S through last captured C | 127466 MCU-clock us |
| Decoder qualification | 128 UNCONFIGURED |
| Decoder evidence | explicit1, contract_valid1, INVALID presence3, NONE level0, candidate mask0 |

The first record is raw2061, sequence1, S412081, native start412083, native end412143,
A412145 and C412149. The last is raw3608, sequence128, S539484, native start539487,
native end539541, A539543 and C539547. Every source/native-status is OK/valid1 with
NOT_ATTEMPTED shutdown, and every decoded raw/sequence/timestamp matches its
actual corresponding sample. The latest Report matches the final committed record.
Read/poll maxima and final values exactly match the committed records. The retained
fresh flag is false while the actual final accepted/decode-match flags remain true.

These source intervals describe the Reader's reported interval; they are not a
separate measurement of only the silicon SAR conversion. S..A includes the actual
read callback. S..C includes due-poll work through the accepted closing clock;
D112 explicitly excludes closing publication assignments after C. Setup957us is
setup timing, not a post-setup tick. None is a calibrated physical-time or full-app
800us acceptance result.

## Original-byte provenance checks

All63 files in the local transfer manifest match both their local original bytes
and the remote manifest. Collection used22 commands, all returncodes0, and18 reads
requesting587232 bytes. Its host-side collection interval was
2026-09-23T22:29:16.707337+00:00 through22:32:12.914437+00:00
(176.2070420400014 seconds); this is not the MCU acquisition duration.

The complete263680-byte loader reads before/after are identical to an independent
ELF32 PT_LOAD reconstruction of the pinned installed loader ELF, SHA256
`e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2`.
Both19840-byte sketch reads exactly match the pinned D114 ZSK package,
`567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9`.
The package loader BIN is not substituted for the ELF load image.

The list and entire196-byte node are identical before/after. One null-terminated
`sketch` node is at0x200138e4; BSS is0x2001530c with size9893. Node/list/Runner/BSS
bounds and alignment agree with the public contract. Runner offset0 places the
9892-byte snapshots at the validated BSS base. The collector reports VERIFIED;
independent byte checks substantiate these collection brackets separately from
semantic acquisition success. Identical reads remain sampled consistency, not a
claim of atomic debugger observation.

## Interpretation and limits

This is actual successful raw acquisition through the identified bare-board native
A1 path. No expected floating-input raw value, noise range or physical voltage was
specified, and none is inferred from2061..3984. All128 results are UNCONFIGURED:
INVALID presence with level NONE does **not** mean a valid release or button state.
No START, MODE, BOTH, debounce, stop gesture or connected resistor-ladder acceptance
follows from these values.

COMPLETE stops further native callbacks under the unchanged Runner contract; it
does not request ADC shutdown. Normal enabled/idle retention is the design, not a
measured shutdown state. Hardware origin/setup provenance remains bounded by the
identified image/collection and the human-reported bare UNO Q setup. Physical
acceptance remains false: no PINMAP OK, calibrated clocks, production ADC approval,
SC-A/SC-AJ closure, full-app WCET, motor/sensor result or human gate is claimed.

Evidence: `P2_ui_adc_probe_raw/actual_analysis/independent_decode.json` preserves both
full typed snapshots and errors; `captures.csv` preserves all128 rows;
`collection_crosscheck.json` binds original-byte identities;
`analysis_summary.json` records the independent result, limits and the initial
filename-only invocation correction. Originals remain untouched in actual_run01.
