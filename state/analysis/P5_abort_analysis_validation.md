# D136 offline opener-abort analysis validation

Status: IMPLEMENTED and HOST-TESTED on final source5277dec0, SHA256
8e002c6f627e1cb39af94d244a3ba62b817967e9d0e8ceac7497f9f6eb52c4d2.
Separate scoped source/receipt review PASS, all reported findings closed; no
physical acceptance, producer execution proof or human phase gate is claimed.

The tool implements the adopted [D136 contract](P5_abort_analysis_contract.md)
and reuses the unchanged CSV validator. It checks declared historical source
binding, exact D135 cue/trace grammar, handover metadata, unsigned qualified
observation-to-application timing and all ten retained attempts. It never
connects to hardware or approves motion. The four acceptance/verification fields
remain false, even for a logical PASS.

## Independent preparation and retained first results

The separate public author froze 74 methods and a full 65536-value cue oracle
before implementation; another context froze 19 private methods. The implementer
did not read those new tests. First source c0afe321/9891c3ea passed all74 public
methods; private first18/19 exposed a test-interception mismatch. The test patched
a different instance of the same CSV module, so its callback never executed.
Separate review preserved original probes/freeze/failure and corrected only
new private test16's dependency selection; every old assertion remains and a
file-identity assertion was added. All19 then passed unchanged original source.
See b3b44e59 and reviews/P5_abort_analysis_review_raw/private_harness_adjudication.json.

Source review then found extra direct/list declarations bypassed canonical
configuration uniqueness. A spec-only author froze eight additional methods;
the first run retained141 failing subcases in d0169983. Fix f717103a passed those
8 plus74 public and19 private cases. Further independent seven-method coverage
exposed252 failing subcases for parenthesized/decorated declarations, preserved
in a2f59819. Fix ea63f527 passes all15 declaration methods,74 public and19 private
cases. Both additional test files were transferred to tests/tooling byte-for-byte
and their discovery checks passed. Original expectations and failures remain.

Subsequent review found an ordinary-read regression inside alignas plus missing
finite builtin/qualified-type spellings. Two independent two-method additions
retained32 and42 failing subcases before each first correction. A different
implementer repaired only the declaration classifiers without reading the new
test bodies. CV/global/pointer/reference forms are checked against ordinary
read controls; canonical literal extraction and all other report logic stay fixed.
The final maintained suite passes **93 public methods in3.721s** (including the
65536 cue oracle) and **19 private methods in1.841s**, both exit0/no skips/errors.

One supplemental discovery command failed before execution because it attempted
to load both archived and maintained copies of a helper with the same module
name. Its original read_fix receipt remains; discovery from the single maintained
tests/tooling directory resolves the harness collision without editing any test.
All four added public files are byte-exact transfers of the independent freezes.

The reader is deliberately a bounded source-admission utility, not a C++ compiler
or a general preprocessor/parser. It supplies no deployed-image verification.
See [the separate review](../reviews/P5_abort_analysis_review.md) for its exact
finite scope, source/receipt identities and preserved original findings.

## Existing evidence preserved

The unchanged legacy analyzer/CSV regression passed112 methods in5.936s,
exit0; its dependencies remain unchanged. Public runners verify694 prior inputs
before and after every run. Firmware, configuration and the43 established locked
files are unchanged by this offline task. No new C++ build was necessary.

Exact command vectors, source/test hashes, results, actual exits and log hashes:
- analysis/P5_abort_analysis_raw/public_first.json, public_fix1.json,
  public_fix2.json, public_read_fix.json and regression_first.json.
- analysis/P5_abort_analysis_declarations/ first.json, fix1.json,
  prefixes_first.json, second_repair.json, alignment_first.json, qualified_first.json,
  qualified_final.json and the transfer receipts.
- reviews/P5_abort_analysis_review_raw/ private_first.json,
  private_harness_retry1.json, private_fix1.json, private_fix2.json, private_read_fix.json
  and private_qualified_final.json. Final694/43/prefix bindings are in
  analysis/P5_abort_analysis_raw/final_binding.json.
- reviews/P5_abort_analysis_review.md and its source-review receipts.

All inputs are synthetic local fixtures. M0 never qualifies a cohort; declared
hardware origin is only eligibility for external review. Neither file hashes nor
a passing report proves deployment, native log delivery, full-token producer
semantics, physical cue onset, full tick WCET or the required physical10/10.
The actual P5 criteria remain in P5_software_acceptance_packet.md.

Final review independently rehashed all694 prior inputs and43 protected files,
all93 maintained public test bindings and19private bindings. Exact report and
receipt: reviews/P5_abort_analysis_review.md (0965edc7) and its
final_receipt_review.json (fcbb4dbc). Review reused a separate same-model context;
it is neither cross-model nor a fresh phase-gate review. No full phase pass follows.
