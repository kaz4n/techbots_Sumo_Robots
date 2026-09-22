# P0 fixed counter transport scoped review - 2026-09-23

## Scope and independence

Same-model fresh-context review by a separate Codex agent. Read-only for implementation,
tests, ledgers, manifests and hardware; this report is the reviewer's only file change.
No board command, upload, reset, dependency change, credential operation or motor run
was performed by this reviewer. Local clock at session entry: 2026-09-23 01:45:41 +04:00;
PLAN section 3 schedules P0 completion/P1 today, before either scope deadline.

Read full AGENTS.md, PROGRESS.md, PLAN section 3, relevant HARDWARE/FACTS, D-051,
D-052, D-062, P0_recon_toolchain.md and REVIEW_GATE.md. Reviewed real changes since
4206bfd, including untracked counter .cpp/test sources. Public contract/header commits
8f94452, cab665c and 3f9ea7f preceded implementation/tests; clarification 2f7e1b4 and
the corrected installed audit define the final exact-status and idle-IRQ expectations.
Read the bounded-stack source report, installed IRQ audit and prior debug-startup audit.
The installed-source reports are supplied evidence, not this reviewer's independent
board inspection. The exact new target binary is assigned to a separate audit.

## Findings

- No open BLOCKER, MAJOR or MINOR finding in the reviewed source/test scope.
- Resolved specification wording: the early feasibility audit described generic positive
  status and faulting a callback without an active transaction. The actual installed
  driver returns Boolean 0/1 status. Contract 2f7e1b4 now explicitly requires exactly 1
  for active update/ready/final-TC status, rejects every other value, and keeps a stale
  idle callback quiet after disabling TX. The source did not change for this clarification.
  The independent author's initial 31/34 result is retained as a failed expectation
  record, not described as a source failure or silently omitted. The revised new,
  unlocked cases test the published clarified policy; established locked tests did not change.

## Source assessment

- `bench/p0_matrix/src/counter_packet.cpp:13`: one 36-byte slot; constant-length loops
  encode the entire uint32 range without allocation. Busy refusal preserves the current
  bytes, cursor and original deadline. `accepted` permits exactly one byte, and every
  invalid lifecycle operation latches a permanent fault. The final accepted byte remains
  BUSY; `complete` is a separate transition. Unsigned subtraction at line 62 handles
  wrap within the contract's service interval; invalid constructor timeouts fault.
- `bench/p0_matrix/src/counter_uart.cpp:34`: each active callback uses at most one update,
  readiness check and size-one FIFO fill. Non-1 status/count faults and disables TX.
  After byte 36 it waits for one subsequent callback and TC==1 before counting completion;
  no final FIFO acceptance is reported as completed or delivered. Idle/fault callbacks
  disable TX without trying to send or restart a partial message.
- `bench/p0_matrix/src/counter_uart.cpp:67`: deferred initialization occurs once, only
  through setup, before the short transaction lock. It checks helper/device/config and
  callback-registration results and never overrides installed baud, pins or framing.
  Failed first setup is terminal; repeated begin does not reinitialize established state.
- All shared runtime packet/diagnostic accesses and UART interrupt enable/disable calls
  are under `irq_lock` with the exact saved key restored. Admission publishes the packet
  before enabling TX in that same section. RX/error IRQs are disabled before callback
  publication. Saturation in `increment` is correct by source inspection; UINT32_MAX
  counter saturation was not driven through billions of public API calls in tests.
- `bench/p0_matrix/p0_matrix.ino:37`: setup is the only initialization caller; loop only
  services the deadline, renders bounded matrix data and attempts one periodic submission.
  No new Bridge/Monitor/Serial begin/write/flush, inbound handler, RX drain, motor write,
  dynamic allocation, delay or wait loop was found. MOTORS_ALLOWED==0 has compile-time
  guards in both sketch and adapter. The config diff adds only the two P0 timeout/baud
  constants; protected behavior defaults, pins, core/HAL and established locked tests
  are unchanged from the reviewed baseline. Functions meet the scoped size convention.

## Independently reproduced evidence

Executed from this workspace through `wsl -d Ubuntu --cd
'/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots' --`:

| Command after the WSL prefix | Reviewer result |
|---|---|
| `python3 -m unittest discover -s tests/tooling -p test_counter_packet.py -v` | exit 0; 25 cases, 156553 assertions; strict real-source C++17 build; runner 4.680 s |
| `python3 -m unittest discover -s tests/tooling -p test_counter_uart.py -v` | exit 0; 39 cases; strict real adapter+packet build with actual config; runner 1.202 s |

