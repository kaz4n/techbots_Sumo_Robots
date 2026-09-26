# D201 offline interpreter fresh-context review

Final status: PASS for corrected source and host interpretation preparation;
all three implementation findings and the one fixture portability finding are
resolved by the bounded changes and receipts recorded below. No open material
finding. Original findings, source/oracle identities and first failures remain
preserved. This PASS does not establish a native capture or decoded board result.

2026-09-26. Reviewer owns this review only. Initial status: BLOCKED on two
implementation findings. No subject, test, transport or device execution was
performed by the reviewer. Initial source is 31143 bytes, SHA256
eb23a62a43379bc69d5cf894a8be4a606da4ea5c417d2d21aaa486dcaf892724.
The authoritative contract is 32296 bytes, SHA256
6007ec4e2e22cdf0e8f751790c49924b26b4adb8f9dfde5d5f6db2ed9bd7dff8.
Independent oracle freeze is 9361 bytes, SHA256
1722bb497d1cfd67e855050acf13d84998aacec75b734d58d16b82c6f93fec0e.

## Initial findings, retained before any repair

1. BLOCKER: `_flash` pairs `FLASH_KEYS` in the order before_loader,
   before_sketch, after_loader, after_sketch with boundaries 4, 6, 20, 25.
   The fixed plan requires after_sketch at 20 and after_loader at 25. This
   rejects valid failed prefixes after the sketch bracket and can accept an
   early after_loader assertion. Bind the last two flag names to their actual
   boundaries while preserving the two predicates and deterministic order.
   The independently frozen all-prefix and explicit flash-boundary cases cover
   the discrepancy. This finding was identified by source inspection.
2. BLOCKER: `_receipt_types` classifies malformed count member types as TYPE
   before `_counts` can inspect them. The deterministic-order paragraph
   explicitly assigns malformed counts to COUNTS; bool commands/reads in the
   frozen independent oracle expect that classification. Move exact-int member
   checks into the late COUNTS phase before arithmetic/comparison. Keep the
   named counts container TYPE and fixed key-set KEYS checks unchanged.
   This finding was identified by source/contract inspection.

Preserve the initial source, oracle and first host results. Neither finding
authorizes changing assertions, accepted inputs, receipt ownership, native
status or firmware. Final review awaits the coordinator's first serial host
receipts and a bounded implementation correction against the same contract.

## Evidence boundary

The interpreter reports saved-format DECODED, PARTIAL or REJECTED and source
predicate annotations only. It cannot upgrade a failed native capture, infer
publication atomicity or associate the lifetime first failure with a trace
stage/epoch. Coherence remains UNPROVEN. Physical cause, timing repair,
production WCET, motor-capable authorization and human gates remain outside
this review.

## Source and independent-oracle inspection

The reviewed implementation is a standalone local parser with three pure work
seams and a fixed main. Import constructs constants/functions and the fixed
read plan only. It does not import the historical decoder, native caller or
transport. The pure seams read no files and return newly parsed/decoded/copied
containers. Exact argument types exclude bool-as-int and mutable byte buffers.
Map length/hash admission precedes parsing. Struct selection is restricted to
the sixteen full observed type names; private aliases remain fixed. Explicit
little-endian widths,64 Call slots, two numeric reserved bytes, strict bool0/1,
finite float32 and ascending field traversal preserve selected-field meaning.

The reviewer compared all fourteen prior map entries and104 fields against
the accepted D195 map: unchanged. The two new structs add eleven fields with
the D199 observed offsets and widths; report28, sample12, reason u8 and the
nine numeric labels agree with the current observed summary. The new global
window is537121768. Report.before_abort.previous stays at overall offset1120.
Validity bits1/2/4/7 are explicitly source semantics, separate from observed
GDB layout/enum metadata. The independent oracle transcribes all115 field
declarations and constructs inverse fixtures; it does not derive expectations
from implementation dictionaries.

Packet parsing rejects duplicate JSON keys, malformed UTF8, nonfinite constants
and numeric overflow. Full paths are allowlisted without normalization or
basename collapsing; duplicates are rejected before map insertion. Canonical
base64, exact sizes and hashes precede decode. Both original parsed receipts
are retained before shape/status checks. Complete and failed-prefix admission
preserves requested-versus-successful command accounting, exact read order,
declared snapshot copies, saved file set and first/postcheck errors. Verified
references and prior decoded windows survive a later rejection. The two initial
findings above concern flash-boundary linkage and count error classification,
not permission to change this admission model.

