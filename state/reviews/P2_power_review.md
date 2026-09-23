# P2 B5 native battery acquisition independent review

2026-09-23, Asia/Dubai. Fresh-context, same-model independent reviewer; not a
cross-model review. The reviewer did not author the contract, implementation,
configuration, test fixtures or test assertions. Only this report and
`P2_power_raw/` are reviewer-owned. No commit, upload, reset, MCU attachment,
peripheral invocation or physical measurement is authorized or performed here.

## Scope and current status

Contract commits `a8e840d` and `fbd9d96`, followed by the documented claim/EPOD
clarifications. Read the complete AGENTS.md, D-051/D-075/
D-078, current PROGRESS, PLAN schedule, HARDWARE power/pin proposals, P2 bench
criteria, public `power.h`/config, the four ADC source audits plus errata report,
and existing inert upload guards. Applied the code-review-and-quality skill.
The host date was 2026-09-23, matching PLAN's Wednesday P0/P1 schedule; no human
gate is inferred from the date or D-075 software authorization.

## Findings

- [MAJOR, resolved in the current reviewed source] `src/hal/power.cpp:229` (initial
  reviewed source): after `waitFlag` observes LDORDY, initialization can issue
  the calibration command before checking ownership again. `waitFlag` checks
  ownership before the flag read, so an ownership loss accompanying that
  readiness observation is detected only after another ADC write. Revalidate
  after observing readiness and before the next command. The independent
  LDO_READY fault-injection case exercised this boundary: the independent test
  author's retained receipt has 17 cases/866 assertions, with exactly one
  failure showing six writes rather than five at loss. Snapshot
  `P2_power_raw/power_ownership_gap_snapshot.cpp` has SHA256
  `4b526ba7ea0d2421a012e9a5b3d1cc6e61ac6805623dbfcd9c76f831d7c5ca92`.
  The author then rechecked ownership and time after readiness, checked minimum
  wait completion, and checked again before calibration/enable. The reviewer
  independently ran the unchanged native core expectations on source SHA256
  `fcb1965c89a1362a530985ecdf3bd39ca7d80ef679c8b3b082c0a292e8785584`:
  all 17 cases/866 assertions passed, zero skips. `native_initial/` retains the
  reviewer commands/streams; `ownership_gap_test_author_receipt.json` explicitly
  identifies the earlier receipt as the test author's, not the reviewer's run.

- [MAJOR, resolved in final source; identified by implementation author]
  `src/hal/power.cpp:289`: an ignored first common-divider write can leave the
  peripheral apparently pristine after an owned failure. Register state alone
  did not prevent a new Reader from recovering that boot. The final source sets
  a zero-initialized permanent claim immediately after pristine admission and
  before the first ADC/pad mutation. Preownership failures do not consume it;
  neither destruction nor a new object clears it. The reviewer inspected that
  placement, its I/O-free initialization, and the dedicated takeover test.
- [MINOR, resolved] `tests/native_power/native_cmsis.h:13`: the initial fixture
  used another family's SYSCFG address `0x40010000`. Installed CMSIS and the
  compiled target use `0x46000400`. The test author corrected the fixture and
  its mapped memory region; all eight modeled bases now match the saved U585
  declarations. Production required no change.
- [MINOR, resolved] `tests/native_power/cases.cc:98`: stock initialized/failed
  owner scenarios initially forked below a successful Reader admission, thus
  inheriting its permanent claim and bypassing the intended state guard. They
  now run in a separate root-level test with fresh children. The reviewer read
  the corrected structure. CHECK and SIGKILL sentinels explicitly prove that
  child assertion failures and crashes propagate to a failed test execution.

The coordinator also added the source-required EPOD operating-state checks.
The reviewer independently verified RM0456 pp410-411 and pinned clock source
496-538/603: at the selected nominal 160 MHz, EPOD BOOSTEN/BOOSTRDY must be set
with the stock MSIS4MHz DIV1 booster prescaler. These are read-only checks and
are distinct from the SYSCFG analog-switch BOOSTEN=0 profile. They do not
resolve the independent MSI automatic-calibration limitation.

## Contract checks

- ADC1/common CMSIS layout is specific to U585: ADC1 base `0x42028000`, common
  base `0x42028308`, CCR at common offset zero. A0 remains proposed PA4/channel9.
- The later LFTRIG requirement explicitly supersedes the older audit's CFGR2=0
  candidate. Ordinary calibration, capture/latch exclusion, command-safe CR
  writes, W1C status clearing and completion-anchored minimum spacing agree
  with the saved installed LL/CMSIS sources.
- Stock ADC1 deferred/failed-init exclusion and ADC4 IRQ-enabled-but-idle
  admission are distinct. Runtime register snapshots supplement the required
  whole-application exclusion of concurrent ADC/DAC/pad/clock owners.
- One acceptance deadline spans sample admission through final cleanup; finite
  poll guards also terminate a frozen clock. Shutdown is a separate bounded
  attempt and cannot turn a failed stop into DISABLED or stale data into valid.
- Existing tooling refuses non-allowlisted uploads before board lookup; only
  five original P0 inert sketches appear in the existing source manifest.

## Final source and compiled evidence

Final source SHA256 is
`505e008ea99f6e739968572ae5674a858fc646a81001f6e6af01e3117c60543d`;
public-header SHA256 is
`bc927275bfa22d24f9eaf3070896d58ceb22537de1242ae90adc4e449e33e4d0`.
The reviewer compared the actual driver, final public API, probe, tests, and
source guards. No implementation/test/configuration was edited by the reviewer.

