# P0 recovery software review — 2026-09-22

Reviewer: native `/root/tooling_review`, a separate fresh Codex context supplied
only a bounded repository review brief. Read-only; no implementation edits.
This is independent-context review, not cross-model review or a human phase gate.
Scope: recovered P0 tooling, tests, inert sketches, config correction, and vendor
byte preservation on top of baseline `b6b6680`. The coordinator transcribed the
reviewer's results below; no hardware evidence is claimed.

## Initial review: FAIL

- MAJOR: `tools/board_tool.py:113` contacted the board before discovering missing
  rsync. Baseline test suite: 14/15 passed; prerequisite test failed.
- MAJOR: `tools/board_tool.py:69` discarded sketch-local `src/` silently.
- MAJOR: `tools/board_tool.py:102` restricted upload by sketch name only; adding
  a source file still reached the substitute upload command.
- MINOR: `tools/board_tool.py:51` missed a symlink in the `bench` ancestor.

The reviewer reproduced these in isolated synthetic projects, never on hardware.
Root repaired each issue and added regression cases without relaxing assertions.
Follow-up found manifest hashes depending on CRLF config bytes; root normalized
config to the declared LF format and added an LF-checkout regression.

## Follow-up reviewer verdict: PASS (scoped software recovery)

No open BLOCKER, MAJOR, or MINOR in reviewed fixes. Seven focused controlled tests
passed. Reviewer independently verified complete staged-source SHA-256 values:

| Sketch | SHA-256 |
|---|---|
| p0_matrix | 261da4cc0e29d791cf492ea63fde5910d658dcbbfb66dfe3132e7a7400d2b874 |
| p0_timing | 7b52c5fbe30cf5e1073f9f20a10fb43f4e02b3b42722aaaf6d86caad0d6db20b |

The staged inputs comprise an inert sketch, configuration and empty core/HAL
placeholders. The manifest grants no motor-run permission. Reviewer also checked
the accidental FC removal, elapsed-counter repair, and vendored doctest hashes.
Full final coordinator runs are in `analysis/P0_tool_tests_recovery.txt` and
`analysis/P0_host_tests_recovery.txt`; these are host/script evidence only.

P0 remains HARDWARE-PENDING / GATE-PENDING: actual installed versions, target
compilation/upload, matrix plus printed-counter round trip, both startup times,
physical micro-benchmarks, verified pins, PINMAP OK and human GATE P0 PASS remain
absent. SC-I (Monitor versus R3/R4) and the protected behavior conflicts remain
unresolved. This review does not approve their recommended options.

## Fact report recovery review

`/root/facts_recovery_review` independently refreshed primary sources for the
tooling API assumptions and reviewed G1-G6 coverage. No new BLOCKER or unsupported
safety claim was reported in F-019 through F-054. Its MINOR finding was the
incomplete tool-dependency list in G4; root expanded it to all 13 package-index
dependencies. MPU6050-specific follow-up research is separately recorded in G6;
it is source research, not successful driver integration.
