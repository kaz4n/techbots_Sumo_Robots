# D199 SETTLE file-only entry observation contract

26 September 2026. Prepare one new fixed wrapper at
`state/analysis/P7_motor_settle_compile_raw/inspect_static_entry.py`.
Preserve all existing code, tests, contracts, receipts and consumed owners.
This contract and its binding contain file-derived scope; they do not claim
initializer contents, instruction semantics, target execution or a successful
new entry attempt. Source implementation and independent host fixtures follow
separately; actual file-tool invocation requires their reviewed closure.

## Accepted evidence and exact inputs

D199 ABI completed its four fixed file commands, all thirteen remote closing
checks and independent local closure. The accepted actual review is PASS.
The raw readelf stdout is 158956 bytes with SHA256
`4aece135bfa9e429227e0ee17c59b54db1a1bf100fdc714de0076361f7ee1e8b`.
It contains all 27 historical entry groups, both aliases of each constructor,
the emitted local publication function and the global native SETTLE function.
No distinct symbol row for `storeSettleSample` or `settleProbeReport` occurs in
that output. This absence neither requires an accessor nor proves inlining or
correct stores. The actual publication path remains for instruction review.

The fixed D198 source SHA256 is
`117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`.

| Repository-relative input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_settle_compile_raw/inspect_static_abi.py | 16106 | 0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea |
| state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py | 10317 | cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/result.json | 905572 | 230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/abi.json | 5410 | 069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/local_result.json | 275 | eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9 |
| state/reviews/P7_motor_settle_abi_actual_review.md | 7312 | a7c3993ab5e0d008b4464bf93f89b5877447992fa8e3197d8c869812e11f874f |
| state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json | 9648 | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 |
| state/analysis/P7_motor_settle_compile_raw/entry_binding01.json | 20870 | 6234676242fdd7e61136fd2a1f66fabb0242b10ee597ef2bf6555a9444ecfd2b |

These eight inputs form the new wrapper's fixed ORIGINALS set. Verify their
exact lengths and hashes plus this contract's final SHA256 before any private
source execution. Preserve every inherited D199/D194/D193/D188 source, contract,
artifact, tool, boot and failure pin. Bind new wrapper bytes through SELF and
reviewed HEAD rather than a recursive self hash. The fixed build remains
`/home/arduino/sumox26_codex_build/app-motor-settle-static01` on boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. No other ELF can be selected.

`entry_binding01.json` is the fixed evidence companion. Its input pins,
readelf hash, sections, 29 ranges, all symbol aliases, initialization bounds,
report object and projection tables are normative. JSON string escapes encode
the actual substitution bytes, including newline characters. It is not a
runtime selector, permission record or proof of a future observation.

## Public interface, bootstrap and private composition

Expose `project_reader(raw)`, `project_parser(raw)`,
`load_reader(*, root=ROOT)` and `main(argv)`. Projectors accept exact `bytes`,
check their input identities, perform only the ordered count-checked
substitutions below and check their final identities. They perform no I/O and
do not mutate inputs. ROOT is the repository inferred from the wrapper path.

Import defines constants/functions only: no input reads, subprocesses, device
calls, owner creation or sys.modules registration. Preserve existing read-only
module-location path calculation. Before input reading, main requires an exact
list containing exact strings matching exactly
`--check-only|--execute --reviewed-head <40 lowercase hexadecimal characters>`
and requires Python `-B`. No alternate profile, target, owner, source, address,
range, symbol or type CLI is introduced. Main delegates exactly once to the
loaded reader's unchanged main.

Copy exactly the source bodies of the accepted D199 ABI wrapper's five helpers
`require`, `_stamp`, `_plain_chain`, `_read_handle` and `pinned`. Preserve full
ancestry checks, plain regular single-link files, reparse refusal,
O_NOFOLLOW/O_NONBLOCK where supported, bounded bytes, pre-read descriptor
identity, same-API before/after stability, final digest, descriptor/stream
closure and preservation of the primary error. Keep the precise Windows
pathname/handle executable-extension 0111 exception and existing cross-API
ctime exception; do not mask arbitrary mode bits or weaken non-Windows checks.
No transport or attempt lifecycle is copied into the new wrapper.

