# D134 working checkpoint

USER-REQUESTED PAUSE,2026-09-24 13:09 Asia/Dubai. Active software phase P5 under D134; real P4/P5
acceptance remains pending. Contract/public interfaces committed27bc075a after
proposal/design reviewcf35d0a8. Prior P4 completion39791703 and byte-preservation
correction2483038a remain intact. Append state ledgers without re-encoding old bytes.

Implementation is present and frozen: core/types.h, countdown.cpp, openers.cpp,
fsm_robot.cpp and tools/board_tool.py. Shipped availability defaults1/1 preserve
all six modes; existing B16 values/push0 are unchanged. Public16 normal+4 new
locked cases and26 Python methods were frozen before their respective source
changes. Separate reviewer6 C++ and8 Python probes were frozen before body reads.
Public/header derivation is documented in P5_mode_availability_test_plan.md.

Static core and tooling review passes; execution has not yet established P5
acceptance. `core_freeze.json` binds523 C++ inputs; combined `freeze.json` binds649.
First full build failed on a new fixture reset expression; an independently
approved typed default operand compiled successfully. Focused binaries each
passed19/20cases, failing only the new draft's universal-edge-brake expectation.
The corrected case now passes all20 public cases perM0/M1. See
P5_mode_availability_first_failure.md. Tooling60, broader296 and private Python8
passed. First private C++M0 failed one improperly established snapshot stimulus;
the independently corrected setup retains all original assertions and its failed
source/receipt. Corrected private execution remains pending.

The full default build then exposed a preexisting CMake timing-test/profile
association error; no CTest ran on that failed attempt. The independently
reviewed CMake-only fix now passes `default11_full_retry2`:all18 CTest targets
and6 private cases perM0/M1, overall exit0. Session69267 is TERMINAL, and its
owned scratch was released. All earlier jobs are also terminal. No build or
hardware process remains active. No evidence file may be overwritten.

On user resume, first verify the pause commit, current source hashes, disk/RAM
and actual Dubai time. No need to repeat the passed normal/full/tooling/layout
runs unless source changes justify it. The exact first unfinished task is the
D134 sanitizer matrix, serially through the existing frozen runner:

```text
python3 state/analysis/P5_mode_availability_raw/run_host.py default11_sanitizer 1 1 1 sanitize,review
python3 state/analysis/P5_mode_availability_raw/run_host.py pair00_sanitizer 0 0 1 sanitize,review
python3 state/analysis/P5_mode_availability_raw/run_host.py pair01_default6_sanitizer 0 1 6 sanitize,review
python3 state/analysis/P5_mode_availability_raw/run_host.py pair10_default4_sanitizer 1 0 4 sanitize,review
python3 state/analysis/P5_mode_availability_raw/run_positive_profile.py positive20_profile_sanitizer
```

Run through WSL Ubuntu with TMPDIR=/dev/shm and PYTHONDONTWRITEBYTECODE=1;
one compiler, one runner at a time. These labels are prepared, NOT executed.
Run the new scoped copied20/configured sanitizer recipe for the CMake repair:
full push family under timing1 plus five D131 timing-family cases; complete old
D129 assertions remain tested at duration0. Do not repeat passed60admission,
296tooling or8private Python checks without a relevant change.
Recheck layouts, original41 protected sources and assertion bodies; finalize
review/packet/ledgers and commit after real passing evidence.

Source/map tasks are not hardware proof. Native fit, loaded RAM/stack, full800us
tick and actual P5 trials remain pending. P7 mapping, if present, is read-only
preparation; no phase advance, release tag or P6 eligibility is inferred.

D135 design4dc72ac1/adoption2aa0ac2e is saved, implementation not started.
Four public draft files are saved only in analysis/P5_abort_timing_drafts/;
they are incomplete/unreviewed/uncompiled, not established locked tests. The
author was interrupted on user pause. Fresh-context reviewer p5_abort_reviewer
was also interrupted before writing private artifacts; no private expectation
freeze or execution exists yet. Resume those bounded tasks only after the user
resumes. Do not move drafts into tests/ or alter production during D134's
remaining frozen matrix. All agents were told to pause; no background promise.
