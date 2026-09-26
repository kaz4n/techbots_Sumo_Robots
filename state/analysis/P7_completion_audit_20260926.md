# Project completion audit - 26 September 2026

Objective remains the complete SumoX-26 project. Current phase is P7 software /
release preparation, with earlier physical and human gates still open. This is
a targeted current-source gap audit, not a completed requirement-by-requirement
acceptance audit. D207's independently accepted inhibited diagnostic now reaches
its 10000-epoch limit with no recorded callback/SETTLE failure. D195's failure at
application921 and D201's setup FINAL_DEADLINE154us remain distinct preserved
observations; one successful run does not prove an intermittent fault cured.
See P7_motor_const_run_actual_validation.md. D208's ordinary static compile has
returned COMPILE_CHECKED and is independently accepted by review8cd383e4.
D209 ordinary file-only ABI is accepted by review585be669; ordinary entry instructions are now accepted by reviewa30c194b; ordinary
inhibited runtime remains pending.

A separate reused-context same-model read-only reviewer inspected current phase
prompts, PLAN, acceptance packets and operational source/tool paths. Core, HAL,
Runtime, setup binding, analyzers and guarded MATCH deployment are implemented;
the audit did not identify a missing primary behavior module. It did identify
the following concrete remaining software and qualification work.

| Track | Current evidence | Work still required |
|---|---|---|
| Native motor fault localization | D201 observes setup FINAL_DEADLINE154us; D202 moves immutable expected metadata to constants; D207 reaches10000epochs, max519us/missed0 and final callback-level inhibition acknowledgment | Preserve D195/D201 failures and trace truncation; ordinary runtime and full initialized operational timing remain unqualified. No measured speedup or intermittent-cure claim |
| Commissioning firmware | Seven trial wrappers remain inert; ordinary app.ino already binds Runtime, configured grants and native dump port | Separate B4/P3 profile/build/deploy admission using the existing entry; preserve historical inert wrappers. See P7_b4_profile_scope_followup.md |
| Production memory/loading | D208 ordinary static/default/M0/probe0 compilation passes native checks; independent actual review8cd383e4 accepted. Package92944B, structural RAM tail94352B. D185 dynamic deficit and conditional MATCH figures remain historical separate profiles | Ordinary ABI accepted585be669; entry accepted a30c194b, separately bounded inhibited load/run, live stack/headroom and full-source timing; no MATCH/B4 fit inference |
| Recorder and next round | Formatting/storage/runtime software exists; native UART ownership/cancel/reopen remains unqualified | Complete actual prerequisites, same-boot delivery and log-preserving rearm under SC-AP; repair only evidenced defects |
| Operator/release deliverables | Runbook, mode card, rehearsal sheets and kit list drafted | Qualify procedures against operational firmware, print/team review, actual rehearsal, freeze artifacts/tag and human gates |
| Conditional P6 | Plotter, real plots, JUDGE_PACK and demo not delivered | Eligibility requires actual P4 gate by30September and no28September scope cut; do not invent eligibility |

## Commissioning gap source evidence

`bench/motor_direction/motor_direction.ino`, `drive_test`, `turn_accuracy`,
`stopping_distance`, `reactive_test`, `reactive_timing` and `opener_timing` each
assert MOTORS_ALLOWED==0, call runtime.begin(SetupGrants{}) and construct Runtime
without a DumpPort. D180 only wired configured grants/native dump in the ordinary
main app. `tools/app_build_policy.py` pins trial M0 flags; `board_tool.py` refuses
their uploads; `match_deploy.py::validate_request` admits only ordinary MATCH app
with Immediate startup, while config's trial guards require !MATCH.

This is an unfinished transition from host/inert trial validation to runnable
acceptance firmware. Use the existing ordinary app entry with separate checked
profile admission; no duplicate sketch is needed. Merely loosening old wrapper
flags would leave START, sensor setup and evidence delivery absent. Existing
D120/P3/P4 contracts scoped those wrappers to compile-only. The new route can be
designed and tested before physical acceptance, but motor-capable execution
still requires configured facts and fresh identified STAND/RING OK.

## External dependencies and boundaries

Actual sensor/button calibration, pins/electrical checks, physical motor/ring
measurements, organizer answers, explanation and human gates cannot be supplied
by software assumptions. B7 full-reverse braking versus R6 remains a protected
decision; the low-duty B4 sequence is not a substitute. Authenticated scratch
cleanup does not prove UART cancellation/ownership or confer general privileged
permission. Dates and a connected bare controller establish no acceptance.

Today26September does not trigger the28September reactive/SIDESTEP/DIRECT scope
cut or establish P6 eligibility. Freeze remains1October21:00Dubai. The goal stays
active; there is meaningful software work available despite unqualified hardware.

Sources: current named entries and tools above; P2_stand_integration_contract.md,
P3_drive_test_contract.md, P4_reactive_profile_contract.md,
P7_current_app_compile_validation.md, P7_default_qualification_validation.md,
P2_native_dump_prerequisite_followup.md, P7_software_acceptance_packet.md and
docs/prompts/P0-P7. No new tests or board operations were performed by the reviewer.

B4 follow-up review: the unchanged sequence ends in Runtime STOP, while current
UART dumping requires active Runtime service in IDLE. Wiring a FIFO8 port alone
therefore cannot deliver a completed B4 recording. Preserve reset refusal for B4;
use separately bound finite same-boot retained-memory capture first, or adopt a
separately reviewed inhibited service policy. This does not block a host-only
operational entry using existing configuration/grants and zero defaults.
