# IMU heading bench independent test preflight

2026-09-24 Asia/Dubai. Bounded review of the design, draft contract/public headers,
actual public imu_acquisition.h/imu_heading.h/imu.h/imu_bus_unoq.h/countdown.h,
config and D080/D081/D082/D083/D094 contracts. No implementation body was read.
This reuses the separate D104-D110 author context and the same model; it is not
fresh whole-repository or cross-model review. Only this file is authored. No
tests, implementation, config, ledger, hardware action or phase gate is changed.

## Conclusion

The proposed same-Acquirer/same-Estimator/actual-Services composition is suitable
for an independent test oracle. The coordinator's selected clarifications below
are incorporated in the final draft reviewed here. The bench-only timer anchor
does not need a fabricated START/GO or a new integration/averaging algorithm.
No public API change is required for the identified issues.

The initial draft left the pending-clear point, S-detected deadline closure,
healthy setup diagnostics, failed-operation counters and bias-report publication
open to materially different expected results. The revised draft and explicit
coordinator choices resolve those ambiguities as follows. These are reviewed
choices, not evidence of implementation or full policy adoption.

## Concrete choices reviewed

- **Admission:** enabled=false has unconditional DISABLED precedence. Otherwise
  missing exclusivity/power/rest grants precede missing callbacks, bench config
  and actual Estimator configuration. Mounting remains the Estimator's real
  confirmation/proper-permutation policy. No grant creates a physical fact.
- **Setup:** first advance is due one TICK after begin S. Healthy reports retain
  setup identity, increase advances exactly once and requests by0or1; cleanup is
  NOT_ATTEMPTED and flags0. No request means busNOT_INITIALIZED; after a request,
  busOK. PROFILE_READY needs a nonzero request count. The bench does not recreate
  the48-operation register sequence. Known native faults retain failed diagnostics;
  unknown enums/contradictory healthy shapes remain CONTRACT.
- **Services anchor:** call actual Services.start only after PROFILE_READY's C
  is accepted, using that actual C and current bias. This timer initialization is
  explicitly outside S..C. The public ServiceResult stays default until the first
  actual step returns it; there is no getter or fabricated post-start result.
- **Pending versus terminal:** mark possibly_pending before beginRead. A coherent
  successful COMPLETE clears it only after admitted A and wrapper source brackets,
  before pure consumers. Bad A or bad wrapper source therefore cancels once.
  A later pure-consumer fault or bad C after that coherent neutral result does
  not cancel. A fully well-formed native FAULT clears pending before A because
  cleanup was already attempted, even if A then fails. Malformed apparent FAULT
  does not establish cleanup. Separate cancellation diagnostics never replace
  primary progress or first cause.
- **Chronology versus health:** accepted chronology and healthy operation are
  distinct. A monotonic S reaching the absolute deadline suppresses the scheduled
  normal callback, cancels with actual S if pending, then takes C to close the
  failed poll. Poll and cancellation can measure S..C when C chronology is valid.
  LIMIT before S uses the explicitly historical last accepted timestamp for one
  required cancellation and takes no new wrapper clock. C-detected deadline uses
  that accepted C for pending cancellation, with no further closing observation;
  this late cancellation has no measured duration. Rejected chronology uses the
  historical accepted timestamp and suppresses every later wrapper clock. A native
  TIME_ORDER/SILENCE result remains actual cleanup evidence, not a replacement cause.
- **Consumer delivery:** no Estimator or Services call on PENDING/early polls,
  and no fabricated NO_NEW. Each well-formed completion with admitted A is consumed
  once. During CALIBRATION, a well-formed native FAULT with admitted A must flow
  through Estimator and Services once, preserving SOURCE as first cause. Services
  uses actual A delivery time and the actual Estimate's presence/raw/source identity.
  D083 closes the window before the completion delivered at CAL_END is considered.
- **Bias:** accepted calibration applies once to the same Estimator, without yaw
  reset. Refresh Report.estimate from the actual post-application report: the bias
  field changes while earlier raw/corrected observation values remain unchanged.
  Actual accepted bias/application flag and pure reports remain diagnostic facts
  even if C later fails. The completion closing calibration is never the measurement
  anchor; that is the first subsequent accepted updated heading.
- **Counters/pulses:** completions and pending_results count actual well-formed
  replies independently of later A/C failure. Observations/no_new, observation_fresh
  and maximum observation gap require accepted C with no wrapper fault. In particular,
  an updated Estimate on a CALIBRATION/NUMERIC rejection is retained diagnostically
  but does not produce a successful observation pulse/count. Checkpoint/count/extrema
  publication likewise waits for accepted healthy C.
