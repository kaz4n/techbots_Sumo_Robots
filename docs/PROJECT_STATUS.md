# Current project status

Updated 27 September 2026, 03:43 Dubai. Connected hardware: **UNO Q only**.

The firmware modules and commissioning software are implemented. The latest
inhibited board diagnostic delivered a complete synthetic recording: **5,001
frames and 8 events**, with the expected session, opening envelope and checksum,
and no reported loss. The receiver saved the original wire data and CSV files.
[Result and evidence](../state/analysis/P7_recorder_repeat_delivery_actual_validation.md).

The remaining release tooling is implemented and reviewed: identified application
delivery, static/Immediate competition compilation, guarded deployment and paired
recording reception. Their focused suites passed 9 and 6 tests respectively.
The current competition build **passed on the UNO Q**, including package and
layout validation and all nine closing checks. The package is 92,092 bytes; see
[the compile evidence](../state/analysis/P7_match_static_actual_validation.md).
It was not uploaded. The board retains the inhibited synthetic diagnostic.

The [full requirement audit](../state/analysis/P7_full_requirement_audit_20260927.md)
identified P2.2 measurement preparation: outer-loop timing and a fixed
five-minute sample window. D243 now implements it with 16 focused cases/143
assertions, independent review and two passing current target builds. Offline
ARM inspection proves timing-observer retention and ordinary-profile exclusion;
the production package is byte-identical to D241. See the
[current timing/build evidence](../state/analysis/P7_outer_loop_timing_actual_validation.md).
A live-sensor timing trial still needs the assembled robot. The user approved
the dedicated B7 full-power bench exception; D244 software implementation is now
in progress. Physical B7 acceptance and specific STAND OK remain outstanding. P6 judge deliverables
remain conditional on the real P4 gate. The full project is not complete.

The connected-board result uses synthetic inputs. Wiring, pin acceptance,
sensor calibration, actual motor behavior, initialized robot timing, stopping
and edge performance, ring trials and human phase gates remain unverified.
These need the assembled robot; none is inferred from the diagnostic.

For the next round, export and validate the recording before normal reset or
power-off. The existing service reset preserves the recorder and motor
inhibition; it is not a command to rearm a match. Physical restart procedures
and rehearsal still need qualification.

The schedule remains: scope decision at the end of 28 September, code freeze
on 1 October at 21:00, rehearsal on 2 October and competition on 3 October.
See [the plan](PLAN.md), [runbook](RUNBOOK.md), and the current
[engineering handoff](../state/CODEX_HANDOFF.md). No phase gate has been invented.
