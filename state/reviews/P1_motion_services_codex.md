# Separate-context scoped review - 2026-09-22

Reviewer: native Codex context `p1_remaining_contract_audit`, read-only. Began as
a spec/header audit, then reviewed actual implementation and independent tests.
This is neither cross-model review nor the full P1 gate. Coordinator transcribes
the reviewer's delivered findings and verdict here; reviewer edited no file.

Scope: base683665b through motion40c8c9c/codec ae3e9e7, then D-024 contract5bfcf70
and the working countdown Services implementation/new locked tests. D-025 is
policy only, pending FSM implementation. All prior locked test bodies preserved.

## Findings and disposition
- RESOLVED MAJOR: largest accepted motion duration could miss expiry across a
  start-relative uint32 wrap at1kHz. Accumulate successive unsigned deltas in
  uint64; keep the accepted range. Exact reproduction is independently tested.
- RESOLVED MINOR: PRNG low-bit parity exercised only fallback in one seeded
  suite. Both suites now explicitly test5,000 healthy and5,000 unavailable cases.
- RESOLVED MINOR: initial contract described only turn/brake. Appended amendment
  records D-022/D-023 and implemented straight/arc/fallback.
- No open BLOCKER, MAJOR or MINOR; scoped verdict **PASS**.

Motion preserves deadlines on IMU recovery, strict heading tolerance, bounded
requests, zero terminal output and D-022 direction-preserving correction. Codec
validates finite fields before bounded conversion;25-byte frames preserve yaw
revolutions and8-byte events retain exact supplied microsecond timestamps.
Services follows half-open windows, max-minus-min spread, minimum2 observations,
invalid rejection and prior-bias retention. Duplicate timestamps create no
observations. Warning latches; snapshot retains latest mask, including zero.
Existing Gate/Buttons/Controller unchanged. No new I/O, heap or motor permission.

Reviewer inspected normal and ASan/UBSan evidence: **182 cases /5,872,365
assertions**, all pass, no skips, exit0; sanitizer compile/link flags present and
no diagnostics. Config checks8/8. Full tooling rerun follows this review.
Initial motion test compile failed because CAPTURE was passed2 arguments;
independent author split diagnostic macros without changing expectations.

## Exact inert source review
Reviewer independently reconstructed and inspected all17 files per sketch and
approved only these byte snapshots for manifest refresh:
- matrix: d214df4f19b438165d2f5307594fdc91a69892340234689963d3e45e1c2883de
- timing: 0d4f83cc88cdf43a431b9aba1b307805e1249f8f032226d146540890169af404

Any future source change invalidates those hashes until reviewed again. Upload
guards, --compile-only and F-061 remain intact; no upload/run approval is supplied.

Production Services composition, raw sample freshness, HAL bias application,
heading reset, complete FSM/MotorGate, recorder storage/overflow, target compile
and actual robot timing remain pending. No board contact or physical measurement.
