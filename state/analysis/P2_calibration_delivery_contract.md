# D105 bounded calibration snippet delivery

2026-09-23, selected under delegated D051/D075. Implements P2 2.4/B13 printing
of D089's actual committed RAM bank. Source inputs: D089/D090/D101/D103,
P2_next_software_inventory.md and reviews/P2_calibration_delivery_preflight.md.
No new wiring, sensor grant, tunable, physical fact, MATCH traffic or human gate.

## Public contract and storage

SetupGrants gains calibration_output_enabled=false. Both dump_enabled and this
new grant are necessary, and MATCH must be0. Truth table: neither/dumpoff+calon
produce no DumpPort callbacks; dumpon+caloff behaves exactly as D101; bothon
in nonMATCH enables this writer with the same single setup-only native owner.
MATCH ignores calibration grant completely while preserving legitimate D101
dump traffic. It must compile out mutable calibration-output state and code.
Do not initialize or construct another UART owner. No lazy setup or poison reset.

Runtime exposes const CalibrationOutputReport& calibrationOutput() const.
The public enum/report is in app/calibration_output.h; no mutating public API.
Report phase INACTIVE/ACTIVE/SENT_UNCONFIRMED/CANCELLED/REFUSED/FAILED; reason
NONE/CONTEXT/RECEIPT/SOURCE/TIME_ORDER/TOKEN_ORDER/BANK_CHANGED/LINUX_UNAVAILABLE/
FORMAT/PORT/STALL/TOTAL/RESET. Fields token:uint64,version:uint32,bytes:uint32
are request identity and acknowledged bytes, not host receipt. Defaults inactive,
none,zero. A new intent replaces the terminal report only when admitted/consumed.
MATCH/disabled accessor returns immutable inactive status without mutable state.

Capture the four bank values and version (20B), offset and small timing/identity
state. Re-render exact qtr_cal::formatConfig into fixed caller-stack80B for each
bounded write; its internal80B scratch also exists. No extra persistent payload,
full calibration report copy, Transfer buffer loan, heap or arbitrary formatter.
Expose the existing80B capacity as qtr_cal::CONFIG_SNIPPET_CAPACITY, structural
storage not a new tunable. Formatter output/validation remain byte-identical.
Pending calls must offer identical bytes/count until progress; stack pointer is
valid only during write, consistent with the native owner's copied64B payload.

## Actual authority and one-shot intent

Only an actual ordinary Runtime postDecision call that just called
calibration_.step and received committed=true can start an intent. Bind its
current real Robot token and nonzero bank version. D103 service-only skips the
owner call; a retained committed bit is never a fresh intent. Consume a genuinely
new version once before readiness/context refusal. Retained SUCCESS, duplicate
version, menu re-entry or reset must never retry it. A later genuinely committed
higher version may attempt once. No delayed intent queue or fabricated SUCCESS.

For admission/progress require ordinary RuntimeRUNNING, not service_only,
actual fresh nonzero/nonmax Robot token, TransactionDECIDED/decision_made,
consumed valid matching Gate feedback, Gate faultNONE and real applied time
within the forward half range from D. Both intended/applied duties0 and motors
disabled; RobotIDLE, countdownIDLE, no release/GO/motion, faults0/escapeNONE,
raw-line mode, current service menuQTR_CAL. Calibration must still be SUCCESS,
reasonNONE, valid captured values/version matching the current bank.

Current button evidence must be explicit/contract-valid/VALID and existing
opponent freshness qualification must pass. Current line evidence must remain
explicit/contract-valid/CALIBRATION and not INVALID. A normal pending/ABSENT raw
frame is permitted: delivery refers to the completed bank, never a fresh sample.
Do not require new IMU/battery data beyond existing Runtime/Robot contracts.
Changing menu/state, starting a new capture (phase no longerSUCCESS), STOP/reset,
source/receipt/context failure or bank change cancels an ACTIVE export once.
A refusal that never became ACTIVE must not cancel/poison the shared port.

Time comes only from actual clock observations inside S..C. Fresh context age
now-D must be<TICK_US; real D/application/now/C ordering remains inherited.
During ACTIVE, tokens must advance exactly1 and decision timestamps strictly
forward below half-range; global clock regression remains Runtime's fault.
An identical repeated token/time must never offer more bytes. Invalid context
beats duplicate suppression. Stall/total ages count actual forward deltas with
saturating arithmetic; deadline equality fails before another write. Use existing
DUMP_STALL_MS and DUMP_TOTAL_MS; no new timing/config defaults. First failure
of a terminal attempt remains until a genuinely new commit is consumed.

Precedence for a newly consumed/active attempt: reset/Runtime failure cleanup,
receipt, inhibited context, sources, token/time chronology, bank/phase, deadline,
Linux readiness, format, write result. Terminal cleanup preserves acknowledged
bytes and request identity. A global Runtime clock failure reports TIME_ORDER;
explicit abort/reset reports RESET. Invalid ordinary receipt reports RECEIPT.
Before ACTIVE, a consumed intent failure is REFUSED. Once ACTIVE, lost context,
receipt, source, bank/phase, Linux readiness or RESET become CANCELLED; time/token
order, FORMAT/PORT/STALL/TOTAL become FAILED. Both terminal paths cancel once.
Missing required callbacks or dump_setup!=OK refuse PORT without readiness/write.
A setup/readiness rejection cannot reinterpret stale SUCCESS as a new commit.
Unreachable same-version mutation/private-state boundaries must be disclosed,
not tested by resetting or seeding private production owners.

