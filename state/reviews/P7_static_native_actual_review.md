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

## Actual receipt review after D148 execution

25 September2026, after coordinator GO commit `dbb5f1a4`. This follow-up reuses
the source-review context above; it is not another fresh-context or cross-model
review. The initial review bytes had SHA256
`960a693ffce8741b8b43637be60bfc58e7229e205dfc286e209b87033b027993` before this
append. Reviewer and bounded helper reviewer performed only local receipt,
hash, JSON and command-token comparisons; neither dispatched board commands or
reran the native validator. No implementation or existing test was changed.

**PASS for the actual D148 read-only receipt set; no open findings.**

The launcher spans2026-09-24T22:16:51.209681Z to22:16:53.187354Z
(25September02:16:51..53 Dubai), returns0, has empty stderr, and records PASS
source postchecks. Its captured host digest matches final `fbde2926` above.
All five numbered receipts have matching sequence, board2629958581, exit0,
empty stderr and no command error. Their phases are installed_pins, source,
native_validation, installed_pins, source. Result records five reads,
query_attempts0, compile_attempts0, no outer or remote postcheck errors and
`NATIVE_STRUCTURE_VALIDATED`; native report status remains exactly
`STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS`.

Independent local comparisons verified:

- All17 current local pins, four scoped sources and both launcher sources match
  their full recorded hashes. Exactly103 current source files and102 existing
  stage files match the fixed manifests and independently reproduce aggregate
  `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
- Both installed observations are identical and each of26 paths/hashes equals
  the literal installed pin sets. Both source observations are identical and
  exactly match102 local stage byte counts/hashes and the aggregate above.
- Decoding actual command0003 without executing its sources gives remote7290B,
  helper33321B, native3718B and base18322B, each matching the full reviewed hash
  and current file. The bootstrap equals its pinned template with the remote
  digest substituted. The decoded Claim and all eight FileRecords match D144
  receipt0021 and the final packet. Packet identity matches original0001,
  including boot `6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6`.
- The0003 stdout packet equals the final result packet. Its seven artifact
  bytes/hashes equal the seven build FileRecords; the exported package equals
  the build flat package. All six TLS tuples, their cardinality and source/
  loader digests match the exact D147 interface.
- All27 JSONs in the original D144 run directory (25 command receipts plus
  inputs/result) are byte-identical to GO commit `dbb5f1a4`. Original status
  FAILED at layout remains preserved. Nothing converts that historical result
  or a production consumer into a successful admission.

Independently checked structural arithmetic: entry0x08100011; flash payload
93080B; reserved application RAM span167792B; remaining reserved-region
tail94352B. The tail is a static address-range remainder, not observed free RAM
or stack headroom. All entry/constructor/native-binding/ABI, runtime, physical
and human-gate limitations above remain applicable.

Exact inspected evidence hashes under `P7_static_link_probe_raw/native_actual/`:

| File | SHA256 |
|---|---|
| inputs.json | 27ad7e22e55faf7826b8c017361046e9767e04f5ce2d8118537d19b9d633b8c4 |
| 0001.json | e269d356b95b8fa9d84d961349c7646e948efeab1dfdc4ab6aea3d86d5632449 |
| 0002.json | de286c503b3ce7cf61e74eb84d83173b9f6761e2e2c639072237ee056cd57e0c |
| 0003.json | d7d21247cce0424d9541f185f75e455e0a322769e565bb21579bbb1ded1fe6e4 |
| 0004.json | 37648322e6f60dfd0ddc0de1f79a70044be77ab355e3031692aa428c90293ef3 |
| 0005.json | 43915c1902c1e1419ba0f531657f69b6e821b8f0452420bc938c228967367ef4 |
| result.json | 806a040d57a791e350b3d10a6bc59967cda67b031169caa3a53ef46aaf0d824d |

Adjacent `native_actual_launcher.json` SHA256:
`0e0f8113531b28413783270c7a30e84a1fe1ea8e1f89937c5367733756a01e59`.
