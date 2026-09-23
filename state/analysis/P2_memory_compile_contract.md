# D-071: isolated recorder memory compilation

2026-09-23. Scope: SC-AH/B15/P2 B8 planning evidence only. D-051 delegates this
engineering choice; no human phase gate or physical result is inferred.

1. Production `src/config.h`, tests, app and upload allowlist remain unchanged.
   Prepare separate fresh source roots under `build/memory_sources/` at 50Hz and
   25Hz. The latter changes exactly the existing `LOG_HZ = 50U` literal to 25U
   in its copied config. No preprocessor override, staged-file mutation or loader
   change. The 25Hz fallback is an experiment, not production adoption.
2. `bench/p2_recorder_memory` owns exactly one static actual `fsm::Robot` and one
   static actual `recorder::AttemptRecorder`. This narrowly supersedes D-070's
   no-hardware-instance restriction for compile evidence. No separate frame/event
   owner, automatic full-owner temporary in probe code or app integration.
3. `setup()` only assigns the owner, ABI and probe addresses to the public
   volatile pointer slots. `loop()` is empty. No probe is invoked. Both MATCH and
   MOTORS_ALLOWED must be zero at compile time. No Arduino/peripheral/Bridge API,
   clock, serial path or dynamic allocation is introduced.
4. Never-called noinline probes retain Robot::step, recorder::consume, read-only
   frame/event/summary queries and reset paths. Query results escape through
   caller-owned View. Reset notifies the recorder then resets Robot. All arguments
   are caller supplied; wrappers do not instantiate storage owners. Inspect the
   underlying Robot reset temporary separately; no stack-safety claim follows.
5. ABI version1 is 24 little-endian uint32 words (96 bytes on the target): version,
   record_bytes, log_hz, window_ms, frame_capacity, event_capacity, pointer_bytes,
   size_t_bytes, eight sizes, eight alignments. Indices: Robot, AttemptRecorder,
   FrameBuffer, StoredFrame, EventBuffer, AttemptSummary, RobotInput, RobotResult.
   The public header fixes the layout and slots before implementation/test authoring.
6. `tools/recorder_memory_build.py` exposes `prepare_source(rate_hz)` returning a
   fresh candidate Path, `compile_candidate(rate_hz)` and `main(argv=None)`.
   ROOT initially equals the repository root. Valid rates are integer25/50 only.
   CLI requires both `--log-hz {25,50}` and `--compile-only`; unknown flags reject
   before preparation/transport. No match/upload/startup option exists.
7. Preparation validates source/bench/build ancestry against ROOT, rejects
   symlinks, copies src plus this bench without overwriting any candidate, checks
   exactly one expected config literal, then records a provenance.json containing
   rate, original/candidate config hashes and relative-path SHA256 maps for both
   source and candidate input files. Original files stay byte-identical. Missing
   files/literal, unsafe paths, invalid rate and copy errors fail explicitly.
8. Compilation uses existing board_tool.flash with candidate ROOT and only
   sketch=bench/p2_recorder_memory, match=False, compile_only=True,startup=default.
   Restore board_tool.ROOT even on failure. Print candidate path/provenance before
   transport. Any transport/build failure propagates nonzero. Retain failed roots.
   Existing content-addressed staging and exact installed-core checks apply.
9. Host substitutes verify setup plus10000 loop calls make zero API/probe/heap
   calls and publish exact addresses; positive motor or MATCH builds reject.
   Controlled tests check validation, isolated literal change, manifests, original
   preservation, failure propagation/restoration and existing upload refusal for
   this bench in all match/startup combinations before transport. A separate
   candidate harness checks25Hz/5001 capacity,40ms cadence and endpoint retention,
   missing-slot accounting; run the original locked tests against the candidate
   unchanged. No weaker production expectations or locked amendments.
10. Actual board compile uses default startup/MATCH0/MOTORS_ALLOWED0 only. Never
    upload, reset, start MCU firmware, open monitors or invoke probes. Preserve
    exact commands/statuses, tool versions, stage hashes, ELF hashes and source
    provenance. A50Hz size-check failure is EXPECTED_OVERSIZE, not build success.
11. Independently inspect final ELF ABI, one-owner census, sections, relocations,
    constructors/init arrays and setup/loop/call retention. Sum SHF_ALLOC excluding
    only installed configured no-reloc rodata; distinguish Arduino's RAM estimate
    from file size. Account for alignment/allocator/metadata/transient load costs
    where known, otherwise mark unknown. Compile success proves neither loader
    success/free RAM nor200s/no-gap capture, full-tick WCET, B8 or phase acceptance.

Separate fresh-context same-model reviewer required. This is not cross-model
review. All failures and review findings remain in state/analysis or state/reviews.
