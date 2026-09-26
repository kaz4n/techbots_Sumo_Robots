# D207 inhibited current-image runtime proposal: preparation review

Date: 2026-09-26. Reviewer: separate review-only agent.
Disposition: **PASS_DATA_ONLY_PREPARATION; no material finding in the proposed
fixed derivations or evidence bindings.** This is not source/host acceptance,
native admission, a cleanup result or runtime acceptance.

Owned output is only this new review. The reviewer read local data/evidence and
pinned predecessor source bytes, performed byte substitutions and AST/data
comparisons in memory, and did not import or execute any subject or oracle,
run tests/compilers, contact a device, authenticate, upload, reset, read MCU
memory or perform cleanup. No actual new D207 implementation, field-map or
preparation file was read or hashed. Their independent-oracle FINAL barrier
remains in force. Other agents' files and all prior reviews were preserved.

## Reviewed proposal and current evidence

The exact reviewed inputs are:

| File | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_const_run_contract.md | 27620 | 1949c7db32bfda4c3318095597b740ea17644ec5b0109cc2e589387842dbbf85 |
| state/analysis/P7_motor_const_run_raw/run_derivation01.json | 87930 | c90961438062c153f9c99621eba0617b3fc26b0f3dbdd2c35859ec2e744b5bfb |

The companion pins the contract, while the contract deliberately has no
companion digest; later scope binding must pin both actual files. This avoids
circular hashes without leaving either normative input optional. The reviewer
rehashed all 168 companion input files and separately checked its contract
pin. All matched. These counts overlap the 129 current firmware source pins
and twelve current provenance files, which were also independently checked.

