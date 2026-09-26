# D209 ordinary application static ABI proposal

26 September 2026. Unadopted, file-only proposal. This document and
P7_ordinary_app_static_compile_raw/abi_derivation01.json are preparation data,
not a reader, test, native admission or authority to run firmware. D208 actual
compile review has closed; adoption of this proposal, independent source and
host review, fresh admission and a clean reviewed HEAD remain prerequisites.

## Purpose and fixed input

Observe the current ordinary app's two relevant static objects and public
runtime/transaction/motor layouts from the exact D208 ELF and debug ELF. This
establishes a bounded basis for later instruction inspection and separately
specified inhibited observation. It does not decode MCU memory or establish
runtime success. The sketch is src/app/app.ino; its setup calls Runtime::begin
with configured grants and its loop continuously calls Runtime::step.

The exact profile is app.ino, arduino:zephyr:unoq:link_mode=static, default
startup, -DMATCH=0 -DMOTORS_ALLOWED=0; source config leaves probe0 and all17
APP_GRANT values zero. No config, grants, timing bounds, production source or
artifact bytes may change. The source digest is
9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.
D208's125-file manifest contains105 source files mapped to104 staged files;
the staged/source byte count is764405. Its real pinned app_source_hash check
and Path-order mapping remain binding through the actual ordinary caller.

| Accepted input | Bytes | SHA256 |
|---|---:|---|
| tools/compile_ordinary_app_static.py | 26136 | 40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89 |
| P7_ordinary_app_static_compile_raw/inputs_static.json | 12940 | a5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7 |
| P7_ordinary_app_static_compile_raw/native_static01/result.json | 1565 | 221d02be2de722a8886a142328d3accb147cf1ab89b60ed9857e62fdd303aeb0 |
| P7_ordinary_app_static_compile_raw/native_static01/artifacts.json | 9281 | 275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0 |
| state/reviews/P7_ordinary_app_static_compile_actual_review.md | 14982 | 8cd383e47ab78db74141c0100aedb134afaeac60195555c8eac3b529e1de9865 |

P7_* relative entries in this table are under state/analysis/. The saved
result is COMPILE_CHECKED, one query, one compiler,230 transports and eight
PASS closing checks at reviewed HEAD9bdd38aeb312404bc1cd2a3b3fa7e7f621f3bad5.
Serial2629958581 and boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 are unchanged
requirements, to be freshly checked by the file-only lifecycle. No prior
receipt substitutes for that check.

The build owner is /home/arduino/sumox26_codex_build/ordinary-app-static01.
The artifact packet pins all eight files, the installed loader and TLS source.
In particular build/app.ino.elf is170376 bytes/SHA
aaeeb64025dae2b2f8bf0458a39c110377ca8d5e4c9f833fae75444a181f6db5;
build/app.ino_debug.elf is1751548 bytes/SHA
71e512382e764810ed02eec110e3c1c003244d41d608b145ea400e1e8235ab90.
The packet records .bss at536951136, size167584, alignment8; the initialized
zero interval is[536951136,537118408),167272 bytes. These are accepted file
section bounds, not proposed object coordinates or runtime values. The
derivation records the complete eight-file binding without duplicating files.

## One direct wrapper and explicit semantic seams

The only prospective subject is
state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_abi.py.
Do not create it until adoption and implementation ownership. Use one direct
private projection of the historical D188 reader, not a stack of diagnostic
Runner, polls-alignment or SETTLE-summary wrappers.

The lifecycle base is
state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py,
16600 bytes/SHA0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c.
The current hardened bootstrap source is
state/analysis/P7_motor_const_compile_raw/inspect_static_abi.py,
16087 bytes/SHAf360a52d6e8c29227b8a59481f37f5e8a30b207d7b66fbffaa8e8785a4dedf3c.
Copy its complete physical-line function bodies require, _stamp, _plain_chain,
_read_handle, pinned, _verify and main byte-for-byte. Their span identities
are recorded in the derivation. Its main already validates an exact string
argv list and delegates to load_reader; do not call the old wrapper's main.

The derivation lists twelve ordered, count-checked metadata substitutions in
the D188 base: RAW, compiler path, build owner, ABI scope owner, scope label,
source digest, compiler/manifest/outcome/artifact digests, compiler binding
through load_caller(root=ROOT), and ordinary ELF basename. Apply these to
hash-checked original bytes and verify the recorded metadata intermediate.
The compiler binding must call the checked D208 launcher's load_caller once;
that returns its real CompileDiagnostic class. Never call compile main/run,
stage, source_admission, sources or a compiler subprocess here.

After that intermediate, only four whole named spans are semantic replacements:

1. TYPES assignment: the twelve types listed below; bool remains appended.
2. WINDOWS assignment: the six ordinary Runtime members listed below.
3. queries(reader): the exact finite command/expression recipe below.
4. summarize(result, layout): the two-object ordinary parser/schema below.

Each original span must occur exactly once, have its recorded bytes/hash and
be replaced as a whole physical-line span. Restoring those four original
intermediate spans must reproduce the complete intermediate bytes. Apart from
the enumerated metadata changes, retain the whole StaticAbi class and all its
local/prepare/execute behavior, loaded, number, checked_command, sha, and the
projected reader's main byte-for-byte. Preserve its historical error wording.
The private projection is never written over an original file.

The wrapper may implement the bounded project_reader, passive private module
construction and load_reader wiring needed for this projection. Ordinary
query/parser helpers belong inside the explicitly replaced queries/summarize
spans or as bounded helpers supplied by this one wrapper; their complete
source must be sealed and independently reviewed. No generic plugin framework,
second executable wrapper, fallback parser or alternate transport is needed.

Before private execution, read and validate exact sizes/hashes for all six
original inputs: D188 base, D204 guard source, D208 launcher, current manifest,
current compile result and current artifact packet. Also pin the adopted
contract's final digest. The companion derivation is design/evidence data,
not executed code or an unchecked runtime patch source. Retain all original
D188 HARD_PINS with the enumerated current destinations, then extend by copy
with the base/guard source/contract pins. Self is bound to the clean reviewed
HEAD and local closure. Assign the hardened pinned function into the private
reader before any owner is constructed or its loaded helper can read files.
Do not execute the D204 wrapper or import its diagnostic load_reader.

Final wrapper and full projected-reader hashes cannot be known from this
behavioral proposal alone. Implementation must seal both exact byte identities
in a metadata-only implementation receipt before host execution; project_reader
must enforce its concrete original/intermediate/final size/hash and occurrence
checks at runtime. No placeholder, unchecked output or dynamically learned
expected digest may reach testing or admission. The independent oracle author
may receive that identity receipt without inspecting the implementation body.

## Exact finite ABI query

There are exactly four child commands: pinned readelf --version, pinned gdb
--version, readelf -hSWs on OWNER/build/app.ino.elf, and the unchanged guarded
GDB builder on OWNER/build/app.ino_debug.elf with the following expressions.
Retain -nx -nh -batch, set auto-load no, set language c++, set may-call-functions
off and the fixed tool prefix. No attach, inferior, target, memory examination,
function evaluation, loader inspection or additional child is included.

Start with set max-value-size1048576 using the inherited separating space.
For these twelve types, in this order, then bool, emit the inherited two-line
SIZE and ALIGN pairs followed by the LAYOUT marker and ptype /o command:

app::Runtime; app::RuntimeReport; app::Transaction; app::TransactionReport;
motors::MotorGate; motors::UnoQPort; motors::Result; motors::HaltResult;
fsm::RobotResult; fsm::PreviousTick; core::Outputs; app::SetupGrants.

For example SIZE uses echo SUMOX_SIZE <type> followed by literal backslash-n,
then p/d sizeof(<type>); ALIGN uses alignof(<type>), not alignof a member
expression. LAYOUT uses echo SUMOX_LAYOUT <type> with literal backslash-n,
then ptype /o <type>. All debug answers must be current observations; no old
size, alignment, offset or type-layout constant supplies a missing answer.

Next query these ordered offsets using the exact expression
p/d (unsigned long)&((app::Runtime*)0)-><member>, with a SUMOX_OFFSET marker:

| Member | Window type |
|---|---|
| report_ | app::RuntimeReport |
| transaction_.report_ | app::TransactionReport |
| transaction_.previous_ | fsm::PreviousTick |
| transaction_.gate_ | motors::MotorGate |
| grants_ | app::SetupGrants |
| attempted_ | bool |

Finally query these47 enum members, in group/member order, using an echo
SUMOX_ENUM <qualified-type>::<member> marker and
p/d (unsigned int)<qualified-type>::<member>. Their source-defined expected
values start at zero and increase by one in each row; require observed equality.

| Enum | Members in source order |
|---|---|
| app::RuntimePhase | NOT_STARTED,RUNNING,STOPPED,FAULT,STOP_OBSERVING |
| app::RuntimeFault | NONE,PORT,CLOCK,SERVICE_LIMIT,TRANSACTION,PROJECTION |
| app::Phase | NOT_INITIALIZED,IDLE,ACQUIRING,DECIDED,FAULT |
| app::Fault | NONE,SETUP,ORDER,CLOCK,IDENTITY,RECEIPT,ABORTED |
| motors::Fault | NONE,NOT_INITIALIZED,PORT,IO,COMMAND,TOKEN,STOPPED |
| core::State | BOOT,IDLE,COUNTDOWN,OPENER,SEARCH,TRACK,ATTACK,DEFEND_TURN,EDGE_ESCAPE,REFLANK,STOPPED,DRIVE_TEST |
| edge::EscapeFault | NONE,WHITE_PATTERN,REPLAN_LIMIT,PERMISSION_LOST,INVALID_CONTEXT |

