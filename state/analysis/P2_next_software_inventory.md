# Next eligible P2 software task

Read-only inventory, 2026-09-23 22:50 Asia/Dubai, while D104 capture/review is
still being completed by other owners. This file changes no policy, production
source, tests, shared ledger, grants or upload key. It does not assume D104 has
passed runtime acceptance.

## Priority and existing gap

**Next: freeze and implement bounded, non-MATCH calibration-snippet delivery
from the actual Runtime calibration result.** Follow that with the missing
physical-bench software, starting with the small opponent-view bench. This order
is explicit in `state/CODEX_EXECUTION.md:39-40`, consistent with
`state/analysis/P2_app_dump_contract.md:96` and
`state/analysis/P2_service_reset_contract.md:158`.

P2 2.4 and B13 require QTR_CAL to retain RAM thresholds and print them for
config.h (`docs/prompts/P2_hal_bench.md:24`, `docs/BEHAVIOR.md:481`). The software
gap is delivery, not another calibration algorithm or matrix renderer:

| Existing piece | Verified present | Missing connection |
|---|---|---|
| Calibration owner | `src/hal/qtr_cal.h:35`: actual eight-stage owner, atomic versioned bank and one-call `committed` pulse | Delivery policy for a new committed bank |
| Exact formatter | `src/hal/qtr_cal_format.cpp:24`: SUCCESS/nonzero valid bank, bounded output, no partial snippet | No production caller; only tests and the never-executed `bench/p2_qtr_cal_compile/src/qtr_cal_probe.cpp:16` call it |
| Actual app integration | `src/app/runtime_inputs.cpp:174`: real Robot/snapshot -> Calibration; committed bank retained | No format/export step after that actual result |
| Calibration display | `src/hal/ui_display.h:18`, `src/hal/ui_display.cpp:213`: stage/color/progress/outcome projection | Already implemented; optical acceptance remains physical |
| Bounded transport | `src/app/dump_port.h`, `src/hal/dump_uart_unoq.h:17`: one setup-only UART owner and bounded write/cancel interface | Calibration writer arbitration with the existing recorder Transfer |
| Host recorder receiver | `tools/dump_match.py:69`: strict framed recorder CSV parser | It is not a calibration-snippet receiver and must not silently accept mixed data |

D089 owns the calibration algorithm, source-era/handover checks, exact snippet
text and display (`state/DECISIONS.md:1108`,
`state/analysis/P2_qtr_cal_contract.md:124-170`). D090/D101 own recorder protocol,
UART lifecycle and actual post-Gate S..C accounting. D103 makes QTR_CAL
unavailable in the permanent service-only lifetime; preserving an old bank does
not authorize a new capture or fresh export intent.

## Freeze these decisions before implementation

These are delegated software design choices under D051/D075, not reasons to
request new hardware or a new human gate. Record the selected contract first.

1. **Traffic scope:** choose non-MATCH, explicit-default-off export. D089 says
   printing transport was deferred and grants no new MATCH Bridge traffic
   (`P2_qtr_cal_contract.md:134-135`; AGENTS R2/R3). Do not route a calibration
   print through MATCH merely because the shared port is currently named DumpPort.
   Existing MATCH log-dump bytes/permission remain unchanged.
2. **Trigger and identity:** smallest behavior is one export attempt per genuine
   newly committed bank, after the corresponding actual inhibited Gate receipt,
   while ordinary IDLE/QTR_CAL authority is current. Freeze token/version
   consumption, duplicate suppression, context loss, rejection and retry rules.
   SUCCESS alone is retained state; a caller-supplied report is not proof of a
   new actual calibration. Service-only/reset paths must not replay an old pulse.
3. **One UART owner:** reuse the existing bounded native instance and grants;
   explicitly serialize recorder dump versus calibration output. Their byte
   streams cannot interleave. Changing menu selection cancels the old Transfer
   (`src/hal/recorder_dump.cpp:60-84`), and cancellation can permanently poison
   native framing. A serializer must observe that status; it cannot reinitialize,
   clear poison, steal an active packet or make a second UART owner.
4. **Wire/host boundary:** retain `formatConfig`'s exact payload. Freeze whether
   a small independent envelope carries identity/completeness or an exclusive
   capture accepts one canonical complete line. Provide a receive-only bounded
   decoder; do not weaken `dump_match.py`, send a remote calibration command,
   append snippets inside recorder CSV, or edit config.h automatically. Captured
   thresholds remain evidence for a separate recorded configuration change.
