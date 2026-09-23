# D-069: offline B8 fixed frame storage

Eligibility: D-068 selects this narrow offline track under D-051. P0/P1
acceptance remains pending. This component alone cannot pass B8 or a phase gate.
Source: BEHAVIOR B15, D-028 event retention, D-060 frame evidence/lifecycle,
src/core/logframe.h and P2 B8. Public interface: hal/recorder_frames.h.

1. Own a fixed array of StoredFrame, each exactly25 codec bytes plus1 PackStatus
   byte. Preserve supplied bytes verbatim, including INVALID records; do not
   re-encode, decode, sort, create a clock/cadence or synthesize missing frames.
   Known status values are OK, CLAMPED and INVALID. No claim of input semantic
   validation follows: the existing core codec/Robot remains responsible.
2. Retain latest frames in insertion order. While not full append at the end;
   when full replace exactly the oldest frame. Every replacement increments
   overwrittenCount with the existing uint32 saturatingIncrement operation.
   Overwrite marks the attempt's evidence incomplete; never hide it as gap-free.
3. Reject an unknown status value without modifying retained bytes, size, order
   or other counters. Increment only rejectedStatusCount, saturating. Known
   INVALID is accepted and counted, with its bytes/status retained. CLAMPED and
   INVALID counters describe all accepted records since reset, including evicted
   records, saturating independently. No rejection can stop events or motion.
4. incomplete is true iff any overwrite, unknown-status rejection, CLAMPED or
   INVALID has occurred since reset. This is local buffer completeness only;
   later composition must retain separate core/frame/event/timing losses.
5. at(index) returns a const pointer oldest-first, or null outside size, including
   SIZE_MAX. Equal/wrapped/nonmonotonic timestamp bytes retain insertion order.
   Borrowed pointers must not survive any append/reset/destruction. append must
   also work if its source bytes refer to a currently retained frame: take a
   fixed-size copy before mutating the selected destination or ring state.
6. reset clears only indices/counters in constant work. Old records become
   inaccessible through at; do not clear the payload array. Construction occurs
   before control-loop use. Delete whole-owner copy/assignment. No heap, Arduino,
   clock, Linux/Bridge/serial/device calls, exceptions, RTTI or unbounded loops.
7. Define config::LOG_FRAME_WINDOW_MS=200000 from B15 and derived capacity
   ceil(window_ms*LOG_HZ/1000)+1. At unchanged LOG_HZ50 capacity is10001,
   conservatively retaining t=0 and final t=200s (or an off-cadence final frame).
   This is a byte-capacity requirement; it does not prove actual sampling quality,
   elapsed time, a complete match, or that the countdown is outside that window.
8. Capacity at50Hz consumes260026 frame/status bytes; adding4096*8 event payload
   yields292794 bytes before metadata/application. This exceeds the installed
   262144-byte LLEXT pool even without the existing app. Preserve this explicit
   deployment blocker. B15's conditional25Hz would yield162794 payload bytes;
   do not silently change LOG_HZ, existing B16 values or claim target/free-RAM fit.
9. Reuse the existing core EventBuffer later; no duplicate event ring now.
   This buffer has no automatic Robot/reset/service/start/stop behavior. Future
   composition must clear only on an accepted attempt, preserve final receipt
   provenance and last-match data, and gate dumps to IDLE. That work is separate.
10. Independent tests derive only from this contract/spec/public headers. Cover
    empty/out-of-range, exact capacity-1/capacity/capacity+1, multiple wraps,
    literal mixed-status records, unknown status at empty/full, retained borrowing,
    logical reset/reuse, event-buffer independence, endpoint capacity and a
    fixed-seed oracle sequence. Existing saturation helper boundary tests remain
    authoritative; inspect that every new counter actually uses that helper.
    Run relevant normal and sanitizer host checks and fresh read-only review.

No app integration, target upload, transport, sensor/motor action, pin choice,
locked-test amendment, measured RAM/WCET, phase closure or human acceptance.
