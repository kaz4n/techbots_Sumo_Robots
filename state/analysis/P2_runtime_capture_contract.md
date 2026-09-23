# D104 fixed Runtime diagnostic decoder and capture

This specializes P2_runtime_inert_contract.md; the public C++ ABI is authoritative.
Prepare tools/runtime_capture.py as a separate entry, leaving D091 unchanged.
The coordinator will pin exact reviewed target paths/hashes before execution.
Unset pins always refuse before any memory command. No target upload in this tool.

## Pure public decoder, frozen before independent tests

`decode_diagnostics(blob: bytes) -> dict` performs no I/O. Exact immutable bytes
only,232 bytes,58 little-endian uint32 words: sequence_front;48-word Report;
8-word StackSample; sequence_tail. Require matching nonzero even sequences,
Report schema1/size192, six reserved words0, and terminal phase FROZEN2 or FAILED3.
Phase2 requires failure0; phase3 requires failure in1..12. Reject malformed data
with ValueError, including wrong type/length, unknown enums/bits and bad sequence.

Result keys are sequence, report, stack, acceptance. report maps the42 named
uint32 fields in runtime_bench.h in exact declaration order; reserved words are
not omitted from validation. stack maps its8 named uint32 fields in header order.
acceptance is `{passed: bool, failures: list[str]}`. A structurally valid FAILED
diagnostic decodes honestly with passed=false; it is not malformed merely because
the experiment failed. Unknown domains: Runtime phase0..4/fault0..5; Transaction
phase0..4/fault0..6; Robot state0..11; contract fault mask0..1023; escape0..4;
Gate fault0..6; receipt mask0..15; absent mask0..31; init boolean0/1; recorder0..4;
stack.valid0/1 and stack.fault0..5. Preserve every raw value without normalization.

Acceptance fails with deterministic reason strings in this order (include each
at most once): probe_failed, runtime_state, owner_fault, source_state,
recorder_state, nonzero_activity, counts, timing, stack_invalid.

- probe_failed: terminal FAILED instead of FROZEN.
- runtime_state: Runtime not RUNNING1, Transaction not IDLE1 or Robot not BOOT0.
- owner_fault: any Runtime/Transaction/contract/escape/Gate fault is nonzero, or
  receipt_flags differs from15.
- source_state: input_absent_mask differs from31 or initialization_complete is1.
- recorder_state: recorder not EMPTY0 or any frame/event count is nonzero.
- nonzero_activity: any enabled_requests/nonzero_requests/invalid_requests nonzero.
- counts: epochs<200000 or epochs>=uint32max; missed_releases nonzero; last64-bit
  token differs from epochs; setup_enable!=1,setup_pwm!=4; enable_low!=epochs+1,
  pwm_zero!=4*(epochs+1),settle!=epochs+1; clock_calls==0 or saturated uint32max.
- timing: elapsed not in[200000000,201000000); first S/D/C or last S/D/A/C is
  not ordered from boot in the forward half-range domain; first C is later than
  last S (except the impossible success one-epoch case, already rejected by count);
  final C<200000000 or>=201000000 from boot; first C>=1000000 from boot;
  elapsed precedes final C; maximum_execution_us is0 or smaller than either
  first/final C-S; maximum_runner_us is0 or smaller than maximum_execution_us,
  or either maximum is outside the forward half range. Natural uint32 wrap is
  valid. These are MCU-clock bounds only, not calibrated physical seconds.
- stack_invalid: valid!=1 or fault!=0; region start not4-byte aligned or outside
  [0x20000000,0x200C0000); region size0/overflow/outside SRAM; delta>size;
  minimum_sp not4-byte aligned or outside[start,start+size-delta]; samples0 or
  saturated uint32max; sampled_headroom_bytes != minimum_sp-start.

For a FAILED partial Transaction, timing/count reasons may also appear; this
does not overwrite the first firmware failure or pretend a successful epoch.
Malformed enum/structural data is rejected before semantic acceptance. A valid
stack sample establishes observed callback-site headroom only, never watermark.

## Concrete capture boundary

Keep the D104 bounds unchanged:48 reads,2MiB total,16KiB/RAM read,64 commands,
600s sequence,30s command. Use the reviewed existing p0 fixed OpenOCD MEM-AP
config/tools/loader hashes plus the pure recorder_heap decoder. Copy/adapt the
explicit guarded capture code if needed; do not mutate old globals, manifests,
caps or D091 entry. No arbitrary address/size/command/path CLI escape.

Pin one ARTIFACT_DIR, ELF_HASH, BINARY_HASH and helper/tool hashes after actual
target review. The public `Capture` class and check_identities/read_layout/
verify_flash/find_bss/read_pool/capture_values/main may follow D091 signatures
for bounded test reuse, but every diagnostic purpose binds runtimeDiagnostics
and232B. All artifact names are runtime_inert.ino.elf and
runtime_inert.ino.elf-zsk.bin. Retain default-only flags0 reviewed source provenance.

Before private RAM, verify local pins, exact flashed loader and exact new sketch
bytes using fixed indexed64KiB flash chunks. Calculate complete maximum read
budget from actual image length before the first MCU read, accounting for up to
three196B LLEXT nodes. Refuse overbudget, never widen a cap at runtime. Only fixed
list/descriptor/node/diagnostic/pool purposes and ranges are legal. One attempt
per purpose; count failed attempts/bytes before invocation. Failure never retries
or reports CAPTURED. Windows/network process execution is outside this board-
Linux entry; root uses exact SSH/ADB commands and preserves exit status.

Require two identical terminal diagnostics and an unchanged24B pinned heap
descriptor; decode/compare the two262144B heap snapshots via recorder_heap.
Preserve all raw bytes, commands, identities, clocks and errors. CAPTURED is
successful collection; acceptance.passed separately says whether this experiment
passed. Neither status implies the full-app image, sensors, motor paths or gates.
