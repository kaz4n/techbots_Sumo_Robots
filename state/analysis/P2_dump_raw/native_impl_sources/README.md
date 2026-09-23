# Native dump implementation source followup

2026-09-23. Source and offline-document evidence only. This new directory leaves
prior audit receipts unchanged. receipt.json records the Linux ADB read-only
fetch program, exit 0, original paths and hashes for nine installed files.
cached_copy_receipt.json records the previously retrieved private UART header.
No MCU attachment, upload, reset, peripheral operation or daemon operation.

Variant includes.txt:8 adds `llext-edk/include/zephyr/drivers`, so the private
UART header is included with `<serial/uart_stm32.h>`. Lines 13-15 include the
STM32 SoC headers, drivers/include and common_ll/include. Actual static config
and API evidence remain in ../native/offline_gdb.txt.

In modules/hal/stm32/stm32cube/stm32u5xx/drivers/include:

- stm32u5xx_ll_lpuart.h:488-490 computes rounded BRR with a 64-bit intermediate.
 160 MHz, prescaler DIV1 and 115200 baud give 355556 (0x56CE4). This is conditional
 arithmetic, not measured baud or clock qualification.
- Lines 520-537 document UE disable stopping outputs/prescaler immediately and
 discarding current operations; ISR resets and configuration remains. Waiting
 for TC after disabling TE and before disabling UE avoids line errors. Immediate
 poisoned abort does not promise an intact final UART character.
- Lines 1855-1864 implement TC clear through ICR.TCCF; lines 2477-2487 write an
 8-bit value using the 32-bit TDR register.
- Lines 2544-2557 describe TXFRQ as FIFO flush when FIFO is enabled. They do not
 establish FIFO-off discard or acknowledgement behavior.

rm_receipt.json verifies the cached 74 MB RM0456 Rev 6 PDF against the prior
publisher hash 52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616,
retaining its URL and exact page text hashes. Relevant printed/PDF pages:

- p2876: peripheral registers require 32-bit word accesses.
- p2882: UE=0 immediately stops prescalers/outputs, discards operations and resets
 ISR. The DMA channel must already be disabled. This supports abort with permanent
 poison, not clean wire completion or application transition timing proof.
- p2888: BRR is at least 0x300 and 20 bits wide; write only while UE=0. Kernel
 clock must lie between 3 and 4096 times the baud rate.
- p2889: TXFRQ is explicitly used when FIFO mode is enabled. There is no promise
 of a FIFO-off flush acknowledgement.
- p2895: with FIFO off, TXE reports transfer from TDR to the shift register; it
 does not report transmission completion. TC reports the last data leaving the
 shift register and is cleared by a TDR write or ICR.TCCF.
- p2897: writing ICR.TCCF clears TC. It does not flush any byte.

Recommended implementation implication: with default FIFO off, disable UE/TE,
check that they read back disabled, and latch permanent transport poison. Do not
call TXE a flush acknowledgement or treat TC observed after disabling UE as proof
that a packet completed. An extra TXFRQ request is unnecessary and has no newly
proved benefit here. A native TX-complete check must observe TC while the owned
UART remains enabled, after the last TDR write.
