# D225 recorder delivery source and host review

Date: 2026-09-26 (Asia/Dubai). Independent fresh-context review only, in isolated
worktree `sumox-recorder-session-20260926`, base
`ee1bdcedf412903445c5076cae5980a43e0dc34e`. No main-checkout writes or board use.
The date precedes the 1 October freeze; the scheduled bench milestone is not a
passed human gate.

Final caller: `tools/run_recorder_delivery.py`, 50,592 bytes, SHA-256
`9ea1be98388139343be02bc74857c220faa75c32b876b9938f855188d750b6cd`.
Contract: `P7_recorder_delivery_contract.md`, 5,864 bytes, SHA-256
`8c8ac3e6ea619981477f392b4869b1ff72066bcd9206f776602c08a56a751283`.

## Verdict

**PASS for the scoped caller source and retained host validation.** No open
BLOCKER, MAJOR or MINOR finding remains in this scope. Both material findings
below were repaired and checked. This review does not authorize an unidentified
native invocation or establish actual recorder delivery.

## Findings and repair trace

1. **Resolved MAJOR: receiver cleanup replaced the first failure and could omit
   partial bytes from capture decoding.** Initial caller 48,144 bytes / SHA-256
   `5732c69650499b9a951c92726fd19d75c4008a840f106d5a32fc97e87bdc3531`
   detected a deadline/output-bound failure before unguarded kill/reap calls.
   A cleanup exception escaped instead, skipping bounded stream reads. A local
   controlled timeout followed by `OSError('secondary kill failure')` returned
   only the latter, with neither cause nor context containing the timeout.
   The output-bound path also replaced its journaled reason with a transport
   wrapper. Saved command files remained intact, but capture decoding and the
   reported primary error were incomplete.

   Repair 50,366 bytes / SHA-256
   `575e6d5c7a4440cc289428a4b479e9cc1d7318f22ed6214281335196d9b0b066`
   separates the primary error from the transport wrapper, records secondary
   kill/reap/read errors, independently performs both bounded stream reads and
   keeps unreaped children tracked. The original reproduction, extended to
   simultaneous kill/reap failures, now retains `TimeoutExpired` and both
   secondary details. Independent focused cases pass for timeout, output-bound,
   available partial bytes, one failed stream read, multiple child cleanup
   failures and the closed launch latch. This repair remains in the final caller.

2. **Resolved MAJOR: Windows host binding validation imported Linux runtime
   support.** The real binding and prepared-payload construction tests failed
   because loading all of `capture_remote.py` imported unavailable `resource`.
   The exception output and exact prior caller remain under
   `../analysis/P7_recorder_delivery_raw/tests/windows03/`.

   Final caller adds `host_binding_support` and changes only `upload_bindings`
   to reuse the existing `match_deploy.binding_support`. The extractor requires
   exactly the same five pure validators from the checked support bytes. AST
   comparison with the retained prior caller confirms those are the only
   function changes. Full native support remains in the native payload, and
   original schema checks remain in use for board execution. The three unresolved Windows
   construction/admission methods pass in `windows04`; the first Linux suite
   also passes those paths. No test skipped or stubbed the Windows defect.

## Source audit

- Exact CLI forms bind current reviewed HEAD, the full 32-hex attempt and a
  positive uint64 session. Session-keyed local/board owners prevent suffix-based
  reuse. Compile and run are separately consumed; no automatic retry is added.
- Generated identity/grants change only the staged recorder header. The checked-in
  header stays disabled; the closed profile remains static/default/MATCH0/M0.
  Source admission compares current bytes to reviewed Git blobs, closes the full
  staged source set/hash and reuses inherited single-job compilation, metadata,
  native ELF/TLS/package validation and closing checks.
