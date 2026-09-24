# D136 independent public companion-analysis oracles

Prepared from the adopted `state/analysis/P5_abort_analysis_contract.md`, D135's
metadata table in `P5_abort_evidence_contract.md`, and unchanged D073/D074/D130
contracts/public test fixtures. This author has not read an analyzer implementation,
imported these drafts, run tests, invoked a compiler, or changed `src`, `tools`,
`tests`, build configuration, protected tests or shared ledgers for this task.
The files remain unvalidated drafts in this owned analysis directory until root
reviews/freezes them and authorizes transfer and first execution.

## Files and planned execution

- `opener_abort_fixture.py`: a small Source/Bundle plus unittest assertion helper,
  reusing the unchanged `countdown_analysis_fixture.py` and its independent D073
  wire fixture. It uses no analyzer parsing code or firmware implementation.
- `test_opener_abort_wire.py`: 25 methods for exhaustive metadata, wire grammar,
  routing, chronology, thresholds and prohibition on inferred evidence.
- `test_opener_abort_cohort.py`: 19 methods for owner/source declarations, all
  reported loss, duplicate attempts, ten-slot accounting, physical declaration
  language, public API and actual CLI behavior.
- `test_opener_abort_source.py`: 20 methods for exact cohort/source schemas,
  historical configuration extraction, lexical/range admission, all four mode
  availability combinations, path rules and source-invalid precedence.
- `test_opener_abort_binding.py`: 10 methods for bounded reads, accepted-byte
  identity, mutation, descriptor checks, no manifest/frame reread, unchanged
  inputs, import/API quietness and denial of writes/network/program execution.

Total: **74 unittest methods**, with loops/subcases rather than expanded fixtures.
The pure `decode_cue(value, mode)` oracle exhausts all 65,536 uint16 values,
checks every wrong attempted mode for every accepted word, and separately rejects
bool/noninteger/out-of-range inputs. It independently translates the literal D135
mode/phase/cause/mask/snapshot table; no production helper computes expectations.
Representative full CSV cohorts verify the helper is actually enforced by the
public analyzer, including DIRECT, mirrored SIDESTEP and ARC, WAIT HOLD/inner
SIDESTEP, ignored-front PIVOT side cues, snapshot-plus-current front and invalid
front/snapshot/phase combinations.

Root may later run from this draft directory with:

`python3 -B -m unittest discover -s state/analysis/P5_abort_analysis_public -p 'test_opener_abort_*.py' -v`

Expected eventual transfer, only after authorization: the five `.py` files to
`tests/tooling/` with the same basenames. Root owns integration/runners. Symlink
and descriptor-race cases are intended for the existing Linux/WSL tooling run;
no platform skip silently removes those checks. Existing D130/CSV regression
suites remain unchanged and run separately under root's established pipeline.

## Coverage and exact boundaries

Every legal prefix/terminal is classified separately, including header-only
INCOMPLETE, explicit HANDOVER_FAILED and late exhaustion. Full ordinal adjacency
applies to HEADER/START and each retained decision suffix prefix; ordinary events
may precede the receipt terminal without invented batch boundaries. Unknown
details, exact value bounds, duplicate/tail/retry grammar, P4 headers/details,
START/GO uniqueness/mode/release, owner epoch/go_seen contradictions, absent GO
versus later GO, and unsigned chronology have independent assertions.

Arithmetic includes 999/1000/1001us, alternate historical bounds, long valid
delays, zero endpoints, ordinary wrap, reversed and half-range offsets, exact
handover/failure/preemption D, and GO-time DIRECT read pairs preceding GO.
INVALID_SOURCE/INVALID_RECEIPT clocks cannot manufacture an elapsed requirement.
Routing checks centered threshold1 versus threshold3/max, off-center front,
side/rear, ignored-front side causes routed by current front, and WAIT's recorded
zero-duty frame. Frame duty/state and ordinary events cannot fill missing markers.

Source tests require all seven historical declarations, exact bytes/SHA, exact
M0/M1 flag strings, supported ranges/capacities, canonical current header supplied
explicitly as a snapshot, lowercase suffix and whitespace, comments/quoted text,
declaration uniqueness, ordinary unconditional reads, malformed/duplicate/missing
declarations, macro/conditional mentions, expressions, huge integers, physical
splices, digraph directives and unterminated constructs. No repository fallback
is permitted. Source failure still calls the unchanged validator for all attempts
and publishes no decoded timing under an unknown configuration.

Schema/path tests cover exact keys and integers, duplicate JSON keys, nonfinite
values, ASCII IDs/counts, local absolute and parent-relative paths, UNC/URI
rejection before declared file access, 256KiB cohort/config boundaries, missing,
nonregular and symlink inputs, 16MiB CSV/16KiB manifest bounds. Descriptor
identity/type/size/mtime checks and same-size/restored-mtime rewrites test the
accepted-byte boundary. Config is read once; events and summary are bound to
accepted SHA/byte/row counts; accepted manifests and frames are not reread.

Aggregation retains original ten scheduled slots, explicit logical failures,
late numeric values, exclusions and every original ID/order. Every D074 detailed
loss field disqualifies visible success; an aggregate-only contradictory loss
flag stays validator INVALID. M0/unsealed/open/unknown/missing declaration cases
retain trustworthy diagnostics but cannot pass a cohort. Reused hash triples
invalidate all aliases/copies. Qualified COMPLETE observations alone supply
extrema. Ten explicit failures are COMPLETE evidence with timing FAIL. Synthetic
M1 may qualify logically; only ten explicitly hardware_reported passing manifests
are ELIGIBLE for separate physical review. All four acceptance/provenance boolean
claims remain false, including ELIGIBLE reports. CLI returns0 only for PASS,1
for checked nonpass results,2 for usage; no write/upload/repair mode is accepted.

## Pre-freeze clarifications and limitations

Root adopted the public pure cue seam under D051 before any execution. Root also
made terminal metadata explicit: COMPLETE retains20/1, HANDOVER_FAILED retains
25/actual state, EXCLUDED retains its observed diagnostic pair, unfinished/no
trace has null terminal fields; observed state19 or25 supplies handover_state.
The canonical header's derived constants required clarifying that unique
declarations are required while ordinary unconditional uses are allowed.

Unchanged D074 closure rules take precedence over shorthand about unknown
closure: absent manifest or valid unknown/open closure is incomplete; a supplied
null or missing required closure invalidates its manifest. Aggregate incomplete1
without any detailed loss is a D074 consistency contradiction, not valid incomplete
owner evidence. These static draft corrections precede first execution and no
test has been accepted/relaxed in response to an implementation result.

For a nonnull manifest identity mismatch, tests require INVALID qualification
and binding, null endpoint/elapsed fields and NOT_EVALUATED logical/timing.
The separately parsed trace may be COMPLETE or INVALID, as root clarified;
the tests do not impose analyzer evaluation order. The earlier source-invalid
path remains exact INVALID with no decoded fields.

The fixtures explicitly declare synthetic bytes. A hardware_reported string is
only adversarial caller-declaration input, never an observed hardware trial.
Neither tests nor analyzer reconstruct T/C, full request token, actual route
invocation, EN, physical cue onset/age, clock calibration, PWM edges or mechanics.
No signed source-to-image relationship, common physical attempt, roster
completeness, atomic cross-file snapshot, RAM/stack fit, WCET or phase pass is
claimed. Existing producer tests and physical review retain those responsibilities.
