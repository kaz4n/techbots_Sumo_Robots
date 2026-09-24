# D129 P4 timing evidence scoped review

Status: PASS for the scoped D129 source, host behavior and checked compile-only
policy review. One reproduced MAJOR trace-lifecycle finding is fixed; no open
BLOCKER or MAJOR remains in this scope. Native compilation, default target byte
identity and MCU fit remain pending because no board is connected. This verdict
does not supply physical timing evidence, WCET, hardware acceptance or a phase gate.

Reviewer is a separate same-model task from implementation and public-test
authors. The reviewer contributed prior options analysis and reviewed D128, so
this is not an independent contract-author review or a claim of entirely fresh
project context. Owns only this report and its adjacent `_raw` evidence folder.
No implementation/public-test/ledger edits and no hardware actions.

## MAJOR, fixed: intermediate invalid epoch can survive to a timing completion

`src/core/fsm_timing.cpp`, `validTimingSource` / `excludeTimingTrace`:
while observing a candidate, current tick/read offsets are checked only against
the supplied current tick start and candidate origin. A direct caller can
backdate that start before the preceding actual completion and repeat an old
read interval. `receiveTimingTrace` detects failed epoch chronology but retains
that fact only inside the approach predicate, which is unused after onset.
Later honest brake/receipt observations may therefore emit LOSS_ZERO_APPLIED
without the required INVALID_SOURCE_TIME closure. Existing owner
`timing_incomplete` remains latched, preventing loss-free physical acceptance;
the finding concerns the trace lifecycle rather than a claimed physical pass.

Recommended scope: retain current per-tick explicit S/D/A/C chronology and
duration validity separately from approach eligibility, require it while ARMED
or OBSERVING, and preserve existing RECEIPT invalidity reason11. Application
identity faults with otherwise valid chronology retain fault reason9.

Root authorized an exception to the general execution hold for this focused,
independently frozen reproducer before the fix. Original source compiled, then
failed four assertions in one case (36/40 passed): it omitted INVALID_SOURCE_TIME
and emitted the later decision and zero-completion records. The owner
timing_incomplete/unchanged ATTACK checks passed. See `original.json`,
`original_test.log` and `repro_freeze.json` in the adjacent raw directory.

The implementation now retains `timing_epoch_valid` independently of approach
eligibility and requires it in source validation. The exact unchanged reproducer
passed 40/40 assertions under normal and ASan/UBSan builds; `fixed.json` and
`fixed_sanitize.json` bind the actual source snapshots. Application identity
validity stays separate, preserving current reason precedence.

Eight additional independent private cases cover source/application timestamps
and wrap, receipt-before-current-safety ordering, transient/no retry, malformed
source without steering changes, lost prior ATTACK eligibility, missing tail and
duplicate behavior, common-anchor half range, actual Runtime source projection,
and capacity/rejection accounting. A pre-execution fixture correction moved a
pre-brake sample from 29999us to 29000us so two successive supplied 100us
acquisition epochs do not overlap. Initial private draft/freeze are preserved.

The first authorized full-private WSL invocation exited1 without output or any
configure/build/test receipt. Concurrent parent jobs also interrupted and WSL
was observed stopped. This establishes no semantic oracle result. No reviewer
runner issues shutdown/terminate/kill commands. The interruption is preserved in
`interrupted_first_private_run.md`; no original failure log was overwritten.

After the parent recovered storage and verified all existing evidence bytes,
the exact frozen private suite ran serially to PASS: eight cases each for M0
(472/472 assertions) and M1 (492/492), with no failures or skips. Actual real
Robot/Gate execution, configured Runtime source projection, natural wrap and
common-anchor rejection behaved as independently expected. `tests.log` and
`private_validation.json` preserve the commands, outcomes and source hashes;
the source remained unchanged throughout execution. The first interrupted
attempt is not counted as a semantic pass or failure.

The same runner compared seven host object sizes against D128 commit3985da16:
Robot, RobotResult, Transaction, Runtime, RobotInput, EventInput and EventBatch.
All six existing profiles (default, B4, drive, turn, stop and reactive) exactly
match their prior layouts. Default and uninstrumented reactive remain
2640/400/162616/166624/192/8/180 bytes respectively. The instrumented profile is
2712/440/162728/166744/200/8/220 bytes. These are host ABI observations only,
not MCU RAM, stack, binary identity or native fit measurements.

Independent Windows-only binding verification passed all641 original public
freeze entries before the tooling-oracle correction, preserved separately in
`bindings_before_oracle_correction.json`. Final binding passes640 original files
plus exactly the adjudicated new tooling-oracle replacement described below,
all39 prior locked raw hashes and Git-filtered identities against D128, all frozen
private files, the unchanged original reproducer, and the fixed normal/sanitized
and full-private source snapshots. `final_bindings.json` records the original
and accepted per-file results separately. Raw-file hashes and normalized Git
identities are checked separately so CRLF conversion is not presented as a
protected-test edit.

