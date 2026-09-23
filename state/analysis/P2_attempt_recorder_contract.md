# D-070: offline attempt recording owner

Adopted under D-051/D-068, before source and independent tests. B15/D-028/D-060
plus public RobotResult are sources. This owns RAM only, not app integration,
transport, dump eligibility, scheduling, motor authority or hardware acceptance.
Use recorder.h/.cpp; FrameBuffer and EventBuffer remain the sole payload owners.

1. Construction before runtime; delete owner copying. Each consume processes
   at most21 events and one frame. No heap, clock, I/O, dynamic strings, motion
   output, global instance or unbounded work. No public clear/storage-reset API.
2. Keep highest consumed nonzero token across attempts and onRobotReset. An
   equal token is IGNORED_DUPLICATE with absolutely no mutation, even if payload
   differs. Lower tokens, nonzero newer !fresh, or ordinary zero tokens return
   REJECTED; while RECORDING/DRAINING increment rejected_results, otherwise
   preserve stored summary. Rejected malformed newer fresh envelopes consume
   their token so replay cannot erase or append later. Newer !fresh does not.
   Track every newer fresh token including outside attempts. Gaps count missing
   result envelopes (delta-1, uint32 saturating) only while active, unless a valid
   new START replaces that epoch. Ignore payload outside attempts except START.
3. Only a newer fresh lifecycle.gate.start_release can start/replace an attempt.
   Before clearing require a known output state0..11, known running_mode1..6,
   events.count<=21, and exactly one START_RELEASE event in the whole batch.
   That marker must pass validEventMetadata, have detail==running_mode and
   t_us==gate.release_us. Any failure rejects the envelope without clearing old
   data; increment active rejected_results. Service/menu intents never clear.
4. On accepted START reset both buffers and AttemptSummary, set epoch_token,
   release_us/mode; enter RECORDING. Discard its prior-epoch ready frame and
   event prefix preceding START; append marker and suffix in order. Import the
   complete envelope's upstream batch loss counters conservatively: their old/new
   attribution is unavailable; they describe observed boundary-envelope loss.
   No previous frame/prefix is counted as a new-attempt loss. Snapshot core
   counters/timing and latch GO if supplied. An accepted START is result count1.
5. For each active newer fresh result require known state0..11 before consuming
   payload; invalid state rejects without payload mutation but consumes token.
   Valid-state results append ordered events then ready frame (order across the
   separate arrays is not asserted), update summary and observed_results.
   Frame must have token==current token-1, token>=epoch_token and token strictly
   greater than last accepted frame token. Otherwise increment identity_rejected
   and discard only that frame. Exact byte/status ownership remains D-069; an
   unknown status uses FrameBuffer rejection and is not accepted for final flush.
6. For events validate count<=21 before indexing. Oversized count increments
   malformed_batches and processes no entries; frame/summary handling continues.
   Accumulate each envelope rejected/invalid_metadata once with saturating add;
   latch upstream_event_overflow separately. Validate each candidate metadata,
   then packEvent then existing EventBuffer::append. Metadata/pack failure
   increments event_semantic_rejected; full EventBuffer reports its own loss.
   No recursive event, frame suppression or output side effect.
7. Snapshot skipped_frames and TickStatistics rather than summing repeated
   cumulative counters. A decrease in skipped_frames, ticks.ticks, ticks.overruns
   or ticks.max_us, or overruns>ticks, is a source regression: increment
   source_regressions once per envelope, retain the previous affected snapshot
   (skip and ticks separately), still process other payload. Saturated may latch
   but cannot clear; preserve previous ticks.saturated. Latch source timing and
   recording incomplete flags. Any ticks.saturated marks timing incomplete.
8. During RECORDING enter DRAINING after any consumed result with STOPPED;
   EDGE_ESCAPE with escape_fault!=NONE; or observed previous COUNTDOWN then
   current IDLE. Save stopping token. START initializes previous state to
   COUNTDOWN for same-result stop detection; accepted START with IDLE therefore
   drains. Remain RECORDING through ordinary motion/GO. An explicit GO pulse
   latches go_seen; no sensor/duty inference of GO.
9. The next valid-state newer fresh result while DRAINING is one tail flush.
   Accept only a ready frame satisfying rule5 AND frame_token==stopping token;
   another ready frame increments identity_rejected. Missing/rejected final frame
   latches final_frame_missing. Append its event batch and counter/timing snapshot,
   then SEALED. A malformed-state rejected result does not seal, so later gaps
   expose loss. Once SEALED, ignore payload until accepted START. No frame
   synthetic fill, reset inference, sorting of wrapped timestamps or catch-up.
10. onRobotReset preserves all bytes/counters/token identity. RECORDING or
    DRAINING -> INTERRUPTED, interrupted=true; if go_seen latch timing_incomplete.
    EMPTY/SEALED/INTERRUPTED unchanged. It is the future caller's responsibility
    to issue this notification before core reset/end-of-stream while unfinished.
11. Special exhaustion: after highest token UINT64_MAX, accept once a token0,
    fresh=false envelope with TOKEN_EXHAUSTED fault, STOPPED and no start pulse.
    Repeated such terminal envelopes are IGNORED_DUPLICATE. Outside active
    attempt return OUTSIDE_ATTEMPT without changing stored summary. While active,
    process bounded events/source summary and ready frame with expected token
    UINT64_MAX (and stopping-token constraint if draining), then INTERRUPTED;
    set terminal_exhausted/interrupted and timing_incomplete if go_seen. If it
    was DRAINING require final frame or mark missing. No terminal result token
    is invented. Other zero envelopes remain REJECTED.
12. incomplete() iff local frame/event loss, any named rejection/gap/loss counter,
    final_frame_missing/interrupted/terminal_exhausted, upstream overflow, core
    recording/timing flags or saturated ticks. EMPTY clean by default. RECORDING
    and DRAINING are unfinished regardless of this loss flag; never claim a
    complete dump from incomplete()==false alone. observed_results counts valid
    active envelopes including accepted START/tail/terminal, saturating.
13. Public summary is read-only. No per-frame token array: last_frame_token plus
    monotonic ingestion protects identity, packed timestamps remain opaque.
    No timer/API/RAM claims. Keep LOG_HZ50/B16 unchanged and SC-AH deployment
    blocker. This class is not instantiated in firmware or connected to Robot.

Independent tests must cover all rules with literal wire expectations, event
4096 overflow while frames continue, frame overwrite independently, reset/service
preservation, epoch boundary prior-frame/prefix exclusion, token gaps/limits/
replay, final receipt and missing receipt, malformed state/count/metadata/status,
snapshot regression and saturated-add limits, plus fixed-seed oracle sequences.
No implementation .cpp reads by test author. Normal/sanitizer + fresh read-only
review; existing core/locked tests remain untouched.
