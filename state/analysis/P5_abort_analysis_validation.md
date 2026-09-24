# D136 offline opener-abort analysis validation

Status: IMPLEMENTED and HOST-TESTED within the results below; source review
remains pending for two concrete configuration-reader cases. Not physical
acceptance, a producer execution proof or a human phase gate.

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

The separate reviewer has identified two further unexecuted cases against
ea63f527: an ordinary constant read inside alignas is mistaken for an incomplete
prefix decoration, and the finite builtin type-head list omits unsigned short.
Independent new coverage and a bounded correction by a different implementer are
pending. Passing earlier tests does not close these findings. No test that failed
a correction has been weakened or repeatedly patched to force a pass.

## Existing evidence preserved

The unchanged legacy analyzer/CSV regression passed112 methods in5.936s,
exit0; its dependencies remain unchanged. Public runners verify694 prior inputs
before and after every run. Firmware, configuration and the43 established locked
files are unchanged by this offline task. No new C++ build was necessary.

Exact command vectors, source/test hashes, results, actual exits and log hashes:
- analysis/P5_abort_analysis_raw/public_first.json, public_fix1.json,
  public_fix2.json and regression_first.json.
- analysis/P5_abort_analysis_declarations/ first.json, fix1.json,
  prefixes_first.json, second_repair.json and both transfer receipts.
- reviews/P5_abort_analysis_review_raw/ private_first.json,
  private_harness_retry1.json, private_fix1.json and private_fix2.json.
- reviews/P5_abort_analysis_review.md and its source-review receipts.

All inputs are synthetic local fixtures. M0 never qualifies a cohort; declared
hardware origin is only eligibility for external review. Neither file hashes nor
a passing report proves deployment, native log delivery, full-token producer
semantics, physical cue onset, full tick WCET or the required physical10/10.
The actual P5 criteria remain in P5_software_acceptance_packet.md.