Total:185 expression strings, including initial setup,78 type expressions,
12 window expressions and94 enum expressions. The derivation contains the
literal ordered expression data and its identity. No unused inline constexpr
constant queries are added. fsm::RobotFault remains a raw/source-defined
bitmask, not a newly queried target enum. No peripheral or recorder object
window and no NativeSources/UnoQDumpPort object is required for this scope.

## Ordinary summary and refusal rules

Keep raw commands, stderr and stdout encodings unchanged. Require the inherited
four command identities, execution/deadline/reap records, canonical base64,
byte counts and empty stderr; missing children or first errors cannot be
converted into parser success. The new summary is a pure function: no reads,
writes, imports, tool calls, source mutation or caller-owned input mutation.
It may parse private copies. It does not call old diagnostic summaries or
normalize a diagnostic symbol into an ordinary object.

Require ET_EXEC, exact ordered SUMOX marker inventory, one numeric answer per
SIZE/ALIGN/OFFSET/ENUM marker and one nonempty complete LAYOUT block per type.
Reject missing, duplicated, reordered, malformed or unexpected SUMOX markers;
reject negative/noninteger answers, bool-as-integer metadata, unavailable debug
information and unsupported type answers. Numeric size must be1..1048576;
alignment must be a power of two in1..16. Preserve complete layout text and
record its type association. Full DWARF layouts are evidence for a later
independently checked field map; this task does not guess scalar offsets or
claim every nested field has already been decoded. Observed bool size and
alignment must both equal1.

Parse the complete readelf output for exactly one row of each symbol:

| Object key | Exact expected symbol spelling | Queried type |
|---|---|---|
| runtime | _ZN12_GLOBAL__N_17runtimeE | app::Runtime |
| motor_port | _ZN12_GLOBAL__N_110motor_portE | motors::UnoQPort |

These spellings come from the pinned anonymous namespace declarations and
remain hypotheses until observed. Absence or changed compiler spelling is a
visible failed attempt, never a selector broadening or guessed coordinate.
Require complete LOCAL OBJECT DEFAULT rows with numeric section indices.
Accept decimal or0x-prefixed readelf symbol sizes explicitly; do not parse a
hex size as decimal or alter raw output. Reject duplicate candidates even when
one duplicate is malformed, global/weak/function/undefined substitutes and
trailing junk. Retain the entire symbol table for later entry-scope derivation.

Independently require each object's observed size to equal its queried type
size, its address to satisfy that type's alignment, and its numeric section
to be the unique current .bss NOBITS WA section. Cross-check that section's
address/size against the checked artifact layout. Both objects must lie wholly
within the checked initialized bss_zero interval, and that interval must lie
within .bss. Require the two objects not to overlap. Do not accept mere total
RAM bounds, the uninitialized section tail or a prior object's address.

For each of the six windows, require nonnegative offset, positive observed
type size, containment within runtime, absolute alignment and pairwise
nonoverlap of these selected distinct members. The window address is only the
fresh runtime address plus its freshly observed offset. The whole motor_port
object is its own object range. No capture reads or target contents follow.

Probe0 and ordinary entry also require absence of these exact diagnostic
symbols in the complete symbol table: _ZN12_GLOBAL__N_110diagnosticE,
_ZN6motors12_GLOBAL__N_119settle_probe_reportE and
_ZN6motors17settleProbeReportEv. Do not request absent diagnostic types. No
Runner, Trace report, before-abort snapshot, poll counter or SETTLE report
field can be synthesized into the new schema.

The ABI JSON has exact top-level keys schema,status,objects,sizes,alignments,
layouts,windows,enums,limitation. schema is ordinary-app-static-abi-v1 and
status remains STATIC_ABI_OBSERVED. objects has exactly runtime and motor_port;
each has symbol,type,address,bytes,alignment,section. sizes,alignments,layouts
have exactly the13 queried type names. windows has exactly the six member
names; each has object='runtime',type,offset,address,bytes,alignment. enums
maps each of the seven qualified type names to its exact named numeric values.
limitation explicitly states file layout only, no MCU contents or coherent
snapshot/runtime/timing/physical acceptance. Do not preserve obsolete top-level
Runner coordinates as misleading aliases. The local lifecycle result remains
the unchanged STATIC_ABI_OBSERVED closure with separate raw result.json,
abi.json and local_result.json.

## Retained admission, error and ownership lifecycle

