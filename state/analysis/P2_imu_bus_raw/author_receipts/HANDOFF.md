# D079 independent native test handoff

Objective: independently test the real bounded I2C4 MPU6050 transport against its
frozen public contract using source-derived registers/LL operations, without
opening production CPP or executing any MCU/board operation.

Modified files: `tests/native_imu_bus/**`,
`tests/tooling/test_imu_bus_unoq.py`, the explicitly authorized D079-only extension
to `tests/tooling/test_p0_config.py`, and this author receipt directory. No shared
production, locked test, board-tool, config or application source was edited by
the test author. No commit was made by the author.

Final host evidence: 10 Python methods PASS in 138.097 seconds, exit 0. Actual
production SHA-256 is
`940f4e2c8c7a251b7060c5336f54da9e128a4a6fae1b21f5f5851203deb9e0de`.
The exact final run has 102 subprocess receipts: 100 exit 0, and two required
intentional child assertion/signal sentinels returning 1. There are 49 positive
native executions, 83 native test cases, and 992 parent doctest assertions.
Parent totals exclude child assertions. All final native commands used one
identical fixture manifest. `final_native_summary.json` records every receipt
filename/hash and these counts. All 31 new fixture/runner files use LF without
trailing whitespace. The config extension independently passed 12 methods.

The suite covers both addresses; every typed register and read-only restriction;
one-byte and 15-byte reads and two-byte writes; repeated START/AUTOEND/STOP and
W1C behavior; complete zero publication on every failure; error priority and
evidence; partial and extra data; stale state/low pads; setup and runtime resource
ownership; per-pin locks; partial irreversible claims; ignored writes/cleanup;
deadlines/equality/wrap/frozen time/shared polling; late final errors/timeouts;
inert constructors/probe; heap avoidance; and upload refusal before transport
lookup in all eight modes.

Actual first-draft defects and fixture/test corrections are detailed in
`authoring_notes.md`; raw failing receipts remain unchanged. The final boundary
regressions also reflect independent review findings supplied as test source,
not production inspection. No assertion was weakened to fit implementation.

Limitations: modeled native host execution cannot prove physical pad ownership,
clock/supply accuracy, I2C waveforms, sensor identity/configuration/freshness,
whole-tick WCET, bias/heading quality, deployed-loader correspondence or a phase
gate. Target compile and separate fresh review remain coordinator-owned evidence.

Next action: coordinator combines the preserved host evidence with the exact
target compile/source/ELF audit and independent reviewer outcome. Subsequent B3
sensor setup and freshness/heading work remains outside this transport test task.
