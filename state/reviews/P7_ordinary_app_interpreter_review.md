# D212 ordinary application interpreter cross-review

Status: FINAL PASS for the corrected decoder source/oracle and host scope only.
The original readiness analysis below is retained; final host adjudication follows.
Reviewed 2026-09-26, before first decoder host execution.
Reviewer: reused `/root/ordinary_abi_scope`, separate from the decoder implementation
and decoder oracle authors. This is a same-model cross-review with prior ordinary
ABI/source context, not a fresh-context or different-model review.

## Boundary and identities

The reviewer read the normative contract, map and historical parser before the
inspection barrier opened. The decoder oracle author reported FINAL and stopped
writes; root explicitly released the barrier before the reviewer read or hashed
the new decoder, its receipt, or the new decoder oracle. Review used source, AST,
JSON, literal projections and hashes as data only. No subject or test was imported
or executed, no device action occurred, and no implementation/oracle file was
changed. This review file is the reviewer's only owned output.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `state/analysis/P7_ordinary_app_run_contract.md` | 25120 | `828b334235877131580618908cc164381a988f297c4e22235eb72e34fe200e75` |
| `state/analysis/P7_ordinary_app_run_raw/run_derivation01.json` | 119497 | `9a8ef9caa96f0e30a8ad741319d5ea59668b8e6066d0c96fb59defd35f896d66` |
| `state/analysis/P7_ordinary_app_run_raw/ordinary_scalar_map01.json` | 42416 | `d8f4eb7eb36430cff975e3032168fa61f2c249e55596401a67862b272bb08fb7` |
| `state/analysis/P7_motor_const_run_raw/interpret_run01.py` | 31259 | `d96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab` |
| `state/analysis/P7_ordinary_app_run_raw/interpret_run01.py` | 29009 | `7091979ca474d85210a2225310b4d356d92c75bd468e562ef80ffbf9d3c2bec4` |
| `state/analysis/P7_ordinary_app_run_raw/decoder_implementation01.json` | 14886 | `6b0a37c458c348d31cc1e8a99d6ec6194625c2a7e99c4ffc2c9f286c32a953e0` |
| `tests/tooling/test_ordinary_app_interpret.py` | 35945 | `69a772a82e67f43996c025924267564ab8431631f87c7fd4714265ddd5659bc7` |
| `state/analysis/P7_ordinary_app_run_raw/decoder_fixture_derivation01.json` | 20031 | `45bf10d2d98bfad857aefe918038de630c7d1c9e851e586fb01e5513183bcbfb` |
| `state/analysis/P7_ordinary_app_run_raw/decoder_independent_freeze01.json` | 55442 | `4c78e9b776c83b5c49fef54a91347c5a64574a953db77f37d36911e4042191ab` |

All 175 frozen input size/hash pairs match the files read during review. The new
subject's identity is separately declared by root and verified by this reviewer;
it was not promoted into the oracle author's pre-inspection input set.

## Implementation accounting

All 55 historical function spans reconcile: 31 exact bodies, nine metadata
spans, nine permitted semantic replacement slots, and six removed diagnostic
helpers. The actual new inventory is 50 spans because one new
`_ordinary_findings` helper is added. Every old and new function-body identity
matches the implementation receipt, and each of the 31 exact bodies matches both
the historical body and normative derivation pin.

The metadata differences are limited to the authorized changes: sketch package
95368 to 92944; ordinary receipt prefixes; maximum retrieval files 14 to 16;
commands 26 to 28; snapshot slice end 19 to 21; gap boundary 13 to 14; flash
boundaries `(4,6,25,20)` to `(4,6,27,22)`; and complete count 28. The nested
`_plan.flash` 311-byte span changes through the same parent `_plan` extent
replacement, with no second application. Its before/after hashes match the
corrected normative classification and receipt.

Top-level AST comparison finds only the eight permitted assignment replacements,
the snapshot-file range change, and removal of `ALIASES`, `REASONS`, and
`SAMPLE_KEYS`. No additional top-level behavior or helper was introduced. The
six removed functions are exactly the diagnostic annotation helpers. The
preserved bounded CLI remains file-only and creates its result exclusively.

## Ordinary decoding and error boundaries

The exact map size/hash precedes map parsing, selected kind and body-size checks.
The admitted map checks ordinary source/schema, seven windows, 107 fields,
scalar widths, unique field names within their window, nonoverlapping bounded
field extents, enum tables and containing-object bounds. It admits only the
pinned map, not an alternate dynamic address map. Exact Python argument types
retain the declared check order; old diagnostic/type aliases are refused.

