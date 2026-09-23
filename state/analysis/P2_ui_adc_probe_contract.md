# D114: one bare-board native A1 diagnostic

Firmware/staging preparation adopted2026-09-24. The user currently reports the
UNO Q alone and authorizes testing.
No extra hardware is requested. D052 supplies bare-board scope; D051 permits
the narrow engineering choice below. This contract is not an upload record; independent tests, exact target/capture
review and one identified run record remain required.

## Purpose and authority boundary

Observe the existing D112 Runner and actual native ADC initialization/failure,
then at most128 raw A1 samples with actual source/callback timing and actual
UNCONFIGURED decoder results. No expected floating-input value/noise/voltage is
specified. An initialization or ownership failure is useful diagnostic evidence,
not successful acquisition. Retain every guard and original result.

D114 narrowly permits this observation-only ADC execution beyond
D078's compile-only scope. SC-AJ remains open: nominal clock lineage and measured
micros intervals are not calibrated physical time or production qualification.
No clock, power, pin, reference, divider, ADC limit or decoder-window value changes.
No PINMAP OK, physical button acceptance, full-app800us, sensor, motor or gate claim.
The current bare-board report establishes the absence of attached peripherals as
human-reported setup only. Whole-image exclusion and native live guards must
independently establish this run's admission; no assumed successful ownership.

References: P2_ui_bare_capture_feasibility.md; D078/D086/D112 contracts and their
exact source/target evidence; D104's deployed-identity-first passive readout.

## Minimal firmware and staging

Use a new explicitly named `bench/ui_adc_probe/ui_adc_probe.ino`, preserving the
ordinary `bench/ui` default-false sketch byte-for-byte. Reuse exactly the existing
four bench/ui/src files; never copy/fork their implementation or move bench code
into the application. The new wrapper differs in purpose/name and the explicit
`Grants{true}` only. It instantiates one existing Native and Runner, invokes begin
once in setup, and one poll per loop. Require MATCH0/MOTORS_ALLOWED0 at compile
time. No new runner, metadata struct, tunable, strategy or hardware module.

Staging gets one literal special case for this named probe: copy the four exact
ui_bench.h/.cpp and ui_bench_native.h/.cpp files into its src after validating the
source ancestry/no symlinks, refusing any destination name collision. Existing
config/core/hal/app copying and source hashing stay unchanged. Never allow a
caller-supplied source path or arbitrary shared-bench include tree. Required
Arduino layout remains build/stage/ui_adc_probe/ui_adc_probe.ino plus src/.

The new checked build route is default-startup/MATCH0/MOTORS_ALLOWED0 only.
Immediate, MATCH and conflicting macro profiles refuse before transport. Existing
bench/ui compile-only behavior and upload refusal stay unchanged. Initially the
new probe also refuses upload. Only after exact source/ELF/package/ownership and
readout review may one separately pinned source entry permit its identified run;
the checked rebuild must reproduce both reviewed loadable hashes before upload.
All old upload keys and guards remain unchanged. Compile-only never uploads.

The Reader's fixed actions remain as audited: A0/PA4 and A1/PA5 metadata, current
analog/no-pull/unlocked pads, unused stock ADC1, inactive DAC channels, idle ADC4,
nominal clocks/supplies/IRQ state and pristine ADC1 checks. PA4 is rewritten to
the same checked analog mode; PA5 is not reconfigured. ADC1 clock enable before
pristine-register admission is an actual side effect even on a later rejection.
Calibration/enable and rank10 conversion occur only after unchanged admission.
Never reset/remux/reconfigure a conflicting peripheral to force success.

Retain D112's bounded per-call work and immutable capture semantics. COMPLETE
ceases native callbacks but normally leaves ADC enabled/idle; it is not an ADC
shutdown. Reader has no stop API. A frozen clock can leave RUNNING indefinitely
with only early polls; this existing limitation is not hidden with an invented
watchdog, fault or successful end marker. The finite host observation below
reports a nonterminal snapshot as such and does not retry/reset it into success.

## Exact target and passive readout

