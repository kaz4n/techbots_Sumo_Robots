# Bare UNO Q A1 capture feasibility

Read-only feasibility, 2026-09-24. No source/config/test/ledger edit, board query,
upload, reset or ADC operation was performed. Current user-reported setup is
the UNO Q alone, with bare-board testing authorized; this is attachment evidence,
not an independently measured wiring, voltage or ADC-ownership fact.

**Recommendation: eligible and useful as a separately scoped, exact-image
diagnostic, subject to the prerequisites below.** No additional hardware or new
pin assignment is needed. It can observe actual native setup/failure, finite raw
A1 conversions, source times and UNCONFIGURED decoder evidence. It cannot qualify
button levels, voltage accuracy, START/BOTH distinction, physical timing limits
or P2 B6. The current D112 image has a false grant and its checked route refuses
uploads; neither an existing compile receipt nor this note authorizes bypassing
that restriction (`bench/ui/ui.ino:12`, `bench/ui/README.md:3`).

## Exact native actions and admission

| Boundary | Actual source and installed evidence | Implication for a bare run |
|---|---|---|
| One owner and fixed profile | `bench/ui/src/ui_bench_native.cpp:9-14` forwards to one Reader's beginWithButtons/readButtons. `power.h:45-53` fixes A0/A1 rather than arbitrary channels. | No Runtime, MotorGate, battery read, matrix, I2C, UART/Bridge or second ADC owner. Construction/factory are passive. |
| Exact pads | `src/hal/power.cpp:64-104`; `P2_adc_pair_audit.md:48-55` binds A0/index14/PA4/channel9 and A1/index15/PA5/channel10 to installed core1.0.0. | No pin or wiring change. Both pads participate in setup even though only A1 is converted. Native metadata/alias rejection remains enabled. |
| Existing pin state | `power.cpp:135-143` requires both pads independently unlocked, analog/no-pull, with GPIOA clock present. Installed DAC boot pinctrl applies those modes without enabling its outputs (`P2_adc_ownership.md`, section "Stock ADC4 and DAC1 are compatible only while idle"). | Reject an unexpected remux/lock; do not repair it. No output HIGH/LOW, pull-up, DAC enable or whole ADC pinctrl group is requested. |
| Mutation after admission | `power.cpp:251-254` sets ADC common /4 and rewrites **PA4 only** to the same analog/no-pull mode. `:296-307` sets both sampling fields, PCSEL0x600 and initial single rank9. | PA5 is checked but not reconfigured. Initial rank9 is not an A0 conversion. Setup calibrates/enables ADC1; first read selects rank10 (`:404-419,485-499`). |
| ADC/peer ownership | `power.cpp:108-132,160-162,195-221` checks never-initialized stock ADC1, idle ADC4, ADC1 IRQ state, inactive DAC1 channels1/2, nominal shared clocks/supplies and pristine ADC1 registers. | Guards are required actual admission observations. They cannot prove absence of a concurrent thread/ISR; whole-image ownership exclusion must also be reviewed. |
| Before the claim | `power.cpp:327-355` validates config/mapping/environment, then enables only the ADC1 peripheral clock before reading pristine registers. | If pristine admission fails, the clock may remain enabled; NOT_ATTEMPTED means no owned-ADC shutdown, not no hardware action. Do not roll it back or reset/retry to force admission. |
| Native faults and terminal state | `power.cpp:358-395,448-499`; `P2_ui_bench_contract.md`, "Clock, timing and terminal ownership". | Native faults retain bounded cleanup or UNCONFIRMED ownership loss. COMPLETE only stops future calls; ADC normally remains enabled/idle. Reader has no public stop/reset/cancel and must not gain one for this run. |

The fixed setup still requires finite nominal reference >2.4F and <=3.6F and
divider >=1, even though readButtons does not compute a voltage
(`power.cpp:36-46,431-432`; `src/config.h:39-40`). Preserve these development
values and all guards; do not treat them as a measured reference/divider or
silently waive them for A1. A floating unconnected A1 may return any admitted
14-bit code, including repeat values or endpoints. No expected raw range,
specific voltage, NONE button state or noise-quality threshold should be invented.

