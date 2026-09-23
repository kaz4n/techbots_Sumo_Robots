# D113 first implementation freeze

Objective: add opt-in Monitor connection tickets and one-shot read-only observation
to the existing receiver, preserving legacy/offline capture and exact wire bytes.

Owned production change: `tools/dump_match.py` only. Source SHA256:
`1492b81d8bbf76d2cd70d1cdea68fdff6097085a2d1f24b9cd10b72752766f79`.
Frozen before checks in `first_dump_match.py`/`first_source_freeze.json`; adopted
contract snapshot binds `33f5429e84bb9a1d78c1ce4c13c32771769d424e4f37fd014852733c3316d1bc`.
Original source remains `baseline_dump_match.py`.

The single module contains fixed shared pure schema definitions, remote
no-follow/exclusive no-replace receipt publication, bounded process/socket
observation, the receive-only ticketed path, and host CLI/evidence integration.
The shared source loaded locally is a repository-owned literal; it does not
execute receipt/caller text or perform I/O. The legacy remote receiver literal
is unchanged, and its original iteration body follows only an opt-in dispatch.

`python state/analysis/P2_dump_receiver_arm_raw/worker/static_check.py` exited0.
`first_static_checks.json` records host/generated-program syntax PASS, identical
legacy literal/iteration AST, passive schema top level, maximum function53lines
and no function>=60lines. This check compiles syntax and inspects AST only.

No independent test body was read; no test suite, generated remote program,
module import, board operation, Monitor connection, upload, reset or MCU action
was executed by the implementer. Behavioral acceptance remains with the separate
frozen test author and source/API reviewer. No post-freeze source edit is allowed
without coordinator direction; retain this first source before any correction.

Next action: independent execution/review, then only concrete scoped corrections
authorized by the coordinator. A live smoke remains a separate reviewed task.
CONNECTED means sampled TCP identity only, with router registration UNKNOWN and
hardware/MCU permission false.

## Coordinated second freeze

Independent checks identified that the new CLI inherited board.transport's SSH
default when SUMO_TRANSPORT was absent. The coordinator authorized one added
presence guard in `_validate_cli`, scoped only to ticket capture/observer.
No legacy path, shared board tooling or test was changed by this implementer.

Final source SHA256 at this handoff:
`5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717`.
`second_source_freeze.json`/`second_dump_match.py` preserve the exact source before
checks and bind the clarified contract
`37dca22f86c9bb636ce7bd4188c86907ef8f16b6948631da0f8e5994f9d06f7a`.
`second_source.diff` records precisely the one added line. All first-freeze
receipts/snapshots remain unchanged. `second_static_checks.json` passes the same
syntax, generated-body and legacy-preservation checks; maximum53lines remains.
Independent author/reviewer were notified for their corrected-source rerun.
No independent tests, generated bodies or board operations were run here.
