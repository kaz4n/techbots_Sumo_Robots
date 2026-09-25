# D194 observed application file-only ABI projection

26 September 2026. D193's static compile completed with all eight closing checks
passing. This scope prepares one separately admitted file-only ABI observation;
software implementation/tests create no native action. Preserve every historical
reader, interpreter, launcher, artifact and consumed owner.

## Public interface and fixed inputs

Add state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi.py only.
Public APIs: parse_request(argv), pinned(path, expected, limit=1048576),
project_reader(raw), summarize(result, layout, *, parser, normalize),
load_reader(*, root=ROOT), main(argv). ROOT is the absolute repository root.
Optional root and parser/normalize arguments are controlled fixture seams; the
production CLI always uses ROOT and the fixed privately loaded functions below.
Import defines constants/functions only and performs no source read, write or
dispatch. parse_request accepts an exact list of strings:
--check-only|--execute --reviewed-head <40 lowercase hex>, returning action/head.
Wrong types/order/count fail before source loading. main validates arguments and
Python -B, loads the private reader, and delegates once to its unchanged main.
Only the new wrapper's own __main__ dispatches. No profile/target overrides.

Fixed source SHA256 is
3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0.
The D193 manifest freshly bound boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8;
this is also the old literal, retained because the new evidence agrees, not
inferred from history. Existing native identity checks must observe it again.
Board identity and installed/tool pins remain the inherited fixed values.

| Fixed input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py | 16600 | 0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c |
| state/analysis/P7_app_motor_fault_compile_raw/interpret_static_abi.py | 5928 | 6a990871af18ca8bc5d10f9d11efda4619052bf1de5ab272188de746f95dad21 |
| tools/compile_app_motor_observe.py | 7583 | 70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827 |
| state/analysis/P7_app_motor_observe_compile_raw/inputs_static.json | 13333 | aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e |
| state/analysis/P7_app_motor_observe_compile_raw/native_static01/result.json | 1615 | 24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b |
| state/analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json | 9651 | 5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b |

The projected reader is exactly16833 bytes, SHA256
f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14.
The original and projected source are LF bytes; no newline normalization.
The normalizer and D193 launcher execute from unchanged original bytes.

## Exact reader projection

project_reader accepts exactly bytes, checks original length/hash, performs
only these ordered byte replacements with their exact occurrence counts, and
checks projected length/hash. No I/O, execution, fallback or unchecked repinning.

| Old bytes | New bytes | Count |
|---|---|---:|
| app_motor_fault | app_motor_observe | 10 |
| app-motor-fault | app-motor-observe | 2 |
| D188_STATIC_FILE_ONLY_ABI | D194_STATIC_FILE_ONLY_ABI | 2 |
| self.compiler = loaded(COMPILE, HARD_PINS[COMPILE]) | self.compiler = loaded(COMPILE, HARD_PINS[COMPILE]).load_caller(root=ROOT) | 1 |
| 21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950 | 3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0 | 1 |
| cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a | 70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827 | 1 |
| d4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5 | aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e | 1 |
| f8928bd0b9a59f47c1bc02c627523af8f250535ffcd269e37e5a80414cc0ce82 | 24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b | 1 |
| 57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce | 5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b | 1 |
| 'countdown::Result') | 'countdown::Result', 'report_.polls') | 1 |

Next replace the single line `    'attempted_': 'bool',` with these two lines:

```python
    'report_.polls': 'report_.polls',
    'attempted_': 'bool',
```

Next replace this unique query prefix:

```python
    expressions = ['set max-value-size 1048576']
    for name in (*TYPES, 'bool'):
```

with the same prefix followed immediately by:

```python
        subject = ('((app_motor_observe::Runner*)0)->report_.polls'
                   if name == 'report_.polls' else name)
```

Finally replace `expression + '(' + name + ')'` with
`expression + '(' + subject + ')'` once, then `'ptype /o ' + name` with
`'ptype /o ' + subject` once. Preserve all original tag labels and other queries.
The existing four file-tool commands now observe20 SIZE/ALIGN/LAYOUT groups and
11 Runner-member windows. report_.polls is a member-expression key, not an
assumed typedef. Its sizeof/alignof/ptype and Runner offset come from file GDB;
no prior padding, member offset, Report/Runner size or address is assumed.
Unsupported GDB syntax fails the attempt; no fallback guesses.

## Strong bootstrap and private composition

pinned accepts an absolute or relative local path (made absolute), lowercase
64hex digest and integer byte limit1..16777216. Require ordinary directories
through full ancestry and one ordinary singly linked regular file; reject
symlink/reparse/special paths. Open with O_NOFOLLOW/O_NONBLOCK/O_CLOEXEC/O_BINARY
where supported, then immediately fstat and compare ordinary type/link count/
attributes/path identity BEFORE fdopen/read. Read at most limit+1 bytes. Require
nonempty bounded contents, unchanged path/ancestor snapshots and descriptor
snapshots before/after read, and matching digest. Compare device/inode/mode/
link-count/size/mtime_ns/attributes across APIs; ctime also matches except that
Windows path/handle ctime are compared only for stability within each API.
All descriptor closes are attempted; preserve a primary read/check exception
if close also fails, and fail on a lone close error. No special file is read.

