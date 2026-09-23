# D109 independent author coverage

Expectations come from the adopted D109 contract, the public bench/Reader/adapter
headers and D085/D089 contracts. The author retains earlier D104-D108 context;
this is independence from D109 production bodies, not fresh whole-repository or
cross-model review. Test development and implementation proceeded in separate
contexts after the expectation checkpoint; final executable tests were frozen
before any execution. No implementation body was read.

`qtr_raw_cases.cc` contains 32 ordinary cases plus two actual native-binding and
default-sketch cases. Loops and subcases cover multiple independently selected
stimuli. Snapshot equality compares every declared member, including all four
pads, per-pad status and every cleanup field; it does not compare padding bytes.

- The actual shared raw validator checks literal pending, complete, mixed
  finite-LOW/right-censored, wrapped and malformed records. Finite intervals use
  D085 lower/upper equations. Timeouts retain distinct uncapped lower bounds.
- Lifecycle coverage includes passive construction/accessors, prebegin polls,
  default grants, missing callbacks, one-attempt begin, neutral/active stop and
  terminal silence. Successful command ordering and source timing are explicit.
- Capture coverage includes all 128 immutable slots, pointer identity, count and
  inaccessible bounds, final true/fresh publication, and bad C hiding a tentative
  slot. Configured capacity 1 repeats applicable acquisition cases; capacity 0
  executes only raw-fixture/passive/missing-callback/zero-capacity cases.
- Source tests cover first/contiguous sequence, exact advances, active identity,
  source brackets, spacing, pending phase progression, truthful NOT_DUE, every
  identity component on NOT_DUE, changed payload, late status and boundary
  straddle. Source guard ownership remains with the existing native Reader.
- Clock tests cover equal clocks, natural uint32 wrap, reverse/half-range gaps,
  aggregate operation closure, half-range minus one, and accumulated source age
  over multiple individually valid observations. Failed S/A/C/P/Q observations
  suppress subsequent wrapper clocks while required cleanup still occurs once.
- Failure tests preserve first cause, raw qualification and primary/cancellation
  snapshots separately. They distinguish malformed data, provider faults, source
  order, explicit cleanup failure and clock evidence. Named timing and callback
  counts include failed semantic/provider operations and valid cleanup brackets.
- Heap wrappers cover begin/start/pending/stop and every complete append. Native
  tests compile the actual new binding and default sketch while replacing only
  the existing public Reader method definitions. The substitute maintains its
  own declared result_ as expressly permitted; no Runner private state is seeded.
- The sole old-test amendment adds the literal QTR_BENCH_FRAMES=128 expectation.
  The unchanged D106 wrapper invokes unchanged D093/D090 registry tests and all
  18 original checks. A copied 129 profile must fail exactly the original value
  assertion; the three existing D096 negative profiles also remain unchanged.

Normal and ASan/UBSan modes cover capacity 128, 1 and 0 plus the actual binding
and default sketch. Three forbidden MATCH/MOTORS flag combinations must fail
their compile-time assertions. Intentional profile filtering is recorded, not
reported as broad test execution or silently dropped coverage.

Limits: no GPIO/electrical/native acquisition is exercised by these substitutes;
no board, transport, target timing or physical colors are qualified. Finite
128-frame public operation cannot naturally reach a uint32 sequence wrap or
counter saturation. Typical counters are executed; saturation branches/callsites
remain source-review evidence, not a claim of billions of executed polls.
