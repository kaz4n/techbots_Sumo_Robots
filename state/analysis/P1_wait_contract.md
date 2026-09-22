# WAIT public contract — 2026-09-22 Asia/Dubai

D-055 adopts the saved spec-only recommendation P1_wait_contract_audit.md under
D-051. The literal no-pivot segment could drive at the charger and its widening
front cue could terminate it immediately. Complete existing SIDESTEP_R is the
explicit selected policy, not a claim of physically successful evasion.

Public API: src/core/openers.h Wait::start/step/reset, WaitPhase/WaitResult.
Its comments specify ordered FC/flank evidence, inclusive300ms window, continuous
FC with clear-only rearm, side/rear/cue/deadline priority, fixed-right delegation,
stationary braking, terminal/pulse semantics and consumed healthy-yaw validation.
The existing Flank supplies approved motion, aborts, profiles and fallback; all
exits still use D-034 current perception and fresh centered qualification/contact.

Related threshold repair: Flank's captured relative turns must use the existing
Turn::startRelative rather than float-normalized heading+angle. As in the row
regression, SIDESTEP_R from -1e-6F observed at45F is strictly within5 degrees of
its50-degree relative turn. Preserve every established test and add an independent
new boundary regression; this repairs B7 representation without changing gains.

Root owns openers.h/.cpp and shared state. Independent test author will own new
tests/test_wait.cpp, reads this contract/spec/header only. Review follows frozen
source and tests, with normal/sanitizer/full tooling evidence and no motor action.