load_reader verifies the original reader, normalizer and D193 launcher against
the above exact lengths/hashes plus this frozen contract against the hash pinned
in the wrapper. It verifies the reader projection before any source execution.
Execute reader and normalizer definitions only, in separate fresh private
ModuleType namespaces with their original absolute __file__ paths, never as
__main__, never registered in sys.modules. Do not instantiate StaticAbi during
loading. Install the strong pinned function into the private reader, affecting
its loaded/local/receipt/ADB reads without changing historical files. Extend its
HARD_PINS with original reader, normalizer and this contract, retaining every
projected/inherited pin. Its existing SELF hash remains runtime-bound to the new
wrapper and clean reviewed HEAD, so no recursive self-pin is introduced.

The one compiler-load replacement calls the new launcher's load_caller(root=ROOT).
Consequently source inventory/mapping, admission and artifact validation use the
actual D193 projected CompileDiagnostic, retaining original-byte manifest pins,
new source tree/schema, strong D193 bootstrap and all compile-derived checks.
Do not copy a lifecycle or invoke any compiler/main/upload routine here.

Install a private summarize adapter using this module's public summarize helper,
the projected reader's original summarize function, and ONLY the unchanged
normalizer.normalize callable. Never invoke the old normalizer's interpret/main:
those explicitly require historical failed-attempt receipts.

summarize requires a dict result containing exactly four command dictionaries;
it creates private result/command copies and decodes command2 stdout as UTF8
from strict Base64. Call normalize(text) to accept the unique diagnostic OBJECT
row's decimal or lowercase0x size under its existing1MiB bound. Update only the
private command2 stdout_base64/stdout_bytes and call parser(private, layout).
Return the parser ABI dict plus readelf_size_projection containing the unchanged
normalizer metadata. Do not mutate result, any command row or layout. Preserve
malformed/duplicate/zero/oversize rejection. Existing execute checks original
stream accounting and command/closure evidence before summarize, and saves the
exact original result.json first. No raw stdout/receipt is rewritten. Static
ET_EXEC/BSS/unique-object/alignment/window checks remain the original parser's.

## Native boundary and retained evidence

Local output is P7_app_motor_observe_compile_raw/native_abi_static01. Its exclusive
owner is never reused after success, failure or uncertainty. The remote scope
/home/arduino/sumox26_codex_build/app-motor-observe-abi-static01 must be absent;
the existing file-only reader does not create it. Build files come only from
/home/arduino/sumox26_codex_build/app-motor-observe-static01/build. No old artifact
or source tree may be treated as current. Retain original D173 gdb builder and
REMOTE_READ, changing only the reader scope label to D194_STATIC_FILE_ONLY_ABI.

All existing D188 ABI safety/evidence checks remain: clean reviewed HEAD, exact
manifest and successful compile/packet receipts, pinned ADB/tool/loader/TLS,
128MiB local space gate, before/after artifact/identity checks, four fixed
file-only children,60s child/5s reap/1MiB streams,400s outer deadline, bounded
compressed command and30000 UTF16 Windows units. GDB has no target connection,
init/autoload/function-call capability. Check-only reads local files/Git and
composes commands without claims/board calls. Execute alone claims the local
owner, retains raw inputs/commands/results, emits observed abi.json and attempts
independent local closure. A secondary closure-write error never masks the
primary error. No upload/reset/MCU read, compile, firmware run or binary download.

Observed layout still requires independent field/initialization interpretation
before a separately scoped inhibited run. It is not electrical acceptance,
measured free RAM/stack, WCET, fault reproduction/repair, motor permission or a
human phase gate. Source implementation here authorizes no native invocation.

## Independent validation

Derive tests from this contract and prior public source interfaces before reading
the new implementation; freeze tests before execution. Cover exact projections
and rejection/drift, original+projected pins, invalid CLI before reads, passive
import/loading, private roots/modules, strong bootstrap type/FIFO/inode/size/
ctime/digest/link/close races, unchanged original sources and extended local pins.
Use controlled synthetic readelf/GDB packets for decimal/0x spelling, full member
SIZE/ALIGN/LAYOUT/OFFSET tags, preserved raw packet and normalization metadata,
missing/duplicate/malformed symbols/tags, ET_EXEC/BSS/size/alignment/window bounds.
Exercise projected StaticAbi.prepare/execute through explicit transport/Git/file
fixtures, including new compiler.load_caller integration, raw receipt retention,
remote command/deadline/stream/closure refusals, consumed-owner failure and primary
error preservation. Check realistic Windows composition with zero dispatch.
No target facts or source constants are inferred from a mock passing result.
