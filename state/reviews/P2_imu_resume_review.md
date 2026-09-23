# D094 resumable IMU independent review

2026-09-23 Asia/Dubai. Separate fresh-context, same-model reviewer; implementation
read-only. Baselines: contract `e507c42`, pre-contract `2f0981c`. Scope: actual
native Bus and Acquirer implementations, public contracts/headers, shared legacy
helpers, independent added tests/build registration, inert retained-method probe,
and seven existing source allowlist identities. Reviewer writes only this report
and `P2_imu_resume_review_raw/`; no board command, MCU action, source/test/config
edit, commit or human gate was performed by this reviewer.

Read AGENTS.md in full, D051/D075/D094, current progress/resume, P2 requirements,
relevant hardware/facts, D094 contract and complete source/public-spec audits.
Wednesday23September matches PLAN's original P0/P1 row; D075 is the documented
software-development exception, not a phase pass.

## Findings

- **[MAJOR, resolved] `src/hal/imu_acquisition_async.cpp:93` and `:131`: malformed
  IDLE/unknown progress could bypass native cancellation.** The first version
  treated every nonPENDING reply with a nonOK transfer as a terminal transport
  failure. An IDLE/unknown envelope does not establish that its native operation
  has ended. This violated the malformed-progress cancellation rule and could
  abandon retained ownership. The reviewer found the branch independently by
  source inspection; the coordinator's retained `host_normal_01.txt` and
  `host_sanitized_01.txt` corroborate six failed assertions. The coordinator fixed
  production by admitting only known COMPLETE/FAULT states to the terminal
  transport shortcut. Independent reviewer ASan/UBSan tests now pass all twelve
  begin/advance, IDLE/unknown, NOT_INITIALIZED/OK/NACK combinations with one
  cancellation, plus four known-terminal precedence combinations without duplicate
  cancellation. See `P2_imu_resume_review_raw/acquirer_execution_02.json`.

No remaining BLOCKER, MAJOR or MINOR source finding in the reviewed scope.

The first authored test set contained two contradictory new interpretations of
unknown progress with a nonOK status. D094 now explicitly rejects unknown/IDLE
before status precedence; the author changed only the new terminal-precedence
stimulus to known FAULT and added unknown/IDLE+NACK cancellation cases. Initial
failures and the original expectation remain in coordinator receipts and
`analysis/P2_imu_resume_failures.md`; no established or locked assertion changed.
The reviewer independently tested both sides of the clarified boundary.

## Source conclusions

- `imu_bus_async_unoq.cpp:19` anchors a single clock read and original operation;
  duplicates/report/post-terminal calls are passive. Private staging stays hidden
  until terminal acceptance. Construction/destruction introduce no I/O.
- The advance switch performs one CR2/TXDR/RXDR/STOPCF action or finalization.
  The fixed two-pass readiness helper reobserves flags; repeated START has a third
  guard. Admission spends at most three cumulative passes. No wait/drain loop is
  introduced; one existing bounded cleanup is the terminal exception.
- The same elapsed<600us and cumulative8192 observation budget cover both
  transactions and every caller gap. STOP clearing and fresh final acceptance
  remain separate. The8192nd observation is valid; requesting another is not.
  RXNE need not be sampled low between bytes; only final-byte RXNE may accompany
  STOP. Failed transfers expose zero bytes/count and retain established phase
  diagnostics. Cancellation/error/ownership paths perform no retry or synthetic
  STOP and do not regain lost ownership.
- Legacy Bus collisions use shared helpers in the original translation unit;
  unsupported register requests still refuse before collision handling. Idle
  legacy paths retain their existing behavior. Acquirer legacy collision retires
  its native operation immediately without accepting the collision's caller time.
- Actual Acquirer checks chronology/silence before advancing, preserves the
  original begin/native start, and increments sequence only after accepted final
  shape, phase, source-time and decoder validation. Pending progress cannot enter
  Estimator as a Sample. Completion pulses are not replayed by passive reports.
- No changes to config, core behavior, MotorGate implementation, app scheduler,
  established tests or locked tests relative to `2f0981c`. The new probe's setup
  only stores the retained exercise pointer; its loop is empty. The exercise is
  a link test, not an implemented application schedule.

## Verification evidence

Reviewer-executed checks:

- `review_execution.json`: UBSan actual-native suite,4cases/48 parent assertions
  PASS. Cases remove TXIS/TC/RXNE/STOPF during the second guard, remove TC during
  the third guard, permit the8192nd missing-event observation then reject another,
  and complete NO_NEW by final acceptance on exactly observation8192. Child
  assertions are enforced by the established process-isolation listener and are
  not included in the printed parent totals.
- `acquirer_execution_02.json`: ASan/UBSan actual Setup/Acquirer,2cases/156assertions
  PASS, independently closing the MAJOR and retaining genuine terminal transport
  precedence. `acquirer_execution.json` retains a reviewer-harness compiler failure
  caused by a missing initializer_list include; only that include was corrected.
