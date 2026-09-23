# P2 B3 native I2C4 transport independent review

2026-09-23, Asia/Dubai. Same-model fresh-context reviewer; did not author the
contract, implementation or author tests. Baseline `6911b25`, prerequisite
commit `4ec0ef4`. Scope is D079 software transport and inert compilation only.
Read AGENTS, D051/D075/D079, P2/HARDWARE/B14, current progress, public header,
contract, installed-source audit and conditional timing derivation. Today is
Wednesday 23 September; the hardware/phase schedule has not been passed by this
review. Only this report and `P2_imu_bus_raw/` are reviewer-owned writes.

## Findings

No open BLOCKER, MAJOR or MINOR in the reviewed software scope.

Resolved MAJOR: draft `src/hal/imu_bus_unoq.cpp:394` sampled accepted time before
its final ownership scan and omitted a later error observation. Four independent
cases reproduced late BERR publication, transfer deadline equality, setup deadline
equality and falsely confirmed cleanup at its deadline. The exact failing draft
is SHA256 `82b0c3314b93095da723aadc11347e685b094fa011faa5dfd03974f35fa55e43`.
Source/header/test snapshots and failing subprocess outputs remain in
`P2_imu_bus_raw/boundary_1790148813696576940/`; the earlier two-case receipt is
also retained. Accepted observations now include later status checks and elapsed
time after the relevant scans. All four reviewer cases pass on repaired source
`940f4e2c8c7a251b7060c5336f54da9e128a4a6fae1b21f5f5851203deb9e0de` in
`boundary_1790149019517195839/`. A preserved intermediate run failed because the
old third-clock injection no longer had a following register access; selecting
the corresponding fourth-clock scan retained every status/zero-buffer assertion.
This is an observation-order fix, not a claim of atomic hardware snapshots.

The independent author's single-pin lock and pristine-admission regressions also
pass after per-pin guards and repeated preclaim checks. The installed lock helper
tests every supplied mask bit; using the combined mask could miss one locked pin.
The fixture was corrected to preserve locked pad fields, and original failures
remain separate from this model refinement. D079's explicit diagnostic addendum
now preserves native errors and unexpected protocol status without treating
ordinary progress as errors. No author test or production file was edited by
the reviewer.

## Verification

- The independently rerun frozen native suite passes all 10 methods in 146.531s,
  exit 0: 83 positive native cases and 992 parent doctest assertions. There are
  102 retained subprocess receipts; the only two nonzero exits are required
  assertion and signal failure sentinels, each exit 1. Child checks propagate
  failure but are not included in parent assertion totals. Source, header, config
  and fixture hashes stayed unchanged throughout the run. See
  `P2_imu_bus_raw/native_1790149071791499865/full_unittest.json` and
  `final_receipt_summary.json`.
- Coverage includes both addresses, all allowed registers, read-only/invalid
  requests, coherent 15-byte and single-byte reads, two-byte writes, repeated
  START/AUTOEND/STOP/W1C order, final RXNE+STOP, partial/extra/unexpected data,
  simultaneous error priority, terminal cleanup and complete-zero failures.
  It checks 27 metadata variants, 15 invalid configurations, source/device/IRQ/
  pad/clock ownership, irreversible and preclaim failures, wrapping deadlines,
  frozen-time total budgets, no allocation, 10,000 inert loops in both macro
  modes and every upload combination's refusal before transport lookup.
- Independent installed-source equivalence passes for 58 LL bodies, 723 LL
  macros, 4109 CMSIS definitions and all five complete peripheral layouts.
  `fixture_equivalence.json` binds the source and fixture hashes. Register storage,
  hardware progression and NVIC observations are explicitly modeled; they are
  not physical measurements. Forked boot isolation has no production reset hook.
- Source review confirms no motor writes, motion command path, Wire/semaphore
  transfer, allocator, unbounded loop, synthesized STOP, IRQ manipulation, reset,
  GPIO recovery pulses or retry. Claim ownership is irreversible; ownership loss
  cannot be reacquired for cleanup. Only PE is cleared during retained-owner
  cleanup; DISABLED remains a local acknowledgment. Private bytes publish once.
  All 37 checked source/probe functions are under 60 lines, maximum 30. Core,
  app, locked tests and board wrapper are unchanged from `6911b25`; config adds
  only the ten D079 declarations and retains all original B16 values.
- Actual board-Linux compilation passes at 81992 program bytes and 33788 compiler
  global-memory bytes. The exact source map is
  `f3e9b5464c0d83b0249cabf78c7cf73a5d150d4b3823277bce320d7d7a84d224`.
  All 42 current source files match the remote receipt. The three ELF hashes,
  36 nonzero native export bindings, direct I2C4/GPIOD/RCC/PWR and NVIC accesses,
  retained real methods, constructor relocations, setup and loop were inspected
  independently. Setup only stores the exercise pointer; loop returns; the new
  source/probe constructor wrappers only initialize inherited RouterBridge HCI
  memory and contain no call instructions. Inherited Bridge/Serial/library
  initialization and `__loopHook` remain F091 limitations. See
  `target_review.json` and `final_disassembly.txt`.

## Exact existing inert-source replacements

The reviewer approves only these five reproduced replacements for the existing
P0 keys. No new key, upload, execution permission or runtime qualification is
approved. `inert_maps.json` retains every constituent file hash.

| Existing key | Reviewed SHA256 |
|---|---|
| `bench/p0_matrix` | `c51afcbcfc101b821e2634600a6846edd43eebaf92c935382fd7885b9227612d` |
| `bench/p0_timing` | `550d18636072c3415bac35bea1294f139dbdbf154ebaf61134bf1d0d38de0d10` |
| `bench/p0_adc` | `b6ab0ee7e0cf71553eb4a585a65f3248322474544eb44dc721059f87d037cfff` |
| `bench/p0_gpio` | `72b4ffb1fa0bcd3bc2d2c988ed4fb308a5a6c38fc987d07bcea9d20416b8ae2e` |
| `bench/p0_qtr` | `a8dab8c24998253afa6285aae326a39092bcd896c9ff0dc8be70d65c0b467e54` |

## Verdict

PASS for D079's native transport software and inert compile-only boundary.
Global SC-AJ clock qualification and F091 inherited runtime paths remain open
deployment blockers. The conditional timing calculation does not prove oscillator
lock, compliance with physical MCU clock limits, bus waveform or whole-tick WCET.
Physical address, pull-ups, sensor configuration/readback/freshness, sample age,
axis transform, bias and yaw remain unqualified or unfinished. No MCU operation,
upload, motor permission, application integration, physical B3 acceptance or human
P2 gate follows. Next action is parent integration of this reviewed increment and
the separately bounded sensor-setup/sample-validity work, within D075 authority.
