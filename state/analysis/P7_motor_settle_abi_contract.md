# D199 file-only native SETTLE ABI observation

26 September 2026. Prepare one new ABI wrapper for the checked D198 image,
then obtain its actual symbols before fixing an entry observation. The image
uses the unchanged app_motor_observe sketch with D197's separate diagnostic
report, static/default/MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1.
This work observes files; it neither reads MCU memory nor runs the image.

Add only state/analysis/P7_motor_settle_compile_raw/inspect_static_abi.py for
the executable ABI subject. Reuse the reviewed D194 ABI02 lifecycle through
private composition. Preserve every historical source, oracle, failure,
receipt and consumed owner. No firmware, pin, configuration, native timing
limit, compiler, upload, reset, credential or motor-control change is included.
The later entry subsection is deliberately conditional on this actual ABI.

## Fixed evidence and artifact binding

The D198 result is COMPILE_CHECKED with one query, one compiler, no first error
and all eight final checks PASS. Its source is
117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da;
boot is 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8; serial is 2629958581.
The reviewed compile HEAD is 18c1135c5b4602405fdcffa3c7d6fe3dbcd38490.
These are compile facts, not new ABI or entry observations.

The new wrapper's ORIGINALS table checks these five complete inputs before
any private source execution. Pin this contract's final SHA separately.

| Input relative to repository | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py | 8219 | a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421 |
| tools/compile_motor_settle_probe.py | 7570 | b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62 |
| state/analysis/P7_motor_settle_compile_raw/inputs_static.json | 13432 | aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/result.json | 1608 | 9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json | 9648 | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 |

The exact129-input compile manifest already binds D197's HAL
f1ee755a7bddec38e86545f4c5e5457b3ed5e5f1bdd7f5cf368cc77f91664f5e
and new header
2eced554fce20ff938daf44866ee0bad6d99fa28e377af762bb0f037376b75a8.
Do not substitute the old observer source or manifest. Retain the complete
artifact packet and its checked package/TLS validator result, including:

| File under app-motor-settle-static01 | Bytes | SHA256 |
|---|---:|---|
| build/app_motor_observe.ino.elf | 172840 | 6091f27dbd136e0a694900bc68507b1cc6806073c6bfd50f5e57d892df6daeb9 |
| build/app_motor_observe.ino_debug.elf | 1839060 | dc610650600803c9e36c141e300cdcec478af4f03f4a350669ebe0a4699877b7 |
| build/app_motor_observe.ino_temp.elf | 1839060 | dc610650600803c9e36c141e300cdcec478af4f03f4a350669ebe0a4699877b7 |
| build/app_motor_observe.ino.bin | 95504 | d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc |
| build/app_motor_observe.ino.bin-zsk.bin | 95520 | e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 |
| artifacts/app_motor_observe.ino.bin-zsk.bin | 95520 | e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 |
| build/app_motor_observe.ino.elf-zsk.bin | 172840 | eca3493c47b494a52c645f57a8034685a27a965ed749d09cd5ba4624cdd1ec7a |
| build/app_motor_observe.ino.map | 452000 | 914eb508828e1d73ce08d12e08be03315056736f4dc4b4194101c7912a84ff42 |

The build owner is /home/arduino/sumox26_codex_build/app-motor-settle-static01.
The checked .bss is NOBITS at536951136 with171680 bytes/alignment8; the actual
zero-initialized subrange is [536951136,537121800),170664 bytes. Use the
artifact packet for these bounds. The larger section is not interchangeable
with the initialized subrange. No report address or function range is assumed.

Retain every inherited original pin, including the repaired ABI wrapper
497f756e4eab440d659a4d26ef38ec8d92abdd9f92a5938d1da04705745f42d5,
original16600-byte reader
0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c,
5928-byte readelf normalizer
6a990871af18ca8bc5d10f9d11efda4619052bf1de5ab272188de746f95dad21,
and the consumed ABI01 failure provenance checked by ABI02. Historical D193
inputs remain provenance dependencies of those unchanged wrappers; their
artifacts do not substitute for D198's current packet.

