# D209 ordinary static ABI: independent source and host review

2026-09-26. Reviewer: `const_cleanup_review`, review only.
**FINAL SOURCE/HOST PASS. No open material finding.** This accepts the revised
reader and its first serial host evidence. Native scope/admission and actual
file-only observation remain separate; no target ABI or runtime result is
claimed here.

## Sealed inputs

Raw paths below are relative to
`state/analysis/P7_ordinary_app_static_compile_raw/`.

| Input | Bytes | SHA-256 |
|---|---:|---|
| `inspect_static_abi.py` | 44449 | `f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d` |
| `abi_implementation02.json` | 8480 | `4e8fb0a1acbf59bac6f729dfdaeeee28104984d0439dfda0ffaf96717c7c7d42` |
| `tests/tooling/test_ordinary_app_abi.py` (repo-relative) | 44414 | `0a88018a27c011965ea7d36b43163c22a595267ce6d1a22fcc14ce01b4ce4ef5` |
| `abi_fixture_derivation02.json` | 54898 | `ec2494c6b131a224d4978ffbc24ff9e1b858362fe17f53f497601e8e11fd1900` |
| `abi_independent_freeze02.json` | 31050 | `847d38315af58f570a8087fb1568a2f1e012464af8efce4febe9bbae53ce432e` |
| `abi_coordinator_freeze01.json` | 30803 | `0173a01c3df2d9c1901d878cb185de4429fce808e3b0929f2ee798d21c07637c` |
| `abi_host_driver01.py` | 3497 | `1e50cb8eb3ec618b4d8040e546bcd28a87bce7754fdf2cc103d789a229a8123a` |
| `abi_host_closing01.json` | 26889 | `9b85a177cbc164ebb0b824f12c0d3344a7f8ddb733d7fa13d6b4a881ef3a2ef3` |

The adopted contract remains 20543 bytes/541710f0 and its derivation 54047
bytes/249a4209, accepted by preparation review 7382 bytes/5f40659e. I waited for
each independent oracle FINAL and root's barrier release before inspecting
that subject version. Review used local source/data/AST/hash inspection only;
I did not execute/import a subject, test, compiler or device tool. Only this new
review is written. `ordinary_abi_scope` independently reviewed the parser and
its bounded correction without execution or edits.

## Source and retained boundaries

Independently reconstructed the twelve counted metadata changes and four
semantic replacements. The private reader is 12965 bytes,
`7fb42d51a3f42f99c7e7890b4f4c1dc90360c2d84c09d3bbde7ccea4d1138aea`.
Restoring all four original physical-line spans reproduces the complete
16613-byte intermediate c6d2fad3 exactly. The seven D204 guard/CLI functions
match their original complete bytes. No unlisted projected-reader change was
introduced by the parser correction.

The six original inputs and contract are checked before private execution;
hardened `pinned` is installed before owner construction/loaded reads.
Descriptor, ancestry, regular-file, single-link, reparse, byte bounds, digest,
opening/closing identity and primary/secondary error protections remain.
The accepted narrow Windows mode/ctime exceptions are unchanged.

The explicit D208 `load_caller` binding returns the real ordinary caller class.
Retained local admission checks all 125 current inputs, ordinary source mapping
and the pinned real `app_source_hash`; prepare uses the complete current
artifact validator. It does not compile or stage. Current/original pins and
clean-HEAD/self closure propagate through the retained lifecycle.

All query constants match the independent derivation: four fixed file tools,
thirteen type layouts, six windows, 47 enum answers, 185 expressions and 92
markers. The supplied guarded GDB builder must produce the exact fixed command
vectors. No target attachment, function execution or MCU reads are included.

The ordinary parser preserves raw inputs, requires complete ordered markers
and typed numeric answers, validates both unique ordinary symbols and current
initialized BSS containment, checks object/window alignment and nonoverlap,
rejects diagnostic symbols and emits the exact ordinary schema. Its current
layout parser rejects unavailable/incomplete sentinels, unbalanced bodies and
additional/trailing outer answers while retaining the original layout text.
Object coordinates and scalar field offsets are not invented from historical
diagnostic data. Complete layouts support a separately reviewed later field
map; they do not already decode every nested scalar.

