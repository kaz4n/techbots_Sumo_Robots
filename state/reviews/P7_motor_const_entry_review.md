# D205 entry contract, source and host review

26 September 2026, Asia/Dubai. Separate fresh-context, same-model reviewer.
The preparation review below covers the contract, binding and derivation
against accepted D204 evidence and pinned historical sources. The later
source/oracle review follows the recorded independence barrier. The final
section accepts both first host runs. Native entry evidence remains pending.
Only this review file was written.

**FINAL SOURCE/HOST PASS. No open material finding in the reviewed contract,
data-only recipe, implemented successor, independent oracle and first serial
Linux/Windows host results. Fixed-scope admission and actual instruction
review remain pending.**

## Reviewed identities

Paths are repository-relative. Each listed identity was independently checked.

| Input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_const_entry_contract.md | 22163 | 6663d1ea7309c809d8f727fc5bf68291128e54c83ca64b7d1ce53b9ff1cea9d9 |
| state/analysis/P7_motor_const_compile_raw/entry_binding01.json | 44374 | 7417ff7055e30238e8a3231db3287ffb3520ec8929ce3437afbd0dff1c2d60ae |
| state/analysis/P7_motor_const_compile_raw/entry_derivation01.json | 25889 | ae6ef0def959489abd89422044e415fa4f4b63d08d91e55792425d9c4088a02f |
| state/reviews/P7_motor_const_abi_actual_review.md | 10178 | 4cd28fe8ce3b689319da5ddb42739c664fd0e4bcdc2552b521ee23b8b3331411 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/result.json | 904847 | bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/abi.json | 5410 | 6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97 |

All 18 binding preparation pins, 20 derivation input pins and eight proposed
runtime ORIGINALS pins match their current local bytes. The eight artifact
pins independently equal the accepted current D203 artifact packet. The
contract and binding avoid a self-hash cycle; the derivation is not a runtime
input. The draft was committed at 10589780050a1be7708346165064dbb4cfa5b945.

The reviewer read AGENTS.md in full, the current handoff/resume, latest
PROGRESS/DECISIONS, active P7 prompt and schedule. Actual date is 26 September;
schedule dates and software preparation do not create physical or human gates.

## Current evidence and fixed instruction scope

Independent decoding and parsing of the accepted raw readelf stream recovers
158419 bytes, SHA256
5632ddc6fe74d5ec5357e2f43f0a36bb74028232d833d4d2eac4537a319ee163.
It contains one complete .symtab and exactly consecutive rows 0 through 2298.
Parsing did not filter symbol kinds, bindings or visibility before the helper
absence checks. Every saved helper-name inventory row matches those bytes.
candidateRate has neither an exact-name nor a name-token row; candidatePeriod
has its unique 20-byte LOCAL FUNC row at Thumb value 0x08110c91. Absence remains
a symbol-name observation, not proof of instruction removal.

Before reading the new binding, the reviewer independently reconstructed the
proposed groups from historical labels and current raw symbol rows. The result
is exactly 32 groups, 34 aliases, 3834 selected bytes and 65 expressions. The
binding retains all 28 present D199 groups in order and appends timer_valid,
bank_valid, write_pwm and map_channel. Both constructor aliases are preserved.
All 34 exact FUNC rows, Thumb values, sizes, bindings, DEFAULT visibility and
section numbers match the accepted stream. Every range is wholly inside
.text at 0x08100010, size 0x16248.

All six initialization-bound rows match. .init_array is section 2 at
0x08116258 for four bytes; its end is 0x0811625c. The expected pointer
0x08100105 is derived from the unique initializer FUNC symbol. D204 did not
observe the initialization word; this review does not substitute historical
bytes or mark that future requirement complete. The binding's complete
separate SETTLE report object, fields and reasons equal the accepted current
ABI summary at 0x2003d3e8 for 28 bytes.

## Exact recipe and inherited behavior

Data-only reconstruction independently reproduces every intermediate length,
hash and occurrence count in the twelve outer, nine reader and seven parser
substitution sequences. This applies literal byte data without importing,
executing or compiling a subject. The actual new entry implementation file
was neither read nor hashed.

The original-first historical ABI projection chain reproduces the required
17051-byte input, SHA256 938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6.
The proposed final identities are:

| Planned product | Bytes | SHA256 |
|---|---:|---|
| Reader projection | 17075 | 580abb32b2597ceed62dadb6ea28ac028d3ffb66e5e5fa2d0c42a7400ad1b9f3 |
| Parser projection | 10866 | c4c4f9e26b35da497e6a092de361b1727759ea1a16c7026b9242037c0544c90b |
| Prospective wrapper | 14941 | a71eb62496ddedcc4d295579cea383635f309c8394dfd6c9ee32913a7418d835 |

These are independently reproduced recipe outputs, not accepted implementation
or execution evidence. Complete-assignment spans and deterministic rendering
of ORIGINALS, identity tuples and byte replacement tables match the contract.
The parser replaces whole RANGES and BOUNDS assignments, the LOCAL tuple,
three contextual initializer-address sites and the fixed build path. Its
literal ranges/bounds exactly equal the independently checked binding.

