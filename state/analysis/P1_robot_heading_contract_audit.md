# Robot GO heading ownership audit - 2026-09-23 Asia/Dubai

Status: **recommendation only, not accepted policy or implementation evidence**.
Coordinator must record the selected material choices under a new D-051 decision
and amend the affected public contracts before Robot implementation/tests.

Scope: B0/B3/B5/B7/B14; D-024/D-031/D-054/D-056; public types, countdown,
Fusion/Stuck/Phantom/BearingMemory, motion, opener, FSM, edge and logframe headers;
P1_robot_interface_audit.md item 6. No opponent/FSM/motion implementation or test
source was read. countdown.cpp was inspected earlier for the separately assigned
menu implementation, not as proof of this proposed Robot policy. This task owns
only this new audit; no source edits, build, hardware operation or commit.

## 1. Finding and recommended ownership

B0/B3 require match heading zero at GO. Lifecycle currently returns its GO pulse
as heading_reset_requested and says the caller applies a heading change through
HAL/app. StuckFilter instead requires continuous accumulated yaw for each live
candidate's observed min/max span, and its declared faults clear only on reset.
Fusion has no coordinate-rebase API and owns that filter privately.

Feeding Fusion a GO-rebased yaw can invent rotation. For example, a detected bit
observed at constant raw yaw 720 degrees before GO and local yaw 0 afterward
would appear to span 720 degrees without moving. Resetting Fusion at GO avoids
that particular candidate but incorrectly clears reset-only stuck faults,
debounce/contact history and retained world/phantom evidence. Merely asking HAL
to reset next tick also changes the coordinates underneath a same-tick opener
or escape reference. None of these is an acceptable composition shortcut.

Recommend two explicit coordinate domains:

| Domain | Owner and consumers | Lifetime |
|---|---|---|
| Raw continuous yaw `H` | Caller supplies an unreset integrated coordinate; Fusion, StuckFilter, PhantomFilter and BearingMemory always consume this domain. | Continuous for the Robot lifetime; GO does not reset or wrap it. |
| Match continuous yaw `M = double(H) - O` | Robot owns origin `O`; motion/scripts, match frame heading and exposed match-world/inward contexts consume this domain. | Establish on actual GO before any same-tick moving entry; then fixed, except the explicitly defined first-observation anchoring below. |

Robot never commands a HAL yaw-integrator reset at GO. It does not modify input
measurements or Fusion's private histories. The raw caller stream may include
bias-corrected integration; "raw" here means **unreset coordinate**, not the
pre-bias gyro sample used by D-024 calibration. Use separate unambiguous field
documentation for these two meanings.

## 2. GO and recovery truth table

B14 explicitly requires timed fallback when IMU initialization fails. Missing
heading history must therefore not silently become a global motor inhibit.
Define an initial coordinate separately from a measured orientation:

| Observation at actual GO | Origin and local coordinate | Evidence and subsequent recovery |
|---|---|---|
| `imu_ok` and finite current `H` | Capture `O = double(H)` from this exact tick; `M = 0` exactly. | Healthy current coordinate; record origin source/current timestamp. |
| IMU unavailable, with a previously observed finite healthy raw yaw `H_last` | Capture `O = double(H_last)`; retain local coordinate 0 while unavailable. | Last-known coordinate only; `imu_ok=false`. On recovery use `M = double(H_current)-O`; do not re-zero or change captured targets. |
| IMU unavailable, no finite healthy history | Use nominal local seed 0 and mark the raw origin **pending**, with no measured world evidence. | Start the specified timed fallback with `imu_ok=false`. On the first later finite healthy raw observation `H_r`, capture `O = double(H_r)-M_nominal` before any motion step; here `M_nominal` remains 0. This first recovered local sample equals the existing nominal coordinate, with no reference jump. |
| `imu_ok=true` but current yaw is nonfinite | Do not claim a healthy zero or silently reinterpret malformed healthy data as ordinary IMU absence. | Preserve the consumed-invalid-heading/zero-demand behavior of the relevant motion contract; coordinator must define the Robot-level diagnostic/fault disposition explicitly. |

