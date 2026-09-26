# D194 observer file-only entry observation

26 September 2026. Define one new wrapper at
state/analysis/P7_app_motor_observe_compile_raw/inspect_static_entry.py.
Preserve all existing sources, tests, contracts, receipts and consumed owners.
This contract authorizes preparation of file evidence, not an MCU run.

## Evidence and fixed inputs

ABI02 completed four file children with returncode0, empty stderr, all13 remote
closing checks and local closure PASS. Its raw result is OBSERVED and its ABI
summary/local closure are STATIC_ABI_OBSERVED. The accepted raw readelf stdout
is158577 bytes, SHA256
b3542b0d38be98be71ff1318648b3f1817ce406e9f62cf64e1dcdcc9c0e4fc0b.
It is byte-identical to attempt01's readelf stdout, confirming the previously
extracted27 function groups, aliases, sections and32 address substitutions.
Attempt01 remains FAILED; no failure or receipt is replaced.

| Input relative to repository | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py | 8219 | a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421 |
| state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py | 10317 | cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34 |
| state/analysis/P7_app_motor_observe_compile_raw/native_abi_static02/result.json | 893020 | a5e67635f43b96b813885687fbafe743cfc3ec6a93d089a66453ca574c0676da |
| state/analysis/P7_app_motor_observe_compile_raw/native_abi_static02/abi.json | 3704 | dfc34596b65d3a82e21e28c3acf9fb1535bec2eb3b489d270c593c9fe3eab3a7 |
| state/analysis/P7_app_motor_observe_compile_raw/native_abi_static02/local_result.json | 275 | 3f17b83efc79026b46d519646798f70d9cf898b0c4a0bef2e06e6da4da0e84a7 |

Pin this contract's final SHA256 in the new wrapper. Preserve every inherited
ABI02/D194/D193 source, failure, contract, artifact, tool and boot pin. The new
wrapper's own bytes are bound through SELF and reviewed HEAD, without a recursive
self hash. Fixed D193 build OWNER and artifact identities do not change.

## Bootstrap, interface and private composition

Public helpers: project_reader(raw), project_parser(raw),
load_reader(*, root=ROOT), main(argv). ROOT is this repository. Import defines
only; no input reads, subprocesses, device calls or module registration. Main
requires an exact list of exact strings matching
--check-only|--execute --reviewed-head <40 lowercase hex>, and Python-B, before
any input read. No other CLI profile, target, type, source or owner option.

Copy exactly the source bodies of ABI02's five helpers require, _stamp,
_plain_chain, _read_handle and pinned. These bootstrap checks must verify the
original code before it is executed. Preserve ancestry, regular-file/single-link,
reparse, O_NOFOLLOW/O_NONBLOCK, pre-read descriptor comparison, Windows pathname
execute-bit exception, same-API stability, bounded bytes, hashes, closure and
primary-error handling. Do not copy a transport or attempt lifecycle.

load_reader checks all five input hashes and exact byte lengths, plus this
contract hash, using that bootstrap BEFORE executing any private source. Use
fresh ModuleType namespaces with the original absolute __file__ paths and
private names, never __main__ or sys.modules. Load the unchanged ABI02 wrapper;
save its project_reader and replace it privately with composition that first
calls that saved projector and then this contract's project_reader. Invoke its
unchanged load_reader(root=root). Project/load the pinned historical entry
parser into a separate private module. Never call its historical load or main.

Copy the returned reader's HARD_PINS, extend it with all five inputs and this
contract, and preserve all inherited entries. Replace reader.queries with the
entry module's queries and reader.summarize with its summarize directly. Do not
wrap or call the inherited ABI summary: entry disassembly does not contain its
polls-type/ABI tags. Keep every other reader function and class implementation
unchanged. Main delegates exactly once to this reader's unchanged main.

## Exact reader projection

project_reader accepts exact bytes, requiring16937 bytes and SHA256
b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981.
Apply only the following ordered, count-checked byte substitutions:

