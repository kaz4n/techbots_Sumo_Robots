# Offline B8 composition follow-up - proposal, not adopted

2026-09-23 read-only audit by separate Codex context recorder_contract_audit,
coordinator transcription. D-068 admits offline RAM storage preparation only;
this document does not adopt a contract, integrate the app, clear a phase gate
or authorize target use. D-069 frame storage is the completed prerequisite.

Recommended next bounded unit is an attempt-scoped owner of FrameBuffer and the
existing EventBuffer. Contract must precede code/independent tests. Own no clock,
cadence, motion, transport or allocation; handle at most21 events and one frame
per call. Delete whole-owner copying. Keep boot/outside-attempt diagnostics
explicitly outside its ownership until a later defined owner exists.

Proposed lifecycle: EMPTY -> RECORDING on accepted match START -> DRAINING on
STOPPED, inhibited Escape fault or COUNTDOWN cancellation -> SEALED after the
next result flushes the stopping tick. An explicit onRobotReset notification
preserves bytes and marks an unfinished attempt INTERRUPTED/incomplete. Only
a validated newer accepted START may clear both buffers. Service START, reset
and menu changes never clear last-match data. No generic public clear method.

Critical source ordering, fsm_robot.cpp:74-89,131-192,251-274,762-860:
admit current token -> receive prior applied receipt/frame/events -> lifecycle
possibly begins new attempt/reset counters -> publish current decision events
-> prepare current pending frame. Thus a START result's ready frame is from
the prior epoch. Events before START are prior receipt extensions; do not copy
them or that frame into the new attempt. Validate the START marker/mode/time
and batch bound before destroying old data. Decide how boundary-envelope loss
counters with ambiguous old/new attribution are labeled conservatively.

RobotResult public API has no reset pulse or pending-frame flag. Do not infer
a reset from counters/state; use an explicit caller notification. Missing final
receipt must mark loss, never fabricate a zero-duty frame. Store frame_token,
not the current result token, as provenance; enforce monotonic exactly-once
consumption, reject older/malformed identities, report gaps and replay handling.
An ordinary ready frame belongs to the previous token. Preserve uint64 limits
and timestamp wrap without sorting raw timestamps.

Special terminal case: Robot::exhaust at fsm_robot.cpp:863-883 can return token0,
fresh=false while flushing the previous frame/events. A blind !fresh early
return loses real evidence. Define one terminal-envelope rule after UINT64_MAX
or an explicit unsupported-terminal/incomplete policy before implementation.

Keep distinct loss domains: FrameBuffer overwrite/status counters; EventBuffer
first4096 overflow/rejections; per-envelope EventBatch rejected/invalid counts;
consumer semantic/identity losses; cumulative core skipped_frames (snapshot,
never repeatedly sum); latest tick statistics and core incomplete flags. Bound
count before indexing, validate metadata then packEvent then append; failures
never stop frame retention, recursively emit events or affect motion.

Independent tests should derive from a frozen public contract and cover accepted
START replacement, rejected/replayed START preserving bytes, delayed final frames,
cancellation/STOP/Escape fault, Robot reset preservation, service intents, gaps,
unknown enums/count corruption, token exhaustion, all loss domains, event4096
overflow while frames continue, and deterministic reference-model streams.

Deployment remains blocked: unchanged50Hz uses292794 payload bytes before
metadata/application, exceeding installed262144 LLEXT pool. B15 conditional25Hz
is a future explicit choice; no LOG_HZ reduction or fit assertion here. App
integration and production Bridge/dump policy remain outside D-068.