## Single-writer order and bounded transport

When enabled: before either writer can offer bytes, inspect/cancel an old
calibration writer that lost eligibility. Then let the enabled existing recorder
Transfer observe actual results through existing serviceDump, including normal
cancellation, token/request consumption and readiness behavior. Preserve D101
bad-receipt exception: abort the Transfer and skip its step/readiness on an
invalid actual receipt; never manufacture authority to satisfy an observation. Only afterward
consider calibration progress, and never while Transfer is ACTIVE. A current
QTR_CAL and LOG_DUMP selection cannot both authorize writes. At most one write
callback per actual epoch. Never fake a result or skip Transfer chronology.

After either cancellation, sample readiness freshly before the other writer.
Native cancel always permanently poisons its owner, even between packets;
never assume cancellation left it reusable. Finishing successfully does not call
cancel. Refusal before ACTIVE does not cancel. Once ACTIVE, any terminal failure
cancels exactly once. Runtime fail/admitApplication/reset cleanup must cancel
before further readiness/output and inside the actual current timing lifetime.

Each progress invokes write at most once, offering min(remaining,DUMP_PAYLOAD_BYTES).
PENDING requires count0 and retains exact offset/offered bytes. PROGRESS requires
1<=count<=offered; acknowledge only count bytes. ERROR, unknown status, invalid
counts or missing callbacks failPORT. Positive progress resets stall age only.
At payload completion become SENT_UNCONFIRMED without cancelling. The next new
bank can use a clean native owner; no host receipt or physical calibration is
inferred from acknowledgement. Readiness false refuses/cancels without writes.
Normal readiness/format/write/cancel work is bracketed by real clock observations
before Transaction::finishAfter; no background or between-tick transport progress.
Inherit D101 failure exception: a finishAfter/C failure or public abort without
an open epoch still inhibits/cancels once. Never fabricate successful C, re-open
a failed epoch or retry cleanup to claim measured successful timing.

## Strict receive-only host artifact

New tools/qtr_config.py offers decode_snippet(blob:bytes,timeout_us:int)->dict.
Exact immutable bytes only,1..79bytes, ASCII canonical one line:
QTR_WHITE_US[4] = {<n>U, <n>U, <n>U, <n>U}; // us\n
Four decimal values, no leading zero/sign/space variation/NUL/CR/additional line;
1<=n<=timeout_us. timeout_us is exact int (not bool),1..0x7fffffff, supplied
explicitly from the intended firmware configuration; no duplicated tuning default.
Malformed data raises ValueError. Return {'white_us':[four integers],
 'timeout_us':timeout_us,'provenance':'UNATTRIBUTED_BARE_LINE'}.

CLI: python tools/qtr_config.py INPUT --timeout-us N --output-dir NEW_DIRECTORY.
File input only; read at most80bytes then reject oversize. Reject nonregular file,
symlink input/output, existing outputdir and extra bytes. No socket/subprocess/
serial commands. Publish snippet.txt with original exact bytes and receipt.json with exactly
white_us,timeout_us,provenance,sha256,byte_count fields; the first three are the
decoder result, sha256 is lowercase raw-byte SHA256 and byte_count is raw length.
Never modify config.h or relax dump_match.py. This command validates a bounded
received file; acquisition may use the separately existing receive-only tools.
No firmware/token/source identity, live end-of-stream, origin or physical claim.

## Acceptance and narrow ownership

Public interfaces/spec freeze before tests and implementation. Independent author
uses actual eight-request Runtime calibration, real Gate receipt, retained bank,
source chronology and completed C; no caller-forged export authority/private seeds.
Test all grant/MATCH cases, duplicate/retained pulse, stage restart, failure and
preemption, partial/PENDING/invalid writes, readiness/poison, wrap/thresholds,
completed snippet->strict parser, and both directions of real recorder arbitration.
Keep D089/D101/D103 expectations and locked tests unchanged. Unreachable private
branches may use review/static reasoning with limitation; do not fake coverage.

Implementation owns only new app exporter plus necessary Runtime attachment,
cleanup/public API; same formatter capacity symbol; coordinator serializes CMake,
config-independent receiver and ledgers. Fullnormal/sanitizer meaningful tests,
exact default/Immediate/MATCH compile and independent target ABI/loader review
are required. Verify MATCH removes new state/code/formatter roots and original
recorder streams remain byte-identical. App margins1088/696B are tight: if it
fails fit, retain the failure and assess a measured narrow fix; never reduce
recorder capacity, hide sensors, broaden pointer ownership or relax gates.
No upload/nativeUART/sensors/motor action is authorized by this software contract.
