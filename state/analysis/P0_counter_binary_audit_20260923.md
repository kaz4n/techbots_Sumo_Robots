# P0 fixed counter — exact target binary audit, 2026-09-23

Read-only artifact inspection completed by01:49 Dubai using bundled Windows ADB and exact serial2629958581. No build, upload, MCU/debug attachment, device write, dependency or source change was performed by this worker. Owned changes: this report and the earlier installed-UART report only.
Result: **PASS for the requested scoped binary checks**, conditional on the pinned installed loader and normal-operation assumptions in P0_uart_irq_installed_20260923.md. This is not MCU execution, physical delivery, interrupt-frequency or WCET evidence, and passes no human phase gate.
Source receipt: P0_counter_target_compile_20260923.txt ends PROCESS_EXIT=0, MATCH0/MOTORS_ALLOWED0/default; source SHA75ab5a2257a6f322bc9b5c2ee9059f3e8ac6b3817eca39f03991d18e2ebda0af. CLI reports77596B program/31416B globals, not measured runtime memory headroom.

## Exact artifacts and source binding

Let `P=/home/arduino/sumox26-build/75ab5a2257a6f322bc9b5c2ee9059f3e8ac6b3817eca39f03991d18e2ebda0af/p0_matrix/artifacts/bench-default`; `E=$P/p0_matrix.ino_debug.elf`; `T=/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`.
The ELF is ET_REL: every sketch address below is a .text/.bss section-relative link value, never an assumed live MCU address. Odd function symbol values include Thumb state.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| p0_matrix.ino_debug.elf | 1812136 | 1af12c624fa5b8b42364deb319f0189d1ea94144351e5d3d8a98e02c322dc17e |
| p0_matrix.ino.elf | 77596 | cac3fac85e3dfc76cb0b41248e914788788d46f4ea5c564247227437a0036e3d |
| p0_matrix.ino.elf-zsk.bin | 77596 | 06de35038870da90a14e7259770d689438c656a5b6346c164db81209eb964939 |
| p0_matrix.ino.map | 1023305 | c3e5b8f12e5f2c8493b341dd42c664764f6e42a9695d1a46de431546e681ccb3 |

Remote staged sources and current local counterparts hash-identically: p0_matrix.ino7157066dec6885019b04be7978ac5c7cbe4cb07898356296aede8abb01e5b4d5; counter_uart.cppbe458e1fbadeeabb484bcb74e1772ba79666306d89282e7d1a53d370d0190bac; counter_packet.cppb1587c55458fd9d442b9ce70edd9c047bceeca3bf6e32953ae52449916897760; config.h2b8caf53435df104f0ccf86464b3eac8d6891d5a35deafb64094fe93a3634f8f. Map:6610–6652 assigns the inspected packet/adapter bodies to those compilation objects.
Built-in Python struct parsing compared debug versus stripped ELF: .text22648B, .rodata936B, .llext.rodata.noreloc1216B, .data12B, .init_array20B are byte-identical; .bss7780B and empty static-thread section sizes match. All runtime relocation tuples(offset,type,name,value,size,section) match: rodata174/text912/data3/exported2/init5/fini3. Debug-only relocations were excluded. Wrapped upload artifact was hashed separately; it was not executed.

## UART dispatch and bounded runtime paths

No `z_impl_uart_*`, `uart_irq_*` or `uart_fifo_*` symbol is undefined. The only emitted named UART helpers are LOCAL/.text `uart_irq_tx_disable.constprop.0`0x271d and LOCAL/.text `z_impl_uart_irq_tx_enable`0x4c91, both real table-dispatch code. In particular, no relocation depends on the loader's zero-valued weak wrapper exports. LPUART1's imported `__device_dts_ord_78` uses the real export/API table established by the installed audit.
ISR0x2754 directly loads API offsets68(update),36(ready),20(fill),48(complete). Update, ready and complete each emit CMP#1; all other values fault during an active packet, matching contract clarification2f7e1b4. fifo_fill receives size1 and its result passes to accepted(), which also requires exactly1.
Idle/stale path at0x276c–0x2780 calls only TX-disable, then restores the key; no packet acceptance, completion/refusal counter increment or new fault occurs. Active source mismatch/API failure/invalid result goes through faultLocked0x272c, setting packetFAULT, ready=false, faulted=true and disabling TX.
After36 accepted bytes, nextByte returnsfalse; next expected callback requires TC==1 and complete()==true before incrementing completed and disablingTX. This is separate from FIFO acceptance and Linux receipt. The expected successful application path is36 byte callbacks+1 TC callback; actual or stray interrupt count has not been observed.

| Live function | Save / mask / restore, .text offsets | Exit audit |
|---|---|---|
| onTransmit | MRS BASEPRI→r7 at275a; BASEPRI_MAX16 at2760; restore r7 at2800 | Idle, active success and every fault converge at2800; ISB at2804 |
| beginCounterTransport | MRS→r7 at287e; mask at2884; restore at28ae | Callback success/failure both restore; earlier init/config failures occur before lock |
| submitCounter | MRS→r6 at2908; mask at290e; restore at293c | Accepted/refused both restore; enable occurs while locked |
| serviceCounter | MRS→r4 at296c; mask at2972; restore at2994 | Not-ready, healthy and timeout/fault all restore |

