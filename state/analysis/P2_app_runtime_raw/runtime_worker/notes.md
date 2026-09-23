# D096 Runtime implementation worker

Owned changes: new `src/app/runtime.cpp`, new `src/app/runtime_inputs.cpp`, and
private declarations/state only in `src/app/runtime.h`. Root owns Transaction,
the native binding, app entry, build integration and shared state/evidence files.

Implementation uses actual Transaction, InputOwner, Estimator and Calibration.
No source/core/config/established test or board/upload tooling was modified by
this worker. All worker callbacks are synthetic; no board or motor action ran.

Initial strict compile: `runtime.cpp` passed. `runtime_inputs.cpp` failed once
with `-Werror=sign-compare` at the opponent native status versus unsigned mask
comparison. The explicit `std::int32_t` cast corrected it; the next strict compile
passed. This initial shell compile was observed directly, before JSON receipt
capture was installed; it has no saved standalone command transcript.

Initial production-owner smoke passed in both `MOTORS_ALLOWED=0` and `=1` with
strict C++17 warnings and UBSan. It covers inert/default setup, missing granted
ports, terminal passivity, grid/missed slots, finite frozen-clock polling,
complete 1200us display work (overrun remains nonterminal), bounded QTR charge
service/cancellation, and updated IMU publication retained through real NO_NEW.
The run script preserves command/source hashes/stdout/stderr/exit code in each
`check_*.json`, with latest successful run indexed in `summary.json`.

During separate root review, DecisionSource gained an optional pure clock
acceptance check before Robot application. Runtime uses that seam and routes
an outer-clock regression to CLOCK without synthesizing a LINE_CONTRACT Robot
decision. Root also renamed the seam to `decideFrom` to preserve existing
`decide({})` source compatibility. These are root-owned contract/public changes.
The worker added actual-D line-age/order checks to CONTROL initialization and
retained a latched expired QTR source across whole-clock wrap.

Limitations: this smoke is scoped implementation evidence, not independent
acceptance, target compilation, physical grants, source freshness measurements,
RAM/WCET qualification or any human phase gate. Independent full runtime tests
and fresh separate review remain root-owned delivery work.

Follow-up implementation: Runtime now admits actual motor application time A
before post-decision work, and passes the latest actual outer clock to the
root-provided `Transaction.finishAfter` boundary. Invalid C chronology becomes
CLOCK before a successful receipt can be published. Independent tests also
found real CONTROL QTR starvation: a remembered threshold crossing prevented
all later advances. The first pump pass now services an active QTR frame once
in every real epoch, then preserves the existing bounded early-exit policy.
No source time, color or completion is inferred by this correction.

The strict/UBSan smoke passed both motor modes again after these fixes. Its
uniquely retained index is
`summary_after_application_completion_and_qtr_service.json`; individual command
receipts remain timestamp-named and preserve the exact source hashes.
