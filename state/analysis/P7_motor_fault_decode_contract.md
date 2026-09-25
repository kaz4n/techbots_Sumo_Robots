# D174 offline motor-fault snapshot decoding

Scope: one pure offline decoder in tools/motor_fault_decode.py, used by a later
capture profile. No firmware/HAL change, native operation or capture admission.
Basis: diagnostic public headers and observed D173 active_abi.json SHA822c917d.
Full hash:822c917d32d5bbbcb209ebfad88fd347b516141f85351b84058b3a5ac4ab77a4.

Public function decode_snapshot(blob) accepts exactly immutable bytes of2592B;
all other types/extents raise ValueError. Interpret ARM little-endian layout only.
The exact observed ABI file is hash-checked; no caller-selected schema/offsets.
Padding, pointers and unused internal Port state are not interpreted. Raw capture
bytes remain the evidence of those fields; the decoder cannot establish origin.

Return a dictionary with status='DECODED', schema='motor-fault-snapshot-v1',
coherence='UNPROVEN', reported_phase (NOT_STARTED/DISABLED/RUNNING/COMPLETE/FAULT),
runner, trace, report and gate. Names inside these objects match source members,
including trailing underscores for private Runner/MotorGate fields.
- runner: attempted_,last_us_,equal_polls_.
- trace: all TraceReport members, including all64 calls plus current/first_failure
  even when their presence flag is false. Never infer a missing/present failure.
- report: all Report members, all4 applied Result slots, and halt. Result includes
  nested feedback with every PreviousTick field; retain uint64 token exactly.
- gate: fault_,initialized_,began_,armed_,hold_complete_,release_us_,last_token_,
  halted_,halt_result_. No callback invocation or pointer dereference.

Booleans must be0/1. Validate enum domains from the public headers: Stage0..2,
Operation0..4, Channel0..3, Phase0..4, Failure0..5, motors::Fault0..6. Retain numeric
enum codes in decoded objects. Require trace.count<=64 and report.applications<=4.
All decoded floats must be finite; retain their finite value without inventing
an electrical-duty acceptance threshold. Rejected/clock/missed/poll counters are
uint32 values, including UINT32_MAX; timestamps receive no ordering assumption.
Malformed input raises ValueError; inputs are never modified.

DECODED denotes structural interpretation only. FAULT, DISABLED, NOT_STARTED,
in-progress callbacks and failed receipts must remain reportable. A COMPLETE
phase is reported firmware state, not proof of atomicity, original fault cause,
physical operation or acceptance. Do not add a success/gate predicate.

Independent tests derive literal offsets/fixtures from the public headers and
actual ABI receipt, without implementation access. Cover all fields/array ends,
padding tolerance, uint64 precision/wrap values, enum/bool/capacity boundaries,
nonfinite rejection, partial/failed/terminal reports and wrong input extents.
