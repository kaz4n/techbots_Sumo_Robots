# Current execution checklist - 2026-09-25 Asia/Dubai

**D186 full-app diagnostic IMPLEMENTED / HOST-TESTED / REVIEWED.**
Source539bfbb0; independent corrected oracle80eb359b; separate same-model final
review c41c6be1 PASS/no open material findings. Current normal+ASan/UBSan each
14cases/23885assertions; default/explicit entry and unsafe flags pass. Staging
passes across Linux/Windows, including real junctions; skips are recorded.
Unchanged Trace/Gate each18cases/2570assertions; legacy tooling final67PASS and
one Windows-onlyskip. Initial source-review finding, first oracle mismatch and
coordinator import-path error retained. Eight pins/protected sources/history exact.
See analysis/P7_app_motor_fault_validation.md and reviews/P7_app_motor_fault_final_review.md.
No target operation, original fault reproduction, live RAM/WCET or human gate.
Next eligible task: fixed static/default/M0 diagnostic compile adapter, reusing
existing bounded executor and D141/D147 checks; independently test exact metadata,
project/flag substitution and seven-file alias mapping before native invocation.
Keep historical helpers/scopes and dynamic/generic admission unchanged. New ABI,
ET_EXEC/package/native initialization/capture binding remains required; no D149
address or D1732592B decoder reuse. D184 is still the last uploaded image.
Latest cleanup removed419.14MiB of verified duplicate installers; source/evidence
preserved. Current tests left0owned RAM/Windows fixtures. All earlier denied
paths remain untouched. Older paragraphs below are historical checkpoints.

**D185 both current profiles TARGET-COMPILED; no firmware upload.**
Bench/default build6d9e48f8 (reviewed34eb56ba) and MATCH/Immediate build1fcc7d57
(reviewed80c059f7) each ran one query/compiler,227/21transports, all7closing checks
PASS. Exact current raw/package hashes match D139/D138; debug hashes differ.
Existing byte-derived models remain: default592B deficit; MATCH conditional864B
span/860B largest payload. No fresh ABI/live RAM/WCET or physical/human gate.
See analysis/P7_current_app_compile_validation.md and actual review records.
Both D185 owners are consumed; do not rerun/relabel them. D184 isolated M0 halted
diagnostic is the last image; original D160/D161 full-app IO fault remains open.
Next eligible engineering work: scope a minimal inhibited full-app trace through
Runtime -> Transaction -> Robot -> MotorGate using existing motor_fault tracing,
with new source/artifact/layout/attempt binding. First resolve its compatibility
with the unresolved default allocation/static full-app context; no speculative
fix, timing relaxation, historical layout reuse or motor-capable upload. Existing
physical setup, live RAM/stack/WCET, explainability and human gates remain pending.
Cleanup92738412 saved174.38MiB; both new stage deletions were policy-denied.
They remain intact/excluded from retries; see STORAGE_LOG.md.
All prior denied deletion paths stay excluded. No native job is running; older
paragraphs below are historical checkpoints, not current action instructions.

**Offline scope audit complete after66672174.** No further eligible implementation
identified by coordinator/separate reused reviewer. Stale P7 acceptance prose
corrected and scoped-review PASS;58 links/diff checked. Exact hardware dependencies
below remain; no new build/test/device action or gate. See analysis/P7_remaining_scope_audit.md.

**D183 identified precompiled MATCH deployment HOST-TESTED / REVIEWED.**
D182 adapter72950615:35PASS/reviewcdbff1d5. D183 caller69bb9981/payload8a1c8523
(comment-only35e86452) passes66independent WSL and26Windows methods, including
source-aware realistic composition29919/29904units within30000.60unchanged
compiler/parser checks also passed; initial failures/oversize receipts retained.
Evidence24d94bb4/review76fbc5ef PASS/no material finding;18current and6/10/24prior
pins checked with explicit comment/newline provenance. No firmware/bench/locked
change, actual scope, qualification, permission or device operation. D180-D183
offline tasks complete; next dependency is fresh board admission/current target
build and existing inert diagnostic, then real qualification/human acceptance.

