# D091 identified inert run 1

2026-09-23 Asia/Dubai. Target UNO Q ADB2629958581. User explicitly connected only
UNO Q and authorized bare-board tests. No other hardware is assumed connected.
No STAND/RING motor authorization is used or needed for this reviewed inert image.

Base revision19f6f7e plus exact staged source
1502e9484068921fe3f96adef402e12fc85a00093b544e4a6c0dee165476b583,
74 files byte-matched to target. ELF eff3e050072b41d888c343ea57c4d966069882892a7dc50bb0224946a26a798d;
ZSK0448e3ac5a5409bdfd08226f42f0d74c66dbe85d7bfd2ffb27a76acc3a7bfd2a.
Review: state/reviews/P2_recorder_bench_review_raw/source_approval.json.

Scope: CLI upload existing reviewed artifact, default startup, MATCH0,
MOTORS_ALLOWED0. This upload resets/restarts the MCU. Synthetic200s recording,
inert checked Gate callbacks, no native sensor/motor/ADC/QTR/IMU/matrix/UART/RX
or Bridge setup. Strong empty loop hook. No router/daemon changes. Fixeddiagnostic
and CRC freeze afterSTOP/sealing. Do not reupload changed bytes under this record.

Capture is a separate read-only step after reviewed pins/guards are ready.
This run cannot satisfy physical sensors, native transport, fullrobotWCET,
SC-AJ calibrated time, B7 or human phase gates.

## Observed outcome - 2026-09-23 17:38 +04

Software committed17bb38a; exact bytes above unchanged. Upload exit0. First capture
timed out before private RAM; reviewed flash subdivision retry completed without
reupload/reset or daemon action. Evidence runtime_retry1/ and runtime_summary.json.
Actual MCU-clock200000998us recording,5001frames/8events, CRC900325728 verified
independently from two identical captured pools. All actual duties remain zero.
Expected absent-IMU calibration rejection is logged. Native UART was not tested.
See P2_recorder_bench_validation.md for timing/memory numbers and explicit limits.
Board remains frozen in this inert image. No further board action needed for this
scoped task; next work is SC-AK software timing integration.
