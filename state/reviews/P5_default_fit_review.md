# Default-app candidate 2: source review complete; fit failed

2026-09-24. Separate same-model reviewer; no compiler, tests, board or source edits.
Scope: four-file candidate against `2d924f1f`, D131/D134 and approved regressions.
Full patch SHA256 `4d196e2c901b56bca4c9d71812d24e522278b990041d00401803887d7aee67b2`.
Source findings: no material behavioral difference found; source-equivalence PASS.

- `candidate2/src/core/edge.h:235`: zero-window active authority is the new bool;
  positive-window authority remains Episode. Default initialization/reset is false.
  All shared active reads/writes use the helper; zero never accesses push-start data.
- `candidate2/src/core/edge.cpp:307,393,422`: positive union initialization, fault,
  DEFERRED/SPENT transitions, expiry, permission loss, replan budget and exit rearm
  remain unchanged. Positive code never uses the new bool to authorize behavior.
- `candidate2/src/core/fsm_robot.cpp:416`: explicit final false equals the existing
  EscapeSample default; positive eligibility/freshness/raw-FC/revoke checks are exact.
- `candidate2/src/core/openers.cpp:65`: P5 terminal evidence sequence is unchanged;
  non-P5 restores direct return of the same plain Result after identical mutations.
- `candidate2/src/core/fsm_robot.cpp:553`: switch matches canonical modeAvailable
  for all 256 underlying IDs and four flag pairs. Rejection calls no script;
  cancellation, SCRIPT_START, active state and downstream inhibition are unchanged.

Retained candidate-2 native ABI reports 10 identical type layouts and 44 old
offsets; the bool occupies offset 205 in Escape 208. This is default-target evidence,
not a portable padding guarantee or positive-window/P4/P5 behavioral proof.
Native model fit FAILED: candidate 1 deficit 24 bytes; candidate 2 deficit 32.
The separately observed D134 default-app deficit is 32 bytes. Unmodified D135
default app has not been compiled here; neither candidate measures that artifact.
No candidate host regressions ran. Root stopped the failed-fit experiment: no
adoption or further optimization is authorized. Target fit remains OPEN.
Exact bindings and unexecuted regression scope: `P5_default_fit_review_raw/source_review.json`.
