# D099/D100 completed target acceptance review

2026-09-23 Asia/Dubai. Separate fresh-context, same-model reviewer; this is not
a cross-model or human review. The reviewer performed local source, receipt,
object and ELF inspection only, with no board/network command, independent
compile, upload, reset, MCU access, motor action, production edit or commit.
Owned files are this report and `P2_app_acceptance_review_raw/` only.

## Findings

No open BLOCKER, MAJOR or MINOR finding is established within the scoped
D099/D100 build-policy adoption task. D099-R1 remains closed by D100's local
remedy and is now exercised by all three real corrected-wrapper builds.

The initial explicit-library control was an experiment error: a literal
discovery value 1 remained active during ordinary core compilation and failed.
The reviewer did not identify that unsuitable control during the first runner
inspection. After the actual error arrived, the reviewer independently checked
the pinned sources and recommended the stock substituted phase property.
The corrected control succeeds; the original failure is retained and does not
count as successful acceptance evidence. Details follow below.

## Verdict

**PASS for the bounded D099/D100 app-only build-policy adoption.** Default,
inert Immediate and MATCH Immediate have actual successful compiler receipts,
verified source and artifacts, retained startup/native behavior and the required
explicit-library rejection evidence. This closes the ordinary app's compile-time
RAM blocker under the checked `native-app-v1` policy. It does not establish a
loaded application, runtime safety, physical acceptance or any P0-P7 phase gate.

## Corrected-wrapper evidence

Read AGENTS, the active P2 resume state, FACTS, D015/D098-D100 and both public
contracts, the prior D100 local review, and the D098 dependency review. The date
is Wednesday 23 September, the scheduled P0 gate day; no schedule entry supplies
a missing human gate. D051/D075 permits the bounded software work separately.

`review_results.json` records this review's fresh independent ELF32/ARM decoder
and actual receipt checks. It does not reuse the implementation auditor's ELF
decoder. Current board_tool, policy, command reference and D100 contract hashes
equal the previously reviewed D100 hashes exactly. No source, config, test or
tool changed from checkpoint 2ded06a during this acceptance task. The previous
46 new / 78 established host tests and local 19-control / 3118-rejection review remain
separate prior evidence; this reviewer does not claim to have rerun those suites.

For each of the three modes, the reviewer independently checked:

- Actual successful compiler JSON and the separate expanded-properties JSON,
  explicit FQBN/safety flags/startup, identical command arguments except the
  preflight-only option, all 84 controlled command properties, all 18 precompile
  pin hashes, and their postcompile identities. Only the two CLI timestamp
  properties differ between preflight and compilation.
- Exact 82-file source list and every current byte, reconstructed aggregate
  `570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84`,
  unchanged generated INO CPP, 73 expanded compilation commands and 121 metadata
  payload hashes. The 117 dependency files contain none of the removed six
  Bridge/RPC-related libraries. Actual successful app results have no library
  entries; this is distinct from the properties-only preflight.
- Every downloaded final/debug/temp ELF and packaged ZSK against the completed
  wrapper and collection receipts: nine ELFs and three packages in total. Each
  package equals its ELF after the 16-byte header. The default and Immediate
  package difference is exactly offset 14, 0 to 4; this proves packaging, not boot.
- All 176 undefined imports in every ELF, unchanged loader identity, 39 native
  exports and 42 AEABI bindings with nonzero addresses. No Bridge/Serial/RPC
  singleton roots reappear.493 retained project function identities remain.
- Actual main, initVariant, static-thread startup, setup, loop and the app
  constructor with normalized code, relocations and resolved BSS targets.
  Main remains exported; the strong loop hook is `7047`; one init entry names
  `_GLOBAL__sub_I_setup`, with no fini entry. Runtime 168888 B and
  NativeSources 848 B remain unchanged. Setup still supplies empty physical grants.

