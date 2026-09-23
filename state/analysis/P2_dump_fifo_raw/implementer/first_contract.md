# D117 proposal: explicitly selected native TX FIFO

Draft only, 2026-09-24. Root adoption, independent public-oracle freeze and source
review remain required. This document authorizes no implementation or board action.
It follows `P2_native_dump_throughput_audit.md`; D090 remains the legacy contract.

## Scope and public seam

The FIFO-off port cannot deliver even the source-derived minimum full5001-frame
stream within unchanged300s at one1kHz call under the pinned nominal baud model.
Prepare a selected FIFO mode in the existing native owner; preserve all record
bytes, capacities, timing values, service cadence, R1-R11 and current false grants.

Exactly four production files are proposed:

- `src/hal/dump_uart_unoq.h`: enum and passive constructors/private selection.
- `src/hal/dump_uart_unoq.cpp`: mode-aware setup/live ownership and cleanup.
- `src/app/app.ino`: explicitly select FIFO8 for its existing native dump owner.
- `bench/recorder/recorder.ino`: explicitly select FIFO8 for its existing owner.

No change to Runtime, Transaction, Transfer, the app factory/port, config, protocol,
installed driver/device metadata, recorder, timing or startup options. No additional
translation unit, native owner, thread, IRQ/DMA service, RX handler or pump.

Proposed public declarations in `recorder::dump`:

```cpp
enum class Buffering : std::uint8_t { LEGACY_SINGLE = 0U, FIFO8 = 1U };
// In existing UnoQDumpPort public section:
constexpr UnoQDumpPort() = default;
explicit constexpr UnoQDumpPort(Buffering buffering) : buffering_(buffering) {}
// Existing NativeStatus begin(const SetupGrant&), ready(), port(), status() unchanged.
// Private immutable selection, initialized by either passive constructor:
const Buffering buffering_ = Buffering::LEGACY_SINGLE;
```

Construction, including an invalid cast enum, performs no I/O, callback, validation,
clock read or ownership claim; initial status stays NOT_INITIALIZED. `port()` and
app::unoQDumpPort(owner) remain passive. There is no mode setter or begin overload.
Existing default construction selects the unchanged legacy branch. Both sketch
edits retain their current disabled/default setup and empty grants verbatim; an
explicit FIFO constructor is a configuration selection, never permission to begin.
The new const member's object size/offset must be measured, not assumed padding.

## First begin and legacy compatibility

Preserve existing once-only behavior: attempted/poisoned reentry follows current
abort/refusal, never reinitializes or changes mode. On a first attempt, latch the
attempt, validate the enum (unknown => INVALID_ARGUMENT), then the four grants
(missing => OWNERSHIP), before any native callback/register operation. Continue
existing context, lifetime owner, metadata, pristine-device and IRQ checks in their
current order/statuses. An invalid enum plus missing grant therefore reports
INVALID_ARGUMENT. Repeated begin retains existing poison semantics, not this
first-attempt priority.

Valid default-mode behavior, register writes/readbacks, callback order and statuses
remain D090-compatible. Immutable installed `fifo_enable` must remain false in
both modes; true metadata at the pre-init gate is still DEVICE failure. Preserve
the existing combined post-device_init gate status (OWNERSHIP), rather than globally
reclassifying every metadata failure. The requested FIFO state is a
separate post-init owned configuration, not rewritten Zephyr metadata.

Retain exclusive lifetime `uart_owner`, privileged Thread requirement, exact
PRIMASK save/restore, PG13 input/pulldown, installed device/base/config checks,
nominal/saved clocks, PG7 AF8, IRQ and RX/DMA prohibitions. No installed source
changes. The existing explicit setup `device_init` still contains unbounded
TEACK/REACK waits: neither complete begin nor FIFO setup reliability is proved
bounded on physical hardware by this change.

## FIFO-only fixed setup sequence

