# Current default-app fit: bounded investigation

2026-09-24 Asia/Dubai. D139's current default image compiles but exceeds the
conditional loader pool by 592 bytes. This note records a separate read-only
explorer's findings. No source, policy, flag, capacity or test was changed; no
additional compiler or board operation was performed by the explorer.

## Source and metadata inspection

The checked ELF contains 549 global function/object symbols, costing 4400 modeled
bytes. The retained loader counts STB_GLOBAL entries; merely changing visibility
would not remove that cost. Four constructor C2 names without named relocation
references share their C1 addresses, so they are aliases, not duplicate bodies.
Their hypothetical metadata saving is only32 bytes. All six globals without such
references total only48 bytes; the other two are toolchain/runtime functions.
Absence of a named reference does not establish safe removal.

Recorder frames use exact25-byte payload arrays, events exact8-byte arrays, and
statuses are already packed four per byte. The1152-byte dump buffer retains
partial-write data. The earlier native pin-table deduplication is already present:
the checked image has one560-byte table. Two gpio_pin_get_raw bodies duplicate
only32 bytes. Display/formatting inspection did not identify a defensible single
source repair with enough artifact-supported saving. This is a bounded negative
finding, not proof that further optimization is impossible.

Evidence: current [ELF account](P7_default_qualification_raw/app/loader_account.json),
[retained loader](P2_memory_validation_raw/llext_load.c),
[frame storage](../../src/hal/recorder_frames.h),
[event payload](../../src/core/logframe.h),
[shared pins](../../src/hal/native_pins.cpp), and the preserved
[two older failed candidates](P5_default_fit_experiment.md). Neither candidate
was restarted or adopted.

## Existing compiler settings and distinct package option

The [captured properties](P7_default_qualification_raw/app/receipt/properties.stdout.json)
already use -Os for C/C++, function/data sections and linker --gc-sections.
The final ELF is stripped of debug data. Current mode is dynamic and startup
wait. Retained platform, boards and C++ response-file hashes match D139's pins;
the C++ response file contains no later optimization override or LTO flag.
No unused optimization preset was found. Full machine/C response-file contents
were not available in the local retained material, so their expansion was not
claimed as independently inspected.

The pinned [boards definition](P2_bridge_dependency_raw/installed/core/boards.txt)
lines54-57 also exposes link_mode=static. The retained
[platform recipes](P2_bridge_dependency_raw/installed/core/platform.txt) select
static linker scripts, allocation wrappers and -prelinked ZSK packaging.
This is a distinct linking/loading mode, not a stronger optimization level.
Current [app policy](../../tools/app_build_policy.py) admits only dynamic mode.

Next eligible investigation: trace the exact static linker/packaging/loader
contract, placement, startup and native-HAL address assumptions in primary source.
Return exact missing files where necessary. Static fit and compatibility are
unknown. This note authorizes no policy change, static compile, deployment or
replacement of D139's negative result. Any feasibility probe needs a concrete
separately reviewed scope with unchanged safety checks and compile-only limits.
