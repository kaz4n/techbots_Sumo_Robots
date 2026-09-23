# Remaining eligible P2 software after D111

Read-only inventory,2026-09-24. D111 currently has frozen implementation/syntax;
independent execution/review/target closure is still in progress. No new test,
hardware, implementation or ledger action was performed for this inventory.

D051 permits recorded engineering decisions, not physical evidence or a specific
motor run (`state/DECISIONS.md:442`). D075 explicitly permits P2 implementation,
independent host tests and compile-only preparation before physical acceptance,
while retaining wiring/run/gate limits (`state/DECISIONS.md:841`). Therefore the
next software task need not wait for hardware, but cannot claim B1-B8 completion.

| P2 requirement | Current implementation/evidence | Genuine remaining work |
|---|---|---|
| B6 `bench/ui` (`docs/prompts/P2_hal_bench.md:16`) | The directory is absent. `bench/ui_matrix/ui_matrix.ino:22` renders synthetic mode/service/countdown scenes; `:46` explicitly grants matrix setup, and `:56` submits rendered scenes. D088 has actual board counter evidence but explicitly leaves optical/full B6 open (`P2_matrix_validation.md:87,99`). The real A1 decoder is `src/hal/ui.h:17`; explicit source admission and actual gestures already exist inside Robot (`src/core/fsm_buttons.cpp:28,72`, `countdown.h:90,301`). | A named bench acquiring and retaining real A1 evidence is missing. Synthetic scene playback does not distinguish physical NONE/START/MODE/BOTH or exercise live gestures. Production windows remain intentionally unconfigured (`src/config.h:34-36`; `P2_button_routing_contract.md:11-16`). Do not invent thresholds or interpret UNCONFIGURED as NONE. |
| B4/B7 `bench/motor_stand` (`P2_hal_bench.md:14,17`) | Directory absent. Existing `p2_motor_gate_compile`/`p2_motor_native_compile` are inert retained-method probes. Actual MotorGate and UnoQPort already provide the checked motor boundary (`src/hal/motors.h:35`, `motor_port_unoq.h:9`). Brake versus coast is already specified, not missing: enabled zero demand intentionally yields HIGH/four zeros; inhibition is LOW/zeros (`P2_motor_gate_contract.md:66`; `motors.cpp:142`). | Missing bounded stand-trial orchestration, retained phase/fault/timing/cycle evidence and later physical measurements. Do not replace the driver. A contract must reconcile full-reversal B7 sequencing with existing token/hold/governor/full-duty checks (`motors.cpp:112-138`); no fabricated Robot permission or direct EN/PWM writes. Default disabled grants and MOTORS_ALLOWED0 are required; actual motor-capable upload/run still needs the specific stand authorization. |
| B8 `bench/recorder` (`P2_hal_bench.md:18`) | Named alternate `bench/recorder_inert` exists: real Robot/Gate/Recorder with inert callbacks (`recorder_inert/src/recorder_bench.h:1,97`). D091 retained actual200s/5001frames/8events plus checked RAM/CRC (`P2_recorder_bench_validation.md:65-82`). D104 separately executes actual Runtime with absent sources (`P2_runtime_inert_validation.md:74-98`). | No need for another recorder runner or a rename-only task. Native UART transfer and assembled-robot/no-gap B8 acceptance remain unmeasured; older notes calling Runtime attachment or local reset absent are superseded below. |
| Runtime dump and post-STOP access | D101 attached the actual Transfer to real receipts; current implementation is `src/app/runtime_dump.cpp:41-59`. D103 added inhibited Robot-only local reset (`runtime_service.cpp:146-176`), with real host GO->STOP->tail->reset->menu->LOG_DUMP streams (`P2_service_reset_validation.md:50`). `tools/dump_match.sh:7` already invokes the strict receiver; `tools/dump_match.py:237,287` supports bounded capture/receive. | Physical native UART/setup/readiness and source/deployment-linked receipt remain; this is not a missing generic transport framework. D103 service-only QTR_CAL/DRIVE_TEST are intentionally UNAVAILABLE (`runtime_service.cpp:191-198`), not accidentally omitted dispatch. |
| QTR calibration/config snippet | Actual owner/service exists; D105 exports through the existing dump port in nonMATCH only (`P2_calibration_delivery_contract.md:11-18,123-149`). D106 closes the later capacity blocker for its exact profiles (`P2_pin_table_validation.md:3-6`). | Physical calibration and actual snippet reception remain. Do not reimplement the bank, text formatter, receiver or dump arbitration, or repeat stale D101/D105 RAM blockers after their exact D102/D106 replacements. |
| Full app timing/integration | `src/app/app.ino:11-28` constructs the real pipeline. D104's actual200001-epoch run is deliberately RuntimeRUNNING/RobotBOOT/recorderEMPTY with absent sources (`P2_runtime_inert_validation.md:82-98`). | Five-minute all-live p99/worst-case<800us, full native load/fault timing and B7 reset testing still require physical work. The inert269us S..C maximum does not establish that requirement. Weight/footprint and human gates remain nonsoftware work (`P2_hal_bench.md:21-33`). |

## Minimum next task

After D111 closes, adopt the bounded **B6 A1 evidence bench contract** under
`bench/ui`, then implement/test it in new bench-owned files only. The smallest
useful first scope is one existing `power::Reader` with direct
`beginWithButtons()`/`readButtons()` (`src/hal/power.cpp:325,485`), actual
`ui::decodeButtons`, and finite immutable raw/status/source-time/sequence/
qualification evidence. Default all grants false; no ADC or matrix callbacks.
Configured windows remain a separate human/electrical fact; host-only configured
profiles can verify all four levels without promoting them to production values.
No new ADC implementation, bus owner, remote command or arbitrary-channel API.

This is a concrete missing prerequisite for live B6, not a claim that raw capture
alone completes mode/menu/countdown acceptance. Existing renderer and logical
gestures should be reused in the subsequent live presentation composition. Do not
copy Robot's private source-admission logic into another controller. If the first
contract includes gestures, explicitly freeze how the existing Robot path receives
UI-only versus synthetic non-UI inputs, and keep that provenance visible.

Two shortcuts are unsuitable: (1) simply enable ADC/matrix in full Runtime—its
initialization requires granted opponent/QTR/ADC and current evidence, so a UI-only
setup remains BOOT (`runtime_inputs.cpp:136-146`); (2) use the native app as an inert
UI harness—MotorGate initializes before source-grant checks (`runtime.cpp:73-81`),
so false sensor grants do not guarantee no header output configuration. These
constraints should be respected without weakening Runtime's readiness rules.

Second priority is a stand-bench contract with existing MotorGate/UnoQPort and
explicit phase/hold/governor semantics; software/compile-only work is eligible,
but energization, electrical truth table/PWM frequency and20 physical reversal
cycles are not supplied by a passing fixture. No P3/P4 work or phase jump follows.

Acceptance for the next software increment: frozen public contract and separate
test author; default no-I/O construction/setup/loops; real callback results and
source identity preserved; bounded work/storage and terminal silence; unknown/
overlapping/unconfigured windows explicit; native single-owner binding; unchanged
existing/locked assertions; checked literal compile route and actual source/ELF/
startup/loader audit. Do not add a new upload key or hardware grant as part of it.