Default and inert Immediate have the exact D098 final ELF
`9808dc594d77be8f43865a17542a48b715b4d5ee4a1277d6f946d0a6ccb09e65`.
Their 73 objects, 1438 allocated sections and 2912 relocations equal the D098 candidate.
MATCH final ELF is
`523f8c12aad4a9f62ff82d8d923bd90dcdd47299b9c026df5c8c2c8ad8fc38b6`.

MATCH changes exactly three allocated sections, with corresponding relocation
changes: MotorGate::transact and UnoQPort::writeEnable/writePwm. Those are the
existing MOTORS_ALLOWED branches. All other 1435 allocated sections are identical;
none is added or removed. The reviewer inspected their source and saved actual
disassembly in `match_motor_functions.txt`: low enable precedes PWM transactions,
four channels and settling precede conditional enabling, error paths inhibit,
and native ownership/period/timer/readback checks remain. Command/hold validation,
governor, edge code and startup are unchanged. This is compile-branch inspection,
not an observed motor trace or permission to execute the MATCH image.

## Explicit-library control and rejection

The unconditional phase-independent `SumoPolicyFixture` source consists of the
same three files in both successful branches. `library_results.json` checks
current fixture bytes, exact target file-set/hash captures before and after each
compile, the 18 pins, process exit 0, strict actual success envelopes, discovered
library lists and four artifact hashes per branch. These fixture binaries were
hashed on the target; they were not downloaded or decoded by this reviewer.

The fixed 0 candidate in run `e6e7e84e7b5a4eeda78c094829685d45` succeeds and selects
only SumoPolicyFixture. The corrected ordinary control in fresh run
`c4a32af6b4554bb2aa542bdb695124ca` succeeds and selects SumoPolicyFixture plus the
six normal Bridge dependencies. Independently passing each unmodified successful
JSON result to the actual app validator raises the exact external-library-policy
error. This reaches the nonempty-library check before app-name/phase-property
checks, so it demonstrates rejection for the intended reason.

The initial literal 1 control in the first run exits 1 with missing
Arduino_RouterBridge.h from core analogReference.cpp. Its failure, discovery list
and raw hashes are preserved in `initial_fixture_control_failure.json` and the
original experiment directory. Pinned platform.txt:108-111 defines normal phase 0
and the substituted phase flag; pinned CLI preprocessor/gcc.go:38 sets phase 1
only during discovery. The control correction uses that exact stock property,
not a new production policy, source change, installed modification or weakened
success assertion. The two successful commands differ only by separate run/build
paths and the fixed 0 versus stock discovery property. This isolated compatibility
experiment is not a D100-wrapper build and proves no arbitrary library's behavior
under a globally fixed phase 0; the app policy rejects all external libraries.

## Memory and limits

| Actual build | Program bytes | Compiler RAM payload | Nominal remainder | Conditional pristine load peak | Conditional largest payload |
|---|---:|---:|---:|---:|---:|
| Default0/0 |153684|248308|13836|252472|9668|
| Immediate0/0 |153684|248308|13836|252472|9668|
| MATCH Immediate1/1 |154156|248684|13460|252856|9284|

Compiler exits are 0 and low-memory warnings are preserved. The reviewer
independently recomputed section payloads and the prior pinned loader allocation
formula from the newly decoded final ELF sections. MATCH adds 376 B copied text;
its extra global-symbol entry adds 8 B temporary allocator consumption. Conditional
figures assume the same pinned loader, pristine pool, persistent-flash peeks and
no additional constructor/interleaved allocations. They are not measured current
free RAM, fragmentation, stack headroom or runtime minima.

No new upload key or physical grant follows. Application load/startup, full 800 us
timing, native UART integration/framing, local reset, calibration snippet output,
physical sensors/motors, PINMAP OK and all human phase gates remain outstanding.
The previous D091 synthetic recorder measurement is not full-app runtime proof.
Future integrated owners require their real linked image and a new memory audit.

Reviewer helper failures and corrections are retained in
`harness_adjustments.md`; no production or test assertion was changed. Next action:
the coordinator may record this scoped adoption and continue eligible P2 software,
preserving all runtime, physical and human authorization boundaries.
