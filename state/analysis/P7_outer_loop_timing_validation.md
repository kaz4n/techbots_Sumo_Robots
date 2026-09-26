# D243 outer-loop timing: source and host validation

27 September 2026, Dubai. **PASS_HOST_ONLY**; independent review is recorded separately.
Contract committed first as a4540854c3a730fe3531a0f6188153e2d0340891. The new
observer is measurement preparation, not a measured five-minute sensor run,
calibrated WCET, physical qualification, motor authority or phase acceptance.

## Implemented boundary

Only the existing SUMOX_TIMING_EVIDENCE app profile owns the new observer. Each
active loop entry reads the existing native clock callback once, publishes the
previous entry interval, calls actual Runtime::step once, then retains its
before/after context and return value. Terminal observer states perform no more
diagnostic clock checks or stores; Runtime continues once per loop. Ordinary
MATCH and default preprocessing omit the object, clock and observation branch.

The cohort is interval starts in the first-entry half-open 300000000-us window.
The entire final straddler, its original start/end and overshoot survive closure.
One separate drain interval exposes final population-publication work. Its
timestamp/store/freeze/compiler-escape tail remains outside the population.
Final SEALED and failure states are immutable; a missing next entry remains
explicitly incomplete. A failed drain retains population_closed separately.

All-poll and completed-labelled distributions use unchanged D229 machinery.
Completed-labelled p99 is not reconstructed per-epoch CPU cost: delayed observer
work can occur in the next idle interval. Clock chronology, overflow, saturation,
first failure, uncertain classification and context are retained. The first
cohort includes warmup; initialization_complete and configured grants cannot
prove continuous all-sensor liveness. These are conservative wall envelopes,
including installed framework/interruption gaps, not isolated CPU durations.

## Focused execution

Reproduction from repository root in existing Linux/WSL:

```text
python3 -B -m tests.tooling.test_outer_loop_timing --raw <fresh-owned-directory>
```

Final `P7_outer_loop_timing_raw/host03/result.json` is PASS_HOST_ONLY with SHA-256
`6961c79ba2a526f6b7bbbeb0aa08b805cf7a72821d73835b11efb5314c59b1e9`.
All 15 serial compiler/process commands returned zero; every final stderr is
empty. Exact input pins before/after agree. Total elapsed time was 40.229 s;
the one real-Runtime UBSan compilation took 34.531 s and execution 0.032 s.

The strict C++17/O1/no-exceptions/no-RTTI/UBSan executable passed **16 cases,
143 assertions**, no failure or skip. Twelve observer-specific cases plus one
new combined allocation case and three reused allocation-probe cases cover:
half-open membership, exact endpoint, whole straddler, final-start retention,
one drain, immutable seal/error, unfinished interval/drain, natural wrap,
quantized zero, equality-limit stall, reverse/half-range error, missing context,
failed-drain closure truth, idle dilution, overflow, saturation, failure/completion
overlap, saturated epochs and six impossible phase/fault/result contexts.

The actual public Runtime fixture executes success, early/idle, ordinary source
failure and stable terminal paths. The combined observer/Runtime allocation
probe includes construction, repeated actual steps, close, drain and summary;
malloc/calloc/realloc/free/new/delete instrumentation observes no heap operation.

**Unexecuted planned seam:** no real defensive post-completion stop-bookkeeping
fault was forced. That branch protects an invariant after actual completion;
forcing it would require private-state corruption, a production test hook or a
wider configured-button fixture. Root and reviewer accepted source-order review
plus a synthetic captured-context overlap case for this classifier. The test
does not claim that the actual defensive branch executed. Other Runtime paths
above execute the real implementation. No assertion or production guard was
weakened to close this limitation.

## Entry binding, retention and size

The unchanged current app.ino bytes are copied into typed native substitutes.
Three Os/LTO/function-section/data-section/GC builds execute setup and loop:
default MATCH0/M0, ordinary MATCH1/M0, and timing/P4 MATCH0/M0. They verify one
Runtime call per loop, no diagnostic clocks in ordinary profiles, four diagnostic
clock reads through sealing in the timing fixture, no later clock/data mutation,
both histograms and the separate drain. The MATCH host fixture is M0; it is not
a production M1 deployment or target-execution claim.

Both ordinary binaries have no outer_loop_timing symbol. The timing binary
retains the 0x1a20-byte named owner. A separate Os/LTO/GC executable whose main
never reads the diagnostics also retains that symbol; saved nm/disassembly show
both histogram update calls and storage. The application uses a narrowly scoped
used object and pointer/memory compiler escape. Target optimization/layout still
requires the later exact-image ELF check; host retention is not target proof.

Host sizes: Observer/Data **6688 bytes**, Summary **96 bytes**, unchanged Runtime
**169888 bytes**. New production edits are the observer header, conditional
app.ino binding and OUTER_LOOP_WINDOW_US diagnostic constant only. Existing
APP_CLOCK_STALL_MAX_POLLS is reused for consecutive equal entry stamps. No control
deadline, source grant, HAL, scheduler, recorder, D229 code or locked test changed.
Function lengths and current file pins are recorded in source_checks.json; all
owned functions are below 60 lines. `git diff --check` passes for source/tests.

## Preserved failures and cleanup

- host01: real Runtime/observer suite passed 15 cases/110 assertions; the timing
  entry substitute failed compilation because its fake runtime.h omitted the
  real header's epoch_timing dependency. Fixed that fixture include. Original
  receipts and tested header/CPP/runner bytes are retained, not relabeled PASS.
- Review finding 1: final interval start was overwritten by drain start. Added
  last_population_entry_us and exact assertions before and after sealed drain.
  host02 passed 15/113 and all entry/retention checks, but is superseded below.
- Review finding 2: epoch arithmetic alone did not flag impossible phase/result
  transitions. Added explicit context coherence and six refusal/uncertainty
  cases. host02 tested header/CPP are retained; host03 binds the final source.

Each host run removed only its own completed /dev/shm temporary build directory
after saving command output and input pins. The final removed scratch contained
1713350 bytes. Raw retained evidence totals approximately 277 KB before this
validation/closure; no target artifact, source, original failure or user file was
deleted. No board, ADB, upload, reset, native timing or cleanup operation ran.

Next: independent source/host review, then root-controlled current timing-M0
compile-only and any justified ordinary production compile. Verify the named
target object and layout before future passive readout. No new capture/deploy
framework belongs to D243, and no P2.2 physical acceptance follows these checks.