One transport, four children, twelve remote file checks plus board identity,
independent local closure, exclusive consumed owner, raw-before-summary
retention and first-error/evidence-write handling are unchanged. Native bounds
remain child60s/reap5s, stream1MiB, transport400s/reply8MiB, command30000 UTF-16
units and local128MiB minimum. Source/host acceptance does not waive these
checks or authorize a retry.

## Preserved pre-execution findings and corrections

Three findings were caught before any subject or suite execution and recorded
in `abi_preexecution_findings01.json`, 3620 bytes,
`35f2ce6d4321581e6efbdc8c0f820fd43ffc0fd20757d698c4e1fb332648689f`:

- Product: balanced braces alone accepted incomplete/unavailable type bodies
  or multiple complete outer type answers.
- Fixture: `ast.literal_eval` could not resolve symbolic HARD_PINS keys.
- Fixture: a positive query used unapproved tool paths/vector despite the
  adopted fixed-command requirement.

All five version01 subject/oracle/receipt/fixture/freeze copies were independently
verified byte-identical under `abi_version01_preserved`. The product change is
only `_complete_layout`; replacing that function restores the complete original
subject bytes. The oracle changes are only three named methods and two fixture
self-pin lines; restoring them reproduces the original oracle exactly.

The revised fixture resolves only bounded pinned AST string expressions,
records canonical guarded query construction and separately rejects changed
commands. Layout negatives increase from 39 to 141 while retaining all original
cases. The 66-method inventory is unchanged; new-method assertion count rises
98 to 102. The recorded authoring bookkeeping refusal was a prewrite static
count check, not a failed test execution. Revision receipt is 2624 bytes,
`fb32ef215fa031dfab6df5cab12f64b9aa9d53082f01babb411a2fb94ec7f55a`.
Focused parser review and this review closed all three findings before hosts.

The frozen selection retains 39 applicable methods: eleven bootstrap, thirteen
lifecycle, one checked-command and fourteen Windows-mode cases. All retained
historical byte projections/assertion metadata are unchanged. Twenty-seven
ordinary methods replace/extend the diagnostic semantics. Each of the 32
excluded D204 methods has a recorded applicability explanation; the obsolete
normalization-success case is replaced by ordinary success with raw ordering,
single dispatch, owner and closing assertions preserved. No blanket historical
71-method PASS is claimed.

## First serial host evidence and closure

| Platform | Results | Suite / outer seconds | Raw stderr SHA-256 |
|---|---|---:|---|
| Linux | 66 PASS, no skips | 52.686 / 65.828039 | `533ae8bbebc816777e44b3cf3c69fdd2f0270dd22be30b401db164385ad5b12e` |
| Windows | 64 PASS, 2 planned skips | 7.423 / 7.836582 | `9ab54cdb4ccd085607a2813895e1324419130daad5feb99f85da9b56961898b6` |

Independently reconciled all 132 ordered raw unittest rows, exact class/method
selection, intent/result argv/bounds, all eight stream/receipt hashes and the
closing summary. Both stdout streams are empty; stderr contains the expected
verbose unittest reports. Both processes return zero, without timeout, retry
or input drift. Windows skips are exactly symlink privilege (WinError1314) and
the Linux FIFO race fixture; both exact method IDs pass on Linux.

The driver remains the accepted historical driver with three count-one
metadata substitutions only. Its effective 360-second outer ceiling is stricter
than the oracle's 600-second maximum and was recorded before execution; native
bounds were unchanged. Linux precedes Windows, with isolated/no-bytecode
interpreters, `/dev/shm` and the dedicated Windows temporary directory.

All 154 independent and 159 coordinator inputs match; the complete 159-file
set was checked again after both suites. The closing method rows equal raw
streams exactly. Windows temporary contents are independently observed empty.
The saved bounded Linux inventory parses to UID1000, `/dev/shm`, prefixes
`sumox-d194-` (also covering mode fixtures) and `sumox-d209-abi-`, remnants [].
Its raw and parsed representations agree. Root closure records 6493216768
local free bytes, zero board calls and no repeated tests.

The source and host stage is complete. A separately reviewed exact native
scope, clean reviewed HEAD and successful local check-only must precede any
single file observation. Board identity and all twelve remote pins/thirteen
closures must be checked at use. D207 remains the last verified flashed image.
No ordinary runtime, atomic snapshot, live RAM, timing/WCET, final inhibition,
physical acceptance, motor permission or phase gate follows. This review is
sealed after final byte/hash reporting; reviewer writes stop.
