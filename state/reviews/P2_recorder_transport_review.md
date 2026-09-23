# D116 recorder transport: independent review

2026-09-24. Final verdict: **PASS_SCOPED_SOURCE_TESTS_CHECKED_DEFAULT_TARGET**.
No open BLOCKER, MAJOR or MINOR defect in this D116 software scope. The separately
identified native full-dump throughput BLOCKER remains open and prevents treating
this as end-to-end native acceptance.

This is a reused separate same-model reviewer context, not a fresh cross-model
review or human gate. The reviewer read the contract, actual implementation,
existing Transaction/Gate/Transfer/button/menu contracts and narrow tooling diff.
The reviewer did not edit implementation/tests, operate the board, or approve an
upload. The initial static assessment preceded executable review; the subsequent
frozen test review and private Linux execution are recorded below.

## Exact reviewed scope

Contract: `state/analysis/P2_recorder_transport_contract.md`, SHA256
`056c69c8cc3246e24932b4e8c0e2e9855aac2051e28a57bf0bc448b955d8466d`.
The first implementation freeze is
`state/analysis/P2_recorder_transport_raw/implementer/first_source_freeze.json`.
Independent byte hashing confirms all five current files match that receipt:

| File | SHA256 |
|---|---|
| `bench/recorder/recorder.ino` | `19302674b85d23dca315e5d735774c7cbe21aad39ca6126019cc4a4ee8b1bf71` |
| `bench/recorder/src/recorder_transport.h` | `3f03e1823d731d8139b95428d77a81b8022fde0034a98cbef8aabf1f60efddd8` |
| `bench/recorder/src/recorder_transport.cpp` | `8ffb2795c0d14116043a7e37bb67314a4637ea08c00d0877a694367f7bfa4957` |
| `bench/recorder/src/recorder_transport_io.cpp` | `55ef764bd94e2584f538b435f8cbb17d1ad050a18629540e5c466aeeecd31440` |
| `bench/recorder/src/recorder_transport_scenario.cpp` | `2d732c91462264021b7b8f14346c6b38c08ba6ed9af837606dfd0c2a07d46c89` |

The header bytes before `private:` are identical to the adopted public header at
`99555b801a225503899000c14dac05f2d4d89cd6`. The implementation's syntax and static
inspection receipts are retained by its author; they are not runtime tests.

Independent hashing also confirms the coordinator's
`coordinator/first_tooling_freeze.json`:

| File | SHA256 |
|---|---|
| `tools/board_tool.py` | `8d89429a9add900ae6234bf9f1b663771d5cc50e9e0715b4017acc32a915fa4c` |
| `tools/app_build_policy.py` | `658d68842fcd44eea284e00ca33672d1feaef8140ea127f3accf815e645ff469` |
| `host/CMakeLists.txt` | `bcddc1525299f6a62382a529604231a07334c7d611ebb06ef1d46da846217136` |

## Findings and reasoning

No new BLOCKER, MAJOR or MINOR defect was found in this bounded static scope.

- `recorder_transport.cpp:44` validates PORT, GRANT and CONFIG before any
  initialization callback, with the disabled branch first. The constructor and
  default sketch retain passive ownership. Repeated begin and terminal polls
  do not replay setup or cleanup. The inert motor port has no native motor
  backend and rejects EN HIGH, nonzero duty, invalid channels and invalid periods.
- `recorder_transport.cpp:72` and `:101` preserve observed clock chronology,
  the final-setup equality baseline, original release grid, one epoch per poll,
  finite stalled-clock rejection and CLOCK/DEADLINE/MISSED admission priority.
  The zero-tick division is excluded with a constexpr guard. Structural deadline
  calculations use uint64 intermediates; elapsed accumulation starts after the
  actual final setup sample.
- `recorder_transport.cpp:128` and `recorder_transport_io.cpp:75` retain actual
  S/D/Gate-A/C evidence and the eight specified ordinary ClockPort observations.
  The two readiness brackets remain when readiness is skipped. Receipt and
  inhibited-IDLE checks precede readiness; the actual Transfer enforces its own
  menu authority. Reversed or expired transfer brackets fail before fabricated
  completion is possible. The closing deadline check precedes freezing success.
- `recorder_transport.cpp:27` inhibits the Transaction/Gate before asking Transfer
  to abort. Clock admission inside the Gate only latches the error; it does not
  recursively abort from its callback. Failure before initialization has no
  cleanup callbacks. Failure before C does not call finishAfter; failure after
  a genuine C leaves its actual finished/timing evidence available through the
  retained Transaction report, while its phase/fault may reflect cleanup.