## Public interface and bootstrap

Public functions are project_reader(raw), settle_expressions(),
summarize(result, layout, *, summary), load_reader(*, root=ROOT), and main(argv).
ROOT is this repository. Import defines only: no input reads, subprocess,
device action, module registration, owner creation or bytecode side effects.
Main validates an exact list of exact strings:
--check-only|--execute --reviewed-head <40 lowercase hex>, then Python-B,
before reading inputs. No configurable target, type, path, owner or profile.

Copy exactly ABI02's source bodies for require, _stamp, _plain_chain,
_read_handle and pinned. They must protect loading the original wrapper, not
be obtained by executing an unchecked source. Preserve ordinary ancestry,
single-link local input and reparse checks, O_NOFOLLOW/O_NONBLOCK, descriptor
admission before reading, same-API stamp stability, size/hash bounds, close
behavior and primary-error preservation. Retain the exact Windows executable
pathname0111 adjustment and cross-API ctime exception; no broader mode mask.
Do not import the unrelated admission observer's installed-compiler hardlink
semantics into this production local-input bootstrap.

load_reader verifies all five ORIGINALS hashes and lengths and this contract
before executing the checked ABI02 definitions in a fresh private ModuleType.
Use the original absolute __file__; never __main__ or sys.modules. Save its
project_reader and privately replace it with composition that calls that
saved projector first and D199 project_reader second. Then invoke the
unchanged ABI02 load_reader(root=root). Its original-first nested loading,
repaired bootstrap, normalization and current polls-type guard remain intact.

Inject settle_expressions into the returned reader's private namespace before
queries or owner preparation can occur. Copy HARD_PINS and extend it with all
five new input pins and this contract; preserve inherited entries. SELF names
the new ABI wrapper and is bound through reviewedHEAD, without a self-hash
cycle. Save the returned ABI02 summarize, then replace it with a wrapper
calling this contract's summarize(..., summary=saved_summary). No class,
transport, claim, prepare, execute, closure or historical main implementation
is copied or replaced. Main delegates once to the returned reader's main.

## Exact projected reader

project_reader accepts exact bytes only:16937 bytes, SHA256
b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981.
This is the output of the original-first D194 ABI02 projection, not the
original on-disk reader or an already transformed D199 reader. Apply only
these ordered substitutions, requiring each occurrence count:

| Old literal | New literal | Count |
|---|---|---:|
| P7_app_motor_observe_compile_raw | P7_motor_settle_compile_raw | 1 |
| '/inspect_static_abi02.py' | '/inspect_static_abi.py' | 1 |
| tools/compile_app_motor_observe.py | tools/compile_motor_settle_probe.py | 1 |
| 'native_abi_static02' | 'native_abi_static01' | 1 |
| app-motor-observe-abi-static02 | app-motor-settle-abi-static01 | 1 |
| app-motor-observe-static01 | app-motor-settle-static01 | 1 |
| D194_STATIC_FILE_ONLY_ABI02 | D199_STATIC_FILE_ONLY_ABI | 2 |
| 3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0 | 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da | 1 |
| 70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827 | b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62 | 1 |
| aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e | aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 | 1 |
| 24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b | 9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5 | 1 |
| 5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 | 1 |

Then replace the unique bytes:

```python
'countdown::Result', 'report_.polls')
```

with exactly these two lines, retaining nine leading spaces on the second:

```python
'countdown::Result', 'motors::SettleProbeSample',
         'motors::SettleProbeReport', 'motors::SettleProbeReason', 'report_.polls')
```

Finally replace the unique complete line, including its four leading spaces
and LF, `    build = OWNER + '/build/app_motor_observe.ino'` with:

```python
    expressions += settle_expressions()
    build = OWNER + '/build/app_motor_observe.ino'
```

Require exactly17061 output bytes, SHA256
67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6.
This hash was calculated from count-checked bytes without executing a reader.
Reject input type, size, hash, occurrence or final-identity changes. Never
write the projected bytes over an original file.

