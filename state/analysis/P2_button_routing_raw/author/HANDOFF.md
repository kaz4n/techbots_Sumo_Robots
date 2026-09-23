# D087 independent test author

Objective: derive assertions from the frozen D087 routing contract, public headers,
and applicable B3/B13/B15 and existing MotorGate contracts. Production CPP bodies
were not read to derive expectations. Opaque copying/hashing and executing the
actual compiled source were used for tests. No production, existing or locked
test file was changed by this author; no commit, transport or hardware action.

New files owned by author:

- tests/test_button_routing.cpp: 23 Robot admission, gesture and lifecycle cases.
- tests/test_button_observed.cpp: 8 direct public observed-time service cases.
- tests/test_button_motor_gate.cpp: 1 actual callback-boundary case, three scenarios.
- tests/test_button_events.cpp: 4 metadata, actual Robot/recorder and CSV cases.
- tests/tooling/test_button_decoder.py: 8 unittest methods and embedded C++ fixtures.
- state/analysis/P2_button_routing_raw/author: raw receipts and this handoff.

Final author validation:

- Four new C++ translation units pass strict C++17 syntax checks with
  -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti.
- build/host/sumox26_tests --test-case=*D087*: 36 cases, 113773 assertions PASS.
- build/host/motor_gate_enabled_tests --test-case=*D087*: 1 case,
  46636 assertions PASS; default-disabled counterpart is in the main run.
- python3 -B -m unittest tests.tooling.test_button_decoder -v:
  final 8 methods PASS in 51.571s, exit 0. Earlier 7-method run also passed.

Decoder profiles independently enumerate every raw value 0..16383 in four
synthetic profiles (off, disjoint inclusive, overlap, gaps), six malformed
configurations, all known provider failures/shutdown variants, malformed
status/timing/data and adapter isolation. Profiles are temporary copies, never
production calibration or wiring recommendations. Two actual native probe
binaries use MATCH/MOTORS_ALLOWED 0 and 1, each proving construction/setup and
10000 loops have zero counted native I/O or allocation. Eight mocked upload
combinations reject before any transport lookup. Detail11 passes existing CSV
schema validation without making a hardware provenance claim; semantic reserved
mask rejection is tested at logframe::validEventMetadata/appendEvent.

MotorGate scenarios feed actual Robot results and actual MotorGate feedback each
tick through the complete 5100ms hold, demonstrate nonzero callback duty in the
host-enabled target, then require EN-low and all four PWM-zero writes on explicit
invalid evidence, expiry, and actual ui::applyButtons with production windows off.
This is host callback evidence, not physical motor application.

Receipt files retain subprocess argv, return status, stdout/stderr and staged
source hashes. focused_*.stdout contains the final C++ counts; tooling_*.stderr
contains the final Python summary. final_source_binary_identity.json records the
four C++ tests, Python runner and the two tested normal host binaries. command_*
JSON files retain synthetic/native compile and run outputs and complete copied
source manifests. upload_refusal_* and csv_compatibility_* record those results.

Preserved initial failures and repairs:

- Root initial builds exposed missing explicit <initializer_list> includes;
  the final independent strict-syntax pass verifies all four files.
- The MotorGate fixture originally expected NONE for intentional STOPPED output;
  the public MotorGate contract explicitly requires STOPPED with a valid inhibited
  receipt, so the fixture now expects that status while preserving write assertions.
- The LINE event fixture now supplies opponent_fresh=true to independently keep
  D085 opponent evidence fresh while isolating the intended high fault mask.
- The first author syntax shell loop lost its quoted filename through Windows
  argument handling; syntax_final.* preserves the failure. run_author.py uses
  subprocess argument arrays, and subsequent per-file syntax commands all passed.

Limitations: direct stepObserved unit tests isolate module timing and intentionally
bypass Robot admission; explicit Robot traces test the actual bounded admission
path. No physical ADC windows, fourth distinguishable electrical state, sensor
cadence, MCU full tick timing, live inputs, or human gate is established. Root owns
full-suite/sanitizer runs, target compile identity, final review and evidence closure.

Next action: root incorporates these tests and raw receipts into the D087 closure
after full normal/sanitizer and separate reviewer checks; keep physical gates open.