- `recorder_transport_scenario.cpp:70` supplies explicitly synthetic current
  inputs and sequence metadata at actual D. It uses Transaction's previous
  feedback, actual release/GO/STOP identity, the full configured recording
  window and completed STOP tail. It does not fabricate frames or rewrite
  recorder storage. SEALED acceptance includes the full configured frame count,
  GO and release identity; incomplete/rejected recorder evidence fails.
- `recorder_transport_scenario.cpp:162` qualifies the synthetic neutral/MODE/
  release gesture from observations. Pending reset forms at the qualified
  release and is used at the immediately following open/S, with previous
  completion and source-age checks. Transfer receives its reset notification
  before the existing guarded Transaction service reset. Neither Gate nor UART
  is reconstructed. The new sequence continues across reset.
- `recorder_transport_scenario.cpp:205` and the stage table retain permanent
  service-only CALIBRATION/ABSENT line evidence, actual BOOT-to-IDLE transition,
  actual menu selection and one actual LOG_DUMP request. The three short MODE
  pairs have the adopted two-G neutral intervals. Match START/GO or motion after
  reset fails. SENT_UNCONFIRMED remains the Transfer's local terminal state and
  requires a genuine completed transaction; it is not a receiver claim.
- The tooling diff adds only the literal `bench/recorder` / `recorder.ino`
  selections to existing checked routing, default-startup/inert restrictions
  and the existing project-name map. It adds no upload key. Existing checked
  provider/precompile/profile safeguards remain on the selected route. CMake
  adds the three pure runner translation units to the ordinary host executable;
  no old assertion, locked test or active-Gate target is changed by that diff.

## Initial static-stage pending evidence and retained limitation

The initial static-only verdict withheld the combined source/test/target result.
Its pending frozen-suite execution and review included the full 200-second
positive run, exact CSV/source roundtrip, clock/failure/cleanup boundaries,
slow-progress TOTAL failure, terminal passivity, no allocation and native/default
wrapper checks. Relevant existing checks must remain intact. No result from
unfrozen test files is claimed here. The newly reported freeze is retained at
`state/analysis/P2_recorder_transport_raw/author/first_test_freeze.json`; its
execution and results remain pending for this verdict.

The exact checked default artifact still needs an independent whole-image audit:
source identity, strong empty hooks/startup constructors, imported owners and
native calls, actual layout, relocation/loader allocation order and peak fit.
Compiler RAM totals alone cannot establish fit. No TARGET-COMPILED or run
acceptance follows from this document.

The current FIFO-disabled native port has a **retained native full-dump
throughput BLOCKER**, separately demonstrated in
`state/analysis/P2_native_dump_throughput_audit.md`. A fast host sink cannot close
it. The proposed four-file D117 constructor-selected FIFO mode is only a future
proposal; D116 neither implements nor proves it. Full source/hardware grants,
framing, receiver attachment, UART exclusivity, MCU timing and physical B8
acceptance remain separate. This review authorizes no upload or human gate.

## Exact checked target addendum

The default-only target audit now passes. Evidence is
`state/analysis/P2_recorder_transport_raw/reviewer/target_e2cd303f_bench-default.json`,
its disassembly witness and `target_audit_run4.json`. The executable-test portion
was still pending at that target-only stage. No board operation was performed by
this reviewer.

The exact 95-file staged source digest is
`e2cd303f701fdff5699c17e40ae401713de0f28fca0c8f2d5ba24a2333e6b4a2`, checked
receipt `eb77072537df44eeb3d7c36fe049c642`. Rehashing proves five first-frozen
bench files plus 90 unchanged shared files, with the checked inert flags, base
FQBN, precompile pins and empty external-library set. All 16 collected ELF/ABI
commands succeeded. Three local ELF files and the ZSK package match their
receipt hashes. Final ELF SHA256 is
`538a7c81a9ee17ebdd9a9d2f6b1bc99a37c7f3de4772b9c373f43cf5675a4462` (102104 bytes).
Every final/debug function matches exactly; every temporary/final function
matches after normalizing only ABS32 relocation slots, while non-ABS32 Thumb
instruction bytes and relocation identities remain exact.

The sole sketch initializer builds passive factory/Runner/Transaction/Robot
state. Actual port bodies store callbacks without invoking them. Actual setup
passes false and four zero grants; begin's observed false branch stores DISABLED
and returns before owner initialization, and poll's terminal branch returns
before clock admission. The loop hook is strong and empty; the inherited
`initVariant` is weak and empty. Static-thread bounds are empty. The retained
native UART code is not executed by default startup. No native motor, sensor,
matrix, Runtime or Bridge owner is retained. All relocation-used imports resolve
against loader ELF `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`;
unused imported allocator/matrix declarations are not described as executed
dependencies. The exception allocation shim remains the abort stub.

