# Current project status

Updated 27 September 2026, 02:42 Dubai. Connected hardware: **UNO Q only**.

The firmware modules and commissioning software are implemented. The latest
inhibited board diagnostic delivered a complete synthetic recording: **5,001
frames and 8 events**, with the expected session, opening envelope and checksum,
and no reported loss. The receiver saved the original wire data and CSV files.
[Result and evidence](../state/analysis/P7_recorder_repeat_delivery_actual_validation.md).

Two release-tooling items are being closed: pairing a qualified application
upload with a fresh recording session, and building the current competition
firmware with static linking and Immediate startup. The application delivery
tool has passed nine focused tests and independent source review.
The production profile will receive a compile-only check. Motor-enabled firmware
has not been authorized for upload or operation.

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
