# Bounded D135 copied-source fault probes

These are **post-source-review fault-injection checks**, not pre-implementation
independent test authorship or hardware faults observed in practice. They test
the originally frozen contract's internal obligations inaccessible through public
inputs. Production files and public APIs remain untouched. No test setter,
friend/private exposure, layout cast, new recorder or controller is introduced.

Root may run `run_mutations.py SOURCE BUILD LABEL` only after ordinary/private
validation and with exclusive compiler access. It reuses actual existing M1
production objects/main, substitutes exactly one locally copied modified .cpp
object and the review probe, removes six public test objects, and runs only the
one named injection test. Every replacement requires one exact source match.
Cases execute serially and stop at first failure; source/copy/object/command
hashes and output remain bound. The runner does not rebuild production or delete
evidence. Root owns subsequent compact evidence/verified build cleanup.

|Case|One copied-source injection|Contract observation|
|---|---|---|
|1|Omit DIRECT's actual routeNormal call but retain its later marker call|Cue and HANDOVER_FAILED(actual OPENER3), no HANDOVER/APPLIED/retry|
|2|After DIRECT's route/marker, force final selected state SEARCH|HANDOVER_FAILED(actual SEARCH4), no success/retry|
|3|Capture cue token with its high32 bit toggled|HANDOVER_FAILED(TRACK5), proving full token comparison at route ownership|
|4|Drop the tag after exact savePending capture|Next receipt INVALID_RECEIPT, no repair despite later good inputs|
|5|Clear pending.valid at receipt entry while phase RECEIPT remains|Missing-owner path INVALID_RECEIPT, no repair|
|6|Drop RECEIPT phase to WAITING at receipt entry while valid tag remains|Tag alone cannot succeed; INVALID_RECEIPT, no reopen|
|7|After a handover is saved, set next token exhausted|Prior genuine matched receipt yields APPLIED first; then token0/STOP without fake request or duplicate terminal|
|8|After GO while waiting without cue, set next token exhausted|Prior ordinary receipt processed, then INTERRUPTED(STOP_FAULT), no APPLIED/fake receipt/retry|

Cases7/8 accelerate the otherwise unreachable 2^64 public lifetime by changing
only the copied implementation's next-token field at the specified existing
boundary. They do not claim that billions of real iterations were executed.
Case1 deliberately leaves a misleading marker, so the independently checked
final-state condition must still reject it; case3 separately rejects the route
token even when final TRACK is plausible. Cases4/5/6 independently cover each
half of owner/tag/phase coupling. Host M1 means synthetic acknowledged callbacks,
not permission to run any motor or use native hardware.

`mutation_probes.cc` includes the corrected private13 solely to reuse its public
Rig. The13 register but the exact doctest name filter runs only the single new
case; first ordinary private results remain separate. All expected wire details
are numeric contract values. Deliberately altered traces cannot qualify P5.3.

Status: DESIGN/SCRIPT PREPARATION ONLY; no injected copy, object or executable
has been generated and no compiler/test has been run by this reviewer.