Target compilation/byte identity/native-fit checks are pending: root's fresh
resume inventory found no connected board. No D129 native compilation or live
memory/stack/WCET result is inferred from D128 artifacts.

The source-based conservative EventBatch bound is 22 legacy plus at most four
trace events. Legacy sources are one FIRST_NONZERO, one receipt FAULT9, two
START/GO, one EDGE, one PHANTOM, ten aggregated other FAULT codes, one STALL,
one STATE_CHANGE, one CONTACT and three REFLANK_PHASE entries. Header exclusivity,
one receipt terminal and at most read-pair plus one suffix terminal/decision are
required for the trace bound. Exhaustion bypasses normal finish and needs its
explicit adopted terminal handling.

The actual implementation satisfies those count invariants: `receive` runs once
before sampling; `receiveTimingTrace` emits at most one completion/rejection and
closes its phase. `publishEvents` emits one HEADER only for accepted START, when
`beginAttempt` has cleared trace state and `attempt_go_`. `publishTimingTrace`
returns on CLOSED/RECEIPT, and its source pair has only one following decision or
exclusion. `closeTimingTrace` emits once and latches CLOSED. Exhaustion invokes
receive first, then closes only ARMED/OBSERVING/RECEIPT, so it cannot append a
second terminal after success. The conservative 22+4=26 does not require the
legacy events to be mutually exclusive. Append/recording loss remains explicit.

Static integration checks: Runtime copies opponent timestamps only after its
complete-channel/status/current-epoch validator succeeds. No added HAL reads or
clock calls occur. `FusionObservation::confirmed_mask` is before stuck and
phantom filtering, so the final loss-brake check does not substitute filter loss.
The hook consumes actual `NormalResult.brake` and observes final committed
contact, permission and governed zeros. It adds no motion or governor mutation.
Conditional source/trace fields and enum/codec capacity leave option0 paths
unchanged. The new wrapper has empty SetupGrants, exact inert C/C++ flags and
default startup; no upload allowlist key was introduced.

## Public tooling oracle adjudication, accepted

The first completed tooling run preserved149 methods with one failed new draft
assertion; the135 established methods passed. At the parent's explicit request,
the reviewer inspected only that new wrapper-check method and its failure log
for adjudication. It searches for `#if`/`#error` spelling, whereas the unchanged
actual wrapper enforces all four required conditions and all other profile
exclusions with one C++ `static_assert` (`reactive_timing.ino`:10). The adopted
contract requires compile-time rejection, not that preprocessor spelling. No
production defect follows from this literal mismatch.

The independent author replaced only the syntax-dependent guard check with
actual syntax-only compilation of the exact unchanged wrapper under the valid
flag matrix and16 invalid matrices (each of eight macros independently flipped
or set to2). Typed declaration-only stubs contain no guard logic. All original
actual-source, empty-grant, no-local-macro and policy assertions remain. Review
accepts this correction to the new, previously unaccepted oracle. No public C++
oracle bodies were inspected.

The original oracle178ae1a1 and its148/149 result remain archived; the corrected
oracle4b9e896f was frozen before rerun. `oracle_correction_freeze.json` and the
reviewer's binding independently confirm this is the sole change among641
originally frozen entries. The actual corrected suite passes149/149 methods,
including the17 wrapper compile scenarios, with exit0. Production did not change
for this correction, so no additional C++ rerun was required.

## Completed public and private evidence

Read receipts in `state/analysis/P4_timing_evidence_raw/` establish:

- All14 normal host targets PASS, covering prior profiles and D129.
- D129 focused normal and ASan/UBSan each pass30 cases for M0 and M1, with
  21034 and21059 assertions respectively, no failures or skips.
- Configured Runtime normal and ASan/UBSan each pass32 cases for M0 and M1,
  with57181 and57219 assertions respectively, no failures or skips.
- Corrected tooling149/149 and registry2/2 PASS. Original tooling failure and
  earlier environmental interruptions are retained rather than reported as passes.

Reviewer-owned evidence adds the original four-assertion failing chronology
reproduction, unchanged fixed40/40 normal and sanitized passes, eight private
cases per motor configuration (472/492 assertions), six unchanged prior-profile
host layouts, instrumented host layout, and final exact source/test binding.

The target wrapper/source policy is reviewed and host-tested, but the absent
board prevents D129 native compilation, artifact identity and MCU loader-fit
checks. The offline timing analyzer remains a separate task. No hardware origin,
measured35ms reaction, mechanical stop distance, or human phase acceptance is
inferred from these synthetic observations.
