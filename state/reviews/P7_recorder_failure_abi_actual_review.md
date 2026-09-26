# D230 independent actual file-only ABI review

Reviewed2026-09-27. **PASS: identified file-only ABI observation accepted.**
No material evidence or layout blocker was found. This accepts the retained
ELF/DWARF observations and the mechanically derived map, not any MCU status,
delivery success, failure cause, physical qualification or phase gate. The
reviewer performed local evidence reads only: no tests or native action.

Collector HEAD is `b90fd29162036e077f5c3bad95bac63d04364a16`;
historical compile HEAD remains `004dc7cff534896a851901f9d7d0ba6066cae060`.
Attempt `377911abefabd094971ee6d089326604`, session3997245574426120340,
source702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8,
serial2629958581 and boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 agree with
the failed D228 recorder. Both the155 local pins and their exact current bytes
match the collector Git blobs. The144 compile inputs also match the historical
Git blobs and prior compile manifest. The pinned109-entry staged manifest and
four compile records remain those accepted in the actual delivery review;
the staged-only session header is not substituted by the disabled source header.

The retained check-only reports STATIC_ABI_CHECKED. One subsequent file-only
transport returned0, with7913 command units and400s transport deadline. Its
decompressed executed program matches the recorded program SHA256
4f57aaadd5c2e8951424dbecd42e769152f06b89e9c1db05e27623cd6048736b.
The payload's12 exact remote pins and4 command arrays match inputs.json and
the observed result. The command order is readelf version, gdb version,
readelf -hSWs on recorder.ino.elf, and offline guarded GDB on its debug ELF.
The4 children each returned0, were reaped, did not time out, and retained empty
stderr. Stream lengths/base64 data agree and remain below1MiB each. The
217 distinct ordered markers represent435 expressions; all8 retained layouts,
10 windows,56 scalar fields and7 enum maps were independently reconciled to
their raw numeric/layout answers. No GDB attach/target/inferior or MCU read ran.

All12 remote file checks and the final board identity check passed in payload
order. UID1000/userarduino, expected boot, no conflicting process and the
retained file identities agree. In particular, package91b6042a, ELF a70f2e16,
debug/temp a494a29d, loader39d4a4fd and TLS68bb1476 remain the D228 artifacts.
The local closing check passed with no first error and exactly1 transport.
Outer check-only/execute and transport stderr are empty; transport stdout
decodes to the same recorded result. This establishes remote file identity,
not readback of the currently executing MCU image.

Fresh symbol and initialization evidence:

| Object | Address | Bytes | Checked interval |
| --- | --- | ---: | --- |
| native_dump | 0x20013890 | 208 | Exact .data copy destination0x20013890..0x20013960 |
| runner | 0x20013960 | 164192 | Initialized BSS0x20013960..0x2003bac4; object ends0x2003bac0 |

Native ELF section4 is writable PROGBITS .data208B, with the matching checked
copy source0x0810d670. Section5 is writable NOBITS .bss164512B; only its checked
164196B initialization interval is used. Both symbols are unique LOCAL OBJECTs,
match fresh type size/alignment, and do not overlap. native_dump is not assumed
zero-initialized. No old B4 object address or diagnostic size is reused.

The fresh10 windows merge, after explicit four-byte alignment padding, into
these6 passive-read ranges totaling684 bytes per snapshot:

| Purpose | Address | Bytes |
| --- | --- | ---: |
| Native status and alignment padding | 0x20013890 | 4 |
| Five native flags and alignment padding | 0x20013958 | 8 |
| Runner Report | 0x20013980 | 120 |
| TransactionReport | 0x2003b2b0 | 504 |
| Transfer Report | 0x2003b4f8 | 40 |
| Session | 0x2003ba88 | 8 |

Field offsets/widths lie within their fresh windows, use the declared scalar
widths and alignments, and preserve exact enum values. These are address/layout
facts only; no value at any listed address has yet been observed by this step.

Evidence lives under state/analysis/P7_recorder_failure_raw/native_abi01.
SHA256 pins:

- inputs.json (51630B): `2c213ddd53151b635e6343df35bd5e3e66d0ccdf904e1454db781080d3e94251`.
- result.json (463834B): `01686113bf27a68ad929186ca33af017390637416ca319be8ab80f2d2b4f26eb`.
- abi.json (231321B): `de0cb0ecb558937a9ad251fd81168fe340bf2440aa9ebd3108a60d7758b89ee9`.
- local_result.json (275B): `344dd1369aefc7a404739093b9e3b95fa3414fa5f82f12b988d364e4279504ae`.
- Transport intent: `62e075b3a1a4741988f04f47a42dddd376a0d38a01171d5a13b7b3d20bd22307`.
- Transport result: `8fc9818a5afdfa518b1b6db9fb1d480768373009a494225ca2d96ac5db528e39`.

This exact accepted ABI may supply mechanical data to the scoped capture spec;
it needs no additional recursive ABI review. Complete passive caller/staging/
retrieval acceptance remains separate and pending. That action must retain the
reviewed full loader/sketch flash comparisons before and after SRAM, exact
source/boot/attempt bindings, one consumed owner and all failure/closing evidence.
An empty D228 capture still does not identify the cause. No upload, reset,
receiver retry, UART access, grant/pin change or motor permission follows.
