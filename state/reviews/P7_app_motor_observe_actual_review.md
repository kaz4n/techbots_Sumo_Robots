# D195 actual inhibited observation review

Date: 2026-09-26. Reviewer: separate same-model agent, reused context. Scope: local read-only inspection and standard-library analysis of the completed run, saved file retrieval and interpretation. No subject import, test execution, device call, firmware change or additional attempt was performed by this reviewer. Only this review was written.

**Verdict: PASS for the bounded collection, retrieval and selected-field interpretation. The native callback failure was reproduced. This is not a runtime-reliability or motor-acceptance pass.** No material evidence-integrity discrepancy was found in the inspected chain. The first failed callback and the later unconfirmed halt remain substantive unresolved results.

## Bound attempt and closure

The invocation records check-only exit 0 and execute exit 0 at reviewed HEAD `10be312678a9ee41adc660cd197b0d7f82f9daaf`. The 44 saved Git observations consistently identify that HEAD, the committed scope and unchanged tracked content; subsequent untracked paths are confined to the claimed native owner. The result and separately saved final checks agree exactly.

I rehashed all 159 admitted local inputs, including the 128 D193 manifest inputs, the 11 scope file pins and 12 preparation provenance pins. They remain exact. Scope `1a6dc8f06b56649754e941657c15cc5812ab31ea02c520921b2593eaecfb8980` and preparation `8acf1b13a5e4fc8dcae2f58f181da481dc40d2f97a78a2d5443a4cf2a826c197` bind the previously reviewed D193 static/default-startup `MATCH=0`, `MOTORS_ALLOWED=0`, probe-enabled artifact and its actual successful ABI02/entry evidence. Raw sketch 95,344 bytes / `f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc` and package 95,360 bytes / `85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c` are unchanged in the actual action payloads.

All 13 transport intents agree with their saved executed argv, command lengths, timeouts and command metadata; each transport exited 0 with empty stderr. Counts are exactly one adapter claim, one push, three each of CLI initialization, builtin-file inventory and capabilities, one upload and one capture. Upload and capture each have one durable attempt. Capture's predecessor hash matches the canonical returned upload envelope. Both envelopes have returned attribution, no first error and no postcheck errors; final diagnostics have no transport, prerequisite, local or finish errors. No second upload/capture appears in this owner.

