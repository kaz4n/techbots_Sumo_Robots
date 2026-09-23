# B8 memory follow-up: default blocked, fallback not yet selected

2026-09-23 coordinator offline analysis while independent D-070 tests were authored.
No board calls, compiler option/rate/loader changes or target allocations.

D-069's mathematical lower bound remains292794B payload at50Hz, exceeding the
installed262144B LLEXT pool before metadata/app. D-070 host sizeof owner292968B
is separately measured in P2_attempt_host_size_20260923.json; host ABI is not MCU.

The compiler label "global variables" must not be interpreted as BSS/data only.
The [pinned Arduino size tool](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/tools/zephyr-check-size/main.go)
adds all allocated ELF sections in dynamic mode, except the designated no-reloc
rodata region when configured. Program size is upload-file length, not another
RAM amount to add. Offline readelf of the cached P0 PWM/IRQ ELF yields
text22784+rodata2312+data16+bss8896+export8+init20+fini12=34048B, exactly its
recorded compile figure. Its1208B no-reloc rodata is excluded. This checks one
cached artifact, not a current target image or the installed tool executable.
Source bytes/hash are in P2_memory_offline_receipt_20260923.json. Its first
readelf invocation failed because a Windows backslash path was passed to WSL;
that exit1 receipt is retained. Reviewer caught this recording defect. Corrected
forward-slash command exits0 with complete output in
P2_memory_readelf_retry1_20260923.json. No artifact or arithmetic was changed.

Installed config previously captured in P0_irq_installed_raw_20260923/
installed_read_01.json has autoconf SHA25652178f5eefcf276720b859bdd60fc87ca
4207b0130ac1fd5ba099af74b877a0c, LLEXT_HEAP_K_HEAP, size256 and RODATA_NO_RELOC.
The [pinned buffer loader](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/include/zephyr/llext/buf_loader.h)
uses persistent storage without the writable flag. The [region loader](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/subsys/llext/llext_mem.c)
can reuse eligible read-only, relocation-free, aligned regions; other regions
need allocations. Region alignment, allocator bookkeeping, symbol/metadata
allocations and transient load peaks are separate from payload totals.

B15 explicitly permits25Hz when RAM is short. At that rate payload would be
162794B (5001*26+4096*8), a130000B reduction. Combining that hypothetical payload
with the prior P1 compiler estimate61004B leaves38346B before new owner metadata,
its code, other HAL/recorder transport, loader overhead and required headroom.
This is planning arithmetic using different images, not a target-fit or free-RAM
measurement. Do not add the P1 program-file125508B again to its RAM estimate.

Next required evidence: an explicit rate/capacity decision and scoped inert
compile-only memory probe with actual owner instantiation, exact source/binary
review and ELF section/load-budget accounting; later physical B8 must report
actual free RAM,200s/no-gap capture and full-tick timing. No such probe, rate
change, loader rebuild or hardware acceptance is adopted by this analysis.
