# D210 ordinary application file-only entry inspection

26 September 2026. Proposed engineering scope under D051, following accepted
D208 ordinary static compilation and D209 static ABI observation. This contract
and its data-only binding require independent preparation review and adoption
before root creates the new wrapper. They do not authorize an unreviewed native
attempt. No executable, test, compiler, transport or device action was performed
while preparing these two documents.

## Evidence and intended boundary

D209 actual review `585be669385e1ca85ddd188d3eeda5fdf11cfc3392eea614370d9bfabbcc4b6a`
is accepted at commit83a4eb3c13960190bd3a4fd69f2c93b2e0df0c25. The reviewed raw
result, ordinary ABI summary, local closure and D208 artifact packet are fixed
below. The image is source
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`,
`app.ino`, FQBN `arduino:zephyr:unoq:link_mode=static`, default startup,
`-DMATCH=0 -DMOTORS_ALLOWED=0`, probe0, with all seventeen checked-in setup
flags zero. No source, configuration, bound, grant or motor permission changes.
The fixed build owner is `/home/arduino/sumox26_codex_build/ordinary-app-static01`.
Existing identity bindings remain boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8,
serial2629958581 and Arduino UID1000, subject to inherited use-time verification.

This task observes selected file instructions for startup, ordinary object/port
binding, construction, zero-grant setup, continuous dispatch/completion and
inhibited motor cleanup. It is not a closed call-graph proof. The ordinary
application has no diagnostic Runner, Trace or SETTLE probe report. The selected
native `UnoQPort::settle` implementation remains in scope; no probe report or
ABI/polls query is added. A finite host file query does not terminate firmware,
freeze a snapshot or manufacture a final-inhibition receipt. No ordinary image
is loaded or flashed by this task; D207 remains the latest accepted flashed image.

## Fixed inputs and data provenance

New subject: `state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_entry.py`.
The eight `ORIGINALS` entries must be checked in this order, with exact byte
counts and SHA-256, followed by this complete contract's SHA-256, before any
private source execution:

| Key | Repository-relative input | Bytes | SHA-256 |
|---|---|---:|---|
| ABI | state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_abi.py | 44449 | f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d |
| ABI_CLOSURE | state/analysis/P7_ordinary_app_static_compile_raw/native_abi_static01/local_result.json | 275 | 9c78721cfaa7330cc523619c31ad207832ffe6f9ca3abcc9e93bec7743212cf0 |
| ABI_LAYOUT | state/analysis/P7_ordinary_app_static_compile_raw/native_abi_static01/abi.json | 274942 | e224750ea11a9bd462c1708e2d797b622e9fee56e3e46e479242bff19eefdbf4 |
| ABI_RESULT | state/analysis/P7_ordinary_app_static_compile_raw/native_abi_static01/result.json | 581671 | 6a17c12cb24396bf9a58a883ea295ec51feff2abe68d826983f363b3bcbb6d3b |
| ABI_REVIEW | state/reviews/P7_ordinary_app_abi_actual_review.md | 9627 | 585be669385e1ca85ddd188d3eeda5fdf11cfc3392eea614370d9bfabbcc4b6a |
| ARTIFACTS | state/analysis/P7_ordinary_app_static_compile_raw/native_static01/artifacts.json | 9281 | 275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0 |
| PARSER | state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py | 10317 | cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34 |
| BINDING | state/analysis/P7_ordinary_app_static_compile_raw/entry_binding01.json | 106792 | 24de4c183fb7478d71cffdbcb2bf1933759c496ee61a79957c05e3cdf89c6420 |

`SELF` is bound through clean reviewed HEAD and inherited local pinning; do not
create a recursive self hash. The binding has no hash of this contract or of
itself. Its `18` preparation input pins and
`23` relevant source-file pins supplement the runtime
input set without introducing runtime selectors. It records the exact old/new
projection operands, every intermediate identity, selected full symbol rows,
source references/rationales and artifact identities. JSON escapes encode exact
ASCII/LF operands; the binding is data, never an executable or permission token.

The complete saved readelf stdout is 153800 bytes,
SHA-256 `24dc0cdd68e9f395f979246a90d5a994a6b5244864a286559dbbb0731ea36181`. Its single `.symtab` declares
2234 entries; all rows0 through2233 were consumed before selection, without
filtering by type, binding or visibility. Every selected alias has one exact
FUNC/DEFAULT/section1 row. Constructor C1/C2 aliases agree in value, size and
all classifications. No next-symbol rounding, address delta, substring-selected
clone, guessed range or runtime-selectable symbol is permitted. Full current
source manifest125 pins were checked during preparation; inherited ordinary
compiler admission must recheck its exact source hash/mapping and artifacts.

## Exact wrapper construction

Use the accepted D205 wrapper as the source algorithm:
`state/analysis/P7_motor_const_compile_raw/inspect_static_entry.py`,
14941 bytes / `a71eb62496ddedcc4d295579cea383635f309c8394dfd6c9ee32913a7418d835`.
Its contract6663d1ea and historical evidence remain unchanged. The new direct
entry composition uses accepted D209 ordinary ABI loading, not D204's diagnostic
ABI chain.

Let C be the lowercase SHA-256 of this complete final contract and B be the
final binding identity already listed above. Root must record the exact
prospective wrapper bytes/hash and each construction intermediate in a separate
metadata receipt before independent oracle FINAL or any subject execution.
This contract does not invent a future wrapper identity. No placeholder or
unchecked projection may remain in executable source.

Perform exactly thirteen ordered, one-occurrence replacements over the pinned
predecessor. Complete assignment operands extend from the first source byte of
the single top-level assignment through its final expression byte, excluding
the following LF. AST/literal extraction during construction is data only; no
new runtime AST evaluator or parser framework is introduced.

| Step | Old operand | New operand |
|---:|---|---|
| 1 | complete first three comment lines, including their LFs | the three exact comment lines below |
| 2 | P7_motor_const_compile_raw/ | P7_ordinary_app_static_compile_raw/ |
| 3 | P7_motor_const_abi_actual_review.md | P7_ordinary_app_abi_actual_review.md |
| 4 | P7_motor_const_entry_contract.md | P7_ordinary_app_entry_contract.md |
| 5 | 6663d1ea7309c809d8f727fc5bf68291128e54c83ca64b7d1ce53b9ff1cea9d9 | C |
| 6 | complete ORIGINALS assignment | ordered eight-entry table above |
| 7 | complete READER_INPUT assignment | (12965, '7fb42d51a3f42f99c7e7890b4f4c1dc90360c2d84c09d3bbde7ccea4d1138aea') |
| 8 | complete READER_PROJECTED assignment | (12987, '331f10914c77f1ece7255262db0d2f0c6472d31f86e680e6ec23c39c4b682b45') |
| 9 | complete PARSER_PROJECTED assignment | (14259, 'a71d5c172b65952ab010441bfd894f2552e08bf2a66c19adf0eed29c381a6e05') |
| 10 | complete READER_REPLACEMENTS assignment | binding projection.reader.steps |
| 11 | complete PARSER_REPLACEMENTS assignment | binding projection.parser.steps |
| 12 | _sumox_d205_entry_abi | _sumox_d210_entry_abi |
| 13 | _sumox_d205_entry_parser | _sumox_d210_entry_parser |

Exact replacement comments, with LF after each line:

```text
# Observes fixed ordinary-app entry and inhibited motor instructions from checked files.
# Preserves ordinary ABI evidence and the reviewed single-attempt file-only lifecycle.
# Independent entry fixtures verify metadata projections, parsing, guards and closure.
```

Render step6 as `ORIGINALS = {`, LF, then one line per symbolic key in table
order: four spaces, KEY, `: (`, decimal bytes, `, `, Python repr of the ASCII
hash string, `),`, LF; finish with `}`. Render steps7–9 as NAME + ` = ` + Python
repr of the specified two-element tuple. Render steps10–11 as NAME + ` = (` +
LF, then each binding step in order as four spaces + `(` +
repr(old.encode('ascii')) + `, ` + repr(new.encode('ascii')) + `, ` + decimal
count + `),` + LF, ending `)`. Only old/new/count determine source; recorded
before/after identities are checked evidence. Preserve all other bytes and LF.

All function bodies remain byte-identical to D205 except the two private module
name literals in `load_reader`. No new function, import, conditional, handler,
filesystem action or device action is introduced. In particular preserve exact
`require`, `_stamp`, `_plain_chain`, `_read_handle` and `pinned`; their body pins
are in the binding and match accepted D209. Preserve `_verify`, `_project`,
`project_reader`, `project_parser`, `_module` and CLI behavior as well.

## Private original-first composition and admission

Public seams remain `project_reader(raw)`, `project_parser(raw)`,
`load_reader(*, root=ROOT)` and `main(argv)`. Imports are passive; projections
accept only exact bytes with exact input/output identities and occurrence
counts. Use private ModuleType namespaces with original absolute `__file__`
values; do not register them in `sys.modules` or mutate historical modules.

After every outer input and contract is checked, project the historical entry
parser as data. Privately load checked D209, save its original `project_reader`,
compose that projector first and the new entry metadata projector second, then
call D209's unchanged `load_reader`. It still performs its full ordinary input
verification, original D188 projection and guarded loader injection. Extend a
COPY of returned `HARD_PINS` with the eight fixed inputs and this contract.
Privately load only the projected historical entry definitions and directly
assign their `queries` and `summarize` to the returned reader. Never invoke the
historical entry parser's `load()`/`main()`, never invoke unprojected historical
device operations, and never call the ordinary ABI summary on an entry packet.
The explicitly required private D209 `load_reader` and final projected reader's
`main` are permitted; the unused ABI summary/helper definitions may remain inert.

Retain complete ancestry/plain-file/single-link/reparse checks, descriptor
admission before bounded reading, O_NOFOLLOW/O_NONBLOCK, digest and size guards,
full same-API stamp stability, only the accepted Windows executable pathname
0111 difference and cross-API ctime exception, closure and first-error handling.
Do not add installed-tool hardlink exceptions to local source readers.

CLI accepts only an exact list of exact strings:
`--check-only|--execute --reviewed-head <40 lowercase hexadecimal characters>`.
Require Python `-B` before input reading and delegate exactly once. No owner,
path, target, grant, address, symbol, range, build profile or retry option exists.

## Reader and parser projections

The accepted D209 reader projection is12965 bytes/7fb42d51. Apply the nine
exact binding reader steps: SELF suffix, local owner, remote scope, D209 ABI
scope to D210 ENTRY scope, CHECKED status, OBSERVED status, file-entry label,
entry.json and StaticEntry class. Counts are **1,1,1,2,1,1,1,1,2**. The OBSERVED
count is one, unlike D205's two; do not silently reuse the old count. Require
12987 bytes / `331f10914c77f1ece7255262db0d2f0c6472d31f86e680e6ec23c39c4b682b45`.

The historical parser input is10317 bytes/cb9ee5bb. Apply exactly nine ordered
one-occurrence steps from the binding:

1. Exact historical full build path to ordinary-app-static01/build/app.ino.
2. Complete RANGES assignment to the frozen64-group literal tuple, with full
   explicit alias strings, no comprehensions or lookup selectors.
3. Complete BOUNDS assignment to the six explicit current symbol addresses.
4. Complete `label in (...)` LOCAL classification context to the three labels
   global_initializer, candidate_period and map_channel.
5. Complete WEAK classification context to init_variant, main and the nine
   emitted default-constructor labels listed in the binding. All other groups
   remain GLOBAL; every FUNC/type/DEFAULT/section/Thumb/size predicate is exact.
6. Exact initializer checked-section address comparison to0x081158f0.
7. Exact initializer byte-dump address comparison to0x081158f0.
8. Exact complete initializer return-dict expression with address0x081158f0.
9. Exact `pointer == 0x08100105` context to `pointer == 0x08100101`.

Require parser14259 bytes /
`a71d5c172b65952ab010441bfd894f2552e08bf2a66c19adf0eed29c381a6e05`. Only `queries`, `symbols`
and `initializer` differ, solely in fixed path/range-classification/address
metadata. All other parser bodies are exact; no new parser algorithm or
relaxed comparison is introduced. Do not globally replace addresses. The
binding preserves each old/new/count and intermediate length/hash.

## Fixed observed ranges and initialization

Exactly64 groups,77 complete aliases,129 GDB expressions and10420 selected
bytes are admitted. The retained two-digit marker parser requires fewer than100
groups. Selected intervals do not overlap; no gaps within any selected function
are allowed in future instruction output. Table values are hexadecimal,
exclusive end. Full alias names/observed rows/source pointers/per-group reasons
are normative in the binding.

| Index | Group | Start | End | Bytes | Binding | Aliases |
|---:|---|---|---|---:|---|---:|
| 0 | entry_point | 08100010 | 081000c8 | 184 | GLOBAL | 1 |
| 1 | setup | 081000c8 | 081000f0 | 40 | GLOBAL | 1 |
| 2 | loop | 081000f0 | 08100100 | 16 | GLOBAL | 1 |
| 3 | global_initializer | 08100100 | 08100294 | 404 | LOCAL | 1 |
| 4 | app_dump_port | 081002a4 | 081002cc | 40 | GLOBAL | 1 |
| 5 | sources_port | 081003dc | 08100458 | 124 | GLOBAL | 1 |
| 6 | sources_adc_port | 08100458 | 0810046c | 20 | GLOBAL | 1 |
| 7 | dump_port | 0810c248 | 0810c25c | 20 | GLOBAL | 1 |
| 8 | motor_port | 08110934 | 081109b8 | 132 | GLOBAL | 1 |
| 9 | power_reader_port | 08112cd0 | 08112cf4 | 36 | GLOBAL | 1 |
| 10 | loop_hook | 081106e4 | 081106e6 | 2 | GLOBAL | 1 |
| 11 | memcpy | 08115644 | 0811564c | 8 | GLOBAL | 1 |
| 12 | memset | 0811564c | 08115654 | 8 | GLOBAL | 1 |
| 13 | init_variant | 0811571c | 0811571e | 2 | WEAK | 1 |
| 14 | main | 08115720 | 0811574c | 44 | WEAK | 1 |
| 15 | start_static_threads | 0811574c | 081157b8 | 108 | GLOBAL | 1 |
| 16 | runtime_constructor | 08100510 | 08100a26 | 1302 | GLOBAL | 2 |
| 17 | transaction_constructor | 081030f8 | 081032a8 | 432 | GLOBAL | 2 |
| 18 | gate_constructor | 08111084 | 081110c0 | 60 | GLOBAL | 2 |
| 19 | input_owner_constructor | 081126ec | 0811273e | 82 | GLOBAL | 2 |
| 20 | robot_constructor | 08102b58 | 081030f8 | 1440 | WEAK | 2 |
| 21 | fusion_observation_constructor | 08102a20 | 08102a44 | 36 | WEAK | 2 |
| 22 | flank_constructor | 08102a44 | 08102a94 | 80 | WEAK | 2 |
| 23 | turn_constructor | 081029d8 | 08102a06 | 46 | WEAK | 2 |
| 24 | straight_constructor | 08102a06 | 08102a20 | 26 | WEAK | 2 |
| 25 | line_thresholds_constructor | 0810046c | 08100484 | 24 | WEAK | 2 |
| 26 | qtr_report_constructor | 08100484 | 081004bc | 56 | WEAK | 2 |
| 27 | line_snapshot_constructor | 081004bc | 0810050c | 80 | WEAK | 2 |
| 28 | robot_result_constructor | 08102a94 | 08102b54 | 192 | WEAK | 2 |
| 29 | runtime_begin | 08100f9c | 08101050 | 180 | GLOBAL | 1 |
| 30 | runtime_valid_ports | 08100a28 | 08100aa8 | 128 | GLOBAL | 1 |
| 31 | runtime_initialize_sources | 08100da4 | 08100ef4 | 336 | GLOBAL | 1 |
| 32 | runtime_initialize_dump | 08101acc | 08101b08 | 60 | GLOBAL | 1 |
| 33 | transaction_initialize | 081032a8 | 081032e4 | 60 | GLOBAL | 1 |
| 34 | gate_begin | 081111b8 | 08111240 | 136 | GLOBAL | 1 |
| 35 | runtime_step | 0810144c | 08101588 | 316 | GLOBAL | 1 |
| 36 | transaction_open | 0810338c | 08103418 | 140 | GLOBAL | 1 |
| 37 | transaction_decide_from | 0810358c | 08103600 | 116 | GLOBAL | 1 |
| 38 | transaction_apply_decision | 0810346c | 0810358c | 288 | GLOBAL | 1 |
| 39 | gate_apply | 08111448 | 08111540 | 248 | GLOBAL | 1 |
| 40 | gate_transact | 081113e0 | 08111448 | 104 | GLOBAL | 1 |
| 41 | runtime_complete_epoch | 0810136c | 0810144c | 224 | GLOBAL | 1 |
| 42 | transaction_complete | 08103600 | 081036c8 | 200 | GLOBAL | 1 |
| 43 | transaction_finish_after | 081036c8 | 081036d4 | 12 | GLOBAL | 1 |
| 44 | runtime_fail | 08100cf0 | 08100d74 | 132 | GLOBAL | 1 |
| 45 | runtime_cancel_sources | 08100c70 | 08100cf0 | 128 | GLOBAL | 1 |
| 46 | transaction_fail | 08103318 | 0810338c | 116 | GLOBAL | 1 |
| 47 | transaction_abort | 081036d4 | 081036e0 | 12 | GLOBAL | 1 |
| 48 | gate_halt | 08111540 | 081115e0 | 160 | GLOBAL | 1 |
| 49 | gate_inhibit | 0811111a | 081111b8 | 158 | GLOBAL | 1 |
| 50 | gate_zero_pwm | 081110f8 | 0811111a | 34 | GLOBAL | 1 |
| 51 | configure_enable_low | 08110a64 | 08110b98 | 308 | GLOBAL | 1 |
| 52 | configure_pwm | 08110db0 | 08110e9c | 236 | GLOBAL | 1 |
| 53 | write_enable | 08110b98 | 08110bfc | 100 | GLOBAL | 1 |
| 54 | write_pwm | 08110e9c | 08110f80 | 228 | GLOBAL | 1 |
| 55 | motor_settle | 08110fc4 | 08111084 | 192 | GLOBAL | 1 |
| 56 | motor_clock | 08110794 | 0811079c | 8 | GLOBAL | 1 |
| 57 | candidate_period | 08110758 | 0811076c | 20 | LOCAL | 1 |
| 58 | map_channel | 0811082c | 08110934 | 264 | LOCAL | 1 |
| 59 | enable_owned | 081109b8 | 08110a64 | 172 | GLOBAL | 1 |
| 60 | enable_low | 08110bfc | 08110c30 | 52 | GLOBAL | 1 |
| 61 | timer_valid | 08110c30 | 08110db0 | 384 | GLOBAL | 1 |
| 62 | bank_valid | 08110f80 | 08110fc4 | 68 | GLOBAL | 1 |
| 63 | gate_valid_port | 081110c0 | 081110f8 | 56 | GLOBAL | 1 |

The categories are startup/binding16, constructors13, setup6, ordinary dispatch/
completion9, fault cleanup7, native motor callbacks/helpers12 and gate-valid-port1.
All aliases are FUNC/DEFAULT/section1, value=start|1, size=end-start. There are
three LOCAL groups, eleven WEAK groups and fifty GLOBAL groups. Four explicit
constructor groups are GLOBAL; nine default-constructor groups are WEAK.
Constructor pairs are selected because their source-defined ownership is
relevant and the FUNC rows actually exist, not because calls have been observed.

The current .text is section1 [0x08100010,0x081158f0), AX/alignment8. The sole
.init_array is section2 INIT_ARRAY [0x081158f0,0x081158f4), WA/alignment4 and
one four-byte entry. Six BOUNDS rows are NOTYPE/size0/DEFAULT/section2:
__init_array_start, __preinit_array_start and __preinit_array_end are LOCAL at
0x081158f0; __init_array_end is LOCAL at0x081158f4; the two
__static_thread_data_list bounds are GLOBAL at0x081158f0. Expected sole pointer
0x08100101, bytes01011008, comes from the current global_initializer FUNC row.
Those bytes have **not** yet been observed. The new readelf .init_array dump
must observe them and the parser must reject a discrepancy.

D208's checked startup copy is208 bytes from0x08116a40 to0x20013890; destination
end0x20013960. Initialized BSS is [0x20013960,0x2003c6c8),167272 bytes. The full
.bss section ends0x2003c800; its312-byte tail is not part of the zero span.
The binding retains _sidata/_sdata/_edata/_sbss/_ebss rows for instruction review.
These facts remain bound by checked artifact identity; the parser does not gain
new ad hoc assertions for otherwise unselected symbol rows.

Observed objects: Runtime0x20013960/166376 bytes and UnoQPort0x2003c348/40 bytes
are the two typed D209 ABI objects. Sources0x2003c370/848 bytes is a raw LOCAL
OBJECT in BSS; dump_port0x20013890/208 bytes is a raw LOCAL OBJECT filling .data.
Do not claim queried type/layout for those latter two. D209's six ordinary
Runtime windows and exact full type layouts remain accepted reference evidence.

Complete symbol inventory has no FUNC name containing the recorded tokens
NativeSourcesC, AcquirerC, SetupC, BusC, AttemptRecorderC, TransferC,
UnoQDumpPortC, UnoQPortC, RuntimeReportC or configuredSetupGrants. There is no
fabricated standalone range for them. Their source-defined default/inline/
constexpr initialization may occur in selected callers or remain source-only;
absence of a name does not prove compiler inlining or absent computation.
In particular constexpr FIFO8 construction of dump_port supplies .data contents;
a sole .init_array hex query does not observe the FIFO8 byte or prove an
initializer instruction wrote it.

## Commands, lifecycle and evidence limits

Retain the four children: pinned readelf --version, pinned GDB --version,
readelf `-hSWs -x .init_array` against the fixed raw ELF, and guarded GDB against
its debug ELF. Retain -nx/-nh/batch/no-auto-load/C++/no-function-call settings.
For every fixed range, in order, emit a SUMOX_ENTRY_00 through SUMOX_ENTRY_63
marker and `disassemble /r start,end`, followed by SUMOX_ENTRY_END. The129
expressions use literal backslash+n echo endings, never embedded newlines.
The positive host command fixture must use the canonical retained tool prefix
and GDB argv builder. No target attach/run, expression function call, MCU memory
read, reset, upload, compile, credential, deletion or hardware modification.

Fresh local owner: `state/analysis/P7_ordinary_app_static_compile_raw/native_entry_static01`.
Fresh remote scope: `/home/arduino/sumox26_codex_build/ordinary-app-entry-static01`.
Inherited admission checks remote absence but does not create it. Check-only
remains local/read-only/unclaimed. Execute claims its exclusive local owner and
allows at most one file-only transport. Preserve the consumed build/ABI owners;
failed or partial entry attempts remain consumed, with no automatic retry.

Retain clean reviewed HEAD, exact ordinary source/manifest/compiler/artifact/
tool/boot checks,128MiB local free-space minimum,60s child deadline,5s reap,
1MiB child streams,8MiB transport reply,400s transport timeout and30000 UTF-16
command units. Preserve twelve remote file pins, thirteen closing checks,
independent local closure, first-error priority, evidence-write failures and
raw-first ordering inputs.json/result.json/entry.json/local_result.json. The
accepted D209 receipt does not replace use-time file/identity admission.

Parser success remains STATIC_ENTRY_OBSERVED with its instruction-only,
semantic-review-pending limitation. Preserve decimal/0x symbol-size parsing,
exact alias/binding/type/section/Thumb bounds, initializer span/content checks,
ordered unique markers, one correct disassembly header/end, opcode widths,
unparsed address-row refusal, gap/overlap refusal, complete function coverage
and raw-block hashes. Never mutate the raw result or checked layout.

After collection, an independent reviewer must inspect all64 emitted groups:
startup copy/zero and initializer relationship; ordinary object/port bindings;
actual constructor stores/call edges; setup's absent grants; dispatch and
completion propagation; inhibited gate/callback ordering; retained live getter,
register checks and150-us/4096-iteration SETTLE limits; and fault/cleanup ordering.
A source member relationship is not evidence that a particular constructor call
was emitted. Runtime.begin's return is ignored by setup; there is no begin_ok
field. Continuous loop/Runtime.step is not a diagnostic bounded Runner.

Claims must stop at unselected callees. Peripheral acquisition bodies, chronology
helpers, Robot strategy, recorder and UART cancellation interiors remain source/
host evidence unless their instructions fall inside selected ranges. Runtime
FAULT may be stored before source/dump cleanup; it is not a publication-completion
barrier. No instruction review creates runtime contents, coherent/atomic reads,
WCET, physical inhibition, loader execution, ordinary runtime acceptance or a
phase gate. If selected instructions are insufficient, report the limitation;
do not dynamically expand the file query or mutate a successful/failing attempt.

## Independent oracle requirements and first execution

The binding names every selected historical method and every exclusion. Retain
these26 applicable obligations through explicit count/hash-checked fixture
projections, with the old assertions preserved wherever their semantics apply:

- `test_passive_import_and_exact_bootstrap_source`
- `test_both_projectors_produce_exact_contract_bytes_without_io`
- `test_projectors_reject_types_lengths_hashes_counts_and_newlines`
- `test_invalid_cli_or_missing_B_refuses_before_input_loading`
- `test_main_delegates_once_and_preserves_result_or_primary_exception`
- `test_all_six_inputs_are_verified_before_private_execution`
- `test_original_first_composition_and_no_historical_entry_load_or_main`
- `test_private_direct_entry_functions_pins_and_fresh_owner`
- `test_exact_four_file_queries_and_all_twenty_seven_ranges`
- `test_full_synthetic_entry_summary_decimal_hex_and_opcode_widths_preserves_raw`
- `test_symbol_address_size_type_binding_section_and_Thumb_failures`
- `test_missing_duplicate_constructor_aliases_and_initialization_bound_tuples_refuse`
- `test_initializer_section_span_dump_and_little_endian_pointer_are_required`
- `test_markers_require_exact_unique_order_and_final_marker`
- `test_disassembly_headers_end_markers_instruction_format_gaps_overlap_and_coverage`
- `test_real_prepare_composes_only_entry_commands_without_claiming`
- `test_execute_retains_raw_entry_summary_labels_and_local_closure`
- `test_scope_stream_and_parser_failures_retain_raw_and_attempt_local_closure`
- `test_consumed_owner_refusal_and_primary_failure_survives_closure_errors`
- `test_exact_wrapper_reader_parser_recipes_and_unchanged_function_bodies`
- `test_every_projection_occurrence_count_refuses_drift`
- `test_current_inputs_refuse_exact_stale_d199_bytes_before_private_execution`
- `test_current_source_manifest_artifacts_refuse_stale_d199_evidence`
- `test_consumed_d199_owner_and_scope_cannot_be_reused`
- `test_all_thirteen_remote_closures_are_required_with_raw_preservation`
- `test_direct_entry_summary_does_not_call_abi_summary_or_require_abi_tags`

The four original methods below remain preserved in historical files/evidence;
their diagnostic-specific fixtures are not globally renamed into ordinary facts:

- `test_added_functions_require_exact_unique_binding_thumb_size_type_and_section`: SETTLE/probe-specific binding and added diagnostic range fixture; ordinary all-group binding/alias/marker cases preserve relevant generic rejection obligations.
- `test_binding_matches_accepted_symbols_and_separate_report_without_invented_contents`: SETTLE/probe-specific binding and added diagnostic range fixture; ordinary all-group binding/alias/marker cases preserve relevant generic rejection obligations.
- `test_complete_symbol_census_helper_absence_and_all_current_ranges`: D205 diagnostic32-group/helper-absence expectations are replaced with independently authored current64-group/77-alias ordinary binding and complete-census checks.
- `test_each_added_range_requires_its_markers_and_complete_disassembly`: SETTLE/probe-specific binding and added diagnostic range fixture; ordinary all-group binding/alias/marker cases preserve relevant generic rejection obligations.

Add the ordinary all-group binding/census case named in the binding, for27 planned
obligations before separately justified additions. It must reconcile all2234
symbol rows,64 groups,77 aliases,129 expressions and10420 bytes; both constructor
alias kinds and GLOBAL/WEAK distinctions; typed and raw-only object evidence;
all selected per-group alias/marker/range failures; current initializer pointer;
source/hash/artifact/owner bindings and stale diagnostic substitutions. The
relevant generic rejection obligations of the excluded probe-addition cases
must remain covered by the ordinary all-group cases. Do not delete a meaningful
assertion or replace a real admission/execute path with a success-only mock.

Keep exact private projection input/output/count/type/newline drift checks;
original-first event ordering; no parser load/main or inherited ABI-summary call;
passive imports and source pins before exec; current ordinary125-file admission;
all four commands and no target operations; raw/layout immutability; decimal/hex
sizes, every selected alias and initialization tuple; marker/header/opcode/gap/
overlap/refusal cases; all thirteen closure refusals, consumed owners and primary
error preservation. Retain stale fault/observe/constant diagnostic negatives and
add rejection of the consumed ordinary ABI scope/owner where relevant; do not
transpose a negative into current valid metadata.

Synthetic packets must use the fixed declared range lengths/aliases/bindings,
current section/initializer contexts and explicit complete coverage, including
both supported32-bit opcode spellings and16-bit rows. They are fixtures, not
observed instructions. Use independently recorded AST/literal transformations;
resolve symbolic constants only as bounded data. Load selected method names
explicitly so subclass inheritance cannot duplicate the suite. Frozen metadata
must include exact method/assertion counts, exclusions, projection operands and
identities, transitive historical inputs and public API expectations. Any new
same-platform or inherited skip must be named and justified; do not assume an
entry test is Linux-only. Historical entry behavior ran on both platforms.

Root seals the implementation identity without reading the independent oracle.
The independent author derives behavior from this adopted contract/binding and
pinned historical material, and must not read/hash/import/execute the new D210
subject until its oracle FINAL. A metadata-only identity receipt is allowed.
Separate reviewers inspect the finalized source and oracle before root first
execution. Existing source, locked tests and historical evidence stay unchanged.

Run `python -I -B tests/tooling/test_ordinary_app_entry.py` serially on Linux then
Windows, each under360s outer timeout (within the previous600s maximum). Use
exclusive local receipt owners `entry_first_linux01` and `entry_first_windows01`
under this RAW. Linux fixtures use /dev/shm as the actual nonroot user; Windows
TEMP/TMP/TMPDIR must point to a dedicated directory before interpreter startup.
Freeze all inputs before/after, save exact argv/environment/status/stdout/stderr,
keep subprocess/native/compiler/network endpoints blocked and complete fixture
cleanup with verified bounded ownership. No suite-specific environment is added
without documenting it before the independent freeze.

The host driver may be the existing D209 abi_host_driver01.py derivative using
three count-checked metadata substitutions; preserve all limits, pre-start temp
isolation, exclusive receipt creation, input-pin checks and failure evidence.
First failures are saved before adjudication. A bounded fixture or source repair
requires explicit disposition and a new freeze/receipt owner, never overwriting
the first result or weakening assertions. Successful host tests, independent
source/host/scope reviews, committed clean HEAD and check-only are prerequisites
to any one native file query. Hold outside writers for that native lifecycle.
No human phase pass or motor-run authorization is inferred from this contract.
