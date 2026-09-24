# Supplemental positive-profile runner static review

Reviewed `run_positive_profile.py` SHA256
`18d5269350217137d50e19f3693a2fbf62f1ff25ab36f6f5ee72e9d39838078f`.
Static PASS: no material issue found. No runner/compiler execution by reviewer.

- Frozen build inputs are verified before copying and after execution; copied
  bytes are checked before the exact20ms/configured-button substitutions.
  Full copied-tree aggregates, configuration hash, manifest hash and runner hash
  bind the retained receipt. The39 copied files outside the freeze are existing
  noncompiled documentation, Python fixture/data and .gitkeep files; no current
  C++/header/CMake build input was found outside the freeze.
- Receipt/log use exclusive creation after no-overwrite checks. Commands and
  output hashes remain recorded on nonzero exits. TemporaryDirectory owns the
  unique scratch; source aggregates are captured before cleanup, and the final
  receipt reports whether that actual scratch path is gone. Source/manifest
  changes or cleanup exceptions cannot yield a false successful exit.
- Four M0/M1 push/timing targets build serially with positive20, configured
  buttons, timing1 and ASan/UBSan/noPIE. Push executes without filters. Timing
  first lists exactly five D131 cases, then executes that exact name filter.
  This does not claim the legacy D129 tests pass under positive20; those belong
  to the separate complete duration0 run.
- Summary regex matches the pinned doctest reporter and color is disabled.
  Exactly one summary is required; selected must be positive, passed==selected,
  failed==0. Push additionally requires skipped==0; timing requires selected5
  and separately verifies the unskipped listing. Listing alone cannot pass the
  execution check. Process failures retain their exit code; parser/identity
  failures return1 with traceback. There is no implicit retry or empty-set pass.
- Optional future guard: require the currently fixed push count37 explicitly.
  The present frozen CMake/source/flags contain all37, and no filter or skip is
  applied, so this is an additional guard rather than a current coverage defect.

Actual success still requires the complete current-source receipt and expected
37+5 executed cases per M0/M1, alongside the independent full duration0 suite.