## Fixed queries and numeric report evidence

Keep four file children: pinned readelf --version, pinned gdb --version,
readelf -hSWs on the fixed new ELF, and the existing guarded GDB command on
its debug ELF. Keep GDB no-autoload/no-function-call flags unchanged.
The23 SIZE/ALIGN/LAYOUT subjects are the existing20 with the following
three types inserted in order immediately before report_.polls:
motors::SettleProbeSample, motors::SettleProbeReport, motors::SettleProbeReason.
The terminal bool subject and all11 Runner-window OFFSET queries remain.
Thus report_.polls still has the exact contiguous unsigned-int layout block
immediately followed by SUMOX_SIZE bool; its ALIGN uses observed unsigned int.
Retain fsm::PreviousTick and every existing Runner window, including the live
previous window. This ABI task does not choose a later capture window set.

settle_expressions() returns a fresh exact list of62 strings, in the order
below. Append them after all inherited Runner OFFSET queries. There are
223 total GDB expressions: original143 + three subjects18 + extra62.
No expression calls a function, dereferences target memory or connects to an
inferior. Only file type/symbol information and null-based member expressions
are used; no member-expression alignof is introduced.

For each field row, T is its type, M its member, and key is T + '.' + M.
Emit these four strings in order (the echo strings end in literal backslash-n,
as do the inherited query strings):

```text
echo SUMOX_FIELD_OFFSET <key>\n
p/d (unsigned long)&((<T>*)0)-><M>
echo SUMOX_FIELD_WIDTH <key>\n
p/d sizeof(((<T>*)0)-><M>)
```

| T | M | Required observed offset | Required observed width |
|---|---|---:|---:|
| motors::SettleProbeSample | elapsed_us | 0 | 4 |
| motors::SettleProbeSample | poll_index | 4 | 4 |
| motors::SettleProbeSample | reason | 8 | 1 |
| motors::SettleProbeSample | fresh_mask | 9 | 1 |
| motors::SettleProbeSample | valid | 10 | 1 |
| motors::SettleProbeSample | reserved | 11 | 1 |
| motors::SettleProbeReport | current | 0 | 12 |
| motors::SettleProbeReport | first_failure | 12 | 12 |
| motors::SettleProbeReport | has_current | 24 | 1 |
| motors::SettleProbeReport | has_failure | 25 | 1 |
| motors::SettleProbeReport | reserved | 26 | 2 |

Then for each enum row emit `echo SUMOX_REASON <name>\n` followed by
`p/d (unsigned int)motors::SettleProbeReason::<name>`:

| Name | Required observed value |
|---|---:|
| NONE | 0 |
| SUCCESS | 1 |
| NULL_CONTEXT | 2 |
| PRECONDITION | 3 |
| INITIAL_BANK | 4 |
| POLL_DEADLINE | 5 |
| POLL_BANK | 6 |
| FINAL_DEADLINE | 7 |
| POLL_LIMIT | 8 |

Numeric field and enum answers must be observed, not supplied from these
expected-value tables. Missing optimized debug information or GDB errors fail
with raw evidence retained; do not suppress stderr or silently replace an
unsupported query with its expectation.

Do not query the unused inline constexpr SETTLE_ELAPSED_VALID,
SETTLE_POLL_VALID or SETTLE_FRESH_VALID objects. The pinned D197 header defines
their source semantics as1,2,4 respectively, with allowed mask7; these are not
target-observed ABI values and do not appear in the ABI summary. The actual
D197 implementation does not reference those named constants, so the D198
-g/-Os build does not guarantee their debug visibility. Their absence has not
been observed or asserted. This restriction was agreed before implementation
or native ABI execution, not as a fallback after a failed target query. The
actual Sample.valid field's offset10 and width1 remain required observations.

## Pure additional summary and separate global object