SETTLE annotations preserve every numeric field. Absent and unknown-presence
payloads never acquire measured availability or completed-branch predicates.
Present branches distinguish early literal zeros from validity-marked samples,
150us deadline comparisons,4095 last poll and freshness conditions. Reserved,
unknown mask/reason, first-failure and publication-relationship issues retain
their specified order. Later SUCCESS cannot erase the lifetime first failure.
Semantic inconsistency stays INCONCLUSIVE without changing saved-format status
or inventing a stage/epoch/physical cause.

The fixed main rejects malformed CLI or missing bytecode inhibition before
I/O, accepts only an explicit lowercase packet SHA and module-relative fixed
paths, reads each input once with limit+1, checks packet hash before interpret,
and exclusively creates decoded.json with allow_nan=False. It never overwrites,
cleans up, contacts a device or changes the original packet. Its exit codes
describe DECODED/PARTIAL/REJECTED only.

Independent oracle66495 bytes / b286bee8028bb52848efd07bdc8f2ca7eaa7a85da3eeccf7112ce8f2e63358a4
has66 methods:13 layout/decode,16 annotation,30 packet/linkage and7 main.
Coverage includes every selected field, every bool leaf, threshold and unsigned
boundaries, all53 permitted count-prefix pairs, full-path collisions, strict
JSON/base64, failure/partial preservation, waits/flash boundaries, deterministic
first-error order, immutable results, bounded reads and exclusive output. Main
fixtures use a temporary canonical repo tree via synthetic __file__, without
requiring an undocumented mutable ROOT seam. The missing-B fixture sets both
sys.flags and sys.dont_write_bytecode consistently. No material fixture defect
was identified during this static inspection.

The reviewer independently verified all ten oracle input pins and all thirteen
coordinator input pins against current files. Original source and oracle bytes
were preserved before any correction. Serial first execution/results and
subsequent bounded fixes are coordinator-owned and remain to be reviewed.

## First host results and adjudication

Original source, oracle and all first receipts were preserved in Git before
repair (source1df96c20, oracleacba66de, resultsb69cc011). First Linux and Windows
each ran66 methods, no skips, with17 failure records across seven methods.
Ten records are failed prefix subtests plus their outer coverage-count failure;
the remaining six are separate failed methods. Result hashes are
a3c677c6db95452f2f74be5ba2b81595fe3ab5bba026601055b26045a8700ea5
(Linux671 bytes) and
19c06d895f610075840675eb00bc854e886d57ff0f3ced00890e100c2f27fed1
(Windows594 bytes). Both report unchanged input closures. Reviewer checked
saved stdout/stderr hashes and inspected first failure text; no tests were
executed by this reviewer.

The failures confirm the two initial findings. The reversed after-flash
boundaries explain all ten prefix subtests and their outer count, complete
status, explicit flash-boundary and failed-hash-retention failures. Count
member bool classification confirms the second finding. Two additional
adjudications follow:

3. BLOCKER, implementation: read-row field type violations currently produce
   READ_PLAN. The adopted receipt type phase requires TYPE for wrong exact
   Python types, including bool address/bytes and nonstring name/hash. Reserve
   READ_PLAN for correctly typed fixed-plan/key/linkage disagreement. Repair
   the type classification/order without admitting malformed data or changing
   the frozen assertions.
4. Fixture portability defect: the oracle assumed a2000-level array always
   raises the standard JSON parser's RecursionError. The coordinator's isolated
   Python3.13.11 standard-library probe confirms that valid JSON parses as a
   list despite sys.getrecursionlimit()==1000. The contract declares no numeric
   depth cutoff; JSON means a parser failure. The source correctly rejects
   that parsed list as packet/KEYS. Do not add an arbitrary depth limit or
   change the contract to fit the fixture. Keep rejection of the same deep
   input, selecting KEYS if an independent standard-library parse succeeds
   and JSON if it raises RecursionError. Add controlled RecursionError
   injection at the packet parse, preserving the normal map parse, to prove
   the required stable packet/JSON classification independently of platform
   parser depth. This is a bounded fixture repair, not weakened acceptance.