`load_reader` obtains checked snapshots of all eight fixed inputs and checks
this contract before executing any private source. Use fresh ModuleType
namespaces, their original absolute __file__ paths and private module names,
never __main__ or sys.modules. Execute the unchanged D199 ABI wrapper in one
such namespace. Save its project_reader, replace it privately by composition
that first calls that saved projector and then this contract's project_reader,
and invoke its unchanged load_reader(root=root). All nested original loaders,
bootstrap checks and source identities remain active.

Project the checked historical entry source into a separate private namespace.
Never call that historical module's load or main. Copy the returned reader's
HARD_PINS and extend it with all eight inputs and this contract hash; preserve
all inherited entries. Replace reader.queries directly with the projected entry
module's queries, and reader.summarize directly with that module's summarize.
Do not wrap or invoke the inherited ABI summary: entry packets intentionally do
not contain ABI/polls/SETTLE-field query tags. The old ABI query/summary functions
may remain unused definitions. Keep every other reader class/function body and
attempt behavior unchanged. No shared globals or original modules are patched.

## Exact reader projection

The input is the D199 ABI projected reader, after its original projector:
17061 bytes, SHA256
`67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6`.
Apply these nine byte substitutions in the listed order. Quotes shown are
literal source characters.

| Old | New | Count |
|---|---|---:|
| `'/inspect_static_abi.py'` | `'/inspect_static_entry.py'` | 1 |
| `'native_abi_static01'` | `'native_entry_static01'` | 1 |
| `app-motor-settle-abi-static01` | `app-motor-settle-entry-static01` | 1 |
| `D199_STATIC_FILE_ONLY_ABI` | `D199_STATIC_FILE_ONLY_ENTRY` | 2 |
| `STATIC_ABI_CHECKED` | `STATIC_ENTRY_CHECKED` | 1 |
| `STATIC_ABI_OBSERVED` | `STATIC_ENTRY_OBSERVED` | 2 |
| `'file-abi'` | `'file-entry'` | 1 |
| `'abi.json'` | `'entry.json'` | 1 |
| `StaticAbi` | `StaticEntry` | 2 |

Require final 17085 bytes and SHA256
`db4122376e7ef2da92ca49633b01248514274744b429ad54bede8d0c8d8da9f8`.
This changes only entry ownership, SELF and receipt labels. It preserves the
D198 compile artifact/source identities and the complete file-only lifecycle.

## Exact historical entry parser projection

The input is exactly the 10317-byte historical entry source with SHA256
`cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34`.
Apply exactly 36 ordered substitutions: the build path, Runner namespace,
32 address literals in descending old-address order, the fixed two-range
append and the local-publication classification. The descending order avoids
replacement collisions. No address arithmetic, generic selection, scanning for
new ranges, fallback source or alternate parser is permitted.

The first 34 substitutions are:

