# D201 offline interpreter fresh-context review

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
