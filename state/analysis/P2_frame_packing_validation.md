# D102 lossless packing acceptance

2026-09-23 Asia/Dubai. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / scoped
independent review PASS. D101-R1's conditional loader-capacity blocker is closed
for this exact source; physical loadedRAM/stack/WCET and phase gates remain open.

FrameBuffer now stores25-byte payloads and four two-bit status lanes per byte.
Copied read returns exact original bytes/status; bytesAt preserves genuine
borrowed-payload aliases. All5001frames/4096events/25Hz, status/loss counters,
logical reset, CSV/wire and CRC remain unchanged. Current callers explicitly own
their snapshots. Probe View owns its frame; the fixed96-byte ABI record remains.

The independent author never inspected implementation cpp. Eleven new cases
pass20513379assertions each under normal and ASan/UBSan. Existing meaningful
alias, wrap, literal, deque, rate, attempt, timing and CSV assertions remain;
the worker's1021predicate mapping and separate review also check scenario meaning
and fresh owner rereads. No locked test, config, core or historical candidate
changed. Original new-test/harness and two migrated-helper compile failures are
preserved with their corrections; see raw/build_failure_analysis.md and author/.

Final full normal and ASan/UBSan runs each pass1434main/45732368assertions and
178enabled-Gate/4536549assertions. Existing memory tooling23cases pass; inert
recorder runner passes11cases/1479334assertions in each normal/sanitizer profile.
Forty-two general/upload/capture-boundary tooling cases pass with substitutes.
Those checks are host script tests, not board uploads. Exact logs are under
P2_frame_packing_raw and command/status receipts P2_app_build_raw/d102_*.

Actual Runtime dump tests/receiver rerun after packing pass in both motor
configurations: default5/166 and configured21/6085 each. Both1268-byte streams
are identical to D101 (SHA256725d57136686946f15694569d5948de134ffa3a32a3eb4711630d3c52c594765),
including session1476, epoch86,2frames/3events and CRC4237426210. The strict
receiver accepts single-byte fragments and exact expected CSVs. These synthetic
fixtures are not competition or native-UART evidence.

Actual source3bf0da005d3268adfca52bb86f96ab40921c4bb4f2c2d10ea1cd90a8cf2a0f38
has85files. Default and MATCH compile-only exit0, with compiler static payloads
253772B/254156B. Both exact source sets,75objects,6ELFs/2packages, startup and
176imports are verified. Actual target DWARF gives FrameBuffer126300/align4,
StoredFrame26/align1, AttemptRecorder159200/align8, Runtime166216/align8.
The frame owner shrinks3752B on target; MATCH net payload saves3628B because
code grows96B and rodata28B. Its conditional pristine loader peak is258768B,
3376B remaining span/3372B largest payload. Default peak258376B/largest3764B.
Every ordered allocation fits the pinned model, including temporary symbols.
See P2_frame_packing_target_audit.md; GDB's initial display-limit failure and
successful offline retry are preserved. No new ABI compilation was necessary.

Separate fresh-context same-model review passes132sanitized cases/23737247
assertions plus786554public-probe checks, inspects every migrated fixture and
independently verifies target/source evidence. This is not cross-model review.
The same seven inert keys were refreshed only after reviewed source maps matched
actual local staging byte-for-byte; no key or upload scope was added.

No upload/reset/MCU/motor operation, physical qualification, new hardware grant,
measured freeRAM/full800us or human gate occurred. Last MCU image remains the
older D0911502e948. Next eligible P2 integration: local post-STOP service reset
with retained evidence and truthful source lifetimes, then calibration-snippet
delivery and remaining physical-bench software. Native-owner rearm is not implied.
