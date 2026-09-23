# Native dump cadence audit and bounded D117 proposal

2026-09-24. Separate reused same-model source review. No board, MCU, service,
UART, implementation or test operation. Only this analysis file was written.
The calculations below are source-derived bounds, not measured throughput.

## Decision

The current FIFO-disabled UnoQDumpPort cannot deliver a complete 5001-frame
recording within DUMP_TOTAL_MS=300000 at one native call per 1 ms epoch under
the pinned nominal-clock assumptions. This is a concrete cadence/capacity
blocker, not merely a missing measurement. A fast fake sink cannot close it.

D116 can still proceed as the full-length host composition and compile-only
bench: actual Transaction, STOP/tail, guarded synthetic reset, real menu and
Transfer, exact receiver roundtrip, and an explicit slow-progress TOTAL failure.
Its native successful-transfer acceptance remains blocked. Do not shorten the
recording, lengthen the timeout, or silently multiply Transfer calls per epoch.

The reviewed D116 contract 912434c45bda6d71900f2dc624f12f19197c3071efcd74f9f567857dcb7e3d19
and public header b43ed24532254ae829f991da55a3081ae654fbe0fbc399497e8b7a6c5a9cf62e
resolve the earlier cleanup, actual A, closing-C deadline and reset-release
chronology findings. This is contract preflight, not approval of future code.

## Pinned code and minimum-byte proof

Reviewed working-file SHA-256 values:

| File | SHA-256 |
|---|---|
| src/hal/dump_uart_unoq.cpp | 6dfaca493024d49d67497f2708ffb51e848447148423b82b4bbb3c10c250d2f3 |
| src/hal/recorder_csv.cpp | 779b1e2609ddb4aadfd1624dabf7c0607039e99a395a3b2abc2c1aa4558318c2 |
| src/hal/recorder_dump.cpp | 222193fd96c9dfa1c15437785879fb154c8e9a9ee6ff20291824ce72f338f058 |
| src/config.h | 7246cee85413b4981c0d3c66c9e61d637ff7b1db42c7e93834bb67206043be85 |
| pinned uart_stm32.c | 144bc137f5a193d8dac508fa21d47aa92deeae1f64da11663e027714d5607bfb |
| pinned stm32u5xx_ll_lpuart.h | 6ef9bf504ddd453112b69b977fe3d6b0ae7e5be4638219e5f30a60e85cbc6247 |

`recorder_csv.cpp:153-177` emits 17 numeric fields, 17 commas, 50 raw-hex
characters (25-byte frame), and one newline. `recorder_dump.cpp:247-263` adds
`FR,<session>,`. Give every numeric field and session just one digit, except
the actual ordinal 0..5000. This intentionally understates real timestamps,
session, voltage, flags, and other values. Minimum frame-line length is therefore
`89 + digits(ordinal)`, between 90 and 93 bytes. Exact Python integer arithmetic:

```
sum(len(str(i)) for i in range(5001)) = 18894
frame_payload_min = 89*5001 + 18894 = 463983 bytes
packet_count_min = 2*5001 = 10002
frame_wire_min = 463983 + 15*10002 = 614013 bytes
```

Every row exceeds 64 bytes. Transfer makes at most one native write per step
and never combines the remainder of one row with the next (`recorder_dump.cpp:298-331`).
The actual native adapter adds exactly 15 bytes to each offered slice, including
short slices (`dump_uart_unoq.cpp:23-27,225-246`). Headers, summary, events and END
add further bytes. The exact forthcoming D116 output must still be counted;
the estimate of roughly 680 kB is not an observed artifact used in this proof.