Static comparison of the planned parser confirms that only queries, symbols
and initializer differ, solely through the permitted literal replacements.
Every other parser function body is byte-identical. Exact symbol/alias checks,
decimal/hex sizes, initializer word validation, ordered markers, opcode widths,
unparsed-row refusal and contiguous coverage remain inherited.

The pinned predecessor wrapper establishes passive import, strict CLI and -B,
descriptor-based ancestry/single-link/identity checks before private execution,
original-first composition, fresh private module namespaces, copied hard pins
and direct entry queries/summarize replacement. The recipe leaves that logic
unchanged except two private namespace literals. No new selector, arbitrary
address, fallback parser, source loading path or native operation is introduced.

The original-first paragraph's prohibition on historical load/main entrypoints
is read as prohibiting the historical entry parser's literal load()/main()
and unprojected file-operation entrypoints. It does not prohibit the accepted
private ABI load_reader() chain, which the next paragraph explicitly requires,
or final projected reader.main delegation. Root and reviewer agreed on this
literal-name interpretation before adoption/oracle freeze. It requires no
contract hash, recipe, source or lifecycle change.

The fixed future operation retains four file children, current raw/debug ELF
bindings, fresh local owner and absent remote scope, 12 remote file pins,
13 remote closing checks and independent local closure. Clean reviewed HEAD,
128 MiB local guard, bounded children/reap/streams/transport, raw-first saving,
first-error precedence and failed-owner consumption remain required.

The separately prepared outer host driver at
state/analysis/P7_motor_const_compile_raw/entry_host_driver01.py is 3502 bytes,
SHA256 e1c5c7252d98658700c4e7a96871af257d86fdbb098bb8c0c484ce543bacd048.
Independent byte reconstruction confirms exactly five single-occurrence
metadata substitutions from accepted ABI host driver 682516a46e11b6bf0ae38bbc356eb5721af51d3d3375c113448319fa27be40d3:
comment D204 to D205, freeze basename, exclusive owner prefix, selected suite
basename and invocation schema. Every other byte is unchanged. It retains
opening/closing pin checks, isolated -I/-B execution, dedicated Windows TEMP
beneath the new owner, Linux /dev/shm fixtures, 360-second subprocess bound,
exclusive intent/stdout/stderr/result files and first-result preservation.
The reviewer did not execute the driver; eventual coordinator freeze and host
receipts must still establish the actual selected suite and completed closure.

## Remaining acceptance boundary

The independent oracle must freeze before its author reads the successor and
before anyone executes it. Root and reviewer must await its FINAL barrier
before inspecting the actual new subject. The historical 23 methods require
explicit, independently derived fixture adaptations and supplements; their
past passes do not validate D205. This preparation review ran no oracle, test,
subject import/execution, compiler, ADB/device operation or cleanup.

After implementation and host closure, separate scope/admission review and
clean committed HEAD/check-only must precede any single file-only attempt.
Actual instructions must then establish the selected constant-selection,
publication, live-check, deadline/poll, startup and terminal behavior. Symbol
absence and parser success cannot establish those semantics, eliminated
division, measured speedup or a SETTLE remedy. A later inhibited runtime
attempt remains separately scoped and reviewed.

D201 remains the latest flashed image. No runtime report, loaded execution,
coherence, RAM/stack/WCET measurement, physical acceptance, motor permission
or human phase gate follows from this preparation PASS.

## Source and independent-oracle follow-up

D205 was adopted at d9753932f9c6abd8dc2a0c00a68d3f58d903f68d. Root explicitly
announced the independent oracle FINAL barrier before this reviewer's first
read/hash of the actual new reader or implementation receipt. The independent
freeze declares zero author reads/hashes/imports/executions of that subject;
the actual subject is deliberately absent from its pin set. This reviews a
recorded independence boundary, not an externally attested private state.

| New reviewed item | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_const_compile_raw/inspect_static_entry.py | 14941 | a71eb62496ddedcc4d295579cea383635f309c8394dfd6c9ee32913a7418d835 |
| state/analysis/P7_motor_const_compile_raw/entry_implementation01.json | 23581 | 63280104aa3697a7c8e27e51af9844b11cfc7a9eca853d98890cdb1611d6df9f |
| tests/tooling/test_motor_const_entry.py | 16089 | daf208faa96fd326676b34515bb23628333507121bdfd5b196474ddbc7c191ed |
| state/analysis/P7_motor_const_compile_raw/entry_fixture_derivation01.json | 40005 | 7e699de06f8a37313fb614aedcbfff4d9fb09cfedba6b9bb855135ca84d52918 |
| state/analysis/P7_motor_const_compile_raw/entry_independent_freeze01.json | 50828 | 16402cc8ba0df65e37f4fc3c696168b247252db46c0bce9c1efa670ffeb7fdbc |

All 260 independent-freeze pins and 21 implementation-receipt input pins were
independently rehashed and are exact. Full data-only replay of the adopted
twelve substitutions equals every byte of the actual new reader. All twelve
function names remain; eleven complete function bodies are unchanged, and
load_reader changes only the two permitted private namespace literals. The
five descriptor bootstrap bodies also equal accepted D204 ABI source bytes.
The actual load_reader retains all input checks before private execution,
original-first composition, copied hard pins and direct parser query/summary
replacement. No source execution or import was used for these comparisons.

