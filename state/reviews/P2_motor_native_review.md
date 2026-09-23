# D077 native MotorGate fresh-context review

## Findings

None. No open BLOCKER, MAJOR or MINOR finding in this D077 software scope.

## Scope and independence

Fresh, separately spawned same-model reviewer; not a cross-model review. Read
AGENTS.md and REVIEW_GATE.md, D075/D077, the finalized native contract, relevant
HARDWARE/FACTS/P2 scope and clock/update audits, and the actual implementation.
Baseline is e814af7. Local date is 23 September 2026, before the PLAN's 28
September scope cutoff and 1 October freeze. D075 permits this P2 software work
while physical acceptance and original human gates remain pending.

Only this report and P2_motor_native_review_* receipts belong to this reviewer.
No implementation, test, config, tools manifest, shared ledger, board state,
phase approval or protected decision was changed by the reviewer.

## Source trace

- `motor_port_unoq.cpp:68-91,175-190`: source-derived candidate rates/periods
  are immutable; unsupported metadata returns zero periods. Factory and default
  construction perform no I/O. Candidate periods are 3200/250/3200/3200 at the
  selected 10 kHz; cached initialized rate and actual PSC checks are separate.
- `motor_port_unoq.cpp:94-154,247-287`: validate the whole GPIO/PWM bank before
  configuring EN; selected physical pads are unique and separate from opponent
  and QTR inputs. Device/channel identity and per-device routing indices are
  checked. EN LOW/readback precedes setup. Already-ready unknown timers are
  rejected; shared TIM3 is accepted only as this instance's initialized timer.
- `motor_port_unoq.cpp:193-244,289-327`: runtime LOW invalidates the transaction,
  native writes preserve status/readback errors, and PWM requires acknowledged
  LOW plus configured ownership. HIGH requires four current write receipts,
  current settle and unchanged settings. MOTORS_ALLOWED0 forbids nonzero native
  pulse requests and HIGH. Runtime callbacks do not initialize or remux devices.
- `motor_port_unoq.cpp:211-244,330-355`: exact reset/partial/full timer settings
  account for first channel enable and shared TIM3 progression. Full register
  comparisons exclude alternate modes/owners; TIM1 RCR/BDTR are checked without
  reading reserved advanced-register positions on TIM3/TIM4. Each used CCR
  matches the last acknowledged request.
- Settle clears stale UIF after all four writes, accumulates three distinct
  fresh observations, revalidates state and requires elapsed time strictly below
  150 us. One unsigned deadline and 4096-pass bound cover the complete attempt;
  no sleep, allocation, artificial UG, counter restart or elapsed-only success.
- `motors.cpp:60-98,142-205`: the existing Gate remains the caller and sole
  transaction boundary. Hold/governor provenance and fault policy are unchanged.
  Fault cleanup tries LOW and every channel zero plus settle; unconfigured
  channels remain explicit failures, and a reset cannot invent successful setup.
  Invalid feedback does not claim physically safe outputs.
- The new compile probe retains real begin/apply/reset calls in a never-called
  function. Its constructor/factory are inert, setup stores only the function
  address, and loop is empty. No application integration or transport was added.

## Reproduction and exact source guards

The production implementation reviewed after the bounded pin-mask repair has
SHA-256 `73e95df12de6ca020fac3df6490bf98dd3623868f577b28a9d8137d04dd0914f`.
Other exact source hashes and all five stage file maps are in
`P2_motor_native_review_manifest.json`. The earlier source-map receipt is
preserved as `P2_motor_native_review_manifest_pre_bit_guard.json` and is
superseded for approval. The repair only bounds bit formation; validPad still
rejects every physical pin >=16 before native GPIO configuration.

Independently ran all 10 config tests: PASS, exit0. Exact bytes and hashes are
in `P2_motor_native_review_config.json` and its stdout/stderr receipts. Existing
76 B16 defaults are preserved. `P2_motor_native_review_protected.json` proves
all 38 baseline core/app/existing locked files byte-identical to e814af7,
including all 14 existing locked tests and their .gitkeep.

Recomputed stage hashes with the actual board_tool.stage/source_hash functions
in a private /dev/shm root. Workspace build/stage and upload manifest were not
modified. All five previous hashes/maps match P2_opponent_review_manifest.json;
every new delta is only config's D077 constants plus motor_port_unoq.h/.cpp.
Those additions have no user hardware initializer. The target native translation
unit does inherit an Arduino.h RouterBridge::HCI initializer; its inspected body
only changes a guard and RAM fields, with no native calls or MMIO. Approval is limited
to refreshing the exact existing five source hashes recorded in the new receipt.
It does not expand the allowlist or authorize any upload.

## Independent native test replay

