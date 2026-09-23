# D086 independent test-author handoff

Objective completed: derive fixed A0/A1 owner tests from the frozen contract,
public headers/config, prerequisite audit and existing native fixture; compile
actual production sources opaquely without reading their implementation bodies.
No board, transport, flash, sensor, motor or physical acceptance action occurred.

## Final validation

`wsl python3 -m unittest tests.tooling.test_adc_pair_unoq -v` passed all **15
methods in 278.692 seconds**, with UBSan enabled by the inherited native runner.
This includes all nine unchanged battery methods and six new pair methods.

- Pair public contract/backward compatibility: eight cases, 63 parent assertions.
- Pair ownership and partial transitions: nine cases, 356 parent assertions.
- Pair time/flags/sequence: eight cases, 112 parent assertions.
- New metadata/configuration variants: 48 independently compiled/executed
  variants, six assertions each. Includes A1 malformed bindings; aliases and
  unknown device bindings for every excluded proposal; channel_a; missing table
  entry; unsupported BUTTON_INPUT_PIN; active QTR_INPUT_PINS aliases/out-of-range.
- Actual pair probe: both macro modes passed one case/15 assertions each through
  constructors, setup and 10,000 loops without native I/O or allocation.
- Eight attempted pair upload combinations refused before target, remote or
  transport lookup. Each refusal is recorded separately.
- Every inherited battery ownership/configuration/deadline/metadata/lifecycle,
  partial-claim, inert-probe and upload test passed without changing its cases or
  assertions. Deliberate isolation assertion/crash sentinels failed as expected.

The ordinary doctest totals above are parent-process counts. The unchanged
isolation listener propagates child failures but does not merge child assertion
totals into doctest's printed parent count. Do not describe these totals as the
complete number of predicates evaluated inside the isolated scenarios.

## Modified files and scope

Added `tests/native_power/pair_cases.cc`, `pair_guards.cc`, `pair_timing.cc`,
`pair_metadata_cases.cc`, `pair_probe_cases.cc`, `README_pair.md`, and
`tests/tooling/test_adc_pair_unoq.py`. The new runner subclasses the existing
battery runner rather than copying its framework.

Five existing fixture files received only the required additive device-tree,
PA5, channel-a, named/foreign GPIO binding, channel-specific sample and rank-write
controls: `native_fixture.h`, `native_fixture.cc`, `wiring_private.h`,
`zephyr/device.h`, `zephyr/devicetree.h`. Default fixture behavior remains intact,
as demonstrated by the complete unchanged battery regression.

No established case/assertion, `test_power_unoq.py`, production source, public
interface, config, build file, shared ledger, phase gate or allowlist was edited
by this author. `final_test_manifest.json` records final test/fixture hashes.

## Preserved initial failures and corrections

All command statuses and streams are saved before failure is raised. The first
run retained three failed receipts:

1. `native_power_1790160036537710445.json`: a new assertion initially prohibited
   all GPIO MODER/PUPDR writes. The reviewer correctly identified that inherited
   D078 PA4 neutral configuration remains allowed. The corrected test seeds
   unrelated GPIO fields and checks every write preserves PA5 and all unrelated
   bits, while continuing to forbid DAC/lock writes. No old assertion changed.
2. `native_power_1790160038924879392.json`: after an injected rank-write readback
   mismatch, the first reported error was READBACK with UNCONFIRMED cleanup.
   The test now expects that precise first error only at the rank-after/malformed
   rank boundary, consistent with the contract's first-failure preservation;
   ownership loss at the other guard boundaries still requires OWNERSHIP.
3. `native_power_1790160040573775497.json`: an initializer mixed host unsigned and
   installed unsigned-long mask constants. A typed uint32 array fixes the fixture
   compilation without changing the flag values or expected outcomes.

Review also found a vacuous destructor check in the new draft. The final test
captures its I/O count before leaving the owner scope and compares it afterward.
Later additions cover final ownership-check time and ADRDY loss at every added
enabled setup transition. All final cases passed the complete run.

`first_failures_index.json` distinguishes the unexpected initial failures from
the expected isolation sentinels. No failed receipt was removed or rewritten.

## Limits and next action

The button-sequence wrap case uses the authorized private-state seam after a
normal successful conversion. It verifies the transition through zero, not
billions of measurements. Fixed-register fixtures establish software behavior
under their declared model; the actual target build remains separate evidence.

No live ownership, pinmap acceptance, A1 settling/carryover, ADC accuracy,
START/BOTH distinction, native call latency, complete-tick schedulability,
SC-AJ/F091 closure or human phase gate is proved here.

Root/fresh reviewer next: complete actual inert target/source/import/startup
verification, full host checks and frozen-source review, then record the final
shared evidence. Tests and fixture source are frozen at this handoff.
