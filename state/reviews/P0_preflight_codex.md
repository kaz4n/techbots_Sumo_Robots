# P0 manual-check preparation review — 2026-09-22

Scope: changes after f0794fb for the user's request to explain manual checks and
continue work. Native reviewer `/root/preflight_review` started with a fresh
bounded brief, read the repository/specs and reviewed actual changes without
editing files. This is separate-context Codex review, not cross-model review.

## Finding and repair

Initial MAJOR: the proposed Immediate matrix startup measurement omitted the
official UNO Q manual section5/p15 warning about using the matrix before startup
completes. The boot logo and blank first sketch draw also made an undefined
first-visible-frame endpoint unsuitable as a sketch-entry timestamp.

Resolved: FACTS F-061 records the manual warning and installed-loader ownership
unknown; G3 is qualified without claiming a measured failure. The checklist and
worksheet distinguish identifiable SUMO display readiness, with its display
delay, from sketch entry and from the boot logo. The script rejects Immediate
matrix uploads before transport pending verification. Compile-only remains
available; the timing-only sketch does not access the matrix.

## Final reviewer verdict: PASS, scoped software/instructions

No open BLOCKER, MAJOR or MINOR findings. Reviewer verified fixed read-only
preflight commands, strict SSH, command deadlines, truthful failures, no firmware
operation or Monitor connection, zero bench motor macro, compile/upload FQBN
and artifact agreement, and preservation of the reviewed-source hash guard.
Firmware/config/manifest/locked tests are unchanged.

Coordinator command:
`wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v`

Result: **45/45 passed, exit 0**. Raw final output:
`state/analysis/P0_preflight_tests.txt`. Nine preflight tests were authored in a
separate context from the specified CLI contract, using isolated SSH substitutes.
Tests include reported SSH timeout/auth failures; no real deadline-expiration or
board operation was measured. The code's command deadline is source-inspected.
The earlier 44-test pass preceded the added matrix-ownership regression.

Physical acceptance, installed versions/loader behavior, PINMAP OK and human
GATE P0 PASS remain pending. No real SSH/USB board connection, target compile,
upload, reset, motor run or voltage/timing measurement occurred.
