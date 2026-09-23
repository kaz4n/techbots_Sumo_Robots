# D-075: MotorGate software boundary (P2 B4 preparation)

The user explicitly resumes software development while acknowledging untested
hardware. This permits P2 software preparation before human gates; it does not
assert physical acceptance or permit motor-capable upload/run. This contract
implements the actual sole write boundary, tested through checked port callbacks.
No concrete UNO Q pin backend is installed in the application in this task.

## Port contract

MotorGate owns all calls to its Port. Callbacks and context must outlive it, run
synchronously with bounded work, never allocate/block, and have exclusive access
to the configured EN and four PWM channels. No constructor performs I/O.
configureEnableLow must configure EN inactive without a HIGH glitch; configurePwm
initializes only its named channel while EN is LOW. writeEnable/writePwm return
true only for acknowledged successful settings; writePwm takes exact integer
period/pulse cycles. Periods are immutable, nonzero, <=16777216 cycles, and already
validated against the actual clock/shared timer configuration by the adapter.
They are measured/derived device properties, not new duty/frequency tunables.
settle must establish that ALL four most recent PWM settings have actually
latched before it returns true; mere register writes are insufficient. It must
return false instead of waiting unboundedly. clockUs is a wraparound microsecond
clock used after the completed transaction for receipt time.

Missing callbacks/invalid periods: begin fails without activation. begin first
configures EN LOW, then explicitly writes LOW; only after both succeed may it
configure PWM. Check each of four configure calls. Then zero all four PWM channels
and settle. Any failure latches IO. begin cannot clear a latched fault or restart
an initialized object. reset explicitly attempts LOW and all four zeros/settle;
only wholly acknowledged inhibition clears a fault, disarms the hold and permits
reuse. It preserves token high-water mark. Reset Robot with it; reset never
enables. reset before successful initialization cannot make it initialized.

## Application contract

apply(decision_us, RobotResult) consumes fresh nonzero tokens strictly greater
than the previous consumed token. fresh=false is an exact no-I/O/no-consumption
operation, even if payload differs. Repeated/regressing/zero fresh tokens fault
and inhibit. Every consumed result returns that token and post-transaction time;
whole-tick duration remains invalid for the later scheduler to measure.

Observe accepted start_release only with HOLDING, current COUNTDOWN, no motion
permission, release_us==decision_us and zero/disabled output. Capture its anchor.
IDLE/BOOT/STOPPED clears the anchor; STOPPED latches inhibition until reset. A
READY lifecycle cannot enable without having observed this accepted release and
the complete COUNTDOWN_MS+COUNTDOWN_MARGIN_MS elapsed (unsigned subtraction).
Validate release identity on HOLDING/READY. Once the complete hold is observed,
retain its completion instead of re-testing elapsed after micros wrap.
HOLDING never permits motion. No missed/replayed release can arm the gate.

Validate finite duties in [-1,1], known state/lifecycle enum, and disabled=>zero.
BOOT/IDLE/COUNTDOWN/STOPPED/DRIVE_TEST must be disabled. An enabled command needs
READY+motion_permitted, no contract/escape fault, and a completed hold. Full duty
on either wheel additionally requires ATTACK, contact and a centered current
front mask per B5's public frontView. This boundary consumes Robot-governed
outputs; it does not replace the governor, sensor validation or edge arbitration.
Invalid commands latch COMMAND and inhibit. Expected disabled results are valid.

MOTORS_ALLOWED=0 unconditionally applies LOW and zero, even for otherwise valid
enabled requests. There is no runtime override. Tests compile a separate host-only
MOTORS_ALLOWED=1 binary for active paths; never flash that test configuration.

Every admitted transaction writes EN LOW first. Only after success write all four
new pulses (other direction zero), settle, and finally HIGH if permitted. For an
active zero-demand brake, HIGH+four zeros is intentional (B7/HARDWARE5.4); inhibit
is LOW+zeros. Quantize each selected channel with floor(abs(duty)*period_cycles),
then report signed pulse/period, never the unquantized request. On ANY callback
failure, latch IO, attempt LOW first and every channel zero once, then settle;
attempt all cleanup callbacks even if one fails. Never retry HIGH automatically.
Failure receipts have applied_valid=false (zeros are not proof of inhibition).
Successful disabled receipts are valid with zero duties/motors_enabled=false.
Faulted calls continue bounded inhibition only. No destructor I/O.

## Validation and remaining target work

Independent tests exercise this production MotorGate at the port write boundary:
boot/hold/release/cancel/STOP/reset, exact deadline and adjacent ticks, wrap,
10000 seeded release streams, duplicate/stale tokens, malformed floats/states,
default-disabled builds, brake/coast, reversal ordering, quantization, failures
at every callback position, cleanup and truthful receipts. Compose real Robot
with Gate to check feedback on following ticks. No existing locked test changes.

Compile/link an inert never-called MotorGate probe on the connected board; keep
it outside upload allowlists. Host traces and compilation are not physical PWM,
EN pull-down, driver truth table, settle timing, electrical approval or full-tick
WCET evidence. Installed native PWM preload/shared timers (F086/F088) require a
separately validated settle implementation. Stock analogWrite masks failures and
may fall back HIGH, so it cannot implement this Port. No fabricated success stub
may serve as a hardware backend. Fresh independent read-only safety review required.