summarize(result, layout, *, summary) accepts an exact dict with exactly four
dict command records, an exact dict layout, and a callable summary. Decode
command2 readelf and command3 GDB stdout from validated Base64/UTF8. Never
alter caller-owned result/layout or their raw encodings. Delegate exactly once
to the saved ABI02 summary on independent deep copies; require a dict result.
Retain all returned fields, normalization evidence and polls-type evidence.
The inherited normalized summary still validates the diagnostic object, all
23 sizes/alignments,11 windows, static ELF and initialized BSS containment.
The execution lifecycle, not this pure wrapper, retains full command/stream
accounting and returncode/stderr/finalization checks.

Require target-observed Sample size12/alignment4, Report size28/alignment4,
Reason size1/alignment1, all eleven field offsets/widths and all nine enum
values exactly as above. Use unique numeric tagged
answers, with the complete new marker sequence in exact query order. Reject
missing, extra, duplicate, reordered or malformed new tags, negative or
noninteger values, and mismatches. Preserve all ptype blocks in raw output for
the separate target-layout review; host static_asserts are not target evidence.

Find the emitted motors anonymous-namespace settle_probe_report entity in the
current readelf symbol table. Its nominal mangled identifier is
_ZN6motors12_GLOBAL__N_119settle_probe_reportE. Require exactly one row for that
complete identifier, with OBJECT/LOCAL/DEFAULT and a numeric section index.
The symbol name and address returned in the summary must come from that
observed row. Do not synthesize an address, demangle another object into its
place or broaden the selector if the expected entity is absent. Parse both
decimal and0x symbol sizes; duplicate rows with conflicting kinds/bindings
must fail, rather than being filtered away by an OBJECT-only regex.

Require its size to equal the newly observed28-byte Report size, address
alignment4, and section to be the same checked .bss NOBITS section observed
for the Runner. Verify the readelf section address/size against the checked
layout again. The whole object must lie in bss_zero, not merely .bss, and its
half-open address range must not intersect the diagnostic Runner object's
range. Do not add it to Runner.windows or assign it a Runner-relative offset.
No retained accessor symbol is required: the report may be observable through
its emitted stores even when settleProbeReport() is garbage-collected.

Return all saved-summary fields plus exactly one new key, settle_probe:

```text
{
  symbol: <observed complete name>, address: <observed integer>,
  bytes: 28, alignment: 4, section: <observed integer>,
  fields: {<T.M>: {offset: <observed integer>, bytes: <observed integer>}, ...},
  reasons: {<enum name>: <observed integer>, ...}
}
```

Each nested mapping has exactly the ordered keys in its table. The inherited
status remains STATIC_ABI_OBSERVED and its file-only limitation remains. This
does not claim RAM contents are zero now, that publication executed, or that
the first-failure guard works on hardware. The checked zero-BSS interval is
initialization file evidence; actual instruction review remains separate.

## Attempt, tool and closing boundaries

Use local owner P7_motor_settle_compile_raw/native_abi_static01, distinct from
the consumed native_static01 compile owner and every D194 owner. Require absent
remote scope /home/arduino/sumox26_codex_build/app-motor-settle-abi-static01;
the inherited file-only reader does not create that remote scope. Four file
children are executed at most once; any failed/partial local attempt is
consumed and its first failure remains evidence. No automatic retry/repair.

Preserve readelf SHA
c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e
and GDB SHA
8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778,
the installed loader/TLS pins, ADB and all original helpers. Preserve the
clean reviewed HEAD, exact local/source/artifact pins, fixed board identity,
60s child/5s reap/1MiB streams,400s transport,30000 UTF16 command units and
128MiB local-space minimum. Retain the complete13 remote closing checks,
independent local closure, first-error and evidence-write-error behavior.
The new compile manifest/path/schema are validated by the actual projected
D198 compiler owner; do not bypass its admission or artifact validator.

--check-only remains local read-only preparation with no owner claim or board
dispatch. --execute invokes only the four allowed ELF-file commands, not the
compiler or any target/MCU operation. Save original transport/stdout/stderr and
result.json before parsing, then abi.json and independent local_result.json.
Preserve raw readelf bytes: any decimal/hex normalization operates on copies.

## Independent tests and first execution