The nominal zero is a coordinate definition, not a synthetic healthy yaw. Until
the first real healthy observation, Fusion gets `imu_ok=false`, world/inward
evidence remains invalid, and no estimated physical turn is fabricated from
elapsed time or motor duty. That preserves B14 while acknowledging that rotation
performed during an outage cannot be recovered from the absent observations.

Pending-origin recovery does not replace any local motion reference, restart a
segment, rerun GO, or extend a timeout. Existing Turn and Search fallback latches
remain latched. Straight may resume correction against its original local
reference and Arc may resume measured sweep according to their existing recovery
contracts; their original deadlines remain in force. No unobserved rotation is
credited as measured arc/scan progress. Later losses retain the established
origin and last local coordinate; only the first ever healthy observation can
resolve the pending origin.

Public entry contracts currently use "initial/last-known" and, in several
compositions, "no synthetic yaw". Explicitly clarify that a finite nominal
initial coordinate is allowed **only with unavailable IMU**, while it never
supplies a healthy observation, world memory or inward evidence. This is a
necessary narrow contract clarification, not permission to turn `imu_ok` true.
Record origin provenance (CURRENT_GO, LAST_KNOWN, NOMINAL_PENDING, FIRST_RECOVERY)
and its actual observation time in the future Robot diagnostics. A recovery
origin is not evidence that physical yaw at GO was measured as zero.

## 3. Same-tick transaction and history handling

1. Admit one fresh tick and retain its actual raw `H`, validity and entry state.
   Obtain each line/opponent observation once. Fusion observes raw-domain yaw
   with the state before arbitration. Lifecycle consumes that same tick's
   genuinely confirmed opponent/line data; no second Fusion observation is used
   to obtain match-relative bearings after GO.
2. Lifecycle alone determines accepted START and actual GO, including its
   existing cancellation/STOP precedence. A canceled/STOP-suppressed deadline
   cannot establish an origin. A real GO may still be vetoed by a stronger final
   motion inhibit; distinguish its pulse from final motor permission.
3. Resolve the GO origin, or a pending origin's first healthy recovery, before
   creating any moving reference or using a world/inward context on this tick.
   Update the last healthy raw/local coordinate only from genuine healthy finite
   input. Unavailable input payloads, including finite stale values, do not become
   new measured history. For fallback supply the retained/nominal finite local
   coordinate with `imu_ok=false`.
4. Build match-domain views of current bearing and retained world/inward history;
   then arbitrate edge/opener/normal motion. Persistent edge at GO starts its
   permitted escape using the same local coordinate the opener would receive.
   An all-white/final STOP/fault inhibit still wins. An executor's stale captured
   reference must never survive into a newly established coordinate epoch.
5. Preserve D-056: optional read-only preview, one final Fusion commit, and one
   final governor pass. A rebase is not another observation or contact event.
   Publish the actual GO pulse and the match-relative frame from this transaction.
   Do not forward heading_reset_requested as a delayed HAL-integrator reset.

Only inactive/transient script state may be initialized as required by its
existing lifecycle. In particular, do not call Fusion.reset or Escape.reset to
implement GO: both own sticky safety state. A true Robot reset may reset them in
the ordinary inhibited startup path; GO is not such a reset. If an active moving
executor unexpectedly straddles a GO epoch, treat it as an invalid composition
state rather than silently using its old reference or clearing sticky faults.

Keep canonical retained world evidence in the raw domain. Let `W(x)` wrap to
`(-180,180]`, with both +/-180 ties represented by +180. For an existing raw world
bearing `A_raw`, its match view is `W(A_raw - W(O))`; compute in double with bounded
operands. Preserve validity, last-seen time, front-side recency and all ages.
Coordinate conversion neither refreshes evidence nor resurrects expired memory.
Relative bearings and left/right recency require no yaw conversion.

