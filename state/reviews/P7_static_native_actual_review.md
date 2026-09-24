# D148 existing-packet read-only composition review

25 September 2026, Asia/Dubai. Separate fresh-context, same-model review,
including a bounded second same-model read-only helper/API inspection. This is
not cross-model review, human approval or native/runtime validation. The reviewer
owns only this file and made no implementation edits, board commands, build,
upload/reset or commits. Six local in-memory `finish()` substitute checks ran
without file writes or transport dispatch.

## Scope and exact identities

Reviewed root AGENTS, current P7 progress, PLAN section3 (25September precedes
the28September scope-cut deadline and1October freeze), D051, D147 and its frozen
interface/review, plus the D148 plan and both new glue files. The review covers
one existing D144 packet and at most five intended read-only commands. It does
not admit static firmware into production or supersede the original rejection.

Rehashed local sources:

| File under state/analysis/ | SHA256 |
|---|---|
| P7_static_native_actual_plan.md | a0169e7405a5550fca8828ba4cd43b7f1387e015b92f980c6d1964707dd828e4 |
| P7_static_link_probe_raw/validate_native_actual.py (reviewed final) | fbde292662d3c183097ac5956a51efc23dedc6067a778e0ada81c9a24dbe7a32 |
| P7_static_link_probe_raw/read_native_actual.py | c6099f6d29ebdc400df5280032a8b5b0d229a003c594033a920f459316e2b8e7 |
| P7_static_link_probe_raw/run_static_probe.py | 983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208 |
| P7_static_link_probe_raw/static_remote.py | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |
| P7_static_link_probe_raw/static_bootstrap.txt | a6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419 |
| P7_static_link_probe_raw/static_native_artifacts.py | cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0 |
| P7_static_link_probe_raw/static_artifacts.py | d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368 |
| P7_static_link_probe_raw/native_actual_preflight.json | 375402c59e5edd918debc131cbfe2ca3766ca0bad67fe2739fd2ed04546e89d2 |

The coordinator's preflight reports28859 UTF16 command units, below30000,
17 local pins,103 source files,102 staged files,26 installed pins, no dispatch and
absent output. That receipt binds the original host1359fcab9494e9a50cb9f8d83a5722164376a54e03f5d131b7c472904906a4e3.
The final host changes only result finalization; command construction is unchanged
and repeats its own length check before any dispatch. This reviewer inspected
the receipt and source; it did not independently run the complete preparation.

## Findings and disposition

**PASS for the exact bounded read-only composition; no open BLOCKER, MAJOR or
MINOR findings.** Coordinator must record the final hashes in D148 before use.

Two initial MINOR receipt findings were repaired in the final host above:

1. Original `validate_native_actual.py:152-154` could replace the first operation
   exception with a result-file write exception. Final `:162-169` preserves the
   original exception when both fail, while propagating a write failure when no
   earlier failure exists. Original command receipts remain available.
2. Original `validate_native_actual.py:155-156` checked command counts after
   saving a success result. Final `:149-163` checks them first and records
   `NATIVE_STRUCTURE_FAILED` with phase `command_counts` on mismatch.

The coordinator reports preservation of original source/preflight in8e3c4348.
Local substitute checks of final `finish()` passed six scenarios: normal success,
bad count, prior failure, write failure alone, write failure with prior failure,
and bad count combined with write failure. The substitute writer only collected
objects in memory; exception identity and saved status/phase were asserted.

## Contract and path checks

- `validate_native_actual.py:30-67` loads hash-checked frozen runner bytes, checks
  the exact repository/-B/ADB identity, pins historical0001/0009/0021 receipts and
  uses their original board boot identity, Claim and eight FileRecords. The
  frozen Probe constructor and `reuse_stage.verifiedStage` inspect local files;
  they do not stage sources or dispatch commands. The new exclusive output
  directory prevents overwriting an earlier attempt.
- `validate_native_actual.py:107-145` reaches only installed `sha256sum`, the
  helper's source observation, the fixed native observation, then independent
  installed/source checks and local pins/stage/scoped-source checks. Calls match
  the actual `Probe.dispatch`, `board_tool.remote`, `verify_hashes`, `source`
  and `postchecks(local_only=True)` signatures. Neither `Probe.execute/prepare`
  nor compiler/property-query, claim-creation or upload APIs are called.
- Bootstrap argument removal agrees with remote `len(sys.argv)==6`. The remote
  helper token is bounded, canonically framed and hashed before execution;
  extension/base tokens use the unchanged `decode_compressed` contract. The
  modules load into fresh private namespaces and do not execute their CLI mains.
- `read_native_actual.py:49-61` matches the actual helper's exact FileRecord
  fields, integer rules and eight-file limits. Claim parsing and `claimed`
  retain run/boot/device/inode checks. `directory` and `read_file` use read-only
  descriptor paths and reject unsafe file types/identity changes. At`:84-94`,
  `build/` extraction yields precisely the seven validator keys; helper scanning
  also checks exported flat-package equality. No binary download is requested.
- Remote`:100-122` checks installed loader/TLS hashes and identities and all
  artifact identities around pure validation. Validator rejection is captured
  without skipping the five available loader/TLS/files/identity/Claim checks;
  each later failure is recorded independently and the first error survives.
  Remote nonzero exits remain in the frozen dispatch receipt even when the host
  does not decode their report into its summary packet.
- `validate_native_actual.py:73-104` requires exact result keys, identity, Claim,
  FileRecords, installed/source hashes, no remote errors, distinct
  `STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS` and all six exact sorted TLS tuples.
  Only an unsaved local dictionary receives the old status for the frozen
  common-schema/bounds checker. The actual report and result retain the new
  status; original production consumers and D144 negative evidence are untouched.

## Evidence limits

An initial remote acquisition failure at `read_native_actual.py:101-106` can
skip the three inner postchecks before baseline loader/TLS records are available;
identity/Claim and the host's independent installed/stage/local checks still run.
This rejects the observation and cannot establish successful validation or full
post-observation artifact coverage. Acquisition failures, timeouts and missing
receipts must be reported as failed/incomplete evidence, never retried by this
composition or treated as a pass.

No actual D148 remote output was inspected because execution follows this review.
A later pass establishes only the fixed packet's structural layout/package
checks and exact inherited aliases. It does not establish entry/constructor or
native binding/ABI correctness, loading, MCU execution, live RAM/stack/WCET,
motor permission, physical acceptance, release readiness or any human gate.
