# D229 completed-epoch distribution host validation

27 September 2026, isolated branch `codex/timing-p99-20260927`, base
`004dc7cff534896a851901f9d7d0ba6066cae060`. Result: **PASS_HOST_ONLY**, pending
independent review. No main-worktree change, target compile, upload, native run,
motor action, physical qualification or phase pass was performed.

## Result and evidence

The new header provides an exact integral nearest-rank p99 for the retained S..C
population below 800 us. Runtime records one duration only after successful
transaction completion and clock admission. Private fixed storage, a const raw
view and a readable summary expose explicit empty, overflow, saturation and
inconsistent-histogram states. Actual maximum and last-completed anchor keep
advancing even when the retained prefix saturates. No reset or transport exists.

The corrected focused run passed **16 cases / 316 assertions**: 13 new cases and
three unchanged existing Runtime heap-operation probes. Ubuntu g++ 13.3.0 used
C++17, O1, warnings-as-errors, no exceptions/RTTI, undefined-behavior sanitization
with no recovery, and malloc/calloc/realloc/free wrappers. MATCH=0 and
MOTORS_ALLOWED=0; the checked production configuration was used without fixture
calibration changes. The serial test compile took 56.10 s, execution 0.03 s.
This is a host execution result, not a target timing benchmark.

`P7_epoch_timing_raw/repaired_fixture03/result.json` records all command arguments,
exact stdout/stderr companions, baseline Git identity, complete production and
fixture input pins, and equal before/after pins. Its SHA-256 is
`77e5f0cff21ce113341b58c42c3d50d206c6a46cf04f9b7c72991866eb9ec12f`.
`06.stdout` contains the successful test summary; all compiler/sanitizer stderr
files in that run are empty. `git diff --check` also passed.

Meaningful cases include sorted-sample rank oracles at N=1,2,98,99,100,101,199,200,
201,2000; exact 799 versus overflow 800; a one-percent overflow tail; unclipped
worst case; zero duration; modular wrap anchors; UINT32_MAX bin/overflow/sample
and rejected-count limits; retained-prefix versus all-observed metadata; invalid
histogram sums; actual sensor acquisition; successful Runtime epochs; idle/stale
and aborted calls; real service/decision failures; and a failure at actual C after
the decision was made. Tests seed coherent near-limit images only through a
test-only const_cast of an originally nonconst object. Production has no such
mutation interface.

## Memory, measurement window and cost

Host ABI sizes: 800 uint32 bins = **3200 bytes**; Data/Distribution = **3236 bytes**;
Summary = **44 bytes**. The same compiler measured baseline Runtime at 166648
bytes and modified Runtime at 169888 bytes: **3240 additional bytes**, including
host layout padding. The new owner is appended, preserving existing members'
source order. Target ABI, RAM fit and addresses must be freshly established for
the new source/image before target capture; these host sizes do not grant them.

Per-observation work is constant: comparisons and fixed scalar/counter stores,
without loops, allocation, I/O or additional clock reads. Summary scans at most
800 bins and is not called by Runtime::step. Neither execution-time overhead on
the STM32 nor generated target instructions have been measured. The observer
and remaining completion bookkeeping run after C and therefore are excluded
from the recorded durations. Work before S, idle/failed polls and the outer loop
are excluded too. This does not claim full-poll WCET or close original P2.2.

Capture population is the object's lifetime completed-epoch prefix, from its
first admitted completion. No automatic five-minute window, liveness inference,
rolling estimator or reset is supplied. Raw start/end anchors alone cannot prove
elapsed time across multiple wraps. Five-minute all-sensor-live provenance and
a later complete-loop measurement including observer overhead remain required.
Concurrent memory reads still require coherent acquisition; a matching histogram
sum is not proof of capture coherence.

## Original failures retained

1. `first_host01`: Linux Git could not interpret this Windows worktree's embedded
   C:/ metadata path; the run stopped before compilation. The runner now accepts
   an explicit translated `--git-dir`. Production and C++ tests were unchanged.
2. `corrected_host02`: compilation succeeded; 15/16 cases and 311/316 assertions
   passed. One new test tried to induce a second QTR acquisition failure before
   the unchanged fixture's 2000-us next-frame interval. The real Runtime correctly
   completed that epoch. The retained original test is
   `corrected_host02/test_runtime_epoch_timing.original.cpp` (SHA-256
   `752674efc0e1316ea536a96e1a7134cd20629becf3c00ac3674172b6343ab184`).
   The corrected test schedules a genuinely due frame and requires the intended
   failure before testing unchanged distribution metadata. No production repair
   or weakened expected behavior was needed.

## Frozen production and tests

| Path | Bytes | SHA-256 |
|---|---:|---|
| src/app/epoch_timing.h | 4007 | 46960d854f19f863e737422937616223d3c961be35b20502c1d05b92b1be7c05 |
| src/app/runtime.h | 9975 | ced423d850d116cdecd13e9e12e68e901a04b293d257148a667acdb14bb882c3 |
| src/app/runtime.cpp | 14087 | 84ad84f3e1e4c5e4647b074465c69ffb072276fd89b9452cbddbb665cc6fc3af |
| src/config.h | 23036 | d3186cf374fe176c3998e8a41b840f1b86f6f66d33c587c8a121ffa113bd502d |
| tests/test_epoch_timing.cpp | 6132 | e04f18e8668f551d1b07f301d639dc3875a45e6a6c42a00ec61b9e708389d9b2 |
| tests/test_runtime_epoch_timing.cpp | 5810 | 789ea48285cf4ad1e6d662ca36bbbe29e99d204f6f5810ed6a94b937fb50bd86 |
| tests/tooling/test_epoch_timing.py | 6191 | fe5f3323a59bfe8ec61ccd59df0e87d55704c8397913aa7ba9b480cb07f99a63 |
| state/analysis/P7_epoch_timing_contract.md | 4914 | 42a98d99b1037366baf385b059e93ab7be9342cf8417fe0d362e7944c9cf49d7 |

Reproduction from WSL, with a fresh output directory:

```sh
python3 tests/tooling/test_epoch_timing.py \
  --git-dir /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/.git/worktrees/sumox-timing-p99-20260927 \
  --raw state/analysis/P7_epoch_timing_raw/reproduction_new
```

Omit --git-dir in a normal Linux checkout. The baseline size probe always uses
the exact base commit named above; it does not silently substitute a later HEAD.
Scratch binaries, temporary baseline headers and generated probes were removed
after recording every outcome; source, original failures and compact evidence
remain. See the isolated STORAGE_LOG append. Next action: independent review,
then coordinator-controlled integration and fresh source-bound target evidence.
