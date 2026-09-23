# Native implementation handoff (D090)

Implemented files: `src/hal/dump_uart_unoq.cpp`, private helper/state additions in
`src/hal/dump_uart_unoq.h`, and the separate strong `src/hal/loop_hook.cpp`.
Public signatures and config values are unchanged.

The native port claims one object for the firmware lifetime after explicit setup,
UART/ready-pad ownership and clean-framing grants. It rejects initialized foreign
UART devices, callbacks, invalid privileged Thread context and unexpected installed
device/config metadata. Setup alone invokes `device_init`; the installed routine's
unbounded TEACK/REACK waits remain a documented startup limitation. It configures
PG13 input/pulldown and checks status, permits LOW at setup, then uses TX-only UART
with CR2/CR3 zero and NVIC66 disabled. Runtime checks exact PRIMASK restoration,
current device/callback state, nominal clock mode, RCC snapshots, pins, registers,
IRQ state and the checked PG13 value. Each call allows at most eight TXE/store
attempts, stops on TXE LOW, checks the 80us call budget and 100ms packet deadline,
and reports payload progress only after the full packet and bounded TC observation.
No UART/RX/Bridge/Monitor/Serial runtime method is used.

Wire arithmetic correction approved by root: the fixed notification has 15 bytes
of overhead, so 64 payload bytes require 79 bytes. The immutable method prefix has
13 bytes; D9 and its one-byte length add two. Private packet storage is 79 bytes.

Cancellation permanently poisons the object, discards pending cursors and, only
under still-valid ownership/context, writes CR1=0 and checks the disabled readback.
RM0456 Rev6 p2882 and installed LL LPUART header lines520-537 document immediate
operation discard on UE=0. TXFRQ applies to FIFO mode only (p2889), so no TXFRQ is
issued and TXE is never described as a flush acknowledgement. Already transmitted
bytes and the Linux decoder's state are not repaired. No automatic recovery exists.

Source references:
- P2_dump_raw/native: exact private uart_stm32.h, generated devicetree, offline GDB
  device/data/config evidence, uart_stm32.c and packaged instruction dumps.
- P2_dump_raw/native_impl_sources/includes.txt:8 admits serial/uart_stm32.h.
- P2_dump_raw/native_impl_sources STM32 LL LPUART header:488-490 gives the 64-bit
  rounded baud formula; nominal160MHz/115200/divide1 gives BRR355556.
- P2_adc_ownership_raw/headers/stm32u5xx_ll_rcc.h and existing power.cpp support
  the checked nominal MSI/PLL clock policy. This does not close SC-AJ.
- P2_dump_raw/native_impl_sources/RM0456_p2895.txt identifies TXE/TC semantics and
  TDR-write TC clearing. The separate empty C++ hook has no platform includes.

Own checks: author_static_checks.json records source hashes, exact wire arithmetic,
nominal BRR arithmetic, and hook source isolation. Independent native tests and
whole target compilation/ELF linkage inspection belong to the root/test author;
these static checks do not replace them. Root's initial target compile succeeded,
but initial staging preceded the final nominal clock predicate and must be refreshed.

Limitations: no upload/reset/native hardware/daemon operation performed by this
worker. No setup time bound, measured clock/baud/WCET, physical Linux loss/cancel,
RAM acceptance, framing recovery, runtime ownership or phase gate is established.
Next action: run independent native tests and final exact-source target build;
inspect strong hook linkage, actual calls/imports and constructors before any run.

2026-09-23 review follow-up: tightened payload admission to exactly LF or ASCII
32..126 inclusive. NUL, CR, DEL, all other controls and high bytes now fail before
packet construction/submission. The independent native test author owns regression
execution. Initial static hashes retained in author_static_checks_initial.json;
author_static_checks.json records refreshed source hashes after this fix.
