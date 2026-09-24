# D134 P5 mode availability independent scoped review

Status: PENDING complete execution; production source review has no material findings.
Independent private expectations
are frozen in P5_mode_availability_review_raw before new implementation/public
test reads. Separate-context same-model reviewer, with prior P4/design context;
not cross-model review or a phase gate.

Review will cover bounded menu cycles, direct opener rejection, Robot final
inhibition, raw-source admission before legacy fallback, preserved historical
IDs, four configurations, default layouts and unchanged motor authority.
Target fit, loaded RAM/full-tick WCET and physical P5 trials remain separate.

Closed MAJOR (new test oracle): original
`tests/locked/test_mode_availability_safety.cc:41`
requires zero duties for every white mask, contradicting B4's rear/side moving
rows. Focused first execution had19/20 cases pass in each M0/M1 build; only this
new draft case failed. Narrow row-specific repair is justified as documented in
source_review.md, with original failure retained. Corrected focused public
rerun passed20/20 cases in both M0/M1.
Corrected SHA901b735c was independently inspected before execution: first-
observation checks, literal row duties, fault inhibition, settled demands and
actual M0/M1 PWM/receipts now match the specification. All41 prior protected
source hashes match original425c8a97. See draft_correction_review.json.

Private-harness correction applied, pending rerun: first M0 private execution passed5/6 cases;
the stale-snapshot case supplied no observation in B3's final300ms window,
therefore no saved front existed to trigger the expected DIRECT exit. Production
OPENER/.85 is correct for those actual stimuli. Preserve original failure and
expectations; corrected SHAe15baf36 adds real snapshot/current-mask preconditions.
Byte-exact original probe/manifest and comparison receipt are retained.
M1 private execution and the complete matrix remain pending.

First-run independent Python result: PASS, 8 methods, no failures/errors/skips,
0.074 seconds. `P5_mode_availability_review_raw/python_first.json` binds the
frozen probes, adopted contract and actual tool SHA500ce3c5, and confirms all
bindings unchanged. External processes and network sockets were forbidden;
the probe still exercised real local staging and copied-config corruption.
No C++ review execution or target check is claimed by this result.

Source findings and runner audit are in `P5_mode_availability_review_raw/source_review.md`.
The deferred `run_layout.py` compares fixed cf35d0a8 baseline host sizeof/alignof
with all four final configurations under M0/M1 using owned RAM scratch. It is
prepared but not yet executed; object-member inspection separately found no
added fields. Host sizes do not establish target fit or available target RAM.

Forward-use limitation: unchanged historical all-six tests assume the optional
features are enabled. The existing `tools/test_host.sh` is not a reduced-mode
release runner; on a future source configuration with flags00, some historical
feature-presence expectations will fail. D134 requires full legacy regression
on the shipped11 source plus the additive real-owner/safety matrix on copied
reduced configurations. Those are separate claims. They must not be reported
as a full historical-suite pass on a reduced source configuration.

A future reduced-mode release can use the same explicit two-configuration
validation contract: bind the actual source/configuration, test its applicable
additive owner/safety/sanitizer cases, and run all unchanged legacy assertions
against a temporary source-identical all-six canonical-default variant. Retain
the exact availability/default substitutions and distinguish that variant from
the actual deployment configuration. Do not skip assertions or edit locked
tests. Native compilation, hardware qualification and source approval remain
separate prerequisites. An automated public runner may make this recipe easier,
but is not required to claim the narrower currently adopted D134 checks.
