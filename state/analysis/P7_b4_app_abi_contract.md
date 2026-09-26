# D215 fixed B4 file-only ABI contract

Prepared under D051 for the accepted D214 compile at commit e3b2f9bc. This is
file inspection only. No compile, upload, reset, MCU memory read, inferior call,
recorder extraction, motor permission or physical acceptance follows. Native
admission and execution remain separate after independent source/host review.

The subject is state/analysis/P7_b4_app_compile_raw/inspect_static_abi.py.
It keeps load_reader(*, root=ROOT), returned StaticAbi, queries(reader),
summarize(result, layout), and the exact --check-only|--execute --reviewed-head
<40lowerhex> CLI with Python -B. Local owner is the fresh native_abi_static01
under that raw directory. The remote absent-only scope is
/home/arduino/sumox26_codex_build/b4-app-m0-abi-static01; it is never created.
Partial local output consumes this owner. No retry or cleanup is included.

Fixed input is D214 app.ino, static/default, source
9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a,
MOTORS_ALLOWED=0, B4_STAND=1 and the exact ten flags in the D214 receipt.
Probe and every other diagnostic flag are0; all17 source grants remain0.
The current 130-input manifest, current launcher and accepted compile result,
artifact packet and actual review are individually pinned. No old ordinary
artifact address, size or DWARF answer supplies a missing B4 answer.

The current packet is 9484 bytes/SHA256
0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085.
The ELF is152780 bytes/12a24abfb96e89863c46f2475d05fb44a549db95cb157411cd794657f15fd422;
the debug ELF is1779680 bytes/4c0fc8e2d3881019aaef222d7a9ab77779da7ca116bca49d1c6badeefeb83f7d.
The build owner is /home/arduino/sumox26_codex_build/b4-app-m0-static01.
abi_plan01.json records exact input identities, eight-file packet binding and
all313 expression strings. Its SHA256 is
874da0a9af0477d3ec94cbbc8f86edc03c68229fa0dc7b0c1bc2c7c7dcdf1037.
The plan is data, never an unchecked executable patch or runtime query source.

## Reuse boundary

Reuse the accepted D209 wrapper44449/f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d
through pinned passive private loading. Copy only its seven complete top-level
require, _stamp, _plain_chain, _read_handle, pinned, _verify and main bodies
byte-for-byte for bootstrap. Preserve D209 project_reader and load_reader,
all original dependency pins and every lifecycle/descriptor/error body.
A counted, final-hash-checked private projection changes only the compiled
reader's profile paths, source packet pins, scope labels and TYPES/WINDOWS
metadata. Bind the checked D214 launcher through its unchanged load_caller;
never call its compile main/run/stage/build/source operations.

Reuse every D209 parser body with an expanded exact type/window/enum/marker/
command inventory. New pure summary helpers may validate only the specified
nested stand container and numeric member extents, then add the fields below.
No old diagnostic parser fallback, framework, generalized query or transport
is introduced. Retain the complete StaticAbi class apart from enumerated
profile metadata substitutions, and seal original/intermediate/projected byte
identities plus exact untouched bodies in abi_derivation01.json.

## Fixed query

Exactly four children: pinned readelf --version, pinned gdb --version,
readelf -hSWs on the current build/app.ino.elf, and the retained guarded GDB
builder on current build/app.ino_debug.elf. Retain -nx/-nh/-batch, auto-load no,
C++ language and may-call-functions off. No target, attach, memory examination
or function evaluation is allowed. Preserve all185 D209 expressions as an
exact prefix, then append these128 expressions in order:

1. SIZE/ALIGN/LAYOUT pairs for stand_sequence::Report,
   recorder::AttemptRecorder, recorder::AttemptSummary, recorder::FrameBuffer,
   logframe::EventBuffer, logframe::TickStatistics, logframe::FrameBytes,
   logframe::EventBytes:48 expressions.
2. OFFSET transaction_.recorder_ from app::Runtime:2 expressions. Add this
   recorder object to the six existing disjoint Runtime windows. Retain all
   existing containment, alignment, initialized-BSS and pairwise checks.
3. SUBOFFSET robot.stand and robot.stand_stopping from app::TransactionReport:
   4 expressions. They are nested fields, not additional Runtime windows.