PASS: all 9 Python methods in 229.624 seconds, exit0; 167 compiler/executable
subprocess receipts all exit0. The 78 executed binaries comprise 38 behavioral
cases in each configuration, 74 malformed-metadata variants and 2 inert probe
variants: 152 doctest case executions and 217368 assertions, no failures/skips.
Default behavior has 108417 assertions; enabled behavior has 108603.

The fixtures distinguish preload writes, fresh update events and active values.
Coverage includes incomplete writes; stale, asynchronous, missing and clear-race
UIF; changed register bits/readiness/EN ownership; wrong periods/routing; boundary,
wrap and frozen-clock deadlines; setup and runtime native failures; real Gate
hold/reversal/full/zero/cleanup/reset; real Robot composition; and 10000 runtime
transactions with allocation/count guards. Both probe constructors/setup and
10000 loops perform zero fixture-native I/O. Eight transport/match/startup upload
combinations reject before target lookup or board action.

During review, requested the initially absent explicit post-HIGH raw-readback
failure coverage. The separate test author added semantic postwrite overrides
and failure injection at every observed setup/runtime GPIO-read position;
the final replay passes all those assertions with actual Gate cleanup and
invalid receipts. This coverage issue is closed without changing production.
The signed-domain and invalid-metadata shift compiler repairs and earlier fixture
failures remain preserved in the author's raw evidence and failure analysis.

Exact command/output bytes, per-subprocess evidence and pre/post hashes are in
`P2_motor_native_review_native.json`, its stdout/stderr and `_native_raw/`.
`P2_motor_native_review_summary.json` enumerates all raw receipt hashes. Every
input remained byte-stable across replay, and every subprocess records the same
73e95df implementation. These are working-tree byte hashes. The coordinator's
`P2_motor_native_raw/staged_source_identity.json` separately records normal Git
CRLF-to-LF canonicalization of new test files; it is not silent source drift or
a claim that the index bytes were separately replayed. Existing protected files
and the actual target source hashes are unaffected by that test-only distinction.

After the coordinator's approved refresh, independently verified the manifest's
same five keys and exact reviewed hash values. No allowlist expansion occurred.

## Actual target inspection

Both final compile receipts use source
`c35726f4dc0fafc87a08efc97a662c4e65937cd1847e3a7618db596040ef33ec`.
Independently staged the actual probe in a private directory and matched every
one of its 38 source-file hashes to the default target receipt; the enabled
receipt has the identical file map. Reviewed all three artifact identities per
configuration and the 33 native symbol exports, all nonzero. Artifact/receipt
hashes are preserved in `P2_motor_native_review_target_default.json` and
`P2_motor_native_review_target_match.json`.

Final default upload-format ELF: 85052 bytes,
`3e3a24128943f62784b57537b756d43b795b8445f7cafc1b74a3233f15ebe60b`;
compiler memory report 35160 bytes. Enabled compile-only ELF: 85588 bytes,
`0fbf06619b497a0125d7135559586d16b8d31dad4fccb45fe746836cd740a8f4`;
compiler memory report 35552 bytes. These figures are not physical free RAM.

Default settle assembly at 0x2e40 clears each timer's SR through three direct
stores of ~UIF at 0x2e80/0x2e88/0x2e94, then reads SR at 0x2eac within the
three-timer loop. It retains the 4096 bound and unsigned elapsed <=149 admission.
Enabled settle has the equivalent stores at 0x2eb8/0x2ec0/0x2ecc and loads at
0x2ee4. Enabled Gate transaction at 0x32d0 retains LOW -> four checked writes ->
settle -> conditional HIGH; every failure branches to its inhibit path.
Enabled native HIGH at 0x2dec checks settled/current-mask/bank before native
GPIO dispatch and checks status, ownership and raw readback afterward.

Both user setup functions only store the retained exercise address; both loops
are `bx lr`. Relocations resolve the probe's constructor calls to inert port()
and MotorGate construction, not exercise. The native translation unit's extra
initializer resolves only RouterBridge::HCI guard/RAM fields. Other inherited
Bridge, Serial and library constructors and the stock loop hook remain present;
this inspection does not qualify platform startup/runtime or Linux independence.
This reviewer performed no board connection or target execution.

## Evidence limits

Host fixtures and source/ELF inspection are software evidence. The source audits
support the chosen UIF method only under exclusive timer/pad/clock ownership.
They do not measure MCU frequency, active waveform, EN voltage, driver truth
table, silicon revision, motor behavior, deadtime or complete-tick WCET.
PINMAP, actual B4/B7 acceptance, original phase gates and a specific STAND/RING
authorization remain absent. Inherited loader/Bridge runtime paths remain
unqualified. No motor-capable image is approved for execution.

## Verdict

PASS for the exact reviewed D077 native-backend software, tests, compile probe
and five source-guard refreshes. This is not GATE P2 or permission to run motors.
Coordinator may attach this review and its receipts to the D077 software
validation; physical acceptance and future app integration remain separate work.
