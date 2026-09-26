# D205 constant motor metadata file-entry observation

26 September 2026. This proposed fixed file-only task follows accepted D204 ABI
evidence and prepares one new entry wrapper at
state/analysis/P7_motor_const_compile_raw/inspect_static_entry.py. No executable
may be created until this contract and its binding are adopted and implementation
ownership is assigned. This contract records actual file symbols and a proposed
instruction scope; it does not claim instruction semantics or target execution.

## Accepted evidence and fixed scope

D204's raw ABI result, summary, independent local closure and actual review are
accepted. The full readelf stdout is 158419 bytes, SHA256
5632ddc6fe74d5ec5357e2f43f0a36bb74028232d833d4d2eac4537a319ee163.
Its single .symtab declares 2299 entries. Every numbered row 0 through 2298 was
parsed without filtering by kind, binding or visibility. The binding records
the selected exact rows and the helper-name inventory.

The exact candidateRate name has no row, and no symbol name contains the
candidateRate token; therefore there is no candidateRate clone in this complete
name inventory. candidatePeriod has one LOCAL FUNC row, value 0x08110c91,
size 20, DEFAULT, section 1, with no additional name-token row. No symbol name
contains expectedRate, expectedPeriod, liveRateValid, storeSettleSample or
settleProbeReport. These are absence observations, not proof of inlining,
correct instructions or eliminated division.

The engineering scope selected before the independent oracle is 32 groups,
34 aliases, 65 GDB expressions and 3834 selected bytes. Retain the historical
29 D199 groups in their original order except the proven absent candidate_rate,
then append timer_valid, bank_valid, write_pwm and map_channel in that order.
No other old group is removed. Both aliases of each constructor remain required.
All selections are frozen from complete observed rows; no runtime selector,
substring search, clone fallback, guessed range or adjustable address exists.

The image is source
4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2,
app_motor_observe.ino, arduino:zephyr:unoq:link_mode=static, default startup,
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1.
The fixed build owner is
/home/arduino/sumox26_codex_build/app-motor-const-static01,
boot 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, serial 2629958581.

These eight inputs are the new wrapper's ORIGINALS set, in the order shown:

| Repository-relative input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_const_compile_raw/inspect_static_abi.py | 16087 | f360a52d6e8c29227b8a59481f37f5e8a30b207d7b66fbffaa8e8785a4dedf3c |
| state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py | 10317 | cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/result.json | 904847 | bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/abi.json | 5410 | 6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/local_result.json | 275 | 3cd224b237fc1b18586d7b2fb22c2a47833a801fea06b96b338027102db5d55d |
| state/reviews/P7_motor_const_abi_actual_review.md | 10178 | 4cd28fe8ce3b689319da5ddb42739c664fd0e4bcdc2552b521ee23b8b3331411 |
| state/analysis/P7_motor_const_compile_raw/native_static01/artifacts.json | 9645 | fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd |
| state/analysis/P7_motor_const_compile_raw/entry_binding01.json | 44374 | 7417ff7055e30238e8a3231db3287ffb3520ec8929ce3437afbd0dff1c2d60ae |

Their symbolic keys are ABI, PARSER, ABI_RESULT, ABI_LAYOUT, ABI_CLOSURE,
ABI_REVIEW, ARTIFACTS and BINDING, respectively. Check exact lengths and hashes
of all eight, then this contract's digest, before any private source execution.
Keep SELF bound through clean reviewed HEAD rather than a recursive self hash.

The binding is normative fixed evidence and exact projection data. It records
18 preparation input pins, the complete-symbol inventory accounting, all ranges
and aliases, initialization symbols, current report layout, eight artifact
file hashes, and the nine reader/seven parser substitutions with intermediate
identities. It is not a runtime selector or permission record. JSON escapes
encode the actual byte operands, including newlines. Its hash is fixed above.
The binding does not contain this contract's hash; no circular binding exists.

## Exact successor wrapper recipe

