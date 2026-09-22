# D-063: startup-only A0 API timing

P0 0.4 explicitly requests bare-board analogRead timing before 0.5 pin acceptance.
D-051/D-052 permit this inert diagnostic; no external part is requested. Installed
source/binary verification is in P0_adc_installed_contract_20260923.md. A0 is
ADC-only PA4/channel9/index14 here. No robot pin assignment or PINMAP approval is
inferred. Stock analogRead has indefinite waits, including warmed calls. Therefore
all calls occur in setup; loop is empty. This is not an R4 production solution.

## Measurement and public record

New bench/p0_adc contains no Matrix/Bridge/UART start, digital output or motor path.
MOTORS_ALLOWED must be0 at compile time. config::P0_ADC_PIN=14 is checked against
the installed named A0 macro at compile time. config::P0_ADC_SAMPLES=1000.
Do not set analog resolution; measure the installed default10-bit API.

Expose volatile p0::AdcCapture p0Adc in zero-initialized BSS, defined by
bench/p0_adc/src/adc_capture.h. Fields are version, complete, completed, start_us,
end_us, then1000 AdcSample records (overhead_us, elapsed_us, signed value).
All fields are32-bit, record size12020B, sample size12B. Version1.
setup writes version1 and start time; for each sample, measure a pair of adjacent
micros calls, then a separate before/analogRead/after interval. Store unsigned
wrap-safe deltas and returned value; increment completed only after that record
is fully stored. Finally store end time then complete1. No call is discarded;
sample0 includes first-use initialization, samples1..999 are subsequent calls.
After return, no field changes and no peripheral API is called by sketch loop.
If an ADC wait never returns, complete remains0: report incomplete, never success.
Host substitution cannot prove real ADC liveness. No outer timeout is claimed to
cancel the MCU call. No watchdog or board reset recovery is introduced.

## Capture and acceptance

Use a dedicated tools/p0_adc_capture.py, reusing only the hash-pinned existing
p0_capture.py passive MEM-AP mechanics and unchanged p0_mem_read.cfg. Exact final
ELF/binary/source identity and layout are pinned after compile and independently
reviewed before upload/capture. Verify deployed loader and complete sketch bytes,
LLEXT/BSS identity and two identical frozen records; reject incomplete/version/
count/layout changes. Preserve raw dumps and command receipts. No halt/reset or
MCU data/register write is permitted during capture. The existing120s capture,
16-read and16384B per-RAM-read limits remain unchanged. Capture after setup has
finished; do not include debug activity in the sampled interval.

Public pure decoder: analyze_record(data: bytes) returns version, samples,
total_elapsed_us, first_call {elapsed_us, overhead_us, value}, subsequent_calls
{samples,min_us,max_us,p99_us}, overhead {min_us,max_us,p99_us}, zero_results,
nonzero_results, value_min, value_max. Nearest-rank p99, no overhead subtraction.
Require exact12020 bytes, complete1/completed1000/version1, all values0..1023,
all measured intervals and total <2^31; total must cover the sum of elapsed and
overhead intervals. Uint32 timestamp wrap is accepted. Invalid input raises
ValueError. A zero result is indistinguishable from the wrapper's error return;
report zero_results as ambiguous, never as calibrated zero volts. Nonzero results
establish successful wrapper conversion paths only under the audited source.
Floating A0 values have no voltage accuracy, battery or electrical acceptance.

Test independently from this contract/header: first-use versus warm separation,
exact count/order, changing signed values, timestamp wrap, frozen empty loop,
motor compile rejection, corrupt/incomplete records, nearest-rank statistics,
zero ambiguity, compile-only/failed-build/source-identity upload safeguards.
Extend upload allowlist only for exact reviewed p0_adc/default. Immediate p0_adc
upload remains disallowed; compile-only remains allowed and cannot upload.
No B16 changes, HAL implementation, phase gate or full-loop WCET claim.
