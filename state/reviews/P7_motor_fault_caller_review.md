# D179 fixed inert caller review

2026-09-25, independent same-model Codex context. This reviewer read the contract,
implementation, reused APIs, frozen oracle and execution receipts. The reviewer
did not implement or execute the caller/tests, contact a device, or change source
or tests. This is not human or cross-model review.

**Verdict: PASS for host preparation. No open BLOCKER or MAJOR finding.**

## Reviewed inputs

- Contract: `P7_motor_fault_caller_contract.md`, initial `dff9ff96`, public-seam
  clarification `924b16e8`, local digest clarification `35f51823`.
- Caller: `d8418fad`, 23100 bytes, SHA256
  `8b47b1d6e9073179e4f587e09ce04e1a1c0cfc6797daf3151d0a7126d279f56a`.
- Independent oracle: original `5fb59139`, SHA256
  `d298ec01fd9c08afd955a81dc2514da6b7043a380910342a47398950d908efa8`;
  corrected fixture commit `6e3d69c8`, 41792 bytes, SHA256
  `2260d0bc3451473c8b62b87ae7ae126a2b1eeb5a67583393a2c3d32005e1460c`.
- Existing pinned `startup_run.py`, `compile_motor_fault.py`, `inert_actions.py`,
  preparation/provenance, uploader/collector/helper and both baseline inventories.
  Reviewer independently checked all 24 corrected-freeze byte counts and hashes.

## Findings and contract assessment

Admission requires a committed, HEAD-bound fixed scope, rejects malformed/duplicate/nonfinite
JSON and pins the executing caller. Both historical baseline query programs read
current identity; they do not embed their old boot. Non-boot identity must match
both baselines exactly, including JSON types. Only copied binding boot IDs change.
Every other baseline field is compared through the existing timestamp projection.

The caller uses explicit permitted local-method aliases and unbound transport;
it does not construct or run the consumed compiler/static launchers. Pinned
modules load under registered non-main names, without process or device calls.
The new caller does not change historical scopes, environment or dependency pins.

Exclusive owner creation, device/inode checks and fsynced exclusive inputs precede
transport. Failed claims retain their owner and cannot dispatch. Immutable command
choices and local checks guard action use. Intent is durable before dispatch, each
action is consumed before its transport, and capture requires the actual checked
upload envelope. The fixed successful sequence is 3 prerequisites, upload,
3 prerequisites, capture, and 3 closing prerequisites: 11 transports maximum.

Prerequisites and closing local checks retain independent failures. Transport
exceptions retain up to eight unique causal links with explicit truncation and
preserve the actual thrown exception. Closure preserves the original first_error,
attempts both final files independently, and marks failure before result.json
when an earlier counter/final-check write fails. D177 sequence_result attachment
remains intact. No retry, staging, decoder or acceptance inference was added.

## Original failures and narrow oracle corrections

`caller_first.json` records 44 methods: 42 passed, 1 failed, 1 errored, no skips.
Both failures were independently adjudicated as new-fixture errors before edits:

1. The dangling-owner fixture called a helper asserting lexists=False after
   deliberately creating a link that the contract requires preserving. It also
   reused an already consumed claim instance. The correction uses a fresh caller
   with controlled Git/ADB and verifies rejection, retained identical link target,
   and no process/transport calls.
2. The total-limit fixture repeated one prerequisite nine times, violating its
   three-phase bound before reaching eleven. The correction performs the exact
   permitted eleven-call sequence, then rejects a twelfth call. Existing command,
   timeout and label negatives remain before the total bound is exhausted.

Only these two new-oracle hunks changed; caller source and established assertions
were unchanged. Original freeze/failure receipts and Git history remain retained.

## Evidence and limitations

Coordinator receipt `caller_corrected.json`: 44/44 methods PASS, no skips,
8.606 seconds, all 24 pins unchanged, native calls 0, no remaining owned RAM
fixtures. The oracle covers scope/commit/pin drift, actual payload composition,
fresh identity and bounded replies, ownership/intent, exact sequence, failures at
both actions and closure, causal errors, partial outputs and CLI/check-only.
Git/ADB and the native transport primitive are controlled substitutes.

`caller_windows.json` records Windows Python 3.13.11 composition of the actual
pinned sources: upload 28990 and capture 25232 UTF16 units including trailing NUL,
within 30000. Historical binding identity was used only for size arithmetic.
Missing real scope returns 1 before any process or owner creation. The reviewer
also verified the real scope and owner paths remain absent.

This does not verify current board identity, bz2 capability, transport behavior,
active firmware/artifact state, runtime success, atomic capture, physical safety,
WCET or a human phase gate. Storage failures can prevent durable output saving;
path checks do not defeat hostile concurrent replacement, and host timeout is
not proof of remote reap. Next eligible native work still requires fresh board
admission, exact active-artifact verification and an explicit committed fresh
scope with its source review. No native operation is authorized by this report.
