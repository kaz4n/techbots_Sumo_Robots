# D143 static remote helper code review

Date: 2026-09-25, Asia/Dubai. Separate fresh-context, same-model reviewer.
Scope: only `state/analysis/P7_static_link_probe_raw/static_remote.py`, its eight
actions, and conformance to the adopted D143 remote/runner contracts. This is a
host-tooling component review, not a phase, target, native-ABI or runtime gate.

**Disposition: two MINOR findings remain open; no open BLOCKER or MAJOR in the
reviewed repair.** Both original MAJOR findings are closed by source inspection.
Behavioral verification remains pending frozen independent tests; this is not a
host-tested component PASS.

## Reviewed identities

| Item | SHA-256 |
|---|---|
| First helper source, 32,185 bytes | `fa209bee067f416f7f7619e350562806b333b4d3e6faf902a7f51878eb231e1b` |
| Reviewed bounded repair | `ff7add89ac849c9849ad4cb0bfd41f7e0e5877d61df9b74150b7da2e354e069a` |
| Adopted remote contract | `a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39` |
| Adopted runner contract | `35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7` |
| D142 validator integration pin | `d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368` |

The helper and both D143 contract hashes were checked directly. The D142 module
was read only for the integration interface, not re-reviewed. HEAD at review was
`2da4979a067387d110885f5f68bca7f403c21ab4`; the helper was then untracked.
The coordinator subsequently preserved that first source in `cd5625e2` before
making the two bounded repairs. The exact text diff from that commit to the
repaired helper was inspected. Finding line references below refer to the first
helper source above; closure line references refer to the repair.

## Findings

1. **MAJOR, closed by inspection — surviving incomplete processes can disappear from inventory.**
   `state/analysis/P7_static_link_probe_raw/static_remote.py:355-357` suppresses
   every ENOENT from `inspect_process`, without checking that `/proc/<pid>`
   disappeared. A missing `comm`, `cmdline`, `status` or `exe` record while the
   PID directory remains can therefore turn an incomplete process into no
   candidate and let inventory succeed. Remote-contract lines 192-201 allow a
   vanished-process race, while other incomplete identities must reject.
   Confirm disappearance of the PID directory before treating ENOENT as that
   race; otherwise return PROCESS_INSPECTION. Keep ESRCH dead-process handling.
   This also matches the independent test author's pre-freeze clarification
   relayed by the coordinator. The repair at lines 355-365 keeps ESRCH handling,
   confirms an absent PID entry under the held `/proc` descriptor before
   accepting ENOENT, and rejects other incomplete records. No runtime
   reproduction was performed.

2. **MAJOR, closed by inspection — a late malformed boot-ID read loses partial-claim evidence.**
   `state/analysis/P7_static_link_probe_raw/static_remote.py:501-509` re-reads
   `boot_id`, whose strict UTF-8 decode can raise UnicodeError, but the local
   handler catches only OSError and Rejected. If that read fails after U/B/A
   were created and identified, the outer handler returns PATH and
   `failure_fields` supplies null partial identities. The created paths survive,
   but the already obtained run/build/artifacts identities are lost. Remote-
   contract lines 227-229 and 305-307 require CLAIM_INCOMPLETE with created paths
   and obtained identities. Route operational decode failures through the
   claim's partial-state handler, preserving its recorded identities. Test an
   initially valid boot-ID read followed by invalid UTF-8 at the final recheck.
   The repair at line 511 adds UnicodeError to this local handler, preserving
   obtained identities and CLAIM_INCOMPLETE after creation.

3. **MINOR — malformed deeply nested claim JSON becomes INTERNAL_ERROR.**
   `state/analysis/P7_static_link_probe_raw/static_remote.py:709-711` translates
   ValueError, UnicodeError and zlib.error into BAD_REQUEST, but not the JSON
   decoder's RecursionError. A deeply nested JSON value in C can fit inside the
   transport command bound and exceed the decoder recursion limit before schema
   validation. The generic handler then emits INTERNAL_ERROR/exit 3 instead of
   the contract's pre-admission BAD_REQUEST/exit 2 with empty data (lines
   297-299). Handle decoder nesting rejection as an invalid request, or reject
   excessive nesting before parsing. This remains fail-closed with no mutation.

4. **MINOR — rejected empty/oversize artifact identity is pathname metadata.**
   `state/analysis/P7_static_link_probe_raw/static_remote.py:540-544` returns
   empty/oversize FileRecords from no-follow `stat` without opening and checking
   the file descriptor. Remote-contract lines 254-255 require regular-file
   fstat metadata for these states. A replacement between lookup and reporting
   is not detected on these two branches. Open with the same nonblocking,
   no-follow safeguards, verify regular-file identity and retain checked fstat
   metadata without reading contents. This does not admit invalid artifacts;
   it affects the promised failure evidence.

## Coverage and limits

All eight dispatch paths and argument schemas were read. Inspection covered
fixed paths and hashes, no-follow descriptor walks, ownership, exclusive claim
creation, source enumeration/hash/recheck, eight artifact observations, export
comparison, pinned D142 loading, final-ELF chunk restrictions, JSON envelopes,
failure observations and postcheck ordering. No helper subprocess, compiler,
network, upload, reset, deletion or caller-selected production root route was
found. Python `compile`/`exec` is limited to the hash-pinned D142 source.

The review did not import or execute the helper, bootstrap, tests or validator;
independent oracles were still being prepared. Findings are source-inspection
results, not reproduced test results. No source, contract, test, shared ledger,
firmware or configuration was edited. Only this report was created.

Next action: resolve the two MINOR contract gaps, freeze independent tests before
execution, retain first failures and review the final source with actual host
receipts. No board action or broader probe acceptance follows from this review.

## Final source-inspection addendum

The coordinator supplied a second bounded repair with SHA-256
`521773e51b62e19421efe7e25192ed938e4367acd6336984b8c7ba954d9a93d1`.
That exact file hash and the complete text diff from preserved first source
`cd5625e2` were checked without importing or executing any implementation.
The earlier dispositions above remain the review history; this addendum is the
current source-inspection disposition.

- **Finding 3, MINOR, closed by inspection.** Current lines 728-731 catch
  RecursionError only at request parsing and translate it to BAD_REQUEST before
  admission. The normal rejection handler therefore retains empty data and
  exit 2. Unexpected failures after admission keep their separate handling.
- **Finding 4, MINOR, closed by inspection.** Current lines 549-564 open rejected
  empty/oversize candidates with O_NOFOLLOW/O_NONBLOCK/O_CLOEXEC, verify regular
  fstat metadata against the first observation, and recheck the named entry.
  They close the descriptor in finally without reading contents. Observation
  errors or identity changes return unstable with the original observed
  identity. Stable empty/oversize records use the checked fstat metadata.

**Current verdict: PASS for bounded source inspection; no open BLOCKER, MAJOR or
MINOR findings in the reviewed helper.** All four original findings are retained
above and closed by inspection. Independent tests were still unfrozen during
this addendum, so behavioral verification remains pending and this is not a
host-tested component, board, full-probe or phase-gate acceptance. Only this
review report was edited. Next action is independent oracle freeze and actual
host verification with retained receipts.
