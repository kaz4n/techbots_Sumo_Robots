# D209 ordinary static ABI actual-result review

26 September 2026, Asia/Dubai. Reviewer `const_cleanup_review`; a separate
actual-result decision by the same-model reviewer, reusing the completed
preparation/source/host/admission context. Only this new review is owned.
Review used saved bytes, strict JSON, source/AST, literal reconstruction,
arithmetic, hashes and read-only Git. No subject import, test, native tool,
device call, compiler or cleanup was performed by this reviewer.

**FINAL ACTUAL PASS. No open material finding.** The single admitted file-only
observation and its closure are accepted. Fresh ABI coordinates and the complete
symbol inventory are available for a separately prepared instruction-binding
contract. This does not admit another native attempt or establish runtime
contents, coherent collection, ordinary loading or physical behavior.

## Exact evidence and provenance

Paths below are relative to
`state/analysis/P7_ordinary_app_static_compile_raw/`.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `native_abi_static01_invocation.json` | 1266 | `fe042f03669896b76464fb5209fb3d5ec66d62e31a0efceea923929a0016e0d0` |
| `native_abi_static01/inputs.json` | 28377 | `3ab0a217e49ffe1508d60f2f8c871eff010dad124c1dc2fdcc27741b32cc6105` |
| `native_abi_static01/result.json` | 581671 | `6a17c12cb24396bf9a58a883ea295ec51feff2abe68d826983f363b3bcbb6d3b` |
| `native_abi_static01/abi.json` | 274942 | `e224750ea11a9bd462c1708e2d797b622e9fee56e3e46e479242bff19eefdbf4` |
| `native_abi_static01/local_result.json` | 275 | `9c78721cfaa7330cc523619c31ad207832ffe6f9ca3abcc9e93bec7743212cf0` |
| `native_abi_static01/0001-file-abi/stdout` | 577792 | `49c21918748d86819ba0da6dd3c0ecc5acfde2d85f08963c94d01488f578b4da` |
| `abi_native_closing01.json` | 4273 | `c850145363dc027a95fc64ecea7aed42d1deaf243e1e71a2294897fa1f217f3b` |

The native reviewed HEAD is
`326931f49fb0512372a8638958acd8093754e227`. Saved invocation check-only returned
zero in 0.5400269 seconds; execute returned zero in 2.1873995 seconds. Their
nested outputs agree exactly with saved inputs/local closure. The inherited
clean-HEAD admission and local closing check passed. Independently compared
all 159 coordinator pins, ten scope pins and 133 runtime-local pins against
current files and this commit's exact blobs: all 162 distinct paths match,
including overlapping identities. No source, oracle or admission drift exists.

