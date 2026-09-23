# Next motor_stand software increment

Read-only bounded audit,2026-09-24. No source/config/test/ledger changes, test
execution or board actions. This refresh narrows the earlier feasibility report
using the actual D095 halt contract; it does not adopt a new motor authority.

**Recommended next action:** freeze a small contract for a **one-shot native
setup/inhibition diagnostic** under `bench/motor_stand`, default disabled and
compile-only. Do not write another synthetic Robot/Gate controller merely to
fill the named directory. Full B4/B7 remain explicitly excluded.

## Smallest distinct work

One existing `motors::UnoQPort` and one `MotorGate`; passive construction and
`port()` binding (`motor_port_unoq.h:9-15`, `motor_port_unoq.cpp:174-191`). An
explicit default-false grant suppresses **all** begin/halt/clock/backend calls.
Require MATCH0/MOTORS_ALLOWED0; no native profile, pin or period changes.

For a software fixture's granted case, call actual Gate.begin once, preserve its
bool and immediate fault, then call actual Gate.halt once and preserve the full
HaltResult. Become terminal; repeated setup/poll/report access performs no I/O.
No apply, reset, RobotResult, synthetic START, token, opponent or contact is needed.
This retains a real diagnostic path currently absent from the never-called
`p2_motor_native_compile` exercise (`src/native_motor_probe.cpp:7-13` there).

D095 already resolves failure cleanup: after **any attempted begin**, even failed
setup, first halt performs one existing LOW/all-writable-zero/settle pass. It
does not configure/retry or invent an application receipt. Begin may already
have done its own bounded cleanup; do not erase that history or call the later
halt a repeated begin cleanup. Preserve both begin and halt results, including
the existing IO upgrade, attempted/inhibition_confirmed/timing_valid fields.
Successful halt ordinarily retains STOPPED, which is not a new trial failure.
See `P2_app_transaction_contract.md:25-53`, `motors.cpp:79-98,200-225`.

Minimum ownership is new sketch and small bench-owned public owner/report/native
binding, with no core/HAL/locked-test change. Freeze independent checks for false-
grant and terminal passivity, exactly one begin/halt, each actual failure outcome,
no fabricated clock or inhibition proof, wrap/bad-clock preservation, no HIGH or
nonzero pulse, and immutable retained report. Then checked compile/source/ELF/
startup/loader review. No upload-key addition or default-true grant. This prepares
native setup/LOW-zero observations; it proves neither waveform nor coast/kill
from a powered state. Even MOTORS_ALLOWED0 begin configures proposed header pads
and timers, so a later actual run needs separate exact setup/ownership review.

## The actual blockers remain

P2 B4 requires each side's forward/reverse/brake/coast and EN kill within a tick;
B7 requires20 full-forward/full-reverse cycles and no reset on a half-charged pack
(`docs/prompts/P2_hal_bench.md:14,17`). Current Gate.apply accepts genuine
RobotResult only (`motors.h:35-44`; `P2_motor_gate_contract.md:34-61`); Robot has no
arbitrary wheel selector and DRIVE_TEST remains unavailable (`fsm.h:479-511`).

Directional B4 therefore needs a **separate recorded stand-command authority
contract** before implementation: how real Countdown qualification, one actual
Governor pass, fresh identity and applied feedback reach the same sole MotorGate
writer while the existing Robot apply path remains unchanged. Below-full caps
alone do not authorize a constructed/edited RobotResult. No such seam is already
provided by a public struct or D051's engineering delegation.

Full B7 needs an additional **explicit bench-only resolution of the R6 conflict**.
The governor reserves full duty for centered contact ATTACK (`governor.cpp:10-33`),
Gate checks it independently (`motors.cpp:133-139`), and Robot ATTACK never produces
full reverse (`fsm.cpp:79-97`). Do not manufacture contact or weaken these checks
to obtain a reversal. Any adopted exception would need a visibly amended scope,
defined dwell/cycle/reversal semantics and independent safety regressions; none
is selected here. Actual energization also still needs that run's STAND OK and
verified wiring/ownership. D051/D075 do not supply those facts or permissions
(`DECISIONS.md:442-453,841-853`); R1/R6/R7/R8 remain in force.

## Why another inert simulation is not the next increment

D091 already composed actual Robot -> inert Gate -> Recorder, retained the full
5.1s hold, genuine tokens/applied-zero receipts,200s recording and terminal STOP
on MCU (`P2_recorder_bench_validation.md:65-79`). D104 additionally exercised the
actual Runtime with absent sources (`P2_runtime_inert_validation.md:81-98`).
These are honest synthetic/inert evidence, not motor trials. Repeating them as
`motor_stand` adds no missing command authority or physical B4/B7 evidence.
Reuse their regression composition if a later authority contract is adopted;
do not fork their scheduler, strategy, driver or provenance rules now.