I decoded the compressed action payloads as data, without executing them. Their bindings exactly match preparation; inline helper/support/upload hashes and the staged adapter pin match the reviewed sources. All three capability observations are equal: the 107 installed source-file records match current mapped file bytes, total 775,376 bytes, and independently rebuild source digest `3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0`. All three initialization and builtin inventories equal their pinned baselines after the explicitly bound boot-ID substitution. Full identity remains the reviewed Arduino UID/GID 1000, aarch64 board and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8` where recorded.

Upload's retrieved full report records one reaped, non-timeout child, exit 0 and empty stderr. Its stdout names the observer package and loader; the reported extra flash erase range is retained. Capture records exactly the reviewed 26 reads / 727,152 requested bytes in order: full loader and sketch before, six current-ABI SRAM windows twice, full sketch and loader after. Every address, extent and snapshot index matches the reviewed plan. Before/after flash chunk hashes agree, and all four remote full-image comparisons are true. These full-image conclusions are bounded by the pinned remote verifier and saved receipt; the 14-file retrieval contains the reports and SRAM windows, not the flash chunk bodies for an additional local image reconstruction.

The recorded pre-sample pause is 30.000400787 seconds, the between-pass pause 2.000380534 seconds, and capture span 251.230523341 seconds. Their monotonic ordering is valid and inside the inherited capture bound. Source ordering places the first pause after the initial flash checks and before SRAM read 7, and the second before read 13. These are host-side observation intervals, not a target-time or target-state assumption.

## Retrieval and independent interpretation

The separate retrieval exited 0 with empty stderr. I inspected its inline program: it uses the unchanged historical file-only reader body (`49494df4594ab7c176145c1f3ae1bc63e9c971b0b9f1e0da3e2b60431eca4e5f`) and hash-checked helper `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`. Only the fixed identity and 14 exact saved-file pins are supplied. No MCU read/reset or tool subprocess is introduced by that reader. Both full identity observations agree, and 14 closing file checks are recorded.

All 14 decoded file bodies total 18,017 bytes and match the retrieval intent's exact path/length/hash records. The full saved upload report is 1,823 bytes / `a5bf84c92dc1fdf8db2c225c78582a37d8977afff27baa4a035782a13b337c82`; capture report is 7,122 bytes / `cc5ef1b0b3cdf35405e92d449f8b93a9786763ccb5c1f5d0e7d7e977980281b8`. Both agree with their action-envelope full-result hashes; saved capture JSON equals the returned capture report. Each SRAM body matches its capture snapshot pin. All six first/second pairs are byte-identical, including bytes not selected by the decoder.

The interpreter differs from preserved `P7_app_motor_fault_run_raw/interpret_run02.py` only in the declared comment, paths, evidence hashes, namespace and schema substitutions. The actual current field-map hash remains `b96b6a3e7349baff471af3bb115c13ab2c1de07c6949a419ed3e9ed1afe16939`; its actual-GDB layout audit is recorded in the caller review. Without running the interpreter, I independently checked all 2,020 selected scalar occurrences across the 12 windows against little-endian saved bytes, current map offsets/widths, object bounds and canonical boolean values. Every decoded value agrees. Numeric phase/reason/operation/fault meanings were checked against the bound C++ declarations.

## Runtime result and limits

- Observer is `FROZEN` / `CALLBACK_FAILURE`, polls 115,539, runtime epochs 921. Begin called/finished/OK, pre-abort snapshot valid, abort called/returned and last step returned are true. It stopped before either 10,000-epoch or 10,000,000-poll bound.
- Trace has 64 retained prefix calls, 5,485 rejected calls, overflow true, timing fault false and first failure present. All 64 retained prefix calls returned true with low-enable/zero-pulse requests. Prefix truncation is expected and preserved; it prevents reconstructing every intervening callback.
- First failure is completed, invoked, timing-valid APPLY / SETTLE for application 921, returning false: 1,347,826 to 1,347,980 microseconds, an outer trace span of 154 microseconds. The last current callback is completed HALT / SETTLE, also returning false: 1,348,467 to 1,348,620 microseconds, span 153 microseconds. The dedicated first-failure slot survived cleanup.
- Before explicit observer abort, runtime is RUNNING with no runtime fault; its transaction is finished/IDLE with no transaction fault, but MotorGate application already reports `IO`, consumed true and invalid application feedback at token 921. Requested feedback duty is zero and motors-enabled false. This is consistent with the observer's callback-failure priority and preserved pre-abort snapshot.
- After abort, runtime is FAULT / TRANSACTION and transaction is FAULT / ABORTED. Final MotorGate is halted, unarmed, hold incomplete and fault `IO`. Its fresh attempted halt is timing-valid but **inhibition_confirmed is false**. Abort returning and software zero-duty fields do not establish physical inhibition or a successful halt.
- Maximum recorded execution and the failing transaction duration are 859 microseconds. This instrumented observation does not establish the under-800-microsecond WCET requirement. Repeated identical windows support a stable observed terminal result; they do not establish atomic cross-window coherence, electrical behavior, physical motor readiness, Linux independence qualification or a phase gate.

The exact internal `UnoQPort::settle` false branch is unobserved. Its source can reject admission, bank validity, elapsed-time checks or poll exhaustion. Outer spans of 154/153 microseconds include trace/native overhead and cannot alone prove the internal 150-microsecond timeout branch. Preserve the current bound and this failure evidence while investigating that branch; this review authorizes no retry or motor-capable run.

## Receipt anchors

Paths below are relative to `state/analysis/P7_app_motor_observe_run_raw/`; hashes were computed from the saved bytes during this review.

| File | Bytes | SHA-256 |
|---|---:|---|
| `native_invocation01.json` | 580 | `516a3bc21b6b2535667fa6f133258619e17afaf43090782a8f6550f8b9c270c7` |
| `native_inert_run01/inputs.json` | 18639 | `80ed93e18559759d9ca560ac3e2e915e19423f088c8b158be2320f5f8aa34f58` |
| `native_inert_run01/result.json` | 60754 | `4fc33583c34cd4ced88bc297098830baa7faca86c7b1d55f63fba8ecc3de21c5` |
| `native_inert_run01/final_checks.json` | 51983 | `6d94e9ef53a69d90fa0c10175ddaf5e8385e87e48ac2f35f3e7ccd24c9e2feea` |
| `retrieved_inert_run01/0001-read-saved-results/intent.json` | 21283 | `fca252eac289f18a81a05b7e1336b8be31034a3e04ef0d9101efde812e35ffcd` |
| `retrieved_inert_run01/0001-read-saved-results/stdout` | 27525 | `3bb9425f39ba71ef796308e8d94b670158f7785eded44849f7ba82515f4e1c90` |
| `retrieved_inert_run01/0001-read-saved-results/result.json` | 122 | `e9d971a9079448d88ba59c635c65b219c59a89567a568beeb378136f4559256e` |
| `interpret_run01.py` | 3516 | `d6409ff5839abcea9f4edbf5c93f8fcf7bf1c27cdc907ba2b9f778bd3d017b26` |
| `retrieved_inert_run01/decoded.json` | 63369 | `c37a3069f0e6eac6707ee579d9d82459cbe6dec685aa937feceececffe2ef5fe` |

The consumed owner and its successful collection of a runtime failure must remain historical evidence. Physical acceptance and motor-run authorization remain separate.