The admitted scope remains 3318 bytes/e34576f4; reader 44449 bytes/f816a523;
source/host review 8934 bytes/f3e72aca; admission review 6585 bytes/bd83b5ce.
The ordinary source remains
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`,
static `app.ino`, MATCH0/MOTORS_ALLOWED0, probe0 and all seventeen setup grants
zero. Actual build bindings remain D208's `ordinary-app-static01`, including
its checked raw/debug ELF, seven artifact identities plus export, loader and
TLS source. No artifact binary was newly retrieved for a local ELF execution.

## Actual transport and complete closure

Strictly parsed saved JSON with duplicate-key/nonfinite refusal and reconciled
the transport stdout object with `result.json`. Intent and transport result
have the same exact argv/bounds; result adds returncode0. The selected ADB
serial is 2629958581. The command is an isolated Python file observer under the
fixed minimal environment, with one transport and 6001 UTF-16 command units
against 30000. Transport timeout remains 400 seconds; response is below 8MiB;
transport stderr is empty.

Decoded the compressed program as data and independently assembled its entire
17529 bytes from reviewed literal metadata, identity preamble, exact retained
wait/reap definitions, current ordered pins/commands and inherited remote
reader body with its sole D209 scope substitution. The complete bytes match
SHA-256 `ef1df2a1fa9517110dc05b4030d3f48447fd69216d16db84d4740aeb6c8ab0b7`.
No transported program was executed by the reviewer.

The resulting identity is UID1000/arduino, expected boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, fixed CLI digest, conflicts [] and
13892366336 reported free bytes. The exact program refuses the previously
absent `ordinary-app-abi-static01` scope before file children. All twelve
remote hashes correspond exactly to eight accepted artifacts, readelf, GDB,
loader and TLS source. Remote checks retain before/after identity comparison;
the receipt reports all twelve closing files followed by board_identity PASS
in their prescribed order. It does not separately serialize those stamps.

| Child | Stdout bytes | Elapsed seconds |
|---|---:|---:|
| readelf version | 283 | 0.011723 |
| GDB version | 281 | 0.073275 |
| raw ELF `readelf -hSWs` | 153800 | 0.029921 |
| debug ELF guarded GDB | 269625 | 0.338941 |

All four exact argv vectors match the frozen ordinary query table. Each record
has deadline60s/reap5s, returncode0, timed_out=false, reaped=true, sequential
start/finish order and empty stderr. Every base64 stream is canonical, has its
declared length and stays within 1MiB. Child outputs identify GNU readelf
2.43.1 and GDB16.2 from Zephyr SDK1.0.1. GDB retains no auto-load/function calls;
there is no attach, inferior run or MCU-memory operation.

Remote status is OBSERVED, local and ABI statuses STATIC_ABI_OBSERVED, with
null first errors. Local closure records one transport and its required PASS.
The closing receipt's four stream hashes, elapsed differences, local result
and complete eight-file census independently match: 1475298 logical bytes.
Root records 6489399296 local free bytes. Root's first local audit used an
absent elapsed_seconds key; its documented corrected difference of started/
finished matches raw records. No native or test rerun, source change or raw
evidence repair followed that audit-only correction.

## Independent ABI reconciliation

All 92 ordered markers match the frozen list, without prefix/trailing answer
substitution. All 79 numeric answers reconcile independently: thirteen sizes,
thirteen alignments, six offsets and 47 enum values. All thirteen retained
layout strings equal their raw GDB blocks byte for byte. `ordinary_abi_scope`
also reviewed their direct member order against current source and checked
nested window arithmetic, without execution or edits; no discrepancy arose.

| Type | Bytes | Alignment |
|---|---:|---:|
| app::Runtime | 166376 | 8 |
| app::RuntimeReport | 600 | 8 |
| app::Transaction | 162544 | 8 |
| app::TransactionReport | 504 | 8 |
| motors::MotorGate | 88 | 8 |
| motors::UnoQPort | 40 | 4 |
| motors::Result | 56 | 8 |
| motors::HaltResult | 16 | 4 |
| fsm::RobotResult | 400 | 8 |
| fsm::PreviousTick | 48 | 8 |
| core::Outputs | 12 | 4 |
| app::SetupGrants | 21 | 1 |
| bool | 1 | 1 |

Independently checked every enum name/value against its actual current C++
declaration, adopted derivation, raw GDB number and summary: RuntimePhase5,
RuntimeFault6, Phase5, app::Fault7, motors::Fault7, core::State12 and
edge::EscapeFault5. Values follow the declared zero-based member order.
The complete `.symtab` has 2234 rows numbered 0 through 2233, including the
empty-name row; selected-symbol inspection did not discard the other rows.

The raw ELF is ARM ELF32 little-endian. Its section5 `.bss` starts at
536951136 (0x20013960), section size167584; the accepted initialized-zero range
is [536951136,537118408), size167272. These are distinct bounds. Both selected
unique LOCAL/DEFAULT/OBJECT symbols occupy section5 and fit wholly inside
the narrower initialized range with the observed alignment:

- `_ZN12_GLOBAL__N_17runtimeE`: 536951136 (0x20013960), 166376 bytes,
  alignment8; raw symbol size `0x289e8` agrees with GDB.
- `_ZN12_GLOBAL__N_110motor_portE`: 537117512 (0x2003c348), 40 bytes,
  alignment4.

Runtime's exclusive end equals motor_port's start, so they do not overlap.
The three exact forbidden diagnostic/SETTLE symbols are absent from the
complete table. This is not a generalized claim that other code was removed.

| Runtime member | Root-relative offset | Bytes | Absolute address |
|---|---:|---:|---:|
| transaction_.gate_ | 200 | 88 | 536951336 |
| transaction_.report_ | 162128 | 504 | 537113264 |
| transaction_.previous_ | 162632 | 48 | 537113768 |
| grants_ | 164640 | 21 | 537115776 |
| report_ | 164664 | 600 | 537115800 |
| attempted_ | 166218 | 1 | 537117354 |

Each address equals the fresh Runtime base plus its queried offset, has the
type's alignment and lies wholly within Runtime; the six windows are pairwise
nonoverlapping. Source/layout cross-check independently finds transaction_
at Runtime+152, with nested gate48/report161976/previous162480, yielding the
three corresponding root-relative offsets above. The other three offsets
agree with the raw Runtime member rows. Full layout text preserves additional
members and padding, including the MATCH0 calibration tail; this stage does
not constitute a decoder for every nested scalar.

The current actual-validation interpretation is consistent with these facts;
its adoption-status sentence is intentionally mutable and is not a review
input pin. Saved ABI data establishes file layout and symbols only. Ordinary
Runtime continues updating, FAULT can precede cleanup completion, and no
terminal/frozen snapshot or final-inhibition semantics are supplied. D207
remains the latest verified flashed image. No ordinary runtime, live RAM,
timing/WCET, atomic coherence, pin measurement, physical acceptance, motor
permission or human phase gate follows. The attempt is consumed; evidence
and prior failures remain retained. This review is sealed after byte/hash
reporting, and reviewer writes stop.