Actual ARM ABI: Runner164176, Report120 at+32, Transaction162544 at+152,
TransactionReport504, Transfer1408 at+162696, AttemptRecorder159200,
FrameBuffer126300, DumpPort24 and UnoQDumpPort204. Runner raw BSS offset is zero;
the native owner begins at164176; total BSS is164384 with alignment8. No nm VMA
subtraction is applied and no capture/readout ABI is adopted.

Using the existing installed-loader model with aligned persistent-flash peeks,
the final compiler payload is216932 bytes. Ordered allocations peak at220280
bytes including initial bookkeeping, extension/section maps, copied regions and
symbol/export metadata. Every allocation fits the conditional pristine256KiB
pool; remaining span41864, largest payload41860. Debug/temp peaks are separately
reported as220392/221800; they are not deployment candidates. This establishes
conditional fit only, not actual heap fragmentation, stack, WCET or UART timing.

Three reviewer harness failures are retained in `target_audit_run1..3.json`:
the first over-assumed that both empty hooks were strong; the second initially
allowed only ABS32 in an expanded full-function comparison; the third copied a
small-ELF header-difference expectation although this ZSK length exceeds65535.
The corrected audit retains weak/strong distinctions, checks unchanged
THM_CALL/MOVW/MOVT bytes and validates the additional length byte. No production
or artifact bytes changed. The native throughput BLOCKER remains open.

## Final executable review and private rerun

The independent author's first freeze precedes its first execution. It discloses
reused context and earlier D104 knowledge, while keeping D116 expectations based
on the adopted contract/public headers without production-body inspection.
The reviewer subsequently read the actual tests and controlled fixtures.
They use the real Transaction/Robot/Gate/recorder/Transfer, literal lifecycle
tokens and timing assertions, original retained source bytes, and the actual
strict Python receiver and publication validator. Native/default tests execute
the actual factory/sketch with counted substitutes for the public native owner;
those substitutes are not a UART or pin measurement.

First-run failures are preserved. Only the Python copied-config method changed:
zero debounce/long values are refused by unchanged upstream static assertions,
and the G==LONG runtime profile now uses debounce596/long600 to satisfy the
existing MODE_SHORT_MS600 dependency. The previous long24 fixture could not
reach Runner validation. Independent AST comparison confirms all other methods
unchanged; every C++/fixture/policy input retains its first-freeze hash. The five
runtime profiles keep the original CONFIG and zero-callback assertions, and the
two static refusals require the specific countdown diagnostic. This is recorded
in `reviewer/fixture1_review.json`; no production or old assertion was repaired.

Final test hashes: C++ `7ecd1cdd58d516826508a85318fe6c90bb2483ae1a68e30b56a6e4991dbda792`,
Python `0fab202af4559143335489b1ade502d94925031d5a32a7a85e2eb78aec3a121e`,
policy `f933345e18cbf4eebe78eee4cbf288c11321a1ad9d1f481dfa64584406491557`.
The reviewer ran these exact final files in an isolated WSL `/dev/shm` copy,
without a shared build or any board path. `private_final_source_copy.json` and
`private_identity.json` bind the production/tooling/test bytes to their freezes.

`private_final_summary.json` passes all11 Python methods with zero failures,
errors or skips. Its underlying C++ suites pass22 cases/4202902 assertions each
normal and ASan/UBSan, two default native-wrapper binaries, six non-inert compile
refusals, five runtime CONFIG profiles and two explicit upstream static refusals,
and eight checked-routing policy methods. Four complete receiver roundtrips
and two truncated-prefix refusals pass. The full200-second positive/wrap cases,
all eight clock positions, closing deadline, Gate-before-cancel cleanup, invalid
progress, Linux loss, exact stream preservation, allocation guard and terminal
passivity are covered. Saturation/token exhaustion is correctly disclosed as
unreachable within this public finite lifecycle, not claimed through seeding.

The complete retained stream has532562 payload bytes,5015 lines,10027 packets,
5001 frames and eight events; the one-byte sink retains its exact300000-byte
prefix and fails the unchanged TOTAL budget. The reviewer independently recounts
682967 modeled native wire bytes with the existing15-byte packet overhead;
`actual_host_wire_accounting.json` preserves that arithmetic. These host results
strengthen, and do not close, the native throughput BLOCKER. Coordinator full
normal/sanitizer suites report1478 ordinary cases/50172466 assertions and187
active-Gate cases/4536952 assertions each; its prior-plus-new183 policy methods
pass. Those coordinator results are distinguished from this private rerun.

Final evidence index: `reviewer/final_review.json`, private command/full/summary
and command receipts, exact target JSON/witness, fixture review and original
author failures/freezes. No actual load, live RAM/stack/WCET, native delivery,
source/ownership/framing grant, motor permission, physical B8 or phase gate is
established by this scoped software PASS.
