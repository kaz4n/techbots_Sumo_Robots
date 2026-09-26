# Ordinary inhibited observation: source planning only

26 September 2026. This is an unadopted planning note after accepted D209 ABI
review585be669. D210 entry inspection is still in preparation. There is no new
upload, capture contract, decoder, address map or native admission here.
The source findings came from the separate read-only ordinary_abi_scope agent.

## Meaningful fields and their limits

The accepted six Runtime windows and separate UnoQPort object cover the useful
field families: attempted/grants; Runtime phase/fault/epochs/release and maximum
execution counters/readiness/freshness; transaction phase/fault/decision and
completion timing; robot token/state/output and contract faults; applied motor
feedback; retained PreviousTick; MotorGate initialization/fault/halt receipt;
and native port configuration, low/settled/mask/timer/channel/pulse bookkeeping.
An independent later decoder must transcribe current offsets from the accepted
raw ptype layouts. RuntimeReport has no nested TransactionReport or duplicate
transaction snapshot: the600-byte outer scheduling/sensor/service report and
the504-byte live transaction report are separate windows (runtime.h61-104,172). No diagnostic Runner or SETTLE lifetime report exists here.

app.ino ignores begin's return and then repeatedly calls step (lines19-26).
Runtime attempted_ latches on entry, not success (runtime.cpp74-88). RUNNING and
positive epochs are consistent with completed begin; a faulted sample cannot
recover an absent begin_ok. Gate initialized_ only describes gate.begin.
Runtime initialization_complete is later sticky readiness (runtime_inputs.cpp
114-151); the current absent grants allow RUNNING/advancing epochs while Robot
stays BOOT (fsm_robot.cpp414-432). BOOT alone is not setup failure.

Runtime::step clears freshness/service pulses on every call, including early
returns and faulted calls (runtime.cpp315 onward); false freshness is not proof
of stalled progress. Transaction::open resets its report before acquisition
(transaction.cpp47-56). Decision, application and completion fields then change
sequentially. PreviousTick receives applied feedback before separate duration
stores (121-152); completed duration belongs there, while applied.feedback's
duration_valid normally stays false. Counters update at different points and
can saturate. None of these reports provides atomic snapshot publication.

Runtime.fail aborts the transaction before publishing Runtime FAULT, then
performs further dump/source cleanup (runtime.cpp253-267). Transaction.fail
publishes its own FAULT before gate.halt and feedback invalidation
(transaction.cpp33-45). Neither FAULT is a cleanup-complete fence. In setup
failure, gate.begin performs its own cleanup before Transaction records SETUP;
later abort may return without another halt. A default unattempted halt record
therefore does not establish failed cleanup. HaltResult.fresh is retained
return data, not a polling publication flag. Native low/settled/mask fields are
transient callback bookkeeping (motor_port_unoq.cpp344-433), not measured pins.
RUNNING/progress alone does not establish valid motor receipts; ordinary gate
fault promotion has its own policy (runtime_service.cpp12-37).

## Possible finite collection, still requiring adoption

A later fixed capture could reuse exact-image flash brackets, bounded one_read
receipts, first-error handling and finalization from P7_motor_const_run_raw/
remote.py128-226 and P7_static_startup_raw/capture_remote.py422-590. A candidate
is exactly two seven-window sets in a declared order, with the existing
two-second pause between them. The selected unpadded payload is1302 bytes per
set. A fixed initial30-second wait is operationally compatible but establishes
no completion criterion. Do not poll adaptively, traverse a dynamic heap,
execute inferior functions, halt/abort the MCU or claim a terminal snapshot.

Preserve every partial-prefix raw byte and receipt and finish file/flash/boot
checks. Collection integrity and sampled application findings are separate.
Coherence stays UNPROVEN even if samples or token brackets match: reports may
span epochs, 64-bit fields may tear, and equal values may be stale. Report only
sampled values/advancement, not continuous run duration, full WCET, every
callback's success or final inhibition. Passive host capture ending does not
stop the ordinary MCU loop; the final policy must explicitly allow continued
inhibited execution.