The native code explicitly requires installed `fifo_enable=false`, uses
CR1=UE|TE, rechecks that exact value, and breaks immediately on TXE low. Its
8-iteration ceiling is not an eight-byte throughput guarantee. Every store is
inside the unchanged <80 us step budget (`dump_uart_unoq.cpp:21,57,166,195,250-291`).
At nominal 115200 baud, 8N1 consumes 10 bits/byte: 86.8056 us per character.
FIFO-off TDR plus the shift register can accept at most two new bytes during
one successful <80 us call. Even ideal two-byte progress at every 1 kHz call
gives only 600000 bytes in 300 s, below the frames-only minimum 614013. Endpoint
rounding of one or a few scheduler slots cannot repair the 14013-byte deficit.
The optimistic aggregate lower bound is 307.0065 seconds, before other records
and packet completion overhead.

The current port also waits for actual TC in a later bounded call before it
returns the payload count; it cannot start the next packet in that same call.
For the deliberately minimal 90..93-byte rows and an ideal two-store call,
`sum(ceil(79/2)+ceil((15+line_length-64)/2)+2)` is 319964 calls, about 319.964 s.
This is a stronger ideal periodic model, not a physical timing result. Actual
TXE sampling may permit only one store, making delivery slower.

## Primary hardware support and limits

The cached publisher RM0456 Rev 6 PDF was rehashed locally:
`build/cache/RM0456_Rev6_52152e41.pdf`, 73439635 bytes,
SHA-256 52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616.
Its prior retrieval receipt is `P2_dump_raw/native_impl_sources/rm_receipt.json`.

RM0456 table 686 (p2848) gives LPUART an eight-entry FIFO. Sections 67.4.5/6
(p2854) describe FIFOEN and TDR queuing. ISR bit7 is TXE when disabled and TXFNF
when enabled; FIFO-mode writes require room (p2892/2895). TC is completion,
not merely room. UE=0 stops output and discards current operations (p2882);
32-bit register accesses are required (p2876). FIFO flushing cannot recall
shifted bytes. [RM0456 publisher copy](https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf)

The pinned U5 LL header supplies finite FIFO enable/read, TXE/TXFNF-read and
TDR-write primitives at lines551-580,1655-1665,2477-2487. The pinned SoC header
aliases USART_ISR_TXE and USART_ISR_TXE_TXFNF to bit7. The installed Zephyr
driver enables FIFO only when its immutable config requests it; this config
does not. `uart_fifo_fill()` remains an ISR-only public API and is unsuitable
for this Thread owner (`P2_dump_raw/native/sources/edk/zephyr/include/zephyr/drivers/uart.h:460`).

