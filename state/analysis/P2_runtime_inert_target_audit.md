# D104 actual Runtime inert probe: offline target audit

2026-09-23. **PASS for the final frozen source, compiled target, ABI and
conditional loader model.** This audit performs Linux file/offline ELF reads
only: no compile, upload, reset, MCU read or runtime qualification. Independent
source/capture review and the coordinator's upload boundary remain separate.

## Selected final image

- Source: `2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5`.
- Completed checked receipt: `360b0e9f766643f98b29c6f6d68b9656`, default startup,
  MATCH=0 and MOTORS_ALLOWED=0.
- Final ELF: `8be8768aca2990eafa1edabcff37b645c9beec51df7617db7324f228f672daf8`.
- ELF-ZSK: `eb1d2b5b7ddeb432ec453da12cf69b4e86f2bb61b2ca63b3e58df4819de5f852`.
- Both files are 124,996 bytes. Package bytes after the 16-byte ELF header agree
  exactly with the final ELF. Do not substitute the separate BIN-ZSK output.

The exact directory containing both reviewed files is:

```
/home/arduino/sumox26_codex_build/_app_builds/native-app-v1/2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5/bench-default/360b0e9f766643f98b29c6f6d68b9656/artifacts
```

`P2_runtime_inert_raw/target_capture_pins.json` contains complete paths/hashes,
layout, loader ABI and read-budget details. `target_summary.json` records the
repeatable checks. Reproduce with
`python state/analysis/P2_runtime_inert_target_analyze.py`.

## Source, entry and linkage

The final collection verifies all **91 files**, all three ELF hashes and the
package against the completed wrapper receipt and retained source snapshot.
The 86 shared files are byte-identical to D103; only the five bench files replace
app.ino/add the probe. The 79 objects include 1,462 common allocated sections
identical to D103 default, plus the three new probe compilation units. The
79-command/133-metadata audit includes 129 dependency files and no external
Arduino library discovery.

The sole initializer is `_GLOBAL__sub_I_runtimeDiagnostics`, constructing one
Runner with the native clock callback. Actual retained relocations establish
Runner -> Runtime construction, Runner::begin -> Runtime::begin, and
Runner::poll -> Runtime::step. Frozen source supplies the checked inert motor
port, empty ADC/Source/Dump ports and `SetupGrants{}`. No native UnoQ motor,
sensor or UART owner is linked. There are no native I/O or heap-allocation
relocations. Runtime's pure strategy/recorder/dump logic remains linked.

All three ELFs share 170 imports: seven native device declarations disappear
from D103 and `z_impl_k_sched_current_thread_query` is added. The 32 automatically
selected native exports and 42 AEABI mappings are verified; the new thread query
is checked separately at `0x08011ae1`. Unused matrix/pinctrl/device import
declarations remain in the core symbol table **without corresponding retained
relocations**; their presence is not a native callback path.

Main/micros/static-thread startup match the previous pinned implementation.
The static-thread region is empty. initVariant and the strong `__loopHook()` are
two-byte return instructions; setup/loop call only the new native wrapper entry
points. There is no fini array.

## Loader and actual target layout

The ordered pristine-pool/persistent-flash-peek model uses the unchanged pinned
loader and 262,144-byte llext pool. It checks each request against its preceding
span and accounts temporary symbols plus the separate export copy.

| Quantity | Bytes |
|---|---:|
| Compiler payload / nominal remainder | 233,120 / 29,024 |
| Text / rodata / BSS payload | 66,228 / 24 / 166,856 |
| Complete conditional peak | 236,968 |
| Remaining span / largest next payload | 25,176 / 25,172 |

Allocation chunks in order are bookkeeping88, extension200, section-map128,
text66240, rodata32, BSS166864, exported-symbol16, init-array8,
temporary-symbol3376 and export-copy16. Every request fits. This is conditional
fit, not observed loaded RAM, fragmentation or transient peak.

Actual target DWARF and linked symbols verify:

| Item | Bytes / offset |
|---|---|
| Runner | 166,584 bytes, alignment8, BSS offset0 |
| Contained Runtime | 166,304 bytes, Runner offset64 |
| Transaction / Robot / recorder | 162,544 / 2,640 / 159,200 bytes |
| runtimeDiagnostics | 232 bytes, alignment4, BSS offset166,624, section7 |
| Diagnostic report / stack / tail | offsets4 / 196 / 228 |
| Report / StackSample | 192 / 32 bytes |

The current loader recheck confirms thread size256, stack-info offset160,
reserved main stack32768, heap descriptor24 at `0x2000112c`, and pool262144 at
`0x20013890`. Stack painting is absent; the stack-space export remains zero.
The current-thread/PSP sampling implementation is retained. These are layout and
reservation facts, not actual sampled headroom or a stack watermark.

## Capture budget and preserved findings

The loader requires five 64KiB-bounded flash reads; the final package requires
two reads of65,536 and59,460 bytes. With two list reads, N extension nodes, two
232-byte diagnostics, two24-byte descriptors and32 pool blocks, total reads are
**45+N**. One node uses46 reads/913,688 bytes; three use48/914,080. Four would
require49 and cannot fit the frozen48-read limit. The coordinator selected a
three-node maximum; command/time limits remain independently enforced by capture.

The initial `1cd2f6cc` source/receipt/ELFs/ABI remain preserved as a superseded
baseline. It lacked the closing-sample overall-deadline check and is not selected
for a run. Final source differs only in runtime_bench.cpp, adding that check;
its target grows24 bytes. An audit-only Windows path normalization error is
preserved in `target_analyzer_attempt02.txt`; normalized-path and final runs
pass. No production source was changed by this auditor.

Raw evidence resides in `target_2bd817c4/`, `target_sources_2bd817c4/`,
`target_abi_2bd817c4/` and `target_artifact_inventory.json`. Actual deployment,
terminal Runtime execution, pool snapshots, sampled stack, clocks, native
peripherals, D103 reset, full-app WCET and all human gates remain unproved here.