For a current valid relative bearing `r`, the match-world view can be formed as
`W(W(M) + r)`, using the same current local coordinate. In particular a healthy
GO sample has `M=0`, so the current match-world bearing is `r`; do not round a
large raw-heading-plus-bearing intermediate before subtracting the GO origin.
Fusion's native world/phantom data stay raw-domain; only externally consumed
copies are transformed. Pending origin means no match-world projection until
the first healthy sample anchors it. Native world validity is still required.

Store inward evidence only on the real Escape.inward_valid exit pulse. Retain
the actual raw yaw from that same input tick plus its actual timestamp; derive
`M_inward = double(H_inward)-O` when assembling SearchContext. This avoids
reconstructing a raw measurement by adding a large origin to a rounded local
float. A retained/nominal fallback coordinate never becomes new inward evidence.

## 4. Numerical and timing boundaries

- Subtract float inputs after promotion to double. Two equal finite raw samples
  give exact local zero even at very large magnitudes. Float precision already
  lost by the provider cannot be recovered or advertised as measured resolution.
- Keep the origin and conversion intermediate in double. Check finiteness and
  float representability before passing local coordinates to today's float APIs.
  Opposite near-maximum float samples have a finite double difference that need
  not fit float. Do not clamp, modulo-wrap or pass infinity as healthy motion
  yaw. Recommend the explicit consumed-invalid-coordinate/zero-demand diagnostic
  path; its Robot fault lifetime requires the new decision. This is different
  from expected B14 IMU-unavailable fallback.
- Raw and match continuous headings are never angle-wrapped for StuckFilter,
  Arc or Search sweep evidence. Only directional world/error views wrap. A
  179->181 observation is a +2-degree continuous change, not 179->-179 input.
  The caller must not reset/wrap the raw integrator while Robot state survives.
  An unavoidable provider coordinate reset needs a separate explicit epoch/rebase
  contract; the core cannot reliably infer it from an arbitrary numerical jump.
- Reduce an angle before adding a small relative bearing or subtracting a huge
  origin: `W(W(H)+r)` and `W(A_raw-W(O))`. Even double cannot preserve a 15-degree
  addend next to every finite float magnitude. Public headers alone do not prove
  that existing BearingMemory/Phantom arithmetic meets this extreme-value case;
  test their public behavior before claiming translation correctness. Any repair
  is a separately reviewed bounded arithmetic change, not established by this
  audit. Preserve B7 strict tolerance and +180 RIGHT-tie behavior.
- Immediate duplicate Robot timestamps must not capture another origin, perform
  first recovery twice, replay GO or resample filters. The future Robot duplicate
  contract must cover this atomically. Micros wrap affects elapsed-time arithmetic
  only; it does not change the yaw origin. Required per-call gaps remain below one
  uint32 wrap, and evidence ages must not resurrect after repeated wraps.
- D-024 calibration accepts/rejects a gyro bias, not a coordinate epoch. Apply a
  published bias to subsequent integration increments under the app contract;
  do not retroactively reintegrate already-observed raw yaw or zero it. A delayed
  call that finishes calibration and reaches GO uses that call's actual yaw for
  its origin; it cannot request a second sensor sample to manufacture simultaneity.
- Frame heading remains accumulated match yaw. Preserve packFrame CLAMPED/INVALID
  status and IMU_OK truth; do not wrap large yaw merely to fit the frame. Origin
  provenance needs explicit Robot diagnostics/telemetry policy, not a silently
  repurposed flag or changed existing 25-byte frame layout.

## 5. Required independent regression matrix