4. MEMBER_SIZE pairs for FrameBuffer.payloads_, FrameBuffer.statuses_,
   EventBuffer.events_, FrameBuffer.first_, FrameBuffer.size_, EventBuffer.size_,
   stand_sequence::Phase, stand_sequence::Reason, recorder::AttemptPhase,
   logframe::PackStatus, core::Mode:22 expressions. Member sizes use sizeof on
   a null typed member expression; enum widths use sizeof(qualified enum).
5. ENUM pairs, source order: stand_sequence::Phase NOT_STARTED through FAULT
   (7 values0..6); stand_sequence::Reason NONE through CLOCK_GAP (5 values0..4);
   recorder::AttemptPhase EMPTY through INTERRUPTED (5 values0..4);
   logframe::PackStatus OK,CLAMPED,INVALID (0..2); core::Mode
   SIDESTEP_R,SIDESTEP_L,DIRECT,ARC_R,ARC_L,WAIT (1..6):52 expressions.

Thus21 complete type layouts,7 windows,2 subfields,11 numeric member extents,
12 enum tables/73 enum values,156 ordered markers and313 expression strings.
Enum widths are numeric entries; do not feed enums to the struct/class/bool
complete-layout parser. Unsupported or absent debug answers visibly refuse.

## Added semantic checks and output

Retain every D209 strict stream, command, complete-layout, number, marker,
object, BSS, window, enum and nonmutation predicate. Require FrameBytes25 and
EventBytes8; observed arrays exactly125025,1251,32768 bytes, yielding5001 frames,
ceil(5001/4)=1251 status bytes and4096 events. All three queried index members
must be4 bytes: explicit supported ABI choice, not a claimed prior observation.
All five queried enum widths must be1. Queried array/index sums must fit their
fresh FrameBuffer/EventBuffer sizes; FrameBuffer+EventBuffer+AttemptSummary
must fit AttemptRecorder, and TickStatistics must fit AttemptSummary. Retain
full layouts for later independent per-member offset transcription.

Parse the single direct numeric offset/size header for struct fsm::RobotResult
inside the fresh app::TransactionReport layout, with its matching } robot;.
Reject missing, duplicate, wrong-type/name, non-direct or unbalanced containers.
Its size must equal queried RobotResult, and its aligned extent must fit the
fresh TransactionReport. Both SUBOFFSET extents must lie inside this container,
satisfy their observed type alignment at the selected live report address and
not overlap. Never infer the robot base from an earlier build or a span maximum.

Summary schema is b4-app-m0-static-abi-v1, status STATIC_ABI_OBSERVED. Preserve
all D209 top-level keys and add exactly subfields, member_sizes, capacities,
profile. subfields has robot.stand and robot.stand_stopping, each with
parent='transaction_.report_', type, offset, address, bytes, alignment. Offset
is relative to TransactionReport; address uses its selected live window.
member_sizes has the11 exact marker names. capacities has frame_bytes25,
frames5001, frame_status_bytes1251, event_bytes8, events4096, index_bytes4.
profile has project, fqbn, flags, motors_allowed exact integer0 and source_sha256.
All layouts and raw results are retained. Rejection type is ValueError.

This output is an ABI basis, not the later scalar decoder map. Such a map must
bind the observed recorder window and exact nested layouts, scalar offsets/
widths, frame/status arrays, ring first/size/loss counters, event prefix counters,
all summary/lifecycle fields and enums from actual evidence. No query result
establishes coherent MCU data, recorder completeness or measured timing.

## Preserved lifecycle and focused verification

Keep D209 tools/board/loader/TLS identities,60s child deadlines,5s reap,1MiB
per stream,400s transport,8MiB reply,30000 Windows UTF-16 units including NUL,
128MiB local free minimum,12 remote file checks plus board identity and
independent local closure. Save raw results before interpretation. Preserve
first errors, secondary close/write failures, no-follow/single-link/reparse and
Windows mode/ctime exceptions exactly. No bound expansion is allowed.

Before any subject execution, independently freeze focused fixtures for the128
new expressions, added layouts/windows/nested parent/member extents/enums,
current artifact/profile binding, summary nonmutation and representative
inherited refusals. Verify unchanged bodies by identity rather than rerunning
every historical suite. Source review and bounded serial Linux/Windows focused
host evidence precede fresh file-only native admission and one execution.