5. **Timing and storage:** readiness, formatting, one bounded progress step and
   cancellation belong inside real S..C, following the D101 pattern in
   `src/app/runtime_dump.cpp:52`. No between-tick polling, delay, heap or synthetic
   C. Keep only the small pending payload/identity, not another Runtime or full
   calibration-report copy. Existing 80-byte formatter scratch and 64-byte UART
   payload bound are implementation facts, not automatic capacity approval.

Target memory is a practical constraint: D103 app default/MATCH conditional
remaining spans are only1,088/696 bytes (`P2_service_reset_target_audit.md`).
The smaller D104 inert image's capacity cannot be transferred to the app. Make
default/Immediate/MATCH target and loader audits an early acceptance check;
do not reduce recorder capacity/cadence or weaken grants to fit the feature.

## Smallest ownership split and concrete acceptance

- **Coordinator:** new delivery contract/decision and literal public report/port
  semantics; owns shared ledgers and any eventual exact build/upload decisions.
- **Implementation worker:** one new app-owned export helper, plus the narrow
  Runtime attachment/report/grant fields and output arbitration needed to use
  the existing DumpPort. Candidate files are `src/app/runtime_calibration.*`,
  `src/app/runtime.h`, `runtime_inputs.cpp` and `runtime_dump.cpp`; finalize exact
  ownership after the contract. Existing qtr_cal formatter/algorithm, UART
  backend, config, core and locked tests should need no behavioral change.
- **Independent test worker:** new configured actual-Runtime fixtures/tests and
  a separate host receive-only parser test file. Existing D089/D101/D103 tests
  remain unchanged. Receiver implementation may be a separate small worker task.
- **Reviewer/evidence owner:** source freeze, full relevant host/sanitizer runs,
  actual target identities/startup/imports/ordered memory, independent review.

Acceptance must demonstrate actual eight-request Runtime calibration -> atomic
bank commit -> exact formatter bytes -> bounded fragmented delivery -> strict
host reconstruction, with no fixture-reset or fabricated owner authority.
Cover default-off and MATCH silence; duplicate/retained report suppression;
incomplete/rejected calibration; wrong bank/version/context; full/partial/zero/
invalid writes; Linux unavailable; source or clock regression/wrap; START/STOP,
reset and service-only preemption; failed actual inhibition; mutual exclusion
with a real recorder dump; cancel-once and permanent native poison. Successful
send is unconfirmed until independently received; capture provenance must not
label synthetic calibration as physical. Preserve original dump roundtrip bytes,
threshold bank, source chronology, motor inhibition and original complete timing.

No physical QTR calibration or native UART success can be claimed from these
host/compile checks. `src/app/app.ino:20` still uses empty grants, and
`src/config.h:34` still leaves A1 windows unconfigured.

## Remaining bench software, after this task

The active prompt names opp_view, qtr_raw, imu_heading, motor_stand, vbat, ui and
recorder (`docs/prompts/P2_hal_bench.md:11-18`); none of those exact directories
currently exists. Existing p2_*_compile sketches are retained, never-called
compatibility probes. ui_matrix shows synthetic scenes, p0_qtr is an older
setup-only diagnostic, recorder_inert is synthetic, and runtime_inert has absent
sources. These are useful evidence with different scopes, not the named physical
bench implementations or B1-B8 acceptance.

Recommended next bench order is opp_view first, then qtr_raw/imu_heading/vbat/UI
as independent software preparations, and the integrated recorder bench after
the source/transport lifecycle is ready. motor_stand/B7 may be prepared and
compile-tested separately; running it still needs the specific STAND OK grant.

For opp_view, keep ownership to new `bench/opp_view/` files and independent
runner tests: reuse the actual opponent HAL and existing matrix renderer/owner,
preserve unavailable/fault states and bounded updates, and prepare a literal
60-second observation record without inventing measured polarity/ranges or an
empty ring. Compile-only is eligible; actual pin setup/upload and physical
range/false-hit qualification remain contingent on the relevant confirmed facts.
No new native HAL, pinmap or configuration values should be needed just to
prepare that bench. Human gates and all assembled-robot criteria remain open.

## Storage and text feasibility addendum

