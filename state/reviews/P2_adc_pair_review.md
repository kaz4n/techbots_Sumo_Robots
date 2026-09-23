# D086 optional fixed A0/A1 owner: independent review

Reviewer: separate fresh-context same-model Codex agent; not cross-model review.
Date: 2026-09-23 Asia/Dubai. Scope: raw A1 acquisition added to D078's native
ADC1 owner. Contract f194579, implementation327c5db, earlier completed QTR
baseline d483268. Only this report and P2_adc_pair_raw/ were written by the
reviewer. No implementation, test, configuration or hardware changes.

## Findings

No open BLOCKER, MAJOR or MINOR within the reviewed software scope.

## Verdict

PASS within D086 software scope. This is not a hardware result, runtime
qualification, upload authorization, decoder acceptance or human phase pass.

## Contract and implementation

Get-Date confirmed23September within PLAN section3's pre-bench schedule.
AGENTS, D051/D075/D078/D086, P2_power_contract, P2_adc_pair_contract/audit,
public power.h, actual power.cpp, HARDWARE5.6 and cached primary evidence were
read. The code-review-and-quality skill guided correctness, architecture,
bounded work and evidence review. Independent rehashing of all42 cached
manual/header/overlay/binding-receipt identities passed.

RM0456 pp1282/1287 supports enabled-idle regular rank changes; pp1354/1355
fixes SMP10, PCSEL and SQ1 fields. Installed generated DT names channel10
channel_a; the pinned overlay binds A1/index15 to PA5/channel10 and DAC1/2.
MODE2=0 remains an explicit conservative policy, not measured high impedance.
Encoded LL channel constants are not confused with integer rank9/10 fields.

The implementation preserves begin/read, Sample layout and status0..13;
NOT_ENABLED14 and ButtonSample are additive. First begin fixes the profile.
Battery-only readButtons rejects without I/O and does not acquire PA5/DAC2.
Failed initialization and either channel's fault share reset-only ownership
and no-I/O faulted reads. No second owner or retry releases the boot claim.

Pair admission checks fixed PA5 metadata, named GPIOA/B/C nonaliases, both
legacy and active QTR arrays, independent pad locks and scoped DAC2/MODE2.
PA4's original analog/no-pull configuration remains; PA5/DAC2 are never repaired
or remuxed. Setup accepts only exact tracked old/new states. Runtime changes
only SQ1 and validates the tracked previous whole SQR1; external9/10 switches
are rejected. Ignored writes permit bounded cleanup only within the narrow
transition; foreign bits produce UNCONFIRMED without blind cleanup.

Each read starts its100us budget before guards/switching, requires fresh EOC+EOS,
ADSTART0, one32-bit DR read and raw<=16383, then checks flags, ownership and time
before publication. A1 endpoints0/16383 are valid; only successful A1 conversions
advance its wrapping sequence. Invalid results publish zero raw/sequence.
The separate bounded shutdown preserves command-safe stop/disable order and
never restores rank, clears PCSEL, repairs PA5/DAC2 or resets shared hardware.

No core, app, MotorGate or established locked test changed from d483268.
The config diff adds only BUTTON_INPUT_PIN15; no B16 values changed. Original
battery assertion files remain intact; fixture additions default to their
original behavior. No new heap, delay, stock ADC call, remote motion path or
unbounded loop was introduced.

## Independent execution

P2_adc_pair_raw/pair_final/receipt.json records the reviewer's frozen WSL
checkout and exact command. All15 native unittest methods passed in122.011s:
nine original battery methods and six pair methods. Actual power.cpp compiles
against installed-shaped controlled headers with C++17, strict warnings,
no exceptions/RTTI and UBSan. This is host register-model evidence.

The210 preserved compiler/execution receipts contain208 exit0 and two required
negative-sentinel exits1. There are103 successful native executions,150 positive
native cases and1329 parent assertions. Child-local assertions are not included
in that parent count. All353 frozen files excluding the inert registry match
the live tree. The registry change exactly matches separate five-key approval.

Coverage includes ABI/profile compatibility, alternating/repeated channel
identity, every new pad/DAC/metadata guard,48 new metadata/config variants,
partial writes, shared latches, no allocation,99/100/101us boundaries at
switch/data/cleanup, initial/final guard cost, wrap/frozen clocks, poll limits,
invalid32-bit raw and seeded sequence wrap. Both actual probe macro variants
execute construction/setup and10000loops with zero native I/O/allocation.
Eight new upload combinations refuse before target/remote/transport lookup.