| Old | New | Count |
|---|---|---:|
| '/inspect_static_abi02.py' | '/inspect_static_entry.py' | 1 |
| 'native_abi_static02' | 'native_entry_static01' | 1 |
| app-motor-observe-abi-static02 | app-motor-observe-entry-static01 | 1 |
| D194_STATIC_FILE_ONLY_ABI02 | D194_STATIC_FILE_ONLY_ENTRY | 2 |
| STATIC_ABI_CHECKED | STATIC_ENTRY_CHECKED | 1 |
| STATIC_ABI_OBSERVED | STATIC_ENTRY_OBSERVED | 2 |
| 'file-abi' | 'file-entry' | 1 |
| 'abi.json' | 'entry.json' | 1 |
| StaticAbi | StaticEntry | 2 |

Require final16955 bytes and SHA256
93729533a1d02e54f6812142aa94cf38e7a93a04d5e03d8a5fc4902386f6a421.
This changes only entry identity/ownership/output labels. The original ABI
queries/parser remain definitions until replaced by the entry functions above.

## Exact parser projection

project_parser accepts exact bytes, requiring10317 bytes and the cb9ee5bb full
hash above. First replace the following complete build-path literal once:

```
/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino
```

with:

```
/home/arduino/sumox26_codex_build/app-motor-observe-static01/build/app_motor_observe.ino
```

Then replace `15app_motor_fault` with `17app_motor_observe`, exactly6 occurrences.
Then apply the32 fixed hexadecimal byte-literal substitutions below in order.
Every literal includes its `0x` prefix. No arbitrary address arithmetic, generic
symbol selection, alternate ranges or unreviewed replacement is accepted.

| Old | New | Count |
|---|---|---:|
| 0x08103b58 | 0x08103b5c | 2 |
| 0x08103bb0 | 0x08103bb4 | 2 |
| 0x08103c08 | 0x08103c20 | 2 |
| 0x08103c94 | 0x08103cac | 2 |
| 0x08103d24 | 0x08103d3c | 2 |
| 0x08103d78 | 0x08103d98 | 1 |
| 0x0810c760 | 0x0810c780 | 1 |
| 0x0810c774 | 0x0810c794 | 1 |
| 0x08110bfc | 0x08110c1c | 1 |
| 0x08110bfe | 0x08110c1e | 1 |
| 0x08110c70 | 0x08110c90 | 1 |
| 0x08110cd8 | 0x08110cf8 | 2 |
| 0x08110d10 | 0x08110d30 | 1 |
| 0x08110ed8 | 0x08110ef8 | 1 |
| 0x08110f64 | 0x08110f84 | 1 |
| 0x0811326c | 0x0811328c | 1 |
| 0x08113290 | 0x081132b0 | 1 |
| 0x08115bec | 0x08115c0c | 1 |
| 0x08115c7c | 0x08115c9c | 2 |
| 0x08115cfc | 0x08115d1c | 1 |
| 0x08115f6c | 0x08115f8c | 1 |
| 0x08115f74 | 0x08115f94 | 2 |
| 0x08115f7c | 0x08115f9c | 1 |
| 0x0811602c | 0x0811604c | 1 |
| 0x08116036 | 0x08116056 | 1 |
| 0x08116044 | 0x08116064 | 1 |
| 0x08116046 | 0x08116066 | 1 |
| 0x08116048 | 0x08116068 | 1 |
| 0x08116074 | 0x08116094 | 2 |
| 0x081160e0 | 0x08116100 | 1 |
| 0x08116218 | 0x08116238 | 4 |
| 0x0811621c | 0x0811623c | 1 |

Require final10333 bytes and SHA256
6a82a9e5381aace9375673678bd763db95f93ad5de6d90d8d26abea2e2852767.
No parser logic is changed. Historical loader constants/functions are unused
definitions; no call to historical load/main is permitted. No source projection
is written back to any original file.