Further read-only assessment requested during D104 execution. **Recommend a
small app-owned exporter that rerenders into bounded stack storage from an
unchanged captured threshold bank.** Keep the existing recorder Transfer and
native UART backend intact. This is a design recommendation for the coordinator's
next frozen contract, not an adopted API or a claim that the final app fits.

### Three storage choices

| Choice | Incremental payload storage | Ownership/text consequence |
|---|---|---|
| Borrow Transfer's existing1,152-byte line buffer | Potentially0 bytes | Requires a new lease/lifetime protocol across pending writes, prevents Transfer::prepare/fail/advance from overwriting it, and couples calibration to recorder-private state. Saving is at most the alternative calibration payload buffer, not1,152 bytes: Transfer already owns that storage. |
| Small app helper with persistent80-byte formatted line | 80 bytes plus identity/progress state | Straightforward stable byte lifetime and format-once work. Still needs arbitration, terminal cancellation and source identity. Reasonable fallback if repeated formatting cost proves unsuitable. |
| Small app helper, rerender on each progress call | No persistent text; captured four thresholds+version contain20 bytes of fields, plus identity/progress state | Avoids buffer leasing and leaves recorder protocol/state untouched. Adds bounded repeated formatting and a larger call-stack contribution. Recommended first implementation to measure. |

`Transfer::line_`, `size_` and `offset_` are private
(`src/hal/recorder_dump.h:63-64`). Its prepare/advance/fail methods all mutate
them; writePending depends on them until acknowledged progress
(`src/hal/recorder_dump.cpp:247`, `:268`, `:71`, `:298`). There is no existing
public workspace API. Exposing a mutable pointer is insufficient to establish a
safe lease. Moving the buffer into Runtime and changing Transfer construction
would also touch existing callers/tests and introduce a new lifetime invariant.
Adding a calibration mode to Transfer would mix an unrelated bank lifetime with
recorder summary/session/CRC state. None is the smallest maintainable seam here.
Do not union/reconstruct Transfer with another owner: its consumed-request and
token history must survive output selection and reset notification.

### Why stable rerendering is supported, and its limits

The native implementation copies each offered payload into its own64-byte array
and packet on the first call. While active it checks both count and every byte
on retries (`src/hal/dump_uart_unoq.cpp:225-245`); PENDING returns zero and only
completed transmission reports progress (`:288-292`). It does not retain the
caller's pointer. Therefore a fresh stack address is acceptable if every pending
retry supplies the identical bytes/count. This is verified behavior of the
current UnoQ backend, not an implied guarantee of every arbitrary Port callback.
Freeze call-only pointer borrowing in the new helper/sink contract and test it.

At commit, retain the four values/version, consumed request token if exposed,
length/offset, phase/reason and bounded stall/total timing state. Reuse Runtime's
actual clock/receipt authority and existing DumpPort by reference; do not copy a
RobotResult, Calibration::Report, RuntimeReport, second Port callback table or
second UART owner. These fields suggest only tens of persistent bytes, but the
actual class/Runtime alignment and report placement need target ABI measurement.

Before each formatting/write opportunity, require the current real calibration
report still be SUCCESS with the same four values **and** version; then call the
existing formatter on that report into local80-byte storage. On PENDING, retain
offset and offer length unchanged. On valid PROGRESS advance only by the reported
count; reject zero/oversize/error statuses. Support bounded partial-progress
test sinks even though this native backend reports its whole payload at once.
Never regenerate from a new bank halfway through a line.

Version-only comparison is defensible inside the current private owner domain:
`Calibration::finishStage` increments version and assigns all four values
atomically, rejecting exhaustion; only genuine Calibration::reset restarts that
domain (`src/hal/qtr_cal.cpp:161-188`, `:230`). Nevertheless, saving the four
values costs16 bytes and gives the exporter a simple explicit invariant plus a
direct adversarial changed-bank test. Prefer that over making the helper's proof
depend on every future owner mutation preserving an undocumented version rule.
No persisted pointer to a mutable public report is needed.

Starting another calibration can change phase to COLLECTING while preserving
the old bank. Cancel/refuse in that context; do not manufacture a SUCCESS report
around the old values to keep printing. A new phase, reset/service-only entry,
invalid receipt, readiness loss or source mismatch cannot silently resume an
old transfer. The policy for an intent refused before the first write must be
explicit; avoid an implicit retry queue requiring additional state.

