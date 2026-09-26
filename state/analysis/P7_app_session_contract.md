# D234 application session forwarding contract

Under D051, close the application mapping gap exposed by D224 without granting
hardware ownership. Add explicit uint32 receive-stream ID and uint64 session ID
in config, both zero by default; reject undefined stream enum IDs before cast.
Map them exactly into SetupGrants and forward the same session into every dump
Context. Keep native setup admission, per-Transfer identity freezing, local
service/IDLE/MotorGate checks, legacy-zero wire behavior and all defaults.

This is identity forwarding only. A configured session does not prove freshness
across resets, independent expected epoch, physical origin, or successful UART
delivery. Deployment's existing protected-literal parser must recognize both
new fields and refuse nondefault values until a separate source-bound receive
workflow qualifies their freshness. Preserve all existing grants and motor
permission/physical evidence requirements; this task runs no board operation.

Test real configuration mapping across build flags and uint64 boundaries,
undefined enum rejection, full Runtime setup and wire identity retention,
legacy application scenarios, and deployment default admission/nondefault and
preprocessor refusal. No locked tests change. Keep unique failures/evidence.
