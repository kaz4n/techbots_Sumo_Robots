# D182 MATCH upload adapter review

Date: 25 September 2026, Asia/Dubai.
Reviewer: separate fresh-context same-model Codex agent, read-only source and
retained-evidence review. This file is the reviewer's only repository edit.
Scope: D182 contract, tools/match_upload.py, independent new oracle and retained
first/corrected test receipts. Implementation commit72950615; corrected oracle
freeze41c596ee. No reviewer test, compiler, network, device or motor operation.

## Findings

- BLOCKER: none.
- MAJOR: none.
- MINOR: none.

The initial oracle defect is closed by the independently agreed narrow correction
recorded below. It is not a production-source defect.

## Reviewed identities and behavior

- Contract: 6e6eb4673bc1e93c528746ae35671879fe872756632364aacfe2e08b900f7fa1.
- Unchanged adapter: 777a2f29a326094c34298f07d3597eb603bf3487f8780f18c5da122bb527d9be.
- Corrected oracle: 0198dc7e0864555b7f75c490f393658945d18c4f63ecb55bc1d052625a447136.

tools/match_upload.py:9 validates exact built-in lowercase hexadecimal identifiers
and derives the closed dynamic/Immediate profile,18 file roles,14 absences,
MATCH schemas and exact precompiled upload argv. Its paths agree with the existing
native-app-v1 compilation layout. Profiles do not alias uploader dictionaries.

tools/match_upload.py:33 changes only initialization. Every execution, admission,
ownership, clock, error-retention, finalization and close method is inherited
without replacement; the historical constructor and profile selector are not
invoked. All required base fields are initialized, including inherited now()'s
latest value, descriptor/error state and the unchanged upload file-limit callback.
Falsey supplied clock/executor objects remain preserved.

tools/match_upload.py:58 uses the frozen strict checker and detached binding copy
before lifecycle dispatch. Packaged/exported byte counts and SHA256 must agree.
Both are checked against actual files during inherited admission and finalization;
binding equality alone is not treated as observed bytes. The frozen _upload is
called exactly once; returned reports and preclaim exceptions pass through.

The inherited120s child limit,180s admission/run budget,2303728-byte upload file
limit, streams below1MiB, exclusive durable output ownership and independent final
checks are unchanged. No retry, compile, capture, cleanup or new transport path
is introduced. These controls do not establish a hard total wallclock guarantee.

Live local hashes match the contract's uploader e926b7ba, support95b0344d and
helper8ba9b190 full pins. The reviewed task diff contains no changed historical
uploader/helper/source scope, firmware, established test or locked assertion.
The added .gitattributes rule only preserves this task's raw evidence bytes.

## Independent test evidence

The new test author drafted the oracle from the contract and frozen interface
without reading the new implementation. This reviewer inspected both the oracle
and the inherited tiny descriptor fixture; execution was performed by the root.

Initial oracle09a14cf5:35 methods,34 PASS/1 FAIL,1.407s. Original output remains
P7_match_upload_adapter_raw/test_output.txt, SHA256
e80958579adcc010fdedd8e8743ba7dcb34130aab5523f16c6d31183a2bc335a.
The failed globals test deep-copied Python's injected __builtins__ dictionary;
identity-based site helper instances do not preserve equality under deepcopy.
Author and reviewer independently agreed to exclude only that dictionary from
deep equality and instead assert all its keys and entry identities. Existing
module key/object identities and uploader-data deep comparisons remain intact.
Only the new oracle changed; production source and established tests did not.

Corrected oracle0198dc7e was frozen before execution. Retained
corrected_test_result.json records Python-B unittest exit0,6.736s wrapper time,
native_calls0 and unchanged source. Its referenced corrected_test_output.txt
actually reports35/35 PASS, no skips,1.384s; SHA256
59a90a29199f2c7f74de8929c58f3228c6cfbeade1643f3b55a3a8db9b9bec0e.

Coverage includes strict identifier/binding refusal, package mismatch, detached
input, all initializer fields, inherited method identity, globals preservation,
falsey callables, budgets/limits, sole dispatch and result/exception identity.
Five tiny inherited-lifecycle cases also establish exported-file admission and
postchecks, preclaim actual-byte refusal, retained postchild drift failure,
one-child failure streams and rejection of consumed output reuse.

## Verdict

PASS for D182's offline adapter implementation and host evidence. The module is
an internal mechanism; a later hash-checked outer caller still must admit source,
checked artifacts, target/boot identity, qualification and fresh identified
STAND OK/RING OK. This review provides no deployment permission, target startup
qualification, physical acceptance, human phase gate or release tag. Historical
consumed scopes and their pins remain preserved.
