# D094 validation failures and disposition

2026-09-23 Asia/Dubai. Preserve original receipts; no established or locked test
was edited. The new author worked from public contracts/headers, not production
CPP. A separate fresh same-model reviewer reproduced the production issue.

Initial full normal/sanitizer runs (`raw/host_*_01`) each failed six assertions
in two new cases. IDLE/unknown native progress with a default nonOK transfer was
classified TRANSPORT before its envelope was checked. This skipped cancellation
despite no trustworthy terminal state. Reviewer classified MAJOR. Root's one
production correction checks for a declared COMPLETE/FAULT envelope first; all
other nonPENDING states abort with RESPONSE and one cancellation.

The next full runs (`raw/host_*_02`) confirmed those six failures were fixed but
exposed a contradictory new authored expectation: another test combined unknown
state77 with NACK and expected terminal TRANSPORT/no cancellation. D051/D094
clarification is explicit in P2_imu_resume_contract.md: unknown/IDLE cannot certify
native termination regardless of status; only declared COMPLETE/FAULT gets the
existing nonOK precedence over remaining pulse/shape/time checks. The independent
author changed that new transport test to FAULT, retained its malformed pulse/time
checks, and added unknown/IDLE+NACK rejection/cancel coverage. Original expectation
and rationale are retained in raw/author/authoring_notes.md. This is not an
established-test exception or a second unsuccessful production repair.

Other retained harness failures: initial pure-test REQUIRE macro was incompatible
with this project's no-exceptions doctest mode, and range-copy loops triggered
-Werror. Explicit checked prerequisites and const references corrected the new
harness. The first native poll-limit fixture tried to halt START after hardware
had already acknowledged it; disabling subsequent byte progression exercises the
intended frozen wait without changing the poll expectation. Exact commands,
source snapshots and diagnostics remain in raw/acquirer_worker and raw/author.

Here `raw/` denotes `state/analysis/P2_imu_resume_raw/`; final successful
counts, identities and independent disposition belong in P2_imu_resume_validation.md.
