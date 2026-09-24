# D143 static remote helper code review

Date: 2026-09-25, Asia/Dubai. Separate fresh-context, same-model reviewer.
Scope: only `state/analysis/P7_static_link_probe_raw/static_remote.py`, its eight
actions, and conformance to the adopted D143 remote/runner contracts. This is a
host-tooling component review, not a phase, target, native-ABI or runtime gate.

**Final disposition: PASS for this host-tooling component; no open BLOCKER,
MAJOR or MINOR findings.** The helper passes 28 original plus 5 independently
frozen supplemental methods; the separate bootstrap suite passes 23 methods.
No target, full-probe or phase acceptance follows. The sequence below retains
earlier review dispositions and the original failed test result.

## Reviewed identities

| Item | SHA-256 |
|---|---|
| First helper source, 32,185 bytes | `fa209bee067f416f7f7619e350562806b333b4d3e6faf902a7f51878eb231e1b` |
| Reviewed bounded repair | `ff7add89ac849c9849ad4cb0bfd41f7e0e5877d61df9b74150b7da2e354e069a` |
| Final reviewed and host-tested helper | `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8` |
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

## First host-result ruling: source mutation classification

The reviewer read the frozen oracle, original execution receipts and failure
trace after the coordinator's first execution. All 17 inputs in
`P7_static_remote_test_draft/freeze_remote.json` were rehashed unchanged. The
recorded helper SHA before and after execution is the reviewed `521773e5...`.
The helper suite ran 28 methods: 27 passed and one failed; the separate unchanged
bootstrap suite passed all 23 methods. The reviewer did not execute either suite.

The failing test at `P7_static_remote_test_draft/test_static_remote.py:449-455`
uses actual descriptor operations and replaces `app.ino` with identical bytes
on another inode during fstat. `read_file` detects the named-entry change at
helper lines 246-249 and rejects with exit 2/FILE_READ. The assertion fails only
because it expects SOURCE_DRIFT. It did not demonstrate hash-only acceptance,
successful collection, or an ignored source mutation.

**Ruling:** remote-contract lines 216-217 require rejection of source mutation;
lines 124-129 include both error codes but do not explicitly assign every source
mutation to SOURCE_DRIFT. The exact-code assertion is therefore more specific
than that contract text. It should not be represented as a demonstrated safety
defect or an unambiguous violation of an explicit error-code mapping.
Nevertheless, SOURCE_DRIFT is the precise classification for positively detected
source inode/content instability and matches the source action's existing
snapshot/hash checks. A bounded implementation clarification can satisfy the
unchanged frozen test without weakening any admission rule.

Recommended repair: distinguish detected identity/extent changes in `read_file`
from ordinary read failures, and let the source action map those detected changes
to SOURCE_DRIFT. An internal, fixed call-site drift-code argument or typed
identity-change exception is sufficient. Preserve FILE_READ for unrelated
unreadability/size/special-file failures and PATH for ancestry failures; avoid
message-text matching or blanket translation of every source read error. Keep
the original failed receipt and test unchanged. Additional parse/metadata
coverage remains separate and must be frozen before its execution.

Evidence SHA-256:

- `P7_static_remote_test_draft/first_remote_execution.json`:
  `4ba5ad23c70795a8f21d7915c7630b4167ed9e714d96078ae7736963644713e5`.
- `P7_static_remote_test_draft/first_remote_stderr.txt`:
  `cb5ed921ee826b4a59efb83b5c73e044b4e8a0019c71f1465409a08c52e097b0`.
- `P7_static_remote_test_draft/first_bootstrap_execution.json`:
  `6844aedfb32bc7ffbe1465b1eceb880a4ee4907f4d7c82a4740c05c9c09b9a2c`.

Paths above are under `state/analysis/`. Current host disposition remains
**not passed**, because the frozen suite has one unresolved classification
assertion. The earlier four review findings remain closed; no implementation,
test, contract or shared ledger was edited by this reviewer.

## Source-drift refinement inspection closure

