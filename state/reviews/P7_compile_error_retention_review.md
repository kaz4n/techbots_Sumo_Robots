# D181 independent source and evidence review

25 September 2026, Asia/Dubai. **PASS for the narrow host Python repair.**
No open material findings. Separate same-model reviewer context; this is not a
cross-model review, target build, physical acceptance or human phase gate.

Reviewed AGENTS.md, the current P7 resume and D181 decision, PLAN section 3,
the D181 corrective contract, public executor tests, the additive independent
oracle, production diff 35644c7f..0d73967b, and retained original/repaired results.
Reviewer ran no tests, builds, compiler or board actions, network requests or
cleanup, and changed only this report. Read-only shell inspections and hashes
were used.

## Exact reviewed inputs

- Source commit: `0d73967b`; final tested checkpoint:
  `d0f259fe4b33d404398344bae4b8ab7e9d52875f`.
- `tools/board_tool.py` SHA256:
  `9e87d893edfc1a0e804a4dd94abf84b3b2808b66a57a0fc5c151268485c3a89d`.
- `tests/tooling/test_compile_error_retention.py` SHA256:
  `72e0068ab6626e67e1cdb379bf6b8a4372dd9d20ff2377eeb5041e0fdcf20ac8`.
- `state/analysis/P7_compile_error_retention_contract.md` SHA256:
  `378d4f191470fc905d9f0b1965986927951bbba7a7f379c2cf0fcbe4041a8dc7`.
- Unchanged `tests/tooling/test_compile_executor.py` SHA256:
  `e7fd034ffa49d1b8070319d4efa16073f5727bcdab9389901889744a95c44734`.
- Original run output SHA256:
  `840ac831a5ff372c4571ba468088bb6a4940556f33e9066a451de85c63a57bfd`.
- Repaired run output SHA256:
  `1d891d6753bc1a807b54b8499eb9942adb08a2b69b1c059dae7fb6406e6037a7`.

The current source/oracle/contract hashes match corrected_freeze.json. Both
output hashes match their corresponding run receipts under
`state/analysis/P7_compile_error_retention_raw/`. Source repair and corrected
oracle were frozen before the repaired execution. Existing executor/parser and
locked tests are absent from the change list.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed scope.

`tools/board_tool.py:423` attempts the existing stdout and stderr receipts once
each in order, catches Exception only, preserves the original UTF-8 and failed
None-to-empty treatment, and attaches ordered path/type/message dictionaries.
It neither retries nor reopens or deletes partial output. Its diagnostic states
the receipt directory and explicitly identifies output that could not be saved.

`tools/board_tool.py:440` retains runner selection, command receipt before
dispatch, successful result identity and successful receipt behavior. The
failure handler re-raises the same CalledProcessError with a bare raise;
returncode, command, streams, cause and context are preserved. A returned
nonzero result still becomes the primary CalledProcessError. A successful
command whose receipt write fails still fails and cannot reach verified.json.

`tools/board_tool.py:412` records diagnostic-write Exception details without
replacing the selected error. The same helper at line 721 preserves main's
compiler exit code or its existing exit 2 for other caught errors. BaseException
remains uncaught, including interruption of a receipt or diagnostic write.
The helpers remain bounded and below the repository's function-length limit.
No command, argument, permission, transport, source pin or firmware changes
occur in the production diff.

Two material new-fixture mismatches were found independently before closure:

1. The common assertion required explicit UTF-8 for the command receipt, whose
   established encoding argument is omitted. The correction checks omitted
   encoding for that receipt and UTF-8 for the two output receipts.
2. The new success-None case required normalization to empty output despite the
   contract preserving success-path semantics. Its corrected memory sink models
   Path.write_text rejecting non-text, and the assertion requires refusal before
   the stderr receipt. Failed-command None-to-empty coverage remains unchanged.

The independent author agreed without reading production bodies. The original
oracle at 07d6d28a and its execution failures remain retained; adjudication is
recorded in 35644c7f, and the corrected oracle is frozen in d0f259fe. Production
was not changed to satisfy either unsupported expectation. No established or
locked assertion was weakened.

## Evidence and limits

Coordinator-run receipts were inspected, not rerun by the reviewer:

- Original source: 27 methods, 3 passed, 2 failed and 22 errors. The two CLI
  assertions independently show compiler exit 43 replaced by exit 2; the error
  count also includes the fixture mistakes and is not a defect count.
- First source repair with corrected frozen oracle: all 60 methods passed,
  comprising 27 new retention cases, 15 unchanged executor cases and 18
  unchanged parser cases; no failures/errors/skips. Unittest reports 1.226 s;
  the enclosing WSL invocation receipt reports 8.649 s.
- Coverage includes raised/returned failures, raw/None failed streams, each/both
  receipt errors, retained partial bytes, identity/cause/context, main status,
  unavailable stderr, BaseException propagation, pre-dispatch command-receipt
  refusal, successful captures, successful-command receipt refusal, and no
  retries. Legacy executor checks retain successful checked-build receipts and
  command-routing safeguards.

These are controlled host script results. They do not prove real disk-full
behavior, actual compiler execution, a target artifact, board access, upload,
MCU operation, timing, physical safety or a phase pass. Source-pinned historical
artifacts remain historical evidence; this review does not refresh them or grant
a deployment action. Hardware and human acceptance remain pending.

## Verdict

**PASS**, limited to D181 host compiler-error retention and its reviewed evidence.