After existing device_init and its exact installed register checks, require the
current installed CR1=UE|TE|RE, CR2=CR3=PRESC=0, BRR=355556 and AUTOCR=0. Preserve
current IRQ-disable/clear placement after the installed checks. Before the first
additional CR1 mutation, establish the same lifetime identity, context, metadata,
device, pads, IRQ-idle, nominal clock and saved-clock/baud facts required for owned
operation. No TDR write is permitted during setup.

Perform exactly the following successful-path CR1 writes, each followed by DMB and
one immediate exact verification readback, with owned non-mode facts rechecked
before every new write. Additional read-only CR1 ownership-guard observations
are allowed; one immediate verification does not forbid those guard reads:

1. Write0; require readback0 (UE/TE/RX disabled).
2. Write TE|FIFOEN with UE still0; require that exact disabled configuration.
3. Write UE|TE|FIFOEN; require the exact selected live configuration and the normal
   ownership check, including TEACK=1, AUTOCR=0 and all retained non-mode checks.

There is no new wait loop, ACK retry, setup clock deadline or tunable. An immediate
missing TEACK fails REGISTER; delayed acknowledgement may conservatively refuse
setup. The implementation must not spin or silently retry until it becomes true.
This fixed sequence is permitted by the pinned CR1/UE/FIFOEN semantics; it is not a
claim that immediate TEACK will succeed reliably on the actual board. Root selected
this conservative behavior before test freeze rather than inventing a poll cap.

After success, keep existing ready sampling: setup may succeed with LOW, while a
GPIO error terminates; runtime sends still require a current HIGH. Do not check
TC/TXFNF as a clean-stream or remote-receiver acknowledgement at setup.

## Partial setup failure and cleanup

The failed begin return and status() queried immediately afterwards must both
retain the first actual failure reason. Later active/reentry calls preserve legacy
poison semantics and may report POISONED; this is not immutable lifetime status.
Before the first
new direct CR1 mutation, retain legacy failure behavior. After any such mutation,
a failure permanently poisons this instance even when cleanup cannot be proved.
No further setup write, reinit, rearm or mode fallback is allowed.

A setup-only cleanup must issue exactly one CR1=0/DMB/readback operation if current lifetime
identity, context, metadata/device, pads, IRQ, saved clocks, baud, CR2/CR3/PRESC and
AUTOCR are still proven owned, and CR1 equals either the exact last verified owned
state or the exact state just attempted. Its TEACK requirement is deliberately
omitted: a failed final TEACK check must not bypass inhibition merely because the
ordinary live ownership() now refuses. Earlier verified/attempted CR1 states are
limited to the exact installed state and the three states above; do not accept an
arbitrary subset/mask or assume a mismatching register is still owned.

For each new FIFO-only owned-state guard, the selected first-failure order is
CONTEXT (Thread privilege), OWNERSHIP (lifetime identity), DEVICE (metadata/device
readiness), OWNERSHIP (clocks/pads/IRQ/saved snapshots), then REGISTER (register
invariants, including AUTOCR). There is no NOT_INITIALIZED gate in this setup
guard. An immediate CR1 readback mismatch is REGISTER and is not replaced by a
later guard/cleanup failure. Preserve the first actual reason on failed begin
return. Existing earlier begin and legacy/live gates retain their original order.

If these facts are lost or CR1 has an unrecognized value, write no potentially
foreign register. In either case, retain first reason, clear pending local buffers,
permanently poison and retain the actual disabled-readback result internally. A
failed cleanup readback stays unverified and never causes another write loop.
Preserve PRIMASK on every branch. Private cleanup evidence need not add public API;
independent register traces must distinguish attempted, verified and skipped cleanup.

Ordinary runtime cancellation keeps D090's strict live-ownership prerequisite:
clear CR1 to0 once if still owned, DMB, record actual readback, always poison. Do not
weaken runtime ownership after a foreign register/clock/IRQ change. No TXFRQ, TC
wait, drain, replay or ACK invention. Queued and shifted bytes may leave a partial
MessagePack notification; UE0 cannot recall already shifted bytes or clean the
Linux continuous decoder. This change supplies no framing recovery.

## Live FIFO operation and unchanged caps