Compile/inspect the enabled image before selecting addresses. Require unchanged
actual Runner/Native/decoder/ADC bodies, sole passive constructor chain, no stock
ADC1 caller, ADC4 producer, DAC writer, motor, matrix, I2C, UART/Bridge worker or
other competing reachable pad/clock owner during/after ADC admission. Expected
stock RCC/PWR/ADC4/DAC pinctrl initialization before admission is audited and
required by the guards; uncalled exports are not execution. Audit the exact
installed loader startup too; a false-grant
D112 ELF or source-only exclusion is insufficient. Preserve the strong empty
loop hook, every native ownership check and actual ordered loader fit evidence.

Derive Runner/Report/Capture offsets and field ABI from the actual debug ELF.
Existing D112 baselines (Runner9892, Report132 at offset16, captures128x76 at148)
are expectations to verify, not addresses to assume. Retrieve the one actual
Runner through the exact relocated BSS mapping after verifying deployed loader
and sketch bytes. Do not invoke MCU functions, halt, reset, write memory or open
a transport peripheral during readout. Reuse immutable reviewed p0_capture
pure helpers without changing their bytes. The new narrow collector follows
D104-style explicit ceilings:48reads/2MiB total/16KiB per RAM read,64commands,
600seconds total and30seconds per command; flash identity reads are fixed64KiB
chunks. These do not change or inherit the different p0.Capture class limits.
Specialize the exact artifact/layout pins and finite purpose-bound reads only.
No heap scan is required for this diagnostic. Precompute the full worst-case
read plan, including at most3LLEXT nodes, before the first MEM-AP operation.

Read Runner twice with unchanged loader/descriptor identity checks bracketing
them. Only identical terminal COMPLETE/FAULT snapshots can be described as
frozen. Preserve original bytes, actual enums, timing history, setup/shutdown,
all committed captures and their real decoder qualifications. Ignore ABI padding;
do not reject an otherwise truthful record because padding is nonzero. Do not
interpret private port pointers as measurements or expected input values.

The decoder must distinguish collection integrity, frozen-state evidence,
successful128-sample acquisition and physical acceptance (always false here).
FAULT is a recorded diagnostic failure; RUNNING is a nonterminal snapshot, even
if two samples happen to match. Unstable snapshots are retained and reported as
unstable; they never become a valid frozen result. Absent/incomplete/unknown or
inconsistent data must not be normalized into success. Exact public decoding
schema and independent literal ABI fixtures are still to be frozen after target
preflight, before decoder execution; no success-shaped summary is invented now.

## Acceptance and identified run

Independent tests first cover opaque reuse/staging/default-disabled old sketch,
one true-grant new wrapper, forbidden profiles/early refusal, all old policy
assertions, unchanged D112 runner tests where impacted, and the pinned decoder's
success/fault/nonterminal/unstable/truncated/identity cases. Default bare wrapper
host substitutions prove call selection, not ADC silicon behavior. Require
separate read-only source/target/readout/guard review with no open safety finding.

Only then write one run record identifying source revision, ADB serial2629958581,
default-startup ELF/package, source/guard/capture/review hashes and scope. One
upload/reset followed by bounded passive collection is in scope under the latest
bare-board testing instruction. Any failed guard, ownership, setup or read remains
evidence; no automatic second upload, reset or changed-firmware retry. A later
fix/run requires its own exact scope/review. No motor-capable run is permitted.

Every command/result and original binary is retained. Any actual result enters
FACTS/TUNING_LOG with clock/reference/electrical limits and measured versus
human-reported provenance. This does not complete P0/P1/P2 physical acceptance,
resolve SC-A/SC-AJ, qualify a connected button circuit or advance a human gate.

## Adoption boundary

This adopts firmware/staging and the diagnostic-only exception after separate
source feasibility/preflight. Public-wrapper tests remain independently authored
before their first execution. No new capture implementation, decoder schema,
artifact pin, upload key or actual run is approved merely by this adoption.
Before those dependent steps, freeze the exact public readout schema/ABI fixtures
and identify the enabled target. Keep original draft/preflight artifacts intact.