All seven selected windows and all 107 scalar declarations match the normative
map. Window decoding uses increasing `(offset,name)` order and preserves the
entire raw window, including unselected nested-report bytes and padding. Each
scalar preserves lowercase raw hex and unsigned little-endian bits independently
of its interpreted value. Signed i8, u64 precision and finite f32 values remain
intact; negative zero remains a finite float with its raw sign bit. Noncanonical
bool and nonfinite f32 values become null with their declared issue, without
discarding later fields. Unknown typed enum values remain numeric with
`UNKNOWN_ENUM`; RobotFault remains a source-bound raw bitmask.

`_ordinary_findings` uses read-plan order, then field offset/name order. Scalar
issues precede and suppress guessed semantic classification. The fixed semantic
order covers sampled fault phase/code, contract bits and unknown bits, nonzero
grant bytes, nonzero selected motor commands/pulses, and canonical unattempted
state. It makes no physical inference from PWM indices or transient port masks.
The 1023 RobotFault mask and zero grant expectation remain source semantics,
not newly observed enum or hardware facts.

The result preserves native upload/capture receipts and their original
`first_error`/`postcheck_errors`. Strict JSON, exact receipt types, canonical
base64, size/hash linkage, file-set admission, waits, flash boundaries and the
first structural failure order remain inherited. Verified prior references,
decoded prior windows and their application findings survive a later structural
failure. The decoder does not synthesize missing fields or repair malformed
receipts. An admissible failed capture stays PARTIAL, even if all reads completed
and closure failed; a complete structural result stays DECODED even with sampled
application findings. These are collection/format statuses, not application
PASS/FAIL or chronology reconstruction.

`repeated_fields_equal` compares only selected scalar raw bytes after both
copies exist. Opaque/padding changes cannot affect it. Every result remains
`coherence=UNPROVEN`, including equal windows, counter progression/regression,
wrap or reset ambiguity. No MCU halt, abort, terminal freeze, reset-continuity,
atomicity, physical motor inhibition or WCET conclusion is introduced.

## Oracle source and negative relevance

Read all 27 retained PacketOracle methods, seven retained MainOracle methods and
12 added ordinary methods, plus their shared fixture/loader helpers. Independently
reconstructed the ten selected historical sections as text only: all counted
replacements and before/after hashes match. The complete projected fixture is
35695 bytes, SHA-256
`99f91b12d22e3ee2bedfd305c57d5647cd2d4e2566d550a57c5d307eed79f39f`.
All 120 inherited assertion/verdict sites remain: OracleBase 21, PacketOracle 71,
MainOracle 28. The ordinary class adds 95 assertions and 11 verdict-helper calls.
The declared selected/excluded historical methods account for all 70 ancestral
methods; excluded diagnostic tests remain in the unchanged historical file.

The 46-method inventory covers all 57 allowed prefix pairs, all 107 scalar
fields, 50 bool fields, six float fields, seven enums/47 names, integer endpoints,
exact public types and order, all window lengths, map identity, opaque attempted
neighbors, nonaliasing outputs, complete/partial findings, stale identities,
structural first-error preservation and exclusive bounded CLI output. The
independent specimen starts with explicitly selected values and derives bytes
and expected scalar records; it does not obtain expectations from the decoder.
The inherited pure-seam guard prohibits file, process and sleep calls while
loading/checking the pure API. CLI filesystem fixtures stay under their temporary
test owner. Both declared platforms expect 46 tests and no skips.

Changed negative values remain genuinely invalid: command/read 29 exceeds 28;
requested bytes 727431 differs from 715858; closure count 13 differs from 16;
the stale previous tuple at index 11 differs from current grants; grants bodies
20/22 bytes violate width and the 21-byte zero body differs from its independent
nonzero specimen; sketch tail 29832 differs from 27408; diagnostic owners,
sources and maps differ from ordinary positives. The 17-file negative reaches
the file-count guard before duplicate-path processing. The new snapshot and
after-sketch indices are correctly separated in the inherited decoder tests.
No assertion weakening or negative-to-positive substitution was found.

## Readiness and remaining work

No material source/oracle finding is open. READY for the root's separately
bounded first decoder host executions. This verdict does not report a passing
test: the reviewer ran no suite or subject. FINAL requires review of the saved
Linux and Windows receipts, exact selected method results, closure/pin checks,
timeouts/owners and any first-failure evidence. Native admission, upload,
retrieval and interpretation of actual MCU data remain separate decisions and
evidence; this review does not authorize them.

## Final host adjudication and closure

