# D155 startup launcher design review

25 September 2026, Asia/Dubai. Bounded same-model design review reusing D154
design/code-review context; not an independent implementation review, native
grant, cross-model review or phase gate. Reviewer edits only this note.

Initial contract SHA256:
`94c74a902be0d495accc6ba100be18a1f9ab48276ad615939d8381aa8cee994b`.
Reviewed against frozen D153/D154 interfaces, existing read_native_init runner
initialization, D144 identity reuse and the advisory startup guard boundaries.

**Initial disposition: one material acceptance gap; clarify before spec freeze.**

R1 **MAJOR** - Define successful capture acceptance fully (initial contract
`:60-61`). The capture paragraph
requires fixed identity and 18/18/713656 counts but does not explicitly require
the exact D153 report schema, actual-int counts, first_error=None, empty
postcheck_errors or valid non-None analysis. Under a literal weak validator, a
malformed or contradictory COLLECTED-shaped report could produce COMPLETED.
Require exact D153 top-level/count keys and scalar types, fixed run/source,
COLLECTED, exact integer counts, no reported errors and valid D152 analysis.
Reuse frozen support.check_analysis for its shallow contract; do not implement
another decoder. Valid fault/no-progress observations remain collected evidence.

Clarify that uncertainty forbids later upload/capture dispatch, while the four
independent final checks may still perform their fixed Linux-file observations.
The current `:67` phrase "No later native dispatch on uncertainty" otherwise
conflicts with mandatory independent remote final checks.

The remaining composition is appropriately small: one fixed launcher, a pure
command constructor, two hash-checked in-memory payloads and an exact callback
sequence. Exclusive local claims precede dispatch; capture intent links the
accepted upload report hash. Failed transport/report/intermediate checks stop
capture, partial claims remain consumed, and persistence failure raises.

Run/source boundaries are present: original D144 artifact identity remains
distinct from static-fcddbd8e-run01; current source, target, HEAD and scoped
inputs are rechecked. Old compile_only=True and consumed grants are not reused
as authority. The later committed run scope must concretely bind all full
digests and the explicit inert upload/reset/activation plus conditional passive
capture; this host contract provides no grant. No further framework is needed.

No implementation, tests, native execution or runtime qualification was reviewed
in this design task. Source review and frozen controlled test receipts remain
required after the acceptance language is settled.

Amended contract SHA256:
`f91f1210154833199d654ee15ece1428cee8ade01a070700f4051903540e8da8`.
R1 is resolved: exact D153 keys/typed counts, clean report, valid analysis,
ordered fixed read records, hashes, finite timing and wait evidence are explicit.
The uncertainty wording now permits only the fixed Linux-file final checks
after stopping upload/capture. Public callable signatures are unambiguous.
The new fixed committed scope must match its bytes at current HEAD and pins
launcher/tests/contract/reviews; CLI reviewed-head names that containing commit.
This binds the run without a circular HEAD field or reusing an old native grant.

**Final design disposition: PASS for D155 host implementation/testing only;
no open material design finding.** Preserve the initial finding and its amendment.
Actual code/receipt review and the separately recorded inert run scope remain
prerequisites; this review grants no native upload, reset, activation or capture.
