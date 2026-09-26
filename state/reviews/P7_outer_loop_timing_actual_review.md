# D243 actual compile and target-retention review

Date: 2026-09-27. Independent reviewer: Codex reviewer. **PASS for the two
compile-only results and offline target-code/layout evidence; no open BLOCKER
in this scope.** This does not accept a five-minute runtime population, physical
WCET, live free RAM, sensor qualification, a motor run or a phase gate.

The reviewer inspected saved source mappings, receipts, ELF bytes, DWARF and ARM
disassembly. No tests, builds, board commands, uploads, resets or MCU reads were
performed by the reviewer. Only this review file was written.

## Exact source and closed compiles

Both native worktrees compiled reviewed HEAD
`ce15bb967614af54cf7f059dc541949ce754c776`, source digest
`fcb9a31adef28ca7d2f79335cc466dcc4ddb31007ff2da4341a33fb07983cace`.
All 136 input hashes match current frozen source and that HEAD's Git blobs;
all 106 staged files (783364 bytes) match their staged manifest. The additional
observer header is included in this closure. This is the accepted D243 source,
not an inferred equivalence to a previous firmware build.

| Result | Timing | Production |
|---|---|---|
| Attempt | `outer_timing01` | `outer_match01` |
| Owner under `state/analysis/` | `P7_commissioning_build_raw/commission-p4_timing-m0-5e497d4294e4` | `P7_match_static_raw/match-static-match-m1-c1c267697b5d` |
| Tuple | p4_timing, MATCH0/M0, static/default, timing enabled | MATCH1/M1, static/Immediate, timing disabled |
| FQBN | `arduino:zephyr:unoq:link_mode=static` | `arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no` |
| Outer compile elapsed | 411.576 s | 252.399 s |
| Transports | 237 | 25 |
| Package | 92480 bytes | 92092 bytes |
| Structural RAM remaining | 84112 bytes | 91280 bytes |
| Structural flash remaining | 693952 bytes | 694340 bytes |

Both results are `COMPILE_CHECKED`, first_error null, one property query and one
compiler invocation with jobs=1. All transports returned zero with empty stderr;
all nine checked remote child processes per owner completed with returncode 0,
timed_out=false and reaped=true. The nine final local/identity/inventory/source/
installed-pin/override/artifact checks passed. Artifact loader, TLS source and
file postchecks passed, with complete static ELF/TLS/body validation and no weak
undefined symbols. Compiler success is true and upload_result is empty. The
production recipes select Immediate and the accepted package flag 0x06; timing
retains the default-start package route. Neither invocation uploads firmware.

The durable timing copy contains 1001 owner files/1756389 bytes; production
contains 153 owner files/1037328 bytes. Every copied leaf matched its length and
hash. Copy closures are in `P7_outer_loop_timing_raw/native_timing01` and
`native_match01`; their SHA256 values are respectively
`08d28d31232de72efb668e5325bc37c8e91faffb072855d119a5be6dd1aa9fa8` and
`2ead5a4af4c51aa53aff15c3faf4ee6a7e13d394f758ddbef19853bd1eafc0eb`.
Original outer check/compile streams remain beside those closures.

Important artifact pins:

- Timing result: `35aaa2c97b11e2edba3ae91dc9220a61f5f4f247d14b72b4d08106ce934691bc`.
- Timing package: `176f764273a5e32511800c641db589bc71f7b48a7783aae7fc4de12d73af5552`.
- Timing final ELF: `47a6d01c58205e4d48e8c8531cea1d67b4908a49764e4265f9c6ef903342499c`.
- Timing debug ELF: `cbcc98cdb8f5fce4422224ef1643bde7885fe7bdc86bf16239eb74e66cdddd40`.
- Production result: `cdc792b2e34c296f7027f3c6ca5383008eb861df30a6c996d3da8f5507fc5b21`.
- Production package: `7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86`.
- Production final ELF: `ba9766a8a207564fa0d2bd25dd6472a16f176f09740eda4689e167e81536a666`.

The production raw binary, package, final ELF and wrapped ELF are byte-identical
to the accepted D241 owner `match-static-match-m1-1d657ca567ed`. Debug ELF/map
identity is not claimed. This independently supports absence of a production
allocated-image change; the retained-code inspection below also checks it.

## File-only inspection and retained failure history

