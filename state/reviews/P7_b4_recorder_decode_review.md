# D216 B4 recorder decoder review

FINAL PASS, 2026-09-26. No material finding. Independent same-model reviewer
with reused project context, separate from implementation and oracle authors.
Both seals preceded new source/oracle inspection. I reviewed source, AST/data,
actual D215 layouts and saved host receipts only; no subject import/execution,
test run, device call or firmware change by reviewer.

## Exact reviewed inputs

RAW denotes state/analysis/P7_b4_recorder_decode_raw.

| Input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_b4_recorder_decode_contract.md | 10168 | 843055fbc3837611ae310d0ecb7e549063ed7280783436581219fd1120fc5d13 |
| RAW/layout01.json | 4443 | f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d |
| RAW/map_derivation01.json | 25482 | 86ec272d73f5a1243725480e44af4298e718f976cc2ba49b42752fa931d61ac0 |
| tools/decode_b4_recorder.py | 11743 | 43347b569098b78cbdbf32a1e4b06ebbbef245c4c57b91609fa38d8bb3cca8a3 |
| RAW/decode_derivation01.json | 5407 | 6afa85cfe8342fcd6e7a3ef6ba6f62c0e2f1676e62a42a860e04c4ebcc4ff800 |
| tests/tooling/test_b4_recorder_decode.py | 28930 | 6baf8870e080f56499de4b42b26061dcd4d77fadf367c2e312b0dbb0a28a2a2b |
| RAW/decoder_oracle01.json | 6735 | 19a3f9e977880a30a42747dcc43c818f9d6fc39afd685e44950ac1c32282e18e |
| RAW/decode_coordinator_freeze01.json | 4751 | ffc00a68159b11befaec7acf631a010300705eca7138d1b8c748df54dc27e593 |
| RAW/decode_host_closing01.json | 6062 | 3fab6436bf85a176611c318cd20b0d341b372f30aa7dce10d21f60d8a6cd2038 |

The unchanged conventional dependency tools/validate_csv_bundle.py is19324
bytes/1c4781fdd0f77a610998644db610bf6adf5a2373d4f32f3ec7ca486185ff52f2.
All declared map, implementation and oracle basis pins independently match.

## Map and implementation

All38 interpreted map entries independently match the fresh accepted D215
AttemptRecorder full layout:35 scalar fields,including nine bools,and three
arrays. Each direct owner offset/width/member name agrees with its standalone
FrameBuffer,EventBuffer,AttemptSummary or TickStatistics parent crosscheck.
Every extent fits the159200-byte owner without overlap. Source declarations
agree with the types, ring ordering, two-bit physical status lanes and retained
event prefix. Four extra owner members remain explicitly raw-only.

The fixed map binds accepted source9044ebbb,artifact packet0acaa30a and
ABI25bf5764; it does not authenticate supplied owner bytes. Production admits
only the exact map digest. The implementation checks schema,binding,exact
integer geometry,widths,alignment,extent and overlap after identity. The
public oracle intentionally does not bypass that pin to reach mutated internal
maps; geometry confidence comes from source and actual-layout review.

The pure API checks exact bytes types and body/layout bounds before hashing or
parsing. Every bounded exact-byte refusal retains original owner bytes and
hash. Refusal order follows the contract: map,owner size,all35 raw integer
reads,nine canonical bools,ring/count bounds,retained statuses,CSV formatting.
Bool2 remains visible in native_values; phase is independently retained.
Summary appears after scalar/bool/index admission, before status validation.
A retained status3 refuses all CSV; unused slots/lanes,padding and raw-only
terminal state do not cause invented refusals.

Frame reads follow (first+ordinal)%5001; events retain their exact4096-entry
maximum prefix. Wire payloads, signed duty-128, unknown codes, timestamp order
and saturation are preserved. The36 summary columns map exactly to34 observed
scalars plus schema_version and incomplete. The latter is the precise22-field
OR from unchanged D074 LOSS_FIELDS and source AttemptRecorder::incomplete;
phase,go_seen,counts or nonterminal lifecycle do not independently create loss.

Rows use unchanged D073/D074 headers,wire structs,ranges and pure parsers.
All three ASCII/LF/lowercase-hex CSV roles publish together after validation,
with exact byte/row/hash records. Existing owner consistency checks run
separately; valid CSV remains available on a consistency failure. Decode calls
no dependency file API and has no CLI,exporter,capture,transport or runtime
configuration interface. Fresh result dictionaries avoid cross-call mutation.

Origin/coherence remain UNPROVEN; provenance remains ABSENT/UNKNOWN with no
declared origin, and common-attempt,transport and hardware flags remain false.
SEALED does not imply IDLE, successful action or physically complete recording.

## Focused host evidence

The independently authored twenty-method oracle covers the actual fixed map,
literal D073 payload goldens,all35 distinct scalar sentinels/unsigned maxima,
all22 individual loss terms,nine bool refusals,ring wrap/four status lanes,
full capacities,index limits,lifecycle versus loss,raw-preserving refusal,
owner consistency and repeated-call purity. Expectations are independent
constants and source-derived data; no old suite is silently collected.

Root's first serial runs passed20/20 each with no skips,errors,repairs,timeouts
or retries: Linux0.803 seconds inner/13.7916399 outer; Windows0.306 inner/
0.5444766 outer. I independently reconciled all40 sorted method outcomes,
eight intent/result/stream identities,all26 current frozen inputs and actual
empty Windows TEMP. Linux stderr is
19300c7a76e760bf50e14618e63eb972309f6d54efcf6b575fe6ca93df295ef6;
Windows stderr is
549a984254b2eb01c3401e16cb5b3b8c69dfd2f06fe1d436d59ef18f7fd39226.
Both stdout streams are empty. The3505-byte host driver428776fe is the exact
five-counted-step derivative retaining exclusive owners,isolated/-B execution,
360-second bounds and stream/input closure. No separate Linux remnant
inventory or inherited native campaign is claimed.

Acceptance covers pure software behavior on synthetic owner-byte fixtures
bound to the real file ABI. No recorder SRAM was captured by this task. The
map hash, successful CSV and equal bytes cannot establish a coherent snapshot,
common attempt, physical origin, capture completeness or hardware qualification.
The prior D215 actual review remains immutable; this review adds no native or
motor authorization. Only this review file was written by the reviewer.
