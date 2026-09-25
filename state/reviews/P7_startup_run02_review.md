# Explicit run02 ownership review

25 September 2026, Asia/Dubai. Separate same-model review reusing earlier
startup design/code context. Design followed by scoped source/receipt review;
no native operation, implementation or test execution by this reviewer.

Initial contract SHA256
`b86d179cd469d9863b4528841c44f529e3877dba46f75072938dd0e9f3b30515`
had one material API inconsistency: a no-global-mutation bootstrap required
explicit bindings, but legacy upload had no bindings parameter. Resolved by
allowing upload(..., bindings=None) while retaining fixed run01 and its old cap;
no run_id override is added to that legacy entry.

Amended reviewed contract SHA256
`0db1c1c534b181d6059ecd4edb2c21d7c703616f966a2125cb3b8182852678f0`.
**Design PASS for host preparation; no open material design finding.**

Closed run01/run02 selection plus per-instance copied bindings is sufficient;
no generic configuration framework or module-global rebinding is needed.
Default run01 retains old scope/output/dependency pins and must reject changed
helpers. Run02 alone selects current uploader/collector hashes, explicit loader
entry and distinct fixed owners; all other dependencies and D144 identity stay
fixed. Original scopes, source, oracles and failed run01 evidence remain intact.

The pure profile/projection helpers make selection independently testable.
Projection changes only run_id/output of checked original bindings; full remote
validation remains before claim. Expected identity must flow from the selected
instance through payload, report validators, intents and orchestration, rejecting
cross-run reports. The constructor rejects other selectors before filesystem
or process work. Bootstrap passes bindings explicitly without assigning globals.

Required tests cover both owners, interleaved isolation, consumed paths,
cross-run/invalid identities, old pins and unchanged legacy behavior. Command
size and actual composed source pins still require verification before future
use. Implementation and frozen receipts are pending, not inferred from design.

No native_run02_scope.json, residue disposition or execution permission was
provided by this design. The then-known /tmp/remoteocd entry blocked admission;
its subsequent D159 removal is separately reviewed and does not revive run01.

Pre-freeze test-author clarifications reviewed, contract SHA256
`e53a3273d2309ebdedd0ccb1fbd52af7ba721ef3f4ea191640c6b779b8f9d45f`.
The payload keeps existing source/hash/bindings fields plus explicit run_id;
API dispatch remains closed and global-free. Historical dependency expectations
come from the preserved16-pin receipt minus its four named D144 receipt entries,
leaving the correct12-key dependency map. This resolves the baseline ambiguity
without changing behavior. **Design PASS applies to this clarified contract.**
Hold actual source/receipt disposition until the independent tests are complete
and frozen; no new execution or cleanup authority follows from this addendum.

Actual source review: initial bcf623dc; first executions preserved in1854bb8e.
Final uploader23661c8a18205cfb64d77c5ae81765463560cf52f451e257bb3bb339d39f2b18,
collectorab0bb32031c1986cc58db1f410a0bdca59449a9dae237672085a81e291b33458,
launcherc95888353c9d85c5d9b0e545553a9e9dcde372b5b313102dd14240ce38db4e0c.
Wrapper validation/copy precedes claims (upload:61-96, capture:67-90); output
checks use each instance. Launcher:143-170 closes profile/projection selection;
scope, payload, intent and report paths consistently use its expected identity.
Legacy12 dependency pins remain intact; only two helper pins change for run02.
No acquisition, child-limit, timeout, fixed command or final-check broadening.

Verified run02_freeze and all eight first receipts: unchanged public55+59+46+30
and reviewer3+4 suites PASS. New20 had19 passing methods and four subcase errors
in its bootstrap method: the controlled support fixture omitted json_bytes.
Original startup_private had8/10: its output-only binding fixture and profile-less
native mock no longer matched the new default seams (initial launcher:428-430,
603-608; original private:178-206). Both negative receipts remain unchanged.

Repair only restores default binding decode/constructor-orchestrator call shape
(current launcher:428-434,605-614); run02 retains strict projection and identity.
The new test adds only a pure serializer to its sentinel, preserving all oracles.
Verified run02_repair1_freeze and three receipts:20/20,30/30,10/10 PASS, exit0,
0.623/0.046/0.079s. All18 pins match each freeze, each receipt reports unchanged
pins, and current bytes match the repair freeze. Legacy test files are unchanged.
Final aggregate:207 legacy/reviewer tests plus20 new ownership tests PASS.
Composition receipt8bc2abe2 uses final launcher,16 dependency/receipt pins and17
runner pins, all checked against current bytes; six forms and zero dispatches.
Upload/capture commands are28751/25436 UTF16 units, with exact run02 owners.
Its source_manifest=null is an unused optional projection, not a measured count;
the existing local-stage/source check remains the separate source evidence.
**Scoped source/host-test/composition PASS; no open material finding.** This
provides no native scope, claim, target success, retry or phase-gate evidence.
