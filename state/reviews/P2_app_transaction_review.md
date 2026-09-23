# D095 application transaction independent review

2026-09-23, Asia/Dubai. Fresh-context separate same-model reviewer; review only.
Baseline `1b5bc3a`, public contract `c17f6d6`, plus current implementation/test
worktree. AGENTS.md was read in full; Wednesday 23 September remains within the
original PLAN schedule. Active work is P2 software under D051/D075, without any
human gate or physical acceptance. The reviewer changed only this review and its
`P2_app_transaction_review_raw/` evidence directory, with no hardware, transport,
shared CMake build, implementation edit or commit.

## Findings

No open BLOCKER, MAJOR or MINOR in this scoped implementation.

The initial target receipt omitted actual `main` disassembly from its selection
filter. The implementer supplied a separate additive receipt after the reviewer
requested it; the original receipt remains unchanged. This evidence gap is closed.

## Verdict

PASS for the D095 software transaction, terminal MotorGate inhibition, source
staging and inert compile probe. This is not approval of a future native source
scheduler, app integration, hardware behavior, a motor run or a phase gate.

## Source and contract review

- `src/app/transaction.cpp:9`: initialize calls Gate.begin first and only once;
  setup failure retains terminal SETUP without an extra inhibit. Construction,
  passive inspectors and repeat terminal calls have no backend/clock work.
- `src/app/transaction.cpp:24`: actual clock observations preserve half-range
  chronology, equality and natural wrap. A duplicate decision clock is rejected
  before invoking Robot or apply. Caller timing/previous receipts are overwritten
  while real sensor source metadata remains unchanged.
- `src/app/transaction.cpp:56`: exactly one actual Robot decision, one checked
  Gate application and one recorder consumption per admitted decision. Robot's
  normal governor, countdown, edge and sensor-validation paths remain authoritative.
  Ordinary Gate rejection remains invalid evidence for the next real Robot tick;
  it is never promoted to an acknowledged motor output.
- `src/app/transaction.cpp:87`: C is read after admitted caller work and validates
  A even on a failed application. The one S anchor enforces D <= A <= C inside
  half-range. Saved previous includes true execution and completion without
  replacing Gate token, actual application time or validity. B14 duration-only
  overrun remains Robot count/log behavior.
- `src/app/transaction.cpp:34`: first terminal ownership fault halts once,
  invalidates saved ordinary receipt validity, preserves actual diagnostic fields
  and invokes recorder interruption without resetting Robot or erasing storage.
  Later calls cannot manufacture completion or repeat hardware work.
- `src/hal/motors.cpp:200`: halt is not a token/result. It disarms before the
  existing LOW/all-writable-zero/settle pass, preserves prior causes except the
  existing IO upgrade, and keeps its first report. Missing/bad clock cannot
  suppress inhibition. Never-begun halt is callback-free; successful existing
  reset clears the cache and failed reset retains it. Non-halt paths keep their
  previous ordering and semantics.
- `src/hal/recorder.cpp` and `src/core/fsm_robot.cpp` were independently traced:
  the stopped tick's deferred frame and complete timing require a genuine later
  decision. Active/draining interruption preserves bytes and marks interruption;
  an already sealed attempt keeps the existing recorder semantics.
- `tools/board_tool.py:104`: support `.h/.hpp/.c/.cc/.cpp` files go beneath
  staged `src/app`, `app.ino` remains a root sketch, and sketch-local `src/app`
  shadowing is refused. Existing source checks and exception propagation remain.
  The probe is absent from the seven-key upload allowlist.

`git diff 1b5bc3a --name-only -- tests src/core src/config.h` returned no tracked
changes: established tests, core and tunables are unchanged. Newly added halt
tests are new files. The initial NEW test clock-priority expectation was corrected
to CLOCK for invalid S..C, and the clean STOP-tail test now supplies real 1 kHz
cadence instead of skipping frames. Both align with D095/B15, preserve assertions,
and require no production change. Root/author retain their original failures.

## Independent executable evidence

`P2_app_transaction_review_raw/reviewer_cases.cpp` is a separately authored,
standalone callback and assertion harness, not the new author's fixture/tests.
`run_independent.py` compiled the actual current core, Gate, recorder and transaction
in an isolated `/dev/shm` directory using `-Wall -Wextra -Wpedantic -Werror`,
`-fno-exceptions -fno-rtti`, ASan and UBSan.

Both `MOTORS_ALLOWED=0` and `MOTORS_ALLOWED=1` passed **47,703 checks each**:
1,458 S/D/A/C combinations per setting, natural wrap, equal and half-range times,
every inhibit failure position, passive repeated terminal methods, failed reset
cache preservation, forged caller receipt/time rejection, dense actual GO/STOP/
tail lifecycle and saved receipt invalidation. Exact commands, stdout, exit status
and source hashes are in `independent_results.json`. This is synthetic host
execution, not physical timing or pin behavior.

One reviewer source-audit harness initially used string sorting for an aggregate
hash, while production stage hashing uses Windows Path ordering. All 80 individual
files already matched; only README.md versus the sketch name ordering differed.
The first failure and correction are retained in
`check_target_receipt_first_failure.json`; no source or expected digest changed.

## Target and inert source evidence

Reviewer independently compared all 80 source-file bytes in the captured target
receipt to current files and reconstructed source identity
`9d6c0005a3708df1df8f8d9dc885d1fbcd595aad97b90ad3826b20484116580a`.
All three captured ELFs retain the real owner/Gate/Robot/recorder methods and
strong `__loopHook()`. Their 188 imports match D094; no new imports. All 40 native
and 42 AEABI export values are nonzero. Loader SHA256 is unchanged:
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
See `target_review_checks.json` and the root's exact captured target receipt.

The 13 `.init_array` relocations were reviewed with disassembly. The added native
port/global transaction initializer copies callbacks, computes candidate periods
from constant metadata and initializes fixed storage; it invokes no begin/read/
apply/halt method or sensor/motor callback. Setup stores the retained exercise
pointer; loop and the strong loop hook return immediately. Additive disassembly
at `state/analysis/P2_app_transaction_raw/target_startup_additive.json` resolves
actual main to inherited initVariant/start_static_threads/setup/loop/loopHook.
Existing Bridge/serial/static-thread infrastructure remains inherited and is not
qualified for runtime by this compile-only inspection.

`inert_source_reconstruction.json` independently reconstructs exact bytes and
per-file hashes for the seven EXISTING inert keys, including both shared app
support files. The common delta adds no static owner/backend call to those seven
sketches. Only those same seven hashes are approved for manifest refresh. Root
independently confirmed their actual Windows stages match this reconstruction.
No new key, upload or changed startup policy is approved by this review.

The compiler reports 149120 program bytes and 238628 globals, with 23516 nominal
remaining bytes and a low-RAM warning. This is neither loaded free RAM nor a
worst-case stack/heap measurement. Native acquisition/resource scheduling, source
cancellation placement, physical clocks, sensor/motor acceptance, loaded memory,
complete-tick <800 us and all human gates remain pending. Next work is the bounded
source/resource scheduler contract using this owner; no current result proves it.