All locks are inline BASEPRI save/MAX/ISB with exact saved-key restore/ISB. No SVC, heap, String, semaphore, delay, yield or Bridge call occurs inside these sections. The private fault helper relies on these locked callers. counterDiagnostics() is unused and removed from this image, so its source implementation has no live binary body to audit.
CounterPacket::submit0x2614 has finite fixed prefix-copy loops and exactly10 decimal-digit UDIV iterations. nextByte/accepted/complete/service/status0x269c–0x271a are finite branch-only paths. Remaining driver LDREX/STREX retries are the explicit conditional limitation in the installed audit; masking ordinary interrupts is observed here, not a hardware-forward-progress or masking-duration measurement.

## Startup, ownership and loop hook

setup0x00d4 calls matrixBegin, matrixSetGrayscaleBits(3), beginCounterTransport, then millis. beginCounterTransport marks attempted first; the installed deferred-init/pinctrl helper call at0x2850 is before the IRQ lock and is reachable from this setup path only. It checks helper return0, readiness, config_get success, baud115200 and packed8N1/no-flow-control0x00030100. Its locked phase disables TX/RX/errors before registering the sole callback. No subsequent configure/init retry exists in loop or ISR.
init_dev_apply_pinctrl0x4c80 delegates to init_device_with_dependencies0x4bac; the installed setup-only init may wait for hardware TEACK/REACK, as previously documented. This review does not claim bounded setup liveness. The helper's presence in unused ZephyrSerial::begin code does not add another reachable call from this sketch.
.init_array contains exactly five entries (map:7315–7321): matrix0x2590, counter0x29b4, Bridge0x4650, ZephyrSerial0x5058, C++ error-category0x5758. All were disassembled. Matrix/HCI initialization stores scalar/pointer defaults; counter constructs the fixed packet with100000us timeout. Bridge construction zeros mutex storage and started(+0x158), stores Serial2's pointer and initializes fixed Monitor storage; it does not begin it. Serial constructors0x5058 call only buffer initialization0x502c (k_sem_init and ring fields). Error-category initialization calls the no-op __cxa_atexit0x472c. None starts UART/Bridge worker threads or RPC.
main0x4aac calls empty initVariant0x4aa8, start_static_threads, setup, then loop/__loopHook. The static-thread section is size0 with equal start/end0x5878 (map:7199–7201), so its thread-create body is not entered. No SerialUSB begin or serialEventRun call appears in main. Linked serial/Bridge virtual methods exist but are not reached from the reviewed constructors/setup/loop/ISR paths.
loop0x010c calls micros→serviceCounter, millis, bounded matrix draw scheduling, and one submitCounter when periods have elapsed. It does not start any serial owner, accept input commands, or call Bridge methods. nm finds no motor/MotorGate, analogWrite, digitalWrite or pinMode symbol in this image; scoped entry/callback paths contain no motor pin/PWM write. Installed matrix and internal UART pinctrl remain their expected peripheral operations.
The actual __loopHook0x254c still calls k_yield, then k_mutex_lock(Bridge+0x38,K_FOREVER), reads started, unlocks, and conditionally update_safe. The reviewed constructor leaves started=false; there is no Bridge begin, static worker, or second caller using that mutex in this active path. Thus update_safe is not entered.
The pinned loader mutex bodies were re-read: z_impl_k_mutex_lock0x08010b48 takes lock_count==0 at0x08010b62 into fast acquisition0x08010b86–0x08010b9c; unlock0x08010c2c sees the null wait queue at0x08010c78 and clears owner/count at0x08010c68. This exact sole-caller path is nonblocking despite K_FOREVER. The library's zero-initialized mutex before explicit begin remains a version-specific upstream caveat, not a pattern endorsed for new code. k_yield scheduling and whole-loop time are not bounded by this audit.

## Commands, limitations and next action

All remote queries used board_tool.remote with SUMO_TRANSPORT=adb/SUMO_ADB_SERIAL=2629958581 and the previously recorded bundled executable; subprocesses only read public artifact files. `${T}nm -n -C "$E"`; `${T}readelf -h -SW "$E"`, `-sW`, `-rW`; `${T}objdump -drC --start-address=START --stop-address=STOP "$E"` inspected the cited ranges. Leaf commands returned0. A broad map filter initially truncated displayed output; focused follow-ups recovered the missing helper/constructor/symbol evidence. No target debugger session was opened.
Packaged loader identity remains SHA39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd; this worker did not establish currently deployed identity or relocate/load this extension. Earlier installed audit supplies driver/config hashes and assumptions. Source-side tests and fresh safety review are separate coordinator-owned evidence; this report does not replace them or erase the preserved host-test discrepancy.
Next: after the coordinator's remaining checks, use only the separately authorized inert deployment/capture workflow for these exact artifacts; observe initialization success, progressing counters, actual Linux receipt, final-TC completion and fault behavior. Timing qualification and actual hardware interrupt count remain open; no motor, P2, electrical or human gate authority follows.