**D181 compiler failure retention HOST-TESTED / REVIEWED.**
Source0d73967b/corrected independent oracle d0f259fe:60methods PASS/no skips,
including33unchanged executor/parser cases. Original negative receipts and two
independently corrected new-fixture assumptions retained. Evidence/review7ad55b8c;
fresh same-model review acafc242 PASS/no open findings. No established/locked
test change;10D180/24D179pins exact;0native. D182/D183 implement the existing
MATCH dynamic/Immediate precompiled deployment route, without hardware execution
or modifying historical pins. Earlier no-further-offline assessment superseded.

**D180 main-app setup binding HOST-TESTED / REVIEWED.**
Contract e4aea29c/source70b9cea5; all17 declarations remain0/unconfigured.
Independent16methods first-run PASS;26selected legacy methods PASS, no skips.
Ten current/24priorD179pins exact; no old value/bench/locked assertion change.
Separate review30f3927f/4e26ed27 PASS, no open finding; source/oracle unchanged.
See analysis/P7_setup_binding_validation.md. No further original-scope offline
omission identified by the bounded audit. Next fresh board admission when available;
changed main-app target compilation and physical/human gates remain pending.

**D179 fixed inert caller HOST-TESTED / REVIEWED; board disconnected.**
Unchanged source d8418fad/8b47b1d6;44 independent methods PASS after two new fixture
corrections6e3d69c8; original results retained.24pins exact,0native/0RAMremnants;
Windows commands28,990/25,232units includingNUL and missing-scope refusal checked.
Separate review dbd4c2e4/d67c0dca PASS, no open material findings.
See analysis/P7_motor_fault_caller_validation.md. Actual
scope/owner/fresh admission remain future work; no other offline omission identified.

**D178 offline capture failure retention HOST-TESTED / REVIEWED.**
Source3f73fd58/baca4d79;13new+45existing Python checks PASS, review7649fb58 PASS.
Original capture failure/path survives error.json write failure; no retry, cleanup
or publication follows. New-fixture correction and original failures retained;
no established/locked assertion change. Native0, board remains disconnected.
See analysis/P7_dump_error_retention_validation.md. All11 prior D177 pins exact.

**D177 thin inert integration HOST-TESTED / REVIEWED; board disconnected.**
Source58d32dda/8ffb65c0; unchanged46+new16 independent methods PASS,11pins exact;
reviewb1de6217 PASS. Real command sizes28,989/25,231 fit30,000. Original failure
and first repair preserved. D175/D176/D174 remain unchanged; native calls0.
Next dependency is fresh current board admission and a reviewed native caller,
as detailed in CODEX_HANDOFF.md. No physical or human gate has been passed.

**Active: P7 software/release preparation.** PROGRESS.md is the append-only phase
authority; preserve its legacy bytes. User asks for prompt commits and continued
software work and authorized inert board checks with the connected UNOQ. Physical/human gates remain
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
- [x] D167 per-instance compile02 ownership:12 independent host tests PASS,
 117 actual local pins and separate review PASS; original failures preserved.
- [x] D168 corrected diagnostic TARGET-COMPILED:123 transports/ten children exit0,
  one query/compile, seven final checks PASS; actual review32e1c119 PASS.
  Source5d3d126e/final ELF87fb03e5; packet1edf4a08. No upload/reset/MCU read.
- [x] D169 default-disabled explicit activation/profile admission: source32b2d9d4,
  independent13+legacy29+driver3 PASS;18cases/2570assertions each normal/sanitized;
  revieweeb297fa PASS. No new native action or existing assertion changes.
- [x] D170 explicit fresh-attempt staging: implementation0160d1a6, independent26
  methods pass across WSL/Windows,91 legacy methods PASS, review8233de35 PASS.
  Original fixture failure retained; production/assertions unchanged on repair.
  Retained104-file stage byte/mtime and all9 input pins unchanged.
- [x] D171 closed active01 compile profile:16independent+12legacy tests PASS,
  actual117-pin local admission, reviewc9781e61PASS; old manifests unchanged.