Do not claim that the Rev6 FIFOEN field itself states a UE=0-only restriction:
its p2876 description does not. Disabling around setup is supported by ST's
HAL implementation, which saves CR1, disables UART, sets FIFOEN and restores
CR1. Use that as a setup-sequence precedent, not an invitation to call the
HAL API or import its locking/handle machinery. [ST UART extended driver](https://raw.githubusercontent.com/STMicroelectronics/stm32u5xx-hal-driver/main/Src/stm32u5xx_hal_uart_ex.c)

The p2876 DMA footnote belongs to the preceding character-match wake-up table;
it does not require DMA for polling TX FIFO. ES0499 Rev12 section2.22 lists DMA
toggle, autonomous character-match wake-up and low clock/baud-ratio issues.
These do not require DMA/interrupts for the proposed Run-mode TX-only path;
the pinned nominal ratio is about1388.89, outside the specified 3..4 transmitter
ratio. This scoped check is not whole-device errata qualification.
[ES0499 Rev12](https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf)

## Smallest proposed D117 change

Keep UnoQDumpPort and its existing protocol/buffers. Add one explicit setup-only
buffering selection, defaulting to legacy single-buffer mode, with a FIFO8
selection at the named recorder bench binding. Do not alter existing Runtime
binding implicitly. Default legacy tests retain their current meaning; add
independent FIFO-specific oracles rather than rewriting their expectations.

1. Validate the selection and existing four grants before callbacks. Preserve
   once-only attempt, lifetime singleton, native context/clock/pad/IRQ/config
   checks and the existing unbounded `device_init` setup qualification.
2. After the unchanged installed-init register checks, configure FIFO only in
   setup, before any packet: disable under proved ownership, verify the actual
   disabled state, enable the explicitly selected UE|TE|FIFOEN state, and check
   actual readback/acknowledgement with a fixed poll/deadline bound. Define failed
   partial-setup cleanup and poison explicitly; do not silently leave enabled
   hardware or invoke device_init again. No mode switch after setup.
3. Keep immutable installed metadata expecting FIFO-off; separately compare
   live CR1 against the selected owned mode. This deliberate post-init register
   configuration does not rewrite Zephyr device metadata. Preserve CR2/CR3,
   baud, prescaler, saved clocks, RX-off, IRQ-off and DMA-off requirements.
4. Retain at most8 stores and <80 us per call, immediate PENDING on full FIFO,
   the100 ms packet deadline, ready/ownership checks before each store, and
   actual TC before payload progress. No wait-for-space or between-epoch pump.
5. Preserve immediate owned UE=0 cancellation, actual disable readback and
   permanent poison. Treat queued/shifted bytes and remote decoder state
   honestly. Do not add a TXFRQ wait or treat TXFNF/TC after disable as a flush
   acknowledgement. Lost ownership must still prevent foreign register writes.

## Full allowed-capacity bound, not only the synthetic scenario

Use all5001 frame slots and4096 event slots, a20-digit uint64 session, and
maximum decimal widths of every encoded field. This deliberately combines
field maxima even when their simultaneous values are not attainable, so it
is a conservative upper bound on legal rows. Ordinals need at most4 digits.
The17 numeric FR widths, in formatter order, are:

```
[1,4,1,10,2,1,2,3,11,6,6,6,4,4,5,3,5] ->74 numeric characters
FR length <=24 prefix +74 numeric +17 commas +50 rawhex +1 LF =166
ER length <=24 prefix +(1+4+10+3+3+5) +6 commas +16 rawhex +1 LF =73
```

For ER this even permits a3-digit event type although the current legal enum
fits one digit. `core/types.h` bounds state0..11 and mode1..6; the frame's
signed widths follow the actual int32/int16/int8 decodes and unsigned widths
follow uint32/uint16/uint8 storage. PackStatus and schema are single digits.
The six remaining records are BEGIN,SH,SR,FH,EH,END. Each is conservatively
bounded by1151 characters from MAX_WIRE_LINE_BYTES, larger than needed for
their actual formats. No row is compressed or omitted.

For a row of length L split into payload chunks p<=64, define the model call
bound `C_b(L)=sum(ceil((p+15)/b)+1)`. Here b is the effective successful stores
per full-space call, and +1 conservatively reserves the separate TC-observation
call for every packet. At regular1 ms service, an8-entry FIFO drains its8
characters in about694.44 us at the nominal baud. This model assumes the
checks/stores fit their80 us budget, readiness/ownership remain valid, and the
drained capacity is available; it is not a proof of those physical conditions.

| Effective stores b | FR calls | ER calls | Other-line bound | Full calls |
|---|---:|---:|---:|---:|
|8|30|15|198|212658|
|7|35|18|234|250167|
|6|40|20|269|283574|
|5|46|23|306|326090|

Thus `5001*30 +4096*15 +6*198 =212658` calls, about212.658 s, covers the full
allowed capacities in the8-store model. Its associated conservative wire-byte
bound is1485625. A6-store model still fits at283.574 s; a5-store model's
conservative bound exceeds300 s. A64-byte payload packet has79 wire bytes,
so even the6-store model requires only15 calls including TC, below the100 ms
packet and2000 ms progress-stall limits. Six is a sufficient service assumption
for this conservative whole-stream model, not a newly adopted config value.

No alternate scheduler, IRQ/DMA service, timeout change or shorter log is
required by the byte-capacity calculation. D117 must test a serial-time/FIFO-depth
reference model (including real packet boundaries and separate TC), not only
an always-high TXFNF fixture. It must establish bounded setup, overflow refusal,
ownership/readiness loss, cancellation and every unchanged byte/time cap.
The actual serialized rows/events, retained slow-sink failure, target code/import
audit and later authorized on-board timing/receiver evidence remain required.
The maximum8-store loop does not guarantee even6 stores before80 us; source
and measured WCET/service-rate evidence must address that separately.

Source retrieval qualifications: direct web access to the74 MB publisher PDF and
the alternate ST PDF URL returned tool errors; the rehashed cached primary PDF
was used for the cited pages. ST HAL source and current ES0499 were accessible.
Exploratory PowerShell wildcard `rg` paths were corrected to literal directories;
these read failures did not affect source hashes or arithmetic. No artifacts
were treated as a measurement or silently repaired.

## Selected D117 public seam and exact compatibility scope

Root accepted this direction on2026-09-24; it is a proposal awaiting its own
contract, independent tests, implementation and review. Add a public buffering
enum to the existing UnoQDumpPort header, a defaulted legacy constructor, and an
explicit passive inline constexpr constructor selecting FIFO8. The private
selection is immutable by contract, checked during the once-only begin before
native I/O; construction itself never validates hardware or grants authority.
Preserve the exact existing `begin(const SetupGrant&)` signature and the four
SetupGrant booleans. Retain `app::DumpPort` and `app::unoQDumpPort(owner)` unchanged.

The minimal production file list is exactly:

1. `src/hal/dump_uart_unoq.h`: enum, passive constructors, private selection.
2. `src/hal/dump_uart_unoq.cpp`: selected setup/live-register expectations and
   bounded FIFO behavior, with legacy default behavior preserved.
3. `src/app/app.ino`: construct its existing native owner explicitly with FIFO8.
4. `bench/recorder/recorder.ino`: make the same explicit owner selection.

The two sketches retain every currently false/empty grant and disabled flag.
No change is needed to Runtime, Transfer, factory callbacks, config, framing,
readiness authority, source ownership or setup-grant layout. Factory construction
continues to call only the passive `owner.port()`. Target layout must be measured
again; a private mode byte is not assumed to fit padding.

This is preferable to replacing begin with a defaulted second parameter: that
changes its symbol and breaks existing method definitions. Retaining the old
begin plus adding an overload and a new factory thunk in the existing factory
translation unit also introduces a new unresolved reference in the untouched
D101 factory probe, which defines only the old native begin/ready/port methods.
Avoid adding another translation unit or adapter solely to work around that
linkage. Appending policy to SetupGrant unnecessarily mixes buffering choice
with its four ownership assertions and changes its public aggregate layout.

Exact inspected compatibility evidence:
`state/reviews/P2_app_dump_review_raw/factory_probe.cpp` supplies the three old
method definitions and193 checks against the actual factory. The existing
`tests/tooling/test_dump_uart_unoq.py`11 methods compile the real native owner
with `tests/fixtures/dump_uart_native/cases.cc`; that fixture already includes
FIFOEN and the TXE/TXFNF alias but expects legacy register behavior and rejects
immutable installed metadata with fifo_enable=true. None of those expectations
should be rewritten to make FIFO mode pass.

Keep those native normal/sanitizer tests and factory probe unchanged. Retain
the Runtime dump/control/service suites and D116 full-length receiver roundtrip
and slow-progress TOTAL refusal. Add independent FIFO-specific cases for passive
construction, invalid enum, one-shot setup and exact register/readback/acknowledgement
ordering, partial-setup failure, real eight-entry capacity and serial-time drain,
TC-only acknowledgement, unchanged8/80us/100ms bounds, ownership/readiness loss,
permanent poison and no foreign writes. Count actual sketch startup calls to
prove both explicit FIFO selections remain inactive with current false grants.
Compile and inspect recorder default plus app default/MATCH artifacts, including
actual constructor paths, hooks, imports, object layout and ordered loader fit.
No physical permission or successful UART delivery follows from these checks.

## D116 retained host-stream accounting

The independent D116 full-length host experiment now supplies actual bytes to
replace the earlier approximate nominal example. Recounting the preserved
`author/run1_commands/normal_exports_1790205416118983952/positive.wire`
under `P2_recorder_transport_raw` gives532562 payload bytes,5015 complete lines
and10027 payload chunks. SHA256 is
`420b4657c0a13d813ca66e29d6217c406de4d13befd8f7584b625724e9dfdfef`.
The source retains5001 frames and eight events. Applying the unchanged15-byte
packet overhead gives682967 wire bytes, or2.2765567 bytes per1ms decision over
300 seconds. Even an optimistic two stores every call would need at least
341484 calls before separate packet-completion observations.

Applying the same per-packet `ceil((payload+15)/b)+1` model to these exact chunks
gives354852 calls for b2 and99267 for b8. Intermediate b5/b6/b7 results are
150154/130252/114307. Evidence and the independently recomputed counts are in
`P2_recorder_transport_raw/reviewer/actual_host_wire_accounting.json`.
These are source-stream arithmetic and ideal service models, not measured UART
delivery rates. This eight-event example does not replace the full4096-event
capacity bound above. Neither result waives80us,100ms or300s limits or establishes
that the native port can achieve the assumed number of stores.

## D117 public-preflight correction: unrestricted retained raw bytes

2026-09-24. The independent public-oracle preflight found that D073 frameRow
accepts arbitrary25-byte FrameBytes when PackStatus is known. The earlier166-byte
FR bound above assumed semantic-valid state/mode/line values; it is retained as
that narrower model, not a universal bound over all formatter inputs. This does
not change the preceding FIFO-off lower-bound impossibility argument.

Actual `src/hal/recorder_csv.cpp:153-177` validates PackStatus only and prints
bytes4/5/6 directly as unsigned values. Their widths are therefore3/3/3, rather
than semantic-valid2/1/2: four additional characters. `recorder_csv.h:40-45` and
D073 preserve exact raw evidence; no new semantic filtering is allowed. The
revised17 numeric widths in formatter order are:

```
[1,4,1,10,3,3,3,3,11,6,6,6,4,4,5,3,5] ->78 numeric characters
FR <=24 prefix +78 numeric +17 commas +50 rawhex +1 LF =170
ER <=73 remains unchanged (its raw event/detail widths already allowed255)
```

The frame payload chunks become64,64,42, each with15 native overhead bytes.
Recomputing the original independent call-capacity formula C_b over5001 frames,
4096 events and six conservatively1151-byte remaining records gives:

| Effective stores b | FR calls | ER calls | Other-line bound | Full calls |
|---|---:|---:|---:|---:|
|8|31|15|198|217659|
|7|36|18|234|255168|
|6|41|20|269|288575|
|5|47|23|306|331091|

Total conservative wire bytes =
5001*(170+3*15)+4096*(73+2*15)+6*(1151+18*15)=1,505,629.
This is20,004 bytes and5,001 modeled calls more than the earlier166-byte bounds
at8/7/6/5 stores. The6-store model still fits below unchanged300s;5 still does not.
This correction strengthens input coverage and does not guarantee physical six
stores per80us call, actual receiver success, framing or a valid Robot attempt.

Root selected this stronger bound before D117 adoption/implementation. The draft
contract now uses170 and the revised arithmetic; the independent author and this
source context coordinated only the public field-width decomposition, not test
bodies. Python integer arithmetic was recomputed locally without executing any
production implementation. Original source-derived166-model text/results remain
above as provenance. No production source, timing, capacity, config or board changed.

Independent author confirmation: the public-only17-field widths independently
match sum78. A literal maximum-width frame row has146 bytes before the24-byte
FR/session prefix. Representative numeric fields are1,5000,2,4294967295,255,255,
255,255,-2147483648,-32768,-32768,-32768,-128,-128,65535,255,65535.
Neither context executed the formatter to derive this correction.
