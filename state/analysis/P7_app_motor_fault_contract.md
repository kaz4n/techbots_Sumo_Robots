# D186 inhibited full-application callback diagnostic

25 September 2026. HOST implementation and staging only. Source evidence:
D160/D161 static/default/M0 full app latched MotorGate IO3 with unknown first
callback; D184's dynamic isolated four-command Runner passed. D185 current raw
ELFs/packages equal D139/D138. Default dynamic allocation still has a592B modeled
deficit; MATCH's conditional864B span is a different profile. No timing limit,
pin, control behavior, config value, recorder capacity or established test changes.

Add bench/app_motor_fault with the public app_motor_fault.h interface, one small
implementation and sketch. Reuse only existing motor_fault::Trace by composition,
not its synthetic-command Runner. One Trace forwards to one native motor port;
one unchanged app::Runtime owns the real Transaction, Robot, MotorGate and recorder.
No production source or shared CMake change is required. Constructor/accessors
perform no I/O. No heap, unbounded loop, delay, serial/network/Bridge command path.
MATCH0/MOTORS_ALLOWED0 remains enforced by the unchanged Trace header assertion.

## Admission, observation and termination

Runner.begin takes existing motor_fault::Grants. A first denied grant enters
DISABLED and returns true with no native/clock callbacks. Any later begin is false
and passive. Granted begin sets RUNNING, begin_called before the real call,
Trace context SETUP/0, then calls runtime.begin(app::SetupGrants{}) exactly once.
Empty peripheral/service grants deliberately match the current unconfirmed main
app and keep this bare-board diagnostic inert if config declarations later change.
No physical grant is inferred. Save exact begin result and begin_finished after
return. A false begin freezes SETUP_FAILED, regardless of secondary trace issues.
A true begin uses the ordered stop rules below; return true only if still RUNNING.

An active poll sets Trace context APPLY with prospective epoch ordinal
runtime.report().epochs+1, then calls runtime.step once and retains its bool.
Early polling never invents ticks; real Runtime owns clocks, release skipping,
wrap/equal/backward admission and STOP tail. A Robot STOPPED value or contract bit
alone is not an extra stop condition: retain existing Runtime stop behavior.

After successful begin or each active poll, choose the first applicable reason:
1. Trace has_failure -> CALLBACK_FAILURE (first false callback stays retained).
2. Trace overflow or timing_fault -> TRACE_INVALID.
3. If transaction.report().decision_made: require consumed, applied_valid, feedback
   token == actual Robot token, motors_enabled=false and both feedback duties
   exactly0. Otherwise APPLICATION_INVALID. No new Gate fault enum interpretation.
4. Runtime phase FAULT or STOPPED -> RUNTIME_TERMINAL.
5. Runtime completed epochs >= EPOCH_SAMPLES (existing fixed evidence extent4)
   -> EPOCH_LIMIT. No synthetic commands or extra catch-up applications.

Freezing first enters FINALIZING and stores the reason plus exact copies of
RuntimeReport, TransactionReport and transaction.previous into before_abort,
with before_abort_valid=true. This precedes any diagnostic abort, because abort
can invalidate the last application receipt. Set Trace context HALT with the
current completed epoch count; set abort_called before calling runtime.abort once.
Set abort_returned and FROZEN only after it returns. Runtime's own terminal abort
may be a no-op; preserve its actual HaltResult, including absent/unconfirmed setup
cleanup evidence. Do not fabricate a fresh halt receipt. First failure/reason
survive cleanup failures. In FINALIZING/FROZEN/DISABLED all polls and repeated
begins are passive. These phases describe observation progress, not hardware PASS.

Trace contexts describe outer SETUP/APPLY/HALT calls. Cleanup performed inside
Runtime::step remains labeled APPLY; this is not an inner operation identifier.
Existing native setup callbacks can block; the in-progress marker does not prove
a timeout. Trace/copy overhead perturbs timing, so observations cannot establish
the original fault's cause or R4 WCET without further evidence.

## Sketch and staging

Construct NativeSources, UnoQPort and FIFO8 UnoQDumpPort exactly as main app,
passing their real ports to the new Runner. setup admits only
SUMOX_MOTOR_FAULT_PROBE==1; checked-in default remains0. loop only polls when active.
Preserve the main sketch's EMPTY macro protection around native includes.

tools/board_tool.py stage adds only the bench/app_motor_fault special case:
copy the two canonical bench/motor_fault/src/motor_fault.h/.cpp bytes to the new
staged src root after ordinary local-src copying. Require plain source trees,
both exact files present and no destination collision; preserve partial staging
on failure under existing fresh-attempt ownership. No copied trace implementation
is checked into the new bench. Source and shared files remain untouched.

Generic flash_profile must reject this new sketch for every flag combination
before transport/staging: it requires a later reviewed static-only native route.
Do not register it in the dynamic app-build policy or generic upload allowlist.
New stage attempts preserve every prior policy-denied path. No target operation
is authorized by this host scope or its tests.

## Validation and next native dependency

Separate tests derive from this contract/public headers, never implementation
bodies. Freeze tests before execution. Exercise the real Runtime/Transaction/Gate
using controlled motor callbacks and absent peripheral grants: denied/repeated
admission, four real epochs/41 successful callbacks, early polls/skips/wrap/stall/
reversal, setup and each application/cleanup callback failure, first-failure
retention, pre-abort receipt preservation, terminal passivity, no native HIGH or
nonzero PWM, missing ports/clock and unsafe compile flags. Check default/explicit
sketch binding with controlled headers, staged exact shared bytes, link/collision/
missing-file refusal, and generic command refusal before I/O. Run focused normal
and ASan/UBSan builds serially in owned RAM, plus unchanged relevant safety tests.

For native reproduction use a new static/default/MATCH0/M0 scope after source
review and host validation. Historical static167792B span/94352B linker tail only
makes added tracing plausible; new ET_EXEC/package, initialization/native binding,
ABI and capture addresses must be checked. No reuse of D149 offsets, D173's2592B
decoder, historical scopes or unqualified dynamic loading. Actual board work,
fault reproduction/repair, RAM/stack/WCET and all physical/human gates remain open.
