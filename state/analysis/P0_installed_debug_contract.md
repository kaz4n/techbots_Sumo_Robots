# Installed UNO Q compile/debug contract — 2026-09-22

Observed 23:01–23:12 Asia/Dubai, only through bundled Windows ADB selecting serial
2629958581. This is a read-only installed-file/source audit and a proposed capture
contract, not an executed debugger procedure. No compile, upload, reset, MCU
attach, RAM/register/flash access, dependency installation or credential access
was performed. Only this report is owned by this worker.

## Findings for the coordinator

- The installed compile recipes contain no MCU operation. Default and Immediate
  compile-only produce different sketch headers; neither starts the sketch.
- Normal startup has a source-backed matrix handoff: the loader stops its boot
  animation before entering the sketch. The packaged ELF contains the matching
  matrixEnd call before llext_load/bootstrap. This does not identify the flashed
  loader; default-startup execution still needs that identity and observed success.
- Never reuse flash_sketch.cfg, flash_bootloader.cfg, remoteocd upload, or the
  installed default STM32 target configuration for passive readout.
- A minimal memory-access-port-only SWD session is the recommended candidate:
  no reset pin assigned, no Cortex target, no flash driver, no target event hooks.
  It can read frozen diagnostic RAM without halting the CPU. It remains to be
  independently reviewed and exercised; debug-port/bus activity is not electrically
  passive and may affect an unfinished timing run.
- Keep the default dynamic sketch. Its runtime addresses can be recovered from
  the verified loader's LLEXT table. Static linking would simplify addresses but
  changes the diagnostic build; it is unnecessary unless dynamic resolution fails.
- No documented Linux view of deployed MCU-loader bytes/hash was identified.
  Hashes below describe installed files only. The observed Linux remoteproc names
  are modem/adsp; no /dev/mtd device or STM32 sysfs view was found in scoped checks.

## Installed identities and public paths

Let CORE mean:
/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0

Let TC mean:
/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin

| File / fact | Observed value |
|---|---|
| Packaged loader ELF | CORE/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf, 2,303,728 bytes |
| ELF SHA-256 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| Packaged loader binary | CORE/firmwares/zephyr-arduino_uno_q_stm32u585xx.bin, 263,680 bytes = 0x40600 |
| Binary SHA-256 | 6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713 |
| Packaged loader flash span | 0x08000000 through 0x080405ff inclusive |
| Loader configuration | CORE/firmwares/zephyr-arduino_uno_q_stm32u585xx.config |
| Generated autoconf | CORE/variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include/generated/zephyr/autoconf.h |
| Actual upload OpenOCD | /opt/openocd/bin/openocd; not owned by a matching dpkg package |
| Actual OpenOCD SHA-256 | 04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff |
| Installed adapter configuration | /opt/openocd/openocd_gpiod.cfg |
| Adapter config SHA-256 | 58c0c341ba2a0c758bb044683884fb4af01ff6c9cf292bec6b2115c44f7ff836 |
| Included target configs | /opt/openocd/stm32u5x.cfg; /opt/openocd/stm32x5x_common.cfg |
| stm32u5x.cfg SHA-256 | 8c0ffc41eadd0593168b825d60d6736329c08974c047fdac722fabb93c0ee46a |
| stm32x5x_common.cfg SHA-256 | 139a2c4167e4fc649ab0057560858e03a24dcafeb5b0b3a3bcb7b9373e0869e4 |

The loader ELF has three contiguous file-backed LOAD spans: physical
0x08000000/size0x3f474, 0x0803f474/size0x1188, and 0x080405fc/size4.
Thus a future raw 263,680-byte read from 0x08000000 can be compared directly
with this packaged binary. BSS/noinit and backup SRAM are zero-file-size LOAD
segments and must not be confused with loader flash identity.

Generated configuration: 32,768-byte main stack, 32,768-byte system heap,
CONFIG_LLEXT_HEAP_SIZE=256 (KiB), ELF-object LLEXT, read-only sketch storage,
no LLEXT veneers, no Zephyr shell, watchdog disabled, 64-bit SysTick cycle counter.
Declared SRAM is 768 KiB beginning 0x20000000. ICACHE/DCACHE options are enabled;
no cache-flush instruction or function call is proposed by this audit. Runtime
capture must validate its data rather than assume every debugger access is coherent.

## Compile versus upload

Installed platform.txt lines128–169 contain: a variant includes.txt existence
check; compiler/archive/link commands; gen-rodata-ld; strip of debug data into
the distributable ELF; objcopy; zephyr-sketch-tool wrapping; and size checking.
No platform.local.txt or boards.local.txt was found in CORE. Preserve the
unstripped *_debug.elf and .map when the coordinator builds the diagnostic.

