# P0 loader identity analysis — 2026-09-22

The first timing capture correctly stopped after its full loader comparison.
No RAM was interpreted. The comparison used the packaged raw BIN, whereas the
installed upload workflow uses the ELF. These two package artifacts differ at
one section-alignment byte. The captured byte matches the uploaded ELF's
file-backed PT_LOAD data exactly; the BIN fills that gap with 0xFF.

This worker performed only installed-file/source reads, offline ELF inspection,
and analysis of the already captured dump. No new MCU read, reset, write, upload,
or OpenOCD operation was performed.

## Exact mapping

Coordinator evidence: P0_loader_difference_20260922.json reports 263,680 bytes
in each image, exactly one difference at raw offset0x3f8bf (260287), actual0x00
versus packaged BIN0xFF.

| Item | Value |
|---|---|
| MCU flash address | 0x08000000 + 0x3f8bf = 0x0803f8bf |
| Containing PT_LOAD physical start | 0x0803f474 |
| Offset within that segment | 0x44b |
| Segment virtual start | 0x20000000 |
| Corresponding virtual position | 0x2000044b |
| Segment ELF file offset | 0x3f5b0 |
| Corresponding ELF file byte | 0x3f9fb (260603) |
| ELF / captured / packaged BIN byte | 0x00 / 0x00 / 0xFF |

Installed readelf -lSW and nm -n -S show:

- datas: VMA0x20000000, ELF offset0x3f5b0, size0x44b.
- Last object there: dac_stm32_data_0 at0x20000449, size2.
- __data_end:0x2000044b.
- sw_isr_table: VMA0x2000044c, ELF offset0x3f9fc, size0x390.
- Thus the differing byte belongs to no allocated output section or object,
  but it is included in the file-backed PT_LOAD segment. It must still be
  compared when verifying that actual upload representation.

Direct od reads at those precise offsets returned 00, FF and 00 respectively.
The coordinator independently parsed the ELF and confirmed the same mapping.

## Why the installed workflow expects the ELF byte

The installed CORE is
/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0.

- boards.txt:92 selects zephyr-{build.variant}.elf as unoq.bootloader.file.
- platform.txt:197 makes that the loader upload artifact.
- platform.txt:323 passes loader and sketch artifacts to remoteocd in that order.
- variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg:15 calls
  flash verify_image on filename0 with format autodetection; line17 writes
  filename0 only if verification fails. The sketch is separately forced to BIN
  at0x08100000 by lines20–22.
- flash_bootloader.cfg:9–10 likewise verifies/writes filename0 as an image.
- The actual run reports OpenOCD0.12.0+dev-ge6a2c12f4. We did not execute its
  verification command during this investigation.

OpenOCD's published image reader recognizes ELF magic and forms image sections
from nonempty PT_LOAD entries using physical addresses and file sizes. This
explains why ELF segment padding is part of its image rather than being
replaced with a section-gap fill byte. The exact installed commit was not
available from the public upstream short-hash URL; this source is corroborating
format evidence, while installed artifact selection and actual byte comparison
are directly observed. [OpenOCD image reader](https://github.com/openocd-org/openocd/blob/master/src/target/image.c)

Installed loader config line1800 and generated autoconf line573 set
CONFIG_BUILD_GAP_FILL_PATTERN=0xFF; BUILD_OUTPUT_BIN is enabled. Zephyr documents
this setting as the output-file gap pattern and raw binaries as gap-filled.
This supports the observed package representation difference. No historical
package build log was available, so the exact producing objcopy invocation is
not claimed as observed. [Zephyr build gap-fill configuration](https://github.com/zephyrproject-rtos/zephyr/blob/main/Kconfig.zephyr)

## Full-byte identity remedy

Keep the pinned package ELF SHA-256:
39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd.

Derive the reference image by validating and concatenating these completely
contiguous, non-overlapping, nonempty PT_LOAD file bytes in physical order:

| Physical address | ELF file offset | Length |
|---|---:|---:|
| 0x08000000 | 0x138 | 0x3f474 |
| 0x0803f474 | 0x3f5b0 | 0x1188 |
| 0x080405fc | 0x40738 | 0x4 |

Total span: [0x08000000,0x08040600), 263,680 bytes. Zero-file-size BSS/noinit/
backup-SRAM segments contribute no flash bytes. Never fill gaps, skip padding,
or accept a loader by ignoring differences. A gap, overlap, out-of-range
file-backed segment, bad header, or incomplete file must fail parsing.

Captured dump SHA-256, as independently computed by the coordinator:
e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2.

The original BIN remains package provenance and must keep its pinned hash:
6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713.
Its single-byte mismatch is recorded explicitly. It is not the runtime golden
image for this ELF-based upload workflow.

The earlier debug-contract statement that the contiguous ELF span could be
compared directly to the packaged BIN was too broad: address coverage alone did
not prove representation equality. This analysis corrects that assumption.

## Evidence and next action

Successful read-only commands included installed readelf -lSW; nm -n -S -C
restricted to the nearby RAM symbols; numbered reads of both variant flash
scripts; targeted boards/platform/config searches; and one-byte od reads from
the pinned ELF/BIN and the existing dump. Initial guessed /opt/openocd flash
script paths were absent; the installed variant paths above were then read.

Coordinator separately authorized updating only tools/p0_capture.py to add
pure loader_image(elfbytes), preserve strict full-byte verification against the
ELF-derived image, and report package BIN provenance/differences. Independent
tests/review remain required before another capture. No hardware result or
phase gate is inferred from correcting the reference representation.
