# D094 resumable native IMU acquisition

2026-09-23 Asia/Dubai; baseline2f0981c. D051/D075 select this P2 B3/app prerequisite.
Previous goal turn made PROGRESS: D093a15cffd/2f0981c completed the ADC input owner.
Read P2_imu_resume_source_audit.md and P2_imu_resume_test_contract_audit.md. Official
RM0456Rev6 supports retained TXIS/TC/RXNE/STOP phases and controller stretching;
MPU shadow/freshness remains D081's conditional inference, not new silicon proof.

This explicitly amends D079's no-resume API limitation and defines the previously
nonexistent mixed synchronous/resumable-call domain. All legal idle legacy calls,
setup, source/decoder/heading/Robot semantics and established assertions remain.
No new config value, deadline, rate relaxation, pin, library or ownership is added.

## Public lifecycle and progress

Headers imu_bus_unoq.h and imu_acquisition.h freeze first. Bus adds beginMotion,
advanceMotion,cancelMotion,motionReport; Acquirer adds beginRead,advanceRead,
cancelRead,readProgress. One existing object owns both paths. No second Bus,
generic bus router, coroutine, IRQ/DMA, allocation, thread or background service.
Construction/destruction perform no I/O. Caller must finish/cancel pending work
before abandoning its owner; destruction is not implicit hardware cleanup.

AsyncState is IDLE/PENDING/COMPLETE/FAULT. Separate progress envelopes prevent
PENDING from becoming a legacy SampleState or fabricated NO_NEW. started and
completed are invocation pulses: accepted begin sets started only; a newly
terminal operation sets completed only. Report getters always clear both pulses
in the returned copy without changing cached state. Repeated advance/cancel after
terminal returns the retained terminal report with both pulses false and no I/O.
Successful completion permits a later begin; fault does not recover the owner.

Duplicate begin during PENDING returns the existing pending snapshot, no pulse,
clock/backend call or state/budget change. It is a refused start, not extra work.
Idle advance/cancel returns IDLE/default without I/O. Before Bus.begin, beginMotion
returns FAULT/NOT_INITIALIZED,completed=true, no I/O or Bus poisoning; a later
successful Bus.begin can still allow a new beginMotion. After a prior native Bus
fault, beginMotion returns no-I/O FAULT_LATCHED/retained cleanup unless an existing
async FAULT report is available, in which case preserve that first report with
no new completion pulse. Never replay a successful acquisition as a new result.

beginMotion on a ready healthy idle Bus only reads its micros-domain clock once,
sets original started_us=observed_us and polls0, and arms PENDING. No command,
ownership scan or data read yet; delayed first advance consumes the SAME deadline.
Every PENDING BusProgress.acquisition is the exact default empty BusAcquisition,
including zero payload/phase metadata. Only progress started/observed/polls are
diagnostic service metadata; their observation is not a physical sensor timestamp.

## Native bounded work and retained protocol

One advance executes at most one guarded protocol action: CR2 launch, TXDR write,
RXDR read, STOPCF clear, or software phase finalization. No wait-until-ready loop,
multi-byte drain or implicit next action in the same invocation. A missing event
performs a bounded observation attempt then returns PENDING. Fixed-size copying
and validation of at most15bytes is permitted, never an unbounded work queue.

Every active advance consumes at least one existing Operation polling pass unless
the previous total is already exhausted. Existing observe counts one pass and
performs its finite time/ownership/error checks; at most three such passes may
guard one advance. Missing readiness uses one pass; ready events require a fresh
second pass before mutation. Launch may require a third existing guard. Admission
and finalization have their fixed finite checks. This quota is structural, not
a new timing tunable or measured per-call WCET. Cleanup is the sole exception:
one existing bounded50us/8192-pass local-disable routine on terminal failure.

Persist one Operation start/observed/polls/error_flags and private staging/index.
The original elapsed<600us and cumulative8192-pass limits span all phases and
caller interleaving. Elapsed equality rejects; the8192nd observation is allowed,
but a request for another pass when the count is already8192 rejects, preserving
D079's existing boundary. Never renew either at resume, phase change,
first STOP, second transaction, pending return or repeated API call. Clock wraps
retain existing unsigned deadline semantics. Frozen-clock progress still exhausts
the shared pass budget. No more active writes after a guard rejects admission.

Exact script, with a return after each action/finalization:

