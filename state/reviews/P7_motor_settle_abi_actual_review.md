# D199 actual file-only SETTLE ABI review

PASS: the single actual file-only observation and its source/artifact/tool closure are consistent, and the separate report's target ABI is now observed. No material blocker found within this ABI scope. Publication instructions, initialization instruction semantics, MCU contents and runtime failure cause remain unproved.

Separate same-model reviewer, reused context, 2026-09-26. Local read-only saved-receipt inspection and independent data parsing/hash checks only; no subject import, tests or device calls. Only this review was written. Source/host review076a9742 and scope reviewb01a4006 supply the previously accepted implementation boundaries.

## Attempt and closure

Actual reviewed HEAD is `23f0aeba788c19607a76ee20e0e43834e163ac77`; source is `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`. Check-only and execute both returned zero. The check output agrees with inputs.json, and execution output exactly equals local_result.json. Local timing is06:33:42.852687 through06:33:44.920691 UTC. One file transport used6229 command units against30000 and400 seconds; intent/result agree, transport returncode0, stderr empty. Its raw stdout parses exactly to result.json. The submitted compressed program unpacks to20828 bytes and independently hashes to the recorded `7d4d443f9856e930bc7ef07682fed4ccb1877e20f01ad33cc2b4054a3c9c1766`; the fixed absent-remote-scope guard is retained.

All143 recorded local pins and all eight fixed-scope bindings match current bytes. The12 remote pins exactly comprise D198's eight artifact files, loader/TLS source, readelf and GDB. Their13 unique closing paths, including board_identity, all PASS. Board UID1000/user arduino, CLI hash and boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 match admission; conflicts are empty. Independent local closure is PASS with no first error and transport_calls=1. The new local native_abi_static01 owner is consumed; it must not be reused.

Files below are under `state/analysis/P7_motor_settle_compile_raw/`.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| `native_abi_static01_invocation.json` |1259|`49ac7cea71ce96bec00c5e8933d2431ed6e6ba42f16c970afebb45e76fb47edd`|
| `native_abi_static01/inputs.json` |33451|`f6d101a1eb81d44f13103b62f308362cddeed9ed9053e643198979c958213611`|
| `native_abi_static01/result.json` |905572|`230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e`|
| `native_abi_static01/abi.json` |5410|`069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941`|
| `native_abi_static01/local_result.json` |275|`eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9`|

Exactly four child argv lists match preparation: readelf version, GDB version, readelf-hSWs on the current ELF and guarded GDB on its current debug ELF. Each execution.returncode is0, timed_out=false, reaped=true, with60-second deadline and5-second reap bound. Stderr is empty and every base64 byte count matches. Observed tool versions are readelf2.43.1 and GDB16.2. Readelf stdout is158956 bytes/SHA256 `4aece135bfa9e429227e0ee17c59b54db1a1bf100fdc714de0076361f7ee1e8b`; GDB stdout is504466 bytes/`bf8cf406f301898840e8ce96dc2894d15177819c36454389b8d01eb63552ef9b`, both below1MiB. GDB uses-nx/-nh/-batch, no autoload and may-call-functions off. There are223 contract expressions after its two setup expressions; no target connection, run, call or MCU memory-read command occurs.

## Independently checked target layout

Raw readelf identifies an ARM EXEC image with entry0x08100011. Section1 .text is AX at0x08100010, size0x162c8. Section5 .bss is NOBITS/WA at0x20013960, size0x29ea0/alignment8; these agree with the checked D198 artifact layout.

All23 SIZE, ALIGN and LAYOUT groups are present. Independently extracting all23 numeric sizes/alignments and all11 Runner offsets reproduces the saved summary. Every window address is Runner base plus observed offset and stays within the observed169736-byte Runner. Its unique LOCAL OBJECT row remains `_ZN12_GLOBAL__N_110diagnosticE` at0x20013960, section5, raw size0x29708. The recorded decimal normalization changes only that row; independently recomputed projected length/hash match its metadata. Raw readelf bytes remain preserved. The report_.polls unsigned-int layout block still directly precedes bool and its observed size/alignment is4/4.

The unique new row is LOCAL DEFAULT OBJECT `_ZN6motors12_GLOBAL__N_119settle_probe_reportE`, address537121768/0x2003d3e8, size28, section5. GDB observes Sample12/alignment4, Report28/alignment4 and Reason1/alignment1. Its complete half-open range is[0x2003d3e8,0x2003d404), inside the checked initialized-BSS interval[0x20013960,0x2003d408), ending four bytes before that interval's end. It is disjoint from Runner[0x20013960,0x2003d068). It is a separate object, not a Runner window.

Each of these eleven pairs is independently read from the raw numeric tags and agrees with the full new ptype blocks and saved summary:

| Type.member | Offset | Width |
|---|---:|---:|
| Sample.elapsed_us |0|4|
| Sample.poll_index |4|4|
| Sample.reason |8|1|
| Sample.fresh_mask |9|1|
| Sample.valid |10|1|
| Sample.reserved |11|1|
| Report.current |0|12|
| Report.first_failure |12|12|
| Report.has_current |24|1|
| Report.has_failure |25|1|
| Report.reserved |26|2|

All31 new tagged answers are unique and match:22 field numbers plus nine enum values. The actual reason mapping is NONE0, SUCCESS1, NULL_CONTEXT2, PRECONDITION3, INITIAL_BANK4, POLL_DEADLINE5, POLL_BANK6, FINAL_DEADLINE7, POLL_LIMIT8. Raw ptype shows an enum class with unsigned-char underlying type. Source validity masks1/2/4 were not queried or represented as target-observed values. These observations establish file ABI, not the current value of either presence flag or any sample.

## Observed function rows for subsequent entry binding

The following references come from this exact current raw symbol table, not historical addresses. Half-open code ranges clear the ARM Thumb low bit and add the observed size; both lie in current section1 .text.

| Observed complete symbol | Binding/type | Thumb value | Bytes | Code range |
|---|---|---|---:|---|
| `_ZN6motors12_GLOBAL__N_113publishSettleENS_17SettleProbeReasonEjjhh` |LOCAL FUNC DEFAULT1|0x08110d61|60|[0x08110d60,0x08110d9c)|
| `_ZN6motors8UnoQPort6settleEPv` |GLOBAL FUNC DEFAULT1|0x081115bd|292|[0x081115bc,0x081116e0)|

No storeSettleSample or settleProbeReport symbol appears in this table. Absence alone does not establish inlining, correctness or store retention. No instructions were disassembled by this ABI operation, and this review does not claim the stores reach the observed object, fields precede flags, first-failure publication is guarded, or initialization adds no constructor. Those claims require the next fixed entry/instruction observation and independent semantic review.

No firmware was compiled, uploaded or reset by this ABI attempt, and no MCU contents were read. It leaves the previously flashed-image provenance unchanged; it does not newly verify a running image. Coherent capture, internal SETTLE failure cause, repair, stack/free RAM/WCET, electrical behavior, motor authorization and human phase gates remain outside this PASS. Finalized; no further reviewer writes or operations are required for this task.
