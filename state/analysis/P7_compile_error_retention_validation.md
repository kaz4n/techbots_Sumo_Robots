# D181 compiler failure retention

25September2026 Dubai. IMPLEMENTED / HOST-TESTED / REVIEWED. No hardware used.
Source0d73967b preserves the primary CalledProcessError and its CLI exit code
when stdout/stderr receipt writes fail. Both writes are attempted independently;
partial bytes remain. Console errors are retained without masking the selected
failure. BaseException still propagates. Commands, permissions, signatures and
successful receipt semantics are unchanged.

## Evidence

All raw files below are under P7_compile_error_retention_raw/.

- reproduction.json: memory-only synthetic ENOSPC shows original compiler43
  becoming CLI2, with no stderr-receipt attempt; no process or device invoked.
- original_freeze.json: independent27-method oracle07d6d28a, original source
  and contract identities frozen before execution.
- original_test_output.txt/result.json: original3PASS/2FAIL/22ERROR in0.203s;
  the two direct43-versus2 assertions reproduce the defect. All output retained.
- The fresh reviewer and independent author agreed two new-fixture assumptions
  were wrong: command receipt encoding is omitted, and successful None streams
  must fail rather than become empty text. Only those assumptions and the fake
  write_text non-string behavior were corrected. No existing/locked test changed.
  Original oracle is retained in Git; adjudication35644c7f.
- corrected_freeze.json: first repair0d73967b and corrected oracle d0f259fe,
  SHA72e0068ab6626e67e1cdb379bf6b8a4372dd9d20ff2377eeb5041e0fdcf20ac8.
- repair_test_output.txt/result.json:60PASS, no skips,1.226s unittest/8.649s
  wrapper:27new +15unchanged executor +18unchanged build-parser methods.
- integrity.json:4current/10D180/24D179pins exact, firmware/bench/locked and
  selected legacy tests unchanged, zero owned executor RAM remnants.

Actual repair command:
`wsl -d Ubuntu -- python3 -B -m unittest tests.tooling.test_compile_error_retention tests.tooling.test_compile_executor tests.tooling.test_app_build_policy.AppBuildParserTests -v`.
Original command selected only the new module. Results include exact commands,
exit statuses, HEADs and output hashes. WSL Python3.12.3; no compiler was run.

Separate fresh-context same-model review:
../reviews/P7_compile_error_retention_review.md,
SHAacafc2426b24f96ac6cf69418a2d80c18a2f39438bcac5682036742dc9b8b094.
PASS with no open material finding. Reviewer inspected source/tests/receipts and
hashes, without rerunning tests or using hardware. This is not cross-model review.

Synthetic storage/process responses prove script behavior only. They do not
establish successful target compilation, current board state, actual upload,
native startup, physical acceptance or a human phase gate. Deployment software
preparation remains the next eligible task; its execution needs separate evidence
and specific fresh motor-run authorization. No old native pin/scope was repinned.