1. Admit idle ownership/lines and issue the one-byte pointer write START, SOFTEND.
2. Await guarded TXIS/START0, write0x3A once.
3. Await guarded TC/START0, repeated START for1byte/AUTOEND.
4. Await guarded RXNE, read exactly one byte into private storage. Allow STOPF
   with this final byte; an early STOP without RXNE is a protocol fault.
5. Await guarded STOPF with START0/BUSY0 and no extra RXNE; clear STOPCF once.
6. Fresh no-event/idle/ownership/deadline acceptance after STOP clear, using the
   same D079 final checks. Publish readiness diagnostics only internally. Byte0
   yields completed NO_NEW; unexpected bits terminal PROTOCOL. Byte1 selects a
   later motion-start action, not a second transaction inside this call.
7. On the later action record motion_started_us immediately before fresh admission
   and launch, then repeat pointer/TC/repeated-START with15bytes from0x3A.
8. One guarded RXDR byte per advance, permitting immediately recurring RXNE when
   hardware had a byte in its shifter. Only byte15 may coexist with STOPF. Keep
   continuous on-wire burst, AUTOEND final NACK/STOP, then steps5/6 final checks.
9. Complete D081's exact OBSERVATION metadata/status/count15 after final acceptance;
   an invalid second status retains its diagnostic byte but zeros motion payload.

Reobserve current readiness before each mutation. A vanished expected event
returns PENDING (except D079 explicit early-stop/command/mode faults), never uses
an old flag snapshot. Do not require an RXNE-low observation between bytes.
No partial byte/status payload is exposed in PENDING, and no status bit grants
a second sensor generation. Completion time is actual final acceptance, not
wire arrival time or later application delivery. First STOP/finalization and
inter-transaction gaps remain inside the original600us interval.

## Faults, cancellation and legacy collisions

Runtime advances preserve D079 error precedence/flags/ownership/readback/timeout
rules. Any failure calls the existing terminal failed/local-disable path once.
Failed transfers remain all-zero bytes/count, incomplete; retain only already
established D081 readiness/motion diagnostic metadata. Cleanup still cannot regain
lost ownership or synthesize STOP/reset/retry/reenable/pulses. Later native calls
make no I/O. No watchdog guarantees cleanup while the caller stops advancing;
600us is an acceptance deadline, not autonomous physical line release at600/650us.

Explicit cancellation while PENDING selects appended BusStatus::CANCELLED as its
cause, records current clock and safely observable error flags, then performs the
same one cleanup and latches failure. Cancellation does not wait for progress or
attempt a completion. CANCELLED retains precedence over simultaneously captured
hardware errors/deadline; raw flags remain diagnostic. Ordinary advance still
retains original D079 hardware-error precedence. Cancel after terminal does no I/O.

Supported legacy readRegister/writeRegister/readMotion/acquireMotion while native
PENDING act as this same terminal cancellation, returning zero/incomplete CANCELLED;
they never issue their requested new transfer. This selects one simple terminal
misuse rule rather than silently interleaving or inventing a legacy pending sample.
Malformed legacy register requests still win INVALID_REQUEST/no I/O without
altering the pending operation; repeated Bus.begin keeps ALREADY_STARTED/no I/O.
Legal legacy idle behavior is unchanged. The cancellation helper lives with the
existing Bus implementation so legacy builds require no async-only link symbols.

## Actual Acquirer integration

Existing Bus/Setup remain privately owned. beginRead before PROFILE_READY returns
IDLE/default Sample/no backend work. Existing Setup/runtime fault returns retained
FAULT Sample without backend work or recovery. Repeated start/advanceSetup must
not rearm runtime, reset silence, or release a pending operation.

Healthy beginRead clears per-request Sample, retains accepted sequence internally,
checks silence config and current caller time exactly as D081, then calls
Bus.beginMotion once. Original caller begin time is retained for final validation.
Successful native begin requires PENDING/started=true/completed=false, polls0,
started_us=observed_us following/equal caller now in forward half-range, and an
exact default acquisition. Save that native start; return PENDING/default Sample.
Service time may advance internally for chronology/silence, never as sample data.

