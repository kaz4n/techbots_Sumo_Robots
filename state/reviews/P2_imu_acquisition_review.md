# D081 qualified MPU6050 acquisition review

2026-09-23 Asia/Dubai. Separate same-model review against baseline `eb4ff3a`
and frozen contract `f0031e8`. Review ownership is this report and
`P2_imu_acquisition_raw/` only. No implementation, header, configuration, tests,
build configuration, ledger, board connection, MCU operation or upload is changed
or performed by this reviewer.

Independence disclosure: this context began without the parent's conversation.
Before assignment as reviewer, it gave read-only advice about the existing D079
fixture and public Bus header. That advice initially suggested a 14-byte second
read; the coordinator corrected it before D081 review. The frozen contract and
this review use the required status read followed by a **15-byte INT_STATUS plus
motion burst**. The reviewer authored none of the D081 contract, implementation,
or specification tests. This is separate same-model review, not cross-model review.

## Findings

No open BLOCKER, MAJOR or MINOR in the bounded D081 software scope.

- CLOSED MINOR, `tests/test_imu_acquisition.cpp:9`: the first independent focused
  build failed because the range-for initializer lists lacked the required
  `<initializer_list>` include under the actual no-exceptions host flags. The
  test author added that standard header only. The complete failed compiler
  output and initial source manifest remain in `initial_focused/`; the final
  unchanged tests pass normal, ASan/UBSan and the independent tooling runner.

The author also preserved an initial native fixture failure: its selected
3500-to-100 poll workload did not exhaust the shared allowance. The repaired
case uses 3500-to-500 and adds positive controls proving each standalone request
fits separately. Failure predicates remain intact; no production repair or
test weakening was needed. A draft 47-entry setup-response typo was reported
and corrected before its first compilation, so it is not claimed as an executed
failure. These development receipts are retained in the author evidence.

## Reviewed source and contract

Actual production hashes:

- `src/hal/imu_bus_unoq.cpp`:
  `1955d95c5e523e1538aaa44c1aa72bfc79398937245a0b573dc7285796a00603`.
- `src/hal/imu_acquisition.cpp`:
  `6dd161d0f4837ecb0c0b2874b1d7a7ddff6228c79c786ae69c2ff6890eabb4ed`.

`scope_audit.json` and the final snapshot manifest bind headers, config, fakes
and final tests. Baseline comparisons confirm no changes in core, application,
locked tests, D080 implementation, original D079 fixture/cases/runner, original
setup Bus substitute, or board wrapper. Config adds only IMU_SILENCE_US=20000;
the strict original declarations and B16 defaults remain checked.

Both native transactions use the same Operation instance, original start,
deadline and poll count. The first transaction completes its full STOP-clear,
idle, ownership/error/time checks before the second admission. Readiness and
motion status diagnostics remain separate from native error_flags. Only the
completed second 15-byte transfer can publish observation data; rejected status
or any transport failure clears payload and enters the existing terminal latch.
Failure cleanup remains one separate bounded local disable, never bus recovery.
The existing public wrappers retain their D079 transaction body and behavior.

Acquirer privately owns Bus and Setup, arms once at checked setup completion,
clears results per call, and validates native shape, aggregate timing and phase
metadata before decoding. NO_NEW advances neither sequence nor silence anchor
and returns no cached motion. Call and completion checks reject exactly 20000us;
time reversal and half-range ambiguity preserve the last validated observation.
Runtime faults clear payload/phase/gap fields and retain an identical report
without further I/O. Only accepted observations advance the uint32 sequence and
anchor; numerical payload equality is accepted without inventing generations.

The source audit and retained manufacturer extracts support the explicitly
adopted shadow/read-clear inference, not silicon synchronization or physical
sample timestamps. The second status read cannot be omitted or counted as an
additional observation. The conditional 198-clock slow corner exceeds 600us
and must fault under the unchanged bound. No blocking API, heap allocation,
new remote path, motor write, core integration or clock change was introduced.

## Independently reproduced checks

`P2_imu_acquisition_raw/review_run.py` copied 308 source/test/build-tool files to
an isolated Linux `/dev/shm` workspace after the final author freeze. The
snapshot contains the final completion-wrap and all-15-NO_NEW-byte cases.
All snapshot files still matched the repository after execution. Exact commands,
exit codes, text-mode outputs, fixture identities and source hashes are retained.

- Focused actual Acquirer/Setup tests pass normal and ASan/UBSan independently:
  15 cases and 36,491 assertions each, zero failures or skips.
- All ten existing D079 tooling methods pass, including the full 83 positive
  native case executions and 992 parent assertions. The 102 subprocess receipts
  contain 100 exit-zero commands and the two required exit-one isolation failure
  sentinels. Parent output reports 49.389s. Their original assertions and native
  model are unchanged.
