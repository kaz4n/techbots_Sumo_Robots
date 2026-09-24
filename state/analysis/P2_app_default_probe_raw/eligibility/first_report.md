# Exact app-default bare-board eligibility audit

2026-09-24. Read-only source/artifact audit requested after D117. No compilation,
test execution, board connection, upload/reset, grant change, manifest change or
firmware modification occurred. This author now inspected app implementation
bodies; the earlier independent D117 test freeze remains historical evidence,
but this audit makes no subsequent app test-author independence claim.

**Conditionally eligible for a narrowly specified, unchanged-image load and RAM
observation on the human-reported bare UNO Q. Not eligible to execute under the
existing D104/D114 run contracts or generic upload allowlist.** No new firmware
runner or granted sensor/dump path is needed to investigate actual loading and
retained allocator metadata. The experiment must explicitly include the app's
existing native inhibited motor initialization. It cannot be described as an
I/O-free Runtime probe, a finite completed app test, or physical motor acceptance.
If the proposed scope requires no GPIO/PWM initialization, the unmodified app is
concretely ineligible.

## Exact candidate and conditional memory result

Use only the checked default/MATCH0/MOTORS_ALLOWED0 candidate:

- Source digest: `e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69`.
- Loadable app ELF: `8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257`.
- ZSK: `c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5`.
- Pinned loader ELF: `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

The exact record is
`P2_dump_fifo_raw/reviewer/target_e820c0e1_bench-default.json`, `records[0]`.
Its ordered model peaks at 262,136 bytes in the 262,144-byte pool: remaining
chunk span 8 bytes, largest allocatable payload 4 bytes. The final transient
allocations are 4,368 bytes for global symbols and 16 bytes for export copying.
The assumptions are a pristine pool, persistent aligned flash peeks and no
interleaved allocations. This is neither measured post-load free RAM nor stack
headroom. The debug ELF is an offline ABI reference, not the image to upload;
its larger section map does not satisfy the same fit result.

Exact debug evidence records Runtime size 166,376/alignment 8, Transaction
162,544/alignment 8, DumpPort 24/alignment 4, Transfer 1,408/alignment 8, and
native dump owner 208/alignment 4. The same actual type output places the
504-byte TransactionReport at Runtime-relative offset 162,128 and the 600-byte
RuntimeReport at offset 164,664. Those are offline ABI facts, not MCU addresses;
their proximity permits small selected views instead of copying the complete
Runtime. Final BSS is 167,272 bytes; initialized data is 208 bytes. Every selected
field and relocated address must still be independently pinned for a new readout.
No address is proposed or authorized by this audit.

## Actual startup and reachable I/O

`src/app/app.ino:11-24` constructs one NativeSources, native motor port, selected
FIFO8 dump port and actual Runtime, then calls `runtime.begin(SetupGrants{})`.
Factories/constructors bind callbacks and initialize ordinary object data; motor
candidate periods are derived from compiled metadata. They do not initialize
sensors or claim native UART ownership.

The critical unconditional chain is `Runtime::begin` at `runtime.cpp:79`,
`Transaction::initialize` at `transaction.cpp:9`, and `MotorGate::begin` at
`motors.cpp:79`. Motor setup precedes optional source/dump initialization:

1. `motor_port_unoq.cpp:245` checks the installed map and configures proposed
   EN D10 as output LOW, then reads back mode and LOW. This is real GPIO I/O.
2. `:261` initializes/applies the selected channel pinctrl for proposed PWM
   D3/D5/D6/D9, using the existing TIM3/TIM1/TIM3/TIM4 mapping and ownership
   checks. This is real device, clock, timer and pad initialization.
3. The Gate writes all four pulses as zero and invokes the real settle callback.
   `:332` clears timer UPDATE flags and polls fresh updates, with the existing
   150 us / 4,096-poll bounds. Native setup may fail; success is not assumed.
4. Each successful due BOOT epoch again performs the real LOW/zero/settle
   transaction. An unmodified successful app keeps doing this indefinitely.

Both software layers independently exclude active requests in this exact build:
`MotorGate::transact` gates enabled output on MOTORS_ALLOWED, and native
`writeEnable`/`writePwm` refuse HIGH/nonzero requests when that macro is zero.
Cleanup retains actual acknowledgement failures. These facts support an
inhibit-only experiment without granting motion authority; they do not measure
pin voltage, PWM waveform, startup transients, electrical coast or powered safety.
The bare-board premise remains human-reported. No STAND/RING authorization is
invented for a later motor-capable or connected-motor run.

Every optional grant is false. `initializeSources`, `acquire`, `serviceImu`,
`display`, `initializeDump` and `serviceDump` therefore admit no opponent/QTR/
ADC/button/IMU/matrix or native dump callback. Pure projection still marks these
sources unavailable. No source grant or pin confirmation is synthesized.
False dump/calibration grants also avoid cancellation callbacks: Transfer.abort
acts only when ACTIVE (`recorder_dump.cpp:340`), and calibration cleanup first
checks enable grants (`runtime_calibration.cpp:34-48`). Thus a failed MotorGate
setup does not accidentally initialize or cancel the native UART.

The exact collected main relocations call initVariant, start_static_threads,
setup, then loop and __loopHook. initVariant is empty; __loopHook is the strong
empty return. Sketch and pinned base static-thread start/end symbols coincide.
No Bridge/Serial/RPC singleton root is added. The retained thread-creation imports
support generic startup code and do not establish that a new worker runs.
Uncalled UART/matrix/device exports are not execution. This does not remove
ordinary Zephyr/loader startup, interrupts, stock RCC/PWR/DAC/pinctrl behavior or
its existing loader/sketch execution context. D117 preserves that pinned loader
identity; a new exact run review must retain the existing base-startup evidence,
not infer whole-system silence from the empty sketch thread list.

## Honest finite observations without new MCU instrumentation

If native setup succeeds and epochs complete, all-false grants make
`initialization_complete` remain false (`runtime_inputs.cpp:134-165`), so the
Robot remains BOOT and the recorder EMPTY. Runtime may be RUNNING and epochs
may advance even though robot initialization never completes. Conversely, setup
failure retains Runtime FAULT/TRANSACTION and Transaction FAULT/SETUP. Later
clock/I/O failures retain their actual causes. No outcome is guaranteed.

The app has no diagnostic sequence wrapper, success freeze, finite run deadline,
sampled PSP minimum or public heap report. It cannot supply D104's immutable
232-byte diagnostic or D114's terminal 9,892-byte Runner. Two live app object
reads are not a coherent transaction, and two equal RUNNING reads are not a
completion or proof of permanent silence. Do not abort/reset the app to manufacture
a terminal report or reinterpret a debugger stop as normal firmware completion.

The minimal next readout should distinguish, using exact reviewed fields:

- Verified flashed loader/sketch identity and a uniquely validated loaded
  extension, versus absent/ambiguous/inconsistent extension evidence.
- Runtime phase/fault, initialization_complete and sampled epoch/miss counters:
  NOT_STARTED, observed RUNNING progress, actual FAULT, or inconclusive live reads.
- Actual Transaction/Robot/Gate state and faults, inhibited applied-output facts,
  recorder phase/counts, and dump NOT_INITIALIZED/idle facts, only where the new
  schema can honestly establish consistency. Dynamic cross-epoch combinations
  must remain unavailable rather than being normalized into a healthy receipt.
- Two validated heap descriptors/pool snapshots interpreted as allocator
  metadata, with actual retained allocation/free-region sizes. Changing app
  payload bytes need not invalidate unchanged allocator metadata.

This is possible without unknown-address probing: derive fixed loader symbols,
heap/node ABI and actual app symbol/section-relative offsets offline from the
pinned loader and exact app/debug ELF. Validate every observed relocation pointer,
node, section extent and containing allocation before a purpose-bound read. Use
raw ET_REL section-relative offsets, not linked-looking nm display values. Do not
scan RAM, call MCU functions, read arbitrary addresses, halt, paint stack, write
memory, start a transport peripheral or widen limits after a refusal.

A verified resident extension plus advancing app epochs would directly establish
that this exact image loaded and ran on that observed boot despite its narrow
model margin. A post-load heap capture can quantify actual retained free space;
it cannot measure the historical 8-byte transient minimum without additional
instrumentation. Absence of the extension is not by itself proof of out-of-memory.
No sampled stack minimum or full-app WCET follows from this unmodified image.

## Narrow next task and current blockers

Prepare one exact-app, default-only run/readout contract and independent public
oracles, retaining the firmware and all false grants. Bind the hashes above,
human-reported bare setup and explicitly admitted inhibited motor I/O. Specialize
the existing reviewed upload pattern to one identified attempt only after review;
fresh checked artifacts must reproduce the loadable hashes. Preserve current
generic app upload refusal and every existing manifest key meanwhile.

Prepare a finite, purpose-bound passive collector using the existing immutable
P0 helpers and D104-style ceilings: 48 reads, 2 MiB total, 16 KiB per RAM read,
64 commands, 600 s total and 30 s per command. First calculate the exact flash,
bounded-node and two-pool read plan; do not assume it fits or read the entire
166,376-byte Runtime as one operation. Choose and freeze only the minimal app
field slices needed above. Preserve raw bytes, launch outcomes, actual failures
and nonterminal/inconsistent observations; no repeated upload or invented success.

Do not combine the old tools' plans mechanically: two complete 256 KiB pools
already require 32 RAM reads. The current loader plus 176,064-byte app package
require at least eight 64 KiB flash reads per full sweep; duplicating that sweep
before and after consumes all 48 reads before nodes, descriptors or app views.
That D114-style double-sweep/two-pool combination is over budget. A D104-style
single full pre-verification plan with bounded metadata consistency checks is
the narrower candidate to count and review explicitly; neither a cap increase
nor an implicit relaxation of D114's separate contract is approved here.

Current blockers are concrete preparation gaps, not a requirement for a generic
runner: no exact-app upload identity/attempt guard is adopted, no app-specific
relocated read ABI/consistency schema and read budget are frozen, and existing
tools explicitly pin other images. D104 expressly excludes loading the normal app;
D114 grants only its identified ADC probe. This eligibility document authorizes
none of those operations and changes none of their boundaries.