- **Measurement:** compute relative delta from double-converted published headings,
  not by subtracting floats before promotion or reading the private integrator.
  Anchor0 and the first real observation meeting each boundary give61 actual
  checkpoints under defaults. The final source span may exceed60s; retain it.
  No interpolation, silent ring overwrite, reset or movement-direction inference.

## Independent test scenarios after adoption

1. Verify grants/port/config/Estimator-admission precedence, passive constructors,
   copied/null-context ports, repeat begin, default sketch plus10000loops, terminal
   silence and exact checkpoint accessor bounds. Count actual Native forwarding
   through one Acquirer; provide no legacy read or unrelated owner implementation.
2. Exercise setup first-release equality, skipped release arithmetic, waits and
   no catch-up. Use explicit source reports with every setup counter/enum/status
   boundary. Link actual native Setup regressions separately; a wrapper fixture's
   short valid setup is not evidence of the48-call hardware sequence.
3. Cover first runtime begin, immutable release grid, one pending advance per poll,
   all pulse/default-payload combinations and actual completed NO_NEW versus
   OBSERVATION/FAULT. Compare every public Sample field, including motion arrays,
   statuses, source intervals and diagnostic metadata.
4. Inject bad S/A/C, callback shape/source faults, native faults, S/A/C deadline
   boundaries and poll-limit adjacency. Confirm first cause, clock flag, historical
   cleanup input, cancel-once and measured/unmeasured timing categories. In particular,
   distinguish bad-A COMPLETE from bad-C coherent COMPLETE and pure HEADING failure.
5. Use the actual Estimator and Services with labelled synthetic proper mountings.
   Exercise raw pre-bias calibration, absence and exact source/delivery windows,
   spread equality/rejection, accepted bias once and future-increment behavior.
   The default3s window requires dense samples to retain the2ms heading continuity
   policy. Exactly-two/too-few cases may use mutually valid, explicitly recorded
   temporary calibration timing/minimum profiles, as selected in the draft.
6. Run a full default60s source trial with61 immutable checkpoint records and all
   intermediate observations counted. Derive constant/ramp and signed rotation
   expectations analytically from real observation completions. Include an excursion
   returning near the anchor, so endpoint drift cannot conceal earlier movement.
   Preserve nonzero premeasurement yaw to prove no reset or second integrator.
7. Check natural uint32 wrap, 2000us source-gap equality/one-beyond, deferred
   completion/closing-clock failure, source endpoint versus delivery, and exact
   slot publication/final pulses. Use normal and sanitizer isolated copies plus
   valid/invalid config profiles; zero divisors must compile without substitutes.

## Reachability and limits

No finite60s first-sequence1 trial naturally executes a uint32 sequence wrap.
The existing Estimator remains authoritative: a source gap beyond its bound
faults HEADING before a checkpoint-gap defense can turn it into a new successful
measurement. Under valid checkpoint_period>=heading_gap and admitted observations,
crossing a second unfilled boundary in one update is unreachable; source-review
that defensive branch rather than privately seeding indices. Likewise, finite
bounded rates, initial bias and lifetime do not justify fabricating overflow of
the Estimator's private accumulator to claim numerical-guard execution.

Finite poll/deadline bounds do not advance when the caller stops. No successful
completion means bus shutdown, and no cancellation result proves electrically
idle lines. Synthetic mounting/rates, nominal1kHz pacing, observed source times
and a60s software endpoint do not prove real sensor generations, stillness,
mounting, calibrated time, drift/rotation accuracy, whole-app800us or a phase gate.

Final draft verification: SHA256
`c08128b2cad63bdcb4f7ceea5da7b74d8111935b8532621108799213cd6db84d`.
The pending-clear, S/A/C deadline, healthy-publication, mandatory fault delivery and
retained actual bias clauses match the reviewed choices. No further material
oracle ambiguity was identified. This remains a preflight, not policy adoption.
The final A-deadline paragraph makes the chronology/health distinction explicit:
an already-returned well-formed terminal reply may undergo bounded diagnostic
pure delivery after admitted A, including real bias/report changes. Healthy
COMPLETE still requires source brackets before pending clears; PENDING cancels
at A. C may measure the failed poll, but no checkpoint, successful observation
publication, measurement or healthy phase transition follows. Malformed or
source-invalid replies are not delivered, and no further normal native operation
is allowed. Earlier native/shape faults retain first-cause priority.

Next action: coordinator adopts the final contract/public headers/constants
before independent test authoring.