The complete predecessor wrapper is
state/analysis/P7_motor_settle_compile_raw/inspect_static_entry.py,
10425 bytes, SHA256
c9e8f023ffc853dce951b05c24cbd55bef04270682c3d271cb1087b2fa67ab81.
Its source algorithm and public seams are retained. Its historical contract is
state/analysis/P7_motor_settle_entry_contract.md, 19485 bytes, SHA256
af8ce726bf49b79fecc07548bd78a808d788894ea9e9e1b59daa69eae8a54e7d.
Supersede only the fixed metadata and projection tables specified here.

Define C as SHA256 of this complete final contract file, lowercase hex. Seal
the binding, then this contract, then compute C and the prospective wrapper
identity in entry_derivation01.json. The contract deliberately contains no
final wrapper digest. The derivation is a preparation receipt, not an extra
runtime input.

Produce the new wrapper using exactly these 12 ordered, one-occurrence
substitutions over the pinned predecessor. Preserve every other byte and line
ending. For complete-assignment operands, take the one top-level assignment
from its first byte through the final expression byte, excluding its following
line ending. Data-only AST source spans may establish these operands during
preparation; the new wrapper gains no AST evaluation or new executable logic.
Each old operand and intermediate identity must be recorded in the derivation.

| Step | Old operand | New operand |
|---:|---|---|
| 1 | P7_motor_settle_compile_raw/ | P7_motor_const_compile_raw/ |
| 2 | P7_motor_settle_abi_actual_review.md | P7_motor_const_abi_actual_review.md |
| 3 | P7_motor_settle_entry_contract.md | P7_motor_const_entry_contract.md |
| 4 | af8ce726bf49b79fecc07548bd78a808d788894ea9e9e1b59daa69eae8a54e7d | C |
| 5 | complete ORIGINALS assignment | the eight current identities above |
| 6 | complete READER_INPUT assignment | (17051, '938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6') |
| 7 | complete READER_PROJECTED assignment | (17075, '580abb32b2597ceed62dadb6ea28ac028d3ffb66e5e5fa2d0c42a7400ad1b9f3') |
| 8 | complete PARSER_PROJECTED assignment | (10866, 'c4c4f9e26b35da497e6a092de361b1727759ea1a16c7026b9242037c0544c90b') |
| 9 | complete READER_REPLACEMENTS assignment | binding projection.reader.steps |
| 10 | complete PARSER_REPLACEMENTS assignment | binding projection.parser.steps |
| 11 | _sumox_d199_entry_abi | _sumox_d205_entry_abi |
| 12 | _sumox_d199_entry_parser | _sumox_d205_entry_parser |

For step 5 use exactly "ORIGINALS = {", LF, then one line per symbolic key in
the stated order, four spaces, KEY, ": (", decimal size, ", ", Python repr of
the ASCII digest string, "),", LF, then "}". The quoted prose marks delimiters;
the resulting source contains ordinary Python punctuation.

For steps 6 through 8 use NAME + " = " followed by Python repr of the specified
two-element (integer, digest-string) tuple, with no trailing LF in the operand.

For steps 9 and 10 use NAME + " = (" + LF, then for each binding step in order
four spaces + "(" + repr(old.encode("ascii")) + ", " +
repr(new.encode("ascii")) + ", " + decimal count + ")," + LF, then ")".
Only old/new/count members of the binding steps determine source. Their
before/after identities are verification evidence. This deterministic rendering
uses exact byte literals; it does not import or execute a source definition.

The result preserves every function body except the two fixed private module
name literals in load_reader. No new function, import, class, conditional,
exception handler, filesystem action or device action is introduced.

## Original-first composition and bootstrap

Keep public project_reader(raw), project_parser(raw), load_reader(*, root=ROOT)
and main(argv), exact bytes-only identity/count checks, passive import, private
ModuleType namespaces and original absolute __file__ values. Never register
private modules in sys.modules or invoke historical load/main entrypoints.

Main accepts only an exact list of exact strings:
--check-only|--execute --reviewed-head <40 lowercase hexadecimal characters>,
requires Python -B before input reading, and delegates once. No configurable
profile, build, symbol, address, range, target, owner or other CLI is added.