Root's separate normal and ASan+UBSan host receipts were inspected: both2/2
pass in6.23s/21.83s, with1173 main cases/22840417 assertions and37 enabled-Gate
cases/3796846 assertions. Those targets do not execute the native ADC MMIO
path; native ADC evidence above uses UBSan fixtures. Config17, selected unchanged
tooling25 and staged-source2 methods also pass. This does not claim every
repository tooling method was rerun.

## Actual target and inert identities

Final compile-only source:
5f2c2329d566b6940d41a3574141773f3e80378358104b3c96fb9a6e7bcb0eb0.
Actual compiler receipt exits0:83912B program,34700B compiler-reported globals.
verify_target.py independently matches all56 staged files to current bytes and
recomputes the aggregate. Three ELF hashes are recorded in target_identity_audit.
All36 native exports resolve nonzero;42 AEABI bindings match saved base-ELF
function addresses with Thumb-bit normalization. This is offline ELF evidence,
not deployed-loader proof.

The actual ELF retains beginWithButtons/read/readButtons and shared native
methods. SQ1 uses offset0x30/exact mask; DR is a32-bit read at0x40 and rejects
16384 before narrowing. Final deadline comparison accepts<=99 before publishing.

Startup disassembly and relocations show setup stores exercise's address and
loop returns. The never-called exercise retains initialization then four reads
in A0/A1/A0/A1 order. The new sketch and power translation-unit initializers
contain no calls and only inherited HCI/Bridge memory setup. Wider inherited
Bridge/loader callbacks, including __loopHook, remain outside this zero-I/O
sketch claim and retain F091. Review extracts: target_disassembly.txt,
target_symbols.txt, target_init_array.txt and startup_relocations.txt.

Only these five existing inert identities were approved/adopted. The complete
staged file maps and machine-readable approval are in inert_approval.json;
final_evidence_audit.json confirms registry equality and no additional key.

| Existing key | Approved SHA256 |
| --- | --- |
| bench/p0_adc | d11b117593a052eda1105f6f0ae309bc64af33f7d6d7b9db5e751ca069b24f50 |
| bench/p0_gpio | 88b526aef99d02135cdd05523f06723cf18acf15d4e550c79b471101ef1afdb1 |
| bench/p0_matrix | fb3bbb7c93d2baf99d61072968406479ef3ad6f8fd610e7c06e403adf8d4745c |
| bench/p0_qtr | 3db522589bad3a0984d463024403c2fb3bf166ccb3802f129a394396d7ab4d1a |
| bench/p0_timing | f4072be8ff5cc3c3d88f6329e609ec2886b0cf68e39eed9a41cd6b6b1661c57b |

## Preserved failures and corrections

The first reviewer nine-method pass predates the final shared ADRDY guard and
remains in battery_regression. Final pair_final reruns all15 on corrected source.
Implementation self-review tightened controlsOwned to require ADRDY when it owns
ADEN1. Four enabled-setup loss scenarios now prove no further writes/publication.
The earlier target compile remains initial evidence, separate from final bytes.

The new draft test forbidding all GPIO mode/pull writes was overbroad under
D078's PA4 setup. After reviewer feedback, the author checked exact preservation
of PA5/unrelated fields while retaining zero DAC/lock writes. Mixed unsigned
literal compilation, rank-readback first-status expectation and destructor-check
issues were corrected only in new tests. Failed author receipts remain; old
assertions were not weakened.

Root's two staging collection failures were invocation errors: nonexistent
module, then incompatible package import. The reviewer inspected both diagnoses
in P2_adc_pair_invocation_failure.md and the unchanged discovery rerun:2methods
pass in3.777s. Failed collections remain recorded and are not counted as passes.
No open software issue follows from those runner corrections.

## Limits and next action

The reviewer performed no board/MCU/register operation, upload, reset or motor
action. A1 settling/carryover/accuracy, SC-A START/BOTH voltage ambiguity, decoder
freshness, whole-tick800us, SC-AJ/F091 and physical/human gates remain unresolved.
IMU600us + motor150us + twoADC100us maxima total950us before QTR/core; no scheduler
or WCET success follows. Register consistency cannot prove race-free ownership.

Root can record this bounded software result and continue separately authorized
P2 work. Application scheduling, button decoding, physical measurements and
human phase acceptance remain separate.
