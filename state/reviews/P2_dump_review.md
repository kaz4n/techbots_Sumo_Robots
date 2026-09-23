# D090 bounded IDLE dump: fresh independent review

Verdict: **PASS for the scoped software change. No open BLOCKER, MAJOR or MINOR finding.**

This is a fresh separate same-model review, not a cross-model review or phase gate.
The reviewer changed only this report and `P2_dump_review_raw/`; implementation,
independent tests, protected tests and state ledgers were not edited by the reviewer.
The objective was to review the retained-attempt transfer, actual native UART backend,
strong loop hook, receive-only capture and exact existing inert source identities.
AGENTS, active P2, B13/B15, D090 contracts, actual Robot/recorder/MotorGate interfaces,
installed source audit and relevant hardware facts were inspected. September 23 is
before the PLAN scope-cut and code-freeze dates; D075 permits this software work.

## Findings and dispositions

- MINOR, resolved: invalid existing output files/file ancestors returned capture
  error 1 instead of argument error 2. `tools/dump_match.py:187` and `:363` now reject
  them before transport. The original reproduction is retained in
  `P2_dump_review_raw/invalid_output_path_initial.json`; existing bytes were preserved.
- MINOR, resolved: native audit/contract packet arithmetic said 78 bytes. The shown
  MessagePack prefix requires 15 bytes overhead, hence 79 with 64 payload bytes.
  The corrected audit and native contract agree with the independent wire tests.
- MINOR, resolved: generic transport errors discarded exact command outcomes.
  `tools/dump_match.py:315` now retains argv, exit/timeout, timestamps and bounded
  stderr; both success and partial-failure metadata preserve the outcome.
- Resolved interface hardening: `src/hal/dump_uart_unoq.cpp:225` rejects control,
  NUL, CR and non-ASCII bytes before submission, permitting printable ASCII and LF.
  Independent native tests also now exercise the 80 us per-call budget, alongside
  the 100 ms packet deadline and adjacent/wrapped values. No test predicate was
  changed by the reviewer.
- Evidence repair: the first supplemental link artifact was overwritten by a
  same-name command receipt. That loss is recorded; a new `link_bodies.json` plus
  separate `link_body_capture.*` preserves the actual disassembly and exports.
  The receipt helper now refuses this collision. No production change was needed.

## Verified behavior and evidence

The transfer checks actual current IDLE, original decision age, monotonic tokens,
zero/disabled outputs and service intent. Unsafe or stale context cancels before
further source access or writes, including repeated timestamps. It binds the source
object and semantic summary, preserves loss/interrupted state, never resets the
Robot or recorder, and reports SENT_UNCONFIRMED only after acknowledged END bytes.
Partial writes, CRC progression, source replacement, reset, deadlines and lifecycle
refusals are covered. The actual Robot -> MotorGate -> AttemptRecorder -> Transfer
fixture preserves STOPPED evidence through an explicit local reset into IDLE.

The receiver validates strict framing, domains, ordinals, raw CSV consistency and
CRC before existing bundle validation. It retains partial evidence, distinguishes
caller-declared origin from physical acceptance and uses atomic no-replace directory
publication on Windows/Linux. No inbound motion/reset request or sender-controlled
filesystem path exists. Native runtime work uses fixed buffers/iteration limits,
checked readiness and ownership, exact saved PRIMASK restoration, no RX parser and
permanent poison after uncertain framing. Cancellation does not promise recovery
of already shifted bytes or of the Linux router decoder.

Reviewer reproduction (all pass, no skips):

- Isolated owner normal and ASan/UBSan builds: 26 cases, 4,052 assertions each.
  `P2_dump_review_raw/owner_results.json`, `owner_*_test.txt`, exact source freeze.
- Final receiver/native tooling: 44 methods in 10.499 s (33 receiver, including
  18 nested legacy config checks; 11 native methods). Native tests executed 154
  isolated normal/sanitizer processes with 4,870 assertions. These include actual
  C++ stream round-trip, maximum collections, hostile fragments and publication.
  `tooling_final.*`, `tooling_final_freeze.json`, `native_final/` retain evidence.

Root receipts were also inspected: full normal and sanitizer suites each pass
1,281 main cases/24,481,257 assertions and 65 enabled-MotorGate cases/3,847,552
assertions. The corrected existing tooling run passes 56 methods in 79.241 s
(25 SSH/tool, 24 ADB, 5 matrix upload and 2 staging checks). Four scoped Windows
publication/outcome methods pass. Historical wrong-import/fixture failures remain
separate; they are not represented as successful runs.

## Actual target and exact source approval

Target source `b8bb9366458c2472d856e81ea4678716ff16d00a3b3d16b51d008e1624818307`
compiled with MATCH=0/MOTORS_ALLOWED=0/default startup. All 72 retrieved source
hashes and the aggregate hash match current local bytes. All three actual ELFs
were inspected; upload-format ELF SHA-256 is
`132ca07034d6ad825cba1b545eae83db62b86f619c7d4555ba4e6c62c6ef44d1`.

Each ELF binds `__loopHook()` as strong T at 0xacf0; the actual body is `bx lr`.
Main loads its 0xe718 relocation and invokes it at 0xe704. Eleven initializer
entries were inspected: the native initializer performs storage initialization;
the probe initializer calls the passive port accessor and memset; Bridge remains
passive; the serial buffer constructor initializes a semaphore and storage. Base
and sketch static-thread lists are empty. Forty native and 42 AEABI loader exports
are nonzero; supplemental fmod/sqrt addresses are nonzero. Actual native instructions
save PRIMASK, mask interrupts, use barriers and restore the saved mask.

`P2_dump_review_raw/target_review.json`, `target_startup_excerpts.txt` and root
`P2_dump_raw/link_bodies.json` document these checks. The initial target_review
pending note is closed by the supplemental artifact and this final report.

`P2_dump_review_raw/source_approval.json` explicitly approves **only** the six
existing keys and exact hashes in `inert_proposal.json`; the refreshed registry
matches them exactly. No new upload key was added. `bench/p2_dump_compile` remains
compile-only. Protected tests and the established config test file have no edits.
Final reviewer source/test freeze hashes still match.

## Limits and next action

The compiler reports 315,332 program bytes and 238,596 global bytes, leaving
23,548 nominal bytes and a low-memory warning. This is not actual loader/free-RAM,
stack, 200-second storage, physical link, baud or full-tick timing acceptance.
Setup-only device_init still has unbounded TEACK/REACK waits. Actual setup ownership,
clock accuracy (SC-AJ), Linux-loss cleanup and clean framing before a future owner
remain unqualified. The application scheduler/local reset UI is not integrated.
A software reset preserves recorder evidence; physical reset/reflash/power loss
has no such guarantee. No upload, MCU action, motor authorization, PINMAP/EXPLAINED
acceptance or human phase gate follows from this review.

Root should finish its byte/Git checks and commit the scoped evidence. Continue
with the separate RAM/loader audit and an identified inert runtime-bench scope
with clean framing established; retain all physical and human gates.