The exact helper SHA-256 is now
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`,
preserved in `5fc7c2d9`. The reviewer inspected the full helper diff from
`047d6576` to that commit: exactly four changed lines implement the previously
recommended diagnostic refinement.

`read_file` at line 234 gains an internal drift-code argument defaulting to
FILE_READ. Only its opening and completed-read identity/stability checks at
lines 244 and 249 use that argument. Only the source action at line 427 passes
the fixed SOURCE_DRIFT literal. Argument parsing, filesystem permissions,
descriptor reads, bounds, no-follow checks and rejection conditions remain
unchanged. Ordinary size/special-file/read errors and ancestry failures retain
their prior handling; there is no caller-supplied CLI error-code option.

**Inspection disposition: accepted; the diagnostic refinement is closed by
inspection, with no new finding.** The original frozen helper test and freeze
remain byte-exact (`63a4a444...` and `b2e01d49...`). No retry receipt was yet
available when this addendum was written, so the actual host result still
requires the authorized retry. This reviewer performed no execution and edited
only this report. The original failed receipt and source remain preserved.

## Verified retry evidence

The reviewer read `P7_static_remote_test_draft/retry1_remote_execution.json` and
its original stderr receipt. The authorized retry reports **28/28 helper methods
PASS**, exit 0, unittest time 0.815 seconds. Both recorded helper hashes equal
the current reviewed `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
All 20 recorded pre/post input hashes agree; all 17 independent frozen inputs
were independently rehashed unchanged during this review. The original failed
execution remains retained.

The unchanged first bootstrap receipt remains **23/23 PASS**, exit 0. Those
bootstrap tests use independently constructed synthetic helper bytes; they
validate framing/bootstrap behavior, not a native board invocation of this
helper. No retry or extra execution was performed by the reviewer.

Retained retry evidence, under `state/analysis/`:

- `P7_static_remote_test_draft/retry1_remote_execution.json`, SHA-256
  `794be08e000261edcdf009adc646ba8cb8078d30eac21a37406019e92e1e6258`.
- `P7_static_remote_test_draft/retry1_remote_stderr.txt`, SHA-256
  `b3afe96cff148b05ac308c88591523680f31822658ac2ba9a9e15343e6e9a55f`.

**Current scoped verdict: no open findings; reviewed source and the frozen
baseline helper host suite pass.** Coverage supplements for deep JSON and
rejected-file metadata await independent freeze/execution and are not included
in these counts. This review establishes neither the full runner's correctness
nor board process/ownership behavior, static compilation, native ABI/runtime
acceptance, motor permission or a human phase gate. Only this report was edited.

## Final supplemental verification and disposition

The reviewer inspected the independently authored
`P7_static_remote_test_draft/test_static_remote_admission.py`, its separate
freeze and the original `first_admission_execution.json`/stderr receipts.
All four supplement freeze inputs were independently rehashed unchanged. All
22 recorded pre/post execution hashes agree, including final helper
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
The original helper suite and freeze remain unchanged.

The supplemental first execution reports **5/5 PASS**, exit 0, unittest time
0.349 seconds. Its coverage directly exercises the two original MINOR findings:

- Deep array/object claim JSON is rejected with BAD_REQUEST/exit 2 and empty
  data for all five claim-consuming actions, without filesystem mutation.
- Empty and oversize artifacts require real descriptor fstat observations and
  preserve their checked identities without reading the rejected contents.
- Replacing either rejected-size file after the first real fstat produces an
  unstable record with the initial identity and no hash.

Supplement evidence, under `state/analysis/`:

- `P7_static_remote_test_draft/freeze_admission.json`, SHA-256
  `54fbbaa24b0452cd621012240380ef1bc5fd09051a77b5035a441cb60c52ef72`.
- `P7_static_remote_test_draft/test_static_remote_admission.py`, SHA-256
  `0e94f5f1e9ca52ac84e5bfe51dc85c95ff28c1855bd8403433056ff8c9225aa9`.
- `P7_static_remote_test_draft/first_admission_execution.json`, SHA-256
  `660871c7b7f7627635dc973f8596db2fade900a26a7d732daf31b8bec72ed49f`.
- `P7_static_remote_test_draft/first_admission_stderr.txt`, SHA-256
  `4a42bf6e1cf51e4d7aaeb3b896cf886519afcd325891e92e074babda937873df`.

**Final component verdict: PASS; no open findings.** Final helper host evidence
is **28 + 5 = 33 passing methods**, with **23 separate passing bootstrap
methods**. The original failure, all original findings and their bounded fixes
remain recorded. This reviewer audited existing execution evidence and made no
additional execution, implementation, test, contract, shared-ledger or board
action. Only this review report was edited. The component's host disposition
does not authorize native execution or settle full-runner, artifact-native,
hardware, motor-run or human phase-gate acceptance.