| Old | New | Count |
|---|---|---:|
| `/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino` | `/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino` | 1 |
| `15app_motor_fault` | `17app_motor_observe` | 6 |
| `0x0811621c` | `0x081162dc` | 1 |
| `0x08116218` | `0x081162d8` | 4 |
| `0x081160e0` | `0x081161a0` | 1 |
| `0x08116074` | `0x08116134` | 2 |
| `0x08116048` | `0x08116108` | 1 |
| `0x08116046` | `0x08116106` | 1 |
| `0x08116044` | `0x08116104` | 1 |
| `0x08116036` | `0x081160f6` | 1 |
| `0x0811602c` | `0x081160ec` | 1 |
| `0x08115f7c` | `0x0811603c` | 1 |
| `0x08115f74` | `0x08116034` | 2 |
| `0x08115f6c` | `0x0811602c` | 1 |
| `0x08115cfc` | `0x08115dbc` | 1 |
| `0x08115c7c` | `0x08115d3c` | 2 |
| `0x08115bec` | `0x08115cac` | 1 |
| `0x08113290` | `0x08113350` | 1 |
| `0x0811326c` | `0x0811332c` | 1 |
| `0x08110f64` | `0x08110fc0` | 1 |
| `0x08110ed8` | `0x08110f34` | 1 |
| `0x08110d10` | `0x08110d30` | 1 |
| `0x08110cd8` | `0x08110cf8` | 2 |
| `0x08110c70` | `0x08110c90` | 1 |
| `0x08110bfe` | `0x08110c1e` | 1 |
| `0x08110bfc` | `0x08110c1c` | 1 |
| `0x0810c774` | `0x0810c794` | 1 |
| `0x0810c760` | `0x0810c780` | 1 |
| `0x08103d78` | `0x08103d98` | 1 |
| `0x08103d24` | `0x08103d3c` | 2 |
| `0x08103c94` | `0x08103cac` | 2 |
| `0x08103c08` | `0x08103c20` | 2 |
| `0x08103bb0` | `0x08103bb4` | 2 |
| `0x08103b58` | `0x08103b5c` | 2 |

Substitution 35 replaces the following unique tail once. The closing parenthesis
is included; neither replacement operand includes a newline after it.

```python
    ('start_static_threads', 0x08116134, 0x081161a0, ('_Z20start_static_threadsv',)),
)
```

with:

```python
    ('start_static_threads', 0x08116134, 0x081161a0, ('_Z20start_static_threadsv',)),
    ('publish_settle', 0x08110d60, 0x08110d9c,
        ('_ZN6motors12_GLOBAL__N_113publishSettleENS_17SettleProbeReasonEjjhh',)),
    ('motor_settle', 0x081115bc, 0x081116e0, ('_ZN6motors8UnoQPort6settleEPv',)),
)
```

The newline separating each closing parenthesis from its Markdown fence is
formatting only; the pinned binding gives the exact operand bytes.

Substitution 36 replaces the following literal once:

```python
('global_initializer', 'candidate_rate', 'candidate_period')
```

with:

```python
('global_initializer', 'candidate_rate', 'candidate_period', 'publish_settle')
```

Require final 10562 bytes and SHA256
`7f96678955bc37082766f3b02b46b1cdbba832624815b1ba4266a549d3e372f2`.
Apart from these fixed query metadata and local-binding additions, parser logic
is unchanged. Do not write projected sources back to any historical file.
Unused historical loader constants/functions remain definitions only.

## Fixed observations and file queries

Retain exactly four child commands: pinned readelf --version; pinned gdb
--version; readelf `-hSWs -x .init_array` on the fixed D198 observer ELF; and the
existing guarded GDB helper on its corresponding debug ELF. Preserve no-init,
no-auto-load, batch, C++ language and no-function-call settings. GDB receives
59 expressions: marker plus `disassemble /r` for each of the 29 groups below,
then SUMOX_ENTRY_END. Echo suffixes are literal backslash+n bytes, not embedded
newline characters. Markers are SUMOX_ENTRY_00 through SUMOX_ENTRY_28 and END.

The first 27 labels and their order are historical; append publish_settle and
motor_settle. Addresses below have the Thumb bit cleared. Each accepted FUNC
symbol value is start|1 and size is end-start. All aliases in the binding are
mandatory, including both C1/C2 aliases for Runner and motor_fault::Trace.
Only Runner uses the app_motor_observe namespace.