Every active advanceRead first validates caller forward half-range chronology and
observed20ms silence, then calls Bus.advanceMotion once. No automatic draining or
new begin. A monotonic caller observation at/after silence faults SILENCE before
native advancement, even if native600us is also overdue; a backward/ambiguous
caller observation faults TIME_ORDER at the prior validated time. Abort the active
native operation exactly once with cancelMotion; retain its actual cleanup/status/
error flags alongside the Acquirer semantic fault, then suppress later backend work.

Pending native progress must have no pulses, fixed original start, polls strictly
advancing within the existing cap, observed time following/equal this call and the
last native observation, elapsed<600us, and exact default acquisition. Malformed
phase/pulse/payload/count/time progress fails RESPONSE (time reversal TIME_ORDER)
and cancels once. The first begin observation also passes D081 silence at its
actual native observation; a delayed begin cannot push the silence anchor forward.

Only COMPLETE/FAULT states can declare native termination. IDLE or an unknown
state instead fails RESPONSE and cancels once regardless of transfer status; such
a malformed envelope cannot establish that native cleanup has already happened.
Within a declared terminal state, a nonOK transfer status selects TRANSPORT before
remaining pulse/shape/chronology validation, retaining diagnostics; do not repeat
native cleanup. Successful terminal progress requires completed=true/started=false.
Otherwise only COMPLETE with NO_NEW/OBSERVATION is
accepted. Require fixed original progress start, increasing bounded polls, final
observed_us exactly transfer.completed_us, and all D081 shape/phase/interval checks.
Validate source start against ORIGINAL caller begin, final time against all active
validated caller times and silence. Native-start identity is exact. Decode and
increment sequence only after full acceptance; observation-gap anchors remain real
accepted completions. NO_NEW is only a completed status0 transaction. Return one
COMPLETE Sample pulse, then retain diagnostics without republishing a fresh sample.

Any malformed successful terminal reply or semantic error ends the pending native
lifetime through one cancelMotion call; a real already-terminal Bus returns its
snapshot without further cleanup. Preserve the original successful reply's native
diagnostics when cancellation reports no new terminal operation; when cancellation
actually aborts, use its native diagnostics. Semantic SampleFault remains primary.
No runtime fault clears itself, including later source recovery.

cancelRead while PENDING applies the same caller time/silence checks, calls native
cancelMotion once and returns terminal TRANSPORT/CANCELLED for an otherwise healthy
cancel (or the earlier semantic fault). Idle/post-terminal cancellation is passive.
Calling legacy Acquirer.read while PENDING selects terminal misuse immediately:
invoke the existing Bus.acquireMotion collision path once, retain its cancellation
diagnostics, latch SampleFault::TRANSPORT at the prior validated time, and retire
async state. It neither consumes caller time as a new sample nor ignores an active
transfer on an early legacy time/silence return. Subsequent reads are the same
latched fault. Ordinary idle read behavior and all its old assertions remain.

Only a completed Sample enters Estimator once. This slice adds no estimator,
calibration, yaw, Robot, governor or app policy for pending data. Future app may
retain only already admitted bounded source evidence through existing D084 rules;
it cannot manufacture NO_NEW or move checked/source time to the current tick.

## Implementation and validation scope

Keep native async service in imu_bus_async_unoq.cpp, lifecycle-collision helpers
in imu_bus_unoq.cpp, and pure async Acquirer in imu_acquisition_async.cpp with
small shared final-admission helpers in imu_acquisition.cpp. Headers retain frozen
public interfaces; assigned worker may extend private helpers only. Preserve all
existing tests; new scripted Bus definitions/build registration are additive.

Independent native tests use actual driver source and process-isolated installed
fixture plus additive async modeling, including hardware progression during yields,
retained RXDR/shift byte, TC, final RXNE+STOP, early/extra events, every yield fault,
deadline/poll equality and wrap, one cleanup, collision/cancel, no allocation and
legacy regressions. Independent pure tests validate pending/final shapes, silence,
time, sequence, completion-once and real Estimator/Robot source-age integration.
An inert retained-method target probe must execute no backend at startup. Check
upload refusal, old source manifests, full host/sanitizer/native/tooling regressions,
actual board compile-only/source/ELF identity and fresh separate review.

Every executed service/cleanup needs future D092 complete-tick ownership. The API
alone proves neither useful sensor rate, QTR service margin, physical stretching,
independent clock, loadedRAM, full800us, physical acceptance nor any human gate.
No hardware operation or upload is authorized by this contract.