Live ownership expects exactly UE|TE for LEGACY_SINGLE and UE|TE|FIFOEN for FIFO8.
FIFO8 additionally requires AUTOCR==0 at initial setup and every live ownership
check; never repair/write AUTOCR. Nonzero AUTOCR gives REGISTER. This preserves
TC-as-whole-packet completion by excluding autonomous TDN/trigger semantics. The
legacy branch does not gain a new AUTOCR requirement or different existing oracle.
All existing CR2/CR3/PRESC/BRR/TEACK/device/clock/pad/IRQ checks remain effective.

ISR bit7 is TXE in legacy mode and TXFNF in FIFO mode. Before every TDR store,
retain existing owner, current ready and deadline admission. Stop immediately on
no room; no wait for FIFO space. Keep at most DUMP_UART_STEP_BYTES<=8 stores and
strict elapsed<DUMP_UART_STEP_US<=80 per call, the fixed packet deadline
DUMP_UART_PACKET_MS<=100, and wrapping unsigned arithmetic. Preserve existing
post-loop ownership/readiness/deadline checks. Boundaries fail at equality.

Keep the exact13-byte MessagePack prefix plus D9/count and1..64 ASCII payload:
maximum79 bytes, stable offered bytes/count while pending, exactly one pending
packet. PENDING returns count0. PROGRESS returns payload count only when all packet
bytes have been submitted and actual TC has been observed within the unchanged
checks. FIFO space/empty alone is never payload acknowledgement. Do not delay
PROGRESS artificially if actual TC is already true, but conservative throughput
models must reserve a separate completion observation. Failure remains ERROR0;
no lost/error/timeout path invents progress. Existing Transfer total300s, stall2s,
source/context/identity policy and at most one step per actual decision are unchanged.

## Independent evidence required before acceptance

Freeze separate additive FIFO tests from this public contract before executing the
implementation; implementation author must not read their bodies. Preserve every
old native11-method normal/sanitizer expectation and the actual factory probe's
three unchanged symbol definitions and193 checks. Preserve Runtime control/dump/
service checks and D116's full200s real Transaction/Transfer receiver roundtrip,
source-row comparison and slow-progress TOTAL failure. Do not rewrite legacy
register or metadata expectations to pass FIFO mode.

New cases must cover:

- Passive default/explicit/invalid constructors; unchanged factory; exact first
  enum/grant/context priority, singleton/reentry and false sketch startup behavior.
- Installed-state refusal; exact three writes/readbacks, no new ACK loop, immediate
  TEACK failure, each partial-write/readback failure, owned cleanup, foreign-state
  no-write, preserved first status/permanent poison and exact PRIMASK restoration.
- AUTOCR zero and nonzero before mutation and during live operations, including
  TDN/TRIGEN changes, refusal without any AUTOCR repair or false TC progress.
- Real eight-entry FIFO plus independent serial-time shift/drain model at nominal
  115200 8N1, full-FIFO PENDING, no overflow, exact packet bytes, pending identity,
  TC-only completion, every unchanged store/time/packet cap and wrap boundary.
- Ready/owner/clock/IRQ/context loss during each admission region, partial packets,
  cancellation after queued stores, no foreign writes and terminal no-retry.

An always-high TXFNF stub is insufficient. The independent fixture explicitly
models eight queued FIFO entries plus one separate in-flight shift byte, exact
115200 8N1 rational serial timing, and TC only after the final stop bit. This is a
fixture-model assumption, not measured board behavior or a physical throughput
claim. A character takes10,000,000/115200 microseconds (3125/36), without integer
rounding that makes the model drain early. Replay actual full D116 serialized
payload through the real native owner under the FIFO/serial-time reference model,
then verify exact decoded bytes and existing receiver result. Separately exercise
all5001 frame and4096 event slots using actual CSV formatter width limits, a20-digit
session and exact native packet boundaries; any deliberately synthetic capacity
fixture must say so and cannot claim a real Robot produced that extreme attempt.