- One directory push is followed by source closure before compilation. Run
  restoration requires successful compile closure and exact artifacts, then
  repeats live prerequisite/source/artifact checks. The original uploader's
  read-only admission precedes receiver arming and retains its separate
  `/tmp/remoteocd` absence check. No scratch deletion, broad whitelist, service
  operation, UART/router RPC, detached retry or extra reset is introduced.
- The receiver uses fixed ADB identity, a fresh ticket and expected session.
  The observed TCP connection makes no router-registration or framing claim.
  One upload retains its inherited child lifecycle. Receiver deadlines, bounded
  joins, daemon worker and the lock shared by launch/closed-latch registration
  contain late work; unresolved shutdown remains a failed result.
- Acceptance reparses retained wire, checks CSV bytes and current declarations,
  and requires the expected synthetic identity, 5,001 inhibited frames, eight
  scenario events, SEALED/no-loss lifecycle and specified timing bounds. Valid
  but short/lossy captures do not become DELIVERED. First and closing failures
  preserve failed status and available evidence.

The D224 session review remains accepted in its own scope and was not reopened.

## Evidence checked

Read the actual scoped source, inherited primitives, independent test sources,
validation report, failure/correction receipts and final closure. Independently
recomputed all 18 final input pins and all 37 evidence manifest entries: PASS.
The two restored CLI inventory files also match their exact Git HEAD bytes.
`git diff --check` passes. The reviewer's only persistent write is this report;
the controlled local reproduction started no native process.

Independently reconstructed the passed-method sets from the retained stderr:
**42 applicable Windows methods and 43 Linux methods**, exactly matching the
closure. The Linux-only generated-header case compiles M0/MATCH0 and rejects
the other three motor/MATCH combinations. Tests exercise real bootstrap,
staging/hash construction, artifact payload bounds and upload bindings, plus
controlled process lifetimes and the real complete 5,001-frame synthetic wire.

Initial fixture corrections remain disclosed: a 33-character intended-valid
token, Windows path separators, an outdated wrapper expectation and a missing
exported-role fixture. Frozen guards correctly refused checkout-converted CLI
inventory bytes; the exact main/HEAD bytes were restored only in this isolated
worktree, with guards unchanged. Linux first-run `linux01` had one inherited
file/ancestor metadata-stability refusal with unchanged input pins. Its cause
was not established; one unchanged targeted rerun passed in `linux02`. All
original failures remain retained. Successful methods and the accepted core
suite were not broadly repeated.

Checked closure SHA-256:
`614390ef733ea85f7f3c11e39b68e4e16f6662d1754abf2e1bf2e4a3209cbfce`.
Evidence manifest SHA-256:
`a69d400ced67bf1bfe26bc5b0f28f5c3f9bf3e34dfbd88d550d4e208b3027fff`.
Validation report SHA-256:
`a4274d4d8f7260ea6dc5e0d3bcdfd00f15006977a589b4069fb304e3f35bcf84`.

This is source/host acceptance only. Exact native-action scheduling/admission,
actual delivery, physical UART/throughput/timing/RAM qualification, sensor/motor
acceptance, motor-run authorization and human phase gates remain separate.
For the parent's already authorized bare-board test, the concrete next action is
one caller attempt after the current compile matrix closes: commit the reviewed
source/helper bytes, use that exact current HEAD and one fresh positive-session
32-hex attempt for `--check-only`, `--compile` and then `--run`. Run proceeds only
from the matching successful compile outcome, all nine closing checks and exact
checked artifacts. Fixed ADB serial/boot and every inherited live admission must
pass. Any required three-file D221 scratch cleanup stays the parent's separate
exact operation; `/tmp/remoteocd` must be absent, and this caller cannot remove it.
Retain the resulting receipts and stop on failure without a retry or replacement
attempt. Static/default/MATCH0/M0 and the single inhibited upload remain fixed.

This source/host review satisfies the caller review prerequisite for that scope;
it creates no extra recursive admission chain. A changed implementation/profile
or a claim of actual successful delivery would require its own supporting
evidence, not an inference from these host results.