- All seven new D081 tooling methods pass in 22.240s. Their 27 subprocess
  receipts all exit zero: 15 Acquirer cases/36,491 assertions, 14 native cases/
  260 parent assertions, nine configuration variants/299 assertions, and two
  actual probe startup modes. Native child checks propagate through the existing
  failure listener; parent assertion totals are not all child assertions.
- The native cases cover exact 1+15-byte protocol order, STOP/idle before the
  second START, zero/one/unexpected status bits, repeated equal/changed payloads,
  errors and ownership loss in both phases, failure zeroing, final deadline
  minus-one/equality/wrap, shared frozen-clock exhaustion with standalone
  controls, one cleanup bound and no allocations.
- Acquirer cases cover actual setup and one-time arming, setup/transport failures,
  no-new versus new observations, no cached bytes, malformed phase/shape fields,
  all 15 nonzero NO_NEW payload positions, exact call/completion silence
  boundaries, transfer completion wrap, time reversal, observation gaps and
  identical latched faults. Config variants reject invalid silence bounds before
  acquisition and unsupported profiles before setup I/O.
- Both actual probe macro configurations execute constructors, setup and 10,000
  loops with a zero-initialized Bus-call counter that is never reset. No Bus
  method is called. All eight upload-mode combinations reject before target,
  transport or remote lookup. These are host checks, never MCU execution.
- All 14 strict config methods pass. Source identities, return-code counts and
  output hashes are summarized in `final_receipt_summary.json`.

The parent's broader host/sanitizer/tooling runs are separate validation evidence;
this report does not infer their final outcome from the focused results above.

## Actual compile-only source and ELF boundary

The actual board-Linux compile receipt exits zero: 86,236 program bytes and
36,172 compiler global-memory bytes. These are compiler figures, not measured
runtime free RAM. Source identity is
`147e08b1c639e43094fce8c78094e5350d2e5852a8f8531df67948237ef9900f`.
The reviewer independently reconstructed and matched all 46 staged source files
and the aggregate identity without modifying staging. All three ELF identities
are bound to the input receipt in `identity_audit.json`; the unchanged base ELF
is `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
All 36 collected native symbol addresses are nonzero.

The final ELF retains actual Acquirer, Setup, decode, native acquireMotion and
shared-Operation transfer methods. Setup at 0x6c stores only the unused exercise
pointer; loop at 0x7c returns. Relocations at 0x74/0x78 bind entry/exercise. The
new probe constructor at 0x2490 initializes object/reference and inherited HCI
memory; its three indirect calls bind to memset through relocation 0x250c.
No Acquirer implementation initializer or startup sensor request appears.
The existing Bus and other native module initializers retain the inherited HCI
memory setup; Bridge/Serial/library initializers and loop-hook behavior remain
F091 limits. Full source receipts and selected actual disassembly/relocations are
retained; the reviewer performed no board connection or MCU operation.

## Exact existing inert-source replacements

Approved only after the actual source/startup review. The adopted manifest
matches all five exact values; no key was added. `inert_approval.json` records
the scoped approval, and `identity_audit.json` retains each constituent map.
No upload, integration or runtime authority follows.

| Existing key | Reviewed SHA256 |
|---|---|
| `bench/p0_matrix` | `b14998e3cfe8f9cab1794b189247f17ee7d80af22deb0ac41c4e8fd31a2555c0` |
| `bench/p0_timing` | `8ac0dd337e2e70449173f0a2e08acde9e02b95f301e8d95310d2bde23b84a96b` |
| `bench/p0_adc` | `a67c74ebcc59f24076f0de68e5396dca4339a434caa03be128ca07eed5c070eb` |
| `bench/p0_gpio` | `0b42c90e52c83d775256fa37f6dab19d47e4c99d6b80ada0441abbe416e71244` |
| `bench/p0_qtr` | `12bf5f74785b64460fc913725a66cd1a812f58752ad40836fe0684c0e668c623` |

## Verdict

PASS for bounded D081 qualified acquisition, observed-silence behavior and the
inert compile-only boundary. No open software findings. SC-AJ clock qualification,
F091 inherited runtime paths, physical identity/power/address/pull-ups/settings,
silicon freshness behavior, accepted sample rate and full-tick WCET remain
unqualified. Mounting, bias, calibration-presence and continuous-yaw integration
remain separate unfinished work. No physical B3 acceptance, application
integration, PINMAP/EXPLAINED record, human phase gate or motor-run authorization
follows.

Next action: coordinator binds this review to its final regression ledger and
continues the separately specified sample-presence/calibration/axis/yaw work.
