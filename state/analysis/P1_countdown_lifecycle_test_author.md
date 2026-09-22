# P1 independent countdown Lifecycle test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: test the production countdown::Lifecycle wrapper from public contract
2e629c1, B3 and D-018/D-019/D-024/D-035. Owned files are
`tests/locked/test_countdown_lifecycle.cpp` and this report. Read public
countdown.h/config, approved decisions and P1_countdown_lifecycle_contract.md;
AGENTS was read in this continuous session. No core implementation cpp was
read, and no established locked test, config, header or shared build was edited.
No build or commit was run.

The 17 cases call production Lifecycle directly. They cover the qualified
release anchor, delayed release qualification, full 5.1 s hold, exact GO and
single heading-reset pulse, raw gyro mean versus prior bias, calibration-window
endpoints, duplicate timestamps, too-few/invalid/spread rejection, and ignored
previous-bias arguments outside an accepted release. Warning/snapshot window
starts, latest zero snapshot, high opponent-bit masking and GO exclusion are
checked without treating those diagnostics as motor permission.

Cancellation tests make MODE qualify exactly at calibration completion and GO,
and apply immediate STOP at those boundaries. The expected retained bias
distinguishes cancellation-before-sampling from finishing calibration first.
Pending-attempt cancellation clears attempt evidence. In contrast, both logical
BOTH and immediate STOP after GO preserve completed bias/count/warning/snapshot
evidence while Controller remains STOPPED and inhibited.

Invalid service starts remain explicit through GO and post-GO STOP, without a
new invented gate veto; pending cancellation clears that failure. New accepted
release starts fresh services with its own supplied bias. Reset clears all
evidence and still rejects a boot-held START as a valid press/release sequence.

Wrapped timestamp tests include release qualification, service windows and GO.
A deliberately sparse legal-gap stream also makes Services' cumulative elapsed
time finish while the existing Gate's wrapped release-relative time still says
HOLDING. The wrapper must preserve Gate's result and cannot grant motion merely
because Services finished. This tests the committed Gate-authority contract;
it does not alter Gate timing or claim realistic scheduler operation.

Static handoff: 17 cases, CHECK/CHECK_FALSE only, no trailing whitespace. Parent
owns host/sanitizer runtime verification and establishment of these new locked
tests. After establishment, AGENTS locked-test protection applies.

Limits: inputs are supplied logical buttons and claimed fresh raw/confirmed
readings. These tests do not verify A1 decoding, physical IMU freshness, actual
bias/heading application, HAL reset, MotorGate/EN writes, full Robot edge/STOP
arbitration, real timing or a phase gate. Next action: parent reviews/runs the
frozen suite and records actual evidence before committing.
