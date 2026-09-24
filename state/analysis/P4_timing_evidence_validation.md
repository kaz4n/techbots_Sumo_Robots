# D129 P4 target-loss timing trace validation

Status: IMPLEMENTED / HOST-TESTED / scoped review PASS; no open scoped BLOCKER or MAJOR.
Target compilation, native fit and physical
acceptance remain pending. Active phase is P4 software under D128.

The default-off P4 trace records one candidate's opponent acquisition window,
actual target-loss brake decision and full-token-matched applied-zero receipt.
It does not change motion, source grants, pins, defaults or run authorization.
The exact `bench/reactive_timing` wrapper is inert with empty setup grants.
The adopted contract is `P4_timing_evidence_contract.md`; implementation began
in preserved WIP `1b47ee0c` after contract `ca076b46`.

## Actual host evidence

All completed commands, exit statuses, CMake caches and CTest logs are retained
in `P4_timing_evidence_raw/`. WSL Ubuntu uses g++13.3.0, CMake3.28.3 and
Python3.12.3. Builds and compiler scratch use `/dev/shm`; coordinator invocations
are `wsl -d Ubuntu -- env TMPDIR=/dev/shm python3 <runner> [arguments]`.

| Runner / arguments | Actual result |
|---|---|
| `run_host.py normal first_retry` | PASS, 30 cases each M0/M1 |
| `run_host.py normal` | PASS all 14 targets: 1519 main, 187 Gate, all prior profiles and new timing targets |
| `run_host.py sanitize` | PASS, 30 cases each M0/M1 under ASan/UBSan |
| `run_host.py configured` | PASS, 32 cases each M0/M1 with synthetic button windows |
| `run_host.py configured_sanitize` | PASS, same 32-case profiles under ASan/UBSan |
| `run_registry.py` | PASS, 2 unchanged registry methods |
| `run_tooling.py`, first completed run | 148/149 PASS; new guard-spelling oracle failure, preserved |
| `run_tooling.py`, corrected new oracle | PASS all 149 methods, including exact-wrapper valid/16-invalid macro matrix |

The button overlay is confined to test fixtures; actual configured windows remain
unset. Host M1 uses simulated electrical boundaries and is not a powered run.

## Preserved findings and independence

Separate reviewer found one MAJOR chronology gap: after trace onset, a caller
could backdate the current tick before the previous completion and reuse an old
source interval. The owner already marked incomplete evidence, but the trace
could incorrectly reach a completion marker. Conditional `timing_epoch_valid`
now carries the existing receipt chronology qualification into source admission.
The original independent reproducer failed 4 of 40 assertions; unchanged after
the repair it passes all 40 normally and under sanitizers. Eight further private
cases pass per M0/M1. The six prior host profile layouts equal D128 exactly.
Instrumented host sizes are separate diagnostics, not MCU memory measurements.

The public test author froze 30/32-case expectations before execution without
reading production bodies. The completed tooling failure requires `#if/#error`
syntax; the actual wrapper instead has an exclusive inert C++ `static_assert`.
Author and separate reviewer agree the contract specifies rejection semantics,
not syntax. Only the new unaccepted tooling oracle was corrected to compile
the exact wrapper against declaration-only stubs with valid/invalid macro
matrices. Production and every locked test remain unchanged by that correction.
Original oracle, first failure and bounded adjudication are retained in
`P4_timing_tooling_oracle_analysis.md`, `original_oracles/`,
`tooling_first_completed.*` and `corrected_oracle/` under the raw directory.
Original test hash178ae1a1 and corrected4b9e896f are both bound; the corrected
suite passed on its first execution. All640 other original frozen files and
all39 established locked files remain exact. `final_validation.json` binds these
files, actual completed commands and per-target case counts. No C++ rerun was
needed after this tooling-only correction.

The initial concurrent host/tooling/private jobs were interrupted by the recorded
WSL service termination at 10:12:13 Dubai. Their partial logs and absent completion
are preserved; these are not semantic test outcomes or failed source repairs.
Subsequent validation is serial. User-authorized cleanup is recorded separately
in `DISK_CLEANUP_20260924.md`, commit `43319eec`.

See `../reviews/P4_timing_evidence_review.md` for the separate same-model review,
its disclosed prior options work, private evidence and findings. This is neither
cross-model review nor a human phase gate.

The new locked timing safety oracle is accepted after these passing checks and
review: `e384e7fbe3b3ab0123d77b1ef6200c3545d88450e5dc4fa99109b3f33e1296d8`.
It is now protected alongside the39 unchanged prior files; see
`accepted_locked.json`. No existing locked assertion was amended.

## Remaining work

Fresh ADB inventory found no board; no D129 native compile, upload, reset or MCU
run occurred. Prepared compile-only/accounting runners remain unexecuted. Verify
exact source/ELF/default compatibility and conditional native loader fit when
the board build environment returns. D128's previous native sizes do not prove
D129's fit. Full-source WCET, live RAM/stack and actual P4.1-4.7 remain pending.

The next offline task is the separately proposed D130 interval analyzer. Positive
push-through is another remaining software dependency: the current assertion
requires `EDGE_PUSH_THROUGH_MS=0`; do not remove it merely to permit tuning.
See `P4_software_acceptance_packet.md`. No physical gate or run permission follows.
