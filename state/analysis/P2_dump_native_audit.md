# P2 B15 bounded native dump transport audit

2026-09-23 Asia/Dubai. Read-only source, packaged ELF and Linux service inventory;
no MCU attachment, upload, reset, pin/peripheral operation or daemon operation.
AGENTS, active P2, B13/B15, F091 and D051/D070/D073-D075 were read. Today is
PLAN section3's Wednesday23September; D075 permits software work without a gate.
This report does not assign a FACT ID or amend an engineering decision.

## Result

**Do not use the installed Bridge/Monitor/ZephyrSerial methods in the tick.**
Their actual sources contain indefinite waits, dynamic allocation and Arduino
String construction. A Linux-ready precheck does not change those properties.

A concrete replacement wire path is available: bounded fixed MessagePack
`mon/write` notifications on the existing internal LPUART1 connection, received
through the existing router's TCP monitor at `127.0.0.1:7500`. It needs no RPC
registration or reset handshake. This is protocol/source feasibility, not a
working or physically qualified driver. A future adapter must own initialization,
UART/pin/IRQ exclusivity, readiness checks, cancellation, and a strong loop-hook
override. Native initialization and cancellation have the qualifications below.

Do not silently call `uart_fifo_fill()` from the control thread: its public API
explicitly declares non-ISR use undefined. Do not substitute `uart_poll_out()`:
its actual packaged instructions contain an indefinite TX-ready wait. Direct
installed STM32 register operations can express a finite nonwaiting TX step.

## Pinned evidence

All audit artifacts are under `P2_dump_raw/native/`. `sources_receipt.json` and
`native_receipt.json` preserve remote paths, exact read-only Python programs,
statuses, SHA-256 and downloaded bytes. `SHA256.json` covers all artifacts at
report creation. `numbered_excerpts.txt` supplies convenient exact source lines.

- Installed Arduino Zephyr core: `1.0.0`, Linux root
  `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0` (C below).
- Installed RouterBridge: `0.4.3`; RPClite: `0.3.1`, from
  `/home/arduino/Arduino/libraries/`. Their full `src` and library.properties
  snapshots are retained. These installed bytes take precedence over main branches.
- Installed EDK version.h: Zephyr `4.4.2-rc1`, build
  `v4.2.0-18364-g1743741760ee`. The matching primary driver is retained from
  https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/1743741760ee/drivers/serial/uart_stm32.c .
- Packaged loader ELF SHA-256:
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
  Offline GDB/objdump operate only on this file; no target/remote GDB command.
- Installed Linux `arduino-router` Debian version `0.10.0`; executable SHA-256
  `3eacd38a9c813209f6985951869105600824e4f7c54a1111a8d48ef094cc1a19`.
  Embedded build strings also say version0.10.0 and Go1.25.2. Public tag v0.10.0
  resolves to `b92ba75a62781a7b79d4bc0429a499542f939233`; matching-tag router source
  and GitHub tree are retained. No reproducible binary-to-source build was made;
  the version agreement does not prove the installed binary is unmodified.
- Cached official loader source from ArduinoCore-zephyr
  `79b3f1afdad455f55e4a25030953617152c0227c` was copied byte-for-byte with its prior
  primary retrieval receipt. Its SHA-256 is
  `0b2af678b67a21a10f211538f5c535f0f92fb3ddbf97a302ed22122665f916b8`.

Principal installed source hashes:

| File below artifact root | SHA-256 |
|---|---|
| sources/Arduino_RouterBridge/src/bridge.h | ca275c57d1865db16a24e14c901757c31fac7ada91bb09130e07dfb6b4b9febb |
| sources/Arduino_RouterBridge/src/monitor.h | d3c8940c58db82eae0064208cdee6bb8e0c4ea68ee56cf75c38ff98038d5cf9e |
| sources/Arduino_RPClite/src/decoder.h | 817328dcfb400cf89a5cedf22384f06557829a55cc659e15b6681a8641a9b2be |
| sources/core/cores/arduino/main.cpp | d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed |
| sources/core/cores/arduino/zephyrSerial.cpp | 8ec1c12e9771e3a17a9d8a0fb59b22f091262ba105c7f6e60fb6e7eaec9e689f |
| uart_stm32.c | 144bc137f5a193d8dac508fa21d47aa92deeae1f64da11663e027714d5607bfb |
| router/internal/monitorapi/monitor-api.go | 23ed289c4a4e2ffe3d09ec88b0b9ef10bca390a6b5534dd2a9a95af56ba67663 |

