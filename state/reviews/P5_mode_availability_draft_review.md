# P5 optional-mode availability draft review

2026-09-24. Design-only review of
`state/analysis/P5_mode_availability_contract_draft.md`; no implementation,
execution, adoption, phase advance or physical acceptance is implied.

No material design gap identified. The two 0/1 switches retain all six default
modes, mandatory IDs 1..3 guarantee bounded menu progress, and disabled public
Flank/Wait starts plus the Robot dispatch guard fail without substituting a
strategy. Historical mode identity stays distinct from current availability.
Both-absent raw configs support exact old sources while new core requires both
symbols. D034's same-tick perception routing and centered qualification remain.

Minimal registry integration: add only literal `MODE_ARC_ENABLED: 1` and
`MODE_WAIT_ENABLED: 1` entries to the existing
`tests/tooling/test_p0_config.py` `BEHAVIOR_EXTRA_DEFAULTS` dictionary, with the
adopted-decision comment. Its existing declared-key/type/value assertions cover
the additions. Preserve the 76-entry B16 assertion, `D096_DEFAULTS`, every
existing assertion body and the current registry wrapper chain; no new wrapper
layer is needed. Add independent copied-config checks proving each new shipped
default's drift is rejected, including legal availability 0 and invalid 2.

Small clarification before adoption: malformed-text, source-splice and digraph
checks should precede the validator's both-absent legacy return. This makes the
direct helper's lexical failure contract as explicit as actual stage admission.
The draft already requires these rejections; this only fixes their ordering.

Verdict: PASS_SCOPED_DRAFT_REVIEW. P4's separate final software review and all
target, physical, run-permission and human phase-gate requirements remain intact.