Fresh local owner is
state/analysis/P7_ordinary_app_static_compile_raw/native_abi_static01.
Fresh remote scope is
/home/arduino/sumox26_codex_build/ordinary-app-abi-static01. As before, the
remote scope must be absent and is checked but not created. All previous
fault/observe/settle/const owners and failures remain untouched. Partial local
output consumes this new owner; never repair, delete, reuse or automatically
retry it. Every subsequent attempt requires a separately reviewed fresh owner.

Preserve the exact hardened ancestry/regular-file/single-link/reparse checks,
descriptor-before-read admission, O_NOFOLLOW/O_NONBLOCK, bounds/digests, full
same-API opening/closing stamps, secondary-close error handling and primary
error precedence. Retain only the accepted Windows cross-API ctime exception
and exact eligible .exe/.bat/.cmd/.com full0111 path-mode adjustment; do not
generalize them or apply installed compiler hardlink allowances to local input.

Import remains passive. CLI is exactly --check-only|--execute --reviewed-head
<40 lowercase hex>, with Python -B required. Check-only is local/read-only,
does not claim an owner or dispatch a board call. The accepted compiler module
performs current125-file source admission and current artifact validation; ABI
admission must not use the historical diagnostic real-prepare fixture as proof
of the new ordinary admission seam. Only one separately approved execute may
claim its exclusive owner and dispatch the single file-only transport.

Keep pinned readelf SHA c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e,
GDB SHA8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778,
all installed loader/TLS/ADB/helper pins and complete board identity unchanged.
Keep60s child deadline,5s reap,1MiB per stream,400s transport,8MiB transport
reply bound,30000 UTF-16 command units and128MiB local free-space minimum.
Preserve12 remote file closing checks plus board_identity, independent local
closure, checked source/manifest/tool identities before and after, first-error
precedence and evidence-write failure reporting. Save raw result.json before
summary interpretation, including failing command evidence. Do not relax a
bound to make a query fit; a prospective over-bound command stops locally.

No compile, upload, reset, MCU memory read, credential, cleanup, board mutation,
inferior execution, peripheral initialization, motor operation or physical
qualification is authorized. D207 remains the last verified flashed image.

## Independent host evidence before native admission

Freeze a contract-derived independent oracle before its author reads the new
implementation body or anyone executes it. Retain relevant D204 descriptor,
projection, CLI, lifecycle, provenance, command and error assertions. Enumerate
selected historical method names and assertions, platform skips and exclusions;
do not claim all71 historical methods apply unchanged when their predicates
require diagnostic Runner/SETTLE layouts. Replace only those semantic fixtures
with independently built ordinary packets covering every new predicate above.
Preserve previous failure evidence and the corrected Windows mode cases.

In particular cover two independent nonoverlapping objects; each absent,
duplicated/malformed/wrong binding/type/section/size/alignment/outside-zero-BSS;
decimal and0x sizes; missing/duplicate/current .bss sections; each window's
containment/alignment/overlap; all marker/order/number/layout/enum failures;
probe-symbol absence; input immutability; all four child and13 closure checks;
first/secondary errors; exact four-span/metadata/bootstrap boundaries; old
diagnostic source/manifest/artifact/build/scope rejection; and real current
ordinary source admission including app_source_hash. Use distinct synthetic
coordinates, not saved target or diagnostic addresses. Current positive and
stale negative fixture values must demonstrably differ; preserve exact guarded
no-I/O projector assertions without fixture file reads inside their guard.

Run serial Linux and Windows suites under separate exclusive receipt owners,
Linux /dev/shm and a dedicated Windows temporary directory set before startup.
Record exact selection/counts, pins, streams, first failures and cleanup. Host
tests must never reach board transports or compilers. Final host/source and
fixed-scope admission review precede clean-HEAD check-only and at most one
native execute. Separate actual review must check raw outputs and closing
receipts before any layout can seed entry or observation work.

## Meaning of any later ordinary observation

Runtime::step continuously clears freshness pulses; Transaction::open clears
its current report every epoch. There is no diagnostic terminal freeze,
EPOCH_LIMIT, before-abort copy, begin_ok field or automatic final inhibition
receipt. setup ignores begin's return. Runtime FAULT can be published before
cleanup completes. A finite host deadline does not terminate this firmware.
No report has a seqlock or atomic snapshot guarantee; repeated reads may tear,
especially64-bit tokens. Matching epoch/token brackets alone would establish
diagnostic consistency only, not atomicity. Native motor masks and settled_
are transient callback bookkeeping, not measured pins. With all grants absent,
source permits RUNNING while initialization_complete=false and BOOT; this is
not readiness, IDLE, complete hardware setup or physical acceptance. These
limits belong in any later separately adopted capture contract.