Preserve byte-identical require, _stamp, _plain_chain, _read_handle and pinned
from the accepted D204 ABI wrapper: complete ancestry, plain single-link local
files, reparse refusal, O_NOFOLLOW/O_NONBLOCK, bounded size/digest checks,
descriptor admission before reading, same-API stamps, exact Windows pathname
0111 executable exception and cross-API ctime exception, resource closure and
first-error preservation. Do not import installed-tool hardlink allowances.

After all nine wrapper inputs are checked, project the historical parser as
data. Privately execute the checked D204 ABI wrapper, save its projector,
compose saved-projector first and new entry projector second, then call its
unchanged load_reader. Preserve its full nested original-first loading,
normalizers, bootstrap and inherited hard pins, including consumed ABI01
failure provenance. Copy HARD_PINS and extend it with the eight new inputs and
this contract; do not mutate original modules.

Privately execute only the checked projected historical entry definitions.
Assign their queries and summarize directly to the returned reader. Never call
the inherited ABI/polls/SETTLE summary on an entry packet; its unused definitions
may remain. Every transport, prepare, execution, parser and closing lifecycle
outside these metadata changes remains inherited and exact.

## Exact reader and parser projections

Reader input is exactly 17051 bytes /
938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6,
the output of the accepted D204 ABI projection, after original-first loading.
Use exactly the binding's nine substitutions: SELF suffix, local owner, remote
scope, D204 ABI to D205 ENTRY scope, CHECKED/OBSERVED labels, file-entry label,
entry.json and StaticEntry class name. Counts remain 1,1,1,2,1,2,1,1,2.
The final reader is 17075 bytes /
580abb32b2597ceed62dadb6ea28ac028d3ffb66e5e5fa2d0c42a7400ad1b9f3.

Parser input is the unchanged historical 10317-byte source
cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34.
Use exactly the binding's seven ordered one-occurrence substitutions:

1. Replace the complete fixed build path with the current constant-metadata
   build path ending in /build/app_motor_observe.ino.
2. Replace the entire original RANGES assignment with the frozen 32-group
   literal tuple. Constructor aliases are explicit complete names.
3. Replace the entire original BOUNDS assignment with the literal six-entry
   dictionary derived from current initialization symbols.
4. Replace the complete LOCAL-label tuple with
   ('global_initializer', 'candidate_period', 'publish_settle', 'map_channel').
5. Replace the unique complete context
   sections[0]['address'] == 0x08116218 with the same context at 0x08116258.
6. Replace the unique complete context
   int(lines[0][0], 16) == 0x08116218 with the same context at 0x08116258.
7. Replace the complete return-dict expression beginning
   return dict(address=0x08116218, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)
   with the same expression at 0x08116258.

The initializer pointer comparison remains exactly pointer == 0x08100105,
because the new observed initializer symbol has that Thumb value. This is a
required future byte observation, not an already observed .init_array word.
No arbitrary global address replacement, address delta or collision-sensitive
sequence is allowed. The binding contains both full assignment operands and
every context operand exactly.

Require final parser 10866 bytes /
c4c4f9e26b35da497e6a092de361b1727759ea1a16c7026b9242037c0544c90b.
Only fixed metadata changes: functions queries, symbols and initializer
differ solely in their build-path, binding-label and address literals.
All other function bodies are byte-identical. Keep historical unused
loader definitions inert and never overwrite any original source.

## Fresh file ranges and initialization

The following starts have the Thumb bit cleared; each mandatory exact FUNC
alias has value start|1 and size end-start, DEFAULT visibility and section 1.
The binding supplies complete alias names and original observed readelf rows.