Freeze the new independent oracle before its author reads the implementation.
Keep all historical sources/tests/assertions and first failures unchanged.
Relevant historical suites are the44 base ABI,14 Windows mode and21 ABI02
methods; the19 entry methods remain future entry provenance. Their old fixed
projection/owner/type-count assertions describe D194, not this new target.
Do not claim a historical-only result proves D199. A bounded current-target
suite may privately reuse assertion bodies with explicit checked fixture
metadata and an extended synthetic packet, recording the selected method
names and every fixture projection in its freeze. Do not weaken assertions.

In particular, reuse applicable bootstrap, Windows mode, strict ABI numeric/
window parsing and real prepare/execute/closure assertions. Replace neither
production lifecycle methods nor failures with success-only mocks. Add new
tests for the exact14-step projected identity, original-first private
composition, all-input checks before private execution, new SELF/pins/owners,
four commands/23 subjects/223 expressions, exact field/reason tags,
polls contiguity, observed separate object and decimal/hex size forms.
Exercise wrong/duplicate/missing binding/kind/name/section, size/alignment,
zero-BSS edge cases and Runner overlap, every numeric mismatch, raw/layout
preservation including an injected mutating summary, and first-error plus
independent closing/write failures. Query syntax must match this contract;
fixtures must not infer addresses from this repository's old ABI packet.

Use unrelated well-aligned synthetic report addresses wholly within fixture
zero-BSS for host tests. Preserve the eleven Runner windows and nested
pre-abort PreviousTick. New tests must exercise the actual projected D198
compiler/manifest packet at preparation, including old D193 packet refusal.
Run Windows and Linux serially after freeze, preserve first failures and all
input hashes, and obtain source/host review before the one native ABI attempt.
Unexpected fixture or subject failures require explicit adjudication; this
contract does not pre-authorize a test repair or query-error suppression.

## Follow-on entry observation after actual ABI

Do not implement or execute entry observation from guessed D194 addresses.
First close the actual D199 ABI raw result, summary, independent local closure
and target-layout review. From that exact raw symbol table, prepare a compact
fixed entry binding listing current names, aliases, binding/type/section,
Thumb addresses, sizes and ranges; pin all three ABI receipts and the binding.
Freeze that entry binding and its independent oracle before entry source use.
This is a continuation of D199 file evidence, not a new firmware experiment.

Reserve local owner P7_motor_settle_compile_raw/native_entry_static01 and
absent remote scope /home/arduino/sumox26_codex_build/app-motor-settle-entry-static01.
Use the historical entry parser/lifecycle and preserve its27 groups and both
constructor aliases with newly observed ranges. Add only the emitted
UnoQPort::settle and publication/sample-copy path needed to inspect D197.
If publication or sample copying is inlined, cover the containing function's
actual complete range rather than requiring a nonexistent helper symbol.
Accessor retention is optional. No generic symbol selector or arbitrary
range CLI is introduced; names/ranges become fixed evidence after ABI.

Retain .init_array contents/bounds and pointer validation, exact marker/order/
opcode-width/contiguous-disassembly checks, static .text containment, raw block
hashes and decimal/hex size support. Separately review emitted instructions:
stores must reach the actual28-byte object; sample fields precede their
presence flag; first_failure publication stays behind its lifetime guard;
initialization is consistent with zero-BSS and adds no dynamic initializer.
Preserve original entry/Runner construction, inert grants, bounded polls,
pre-abort snapshot and terminal passivity review. Parser acceptance is not
that semantic review and does not establish runtime behavior.

The read-only capture plan4ca7a96ddf71fb4db77729e8f33cd7f75b14c6fa319e46716ef7e5114c45b531
remains later planning: replacing a live previous window with this report,
field-map/caller/remote changes, finite waits, flash brackets and new cleanup
ownership are outside this contract's ABI implementation. Preserve
coherence=UNPROVEN and all loss fields in any later capture. No cause, repair,
live RAM/stack/WCET, electrical qualification, motor permission or human gate
is established by the file observations specified here.
