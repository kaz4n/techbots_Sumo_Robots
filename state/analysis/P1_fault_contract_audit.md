# Remaining B14 host obligations — 2026-09-22

Read-only separate audit by p1_timed_arc_worker; coordinator records its findings.
No new behavior approval, measured duration, hardware operation or gate is implied.

Next unblocked implementation: pure tick statistics in core/logframe, from B14
and the existing B15 FrameInput.tick_max_us field. Caller supplies one measured
execution duration per included match tick; the component reads no clock and
owns no scheduler or match boundary. Count ticks, count strictly greater than
TICK_US, retain the full uint32 maximum, report strictly more than1% using the
overflow-safe integer test overruns > ticks/100. Empty statistics do not exceed
the limit. Report saturation explicitly rather than wrapping; preserve the full
maximum and the existing frame encoder's clamping status. Final interfaces must
be committed before independent tests/source. Do not invent a motor response,
latched fault or a reset trigger. The1% threshold is existing text, not tuning.

Test999/1000/1001us, empty/reset/max, exact1% and either side, large-count integer
arithmetic and saturation through the actual production operation. A host test
proves this arithmetic only: it never proves R4's separate robot WCET<800us.

Other narrowly available calculations:
- Low battery: finite supplied voltage, IDLE and strict voltage<VBAT_WARN_V.
  Do not add latch/hysteresis/match behavior. Full warning integration must resolve
  raw-versus-filtered voltage source; the pure comparison does not select it.
- IMU freshness: initialization success, actual valid-sample presence and supplied
  age<20ms. Unique sample detection/acquisition timestamps remain HAL work; no
  repeated read can be counted as fresh by assumption. Centralize20ms if implemented.

Remaining dependencies:
- Opponent stuck qualification is implemented by StuckFilter/Fusion; actual fault
  event/icon dispatch remains unfinished.
- QTR stuck warning must keep obeying white. Defining "pivoting in place" from
  arbitrary duty signs would invent a predicate; physical freshness also needs
  SC-B. Do not silently turn this warning into sensor suppression.
- Watchdog reset-cause acquisition and availability are P2 HAL facts. Core reset
  defaults inhibit motion; actual actuator/reset safety still needs its own tests.

Sources: BEHAVIOR B14/B15, P1 task1.2, core/logframe.h and governor.h.