- `independent_manifests_final.json`: independently reconstructed all staged bytes
  and WindowsPath ordering without invoking board_tool or editing the manifest.
  Current allowlist equals all seven recorded hashes exactly, with no added key.

Coordinator/independent-author evidence inspected:

- Full normal and ASan/UBSan host runs `host_*_03`:2/2 executables PASS each;
 1349main cases/24,501,424assertions and111enabled-Gate cases/3,850,460assertions.
- Independent author:22actual Acquirer/Estimator/Robot cases/17,259assertions per
  motor macro mode;21native resume cases/728parent assertions;44established native
  cases/932parent assertions with async source linked; actual probe startup plus
 10000loops,1case/13assertions per mode; eight mocked upload refusals before target
  or transport lookup. Exact source snapshots and outputs are in
  `analysis/P2_imu_resume_raw/author/`.
- All61 controlled tooling methods PASS in `tools_regression_01.json/.txt`.

## Final target source and ELF inspection

Reviewer independently rebuilt the78-file probe source map and Windows-order
digest from current source and matched the captured target map byte for byte:
`b495f085a5e9d0277e0837b5fdf1e8da32f7149e0be3945bc706ebb9e85ec485`.
The actual compile-only receipt `target_compile_02` exits0,330844program bytes,
247564globals and14580nominal remaining, with its low-memory warning preserved.
Earlier target `d1d724dc` predates the production fix and is not final evidence.

`P2_imu_resume_review_raw/target_identity.json` binds the reviewed source to the
captured target receipt and three ELF identities; the upload-format ELF hash is
`cf73213fcd3ded8f72c3bd9db0f2262f21cbc1a1dbad04e60a14ce118311b50c`.
All three retain the actual native Bus/Acquirer, Estimator, Robot, MotorGate and
recorder methods. The captured native40 and AEABI42 export lookups each have
nonzero addresses and no missing/error result. Coordinator source_integrity records
188imports with no additions/removals against D092 and the unchanged installed
loader hash39d4a4fd...; this is offline linkage evidence, not loader execution.

Inspected disassembly and literal-pool relocations: setup at0x64 only stores the
exercise pointer; loop at0x74, strong `__loopHook` at0xce10, and weak initVariant
at0x107ac return immediately. The13-entry init array resolves to named functions,
including the new Bus translation unit's passive RouterBridge/HCI guard and
pointer initialization. The probe owner initializer uses memset, field stores,
the pure callback/period builder `UnoQPort::port`, and MotorGate's copying
constructor; it does not call begin/advance/exercise or a peripheral callback.
Inherited Bridge/Serial runtime paths remain unqualified and unchanged; no new
background service is introduced. Captured excerpts/relocations are saved as
`P2_imu_resume_review_raw/target_startup_excerpt.txt`. The reviewer did not run
gdb, transport or any board command; inspection used coordinator-captured files.

## Existing source allowlist

Added native CPP source-owned definitions are functions; Arduino headers also emit
the passive framework initializer inspected above. Added pure CPP has only passive
constexpr/functions. Header state initialization is passive. Existing sketch-local
startup code is unchanged. Source review supports refreshing only these seven
existing identities; this does not approve new uploads or new allowlist entries.

| Existing key | Reviewed Windows-order source SHA-256 |
|---|---|
| bench/p0_adc | f72e4927b0893e7be96f222f06c67183ee62e0856b28bdc0946563ddf50e1fe6 |
| bench/p0_gpio | efc9770e58536c0a84398567bd3eff048296f713aca84a4377ffb1a7b0dbc599 |
| bench/p0_matrix | d62f785a8313ab51172ca68d6ebaeffdd5c19f26d7aaf941072ae3d472efa8d8 |
| bench/p0_qtr | e70397612c33a852df0e7c6d0d7763bb491db4224416ee04906c26be7c7ab16b |
| bench/p0_timing | 457807ea4634e34094a9f4ababbaaaed8a27c85412557dfdcfa557fa591d8f71 |
| bench/recorder_inert | d9e40d00956167c3b0b399fbe9f7c2ed7bb1844a6d6857962116a5617acf6506 |
| bench/ui_matrix | 5a423fa4fe7b2bf3d082586cadb4b4acead0ffd32e25c5d76b9d1c7d50b21ed9 |

## Limits and next action

Host models and source review do not qualify physical clock/stretch behavior,
sensor coherence/freshness beyond D081's conditional inference, useful service
rate, loaded RAM/stack, QTR service margin, per-call or full800us WCET, physical
sensor/motor acceptance or any human gate. A stopped caller has no autonomous
timeout cleanup. The target retains all downstream methods and issues a low-RAM
warning; linker accounting is not a runtime memory measurement. The old D091
uploaded image and measurements do not validate this new source.

The next work is an explicit complete-tick application/resource owner under D092,
with truthful pending-source aging and cancellation/cleanup accounting. This
review does not implement or approve that future scheduler.

## Verdict

**PASS for the scoped D094 software/source/compile-only change.** The MAJOR is
resolved; no open BLOCKER/MAJOR/MINOR finding. Final target identity and startup
inspection are complete. This is not a physical acceptance or phase-gate pass.
