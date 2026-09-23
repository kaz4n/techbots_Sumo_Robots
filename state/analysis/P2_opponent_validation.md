# D076 native opponent inputs - software verification

2026-09-23 Asia/Dubai. Contracts98adcda/3c39bc4; baselinea806e05.
D075 permits software preparation before physical acceptance. This is the real
P2 B1 native GPIO driver, not physical B1 acceptance or app integration.

## Implemented behavior

`src/hal/opp_sensors.cpp` validates the complete proposed bank before setup,
configures seven input-only pins using checked native APIs and preserves signed
failure codes. Read snapshots distinguish valid electrical HIGH/LOW from errors,
retain per-channel status/validity and actual start/end timestamps. Core retains
the sole polarity/debounce conversion. No previous reading becomes a new sample.
No constructor I/O, output/pull configuration, allocation, wait or retry loop.

Only config addition is HARDWARE3's existing proposed pin array11/12/13/16/17/18/19;
no B16 value changed. Existing locked tests, core and app are unchanged against
baseline. The app remains inert; invalid-snapshot integration policy is future
work. This does not approve the proposed wiring or certify a detected voltage.

## Independent tests and review

Separate author used contract/public headers and installed API evidence without
reading implementation cpp.18 native unittest methods cover210 scenario processes,
65 successful native builds and one deliberately rejected motor-enabled probe.
All128 electrical masks, seven failure positions, signed/unexpected-positive
statuses, malformed mappings, retries, timestamp wrap, exact bounded API calls,
no-allocation guards and real core polarity composition are included. A later
strengthening proves begin invalidates previously ready state on a malformed map.
Fixtures compile the actual production source under strict C++17 and UBSan.

Author18 tests PASS48.076s plus nine config checks PASS0.046s; strengthened method
PASS3.047s. Fresh separate same-model reviewer reproduced18 PASS46.168s, strengthened
method PASS1.080s and config9 PASS0.083s. Review: `../reviews/P2_opponent_codex.md`,
PASS/no open findings. This is separate-context review, not cross-model review.
Installed typedefs exactly match fixtures; raw header/hash evidence is retained
in `P2_opponent_raw/installed_typedefs.json`.

Initial author run had two probe fixture failures because temporary src/config.h
was missing. The correct staging copy repaired both; assertions were not weakened
and production required no repair. Original observed transcript and retry receipts
are retained under independent_first.txt/independent_retry.*. Review's first upload
check caught the wrong exception class; its harness-only correction and original
error remain in its rejection receipt. No repeated unsuccessful production fix.

Aggregate final regression: normal host CTest2/2PASS4.79s; ASan+UBSan2/2PASS36.50s,
with1030cases/20982541assertions in the default suite and37cases/3796846assertions
in the host-only enabled MotorGate suite, no failures/skips. Exact build/run
commands and returncode0 are in opponent_host/opponent_sanitize_build/
opponent_sanitize_tests receipts under P2_opponent_raw. The normal CTest output
reports target passes; the verbose sanitizer output additionally records counts.
These host measurements do not establish an MCU execution-time bound.
Full controlled tooling suite:400tests PASS272.556s, exit0, including the final
strengthened native test and reviewed inert guards. Raw opponent_tooling.json/txt
also retain the separate existing25-case/156553-assertion candidate replay.
Receipts were produced by the existing P2_motor_gate_record.py utility and moved
unchanged from its default folder to P2_opponent_raw; no old D075 receipt changed.

## Actual target compilation and offline inspection

Actual board Linux CLI1.5.1/corearduino:zephyr1.0.0 via USB2629958581:
`python tools/board_tool.py flash bench/p2_opp_compile --compile-only`, exit0.
Source ef44ace309afc50dfdd85c583e22a74c76ddbe6e06108809a878b3555416c9f8;
MATCH0/MOTORS_ALLOWED0/default. Program76308B, compiler-accounted memory31032B.
These figures are not free RAM or complete-firmware memory measurements.

Probe setup publishes a never-called function pointer; loop is empty. Actual
native begin/read bodies are retained. Three ELF artifacts, relocations, imports,
five init-array entries and native exports are in P2_opponent_raw/target_elf.json;
all31 inspected device/clock imports resolve nonzero. GPIO wrappers dispatch
through native device APIs, without the installed zero named z_impl_gpio exports.
Reviewer matched all36 staged source files and exact aggregate source hash.

Only existing five inert source guards were refreshed after independent review;
their old/new/per-file maps are in P2_opponent_review_manifest.json. No new upload
allowlist. Six author and eight reviewer controlled upload combinations reject
before target/transport; probe with MOTORS_ALLOWED1 is rejected by static_assert.
No upload, reset, pin read/configuration, MCU execution or motor action occurred.

## Remaining physical and integration work

Installed audit P2_opp_gpio_audit.md/raw validates actual mappings/API paths and
identifies SPI2 conflicts with front sensors/proposed EN, Wire2 with rear sensors.
Exclude competing same-pad APIs and serialize shared-port setup. Native checks
cannot detect every broken/floating wire or later mux takeover. B1 live matrix,
polarity, ranges and60-second empty-ring readings are still unmeasured.

F091 inherited platform constructors/Bridge loop hook remain unqualified; this
inert source audit does not establish bounded full runtime, Linux independence or
the800us worst-case tick. No human EXPLAINED/PINMAP/GATE or run authority follows.
Continue real P2 software under D075, preserving these explicit limits.
