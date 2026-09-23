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