## Scope and prerequisites before an actual run

1. Record one diagnostic revision under D051/D052 and the user's current bare-board
   authorization: MATCH0/MOTORS_ALLOWED0, existing A0/A1 assignments and128 captures,
   only exclusive_adc=true. No external connection, grant to another owner,
   threshold calibration, output pin, remote command or policy change by implication.
   R8 is preserved because no pin/voltage/wiring assumption is changed; the run
   makes no PINMAP OK claim. D052 explicitly permits eligible bare-board diagnostics
   (`state/DECISIONS.md:455-466`), while D075 permits software preparation (`:841`).
2. Explicitly reconcile D078's current software/compile-only authorization and
   unresolved SC-AJ with this **observation-only** diagnostic (`DECISIONS.md:886-903`;
   `P2_power_contract.md`, clock paragraphs). Source guards show nominal lineage,
   not MSI calibration lock, true frequency or silicon-revision history
   (`P2_adc_ownership.md:144-192`). Preserve the stock clock/power configuration.
   Recorded micros intervals may characterize this image's clock observations;
   they cannot close SC-AJ, establish calibrated100us/1ms physical limits or
   approve production runtime. This needs a visible narrow decision, not a silent
   assertion that earlier ADC runtime qualification has passed.
3. Independently review the complete exact sketch/loader/startup/callback image
   for no stock ADC1 call, ADC4 producer, DAC writer, clock/power mutation or
   concurrent pad/register owner. A new sketch reset/boot and a static grant do
   not themselves prove that exclusion. Installed F097/F108 are source evidence,
   not this run's live ownership (`state/FACTS.md:258,350`). Let the unchanged
   Reader reject the live environment; preserve SETUP/ADC/OWNERSHIP failures as
   useful outcomes rather than weakening checks or inventing successful cleanup.
4. Compile and inspect that exact enabled revision, including actual staged
   sources, ELF/package/loader identities, retained native operations, startup and
   conditional load fit. The false-grant D112 model (peak17128, Runner9892 bytes)
   is a baseline, not an enabled-image receipt (`P2_ui_bench_validation.md:48-65`).
   Review any narrowly pinned upload entry separately before execution; never use
   a generic bypass or reinterpret a compile-only command as run authorization.
5. Use a reviewed, bounded MEM-AP readout specialized to this exact build and ABI.
   The existing D104 approach verifies deployed loader/sketch before private RAM,
   follows bounded LLEXT mappings, reads terminal evidence twice and never halts,
   resets or writes the MCU (`P2_runtime_inert_contract.md:96-109`). Its script is
   pinned to runtimeDiagnostics and is **not** a UI reader (`tools/runtime_capture.py:25-38,332-355`).
   D112's offline ABI gives Report132 bytes at Runner+16 and128 Capture records
   of76 bytes, but all symbol/field offsets and padding must be pinned again from
   the enabled image (`P2_ui_bench_raw/target_bf67d46d_bench-default_checked/audit.json`, abi).
   Read only terminal COMPLETE/FAULT evidence and published records, confirm two
   stable observations and unchanged mapping, preserve partial native failures,
   and derive a finite byte/read/time budget before any read. Do not return data
   as COMPLETE merely because count is128 or because a fixed host wait elapsed.

If the clock freezes, the wrapper can remain RUNNING on early polls; finite
storage does not promise a wall-time watchdog. A capture timeout/nonterminal
observation must remain a failed/incomplete diagnostic, without a hidden reset
or ADC cleanup operation. Capture retrieval itself is separately observable work,
not evidence that the run finished before attachment.

For healthy admitted samples, the actual decoder preserves source identity and
returns UNCONFIGURED because BUTTON_WINDOWS_CONFIGURED remains0
(`src/hal/ui.cpp:39-43,61-74`; `src/config.h:34`). That is a successful raw-source
diagnostic with unavailable logical interpretation, not a detected release.
Setup failure, a partial FAULT capture and full128-record COMPLETE are all honest
possible outcomes. A useful result reports which occurred and the observed
status/shutdown/source/wrapper durations; it supplies no button accuracy,
calibration, settling/carryover, voltage tolerance, full-loop WCET or human gate.