## Why stock calls fail the required boundary

All line references here are to the retained source files, preserving original
line numbering.

| Path | Concrete behavior |
|---|---|
| bridge.h:46-75 | RpcCall access/error methods take K_FOREVER mutexes. |
| bridge.h:82-132 | result() has unbounded write/read retry loops; destructor calls result(). |
| bridge.h:174-214 | is_started takes K_FOREVER; begin has serial wait, new transport/client/server, stack allocation/thread creation, synchronous reset call. |
| bridge.h:278-288 | notify retries a ten-millisecond mutex acquisition indefinitely; it has no bounded send deadline. |
| bridge.h:291-357 | update_safe includes ten-millisecond read locking, one-millisecond sleep and indefinite write retries; weak __loopHook yields then invokes safeUpdate. |
| monitor.h:41-85 | begin and connection checks can call synchronous RPC and use K_FOREVER mutexes. |
| monitor.h:128-150 | write first calls the blocking connection conversion, creates/grows Arduino String, then synchronous RPC or the unbounded notify. |
| Arduino_RPClite/src/decoder.h:37-57,288-298 | MsgPack Packer serialization followed by a blocking send-until-all loop. |
| Arduino_RPClite/src/SerialTransport.h:26-37 | delegates to Stream and reports requested write size; no transport deadline. |
| zephyrSerial.cpp:118-177 | availableForWrite/read/available use K_FOREVER; write retries until all bytes are stored. |
| zephyrSerial.cpp:180-187 | flush waits indefinitely for software buffer and physical completion. |

The stock call object's asynchronous-looking lifetime is especially unsuitable:
abandoning it invokes a blocking destructor. Checking `availableForWrite()` does
not repair the caller because that check itself locks indefinitely. Readiness
does not prove Linux will respond or continue to drain traffic.

## Exact internal link and ready signal

The installed overlay:390-391 assigns `arduino,router-serial=<&lpuart1>` and serial
indices USART1, LPUART1, USART3. `zephyrSerial.h:148-149` obtains the router serial
from that property; singletons.cpp:18 constructs Bridge from that object.
The path is **hardware UART**, not RPMsg, OpenAMP or mailbox transport.

Generated devicetree evidence:

- lines11881-11924: LPUART1 ordinal78, base0x46002400, IRQ66, priority0.
- lines11956-11979: clock bus168/APB3, enable mask64, reset ID4102.
- lines11992,12019-12030,12069-12072:115200baud, PG7TX/PG8RX and PG6RTS/PG5CTS
  pinctrl entries, FIFOdisabled, hardware flow control disabled.
- lines12124-12125 and overlay:269-272: **deferred-init**, so device presence does
  not mean it was initialized by boot.
- lines21031-21036: control_gpios index0 is GPIog/PG13, activehigh; GPIog ordinal94.

Offline GDB confirms config, device API, UART defaults and real nonzero exports:
device78 at0x0801c13c, device94 at0x0801bf8c. See `offline_gdb.txt` and
`uart_identity_receipt.json`. Packaged static UART user_cb/user_data are null.
These are packaged initial values, not a read of current RAM or ownership.

Installed Linux systemd service, read with `systemctl cat` only, opens
`/dev/ttyHS1` at115200 and runs `gpioset ...70=1` after router ready. Its stop
hooks lower ready and toggle MCU control lines. **Never stop/restart that service
as an innocent transport recovery operation:** its configured hooks can reset
the MCU. None of those hooks was executed by this audit.

