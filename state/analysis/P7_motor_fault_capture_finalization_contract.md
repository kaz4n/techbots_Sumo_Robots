# D176 finalization regression addendum

Clarifies original D176600s total and first-failure/evidence requirements after
separate source review4eddcdb5. Original contract/tests/freeze remain retained.
No native scope, new timeout value, legacy manifest repin or locked-test change.

After all independent final file/identity/directory checks, at elapsed599.999s a
complete valid capture may be COLLECTED; at600s or later it must be FAILED.
Preserve an earlier primary failure; add deadline evidence separately when it is
secondary. Continue every independent final check even when a prior check fails.
The existing default child result is stored at NN.result.json['subprocess'] with
returncode,timed_out,reaped fields. Record the actual outcome before later stream
flush/fsync/close failures can replace it. A nonzero/timeout/unreaped child is the
primary failure even if cleanup subsequently fails. A successful child followed
by cleanup failure remains FAILED, with its successful child result preserved.
Attempt stream cleanup independently and retain its errors separately in existing
receipt.output_errors(file,type,message) or report.postcheck_errors(check,type,message)
when a primary error already exists. Raw files and independently readable streams
remain evidence. No retry, extra MCU command or relaxed bound follows a failure.

These repairs apply to the shared collector's intended lifecycle contract, so
run the unchanged legacy collector suite as well as the new independent cases.
The initial38D176 tests already passed against96fb8935; retain that result and the
source-review FAIL. New separate regression file must be frozen and executed on
that original source before repair. Do not alter established expectations.