## Bound file queries and interpretation

Reuse exactly four entry commands: pinned readelf --version, pinned gdb
--version, readelf -hSWs -x .init_array on the fixed D193 observer ELF, and the
existing guarded GDB helper on its debug ELF with27 marker-delimited
disassemble /r ranges. Retain GDB no-autoload/no-function-call settings.

The accepted readelf establishes .text section1 at0x08100010, size0x16228,
and .init_array section2 at0x08116238, size4. Function groups remain the original
27 labels in the same order: entry_point, setup, loop, global_initializer,
app_dump_port, sources_port, sources_adc_port, runner_constructor,
runner_application_valid, runner_stop_reason, runner_freeze, runner_begin,
runner_poll, dump_port, loop_hook, candidate_rate, candidate_period, motor_port,
power_reader_port, trace_constructor, trace_port, memcpy, memset,
unsigned_divide, init_variant, main, start_static_threads. Retain both C1/C2
aliases for the two constructors and all original binding/type/Thumb checks.
Only the Runner namespace changes; shared motor_fault::Trace aliases do not.

__init_array_end is0x0811623c; __init_array_start, __preinit_array_start/end and
__static_thread_data_list_start/end are0x08116238. Preserve the original exact
LOCAL/GLOBAL NOTYPE tuples and section2 binding. The initializer FUNC symbol
remains0x08100105. ABI02 did not dump .init_array contents: the new entry query
must observe its single little-endian word and confirm that pointer; do not
claim it has already been observed.

Retain decimal/0x readelf size parsing, exact symbol tuples, .text containment,
initialization section/bytes/bounds, ordered unique markers, exact range
headers/end markers, recognized opcode widths, contiguous instruction coverage
and raw block hashes. Preserve raw result bytes. The inherited entry summary
returns STATIC_ENTRY_OBSERVED with initialization/disassembly fields and its
explicit file-only/semantic-review-pending limitation. Follow with a separate
instruction review of entry wiring, construction, inert grants, bounded polls,
stop priority, pre-abort capture and terminal passivity; parser success alone
does not establish those semantics or any MCU execution.

## Attempt boundaries and independent validation

Exclusive new local owner: native_entry_static01 beneath the observer raw
directory. Required absent remote scope:
/home/arduino/sumox26_codex_build/app-motor-observe-entry-static01.
The inherited file-only reader does not create that remote scope. Preserve both
consumed ABI owners and every historical entry owner. Fixed D193 artifact paths
remain app-motor-observe-static01; do not retarget another ELF.

Retain four children,60s child/5s reap/1MiB streams,400s transport,
30000 UTF16 command units,128MiB local free-space guard, source/artifact/tool/
boot pins, clean reviewed HEAD, before/after remote checks and independent local
closure. Empty stderr remains mandatory. No compiler, upload, reset, MCU read,
motion, credential or firmware/configuration change is introduced.

Freeze an independent oracle before reading the new implementation. Cover:
passive import/invalid CLI; exact bootstrap source equality; input type/size/
hash and substitution-count refusals; both exact projected identities;
all-input verification before private execution; original-first composition;
separate module namespaces/no registration/no historical load or main; retained
pins and new SELF/owners; exact four commands and27 ranges; direct replacement
of ABI query/summary without polls-tag requirements; synthetic complete valid
entry packets and decimal/hex symbol sizes; wrong/duplicate/missing symbols,
aliases, binding/type/section/Thumb/ranges; initializer section/bytes/pointer;
missing/duplicate/reordered markers, malformed instructions, gaps/overlaps and
incorrect final coverage; raw preservation and failure/local-closure delegation.
Preserve all old tests/assertions. Run Linux and Windows serially, record first
failures, and review/freeze the new inputs before actual native admission.

This work proves file observations only. Runtime behavior, physical acceptance,
motor-run permission, RAM/WCET measurement and human gates remain separate.
