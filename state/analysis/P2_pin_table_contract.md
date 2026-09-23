# D106 single native pin table

2026-09-23 Asia/Dubai, selected under D051/D075. This is storage deduplication,
not a new pin map or approval of any proposed pin.

D105 default source c05916c6 compiles but its modeled loader peak263112 exceeds
the262144-byte pool by968 bytes. Inspection of its predecessor's exact target
ELF found four560-byte installed `arduino_pins` tables, each byte-identical and
with the same70-relocation sequence. The consumers are motor_port_unoq.cpp,
line_qtr.cpp, opp_sensors.cpp and power.cpp. Save duplicate copied data while
preserving the installed table's meaning and every native owner check.

## Fixed interface and semantics

New `src/hal/native_pins.h` declares, only for ARDUINO_ARCH_ZEPHYR:
`namespace native_pins { extern const gpio_dt_spec* const TABLE; extern const
std::size_t COUNT; }`. Forward-declare the native descriptor type; do not define
a second representation. A single native_pins.cpp includes the installed
wiring_private.h and binds TABLE to its genuine static table; COUNT is derived
with sizeof, never a guessed constant. Static constant initialization only.

The table and descriptor references remain const and stable for the complete
firmware lifetime. There is no accessor call, initialization operation, mutable
owner, heap, fallback pin, dynamic constructor or I/O. Preserve exact count,
entry order, descriptor bytes and relocation targets. Entries still refer to
the installed core's device objects. No copied handwritten pin assignments.

In the four consumers replace only the direct table/count dependency. Preserve
all existing bounds validation before dereferencing, alias checks, setup grants,
native metadata/register checks, operation order, errors and cleanup. The old
per-translation-unit tables must disappear from the final retained ELF. Do not
edit configuration, device tree, installed core, pin constants or locked tests.

## Evidence and ownership

Coordinator owns this decision/interface, mechanical standalone-test source
link lists, target collection and ledgers. Implementation worker owns new
native_pins.cpp and the four consumers. Independent test author derives a small
cross-translation-unit descriptor/count identity test from this interface and
existing native substitutes, before reading implementation. Existing native
assertions and traces remain unchanged; only source-copy/link lists may add the
new dependency. A reviewer checks source diff, immutable predicates and actual
target bytes/relocations. A same-model context is not cross-model review.

Required validation: unchanged motor/opponent/QTR/ADC native suites, relevant
sanitizers and full host suites; positive cross-TU identity/count and invalid
index rejection; default/Immediate/MATCH target builds, one retained table,
unchanged imports/startup and exact ordered loader fit. D105 calibration tests
remain unchanged and must still pass. Measure final net saving including new
pointer/count data, symbol metadata and changed instructions;1680-byte gross
duplicate payload removal is not the final saving or actual loaded free RAM.

No firmware upload, reset, native sensor activation or physical acceptance is
part of this task. Current MCU remains the frozen D104 inert probe. Preserve all
initial failed-fit artifacts and report any remaining capacity deficit honestly.
