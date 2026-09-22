# B3 production lifecycle contract — 2026-09-22 Asia/Dubai

Approved D-018/D-019/D-024/D-035 authorize this composition. The earlier audit
P1_countdown_lifecycle_audit.md identified diagnostic-lifetime details now made
explicit in the public header before source or independent tests.

Use a single ServiceSample timestamp/raw reading plus logical button level,
previous bias and optional immediate qualified STOP. Controller updates first.
Accepted release starts Services; cancellation occurs before sampling. Service
start failure is explicit until canceled/restarted/reset, with no new motor veto.
GO ends pending status and freezes completed service evidence even if a later
STOP arrives. STOP still inhibits via the existing Controller. New release starts
a new attempt; previous-bias arguments outside accepted release are ignored.

Return Controller's gate result unchanged, Services' result, diagnostic start
failure and heading_reset_requested exactly equal to the GO pulse. No HAL reset,
new service policy, gate-timer rewrite or permission based on service completion.
Preserve every established locked case; NEW locked production-wrapper tests must
cover qualified release, full hold, cancellation before calibration/GO deadlines,
raw bias/snapshot/line windows, explicit invalid-bias start, diagnostic retention,
logical/external STOP, reset, duplicates and timestamp wrap. Physical freshness
and real MotorGate writes remain pending.