The oracle applies 24 explicit, count-checked private substitutions to D199's
entry oracle and twelve to its earlier EntryContract fixture class. Independent
reconstruction reproduces each recorded intermediate identity and both final
private fixture identities. All 23 historical test names and 119 assertion or
rejection call sites remain. These are static call-site counts, not executed
assertion totals. Metadata/schema updates retain the old predicates and make
the out-of-range marker 32, which remains invalid beside valid markers 0-31.
The older method name saying twenty_nine is preserved provenance; its current
assertions require 32 ranges and 65 expressions.

The ADDED fixture expands exact-symbol and malformed-disassembly mutation
coverage from publisher/SETTLE to include current candidate_period and all
four added consumers. The retained constructor alias, initializer, scope,
stream, owner, error and closure negatives remain active. The historical
direct-summary sentinel still rejects inherited ABI summary use or ABI tags.

Seven supplements add 64 independently counted assertion/rejection call sites:
exact wrapper/reader/parser recipes and unchanged functions; every replacement
count; complete symbol census and fixed groups; exact stale D199 input refusal
before private execution; stale manifest/outcome/artifact refusal; old
owner/source/scope refusal; and each of thirteen remote closing-row failures.
Real admission/prepare and execute paths are retained with controlled file
and transport fixtures; returned success alone is not the assertion. Failure
cases require raw-first saving, FAILED closure and no accepted entry summary.
The test loader explicitly selects all 23 retained methods plus seven new
methods, exactly 30, with no planned platform skips.

The reviewer ran no oracle or host driver. The following section closes the
root-owned serial Linux/Windows results, coordinator pins and fixture evidence.
Actual instructions and any later runtime operation remain outside this review.

## First serial host results and final closure

The coordinator freeze is 44433 bytes, SHA256
2e02ce58891fc2a8a5e2b8abc1d25400bb0e92da881da3f20d6f5eff635c4c45.
After both host runs the reviewer independently rehashed all 268 frozen files;
every byte count and digest remains exact. No implementation, oracle, fixture,
guard or assertion change was needed, and no host retry is recorded.

| First host owner | Passed | Skipped | Result bytes | Result SHA256 |
|---|---:|---:|---:|---|
| entry_first_linux01 | 30 | 0 | 846 | b2b5d1b82c0a19dfd0e1777e567f4f06014d9ce9b54c4363cf83f4afc77aaddf |
| entry_first_windows01 | 30 | 0 | 903 | b0de6de95645c351476f38961609253151e3adacec9be9d4986e601160dd3cc4 |

Both owners are under state/analysis/P7_motor_const_compile_raw. Each saved
result agrees with its intent argv, platform, start time, 360-second bound,
temporary-root selection and coordinator-freeze hash. Both exit zero, report
unchanged inputs/freeze and have no timeout. Linux started at
13:39:50.171759+04:00 with outer elapsed 29.065766 seconds; Windows started at
13:40:43.132425+04:00 with outer elapsed 13.270799 seconds. These saved values
establish serial Linux-before-Windows execution.

Both stdout files are empty. Exact raw stderr hashes match their receipts:
Linux 5717 bytes / 9978f7d41457c198953f41bad2ca4ac0c473346b815633589ff0a76281131e71;
Windows 5752 bytes / 5886612e24cf363d993f70a5363563e410b48d9cfab50d87ca8b3332f3625b8f.
Independent text parsing recovers the same 30 unique methods in order: all
23 sorted retained names followed by the seven frozen supplements. Every
method reports ok, each summary says 30 tests and OK, and neither contains
skips, failures or errors.

The reviewer's first read-only stderr comparison assumed LF endings and
stopped on Windows CRLF. Normalizing line separators solely for text comparison
resolved that audit assumption; exact raw-byte hash checks remained unchanged.
No host test, source, fixture, receipt or native operation changed or reran.

Root closing entry_host_closing01.json is 1937 bytes, SHA256
60995dee6b837ff199fdb6f8c2432b4fa9963da5d8a11d7db493bad08a915572.
Its freeze, all eight intent/result/stream identities, method counts/order and
unchanged-pin results independently reconcile with the saved evidence. It
records empty Linux RAM, shared Windows and dedicated Windows fixture
inventories; the reviewer separately checked that the dedicated Windows
directory is empty. The recorded C: free-space observation is 6858928128 bytes.
No manual deletion or reclaimed-size claim is made. The associated validation
document agrees with these results.

Accept the exact reader and these first host results for preparation of a new
fixed file-only entry scope. This review is not native admission. Separate
scope/admission review, clean committed reviewed HEAD, local check-only and
embedded current-file/board checks remain mandatory before one observation.
Actual initializer bytes, emitted instruction semantics, constant selection,
SETTLE repair and timing gains remain unobserved. D201 remains flashed; no
motor permission, physical acceptance, WCET or human phase gate follows.
