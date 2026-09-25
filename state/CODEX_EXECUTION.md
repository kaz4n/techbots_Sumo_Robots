# Current execution checklist - 2026-09-25 Asia/Dubai

**D156 actual upload FAILED; capture0; scope consumed.** The inherited1MiB
process file cap blocked copying the2,303,728B loader. Independent final checks
passed; original failed report/temporary fragment retained. D155's30+10 host
methods pass but did not model this native copy. Next upload-limit correction.

**D152 pure startup interpretation:37 host methods PASS and scoped review PASS.**
See analysis/P7_static_capture_validation.md. Loader reference is ELF-derived
e9322826; original packaged-BIN reference defect is preserved and corrected.
No current-image upload or MCU capture. Next implement/review the bounded guard.

**D139 qualification complete: compiler PASS, conditional default fit FAIL.**
The unchanged default/M0 image exceeds the modeled loader pool by592 bytes.
Exact evidence is in analysis/P7_default_qualification_validation.md and its
separate review. D140 source research and D141/D142 pure policy/artifact host
validation are complete. Production policy remains dynamic-only. D143 passes80
host methods; D144's one static compile returned0 but the structural validator
rejected unsupported symbol encoding. No upload/reset/run. The GO is consumed;
D145 identified six absolute TLS type6 symbols after one checked read; exact
installed TLS assembly/object provenance is verified by D146. Native/indirect
use remains unqualified. D147 pure host extension passes19new+51old methods and
separate fresh-context code/receipt review; actual new-interface validation pending.


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
- [ ] Add explicit fresh run ownership without global rebinding or cloned wrappers;
  review known temporary residue before another inert attempt. Reuse the packet,
  collector, pinned loader helper and explicit CLI config; no binary/source copy.
- [ ] Qualify native loading/startup, stack/heap/WCET and release workflow before
  adoption. Structural RAM tail94352B is not measured free memory.

Preserve original D144 rejection, D139 dynamic592B deficit, old frozen contracts/
validators/oracles and production admission. No upload/reset or firmware changes
were made by D148. No current STAND/RING authorization. The last upload remains
consumed D118defaultM0 sourcee820c0e1; do not infer current MCU state or reuse it.

Original P0-P5 physical/human packets, D121 B7/R6 conflict, native dump holder/
quiescence/cancel/reopen requirements and SC-AP release workflow remain pending.
P6 conditional, no release tag/rehearsal/human PASS. Do not request extra hardware
now. Current permission advances software, not invented measurements or gates.

Storage: no new disposable candidate in the bounded follow-up f2fa3c28. D148 saves
125141B compact receipts plus launcher, no duplicate binaries/builds. Keep required
evidence and all previously denied targets intact, including the111-file matrix
host-output batch newly blocked on25September. Verified compression and incremental
Git packing saved about49.9MiB; all refs/reflogs and content remain intact. Read STORAGE_LOG.md and check
free space before material work. Python-B; no persistent fixture/compiler tree.

Schedule: actualP3 not passed by end28Sep invokes reactive+SIDESTEP/DIRECT plus
recorder cut; P6 needs actualP4 by30Sep and no stronger cut. Freeze1Oct21:00Dubai,
rehearsal2Oct, competition3Oct. No scheduled date creates acceptance.