| Label | Start | End (exclusive) | Bytes | Binding | Aliases |
|---|---:|---:|---:|---|---:|
| entry_point | 0x08100010 | 0x081000c8 | 184 | GLOBAL | 1 |
| setup | 0x081000c8 | 0x081000e8 | 32 | GLOBAL | 1 |
| loop | 0x081000e8 | 0x08100104 | 28 | GLOBAL | 1 |
| global_initializer | 0x08100104 | 0x08100298 | 404 | LOCAL | 1 |
| app_dump_port | 0x081002a8 | 0x081002d0 | 40 | GLOBAL | 1 |
| sources_port | 0x081003e0 | 0x0810045c | 124 | GLOBAL | 1 |
| sources_adc_port | 0x0810045c | 0x08100470 | 20 | GLOBAL | 1 |
| runner_constructor | 0x08103984 | 0x08103b5c | 472 | GLOBAL | 2 |
| runner_application_valid | 0x08103b5c | 0x08103bb4 | 88 | GLOBAL | 1 |
| runner_stop_reason | 0x08103bb4 | 0x08103c20 | 108 | GLOBAL | 1 |
| runner_freeze | 0x08103c20 | 0x08103cac | 140 | GLOBAL | 1 |
| runner_begin | 0x08103cac | 0x08103d3c | 144 | GLOBAL | 1 |
| runner_poll | 0x08103d3c | 0x08103d98 | 92 | GLOBAL | 1 |
| dump_port | 0x0810c780 | 0x0810c794 | 20 | GLOBAL | 1 |
| loop_hook | 0x08110c1c | 0x08110c1e | 2 | GLOBAL | 1 |
| candidate_rate | 0x08110c90 | 0x08110cf8 | 104 | LOCAL | 1 |
| candidate_period | 0x08110cf8 | 0x08110d30 | 56 | LOCAL | 1 |
| motor_port | 0x08110f34 | 0x08110fc0 | 140 | GLOBAL | 1 |
| power_reader_port | 0x0811332c | 0x08113350 | 36 | GLOBAL | 1 |
| trace_constructor | 0x08115cac | 0x08115d3c | 144 | GLOBAL | 2 |
| trace_port | 0x08115d3c | 0x08115dbc | 128 | GLOBAL | 1 |
| memcpy | 0x0811602c | 0x08116034 | 8 | GLOBAL | 1 |
| memset | 0x08116034 | 0x0811603c | 8 | GLOBAL | 1 |
| unsigned_divide | 0x081160ec | 0x081160f6 | 10 | GLOBAL | 1 |
| init_variant | 0x08116104 | 0x08116106 | 2 | WEAK | 1 |
| main | 0x08116108 | 0x08116134 | 44 | WEAK | 1 |
| start_static_threads | 0x08116134 | 0x081161a0 | 108 | GLOBAL | 1 |
| publish_settle | 0x08110d60 | 0x08110d9c | 60 | LOCAL | 1 |
| motor_settle | 0x081115bc | 0x081116e0 | 292 | GLOBAL | 1 |

All 31 function symbol tuples are FUNC/DEFAULT/section1 with the binding above.
The two added exact symbols are:

- `_ZN6motors12_GLOBAL__N_113publishSettleENS_17SettleProbeReasonEjjhh`,
  LOCAL value0x08110d61/60 bytes;
- `_ZN6motors8UnoQPort6settleEPv`, GLOBAL value0x081115bd/292 bytes.

The checked .text is section1, address0x08100010, size0x162c8, AX, alignment8.
The checked .init_array is section2, address0x081162d8, size4, WA, alignment4.
__init_array_end is0x081162dc; __init_array_start, __preinit_array_start/end and
__static_thread_data_list_start/end are0x081162d8. Preserve exact original
NOTYPE/zero-size/DEFAULT/section2 tuples: thread bounds GLOBAL, other bounds
LOCAL. The initializer FUNC symbol remains0x08100105.

The accepted ABI did not dump .init_array contents. This entry attempt must
observe its one little-endian word at0x081162d8 and confirm0x08100105; this is
an acceptance requirement, not an already measured value. Preserve decimal/0x
readelf size parsing, exact unique symbol tuples and .text containment. Retain
initialization section/bytes/bounds checks, exact ordered marker sequence,
range headers/end markers, recognized opcode widths, no unparsed address rows,
contiguous instruction coverage and raw block hashes. Preserve original raw
receipt bytes. Do not relax malformed, missing, duplicate or reordered evidence
to obtain acceptance.

