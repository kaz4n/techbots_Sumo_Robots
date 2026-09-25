# Resume SumoX-26 with Codex

Active phase: **P7 software/release preparation**, under D051/D075/D122/D137.
Physical/human gates remain pending. Assumptions, dates and host tests are not
physical acceptance. Do not reset the project to P0.

1. Read AGENTS.md fully, state/CODEX_HANDOFF.md and CODEX_EXECUTION.md, latest
   PROGRESS/DECISIONS/FACTS/TUNING_LOG, active P7 prompt and relevant open findings.
   Check nested instructions, Git status, actual Asia/Dubai time and free space.
   Preserve uncommitted user work. PROGRESS has legacy non-UTF8 bytes: append
   without re-encoding its history. The handoff holds the exact current next task.
2. Read current native evidence before any device action. D160 is the last
   successful upload (static/default/M0); its runtime stopped at epoch3. D161's
   passive diagnosis confirms invalid MotorGate application feedback but does
   not identify the original failed callback. D172 compiled the active inert
   diagnostic; D173 observed its file ABI; D174-D177 decoding/upload/capture/glue
   are host-tested. Active diagnostic execution, native startup and WCET remain
   unqualified. The user disconnected the board; do not assume current access.
   D178 subsequently repaired offline capture failure reporting (13new+45existing
   Python tests and separate review PASS); its evidence is in the handoff.
   No device operation or firmware change occurred during that host continuation.
3. All old native scopes are consumed. Never rerun a historical launcher, repin
   its consumed manifest, reset the MCU or infer that an old capture layout fits
   changed firmware. A new operation needs fresh source/artifact/identity binding
   and review using the existing bounded primitives. Preserve original failures.
4. The user permits testing a bare UNO Q, and requests no other hardware now.
   No motor-capable upload/run has fresh STAND OK or RING OK. D051 engineering
   delegation permits documented software choices; it does not create measured
   acceptance, PINMAP/EXPLAINED approval or human GATE Pn PASS.
5. Storage is constrained: recheck before large work. Read state/STORAGE_LOG.md.
   Use Python-B, small owned RAM fixtures and serial builds; retain compact
   results/source hashes. Remove only verified disposable outputs when permitted.
   The policy-blocked build/stage/motor_fault and all other denied deletion
   targets remain untouched, including implicit staging cleanup. Do not retry
   through another method or modify paging/persistent virtual disks.
6. P0-P5 physical/human packets, D121 B7/R6 conflict, native dump lifecycle and
   SC-AP release readiness remain pending. P6 is conditional; P7 incomplete.
   Actual P3 not passed by end28Sep requires reactive+SIDESTEP/DIRECT+recorder,
   dropping ARC/WAIT/P6 polish. P6 also needs actual P4 by30Sep. Freeze1Oct21:00
   Dubai; rehearsal2Oct; competition3Oct. No scheduled date creates a gate.
7. Use independent spec-derived tests and a separate read-only reviewer. Label
   second Codex contexts as same-model, not cross-model/human review. Preserve
   locked tests and all existing assertions. Commit finished tasks promptly;
   never push, rewrite history or move release tags without authorization.

At each boundary, save completed work/commits, actual validations and failures,
limitations, active process IDs (if any) and the exact next eligible task. Keep
this prompt general; use the current handoff instead of stale embedded steps.