For the current QTR_TIMEOUT_US=1500, the exact formatter's maximum line is54
bytes including LF, or55 including NUL. It fits one64-byte native payload. For
four general uint32 decimal values the same format is78 bytes plus NUL. Keep the
existing80-byte capacity rather than hard-coding the current four-digit domain
or assuming one packet forever. The formatter already has its own local80-byte
scratch (`src/hal/qtr_cal_format.cpp:31`): caller buffer plus formatter scratch
means **160 bytes of simultaneous character arrays**, before decimal scratch,
register saves and caller frames. Reformatting is bounded, but its repeat cost
and actual stack use must be measured/inspected; D104's absent-source stack
sample does not cover this path.

### Minimal API/ownership seam

Keep authorization in Runtime's actual post-application path. A small private
app helper should handle only committed-bank identity, bounded formatting/byte
progress and a const status view. Candidate operations are commit admission,
one progress call supplied an already-admitted timestamp/current report/existing
Port, and terminal cancellation. These are proposed responsibilities, not
currently existing methods. Prefer a status accessor over copying a second
full export report into RuntimeReport. If one shared80-byte bound needs to be
public, expose the existing formatter capacity as a named structural constant;
do not introduce another formatter or tunable timing value.

Runtime must arbitrate **before either writer can emit bytes**:

1. Revoke/cancel an active calibration writer that has lost current eligibility,
   before allowing a new LOG_DUMP intent to reach Transfer.
2. Let the existing Transfer observe its ordinary context/preemption and preserve
   its own token/request history; never begin calibration while it remains ACTIVE.
3. Only then permit the eligible writer's single bounded progress operation,
   with real readiness and clock observations, before the actual final C.

Simply calling serviceDump first and calibration second is unsafe when an old
calibration packet is pending and the current menu has just selected LOG_DUMP.
Both optional-output-disabled and MATCH paths should retain the old dump call
order/behavior. Relevant cleanup seams are Runtime::admitApplication,
Runtime::fail and applyServiceReset (`runtime_service.cpp:12`, `runtime.cpp:253`,
`runtime_service.cpp:143`); actual C remains Runtime::completeEpoch (`:276`).

`UnoQDumpPort::abort` **always sets permanent poison**, including cancellation
between packets (`src/hal/dump_uart_unoq.cpp:301-318`). It is not a benign
release-workspace operation. Normal successful completion must clear the app's
writer selection without canceling the port. Refusal before any write need not
pretend it has emitted data; once a pending/partial stream is revoked, cancel
exactly once under the frozen contract and preserve poison. Never start the
other writer immediately after such cancellation assuming a clean UART.

### MATCH exclusion and measurable cost

Use compile-time MATCH exclusion for the exporter body, retained payload/state
and formatter call sites, rather than only checking an optional runtime grant.
Keep any common public grant/status semantics explicit: a newly unconditional
field or copied status can still enlarge MATCH structs even when methods are
compiled out. A stable accessor can report unavailable in MATCH without a
mutable exporter lifetime. Every translation unit must use the same macro value,
as enforced by the checked build. Match tests must prove zero calibration
readiness/write/cancel calls even if a caller attempts to grant the feature;
ordinary IDLE recorder dumping remains unchanged.

Concrete existing target evidence limits optimistic estimates: D103 default's
final ELF has **no retained formatConfig symbol**. Its already-collected
`sketch/src/hal/qtr_cal_format.cpp.o` contains368 bytes of formatConfig text and
30 bytes of string data (`P2_service_reset_raw/target_1fbd7238_bench-default/audit.json`).
Those are object-section sizes, not the final marginal loader charge: rodata
splitting, alignment and loader symbol metadata still apply. New exporter,
arbitration, status and cleanup text also consume the same llext pool as BSS.
Thus saving80 persistent bytes alone does not establish fit within1,088 bytes.

First keep wire format to the existing canonical line unless the frozen contract
demonstrates a need for an envelope. A separate exclusive receive-only decoder
can require one complete line and publish an external provenance receipt without
changing recorder framing or adding on-target decimal/CRC/envelope machinery.
It must not claim token/source/physical identity that the line itself lacks.

Before acceptance, compile exact default/Immediate/MATCH sources and repeat the
ordered loader/ABI/import/startup audit; verify formatter/exporter elimination
in MATCH, unchanged recorder bytes/tests, new helper layout and target call-stack
frames. If default does not fit, record the blocker and measure a narrow next
change. Do not silently broaden Transfer ownership or weaken evidence to assert
the feature fits. No production or test edits were made in this assessment.