`source_checks.json` independently verifies all nine saved native header hashes
and the cached official RM0456 PDF hash, and retains 18 selected manual pages.
`native_header_comparison.json` verifies all 28 copied LL operation bodies
against the installed originals. Fixed-width register layout, W1C semantics,
read-as-set command masks, calibration barriers, fixed poll counts, ownership
checks and full-width raw validation were reviewed directly.

The coordinator's final board-Linux compile-only receipt is
`state/analysis/P2_power_raw/target_a936d10d_bench-default.json`.
The reviewer independently matched all 40 staged files and aggregate source
`a936d10d471c80c937bee3d312a99de40acfbc57fefced9fd51d409a097024dd`.
All collection commands returned zero and all 36 selected native imports resolve
in the pinned packaged base ELF. Final loadable ELF SHA256 is
`93b66eaa69238030e45c22c96b47d44609a99f8505916b7f35e9727385a1976c`
(81,132 bytes). Compiler-reported globals are 33,476 bytes; this is not measured
free RAM or a deployed-loader qualification.

`target_review.json` and `final_disassembly.txt` retain the reviewer checks:
setup only stores the exercise address, loop returns, and the new power/probe
constructor wrappers only initialize inherited RouterBridge::HCI memory with
no call instruction. Exercise retains begin/read through relocations. Actual
ADC1/common-CCR offset, GPIO/PWR/RCC/SYSCFG/ADC4/DAC/NVIC addresses, two DMBs,
and 65,536/4,096 count limits are present. Existing Bridge constructors and
`__loopHook` remain inherited runtime limitations; no whole-platform startup
or Linux-independence acceptance is claimed.

The five exact inert hash replacements were approved separately for source
inertness, without adding an upload key. `inert_maps.json` independently rebuilds
each staged file map; the adopted manifest matches all five aggregates. Core,
app, locked tests, config and board_tool.py remain unchanged from `fbd9d96`.

## Final native verification

The final nine-method independent reviewer run **passed in 163.787 seconds**,
exit zero. It executed 75 positive native cases: 18 core, six ownership, four
timing, one takeover, 22 invalid-config variants, 22 metadata variants, and two
probe cases. No positive case failed or skipped. The 480 reported assertions
are parent status checks, not a total of every assertion executed in children.
All 104 subprocess receipts are retained in `P2_power_raw/native_final/`:
102 return zero, while two deliberate CHECK/SIGKILL sentinels return one and
are explicitly required by the passing isolation test. Every receipt identifies
the same final production SHA256 above; staged config variants are separately
identified. `final_unittest.txt` retains the reviewer run output.

The fixture uses fresh OS processes for modeled boots and provides no reset
hook into the production claim. Admission exclusions, reset-only takeover,
readiness ownership loss, setup and runtime deadline equality, frozen/wrapped
clocks, stale/partial/overrun data, full-width raw rejection, failure cleanup,
no cached voltage/allocation, 10,000 inert loops in both host macro modes, and
every tested upload mode refusing before board lookup all pass. The reviewer
also read the coordinator's normal host and ASan/UBSan results: both existing
CMake test executables pass; sanitizer output reports 1,030 host cases and 37
enabled MotorGate cases without failures or skips.

## Explicit limitations

SC-AJ remains an open **global runtime/deployment blocker**: stock MSIS automatic
calibration is enabled, and oscillator-ready/mode/rate checks do not establish
its lock history, actual frequency or recovery. This review will not describe
software-valid samples as qualified physical voltage measurements. Divider,
reference, supplies, silicon revision, deployed-loader identity, B5's 0.05 V
multimeter criterion, runtime WCET, PINMAP, integration and human gates remain
unproved. No motors or MCU are exercised.

## Verdict

**PASS for this P2 B5 software increment. No open BLOCKER, MAJOR or MINOR in the
reviewed implementation/test/compile-only scope.** The two production lifecycle
findings and two fixture findings above are resolved and independently checked.

This is not a P2 gate, integration/deployment approval, motor authorization or
physical B5 pass. SC-AJ remains an explicit global runtime blocker. The next
action is the coordinator's ordinary evidence/commit handoff while preserving
all inherited runtime and human acceptance requirements.

## Post-review fixture canonicalization addendum (2026-09-23)

**PASS; the existing software-scope review remains applicable.** Independent
`P2_power_raw/review_normalization.py` checks bind all 29 archived worktree files
byte-for-byte to this review's original passing-run hashes, and all 29 archived
Git blobs to `e6b7060`. The archive contains exactly 58 entries and has SHA256
`8edf4a8dc3adbe140ddf31e924c280335232802c972a7afd33f07b2fc2d88927`.

The five changed Git blobs contain trailing-whitespace/EOF cleanup plus the
extractor's explicit two-line output-format loop. All existing extractor AST
nodes are unchanged; assertions, register values, LL bodies, macro continuation
boundaries and vendor notices are preserved. Every other scoped change is CRLF
normalization. Executing the extractor in an isolated reviewer scratch tree
reproduces all five current generated headers byte-for-byte; scoped
`git diff --check` passes. The independent receipt is
`P2_power_raw/normalization_review.json`.

Production `power.cpp` remains SHA256
`505e008ea99f6e739968572ae5674a858fc646a81001f6e6af01e3117c60543d`;
`power.h` and `config.h` also retain their original reviewed hashes. No broad
suite was rerun for this bounded formatting followup. The original passing
native run and compile-only review remain the applicable evidence, with SC-AJ
still an open global runtime/deployment blocker and all physical/gate
limitations unchanged.