Unresolved choices for that future contract are the independent field map and
enum provenance; alignment of byte-sized attempted_ under the existing word
read rule; exact bounds for any aligned container; whether fixed bookends add
useful diagnostics without implying coherence; fault/unknown/inconclusive and
partial-sample classifications; and reset-continuity limits. Linux boot ID and
unchanged flash do not prove that the MCU did not reset. No existing read guard
may be silently relaxed. These are preparation questions, not requests for
human physical acceptance or permission to run motors.

## Existing guarded tool seams, source planning only

D207 run.py201-225 is diagnostic-specific: manifest schema,129-file count,
source4bc3 and compile_motor_const source mapping. A later ordinary caller must
use the accepted compile_ordinary_app_static.py mapping/admission,125 inputs
and source9044, preserving collision/reserved-name/count/4MiB/digest checks.
Changing only the count or required sketch predicate would be insufficient.
Its capability_program118-136 and run.py180-199 also bind diagnostic sketch
and artifact paths. The ordinary raw upload BIN is92928B/6f5f531b; its checked
flat package is92944B/7fa9d41d. Preserve the exact static/default CLI shape;
M0/MATCH0/probe0 come from source/artifact evidence, not new upload arguments.
The checked_evidence provenance must select accepted D208/D209/D210 packets.

D207 remote.py102-143,188-218 and actions.py constants/_bootstrap/_plan/_capture
contain fixed diagnostic schema/path/window/read-count/byte-total assumptions.
A later scope needs exact ordinary replacements and fresh owners, with no
Runner/Trace/SETTLE terminal predicates. Preserve raw samples, coherenceUNPROVEN,
full before/after loader+sketch comparisons and first-error/partial evidence.
Existing source_data/source_snapshot/source_action bodies remain candidates
for exact reuse with before/after tree stability and complete source hashes.

Preserve core upload lifecycle bodies and descriptor/file/process/identity
guards,14 fixed absence selections (only three sketch-path substitutions),
/tmp/remoteocd absence, one upload claim/intent,180s+5s reap and1MiB streams.
Capture command/one_read/pause/finalize/close/_collect bodies retain bounded
process/output ownership,600s total/30s child budgets, raw-first retention and
returned-only success. Any claimed byte identity needs its own later contract
and oracle; this note does not approve an implementation or additional query.

The passive command is pinned OpenOCD plus p0_mem_read.cfg and only dump_image
and shutdown. The config uses reset_config none and an AP0 mem_ap target with
no Cortex target, flash driver or events; network command ports are disabled.
Passive capture does not halt/resume/reset/write the MCU. Host shutdown or
SIGKILL terminates OpenOCD, not firmware. Upload separately flashes/resets.

Exact alignment distinction: tools/p0_capture.py127-134 requires an exact-int
uint32 address divisible by4, a positive exact-int length and containment in
[0x20000000,0x200c0000). It does not require length divisible by4. D207's fixed
Capture.one_read/command does not call p0.ram_range; its windows are predeclared.
This does not establish target support for an unaligned one-byte attempted_
read. Prefer an explicitly scoped aligned containing read or independently
reviewed fixed-byte support later, with no silent shared-policy relaxation.

The two real receipt copies are transaction_.report_.applied.feedback and
transaction_.previous_. Preserve them separately: completion first finalizes
the live report, copies feedback to previous, adds its duration/completion
fields and finally marks transaction IDLE. Runtime then advances outer epoch/
maximum/freshness/scheduling fields. New open resets the report while retaining
previous. Failure invalidates both after publishing transaction FAULT and
attempting halt. Differences can reflect normal lifecycle stages or torn live
reads; even stable IDLE does not require byte equality because previous has
additional duration data. The runtime/transaction/previous composite Snapshot
and before_abort copy belong only to the diagnostic observer, not ordinary
RuntimeReport. No duplicate transaction window should be invented.