- [x] D172 active default/dynamic inert compile: evidence db1228ce;123transports/
  tenchildren0, sevenfinalchecksPASS, actualreview41ecc2c9PASS. No upload/reset.
- [x] D173 file-only ELF/ABI/recipe observation: evidencecc9f50c6, compactABI822c917d,
  fivechildren0/146postchecksPASS, review60fdc78ePASS. No MCU operation; scope consumed.
- [x] D174 offline decoder: source68653597, independent22/22 tests PASS, sevenpins
  exact/reviewefe5a39ePASS. Structural DECODED only; coherenceUNPROVEN.
- [x] D175 closed inert upload profile: source67eccbc5, independent34PASS, direct
  legacy tests PASS, historical consumed snapshot mismatch preserved; review1317cc4fPASS.
- [x] D176 closed finite capture: source7b7e8c69,8+38+46methodsPASS/review93ef66a7PASS;
  twoMAJOR findings reproduced/repaired, fourteenpins exact. Native0.
- [x] D177 command framing, strict receipts and conditional upload/capture callbacks;
  46+16host methods PASS, separate reviewb1de6217. No actual native run.
- [x] D178 original P7 log-preservation defect repaired;13new+45existing Python
  methods PASS, review7649fb58; synthetic storage failures, no hardware claim.
- [x] D184 fresh board admission and unchanged reviewed D179 caller: actual
  one-shot diagnostic completed, separate evidence review PASS. No rebuild.
- [ ] Current app source37a2099f checked target compile-only profiles, fresh
  stages/owners and current identity; preserve prior denied cleanup paths.
  Original D160 failing operation remains unknown; do not relax safety bounds.
- [ ] Qualify native loading/startup, stack/heap/WCET and release workflow before
  adoption. Structural RAM tail94352B is not measured free memory.

Preserve original D144 rejection, D139 dynamic592B deficit, old frozen contracts/
validators/oracles and production admission. No upload/reset or firmware changes
were made by D148. No current STAND/RING authorization. D184 is now the last
successful upload: dynamic/default/M0 isolated diagnostic COMPLETE. Earlier D160
static full-app samples made no progress; that fault remains unresolved. All
consumed D118/D160/D184 scopes remain ineligible for reuse.

Original P0-P5 physical/human packets, D121 B7/R6 conflict, native dump holder/
quiescence/cancel/reopen requirements and SC-AP release workflow remain pending.
P6 conditional, no release tag/rehearsal/human PASS. Do not request extra hardware
now. Current permission advances software, not invented measurements or gates.

Storage: retained D168 stage104files/764049B and D172 active stage104files/764719B
both had automatic cleanup review rejection (blocked by policy). Never retry
removal directly or implicitly. D172 raw packet890157B/metadata5241B is useful;
no firmware downloaded or new bytecode. Incremental Gitpacking recovered720896B,
with new pack/connectivity checked and HEAD/refs/reflogs unchanged. This adds to
D170's11196416B and historical old-session compression; see STORAGE_LOG.md.
D173 rawABI219185B/compact D174 test evidence retained; no firmware download or
new cleanup attempt. C: observed1296179200B free; recheck before large work. Prior denied targets and
unique evidence remain; serial RAM builds/Python-B avoid redundant outputs.

Schedule: actualP3 not passed by end28Sep invokes reactive+SIDESTEP/DIRECT plus
recorder cut; P6 needs actualP4 by30Sep and no stronger cut. Freeze1Oct21:00Dubai,
rehearsal2Oct, competition3Oct. No scheduled date creates acceptance.

D175 final storage audit: zero new disposable files/zero RAM remnants,0B reclaimed.
Current1195085824B C:free is a fluctuating observation; keep retained evidence and
exclude every prior denied path. Exact capture next-step is in CODEX_HANDOFF.md.

D176 storage:0RAMremnants/126287872B C:free observed; no new diskcleanup claimed.
Recheck space before work and preserve all earlier blocked cleanup exclusions.
