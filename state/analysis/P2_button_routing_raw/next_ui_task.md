# First unfinished B6 task after D087 closes

2026-09-23 Asia/Dubai. Read-only next-task assessment; no rendering or hardware
policy is adopted here. D087 completes raw decoder and explicit gesture routing,
not the physical button circuit, matrix output or application scheduler.

Implement the actual matrix rendering/output path next, continuing P2 B6 under
D051/D075. Read BEHAVIOR B3 and B13 mode table/service menu/battery bar/fault icons,
B14 fault list, P2_hal_bench.md B6 and existing RobotResult/MenuSelection. Existing
fields already expose selected/running mode, countdown phase/release time, masks,
calibration rejection and fault states. A renderer must never influence motion.
Keep core pure; UI can produce a fixed104-byte8x13 frame using supplied time and
explicit available data. Freeze glyph/layout, overlap/priority, countdown final
margin display, battery bar scaling/unavailable indication and fault-display
policy as recorded delegated engineering choices before independent tests. Do not
invent sensor freshness, battery accuracy or service execution from a display.

Existing primary-source lead: P0_G2.md pins core1.0.0 to commit
79b3f1afdad455f55e4a25030953617152c0227c and reports matrixGrayscaleWrite fixed104-byte
copy/flag. Its matrix initialization enables a periodic10us ISR; a bounded caller
alone cannot prove complete tick WCET. P0_matrix_readout_plan.md preserves actual
installed source/constructor/startup evidence and explains matrix-active timing
limits. Re-read installed header/loader/matrix.inc and relevant exact artifacts
before choosing the native adapter; historical seeded verification is not current
runtime proof. No stock scrolling/waiting text routine belongs in the1kHz tick.
A deterministic pure renderer and checked bounded adapter can be tested with
independent literal pixel fixtures/guard bytes and real retained target calls.
Retain an inert compile-only probe and all upload refusals; avoid a demo-only
scaffold. No new board/MCU action or additional hardware request is needed now.

Later unfinished work remains: QTR_CAL consumer, live service views, bounded IDLE
recorder transport and integrated scheduler. ADC freshness/cadence, asynchronous
QTR work, IMU600us/motor150us/twoADC100us ceiling conflict and SC-AJ/F091 need explicit
scheduling/runtime resolution. Complete800us worst-case is physical evidence.
SC-A still forbids pretending START/BOTH at the same voltage are distinguishable;
production button windows remain unconfigured. All physical/human gates pending.
