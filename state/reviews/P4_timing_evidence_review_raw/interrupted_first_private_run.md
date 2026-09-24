# D129 private first full-run interruption

The first invocation of `wsl -d Ubuntu -- python3 state/reviews/P4_timing_evidence_review_raw/run_private.py` returned exit 1 in approximately 7 seconds with no stdout/stderr. Inspection immediately afterward found no configure, build, tests, or private_validation output file. No semantic oracle failure is established by this invocation. The previously completed focused repro logs remain unchanged.

The parent concurrently observed WSL stopped, low Windows free space, and other interrupted jobs. This reviewer did not issue WSL shutdown/terminate or any process-kill command. The runner contains no such operation. Further WSL execution was held on the parent's instruction pending environment recovery.

Separately, the Windows-only binding script's first invocation failed before producing final_bindings.json because it treated the parent `prior_locked.json` metadata wrapper as a flat path map, resulting in `git rev-parse 3985da16:head` exiting 128. The reviewer corrected only the reader to select its `sha256` mapping. No tested implementation, fixture, or oracle expectation changed.