FINAL PASS, 2026-09-26. The original Linux decoder attempt is preserved in commit
`acf8cddf` and `first_interpreter_linux01`: 46 methods ran, 39 passed and seven
MainOracle methods errored. The nine reported error records include three
subtests of the canonical-output method. Windows01 did not execute. Every error
was the same fixture setup `FileExistsError`, before decoder loading/calling:
the new ordinary map lives under RAW, already created by the packet fixture.
This fixture geometry defect was missed in the initial readiness review; no
decoder source defect was established by that run.

After preservation and root adoption, the independent oracle author appended
exactly one count-1 projection changing only
`map_path.parent.mkdir(parents=True)` to
`map_path.parent.mkdir(parents=True, exist_ok=True)`. This reviewer independently
compared the revision with the preserved original: removing that sole keyword
restores the entire projected MainOracle class byte-for-byte. Packet-directory
creation and exclusive decoder output remain unchanged; all 46 methods and all
existing assertion/verdict sites remain. The concrete oracle changes only its
fixture hash. Its five additional frozen inputs preserve original failure
receipts and coordinator01. No product, contract, map or semantic assertion was
changed. Fresh driver02 changes only the coordinator and exclusive owner suffix
from 01 to 02; the 600-second bounds and other guards are unchanged.

| Final evidence | Bytes | SHA-256 |
|---|---:|---|
| `tests/tooling/test_ordinary_app_interpret.py` | 35945 | `c48679f489054004398dae6e191cccb93fe3462e9b80894764fc2f487c9ab4b1` |
| `decoder_fixture_derivation01.json` | 22892 | `97b76a3d364459bf15b58f98ffaa094e00ead8a4273bb034f72b98aca89e66b1` |
| `decoder_independent_freeze01.json` | 59709 | `583c50b81b07810c7c814f806082276c6de8c456bfb395afd7c9860aa434a4c8` |
| `interpreter_host_driver02.py` | 3666 | `319cbdd81ab804d8269d844aee4268f3d706e122848d244c274cf9f60191542b` |
| `interpreter_coordinator_freeze02.json` | 30572 | `22ec14b4a644eddacdc5e31ecebd2825c9560fe6275fc7ef4e85a7607af817d5` |
| `first_interpreter_linux02/result.json` | 881 | `f8630f0fe218a40495004af0b37eccc1766c76243e84dcda3311c9eea751c90e` |
| `first_interpreter_windows02/result.json` | 949 | `12020b2df66c6b45f5a96705c6f669f9e556482f022453209ae8911c773dac0d` |
| `interpreter_host_closing01.json` | 12817 | `71178b0765a3a9b05e77f7c65c73cbe0c7ee99d2325a12dc28af760a84582b5b` |

The final table's short paths are relative to
`state/analysis/P7_ordinary_app_run_raw`. The decoder remains 29009 bytes,
SHA-256 `7091979ca474d85210a2225310b4d356d92c75bd468e562ef80ffbf9d3c2bec4`.

Root executed Linux02 then Windows02 serially. Both returned zero with **46/46
methods passing and no failures, errors or skips**: 92 successful method outcomes.
This reviewer matched every method identifier and its order to the frozen
46-method list, verified original stdout/stderr hashes and intent/result fields,
and reconciled both successful unittest summaries. Linux used `/dev/shm` and
Python `-I -B`; its outer elapsed time was 13.3107014 seconds. Windows used its
dedicated temporary root and `-I -B`; its elapsed time was 2.8764731 seconds.
Neither timed out. Both stdout streams are empty. Both report unchanged inputs
and coordinator bytes; this reviewer independently rehashed all **187** closing
coordinator inputs with zero mismatches. The closing artifact pins the coordinator
instead of duplicating its complete file list and records all 92 ordered outcomes.

The Windows temporary root contains no children. An attempted removal of that
exact verified-empty directory was rejected before execution by automatic tool
policy with reason `blocked by policy`. No retry or alternate deletion occurred;
the empty directory is retained, with no test payload remnants. Linux's
context-managed fixture cleanup and recorded `/dev/shm` root are retained as host
evidence; no independent Linux directory inventory is claimed. One read-only
receipt-comparison attempt encountered CRLF in Windows stderr; comparison was
corrected to line-based text analysis while raw bytes/hashes remained unchanged.
This was review bookkeeping, not a test rerun or altered result.

No material decoder source/oracle/host finding remains open. The reviewer did
not execute any subject or suite. This FINAL verdict retains the same-model,
reused-context limitation and does not establish actual MCU observations,
atomicity, reset continuity, physical inhibition, WCET or a human phase gate.
Native admission and any subsequent execution require their separate recorded
authorization and review. Writes stop after this review is sealed.
