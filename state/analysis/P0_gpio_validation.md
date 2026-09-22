# P0 0.4 internal LED GPIO timing: validation

D-064 contract/headerd01e0f6 precedes code/tests. D-051/D-052 allow this bare-board
P0 diagnostic without other connections; no human phase gate or motor authority.
Installed mapping/readiness/ownership: F-080 and
P0_gpio_installed_contract_20260923.md. PH10/index50 is LED_BUILTIN/LED3_R, not D13.

## Software and target checks

- Independent spec/header author, implementation unread:27 GPIO tests (12 opaque
  real-sketch/15 decoder),14 passive-boundary and8 config cases PASS on first
  execution. WSL g++13.3/C++17, strict warnings, UBSan. Receipt:
  P0_gpio_host_tests_20260923.txt. No locked-test or expectation amendments.
- Five coordinator upload tests PASS for both SSH/ADB: default inert source,
  same artifact, compile-only/match permutations, Immediate rejection, altered
  source and failed compilation. P0_gpio_upload_script_tests_20260923.txt.
- Full tooling243 cases PASS in83.219s, exit0, no failure/skip. Receipt:
  P0_gpio_tooling_20260923.txt. Prior core895-case evidence remains separate;
  no unnecessary full-core retest was claimed for this diagnostic-only change.
- Actual board-side default compile-only PASS, source1dfbd571, MATCH0/
  MOTORS_ALLOWED0,76148B program/45416B globals/216728B remaining per compiler;
  no upload during compile. P0_gpio_target_compile_20260923.txt.
- Exact target source/binary audit: P0_gpio_binary_audit_20260923.md. Fresh
  same-model scoped reviewer: reviews/P0_gpio_codex.md. These are separate
  contexts, not cross-model or human gate acceptance. Reviewer independently
  reproduced the focused tests and16 bounded offline layout fixtures.

## Exact capture and upload identities

GPIO source1dfbd5711114e699fec324bcc0b97de7defd37889b5dc81c824dcde69be93dda,
26 staged files. Final ELF46c135bd8d2385e860dcc86ddf577407da9f205721a4a576e14c984836ac934f;
dynamic .elf-zsk.bin a0a36e77e467d4a0f02bf59637f40dda3fa60334acd18e7c3c2c7efd2b093828;
both76148B. Separate .bin-zsk.bin is not the default dynamic upload artifact.
Final BSS size21980/address0x5598. readelf reports section-relative p0Gpio value4,
size14428; nm's0x559c includes the section VMA and must not be used as an offset.
This distinction was resolved before execution; the capture separately pins VMA
and raw readelf offset. The shared passive helper/config remain unchanged.

Exact source maps P0_gpio_inert_manifest_proposal.json were independently checked
before allowlist refresh: matrix5c5a72ac (28 files), timing0d5baec0 (24), ADC18c4dfa8
(25), GPIO1dfbd571 (26). First three differ only by two unused GPIO diagnostic
constants. Their old runtime measurements are not reassigned to the new hashes.

## Physical status and limits

At this pre-upload checkpoint, GPIO has not run. Last actual MCU image remains
ADCf5f637b2/default. A future reviewed upload and passive capture will be recorded
separately.400 samples measure individual configure/write/read calls and the
contiguous configure/write pair; first and subsequent calls remain distinct.
Readiness failure causes no GPIO operations. Mismatch stops sampling and attempts
final HIGH/off; an incomplete or mismatched record cannot pass capture.

Arduino wrappers discard native errors; LOW may mask a read error. Successful
expected readbacks do not recover those codes or prove optical/electrical output.
Microsecond quantization permits0us reported intervals; no overhead subtraction.
Empirical maxima do not prove production contention/interrupt/bus timing or full
robot WCET. Keep a same-host quiet interval before passive readout; completion
before attachment remains independently unproved. P0/QTR/cold-power/optical/
electrical checks and P0/P1 human gates remain pending. No additional hardware,
pin-map approval, B16 tuning, motor action or P2 implementation is inferred.
