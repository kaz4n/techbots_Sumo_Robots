# D217 fixed B4 application file-only entry inspection

26 September 2026. Fixed engineering scope under D051: reuse accepted D210 entry
inspection for the accepted D214 B4 app M0 artifact and D215 file-only ABI.
This is a file observation preparation, not upload, reset, MCU memory capture,
motor permission, physical acceptance or a phase gate.

## Fixed evidence and public interface

Subject: `state/analysis/P7_b4_app_compile_raw/inspect_static_entry.py`.
Binding: `state/analysis/P7_b4_app_compile_raw/entry_binding01.json`,
78168 bytes / fb2ab19d0cd0337f7d74a9578eee58d2e0029bf8a45ad6851a9ddbf558c79d55.
The binding is normative data: complete current symbol rows, exact ordered
ranges/aliases, initialization bounds, source/profile/artifact pins, every
projection operand/count/intermediate identity and the inherited limits.
No runtime symbol, owner, profile or range selector is added.

D215 actual review is FINAL PASS, 5715 bytes /
c7fe6fe9b0629e65548e69eb7aa66a94cbda3bf9da5f5e13baeaa18be32902b6.
Its saved ABI is 293222 bytes /
25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc.
The checked source hash remains
9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.
The inherited B4 compiler admission enforces app.ino, static/default startup,
MATCH0, MOTORS_ALLOWED0, SUMOX_B4_STAND1 and the seven other explicit profile/
probe macros zero. All seventeen checked-in setup grants remain zero.

Public functions remain `load_reader(*, root=ROOT)`, `project_reader(raw)`,
`project_parser(raw)` and `main(argv)`. The loaded reader exposes StaticEntry.
CLI is exactly `--check-only|--execute --reviewed-head <40lowerhex>`, requiring
Python -B. The returned reader retains its inherited admission/check/execute
interfaces; query and summary signatures remain `queries(reader)` and
`summarize(result, layout)`. Summary remains exactly status, initialization,
disassembly and limitation, with status STATIC_ENTRY_OBSERVED.

The build owner is /home/arduino/sumox26_codex_build/b4-app-m0-static01.
The fresh local output is RAW/native_entry_static01. The fresh remote scope is
/home/arduino/sumox26_codex_build/b4-app-m0-entry-static01, absent-only and never
created by this file-only helper. Consumed result owners are never reused.

## Exact reuse and bounded changes

Use accepted D210 inspect_static_entry.py as the direct wrapper predecessor.
Use accepted D215 inspect_static_abi.py as ABI loader. Preserve require, _stamp,
_plain_chain, _read_handle, pinned, _verify, _project, project_reader,
project_parser, _module and main byte-for-byte. load_reader changes only its two
private module labels from _sumox_d210_entry_abi/parser to
_sumox_d217_entry_abi/parser. Constants and the three introductory comments may
change to current paths, identities and recorded projection tables.

Before any private source execution, pin the D210 wrapper predecessor and the
eight D210 role-equivalent inputs in ORIGINALS: D215 ABI source, actual local
closure, layout, raw result, actual review, D214 artifact packet, historical
entry parser and this fresh binding. Then pin this complete contract. Retain
all deeper D215 input pins and inherited compiler/artifact admission; add current
wrapper pins to the loaded reader. No historical source is edited.

project_reader takes D215's private projected 13204-byte reader
069af034c960acc478b11ec8c516da58121a8adf2d936531309d298d7ca3feba.
Apply exactly the nine binding steps, counts 1,1,1,2,1,1,1,1,2, producing
13226 bytes / 5df04ffc6c532d236006bb67bfa772493d8b2dc165b5523e4777300a04f0bba9.
These rename the wrapper/output/scope/status/class at the accepted D210 seams;
D215_STATIC_FILE_ONLY_ABI becomes D217_STATIC_FILE_ONLY_ENTRY. All reader
algorithms, descriptors, bounds, child handling and closing checks are retained.

project_parser takes the unchanged historical parser
state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py,
10317 bytes / cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34.
Apply exactly the nine binding steps, all count1, producing 14256 bytes /
dd011caad902b86cc6e47fded3be1695e4a96f84581e6a654acf38a2c96a1bfc.
Relative to accepted D210, only the build path, whole RANGES/BOUNDS literals
and three initializer-address contexts change. The three LOCAL labels, eleven
WEAK labels and expected pointer 0x08100101 remain identical. No parser
algorithm, assertion or failure path changes.

## Exact observation scope and interpretation

Consume the complete fresh 2037-row symbol census before selecting the existing
64 groups and 77 exact aliases. Every selected alias is unique FUNC/DEFAULT/
section1, with its observed binding, Thumb symbol value and exact size. Thirteen
constructor C1/C2 pairs retain identical values/sizes/classifications. Ranges
total 10488 bytes. Four groups grew: Robot constructor1440->1484, RobotResult
constructor192->208, Transaction::applyDecision288->292 and MotorGate::apply
248->252. No address is extrapolated from a preceding image.

The four children remain readelf --version, gdb --version, readelf -hSWs -x
.init_array against the fixed ELF, and fixed GDB disassembly against its debug
ELF. GDB has exactly129 expressions: marker plus disassembly for each64 groups,
then SUMOX_ENTRY_END. Keep file-only GDB options, no auto-load and no inferior
calls. The existing exact opcode coverage and symbol predicates remain.

Initialization section2 is [0x081131e4,0x081131e8). Preinit and static-thread
ranges are empty at0x081131e4. Pointer0x08100101/bytes01011008 are expected from
the observed global-initializer symbol; contents remain unobserved until this
entry query. Data copy is208 bytes from0x08114310 to0x20013890.
Zero-BSS is[0x20013960,0x2003c718),167352 bytes. Preserve the distinction between
these zeroing bounds and the larger allocated BSS section.

Claims remain selected startup, binding, construction, zero-grant setup,
continuous dispatch/completion, M0 motor gating and fault cleanup. This is not
a closed B4 call graph. The seven new stand function ranges are deliberately
excluded; B4 routing/governor/lifecycle interiors retain source/host evidence.
Missing standalone Sequence/Report constructors and terminate functions do
not prove absent work or inlining. Inspect B4 defaults through the selected
enlarged Robot/RobotResult constructors and initialized BSS. Firmware still has
no diagnostic Runner, Trace, SETTLE report, snapshot freeze or finite-loop exit.

Retain one transport, four children,60s child deadlines,5s reap allowance,
1MiB per child stream,8MiB reply,400s transport,30000 Windows UTF16 units
including NUL,128MiB local free space, twelve remote file closes plus board
identity, and local closing verification. No limits are expanded.

## Verification boundary

Seal wrapper and derivation identities before reading the independent new
oracle. Independently check the binding and unchanged bodies, then use focused
fixtures for current/stale range and initializer rejection, B4 admission, fixed
commands and closure. No repeated historical full native test campaign is
required. Root controls first host tests, separate review/admission and any
single file-only native attempt. The implementation author performs no subject
imports, tests or device actions.

