# P0 execution checklist

PROGRESS.md is the phase/gate authority. No gates passed; no motor-run authorization.

| Existing task | Status / dependency | Acceptance / evidence / next action |
|---|---|---|
| Kickoff migration | IMPLEMENTED | D-015, AGENTS addition, CODEX_HANDOFF, baseline 52b935e |
| P0 0.1 G1-G6 | IN PROGRESS | Primary sources in analysis/P0_G*.md; coordinator merges FACTS |
| P0 0.2 scripts | IN PROGRESS | Staged sketch, controlled substitute tests; board result separate |
| P0 0.2 round trip/startup | HARDWARE-PENDING | SSH target, safe bare board, installed versions, matrix + counter, both startup times |
| P0 0.3 scaffold | IN PROGRESS | CMake/doctest/config defaults; tools/test_host.sh must pass |
| P0 0.4 micro-benchmarks | HARDWARE-PENDING | 60 s jitter/max/p99; GPIO/QTR timeout/ADC; model-dependent I2C |
| P0 0.5 pin map | BLOCKED | source inventory, physical checks, approved changes, PINMAP OK |
| P0 review/gate | GATE-PENDING | fresh-context reviewer, real exit evidence, human GATE P0 PASS |

Protected conflicts: analysis/spec_conflicts.md. No recommendation is approved.
Next: finish safe P0 implementation, validate host and scripts, review diffs; await
requested connection/setup/model/rulebook/layout facts for hardware work.