Current source is
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`.
D203 COMPILE_CHECKED/ARTIFACTS_CHECKED and D204/D205 local/summary observed
statuses remain successful with no first error. The exact current raw ABI and
entry results and final actual reviews are among the twelve provenance roles.
In particular the D205 actual review is the accepted 19761-byte
`008572bfc541b8f0213fe6ed284af242dff8517e7fdc96283ee255d386d9e3f1` result,
not an unfinished review or a historical review silently relabeled current.

The proposed image is the existing app_motor_observe static/default-startup
build under app-motor-const-static01. Its raw binary is 95352 bytes /
`76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3`;
its package is 95368 bytes /
`f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7`.
The selected installed loader and 263680-byte loader_image remain the pinned
predecessor identities. This review establishes local proposal consistency;
fresh use-time file/tool/board checks remain mandatory.

## Correct predecessor and counted derivatives

The four prose recipe tables equal the companion's complete ordered operands
and counts. The reviewer independently applied all 40 metadata substitutions
to pinned complete predecessor bytes, checking each before/after size and
SHA256, plus all ten private-projection substitutions. Every prospective
identity matches. No prospective source was written to disk by the reviewer.

| Prospective product | Steps | Bytes | SHA256 |
|---|---:|---:|---|
| remote.py | 10 | 11331 | 51c60cd5ac87b823b84b2c7d993933690f0a3110e4d89c7cb958549fb5f111bc |
| actions.py | 8 | 12501 | 8aac6877a3bae25001c26c088ea947bbf3c7c0f2c0113619fb1db8c2a53834d9 |
| run.py | 15 | 24862 | d135835d22be424e9599d5a100f66275732bac6486facd7b86367d09c2c811ff |
| interpret_run01.py | 7 | 31259 | d96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab |
| private inert caller | 9 | 22983 | 3bd88946372ae637acdcfce2170a385e92dc313665bc75ed268c4aaa9ba1af75 |
| private inert actions | 1 | 19156 | cd3a28e82de554358e1a4855a76b5dc316f0007158bdac846fcb464e9130c3ab |

The prospective remote/actions/caller/interpreter function inventories remain
16/9/23/55, with unchanged names; the two private inventories remain 31 and 26.
The private legacy caller preserves the three accepted injection seams,
11-to-13 command-count adaptation, labels and caller path. The new operation
prefix changes ownership, without installing private modules in sys.modules
or invoking historical mains. The proposed run/actions imports retain their
existing checked local source reads; the contract correctly does not describe
those imports as passive or free of I/O. Remote remains definition-only.

The decoder predecessor is exactly the corrected 31266-byte ea43a42f source,
not the failed 31143-byte eb23a62a implementation. The reviewer read the pinned
interpreter_repair01.json and interpreter_oracle_portability01.json evidence.
The prospective `_flash`, `_receipt_types`, `_counts`, `_read_types` and
`_read_rows` source segments are byte-identical to that corrected predecessor.
The fixes therefore retain:

- Flash terminal association in before_loader/before_sketch/after_loader/
  after_sketch order at indices 4/6/25/20.
- Late exact-int count validation classified as COUNTS, with early container
  type/key checks preserved and bool excluded.
- Read-row key/shape and scalar type ordering before identity checks, followed
  by unchanged late prefix extent, fixed values, hash and filename checks.

The separate oracle portability correction remains pinned at
`1800b0cd3772e06020bff45d0637ea8a9c8f70ab7a6624a81f6a05af30fdde66`.
It preserves valid deeply nested JSON rejection according to the standard
parser's actual result, and independently injects RecursionError for a dedicated
packet only. No production depth limit or special case is proposed. Original
failures and the accepted corrected 67-method baseline must remain visible.

The accepted current compile launcher is pinned at 7557 bytes /
`957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247`.
The prospective caller uses its checked private loading and only
CompileDiagnostic.source_names/source_mapping to validate the current source
inventory. Static inspection of these seams finds no compiler main, build,
claim or transport call added by this proposal. The existing three private
compile projections remain accepted provenance, not newly executed compiles.

## Current ABI, map and bounded read plan

The reviewer compared the actual D204 ABI with D199: all 23 sizes and
alignments, all eleven Runner windows, Runner address/size/section and the
separate SETTLE layout/reasons are equal. More strongly, each of the sixteen
selected complete SUMOX_LAYOUT blocks was independently sliced from both raw
GDB outputs; every complete byte sequence is equal without projection and
matches the companion's length/hash. Current equality is observed, not inferred
from source similarity or a historical address delta.

The seven top-level map updates were independently applied in order and
serialized exactly with sorted keys, indent 2 and one final LF. All
intermediate hashes close. The prospective map is 16755 bytes /
`ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709`.
Every other JSON value equals the pinned D199 map, including all 115 selected
fields in sixteen types, field kinds/offsets, nested/array definitions, windows,
enum values and source-only validity masks. Each selected type size agrees
with the current ABI. The masks 1/2/4/7 remain explicitly source semantics;
they are not newly observed target constants.

| Window | Address | Bytes | Current ABI binding |
|---|---:|---:|---|
| trace | 536951180 | 2128 | trace_.report_ |
| report | 537119696 | 1168 | report_ |
| runtime | 537117984 | 600 | runtime_.report_ |
| transaction | 537115448 | 504 | runtime_.transaction_.report_ |
| settle | 537121768 | 28 | Separate settle_probe object |
| gate | 536953520 | 88 | runtime_.transaction_.gate_ |

Each window matches its actual current ABI entry. The Runner is
536951136/169736 bytes/alignment 8. The separate report is 537121768/28 bytes/
alignment 4. Nested before_abort.previous is still captured through the report
window at 537120816/48 bytes. The live previous object at 537115952 remains
omitted; the two objects are not interchangeable.

The reviewer rebuilt every address, length, name, index and basename in the
read plan independently. The fixed sequence is five before-loader chunks,
two before-sketch chunks, six first windows, six second windows, two
after-sketch chunks and five after-loader chunks. Loader chunks remain
65536/65536/65536/65536/1536. Each packaged-sketch span is two chunks
65536/29832, totaling 95368 bytes. All rows match the companion exactly.

There are 26 reads and twelve SRAM snapshot files, indices 7 through 18;
SETTLE remains at indices 11 and 17. The six windows total 4516 bytes per
sample. Independently summed requested bytes equal
`2 * (263680 + 95368 + 4516) = 727128`.
The total shrinks by 304 from D201 solely because both sketch brackets are
152 bytes shorter. No read is added or omitted. The retrieval boundary remains
the two saved result files plus at most twelve declared SRAM files, with exact
packet hash and closing rereads; it does not authorize a new target read.

## Preparation, owners and inhibition

The reviewer independently rebuilt proposed preparation data from the pinned
D201 preparation, applying only the recorded exact string/path identity
changes, replacement of the twelve provenance entries and raw/package
size/hash updates. Canonical output is exactly 9988 bytes /
`519a95f623e3c463842217cdb568cb1909941974b49c36453bfc8f8ea1f8449e`.
Upload/capture binding keys, installed tools, loader/capture configuration,
directories and all fourteen upload absence paths remain accounted for.
The future implementation must obtain the same complete object; matching
only digest strings in its files mapping would not satisfy this preparation.

The scope keeps six top-level keys and eleven distinct file roles. The old
caller-contract role becomes the single new contract, while the old
remote-contract role becomes run_derivation01.json. This is an explicit
metadata role mapping; it preserves both policy inputs and avoids duplicate
scope keys. Actual final oracle and caller/remote review pins remain required.
Offline interpreter/map acceptance and cleanup closure are additional
coordinator gates, not silently enforced by those eleven caller file roles.
No self-hash or guessed future hash is proposed.

All five owner names are distinct: new local native and retrieval directories,
and the adapter/capture/upload names under
`app-motor-const-4bc3a2e6-run01`. The proposal explicitly records
absence_observed=false. Names being new in this document do not establish
current filesystem absence. Fresh owner absence and current board identity
must be checked at native admission and again through inherited guards.

The profile stays MATCH=0, MOTORS_ALLOWED=0, probe1 and default startup. The
empty grant claim concerns app::SetupGrants and peripheral grants; the probe's
explicit exclusive-motor-output ownership flag is still true, as documented
by D205. These distinct grants must not be conflated. No new motor-capable
authorization is supplied. Fixed 150-us/4096 SETTLE bounds, 10000 epochs,
10000000 observer polls, source/config/pins, arbitration and stop behavior
remain unchanged. A new upload necessarily reset-runs the fixed inhibited
image once; it is not a read-only operation and requires the remaining gates.

## Preserved lifecycle and remaining gates

The proposal retains the original one-adapter-claim, one verified push, one
upload and conditional capture sequence; complete success is thirteen
transports over seven labels. Durable intent, prerequisite counters/closures,
exact commands and consumed-owner behavior remain. Outer bounds stay
195/630/60 seconds for upload/capture/prerequisites; inner bounds stay
180/600. The 30000 UTF-16 command limit, 65536-byte reply, 196608-byte action
payload, 1 MiB decoder packet and 65536-byte map bounds are retained.

The only waits remain the declared 30-second pre-sample and 2-second separation
waits with exact types, injected clocks/sleepers, ordering and remaining-budget
checks. Completion of either wait proves no MCU progress or terminal phase.
The eleven-key action envelope, five-key analysis, framing and first-error
priority, returned-only success and durable_unattributed fallback remain.
Partial prefixes and original native failure statuses must survive retrieval
and interpretation. An inner successful report cannot override an outer
transport, framing, source, closing or postcheck failure.

At review, D206 actual cleanup and its separate actual review are not accepted
evidence for this proposal. Their completion is an explicit prerequisite,
followed by fresh /tmp/remoteocd absence and full current identity/process/
tool/source/artifact/owner checks. Initial nonprivileged inventory does not
establish protected-process clearance. This preparation review authorizes no
cleanup retry, credential handling, root command or native runtime use.

The independent oracle must freeze before new implementation inspection or
execution. All 99 accepted native methods (45 remote, 27 actions, 27 caller)
and all 67 corrected interpreter methods must survive, with the 43 explicit
Windows native skips still covered on Linux. The specified recipe/current
map/plan/stale-provenance supplements are additive. First failures, partial
branches and actual admission behavior must remain tested; no success-only
mock substitution is justified. Linux RAM fixtures and dedicated Windows
TEMP/TMP/TMPDIR, serial execution, raw receipts and opening/closing pins are
required before separate source/host/map/interpreter/scope reviews.

Only after those gates, D206 cleanup closure, a committed clean reviewed HEAD
and local check-only may the coordinator admit one fresh native attempt.
This review supplies the preparation assessment only. Root reported later
materialization and an independently preserved preparation-shape refusal;
neither actual implementation nor that failure/repair is accepted by this
data-only review. They belong to subsequent source review after the oracle
barrier.

## Outcome interpretation boundary

The proposal accurately preserves D201's accepted negative result:
FROZEN/SETUP_FAILED, begin_ok=false, zero epochs/polls, lifetime
FINAL_DEADLINE at 154 us/poll 5/fresh 7, followed by current SUCCESS at
132 us/poll 4/fresh 7 during initialization cleanup. The latter does not
retroactively make setup or runtime halt successful. The pinned prior actual
review 690a4164 supplies this comparison; no historical evidence is rewritten.

Future collection integrity must be reported separately from application
behavior. Any statement that current setup passed needs actual begin_ok,
observer/runtime and trace support. Later CALLBACK_FAILURE, timing/runtime
abort, poll exhaustion or other limitation remains reportable even if setup
passed. Current and lifetime first-failure fields, flags, validity/loss fields,
polls/epochs, maxima and halt/inhibition outcomes all remain required.

The standalone first_failure has no stage/epoch/token for automatic callback
association. Two identical sequential sample sets still yield
coherence=UNPROVEN. One successful attempt would not establish elimination of
intermittent SETTLE failures, live getter cost, cycle savings, worst-case timing,
electrical behavior, physical acceptance or a human phase gate. No relaxation
of bounds or automatic retry is justified by the prospective result.

Reviewer writes stop after this file's final size/hash is reported.