The separate report was observed at0x2003d3e8 for28 bytes, LOCAL OBJECT DEFAULT
section5, exact name `_ZN6motors12_GLOBAL__N_119settle_probe_reportE`. The pinned
ABI establishes its layout and bounds in checked zero-BSS separately from
Runner. The unchanged entry parser does not re-parse that object or invent new
SETTLE summary fields. Its output remains STATIC_ENTRY_OBSERVED with
initialization, disassembly and the inherited file-only/semantic-review-pending
limitation. Review the actual publication and SETTLE instruction blocks against
this accepted report layout after successful file observation.

That separate semantic review must assess actual stores to current, flags and
first_failure; preservation of the first failure across later outcomes; use of
the fixed report address; retained native condition/call ordering and bounded
paths; plus existing entry wiring, constructors, inert grants, poll bounds,
stop priority and terminal passivity. Symbol presence and parser success alone
prove none of those semantics. No accessor/store helper symbol is required.
No success claim is assigned in advance if emitted code is ambiguous.

## Attempt boundaries and independent validation

The exclusive new local owner is
`state/analysis/P7_motor_settle_compile_raw/native_entry_static01`.
Required absent remote scope is
`/home/arduino/sumox26_codex_build/app-motor-settle-entry-static01`.
The inherited file-only reader checks but does not create that remote scope.
Neither absence has been claimed by this contract. Preserve all historical and
consumed ABI/entry/build owners. The actual ELF paths remain beneath the fixed
D198 app-motor-settle-static01 build owner.

Use STATIC_ENTRY_CHECKED for check-only and STATIC_ENTRY_OBSERVED for successful
observation, raw scope D199_STATIC_FILE_ONLY_ENTRY, operation file-entry and
summary entry.json. Keep four children,60s per child/5s reap/1MiB stream bounds,
400s transport,30000 UTF16 command units,128MiB local free-space guard, clean
reviewed HEAD, source/artifact/tool/boot checks, thirteen remote closing checks
and independent local closure. Save original command/receipt bytes before
summary parsing. Empty stderr, return-code checks and bounded closure remain
mandatory. Preserve first failure, failed-owner consumption and every receipt.

There is no compile, upload, reset, target connect/run/call, MCU read, motor
run, sudo, credential change, firmware/configuration edit or arbitrary-range
facility in this task. Runtime cause, capture coherence, live RAM, WCET,
physical acceptance, motor permission and human phase gates remain separate.

Before reading the new implementation, freeze an independent oracle derived
from this contract, its checked binding and the unchanged historical entry
fixtures/public interfaces. Retain all old sources and assertions. Reuse
applicable historical 19-method behavior through narrowly checked metadata and
packet fixtures; exact old projection identities remain historical evidence
unless explicitly replaced with independent new-identity checks. Record every
selected method/adaptation rather than claiming incompatible historical
metadata bodies validate the new target unchanged.

Cover passive import and invalid CLI; exact bootstrap body equality; bounded
input type/length/hash failures and every required substitution count; both
fixed projected identities; all input checks before private execution; saved
original-first composition and fresh namespaces; no sys.modules or historical
load/main; inherited pins/new SELF/new owners; exact four commands,59
expressions and29 fixed groups; direct entry query/summary replacement without
ABI tags; complete synthetic packets and decimal/hex sizes; missing/duplicate/
wrong aliases, local publisher/global SETTLE binding, type/section/Thumb/range;
initializer bytes/pointer/bounds; missing/reordered/duplicate markers, malformed
opcode rows, gaps/overlap and final coverage; raw preservation; real prepare,
check-only/execute delegation, failed owner and closing behavior. Keep all
historical failures. Freeze new source/host review before actual admission;
run Linux and Windows host checks serially and preserve their first results.

This contract and binding were prepared by read-only artifact parsing,
count-checked byte transformations and AST/data inspection only. No new wrapper,
test body, native file-tool child, firmware operation or device action was
executed during their preparation.
