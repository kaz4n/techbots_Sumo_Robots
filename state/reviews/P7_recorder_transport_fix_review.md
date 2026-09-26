# D228 independent recorder transport fix review

Disposition: **FINAL PASS for the scoped source/host correction**. No open
BLOCKER was found in this change. Under D228 and the previously accepted D225
caller scope, this satisfies the review prerequisite for one fresh corrected
static/default/MATCH0/M0 recorder attempt, subject to the existing exact-source
and live admission checks below. It is not evidence of successful delivery.

## Reviewed change

`tools/run_recorder_delivery.py` is 50,735 bytes, SHA-256
`df287140c3fbb24ebc5cc1bc4e98d1974f42522746ab5b33175a26cc807698f0`.
The production diff is limited to the private receiver board module and the
pre-arm check. That module now reports ADB transport and serial `2629958581`,
matching the route already enforced by `ReceiverCommands.remote`. Arming checks
those private bindings instead of consulting ambient `SUMO_TRANSPORT` and the
original board module's ambient target function.

The clone leaves the original board module and process environment intact.
Its `remote` remains the checked command owner's method. The real dump helper's
constructor, connected iterator and connection observer use this private board
module, so the fixed mode also reaches their constructed command arguments.
An altered private mode/target is refused before capture or worker construction.
There is no general transport override or additional accepted command.

Inspected the unchanged command boundary and run sequence. Exact target and
two-command whitelist, ADB executable hash, 30,000-unit command bound, expected
ticket/session, current boot check, prerequisite ordering, one upload, stream
bounds, 900/915-second receiver deadlines, closed latch, bounded kill/reap and
independent closing/error retention remain intact. Firmware, configuration,
profile, upload primitive and checked-in disabled recorder identity are
unchanged by this diff. The existing receiver test fixture adds only its actual
private `board` field; no existing assertion or safety test was weakened.

## Evidence reconciliation

The retained original caller is 50,592 bytes, SHA-256
`9ea1be98388139343be02bc74857c220faa75c32b876b9938f855188d750b6cd`.
I independently compared it with the committed `HEAD:tools/run_recorder_delivery.py`
bytes present during this review: exact match. The two-method old-source negative
control exits 1 and reproduces both the inherited ambient route and the actual
`Explicit identified ADB transport required` pre-arm failure. Its five failure
records include four ambient subcases plus the not-called assertion; its one
error is the missing-environment arming failure. These are two test methods,
not six independent methods.

The fixed Windows and Linux receipts each exit 0. I reconstructed their method
sets from retained stderr: the same **17 distinct methods pass on each platform**,
with no skips or failures. Four new methods cover absent/conflicting ambient
configuration, the real connected iterator's fixed command at a no-spawn
boundary, empty-environment arming, and altered private binding refusal. Thirteen
inherited methods retain command admission, connection ordering and failure,
output limits, timeouts, latch races, partial evidence and cleanup-error coverage.
The test boundaries prohibit an actual ADB launch; these are host results.

The source and both test files currently match all three recorded input pins:

- New fixed-transport tests: 5,016 bytes,
  `279a182df7b249bd00abb5eac8dc5be7c56e9684d1d4b039a94b0bb6e10643b0`.
- Existing receiver tests: 17,016 bytes,
  `79e8ef4bcc1cc28d88135d92aef8123a6e0bc0db03ba3128fa16b3ad5fae8a5d`.
- Corrected caller: `df287140c3fbb24ebc5cc1bc4e98d1974f42522746ab5b33175a26cc807698f0`.

Recomputed every evidence file hash listed in
`analysis/P7_recorder_transport_fix_raw/host_closure01.json`: all match. Closure
SHA-256 is `1f1f9ce47935c33278bb054e14e7fc4fed1d5549156b358ae1f80428f80d6fd7`.
Windows receipt is `2a4ffb144a354a13d38e04593003d192c39143b990649c10835c96e066cff406`;
Linux receipt is `f6317d0755fb1d924d8f3aac28bacb2ddcd75e12e39057f9c8d157c09eb3f115`.
The scoped tracked diff passes `git diff --check`. I inspected the test sources,
raw failures/results, previous D225 review and actual failed native run receipt;
I did not repeat the passed suites or perform any native action.

## Fresh attempt boundary

The prior attempt `36370b3b911165b926583f33448b0b09` remains consumed. Its retained
run result, SHA-256
`663cd5eebc62dc9fde3621ea11a7720f3dbffb3365d3444cb6d9891e574589c3`, reports FAILED,
zero upload attempts, null connection/capture/upload and no closing errors.
This review does not reopen that owner or reinterpret it as a delivery.

After committing the exact reviewed source/test/evidence bytes, use one fresh
32-hex attempt with a fresh positive session under the same D225 caller:
check-only, compile, then run, retaining the same clean reviewed HEAD and exact
source identity throughout. Successful single-query/single-compiler outcome,
all nine compile closing checks, checked artifacts, fixed serial/boot and every
existing live source/dependency/upload/connection admission remain required.
`/tmp/remoteocd` must still be absent; this correction authorizes no cleanup.
No ambient environment workaround is needed. Stop on failure without retrying
or replacing that newly consumed attempt automatically.

D228 explicitly authorizes this corrected fresh attempt after the observed
software defect and review; it does not relax D225's one-attempt lifecycle.
No additional recursive review chain is required for this unchanged scope.
Acceptance of an actual delivery still requires the caller's retained complete
synthetic capture checks. Framing remains UNKNOWN. BOARD ONLY supplies no motor
permission, sensor/electrical acceptance, physical WCET/RAM qualification or
human phase gate. The only persistent file written by this reviewer is this
report; source, tests and native state were not modified.