Reviewed the independent formatting oracle, lifecycle/boundary cases, and UART substitute
sources. Adapter cases start fresh processes and check one-byte callback bounds, setup
failures, no RX/configuration operations, separate final completion, busy retention,
timeout before/at/after/wrap, zero/negative/unexpected positive driver results, permanent
faults and saved interrupt-mask restoration. These are host substitutes, not physical
UART/IRQ timing evidence. `git diff --check` also passed.

Read `state/analysis/P0_counter_target_compile_20260923.txt`: the actual coordinator-run
matrix/default compile reports exit 0, MATCH=0, MOTORS_ALLOWED=0, 77596 program bytes and
31416 global bytes. This reviewer did not run that compilation; compiler size reporting
does not measure runtime headroom or latency.

## Exact source approval

Independently rebuilt the per-file SHA-256 map directly from repository bytes and the
staging rules, without invoking staging or modifying files. Source, proposal and current
staging match exactly, with no additional source file. Approved source snapshots:

| Sketch | Files | Aggregate SHA-256 |
|---|---:|---|
| bench/p0_matrix | 28 | `75ab5a2257a6f322bc9b5c2ee9059f3e8ac6b3817eca39f03991d18e2ebda0af` |
| bench/p0_timing | 24 | `b4c61daf57f7273c93e97572d53f5ccd8ac456b4c104cdc328ab30d87086afd2` |

Full mapping: `state/analysis/P0_counter_inert_manifest_proposal.json`. At verification,
the unchanged upload guard file `tools/p0_inert_sources.json` still had SHA-256
`b1c4f8dbb80e4e1290eb25780aa161de8a39351dba2f6dedbcde3017520533e0`; its exact-hash check
would reject these new source snapshots. This report authorizes those source identities for the narrow
inert diagnostic review; the coordinator owns any subsequent guard update after the
remaining exact binary prerequisites are satisfied. Immediate matrix upload remains prohibited.

## Verdict and limits

PASS for scoped inert source and host-contract review. This is not a phase-gate pass,
production HAL review, motor authorization, full Robot timing result or unconditional
R3/R4 qualification. Installed CR1 exclusive retry paths are conditionally finite only
under the audited single-core, ordinary-IRQ-masked, exclusive-owner assumptions; this
review does not establish NMI/fault/debug/bus-agent behavior or physical forward progress.

Before a new upload, complete the separately assigned exact linked-binary/startup/driver
dispatch audit, including the unstarted required Bridge global and its loop hook. After
an authorized inert run, collect real received counters, deployed image identity and
runtime progress/failure/timing evidence. First TC startup, actual callback count/rate,
Linux-unavailable/late behavior, optical display and cold-power timing remain unmeasured
by this review. Diagnostic counters distinguish software admission and observed TC;
neither is acknowledgment of Linux delivery. P0 physical acceptance and all human gates
remain separate.

## Bounded fixture follow-up - 01:54 Dubai

Same reviewer, reused context for this follow-up. Reviewed only the additional fixture
diffs in `tests/tooling/test_p0_config.py` and `tests/tooling/test_p0_diagnostics.py`,
rechecked approved source identities, and read the coordinator's final receipts. No
additional implementation/test/manifest or hardware change was made by this reviewer.

No new BLOCKER, MAJOR or MINOR finding. The config fixture adds exactly two explicitly
expected diagnostic values: timeout 100000 us and existing UART baud 115200. It preserves
the exact declaration-set check, all 76 B16 values/types and every prior assertion.
The scheduling fixture adds public counter-transport stubs needed to link the changed
real matrix sketch; real transport remains covered by the separate opaque adapter tests.
All six original matrix/timing scenarios and their assertions are preserved. New assertions
check setup once, deadline service and submitted counter/time for boundary, delayed and
wrap cases. The diff is additive: 2 config lines and 42 harness lines, zero removed lines.
The shared synthetic millis/micros clock is a scheduling fixture, not a physical time-unit
or UART-delivery measurement.

Independently reran the two fixture suites with the same WSL prefix above:

- `python3 -m unittest discover -s tests/tooling -p test_p0_config.py -v`: 8/8 PASS,
  0.023 s; confirms protected B16 values and the exact two new diagnostic values.
- `python3 -m unittest discover -s tests/tooling -p test_p0_diagnostics.py -v`: 6/6
  PASS, 1.054 s; the existing strict build/UBSan harness remains enabled.

Read preserved `P0_counter_tooling_20260923.txt`: the initial full run had 150 tests,
one config-inventory failure and one missing-public-transport-symbol setUpClass error;
that setup error prevented the six existing diagnostic scenarios from running. These
were fixture omissions, repaired without changing firmware or relaxing old assertions.
Read `P0_counter_tooling_20260923_final.txt`: final full discovery reports 156 tests,
44.130 s, OK and PROCESS_EXIT=0. The six restored scenarios and exact config checks are
explicitly listed as passed. This is the coordinator's full-run receipt, not an independent
full-suite rerun by this reviewer.

