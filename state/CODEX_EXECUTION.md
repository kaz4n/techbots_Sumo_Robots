# Current execution checklist - 2026-09-25 Asia/Dubai

**D165 target compile FAILED; D166 identifier-only host fix PASS.**
Actual nativeCONFIG_PWM macro collision is retained. Corrected names preserve all
values/behavior; macro1/1, normal+sanitized18cases/2570assertions each and separate
review PASS. No upload/reset. Next fresh per-instance compile02 ownership/source
binding in existing bounded caller, then one reviewed inert compile.

**Active: P7 software/release preparation.** PROGRESS.md is the append-only phase
authority; preserve its legacy bytes. User asks for prompt commits and continued
software work with the bare UNOQ. Actual physical acceptance/human gates remain
pending; D051/D075/D122/D137 permit scheduling, not fabricated measurements.

| Existing task | Software/evidence status | Remaining acceptance |
|---|---|---|
| P0 | Scripts/source checks and actual inert diagnostics | Electrical/PINMAP/human gate |
| P1 | Core/properties/locked safety and review | Human EXPLAINED OK/GATE P1 PASS |
| P2 B1-B6/B8 | HAL/Runtime/recorder; historical inert app observation | Actual sensors/buttons/motors, dump, live stack/WCET; current default app modeled592B deficit |
| P2 B7 | Inhibition/receipt checks | Full-reverse/R6 conflict and actual stress trial |
| P3 | Drive/turn/stop profiles and countdown analyzer | Measured trials/tuning/gate |
| P4 | Reactive/timing, target-loss analyzer, bounded push/admission | Actual combat trials/deployment/gate |
| P5 | Six openers, availability, abort producer/analyzer | Actual opener/mirror/UI/abort trials/gate |
| P6 | Deferred | Actual P4 gate by30Sep and no stronger28Sep cut |
| P7 7.2/7.4 | Runbook/mode card/kit/blank sheets; D138 R/threshold software | Native/physical readiness, qualified procedures, printing |
| P7 7.1/7.3 | Safe compile-only example and source-bound MATCH checks | Qualified release/tag and actual2Oct rehearsal |

## D138 software validation and scoped review PASS

- Production first-source d19f8964; no production fix during testing.
- 20ordinary cases perM0/M1;29public+2private configured cases perM; both normal
 andASan/UBSan PASS. Full22targets PASS, including current profile suppression.
- Three new-draft issues retained/adjudicated independently: typedGuard init,
 doctest expression grouping, incorrect filtered-warning premise. No established
 assertion/43protected source changed. Ordinary preprocessing identity preserves
 fullrun relevance after configured-only correction.
- Final687inputs0fe188b7 exact;82links/9fragments and legacyPROGRESSprefix verified.
- Exact MATCH/Immediate sourcefcddbd8e/ELFcb5fbb53 compilePASS; conditional261280B
 peak/864Bspan,62imports,16ABI sizes and72oldoffsets unchanged. No upload/reset.
- Read analysis/P7_readiness_validation.md and reviews/P7_readiness_review.md for
 final scoped disposition. D138 commands are terminal; owned RAM scratch released.

## Next original-scope task

- [x] D141 fixed policy:35public+4private host methods; scoped review PASS.
- [x] D142 static artifact parser:45public+6private methods; scoped review PASS.
- [x] D143 one-shot transport/helper:80 methods; scoped review PASS.
- [x] D144 current static/default/M0 compile:exit0; original layout rejection retained.
- [x] D145 exact rejected ELF read and D146 installed TLS provenance; both consumed.
- [x] D147 exact-six-alias extension:19new+51old methods; independent review PASS.
- [x] D148 actual seven-artifact validation:5 read-only commands exit0, all postchecks
  pass, query/compile0. Sourcefcddbd8e/finalELF5cc2dfde unchanged. See
  analysis/P7_static_native_actual_validation.md and linked review/raw receipts.
- [x] Local entry/constructor inspection:34 commands/32 functions; source/ELF match,
  separate review14e6d959 PASS. Original raw92b72069 retained; literal-elision
  description corrected. Early native printk/startup behavior remains unmeasured.
- [x] D149 exact16-type/82-offset debug-layout comparison: all match; five reads
  exit0 and separate actualreview3f4d20b7 PASS. See analysis/P7_static_native_abi_validation.md.
  No MCU execution; the file-only observation is terminal and consumed.
- [x] Bounded native binding audit:168ABS/22veneers/62native values/119table entries
  verified; scoped reviewf738ef54 PASS, complete indirect dispatch still pending.
- [x] Selected GPIO/PWM/RCC direct calls and types observed; D150 remains FAILED
  on the ambiguous init-name query, with49 useful partial sections preserved.
- [x] D151 numeric18-byte wrapper observation:5 reads exit0/all postchecks pass;
  separate actual reviewe35ee292 PASS. No build/upload/reset. Original negatives
  remain unchanged. See analysis/P7_static_native_dispatch_validation.md.