| Label | Start | End exclusive | Bytes | Binding | Aliases |
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
| candidate_period | 0x08110c90 | 0x08110ca4 | 20 | LOCAL | 1 |
| motor_port | 0x08110ea8 | 0x08110f2c | 132 | GLOBAL | 1 |
| power_reader_port | 0x081132a8 | 0x081132cc | 36 | GLOBAL | 1 |
| trace_constructor | 0x08115c2c | 0x08115cbc | 144 | GLOBAL | 2 |
| trace_port | 0x08115cbc | 0x08115d3c | 128 | GLOBAL | 1 |
| memcpy | 0x08115fac | 0x08115fb4 | 8 | GLOBAL | 1 |
| memset | 0x08115fb4 | 0x08115fbc | 8 | GLOBAL | 1 |
| unsigned_divide | 0x0811606c | 0x08116076 | 10 | GLOBAL | 1 |
| init_variant | 0x08116084 | 0x08116086 | 2 | WEAK | 1 |
| main | 0x08116088 | 0x081160b4 | 44 | WEAK | 1 |
| start_static_threads | 0x081160b4 | 0x08116120 | 108 | GLOBAL | 1 |
| publish_settle | 0x08110cd4 | 0x08110d10 | 60 | LOCAL | 1 |
| motor_settle | 0x08111538 | 0x0811165c | 292 | GLOBAL | 1 |
| timer_valid | 0x081111a4 | 0x08111324 | 384 | GLOBAL | 1 |
| bank_valid | 0x081114f4 | 0x08111538 | 68 | GLOBAL | 1 |
| write_pwm | 0x08111410 | 0x081114f4 | 228 | GLOBAL | 1 |
| map_channel | 0x08110da0 | 0x08110ea8 | 264 | LOCAL | 1 |

The current .text is section 1 at 0x08100010, size 0x16248, AX, alignment 8.
Every selected complete range is inside it. The current .init_array is section 2
at 0x08116258, size 4, WA, alignment 4. __init_array_end is 0x0811625c.
__init_array_start, __preinit_array_start/end and
__static_thread_data_list_start/end are 0x08116258. Require their observed
NOTYPE/zero-size/DEFAULT/section2 rows exactly; thread bounds are GLOBAL,
the others LOCAL. The expected initializer pointer 0x08100105 comes from the
unique _GLOBAL__sub_I_setup FUNC row.

D204 did not dump initialization bytes. This entry attempt must freshly obtain
the single four-byte little-endian word, at the fixed current section address,
and require that pointer. Do not substitute old D199 .init_array bytes.

The current separate report is freshly observed at 0x2003d3e8 for 28 bytes,
alignment 4, LOCAL OBJECT DEFAULT section 5, complete name
_ZN6motors12_GLOBAL__N_119settle_probe_reportE. Its 12-byte samples, presence
flags, fields/reasons and initialized-BSS/nonoverlap checks come from accepted
D204 ABI, which the binding preserves. The unchanged entry parser does not
invent new report fields or reread RAM.

## Commands, interpretation and remaining limits

Retain four children: pinned readelf --version, pinned gdb --version, readelf
-hSWs -x .init_array on the fixed raw ELF, and guarded GDB on its debug ELF.
Retain no-init/no-auto-load/batch/C++/no-function-call settings. Exactly 65
expressions are marker plus disassemble /r for each of 32 groups, then
SUMOX_ENTRY_END. Markers run SUMOX_ENTRY_00 through SUMOX_ENTRY_31 in order.
Echo endings remain literal backslash+n bytes.

Preserve unique exact symbol tuples, decimal/0x size parsing, section/Thumb/
binding/alias checks, initializer bounds/bytes/pointer checks, exact markers,
range headers and end markers, opcode widths, unparsed-row refusal, no gaps or
overlaps, complete selected-function coverage and raw-block hashes. Preserve
the raw readelf/GDB bytes. Parser success remains STATIC_ENTRY_OBSERVED with
its inherited instruction-only, semantic-review-pending limitation.

After successful collection, a separate reviewer must inspect the emitted
instructions, including all retained entry/Runner/constructor/init/publication
and SETTLE groups, not infer their correctness from historical reviews.

Review current and first-failure stores, their presence flags and lifetime
guard against the newly bound report address/layout. Verify zero-BSS startup,
initializer consistency, inert grants, bounded poll/epoch stops and terminal
passivity. In SETTLE and bank/timer consumers verify the retained live getter
and checks, register comparisons, call/order boundaries, fresh-mask path,
150-us deadline and 4096-poll limit. Compare candidate_period and its selected
callers with the prior emitted expected-metadata arithmetic.

