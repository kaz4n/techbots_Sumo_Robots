# D184 scoped inert diagnostic run review

25 September 2026, Dubai. Reused same-model reviewer context; this is a concrete
scope review, not a fresh phase-gate review. Implementation was read-only. The
reviewer inspected local source/receipts and computed local hashes/projections;
no project tests, compiler, network/device command, upload or capture was run.

## Findings

No open BLOCKER, MAJOR or MINOR finding for the proposed bounded inert attempt.

Reviewed scope: state/analysis/P7_motor_fault_raw/inert_run01_scope.json,
SHA256 e9fb5248b1e9719c6a5382704614fb8c4457c2ac8f2268207166c46bae425827.
Reviewed plan: state/analysis/P7_motor_fault_run01_plan.md,
SHA256 c2de55761d33834b4b47082e117f913bb9439c4cc23323fd4f12a7dd19c85662.
Both were uncommitted during this review; native_inert_run01 was absent.

The scope selects the unchanged D179 caller and fixed run
motor-fault-8f592937-run01, board2629958581, fresh boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. It supplies no arbitrary command, source,
artifact, pin, timeout or target override. Its four source hashes match the
reviewed caller/oracle/contract/prior review. Independent local hashing also
matched all nine fixed inputs, six preparation provenance files and the pinned
Windows ADB executable:20checks, no mismatch.

## Admission and artifact evidence

The raw admission_20260925_1552 receipts retain the initial get-state exit0 and
device response together with the ADB40-to41 daemon restart stderr and resulting
host assertion. This is not represented as a clean first admission or an MCU
operation. The two subsequent inventory receipts independently have exit0,
empty stderr, COLLECTED and the exact fresh scope identity. The reviewer checked
their recorded argv against the frozen commands and recomputed their nonidentity
projections: both match the baselines, omitting only the existing timestamp
fields. Non-boot identity also matches both historical baselines exactly.

The capability receipt reports the same boot and UID1000, with no-bytecode,
bz2 and canonical Base85 checks true. The isolated command remains the fixed
D179 query. local_composition.json records fresh-boot upload/capture command
sizes28984/25236 UTF16 units including NUL, within the unchanged30000 limit;
it records no owner or action dispatch.

The identified artifact remains D172 source8f592937, default-wait/dynamic,
MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1. D172 verified provenance and
D173 ABI match raw ELFf9460a16 and packaged sibling b4416792,29836bytes each.
The diagnostic performs four zero-output MotorGate applications; the grant
selects this existing inert diagnostic and does not enable a motion profile.
The Runner layout remains2592bytes in2632byte BSS, alignment8. The bound capture
retains its finite24-read/593424byte ceiling and two Runner snapshots.

These retained files establish artifact provenance, not fresh remote artifact
existence. The unchanged uploader must still verify every bound current file,
directory, absence, process and identity before its native upload child. The
plan explicitly preserves that prerequisite; this review does not waive it.

## Execution boundary

After committing these exact inputs and this review, use the containing clean
HEAD40 for the existing check-only admission, then at most one execute attempt.
The caller independently checks committed scope equality, executing source,
all pins, current HEAD, absent owner and the immutable command set. Its exclusive
fsynced claim precedes all transport. A changed or consumed scope fails closed.

The existing sequence remains three prerequisites, one upload, three prerequisites,
one conditional capture and three closing prerequisites: at most11transports.
Capture requires the actual strictly accepted upload envelope. Local timeouts
remain195seconds/630seconds, with independent final checks and durable failure
evidence. Failure or uncertainty consumes the attempt: no retry, extra reset,
fallback upload, rebuild or old-boot reuse follows. A host timeout does not prove
that remote execution stopped. Any later retrieval must remain bounded to the
actual saved evidence and preserve its hashes before offline decoding.

## Verdict

PASS for this single existing inert diagnostic upload and conditional capture,
subject to the caller's unchanged committed-scope admission and live checks.
This is a technical scope disposition, not motor-run permission or acceptance.
The user-requested connected testing supplies the task authorization; this review
adds no authority for motor-capable firmware. No PINMAP, physical qualification,
current main-app target qualification, live RAM/WCET, atomic capture, diagnosed
root cause or human phase gate is established. Retain the observed outcome even
if the experiment fails.