Loader source `official_main.c:239-268` uses
`GPIO_DT_SPEC_GET_BY_IDX(DT_PATH(zephyr_user),control_gpios,0)`, configures it as
input with pulldown and waits during normal startup. Immediate bypasses that
block. A native adapter must sample that exact ready input with checked status
before using its UART path and reject LOW/error; normal boot is not a continuing
ready guarantee. The adapter must provide correct setup under Immediate or
explicitly reject that mode. No generic Bridge `isReady()` API was found.

## Exact wire protocol and receiver

RPClite decoder.h:37-57 serializes ordinary MessagePack-RPC, and SerialTransport
writes those bytes directly. There is no outer CRC, length prefix, eRPC framing,
COBS, sync word or terminator. A fixed notification is:

```
[2, "mon/write", [payload_string]]
93 02 A9 6D 6F 6E 2F 77 72 69 74 65 91 <string-length-code> <payload>
```

For n=0..31, `<string-length-code>` is A0|n; overhead14 bytes. For n=32..255 use
D9,n; overhead15 bytes. A64-byte slice therefore requires79 fixed packet bytes.
Arithmetic corrected during D090 review: the earlier narrative undercounted the
nine-byte method by one; the retained raw protocol bytes were already correct.
If an implementation always uses D9,n for0..64, MessagePack still represents the
same string and the router parser accepts it; shortest encoding is optional for
strings. The root's higher-level session/checksum protocol is distinct from this
unchecksummed wire format. Require ASCII or valid UTF8 when selecting the string
encoding. The monitor also accepts a MessagePack bin payload (C4,n), confirmed
by monitor-api.go:122-130; that option avoids UTF8 interpretation.

Router source main.go:78 defaults its monitor socket to127.0.0.1:7500; the
installed service does not override it. monitor-api.go:30-42 registers mon/write
globally before the serial link is opened. monitor-api.go:117-156 accepts one
string/bin argument and writes it to connected monitor sockets. Thus a sender
does not need Bridge.begin, $/reset, $/register or mon/connected for a notification.
A receiver must connect before the service trigger; zero clients silently loses
data while the RPC method still reports the supplied length. Notifications have
no response anyway. Native TX-complete can mean only local UART completion,
never receipt, parsing, file durability, no gaps or common-attempt provenance.

Router monitor writes may wait indefinitely with a single slow monitor client
(monitor-api.go:142-148 removes its deadline). Multiple clients have500ms write
deadlines. Neither condition may make the MCU wait. A complete file must be
validated by the host session/count/checksum policy; absence of physical flow
control does not establish no-loss delivery or make UART TX-ready a Linux ACK.

Router `msgpackrpc/connection.go:180-260` parses nested array/string lengths from
the continuous byte stream. **Abandoning a partially emitted packet poisons its
framing:** later packet bytes can be consumed as the missing string tail. There
is no reset byte. A bounded safe policy is to latch transport poison after any
partial-packet cancellation and refuse subsequent packets in that object lifetime.
Do not finish a cancelled packet during non-IDLE to repair the stream. Restarting
the MCU alone does not prove the still-running Linux decoder was reset. A future
explicit decoder reconnect/recovery protocol must be independently justified.

## Native step, setup and ownership requirements

Actual packaged functions are in individual `uart_stm32_*.txt` disassemblies:

- poll_out0x08019a2c spins on ISR bit7; unsuitable.
- fifo_fill0x080199d4 checks bit7 and has a size-bounded loop, but the public
  uart.h:461-467 contract restricts it to ISR use; do not call it from Thread.
- irq_tx_ready0x0801992e additionally requires CR1bit6/TCIE, not just data-room.
  It is not a standalone polling readiness API after interrupts are disabled.
- poll_in0x08019ac8 is finite, but also clears overrun and consumes data. A
  transmit-only service needs no RX parser; it must never dispatch motion input.
- irq_tx_disable/irq_rx_disable use LDREX/STREX retry loops. A strict instruction
  bound needs a proved exclusion policy or direct controlled register writes.
- ISR/TDR accesses in the installed driver are ISR offset0x1c, TXE bit7, TDR
  offset0x28. A checked direct TXE test followed by a single TDR byte store under
  exclusive ownership provides a finite polling primitive. Use at most a fixed
  number of attempts per call, return pending when full, and carry explicit packet
  offset. A deadline check is additional, not a replacement for an iteration cap.
