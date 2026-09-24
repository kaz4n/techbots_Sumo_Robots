# D135 completed host and native receipt review

2026-09-24. Same independent reviewer; read-only local inspection and SHA256
verification only. No compiler, test, board, network or motor action here.

All 656 current inputs match `P5_abort_timing_raw/freeze.json`; all 42 existing
protected tests match `initial_protected.json`. Reviewed production paths have
no diff against `2d924f1f`. The corrected private source/runner match the exact
hashes frozen after the approved one-case correction in `94a7bb5d`.

| Root receipt | Reviewed terminal outcome |
|---|---|
| `full_retry2` | All 20 CTest targets PASS; P5 public 40/40 and private 13/13 per M0/M1 |
| `configured_first` | Public 42/42 and private 13/13 per M0/M1 PASS |
| `sanitizer_first` | ASan/UBSan public 40/40 and private 13/13 per M0/M1 PASS |
| `configured_sanitizer_first` | ASan/UBSan public 42/42 and private 13/13 per M0/M1 PASS |

Each root receipt has exit zero for configure/build/CTest/private runner, a
matching retained log hash, post-run input verification and released scratch.
Each private receipt binds the current source and runner, excludes exactly six
public test objects, retains 45 objects including genuine motor_gate_main and
the production owner, and records six successful compile/link/run commands.
Configured flags and sanitizer flags agree with the corresponding receipt.
Private logs retain 725533 M0 / 725543 M1 assertions and zero failures; public
LastTest logs retain the expected 40/42 cases with zero skipped or failed cases.
The copied ADC windows are synthetic and do not qualify physical A1 decoding.

The native index's 44 local artifacts and report rehash without mismatch, as do
all 134 current files in its working-source manifest. Actual remote command
records show one compiler invocation, exact exclusive P5/M0/MATCH0 flags,
`--jobs 1`, default UNO Q FQBN and no upload. The separate properties query is
not a second compiler invocation. This reviewer performed no remote operation.

Checked ELF `9583f94d7f7595639ef84a39822e19ed7c2110e1d2e65770b10f4986319e1a41`
contains the real opener/trace functions and a 166424-byte Runtime symbol.
The retained model's copied chunks plus metadata independently sum to 260816,
leaving a conditional 1328-byte span in its 262144-byte pristine pool. All 61
relocation-used imports have nonzero exports in the checked packaged loader.
The source/report correctly distinguishes that file from the flashed loader.

Offline DWARF directly confirms Pending 88 bytes with the tag at offset85,
Tick 200 with transient token at184, Robot 2680, RobotInput 200 and Runtime
166424. The single trace phase has seven bytes of following alignment padding;
the read-window growth partly occupies former input padding. No second persistent
trace token/timestamp owner or new recorder capacity was concealed by the sizes.
The report includes the two persistent result copies and input/result by-value
operations without incorrectly summing them into a measured stack peak.

Native compile/policy and conditional model fit PASS only for this inert wrapper.
It omits the default app's native DumpPort transport owner; its fit does not repair
the separately measured default-app 32-byte deficit. Live loading/free RAM/stack,
800us WCET, source/clock qualification, extraction and physical 10/10 trials
remain unproved. No motor-run authorization, hardware acceptance or gate follows.

Disposition: no material finding in these completed receipts. Final D135 software
review remains pending the remaining tooling, default/P4 layout and eight copied
implementation mutation results; this note does not mark those checks passed.
