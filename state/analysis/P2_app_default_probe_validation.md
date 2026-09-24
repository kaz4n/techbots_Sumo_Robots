# D118 exact default-app observation tooling

IMPLEMENTED / HOST-TESTED / separate software reviews PASS, 2026-09-24.
Actual upload and observation are still pending at this software checkpoint.

The new collector `tools/app_default_capture.py` is frozen at
`beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1`.
Its independent public-contract oracle is
`0acddcc62b369f4ec725521b996a13622d6dcaf06fc1d89c592350d4aa0b4e15`.
The first author run and separate reviewer run each passed40 new methods plus28
unchanged heap tests. No executable failure, test amendment or implementation
repair occurred. Static pre-execution source snapshots remain in raw/implementer.
The public lifecycle clarification preceded oracle freeze; adopted06377731 and
currentfbf34f25 contract versions remain preserved.

The new standalone upload guard `tools/app_default_run.py` is frozen at
`7fbeceb269912321b3b06c2b9ea9cace466c2faf4f06bebf6ec1d4ebf4d5da58`.
Root authored its public-contract oracle before the separate implementation;
this is disclosed coordinator authorship, not a fresh-context test author.
Separate static review strengthened two coverage points before execution:
attempt-specific fsync and exclusive-create collision. Original20 methods and
the final22-method oracle6a4dcde6 are retained; no expected behavior was weakened.
First22, independent22 and six new reviewer probes all pass unchanged production.
The guard reviewer used a fresh context of the same model, not cross-model review.

The unchanged ADC guard/build-policy/override regression suite passed97 methods.
The first root invocation omitted tests/tooling from Python's import path,
causing19 setup ModuleNotFoundError results. Exact original output is retained;
correcting only the launch environment yielded97/97. No existing test or helper
was changed. Full firmware host tests were not repeated for these additive Python
tools; D117's preceding full normal/sanitizer evidence remains separately valid.

Commands, frozen input/source hashes, actual statuses and complete outputs:

- `P2_app_default_probe_raw/author/`: independent capture68, first freeze and recipes.
- `P2_app_default_probe_raw/reviewer/`: capture private68 and final source review receipt.
- `P2_app_default_probe_raw/guard_author/`: original/strengthened oracle, first22, private22.
- `P2_app_default_probe_raw/guard_reviewer/`: six fresh-context private probes.
- `P2_app_default_probe_raw/root_regressions/`: first failed launch and corrected97.
- `P2_app_default_probe_raw/root_source_check.json`: exact new/shared source hashes.
- `state/reviews/P2_app_default_capture_review.md` and
  `state/reviews/P2_app_default_guard_review.md`: actual scoped source reviews.

The exact pair of176048-byte app files was exclusively copied from checked
buildd92f929c into the contract's passive input directory. Four reviewed collector/
helper/config files were separately copied into an exclusive Linux tool directory
and rehashed. `preflight/capture_input_staging.json` and
`preflight/capture_tool_deployment.json` retain actual commands and exit0 results.
These were Linux regular-file operations only. No collector execution, MCU read,
new upload/reset or peripheral operation occurred at this checkpoint.

Firmware/sourcee820c0e1, config/grants, shared board tools, all old/locked tests and
the exact nine-key manifest remain unchanged. Generic app upload is still refused.
The standalone route admits only the exact default/M0 build, current local commit,
review records and file map; its once-only claim consumes failed/unknown uploads.
Preparation retains inherited lack of a uniform deadline; upload is120s, capture
is600s with30s maximum child commands. No retry or recovery path was added.

Before an actual run, commit this software, bind the exact live review/approval/run
records to that current commit and complete the separate run review. The planned
test includes real EN LOW/zero-PWM/timer setup on the human-reported bare board.
It grants no optional sources/UART, nonzero output, motor permission or human gate.
The eight-byte loader margin is still a model; live sampled heap/progress/fault
evidence cannot prove transient loading margin, stack space, full WCET, pin
voltages or assembled-robot P2 acceptance.