- TC is ISRbit6. A complete submitted packet is not physically complete until a
  later bounded TC observation. A native status must say which it represents.

Before any register use, validate the package-derived device/config/base,
privileged Thread context, clock/setup state, relevant IRQ/DMA conditions,
readiness and exclusive ownership. Save and restore the incoming interrupt mask;
do not unconditionally enable interrupts. The full ownership rules must exclude
stock Bridge.begin/Monitor/Serial use, user callbacks, other threads and any ISR
that can write this UART. A port's own initialized flag cannot prove exclusivity.
Full R2 integration must account for bytes already in hardware when IDLE is lost:
cancelling the software buffer does not stop an already started UART character.
Do not claim zero non-IDLE wire activity from a cancelled cursor alone. Peripheral
disable/flush behavior requires an explicit tested cancellation policy.

Native setup is still an implementation obligation. LPUART1 is deferred. The
default `device_init` executes uart_stm32_init, including pinctrl and clocks, then
**unbounded TEACK/REACK waits** (uart_stm32.c:2394-2404). Its packaged init
disassembly confirms those waits. It must not be a lazy runtime operation. An
explicit setup-only use is a limitation, not a bounded-initialization proof. A
fully bounded owner must perform checked native clock/pinctrl/register setup and
poll acknowledgements using fixed budgets, or fail closed until a separately
qualified setup grant exists. This audit does not invent that implementation.

## Inherited hook and strong override

Core main.cpp:23-24 defines a weak empty C++ `__loopHook`; main.cpp:38-44 calls
loop then the hook every iteration. RouterBridge bridge.h:354-357 also defines
a weak hook, with yield and safeUpdate. Variant postvariant.h auto-includes the
RouterBridge header, explaining F091's retained Bridge machinery without an
explicit sketch include.

The prior actual D071 memory ELF remains concrete evidence: symbol
`_Z10__loopHookv` is weak, size68bytes, at0x24a4; main's relocation at0xbfe4 is
R_ARM_ABS32 against that symbol. Its disassembly takes an infinite mutex wait
and conditionally dispatches Bridge.update_safe. See existing
P2_memory_validation_raw/elf_25_symbols.txt:401,
elf_25_relocations.txt:1409, elf_25_disassembly.txt:3752-3773,18645-18657.

A strong C++ `void __loopHook()` in a **separate .cpp without Arduino.h or
bridge.h** is the supported linker-resolution candidate. Including the weak
definition and redefining it in the same translation unit is a redefinition,
not a safe override. `extern "C"` produces a different symbol and will not work.
Installed platform.txt:75-96 includes object files before the archive and creates
the dynamic artifact with GNU `-r`; a strong symbol should supersede weak ones.
That is linker reasoning until the new real target ELF proves: strong T binding,
intended finite body, and main's relocation to that exact body. Also inspect
check/debug/final ELFs and init arrays. Merely finding the function in a source
file does not resolve F091.

The retained Bridge/HCI constructors initialize storage but do not call
Bridge.begin in the inspected source/old ELF. ZephyrSerial constructors initialize
semaphores/rings. Core initVariant is weak empty in the old ELF; static thread
startup also remains. A new whole-image audit must check these paths, static
thread table and constructor calls. Suppressing the hook does not automatically
remove every platform initializer or qualify the complete schedule.

## Boundaries and next action

Native driver and hook implementation, independent host tests, actual target
compilation/relocation review, matching deployed loader, runtime ownership,
Linux-loss/cancel behavior, physical link loss, fullRAM and whole-tick WCET remain
unproved. No P2B8 acceptance or phase pass follows. Safe next action is a frozen
bounded protocol/port contract and implementation using this pinned evidence,
with the partial-packet poison and setup limits explicitly addressed.

Exploratory errors were reads only: guessed nonexistent core variant.cpp and
RouterBridge.cpp, and PowerShell rg wildcard paths, were corrected using installed
inventory paths. No missing source was silently represented as verified.
