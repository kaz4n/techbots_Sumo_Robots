# Resume SumoX-26 with Codex

Active phase: **P7 software/release preparation**, under D051/D075/D122/D137.
Physical/human gates remain pending. Assumptions, dates and host tests are not
physical acceptance. Do not reset the project to P0.

1. Read AGENTS.md fully, state/CODEX_HANDOFF.md and CODEX_EXECUTION.md, latest
   PROGRESS/DECISIONS/FACTS/TUNING_LOG, active P7 prompt and relevant open findings.
   Check nested instructions, Git status, actual Asia/Dubai time and free space.
   Preserve uncommitted user work. PROGRESS has legacy non-UTF8 bytes: append
   without re-encoding its history. The handoff holds the exact current next task.
2. Read the current handoff before selecting a native task. D184 remains the last
   successful firmware upload (halted isolated M0 diagnostic). D188 static full-app
   diagnostic was target-compiled and its ABI/entry files audited. D189 run01
   rejected old /tmp/remoteocd before uploader CLI; consumed, no new firmware.
   D190 fresh run02 variants now pass62host methods; D191 human-assisted cleanup
   passes37host methods and its three files are staged/hash-verified. The human
   sudo command is pending because protected adbd handles require authentication.
   Read analysis/P7_d190_d191_validation.md and its final review. After the human
   replies CLEANUP DONE, validate the saved result and fresh identity/absence
   before preparing/reviewing actual run02 inputs and using its existing caller.
   No automatic cleanup retry or old owner reuse. Original full-app fault,
   physical setup, RAM/stack/WCET and human gates remain pending.
3. All old native scopes are consumed. Never rerun a historical launcher, repin
   its consumed manifest, reset the MCU or infer that an old capture layout fits
   changed firmware. A new operation needs fresh source/artifact/identity binding
   and review using the existing bounded primitives. Preserve original failures.
4. The latest user explicitly reconnected the board and requested continuation,
   superseding older offline-only paragraphs. Connection/boot must still be
   observed for each distinct native scope. D191 staged files are preparation,
   not cleanup success or firmware execution. Do not request the sudo password
   in chat; the human enters it in the board terminal for the exact reviewed
   command. No motor-capable upload/run has fresh STAND OK or RING OK. D051
   engineering delegation does not create measurements, PINMAP/EXPLAINED approval
   or human GATE Pn PASS. Retain the specific next action in the current handoff.
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