The inspector operates on the closed ELF files only: fixed boot/serial/UID,
pinned ADB/GDB/parsers, no inferior, target connection, execution or MCU memory
command. Numeric function ranges derive from allocated executable ELF extents,
with a 16 KiB total code bound. DWARF queries use the exact debug ELF. Hash and
descriptor observations bracket final ELF, debug ELF and GDB; source, receipts,
ADB and inspector close locally. Child deadlines, kill/reap and bounded pipe
drains retain original and secondary failures. Source review corrected those
failure-retention details before execution.

`target_timing01` retains the original local Windows Python 3.13 stat/fstat ctime
refusal and exact attempted inspector. Its commands and file_observations arrays
are empty. The repair substitutes Windows birthtime in the local identity stamp;
device/inode/type/link count/size/mtime/content checks and Linux ctime checks stay
in force. The repaired inspector is preserved as `inspect_target_first_pass.py`,
SHA256 `f6b1571ad1c000a9021bc045dfb346d1bb8cdfee76e69d5c15745630230e9722`.

`target_timing02` and `target_match01` closed successfully with that inspector.
The first timing disassembly exposed an indirect literal-pool histogram call,
so its direct-call selector did not collect the 108-byte callee. This was an
evidence gap, not a firmware failure. A narrow selector addition includes that
exact ELF FUNC while keeping all bounds and remote lifecycle unchanged.
Final inspector SHA256:
`3409bf716280b0a101fc289812c425a7429d9bcc4848678daba18c91abbb6797`.
No production repeat was needed.

Final evidence under `P7_outer_loop_timing_raw/`:

- `target_timing03/summary.json`: 171374 bytes,
  `3436401eb39e3efe61d3d0318f60a0b8d38fdfb32da4c9af26cb6e89787cf4bb`.
- `target_match01/summary.json`: 66055 bytes,
  `8a397fea91fbfe3c73244876b7be40936acf914ccd3f79952c61ca7df65640bb`.

Both are `FILE_ONLY_INSPECTION_PASS`, with null first_error and no closing
errors. Timing's three GDB children and production's one child returned zero,
were reaped and had no stderr or secondary errors. All raw child streams match
the saved encoded records; transport argv/stream lengths also reconcile. All
before/after file observations agree across each complete inspection, and actual
boot/UID/eUID remain the expected boot and 1000/1000. Timing's seven local command
receipts and production's six succeeded without truncation or evidence-write
failure. Pulled final ELFs match the compile artifacts above.

## Manual target-code finding

The timing ELF contains one writable, allocated `outer_loop_timing` object at
`0x2003d430`, size 6688 and alignment 8, wholly inside the validated BSS zero
interval. DWARF independently gives Observer/Data size 6688 and alignment 8;
all/completed distributions occupy offsets 0 and 3236. Count, pending context,
status, population anchors and drain fields have the expected fresh layout.

The actual ARM timing `loop` is 428 bytes at `0x0810038c`. It retains the entry
clock call, anchor/elapsed/status stores, before/after context stores and the
observer call. The active path calls Runtime::step once through `0x08101941`;
the terminal path at `0x08100502` bypasses diagnostic clock/stores and tail-calls
that same function. These are instruction observations, not symbol-presence
inferences.

Observer::observe loads literal `0x081000c9` and calls it at `0x08100262` with
the all-population base and at `0x081002c2` with base+3236 for the completed
population. `target_timing03/gdb_02.stdout` covers that exact 108-byte
Distribution::observe FUNC (`0x081000c8..0x08100134`). It stores sample count at
offset 3200, the indexed histogram bin at `0x08100116` for duration<800, overflow
at offset 3204 otherwise, plus maxima/start/end and saturation/rejected fields.
Thus both histogram updates survive target optimization. The 300000000-us
cohort boundary, separate drain and immutable terminal paths remain represented;
this inspection does not execute those paths or establish their runtime values.

Production contains no outer_loop_timing object or helper. Its 16-byte loop at
`0x081000f0` loads Runtime and tail-calls Runtime::step (`0x08101499`) with no
observer path. This and the byte-identical allocated image establish the claimed
production exclusion for this exact build.

## Acceptance boundary

D243 now has accepted source/host evidence plus actual native compile, target
layout and retained-update evidence. Static remaining RAM is not measured free
RAM under stack/heap load. No timing firmware was uploaded or run here; no
300-second population, completion-labelled p99, all-sensor ready state, physical
sub-800-us worst case or competition qualification follows. The observer remains
a conservative entry-to-entry wall-envelope instrument with the documented
classification, final-straddler, drain and unmeasured final-freeze-tail limits.
Existing physical evidence and specific STAND/RING authorization requirements
are unchanged.