Default is link_mode=dynamic and wait_linux_boot=yes. Immediate sets
build.boot_mode=immediate and passes -immediate to the wrapper; static sets
-prelinked and changes the upload artifact to bin-zsk.bin. Compile-only must
omit --upload and must not call the separate upload command. This conclusion
is from the installed recipes, not an executed build or exhaustive audit of
every compiler binary.

UNO Q upload selects remoteocd. The versioned remoteocd source launches
/opt/openocd/bin/openocd using /opt/openocd/openocd_gpiod.cfg; it does not use the
other SiliconLabs OpenOCD installation merely because that tool is a core
dependency. [remoteocd 0.1.1 flash implementation](https://github.com/arduino/remoteocd/blob/0.1.1/flash.go)

Installed flash_sketch.cfg asserts a reset configuration, initializes, resets
and halts; conditionally writes loader and sketch if verification fails; resets
again; then writes 0xCAFFEEEE to backup SRAM at0x40036400. flash_bootloader.cfg
also resets/halts, conditionally writes the loader, then resets. Upload can
therefore replace the loader as well as the sketch. Neither is a RAM-read script.

Even /opt's ordinary target setup is unsuitable unchanged: its AP examine-end
writes DBGMCU_CR; CPU examine-end changes low-power/watchdog debug registers;
reset-init changes voltage, flash latency and clocks; GDB attach can invoke
reset initialization. Omitting explicit reset from the command line alone
does not establish a non-mutating attach.

## Matrix compatibility and limits

Installed Arduino_LED_Matrix0.1.3 header has begin -> matrixBegin, end ->
matrixEnd, draw -> matrixGrayscaleWrite, and a conditional ArduinoGraphics
include. The current diagnostic uses the 104-byte draw path and does not use
the unsafe three-word _frameHolder/renderBitmap convenience path. The installed
library's native functions are supplied by the loader.

The versioned loader's normal path waits for Linux readiness, finishes and blanks
its boot animation, stops the matrix timer, then enters the sketch. An already
ready Linux avoids that animation; USB animation mode does not reach the sketch.
Immediate bypasses this normal wait, so the existing Immediate matrix restriction
is not cleared. [Loader startup source](https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/loader/main.c)

The packaged ELF disassembly places matrixEnd at0x08005694, called at0x0800583a
before llext_load at0x080058ba and bootstrap at0x080058e2. This supports the
handoff in the packaged binary without treating source tag alone as binary
identity. Source line numbers differ between its DWARF and the online file;
this report does not claim byte-identical source provenance.

matrixGrayscaleWrite copies104 bytes. matrixBegin starts a counter with a10us
top interval; matrixEnd stops it. Matrix-active timing must therefore be a
separate diagnostic condition. The initial diagnostic frame is blank and the
SUMO glyph scrolls in later, so first visible text is not exact sketch-entry time.
[Matrix implementation](https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/loader/matrix.inc)

## Candidate no-reset capture configuration — not executed

These internal Linux GPIO selections are copied from the installed adapter
configuration, not new header wiring. Deliberately omit SRST/TRST GPIO38.
The exact /opt binary already supports mem_ap in its shipped target configuration.

~~~tcl
adapter driver linuxgpiod
adapter gpio swclk 26 -chip 1
adapter gpio swdio 25 -chip 1
transport select swd
adapter speed 4000
reset_config none

source [find target/swj-dp.tcl]
swj_newdap sumox cpu -irlen 4 -ircapture 0x1 -irmask 0xf -expected-id 0x0be12477
dap create sumox.dap -chain-position sumox.cpu
target create sumox.mem mem_ap -dap sumox.dap -ap-num 0
targets sumox.mem
gdb_port disabled
telnet_port disabled
tcl_port disabled
init
~~~

A mem_ap target represents an access port rather than a CPU. That avoids Cortex
halt/GDB hooks. Only the helper swj-dp.tcl is sourced; do not source either STM32
target file or an upload script. Debug infrastructure initialization still writes
DAP control registers and claims GPIO lines; “read-only” here means no MCU memory,
peripheral, flash, reset or execution-control writes are requested.
[OpenOCD target types](https://openocd.org/doc/html/CPU-Configuration.html),
[Linux GPIO adapter](https://openocd.org/doc/html/Debug-Adapter-Configuration.html)

After independent review, a bounded Linux process could use the candidate file
with /opt/openocd/bin/openocd -s /opt/openocd/share/openocd/scripts -f <capture.cfg>.
Restrict its command list to the following examples with reviewed output paths
and validated addresses:

~~~tcl
# Only after selecting the sole sumox.mem target:
dump_image /home/arduino/sumox26-capture/loader-read.bin 0x08000000 263680
sumox.mem read_memory 0x200017bc 32 2
# For a validated aligned scalar address:
sumox.mem read_memory <SCALAR_ADDRESS> 32 1
# For validated histogram address and exact 1001-word size:
dump_image /home/arduino/sumox26-capture/p0-histogram.bin <HISTOGRAM_ADDRESS> 4004
shutdown
~~~

Placeholders must be resolved first; the examples are not a ready-to-run script.
dump_image writes a Linux evidence file, not MCU memory. Use a fixed process
deadline and fixed byte/count bounds; on failure, stop and report it. Do not add
reset/halt/resume, register writes, load_image, flash commands, breakpoints,
MCU function calls, cache maintenance or a “recovery” write. Avoid verify_image:
its checksum optimization need not be assumed to be a simple byte-only read.
[OpenOCD read/dump commands](https://openocd.org/doc/html/General-Commands.html)

Prefer reading only after the uninstrumented capture has had time to finish.
If the first sample check shows fewer than60000 observations, do not call that
run unperturbed: memory-bus/debug traffic may have affected it. No halt is
necessary after completion because p0_timing stops changing its counters.

## Dynamic symbol resolution: exact installed ABI and finite bounds

Offline TC/arm-zephyr-eabi-gdb -nx -nh -batch on the packaged loader ELF
successfully reported the following DWARF layouts. No remote target was attached.
TC/nm and readelf independently confirmed symbols and debug sections.

| Loader object | Address / layout |
|---|---|
| llext_list | 0x200017bc; head pointer+0, tail pointer+4 |
| struct llext | 196 bytes |
| Embedded next pointer | +0 |
| name[16] | +4 |
| mem[12] | +20; 4-byte pointers |
| mem_size[12] | +80; 4-byte sizes |
| sym_tab | count+132, entry pointer+136 |
| exp_tab | count+140, entry pointer+144 |
| struct llext_symbol | 8 bytes: name pointer+0, resolved address+4 |
| LLEXT_MEM_BSS | index3: base pointer+32, size+92 |
| kheap_llext_heap | 0x20013890; configured length0x40000 |

Use these addresses/layouts only after loader-byte comparison succeeds. Also
compare the deployed sketch bytes at0x08100000 against the exact reviewed
elf-zsk.bin artifact, using that artifact's actual size; matching loader alone
does not identify the running timing sketch.

Recommended finite decoder contract:

1. Every structure/table address is 4-byte aligned and the complete range lies
   within [0x20000000,0x200c0000). Check addition without wrap before any read.
2. Follow at most four LLEXT nodes, maintaining a four-entry visited set. Null
   terminates; repeated pointer, out-of-range pointer or excess nodes fails.
   Accept exactly one node whose fixed16-byte name is NUL-terminated “sketch”.
3. Accept sym_tab.sym_cnt only in1..min(4096, actual artifact ELF symbol-entry
   count). Require the whole count*8 table in SRAM. Never follow an unlimited
   string: read at most128 bytes, requiring a NUL within the containing region.
   Symbol-name pointers may lie in SRAM or within the exact verified sketch
   flash artifact range; reject other regions.
4. Resolve exact names p0Samples, p0MaxLateUs, p0OverPeriod, p0Histogram.
   Require unique entries, aligned addresses, and non-overlapping ranges
   matching each symbol's size in the exact compiled ELF. Require all four
   complete ranges inside that extension's validated BSS region.
5. If the runtime table omits a symbol, fail this method rather than guess.
   A separately checked fallback can use BSS base plus the symbol's section-
   relative st_value from the exact ET_REL diagnostic ELF, after confirming
   its section really is .bss and its size/range fits. Do not blindly use nm's
   displayed zero-based values as absolute MCU addresses.
6. Read p0Samples first, requiring exactly60000; read the1001 bins, maximum and
   over-period count; read p0Samples again and require60000. Repeat the small
   counters/histogram and require identical frozen values. Sum bins=60000,
   and overflow bin1000 equals p0OverPeriod for the current1ms/1000us config.
   Report p99 as a lower bound if it lands in the overflow bin, not an exact
   value. Capture elapsed wall time separately;60000 samples can take >60s.

Installed build-dynamic.ld explicitly consolidates .data and .bss. Its LLEXT
header distinguishes resolved global sym_tab from exported exp_tab; p0 globals
need not be exported API functions to be located in the global table. Table
availability is still checked at runtime before relying on it.

GDB is optional. If later used, add-symbol-file can assign independently verified
.text/.data/.bss bases to the exact *_debug.elf; one global relocation offset is
not justified for independently allocated regions. Never call llext_by_name or
llext_find_sym on the MCU merely to resolve addresses.
[GDB section relocation](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Files.html)

Static-link alternative: memory-static.ld fixes RAM at the loader's
kheap_llext_heap and Flash at _sketch_start+16; the linker map then provides fixed
addresses. It still depends on the exact loader, changes the build mode, and
requires separately captured evidence. No mode or source was changed here.

## Read-only evidence and remaining validation

All board file queries used the exact Windows bundled adb -s2629958581 shell
transport recorded in P0_board_inventory_20260922.json. Successful queries
(exit0) included numbered platform/board hooks, both upload configs, matrix
header, generated autoconf, firmware config/DTS, LLEXT headers, linker scripts,
/opt OpenOCD configs, sha256sum, TC/nm, TC/readelf, TC/objdump and offline GDB
ptype/info commands. No external-program launch by GDB, target connection or
MCU function evaluation occurred.

Expected nonzero observations: command -v rg exit1 (grep used); dpkg-query -S
/opt/openocd/bin/openocd exit1 (no owning package); /dev/mtd* listing exit2
(absent); selected service-file hash/firmware keyword search exit1 (no match).
Both remoteproc names were read successfully. A broad initial nm filter included
too many exported symbols and hit output truncation; anchored follow-up queries
returned the precise addresses above. All core files examined were public code,
generated configuration or package artifacts, not account or credential files.

Primary web references were inspected at the pinned tags linked above. The
OpenOCD/GDB manuals document candidate commands; they do not substitute for
installed-target execution. The current board's loader hash, diagnostic
addresses, debug-port permissions, read coherence, actual no-reset behavior and
timing results remain unmeasured. No physical safety or phase gate is passed.

Next action: independently review the minimal configuration and finite decoder;
coordinator completes its separately owned compile validation, preserves exact
artifacts, and authorizes the bounded attach/read. Abort on any identity, bounds
or read failure rather than falling back to a reset or write.

## Follow-up: installed RouterBridge and exact timing ELF startup

After the coordinator completed installation, read-only source and offline ELF
inspection verified Arduino_RouterBridge 0.4.3, Arduino_RPClite 0.3.1,
MsgPack 0.4.2, ArxContainer 0.7.0, ArxTypeTraits 0.3.2 and DebugLog 0.8.4.
The worker did not install or compile these. The coordinator supplied the
successful timing build directory:

```text
/home/arduino/sumox26-build/3de6da69f44c2317b82b246b0fe8e324e1001a531b4741c09e511269fb24e7f4/p0_timing/artifacts/bench-default
```

The exact p0_timing.ino_debug.elf inspected has SHA-256
b582d62e40ef9b046d16c0a5390101059893569291445acdf2e713d95b8a3570.
This follow-up found no automatic Bridge connection, Linux RPC wait, network
socket creation, or Bridge worker-thread start on this inert sketch's startup
path. It did find a library-provided loop hook, so this timing measurement
includes the installed core/library's yield and mutex-check overhead.

Installed source paths below are relative to
/home/arduino/Arduino/libraries/Arduino_RouterBridge/src unless prefixed CORE:

- singletons.cpp:18–19 defines Bridge and Monitor; line23 aliases Serial to
  Monitor when the variant enables it. BridgeClass's constructor at
  bridge.h:166–168 only stores the hardware-serial pointer.
- monitor.h:37 stores the Bridge pointer. RingBufferN's constructor zeros its
  fixed buffer and indices; Stream and Print constructors only set scalar
  defaults. hci.h:49–51 stores a pointer and default-constructs its empty vector;
  inline RouterBridge::HCI at line161 does not call begin.
- bridge.h:182–217 places UART begin, heap allocations, worker-thread creation
  and the reset RPC in explicit Bridge.begin(). monitor.h:41–66 can call that
  begin path, but only when Monitor/Serial.begin() is explicitly called.
  RpcCall::result at bridge.h:87–117 has unbounded response waiting; none of
  these operations is invoked by this reviewed diagnostic.
- CORE/variants/arduino_uno_q_stm32u585xx/postvariant.h requires the header for
  library discovery; variant.h:8–16 enables its Serial alias. Forced inclusion
  is therefore a build dependency, not evidence of automatic communication.
- CORE/cores/arduino/main.cpp initializes the variant/static-thread section,
  calls setup, then loop and __loopHook repeatedly. SerialUSB.begin is
  conditional. The exact linked main at .text+0x45f0 contains no SerialUSB call;
  linked initVariant at0x45ec is a return; the static-thread section has size0.
  The loader/core still have their separate boot sequence and entry printk
  diagnostics. This finding does not remove default startup's Linux-ready wait.

The linked weak __loopHook at .text+0x24c4 is the RouterBridge version, not
the empty weak core version. Its exact machine code:

1. Calls z_impl_k_yield.
2. Locks Bridge+0x38, reads started at Bridge+0x158, then unlocks.
3. Calls update_safe only when started is true.

The linked constructor at .text+0x4194 explicitly zeros started and the mutex
storage. It does not call k_mutex_init until explicit begin; this is an upstream
initialization caveat, not an API pattern to copy. For this exact packaged
loader and this single uncontended caller, offline disassembly establishes the
path is nonblocking: z_impl_k_mutex_lock at0x08010b48 takes its lock_count==0
fast path (0x08010b62–0x08010b9c); z_impl_k_mutex_unlock at0x08010c2c handles
the null queue at0x08010c78 by clearing owner/count and returning. No competing
Bridge thread exists because begin is never called. This is limited binary
evidence; it is not a general guarantee for a different library/core or
concurrent use, and it is not a measured timing result.

The .init_array relocation table has exactly four entries, all inspected:

| Function offset in debug .text | Constructor effect |
|---|---|
| 0x2508 | HCI guard/reference and empty-vector initialization |
| 0x4194 | Bridge/Monitor zeroing, references, fixed-buffer initialization |
| 0x4aa0 | Serial1/2/3 references plus semaphore/ring-buffer initialization; no UART begin |
| 0x5284 | C++ error-category destructor registration through __aeabi_atexit to the no-op __cxa_atexit stub |

No static thread definition or startup initializer was found in the installed
RouterBridge/RPClite dependency sources. The absence of the actual linked
BridgeClass::begin/updateEntryPoint symbols and the empty static-thread area
corroborate the source call-path check. Monitor methods exist because its
vtable is linked; their presence alone does not call them.

### Exact final-ELF BSS offset method

The final upload-side p0_timing.ino.elf is ET_REL and contains normalized
section-relative symbol values. Its .bss is section9, size0x2d34, alignment8.
The preserved _debug.elf predates symbol normalization: its nm values differ.
Use readelf -sW on the exact final .ino.elf for the following offsets, not raw
_debug.elf nm addresses.

| Symbol | Final ELF .bss st_value | Size |
|---|---:|---:|
| p0Histogram | 0x8 | 4004 bytes |
| p0OverPeriod | 0xfac | 4 bytes |
| p0MaxLateUs | 0xfb0 | 4 bytes |
| p0Samples | 0xfb4 | 4 bytes |

After the loader/sketch identity checks and bounded unique sketch-node
traversal above, validate the runtime BSS pointer/size and add these offsets
with overflow/full-range checks. This is the separately checked direct method
for this build; full runtime symbol-name traversal is unnecessary. For example,
Bridge is0x1280 in the normalized final ELF but0x6630 in the debug ELF; silently
using the latter as a BSS offset would be wrong.

### Follow-up evidence commands and file identities

All operations again used bundled adb -s2629958581 shell. Successful exit0
queries included numbered source reads; dependency library.properties versions;
TC/nm -C; TC/readelf -hSW, -sW and -rW; and TC/objdump -drC on the exact
coordinator-provided artifact. Packaged loader mutex bodies were read with
TC/objdump -dC, never executed through a debugger. A preliminary guessed variant
path was absent; the corrected path above was enumerated. A preliminary bounded
find under /home/arduino reported permission denied for lost+found while finding
the cache artifacts; the final evidence uses the exact supplied build path.

| File | SHA-256 |
|---|---|
| RouterBridge/src/singletons.cpp | 6184e7a02393b01457dc4233d0e96e543f2b8cf051e9a03adeb6da343dc3b045 |
| RouterBridge/src/bridge.h | ca275c57d1865db16a24e14c901757c31fac7ada91bb09130e07dfb6b4b9febb |
| RouterBridge/src/monitor.h | d3c8940c58db82eae0064208cdee6bb8e0c4ea68ee56cf75c38ff98038d5cf9e |
| RouterBridge/src/hci.h | 3151c72764945649405ad189f3954402f9d2e074d5542df13878a634d872e050 |
| CORE/cores/arduino/main.cpp | d31dc5f78acf0a3535b4650a63a8952908f8c6f4bf8164d639da4a02486b87ed |

Source and binary inspection support proceeding to the coordinator's separately
reviewed inert upload/readout. They do not substitute for flashed identity,
successful sketch execution, stable RAM capture, measured scheduler behavior,
or any phase gate.