A conclusion that immutable metadata arithmetic was eliminated must follow
actual selected instructions and relevant call/tail-call targets. An absent
candidateRate symbol alone is insufficient; its computation may be inlined.
Conversely the retained global __aeabi_uldivmod stub alone does not establish
that these paths still use it. Separate expected-value selection from the
required live PWM getter, whose loader-internal implementation is outside the
selected scope. No whole-program absence of division or cycle savings is
predeclared. If constants, calls or stores cannot be established from the fixed
observations, report the uncertainty without adding unreviewed queries.

## Single-use lifecycle and independent tests

The fresh exclusive local owner is
state/analysis/P7_motor_const_compile_raw/native_entry_static01.
Require remote scope
/home/arduino/sumox26_codex_build/app-motor-const-entry-static01
to be absent; the inherited reader checks but does not create it. The build
owner remains the separately consumed app-motor-const-static01. Preserve every
historical source, owner, successful/failed receipt and first error.

Keep STATIC_ENTRY_CHECKED/STATIC_ENTRY_OBSERVED, scope
D205_STATIC_FILE_ONLY_ENTRY, operation file-entry and summary entry.json.
Retain clean reviewed HEAD, exact local/source/artifact/tool/boot checks,
128MiB local free-space minimum, 60s child, 5s reap, 1MiB streams, 8MiB reply,
400s transport and 30000 UTF-16 command units. Preserve all 12 remote file pins,
13 remote closing checks, independent local closure, raw-first saving,
failed-owner consumption and evidence-write-error behavior. The accepted
D204 raw result and eight D203 artifact pins do not substitute for use-time
checks of the actual fixed files.

Check-only stays local, read-only and unclaimed. Execute remains at most one
file-only transport containing four children. A refusal or partial attempt is
preserved; no automatic retry or repair is authorized. No separate observer
is required beyond the unchanged embedded admission, but fixed source/host
and scope reviews, committed clean HEAD and check-only must precede use.
No concurrent outside writer may invalidate the continuous clean-tree checks.

The historical D199 entry oracle is tests/tooling/test_motor_settle_entry.py,
13633 bytes / 4e6e1caed73b3612d63319e6b15e827cce941e0e365f755083774ed9396f49f6.
Its 23 methods passed on Linux and Windows. Preserve all applicable assertions
through independently derived, count-checked private metadata fixtures; retain
the earlier 19-method provenance and first failures. Freeze the new independent
oracle before its author reads the new implementation and before anyone
executes it. Root and reviewer must await that FINAL barrier before inspecting
the actual new subject. The implementation author must not read the new oracle.

Record every selected method, fixture substitution/count/identity and pin.
Add exact 12-step wrapper, nine-step reader and seven-step parser derivation
checks; unchanged bootstrap/parser function bodies outside permitted literals;
whole RANGES/BOUNDS replacement and context-count drift; the fixed 32-group/
34-alias/65-expression packet; current binding and stale D199 receipt/owner
refusal; proven helper absence as bound evidence; and all inherited input,
alias, section, marker, opcode, initialization, first-error and closure cases.
Do not weaken assertions or replace actual prepare/execute paths with
success-only mocks. Synthetic addresses are explicit fixture metadata, never
unobserved target claims.

Run new Linux and Windows host suites serially under fresh evidence owners,
preserving raw output, skips, all first errors and opening/closing pins. After
source/host and scope reviews close, commit the exact reviewed inputs, check
the fixed reader locally, then perform one separately admitted file observation.
Review its actual receipts before deriving any later runtime scope.

This task does not compile, upload, reset, connect to an inferior, call a target
function, read MCU memory, change firmware/configuration/pins/credentials or run
motors. It supplies no runtime report, loaded execution, timing benefit,
coherent capture, live RAM/stack/WCET, physical acceptance, motor permission or
human phase gate. No new executable or device operation occurred during
preparation of this contract and its data binding.
