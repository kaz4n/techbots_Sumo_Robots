# D205 entry contract and data-derivation review

26 September 2026, Asia/Dubai. Separate fresh-context, same-model reviewer.
This is a bounded preparation review of the contract, binding and derivation,
against accepted D204 evidence and pinned historical sources. It is not a
review of an implemented successor, host results or a native entry attempt.
Only this review file was written.

**PREPARATION PASS. No open material finding in the reviewed contract and
data-only recipe. Implementation, independent oracle, source/host review,
fixed-scope admission and actual instruction review remain pending.**

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