Retain a checked conservative full-capacity bound, not only the sparse D116 run:
FR<=170 bytes, ER<=73, six remaining lines<=1151 each. D073 frameRow formats
all raw bytes, not only valid semantic enums/masks. Its17 numeric widths are
[1,4,1,10,3,3,3,3,11,6,6,6,4,4,5,3,5], sum78; FR is
24 prefix +78 numeric +17 commas +50 rawhex +1 LF =170. State/mode/line
bytes may each be255; a known PackStatus does not certify their semantic validity.
This replaces the earlier166-byte semantic-valid-only bound, retained with the
explicit correction/provenance in P2_native_dump_throughput_audit.md. For line length L split
into p<=64, C_b(L)=sum(ceil((p+15)/b)+1). At8 effective stores/call the complete
bound is217659 calls/1,505,629 wire bytes; at6 it is288575 calls, at5 it is331091.
Verify widths against actual serializers and independently recompute the arithmetic.
Demonstrate the conservative six-store complete case in the independent call-capacity
model within unchanged300s and retain slower-case refusal; do not alter native caps
or fabricate FIFO contents to force this model into the real native owner. It is
a model assumption, not a guaranteed minimum from the8-store ceiling. Real reference-model packet completion must include shift
register timing, not merely FIFO removal. Do not shorten, compress or omit records.

Compile-only recorder default and app default/MATCH require exact source/artifact
receipts, constructor/ownership paths, strong empty `__loopHook` (the inherited
empty `initVariant` may remain weak), imports, no new worker,
actual native-owner ABI/BSS and ordered loader peak/largest-region fit. Preserve
initial failures and compare final source identity. No raw-memory/layout assumption
or physical WCET/baud/drain/setup/receiver-delivery claim follows from target code.

## Pinned basis and remaining limits

Current native header SHA256 b7c654a990cd08ca7460fca6f472567e37a6ae0d90bc3ec1cb15fccf11c7f28e;
implementation6dfaca493024d49d67497f2708ffb51e848447148423b82b4bbb3c10c250d2f3.
The owned setup and live checks are in `src/hal/dump_uart_unoq.cpp:138`, `:186`;
packet/time/store/cleanup behavior in `:225`, `:250`, `:267`, `:301`.

Primary cached RM0456 Rev6 PDF is `build/cache/RM0456_Rev6_52152e41.pdf`, SHA256
52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616.
Table686/p2848 establishes eight entries;67.4.5/6/p2854 describes queuing;
CR1 FIFOEN p2876 is software-controlled without an asserted UE-only restriction;
UE p2882 states immediate discard. ISR TXFNF/TC p2892 explicitly distinguishes
TDN0 whole transmission from TDN-limited TC with FIFO data still pending.
Cached page `P2_dump_raw/native_impl_sources/RM0456_p2892.txt` SHA256
 a64b2691363c9b2bd6da2d66d6e6f3aaba110d88f71c593872ed0a7d7cff4309.

Pinned `native_impl_sources/modules/hal/stm32/stm32cube/stm32u5xx/drivers/include/stm32u5xx_ll_lpuart.h`
SHA2566ef9bf504ddd453112b69b977fe3d6b0ae7e5be4638219e5f30a60e85cbc6247:
lines515-580 expose enable/disable/FIFO readback;2635-2653 place TDN in AUTOCR.
Pinned corresponding `soc/stm32u585xx.h` SHA256
8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06
supplies FIFOEN bit29 and TXE/TXFNF bit7 aliases. Existing public substitute
`tests/fixtures/dump_uart_native/installed_uart.h:21` already declares AUTOCR;
no stub rewrite is needed merely to compile that read-only check. No test bodies
were read to prepare this proposal.

The fixed sequence is supported at register/API level; its immediate acknowledgement
success is intentionally unqualified. No remaining public choice is proposed as
silently resolved: root must adopt this draft and its exact enum/cleanup/status
clauses before independent tests/implementation. Physical framing/exclusive UART,
receiver attachment, actual8/80us service rate, complete-delivery timing, whole-tick
800us and run authorization remain separate. No board connection or action occurred.