The earlier static statement that no fixture defect was identified is retained
as the result of that initial inspection; this first-run evidence exposes the
specific portability assumption. These four causes account for all17 first
failure records. Final PASS requires separately frozen bounded corrections and
new serial receipts; all original failures remain evidence.

## Corrected-source closure

Correction commit82a24b14 preserves contract6007ec4e, field map0faba243 and all
firmware/native source bytes. Corrected interpreter31266 bytes has SHA256
ea43a42f582f6e8bf2dfa4e2090efb03313f3333036cc1a3159d72295f680c88.
The reviewer inspected the exact Git diff from original1df96c20 and the repair
receipt7384 bytes / baa0aacba7a4d8d12878db6ee9eebf532820b88ba81960e404f0ef7f2e56eb71:

- Finding1 resolved: the existing ordered flag keys now bind boundaries
  (4,6,25,20), matching before_loader, before_sketch, after_loader,
  after_sketch. Both original boundary predicates remain unchanged.
- Finding2 resolved: exact-int count member checks execute at the start of
  the late COUNTS phase, before comparisons/arithmetic. Named counts-object
  TYPE/KEYS checks remain. No malformed count is admitted.
- Finding3 resolved: a small read-row type helper preserves the existing
  exact key check and applies capture/TYPE at the receipt type phase. Later
  fixed-plan checks retain READ_PLAN for correctly typed name/address/extent,
  hash and basename disagreement. No read, file or partial-prefix rule changes.

The source diff contains only these three bounded repairs. No accepted schema,
native status, caller guard, timing limit, output ownership or firmware branch
was changed. No parser depth cutoff was added to production.

Corrected independent oracle67442 bytes has SHA256
1800b0cd3772e06020bff45d0637ea8a9c8f70ab7a6624a81f6a05af30fdde66.
Portability receipt5794 bytes /
883bdf33acb61412a0963417b98786374fb4010cdb65c9e6a086559322ba0006
records the isolated fixture repair. The reviewer compared its exact diff
against oracleacba66de: one existing method keeps the same2000-array input and
all its other strict-JSON assertions, but derives the expected parser-failure
versus parsed-list category from standalone json.loads. One new method injects
RecursionError only for a dedicated packet value, delegates the map parse to
the captured original parser, asserts packet/JSON and exactly one injection.
All other original test methods and assertions remain unchanged. The corrected
suite has67 methods, with no subject-derived expected values or relaxed packet
acceptance. Finding4 is resolved as fixture portability, not a firmware fix.

Coordinator freeze02 is3375 bytes /
817ab4abe570f1fe97970917330022ca0b2491756a021b0c93ccbecfb8bce6a3.
It retains the original closure with only the authorized source/oracle updates
and adds the original freeze and two correction receipts, for sixteen pins.
The reviewer independently hashed all sixteen current inputs; all match.

| Corrected first receipt under P7_motor_settle_run_raw | Actual result | Result SHA256 |
|---|---|---|
| second_interpreter_linux01/result.json | 67 PASS, no skips, exit0 | 5e583f780aeaec50fc11104b0e55c253b9842699762d107fb8940a081805d535 |
| second_interpreter_windows01/result.json | 67 PASS, no skips, exit0 | c63f7854dcba425110f8ce9916cf515fa4d7f945543afbf814883284a8ad248a |

Both commands use Python-I-B and360-second host bounds; Linux uses
TMPDIR=/dev/shm. Linux started07:31:58.689682UTC and Windows started
07:32:09.647305UTC after Linux completion. Unittest times are2.033 and2.165
seconds. Neither invocation timed out or changed a frozen input. Exact stderr
hashes areca81fbea096e6febaa7e88df316ce8e0505290af8d42b2ebd892c07165669ea5
and771100c575e9569e2f7e08dcf44bdeab5994f71b292731e7c44be70bfebe7943.
The reviewer verified saved stdout/stderr bytes against the receipts. All
fifty-three partial-prefix cases, branch/field checks, original failure cases
and the new parser-error injection now pass on both platforms.

This final PASS closes offline source/host preparation only. A future saved
packet still requires its independently observed explicit hash, original raw
receipt preservation and separate actual-byte review. DECODED is format status,
PARTIAL preserves a failed capture, and semantic CONSISTENT does not establish
atomicity or measured success. No native failure can be upgraded by this parser.