Also read `P0_counter_sanitize_20260923.txt`: the coordinator's ASan/UBSan counter run
reports 40 Python test invocations, 13.841 s, OK and PROCESS_EXIT=0. Read the separate
`P0_counter_binary_audit_20260923.md` scoped PASS: it binds the exact new matrix source
to debug/stripped artifacts and checks constructors, sole UART ownership, dispatch and
saved BASEPRI restoration. Its driver-forward-progress and runtime limits remain in force;
this reviewer has not independently repeated its artifact inspection.

Independently recomputed source/proposal/current-stage per-file and aggregate hashes
again: matrix remains the approved 28-file `75ab5a2257a6f322bc9b5c2ee9059f3e8ac6b3817eca39f03991d18e2ebda0af`;
timing remains the approved 24-file `b4c61daf57f7273c93e97572d53f5ccd8ac456b4c104cdc328ab30d87086afd2`.
The coordinator has now updated the upload manifest to exactly these approved hashes.
PASS remains the source/test disposition; no open source/test review prerequisite remains
for the already authorized narrow default-startup inert experiment. No upload, execution,
actual received counter, timing, optical result, motor authorization or human phase-gate
pass is claimed by this follow-up.

## Post-upload evidence follow-up - same date

Same reviewer, reused context, local receipt review only. No new build, board command,
upload, readback or execution was performed by this reviewer. Reviewed coordinator
receipts `P0_counter_upload_20260923.txt`, `P0_counter_monitor_capture_20260923.json`,
`P0_counter_monitor_reconnect_20260923.json` and
`P0_counter_post_upload_identity_20260923.json`.

No material evidence inconsistency or unsupported claim in the proposed narrow scope;
no new BLOCKER, MAJOR or MINOR finding. Upload receipt identifies revision 6b99a60,
approved matrix source 75ab5a22, MATCH=0/MOTORS_ALLOWED=0/default startup, actual OpenOCD
upload/reset/start and PROCESS_EXIT=0. Its recorded completion 21:55:51.731637 UTC is
01:55:51.731637 on 23 September Dubai. This is a successful upload command receipt,
not independent byte-for-byte MCU flash verification.

Independently validated the captured JSON and current logger source locally:

- Both recorded logger SHA-256 values match `tools/board_tool.py`. AST extraction of
  its actual `logs()` program matches each recorded original command exactly. Executed
  commands add only `import signal; signal.alarm(8)` on separate lines before that body.
  The program receives socket bytes and writes stdout; it has no application-payload
  send operation. This supports the recorded zero monitor bytes sent.
- First capture contains exactly eight complete formatted lines, counters 4 through 11,
  in 8.119839899940416 s. The second contains exactly eight complete formatted lines,
  counters 56 through 63, in 8.130008299951442 s. Independently parsed counters exactly
  match the stored arrays and counts, with no malformed or duplicate line.
- Both receipts record empty stderr and remote status 142, consistent with the explicit
  eight-second SIGALRM deadline; this is expected observer termination, not a claimed
  zero-exit logger or MCU fault. Local receipt consistency validation exited 0.
- Capture-start timestamps differ by 52.015743 s and the first counter values differ
  by 52. These records show continuing counter output and this client's reconnection;
  absent per-line receive timestamps they do not measure precise 1 Hz cadence or jitter.
- Post-upload Linux debug ELF, stripped ELF and wrapped binary hashes all equal the
  separate pre-upload binary audit values. The read command hashes Linux filesystem
  artifacts only; it neither reads nor verifies deployed MCU flash.

The `ss` observation shows an already established 127.0.0.1:7500 client before the second
capture. Therefore the interval cannot be described as having no monitor subscribers,
and these runs do not demonstrate Linux-unavailable or router-stalled resilience.
Observed complete counter strings support actual delivery through the physical diagnostic
path into Linux and this receive-only logger. They do not directly observe the adapter's
submitted/completed counters, every UART interrupt, timeout/fault injection or optical
matrix appearance. The earlier 3 us RAM-jitter result belongs to a different image and
workload and must not be assigned to this counter/matrix workload.

PASS remains limited to the reviewed inert source/tests and the consistent observed
upload/counter-delivery/reconnect evidence above. Cold power-on timing, optical acceptance,
IRQ count/rate, new-workload WCET, physical fault handling, production Bridge/HAL/P2
acceptance and human phase gates remain open. No motor action or permission follows.