- [x] Fresh-context same-model combined dispatch reviewe4eca064 PASS, no open
  findings.836 retained app instruction/literal rows match the actual debug ELF.
- [x] Verified upload dependency/filename route; D152 pure18-read plan/parser,
  37 independently frozen host methods first-runPASS and separate reviewcdae7896.
- [x] D153 passive collector:46 independent+4 supplemental methods first-runPASS,
  revieweed7414d; exact reads/deadlines/claim/failure evidence, no native operation.
- [x] F165 file-only core/tool version, metadata and override inventory; selected
  boards/platform bytes unchanged. CLI initialization query intentionally not run.
- [x] D154 one-shot upload wrapper:55 unchanged public+3 reviewer methods PASS,
  both MAJOR findings resolved; original failures retained. F166 observed CLI
  initialization prerequisites; see analysis/P7_static_upload_validation.md.
- [x] D155 host coordinator:30public+10reviewer methods first-runPASS;
  review26fcf2f7PASS, actual local composition/source/packet checks and sizing.
  See analysis/P7_static_startup_launcher_validation.md; no native action.
- [x] D156 one scoped bare-board M0 attempt: FAILED loader-copy file limit,
  capture0, nine transport calls0/clean final checks. Scope consumed, no retry.
  See analysis/P7_static_startup_actual_validation.md and actual review.
- [x] D157 explicit upload_loader cap: 55 legacy +59 new-entry tests PASS,
  four real child-copy boundaries PASS, scoped review fc1b2414 PASS. D153 and
  historical failure/oracles preserved; no new native action. See
  analysis/P7_upload_file_limit_validation.md.
- [x] D158 per-instance run02 ownership:227 aggregate methods PASS, review
  bda4208e PASS; original failures/oracles preserved. Composition fits command limits.
- [x] D159 exact known1MiB temporary fragment and empty parent removed; reviewed
  code/result verify identity/hash, no MCU action. Original D156 remains failed.
- [x] D160 one run02 upload/capture: upload success,18 passive reads/full flash
  matches,14 transport/final checks PASS. NO_RUNNING_PROGRESS: STOPPED/epochs3.
- [x] D161752B passive diagnosis: Robot0x0110/GateIO3/invalid prior receipt,
  exact D160 prefixes; independent scoped reviewc323dc88 PASS. Scope consumed.
- [x] D162 inert callback diagnostic implemented and independently host-tested;
  real Gate, first-failure retention, default denied setup; unchanged native limits.
- [x] D163 checked compile-only route: five literal additions;65policy tests PASS.
  No historical pins, upload manifests or existing assertions changed.
- [x] D164 per-call executor:146legacy+15new host methods and review PASS.
- [x] D165 one identified target compile: onecompilerexit1, all122transports0/
  sevenfinalchecksPASS; CONFIG_PWM macro collision. Consumed, no upload/reset.
- [x] D166 literal enum rename; independent macro and normal/sanitized tests PASS.
- [ ] Fresh per-instance compile02 ownership in existingcaller, separate input
  binding and review; preserve all compile01 pins/receipts and process bounds.
- [ ] Recompile corrected diagnostic under new scope and inspect actual result.
- [ ] Review target result before any separately identified inert diagnostic run.
  The original D160 failing operation remains unknown; do not relax safety bounds.
- [ ] Qualify native loading/startup, stack/heap/WCET and release workflow before
  adoption. Structural RAM tail94352B is not measured free memory.

Preserve original D144 rejection, D139 dynamic592B deficit, old frozen contracts/
validators/oracles and production admission. No upload/reset or firmware changes
were made by D148. No current STAND/RING authorization. The last successful upload is now
D160 static/default/M0 sourcefcddbd8e; both runtime samples showed no progress.
This is not whole-robot qualification; neither D118 nor D160 may be reused.

Original P0-P5 physical/human packets, D121 B7/R6 conflict, native dump holder/
quiescence/cancel/reopen requirements and SC-AP release workflow remain pending.
P6 conditional, no release tag/rehearsal/human PASS. Do not request extra hardware
now. Current permission advances software, not invented measurements or gates.

Storage: D162/D163 RAM compiler/fixture outputs removed; fresh check zero sumox
scratch directories. Independent repo/task-Temp audit found no new safe candidate.
Old-session lossless compression reclaimed1369392201reported allocatedB; previous
cleanup is recorded in STORAGE_LOG.md. Retain compact evidence and leave all prior
policy-denied paths untouched. Recheck disk space before material work; Python-B,
one compiler, no duplicate source/firmware snapshots.

Schedule: actualP3 not passed by end28Sep invokes reactive+SIDESTEP/DIRECT plus
recorder cut; P6 needs actualP4 by30Sep and no stronger cut. Freeze1Oct21:00Dubai,
rehearsal2Oct, competition3Oct. No scheduled date creates acceptance.
