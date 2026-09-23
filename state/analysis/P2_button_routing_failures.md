# D087 preserved initial failures

- Worker first CMake configure ran before the new enabled-MotorGate test file
  existed; it stopped before compilation. Direct receipt under implementer/.
- Root host_initial stopped on missing <initializer_list> in the new observed
  fixture. host_corrected/sanitizer_build then reached the newly added event
  fixture with the same missing include. host_repaired/sanitizer_build_repaired
  reached the new routing fixture, also missing that direct include. Root began
  retries before the author completed requested all-unit syntax checking; these
  are distinct drafts, not passing evidence. No existing assertion was weakened.
- After this repeated fixture-build issue, root stopped speculative full retries,
  referred it to the independent author and separate reviewer, and required
  strict syntax validation of ALL four new units before another full build.
  Author reports that check now passed, with direct syntax receipts.
- gate_initial deliberately stopped Robot, but its new fixture incorrectly
  required MotorGate Fault::NONE on that tick. Public motor contract requires
  STOPPED; author corrected this new expectation and retained every EN/PWM-zero
  assertion. No production change follows from this fixture repair.
- Initial event LINE256 scenarios omitted the independently fresh opponent bit,
  adding legitimate STALE_SENSORS32. Reviewer identified fixture contamination;
  author provided opponent_fresh=true to isolate the intended event-mask test.
- Initial root PROGRESS update attempted UTF8 decoding of inherited mixed bytes
  and failed before writing. Corrected to append new UTF8 bytes without rewriting
  the historical ledger. See root_ledger_failure.txt.

All failed command receipts are retained in P2_button_routing_raw. This analysis
is not a waiver or green result; final validation receipts are required separately.

Existing tooling then caught a real packaging issue: root's logframe.h comment edit
used Windows CRLF, so the newly reviewed inert registry failed two LF-checkout
subcases. Corrected only that header's line endings to repository-required LF;
no non-newline byte changed. Original target/approval retained, reviewer asked to
approve new exact hashes, and target compilation repeated for final exact bytes.
See line_ending_normalization.json. No test assertion changed.

Initial root manifest reproduction used the same filename for its internal map
and outer command receipt; the outer receipt replaced the internal map. The
reviewer's original complete approved file map and root exit0 remain. Final
adoption uses distinct manifest_adoption_final.json and *_command.json names,
retains the current-old map and the final independently approved map in full.
