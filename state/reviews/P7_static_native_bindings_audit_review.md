# P7 bounded native-binding audit review

25 September2026, Asia/Dubai. Separate same-model review reusing the prior
P7 review context, with a bounded second same-model ELF/provenance inspection.
Not fresh-context, cross-model, human or runtime review. Reviewer owns only
this file. No board, debugger, objdump/readelf rerun, compiler/upload/reset,
implementation/test edits or commit; independent local JSON/hash/ELF-byte
parsing only.

## Verdict and identity

**SCOPED PASS for the enumerated file-derived bindings; no material findings.
Complete native-reference and driver API coverage remains explicitly pending.**

- `state/analysis/P7_static_native_bindings_audit.md`:
  `fe7927c425a0f7dfb0f2c520e1d1553d0400c2441fc111019b6cd1f8a7ebd77d`.
- `state/analysis/P7_static_link_probe_raw/native_bindings_audit.json`,74101B:
  `c3233593034e9446b4333f8e02bacf1fcec8b89de3d48fefd6b1406f09565804`.
- Debug ELF:
  `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.
- Final ELF:
  `5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
- Retained packaged loader binding:
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

## Independent checks

Rehashed all four direct ELF/map/linker inputs against their before/after
records, the frozen manifest and all103 project source files. Receipt records
six successful local commands with empty stderr and unchanged tool hashes.
Its two full-disassembly output hashes/sizes agree. Full discarded outputs
were not recreated for this review; retained selected bytes were independently
checked against the authoritative ELF.

Both images have identical five allocated-section records, including addresses,
sizes, file-backed hashes and BSS/NOBITS treatment. Neither has a nonempty
REL/RELA section. Independent symbol parsing finds no named undefined symbol;
the mandatory empty null entry is correctly excluded from that claim.

Independent symbol/source comparison reproduces all168 present linker-provided
NOTYPE ABS values in both images. The other three NOTYPE ABS symbols are the
stated derived bounds; the six TLS aliases remain outside this audit. Numeric
symbol presence is not presented as control-flow reachability.

Independent Thumb decoding of actual ELF bytes reproduces all22 veneer targets:
17 MOVW/MOVT/BX helpers, four PC-relative literal/BX helpers and abort's literal/
BLX call. Starts, Thumb bits and final/debug bytes agree. Each computed target
matches both its linker definition and the named retained D139 export value.
All65 cataloged text literal bytes match their ELF locations and produce28
unique values. Their union with veneers and initialized native table values
contains62 values:61 retained exports and the separately checked printk address.

All four tables' raw bytes, symbol locations/sizes, interpreted strides and
recorded first words match the debug ELF. Recomputed119 entries comprise118
named native device addresses and one null. The stored COUNT is70 and TABLE
is0x08116168, exactly the shared array. Current native_pins/motor/opponent source
supports the stated table interpretation; this is not an independent full
packaged-driver structure-layout qualification.

All1260 rendered instruction/literal bytes across the eight selected call bodies
match the ELF. Source and register-flow inspection supports the named conditional
native calls, table indexing and consumption. In particular, opponent setup
loads the device API pointer using `ldr.w fp,[r0,#8]` at0x08111772, loads slot0
using `ldr.w r3,[fp]` at0x08111784, then `blx r3` at0x08111788. The actual native
slot target is not resolved by this application's literal catalog.

## Packaged-image provenance and alias limits

The original D139 import-export JSON hash is
`a948dc53c459df625811b65ae0e350e7a7c108b20f2e21b76ffd03c9c8a1a392`.
Independent parsing of its original GDB stdout reproduces all61 exported
addresses; its successful hash command binds GDB and loader39d4a4fd. This check
did not merely trust the new summary booleans.

The original D140 loader-dispatch output hash is
`bb578bae6f83763e54eabd232b84c5af3dc92ac9dc23c197d401cea793b8b612`.
Retained installed/closing hash observations bracket that file-only dispatch
inspection and identify the same packaged loader. The recorded native calls
to instruction0x080173d4 support the remaining Thumb printk value0x080173d5.
These are retained file observations, not a fresh board or live-memory check.

Both symbol tables omit all five named allocator/random wrappers and their exact
base names. Independent aligned-word scans of allocated file-backed sections,
checked veneer targets, installed definitions and map `[!provide]` lines agree
with the note. The qualified conclusion is absence through those checked names
and encodings. No missing-definition defect or universal no-allocation result
is asserted, and such a conclusion would not follow from this evidence.

## Remaining work is not closed

No complete used-reference set, register-indirect target analysis or native
driver-slot reconstruction was established. The concrete opponent API dispatch
above and analogous HAL paths remain to be matched to the pinned packaged
image and exact structure offsets. The62-value catalog and119 table entries
must not be promoted to full coverage or measured hardware evidence.

The note preserves these limits and separates address agreement from native
semantics, reachable execution, initialization, public/driver ABI scope, runtime
RAM/stack, timing/WCET, physical acceptance, static production adoption and human
gates. This review does not supply motor-run permission or close those items.
