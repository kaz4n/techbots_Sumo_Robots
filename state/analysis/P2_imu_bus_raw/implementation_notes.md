# P2 B3 native transport implementation handoff

Objective: implement only D079's private, bounded native I2C4 MPU6050 transport and
an inert retained-method probe. No application integration, sensor interpretation,
hardware execution, upload, or phase acceptance is part of this change.

Owned files: src/hal/imu_bus_unoq.cpp; private declarations/state only in
src/hal/imu_bus_unoq.h; bench/p2_imu_bus_compile/{p2_imu_bus_compile.ino,
src/imu_bus_probe.h,src/imu_bus_probe.cpp}. Shared config, contract/public API,
independent tests, ledgers and inert upload manifests are parent/other-agent owned.

Source binding: P2_i2c_native_audit.md/raw, P2_i2c_timing.md/raw, installed U585
CMSIS/LL definitions and existing source-verified RCC/EPOD predicates. The source
uses deferred I2C4, PD12/PD13 AF4 and the published 0x40EB202C profile. GPIO pull,
type, speed, alternate function, clock source, supply, device state and both IRQs
are checked. No stock Wire/native I2C transaction API is used.

The implementation has one irreversible boot claim, exact controller/pad readback,
one request budget shared across every byte/phase, private result staging and
terminal PE-disable-only cleanup. The device and application ownership premise is
explicit; these finite observations are not an atomic hardware snapshot or a
proof of whole-loop WCET. DISABLED proves only the checked local PE state.

Preserved failures on draft CPP SHA256
82b0c3314b93095da723aadc11347e685b094fa011faa5dfd03974f35fa55e43:
- The selected LL pin-lock helper required all mask bits: each individually locked
  pin escaped the combined-mask guard. Fixed by checking each selected pin.
- A pad mutation during pristine ISR observation escaped the earlier pad check.
  Fixed by rechecking environment and pristine pads before consuming the claim.
- Accepted time preceded the ownership/PE scans, and final transfer errors could
  arrive after the last ISR observation. Fixed with final error observations and
  elapsed timestamps after the scans being accepted.
- Protocol diagnostics now retain unexpected event/target status bits according
  to the root's D079 addendum; allowed progress bits are not classified as errors.

Independent author receipts and reviewer snapshots preserve original failures;
no independent assertion was edited by the implementation author. In particular,
reviewer boundary_1790148813696576940 retains all four original final-boundary
failures. Regression reruns and final actual-target evidence are coordinated by
root and the two independent agents.

Repair batch frozen CPP SHA256:
940f4e2c8c7a251b7060c5336f54da9e128a4a6fae1b21f5f5851203deb9e0de.
Local static checks: git diff --check passed owned files; 35 functions were counted,
maximum 30 lines. No broad test suite or board command was run by this agent.

Limitations: MSI clock qualification (SC-AJ), physical address/pull-ups/waveforms,
measured fault timing/WCET, sensor reset/configuration/readback, data-ready/age,
axis transform, bias and heading remain separate work. No human gate is implied.
Next action: independent regression/review and root's final compile/source/ELF
binding, followed by parent disposition of this software-only increment.
