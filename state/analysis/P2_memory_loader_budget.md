# D-071 conditional loader budget for candidate25

Separate read-only explorer analysis, independently decoded ELF32/ARM/ET_REL
b1fd8678...df76:19sections,369 GLOBAL FUNC/OBJECT symbols,1export. Installed
version evidence identifies Zephyr1743741760ee; pinned source model is not an
actual candidate load. No MCU call or file edit by that explorer.

| Copied region | Payload B | Alignment | Retained allocator chunk B |
|---|---:|---:|---:|
| text |52720|8|52728|
| data |165316|8|165328|
| rodata |936|4|944|
| bss |7580|8|7592|
| exported_sym |8|4|16|
| init_array |16|4|24|
| fini_array |8|4|16|
| Total |226584| |226648|

No merged-section gaps/prepadding occur in this ELF. Given the prior documented
persistent flash base0x08100010, no-reloc rodata1573B, raw symbol table30528B,
string tables30174/161B and section headers760B meet peek alignment and need no
heap copy. The actual future load address/path must still be checked.

All instruction/data/metadata allocations share the262144B LLEXT pool under
the installed non-Harvard k_heap configuration. Separate system heap32768B and
libc's remaining-SRAM arena are not extra LLEXT capacity. Metadata requests/chunks:
extension196/200, section map152/160, temporary global-symbol table2952/2960,
export copy8/16. Initial heap metadata/footer88B. At pristine load peak:

    226648 + 200 + 160 + 2960 + 16 + 88 = 230072 B
    free chunk span = 262144 - 230072 = 32072 B
    largest allocatable payload = 32072 - 4 = 32068 B

After default temporary map/global-table cleanup:226952B consumed;35192B total
free chunk spans,35180B usable payload across separate holes; largest32068B.
Do not confuse those with the compiler35560B difference or measured free RAM.

Allocator rounding used for this exact32-bit configuration: normal request n
uses round_up(n+4,8); alignment8 retains8+round_up(n,8). Alignment requests must
also have a contiguous initial region; here maximum8 adds no larger reserve.
The262144B initial heap first reserves an8-byte footer; resulting32767 chunks
select4-byte allocation headers. Source model assumes no prior/interleaved
allocations, successful flash peeks, unchanged config and default cleanup.

Primary sources (commit1743741760ee5d2d58da50d504855d43f9f8e826):

- [llext_kheap.h](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/subsys/llext/llext_kheap.h), lines12-36: shared pool.
- [llext_load.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/subsys/llext/llext_load.c), lines111-145,420-470,620-671,854-918: metadata, spans and lifetime.
- [llext_mem.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/subsys/llext/llext_mem.c), lines64-188: copies/peeks/alignment.
- [heap.h](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/lib/heap/heap.h), lines103-121,238-266,303-306; [heap.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/lib/heap/heap.c), lines466-526,726-793: chunks, aligned allocation and initial bookkeeping.
- [mempool.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/kernel/mempool.c), lines15-52,90-114; [malloc.c](https://github.com/zephyrproject-rtos/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/lib/libc/common/source/stdlib/malloc.c), lines89-117,140-146: distinct other arenas.

Pinned source downloads/hashes are in P2_memory_validation_raw/source_receipt.json
for the four initially cached files. Other links were read by the explorer.
Constructor allocations, stack, loader fragmentation, later HAL/transport growth,
physical200s/no-gap capture and full-tick timing are NOT measured by this model.