| Case | Required result |
|---|---|
| Constant raw yaw 720 across GO; bit held beyond OPP_STUCK_MS | Match yaw becomes 0; Fusion candidate span stays 0; no fake stuck fault. |
| Live candidate with small real pre/post-GO change | Candidate age/min/max survive GO; only actual raw range contributes. |
| Raw span exactly 360, adjacent above, duration equality/adjacent | Existing strict span and time thresholds unchanged, including across GO. |
| Stuck fault already declared, input later clears, GO occurs | Fault/masking survive; only true reset clears it. |
| Retained phantom marker and world memory across origin change | Native marker/mask outcome unchanged; exported world angles rotate coherently; no new event/age refresh. |
| Current GO with raw yaw 1010 and relative +15 | Local yaw 0 and current match-world +15; one observation/commit. |
| Prior memory at raw yaw 1000 and relative +15; GO at 1010 | Match memory points +5, with original timestamp/recency/validity. |
| Prior real inward yaw 1005; GO origin 1010 | Match inward -5 if still eligible; no refresh of its age, no fabricated exit. |
| Missing-at-boot IMU, no healthy history, every supported opener/edge fallback | Nominal zero with imu_ok=false; existing timed fallback works; no global stop solely for absence, world/inward evidence invalid. |
| No-history first healthy recovery after timed motion started | Anchor once at frozen nominal local coordinate; no target jump, GO replay, deadline extension or credit for unobserved turn. |
| Missing at GO with real last-known raw history | Seed from that history; later healthy raw deltas use the fixed origin, not recovery re-zero. |
| Turn/Search loss and recovery; Straight/Arc recovery | Preserve each primitive's documented latch/resume behavior and exact original timeout boundaries. |
| Healthy NaN/+Inf/-Inf vs unavailable arbitrary yaw payload | Invalid consumed healthy coordinates cannot become healthy zero; unavailable payload ignored while honest fallback continues. |
| Persistent edge, all-white and STOP/cancel ties at GO | Same-tick local origin used for permitted escape; safety arbitration intact; canceled GO creates no epoch. |
| Exact +180/-180, adjacent tolerance values, left/right mirror | World range and RIGHT tie preserved; no coordinate-induced strict-tolerance change. |
| Very large equal finite raw yaw at GO; small relative bearing | Exact local zero; small bearing survives reduction; no intermediate overflow/erasure. |
| Finite raw pair whose difference exceeds float range | Explicit coordinate error/zero-demand disposition; never clamp/wrap into a healthy command. |
| Provider raw coordinate discontinuity | Declared unsupported without an epoch contract; test cannot count a reset as real yaw evidence. |
| Duplicate GO/recovery timestamp with changed input; repeated micros wraps | No second origin capture/event/filter sample; no evidence-age resurrection. |
| Calibration finish coincides with sparse GO call | Same input yaw supplies origin; accepted bias affects later increments, not already-observed coordinates. |
| GO frame, missing-heading frame, large accumulated frame | Zero/retained-or-nominal heading with truthful validity; preserve codec status and unwrapped accumulated yaw. |

## 6. Decision boundary and next action

Preferred course is the raw-Fusion/match-Robot split plus explicit nominal
initial fallback and first-recovery anchoring. Before implementation, record one
coherent decision defining: ownership of raw versus match coordinates; logical
meaning of the existing heading-reset pulse; no-history fallback/recovery;
invalid healthy/unrepresentable coordinate disposition; origin diagnostics; and
history projection without resets or freshness changes. Clarify B0/B3/B14 and
the affected public entry contracts visibly. D-024 and D-056 do not themselves
authorize these coordinate choices, and this audit does not self-approve them.

If hardware-integrator zeroing is retained instead, add explicit narrow rebase
APIs before use. They would have to transform every live Stuck candidate min/max
without changing age/fault bits, Phantom marker, BearingMemory/current cache,
Robot world/inward history and active motion reference atomically, while
preserving pending Fusion observation/commit and event semantics. That is a
larger change with more precision and same-tick failure surfaces; never substitute
reset() for it. No examined requirement needs physical integrator zeroing rather
than a documented logical match zero, so this is not the recommended route.

Next: coordinator selects/records the contract, publishes the minimum Robot
interface, then commissions independent spec-derived tests including the matrix
above. Existing arithmetic may need separately scoped extreme-value tests before
claiming all-finite coordinate equivalence. No target timing, physical yaw,
integration freshness, human gate or motor permission is established here.
