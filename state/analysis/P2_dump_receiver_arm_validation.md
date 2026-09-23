# D113 receive-only connection evidence validation

IMPLEMENTED / HOST-TESTED / SCOPED-REVIEW-PASS, 2026-09-24 Asia/Dubai.
No board execution is included in this result.

`tools/dump_match.py` adds an opt-in fresh connection ticket and one observation
mode. Immutable private Linux receipts and bounded process/socket observations
describe the actual receive-only TCP connection. They explicitly leave router
registration unknown. Existing no-ticket/offline behavior is unchanged.

Final source SHA256: `5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717`.
Contract: `37dca22f86c9bb636ce7bd4188c86907ef8f16b6948631da0f8e5994f9d06f7a`.
Independent tests: `c864142fed553356254cdbfc97d7cdccf41eb2b4a78ed4a1cc4537292445fe44`.

The independent author used the public contract without reading implementation
bodies. Its final isolated WSL run passed all75 methods:42 new and33 unchanged
D090 methods, plus their unchanged nested18 config assertions. A separate reused
same-model source reviewer privately reproduced75/75 with zero skips. This is
separate review, not a fresh-context phase gate or cross-model review.
Exact commands, exit statuses, source copies, counts and elapsed times are in
`P2_dump_receiver_arm_raw/author/validation.json`, `run4_final_*`, and
`P2_dump_receiver_arm_raw/reviewer/final_review.json`.

Original failures are preserved. The first fixture incorrectly mapped the
simulated Linux root and omitted binary stdout; its reviewed repair changed no
test-method AST. No current residue existed at the one inspected real temp path;
the flawed run is not claimed to have been confined. A separately frozen new
test then exposed a real missing explicit-transport check. The sole production
fix rejects that new-mode CLI case before remote access; controlled red/green
and the final full suite prove the repair. No established test was weakened.

The review has no open finding. It verifies finite file/process/TCP queries,
receive-only traffic, preserved fragment/error evidence, failure precedence,
and unchanged legacy parser/receiver paths. See
`../reviews/P2_dump_receiver_arm_review.md`. Concurrent D114 staging edits are
outside this verdict and their exact copied helper hashes remain in receipts.

This proves software behavior under controlled substitutes. It proves no actual
router registration, clean framing, native UART dump, MCU action, physical
acceptance or human gate. A bounded bare-board Linux smoke is the next separate
observation; firmware remains the earlier D104 inert probe.

## Subsequent bare Linux smoke

The reviewed single ticket01aac4fffa214aa2b332b261734de7e9 passed on USB target
2629958581: CONNECTED then TERMINAL/TIMEOUT, zero received bytes, capture exit1
as expected, no successful bundle. Linux closed the socket12013.388427ms after
its12s deadline start. Before/after boot, service and existing socket identities
were unchanged. Original commands, partial output and14-file manifest remain
under raw/reviewer/smoke_runs/. Root rehashed every retained file. F138 records
this Linux-only observation; no MCU action or native UART transmission occurred.
