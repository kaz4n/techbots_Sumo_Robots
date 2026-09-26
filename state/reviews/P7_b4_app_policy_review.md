# D213 B4 application policy review

FINAL PASS, 2026-09-26. No material finding remains. Separate source/oracle and saved-host review by a same-model reviewer with reused context; not human or cross-model review. The reviewer executed no subject, test or device operation and wrote only this review plus the explicitly assigned host closure.

## Checked identities

| File | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_b4_app_policy_contract.md |3996|`1d6ffa2f49ba5a7925e1fbfc70a80a73a22dc0b5cc04a936b318eb97159d52c7`|
| tools/b4_app_static_policy.py |4055|`aadccdbb0a92338a90a789251f691a42e029c7f73b312b638b85d04c5d2d4ddf`|
| tests/tooling/test_b4_app_static_policy.py |44244|`ce5e915a76eb8649da078748d0060d9b33b7e1344d910aa88e2ea01f00a8137c`|
| state/analysis/P7_b4_app_policy_oracle.json |30791|`5cdcb360e9f4b114d0037233ada0448625ec98f667a97921e230290c6d009dc6`|
| state/analysis/P7_b4_app_policy_raw/coordinator_freeze01.json |2867|`d850b9dacced1a59cf6b4216f11ed019863d47e75266cd06338acf6defa3ab6e`|
| state/analysis/P7_b4_app_policy_raw/host_closing01.json |11226|`acaf2f32e9690379ee03c734a598fabf78a4a08ee4a04bababaf3159cdf6a914`|

The implementation seal is550 bytes / `0ff4092a83e148f709a1cc364a8e8c9439c35cb95abc4eeee4fc64091de8f30e`. All12 oracle inputs and16 coordinator inputs independently match after both runs.

## Source and oracle findings

The three public validators require keyword-only motors_allowed and snapshots, without defaults. Exact integer0/1 admission runs before snapshot inspection, hashing or private execution. Snapshot admission requires an exact dict, five exact ordinary string keys and exact bytes values; every length/hash is checked before exec. The copied mapping contains immutable bytes and is newly constructed on every call.

The unchanged pinned D187 adapter is executed into a fresh private namespace. Its checked-source seam is redirected only to the validated snapshots; app.ino, the static/default FQBN, exact ten flags and seven identity aliases are the only expectation changes. Retained metadata and artifact validation bodies receive the original raw text, paths and byte objects. The84-property,24-name and5-old-flag counts remain checked. Fresh private dependency namespaces and per-call reports prevent M0/M1/M0 state leakage. There is no new filesystem acquisition, subprocess or transport; inherited read-only module-location resolution remains allowed. Artifact output changes only the specified status and adds the declared motors_allowed field, retaining the full historical report.

The explicit65-method selection comprises seven snapshot cases, sixteen metadata cases per profile and thirteen artifact cases per profile. Both canonical profiles are positive; opposite/coherently replaced profiles, reordered/missing/extra/duplicate macros, changed project/link/startup metadata and unsafe paths are actual changed negatives. Snapshot shape/type/hash mutations fail before private exec; the first-exec mutation hook checks that caller-map changes cannot replace admitted bytes. Sentinel historical modules, M0/M1/M0 calls and mutated returned dictionaries check isolation. Full report equality, forwarded-object identity, TLS tuples, every image, layout/initialization and both package formats retain meaningful checks.

All28 adapted historical method identities and direct assertion counts reconcile. Five historical filesystem dependency cases are explicitly mapped to the new byte-snapshot boundary; their original33-case suite remains unchanged. Filesystem symlink acquisition is not claimed for this bytes API. One read-only audit initially applied a uniform method-extraction convention; the frozen original records use whole lines plus LF and current records use AST source segments. Applying their actual conventions reconciled every record without changing source, oracle or tests.

## Saved host acceptance

Both first serial runs passed65/65, with zero skips, failures, errors or retries. Linux recorded84.402s unittest /99.128233s outer; Windows58.225s /58.591222s. Each used Python-I-B and the600-second limit. The closure independently records all130 ordered outcomes, both intents/results and four raw streams with exact hashes. Stdout is empty on both platforms. Frozen inputs are unchanged.

Windows receipt and actual directory both show an empty isolated temporary owner, which is retained. Linux used /dev/shm; its receipt has null temporary inventory. No extra Linux scan was requested for these pure-data tests, and this review does not claim a measured empty Linux directory.

This accepts host-only policy software. The M1 artifact field declares the validated selection; it does not prove compiler origin, target loading, runtime state or motor permission. Separate build/deploy admission, actual artifacts, physical grants and fresh STAND OK for a particular M1 run remain required. No firmware/configuration/locked-test change, target action, commissioning measurement or phase gate follows. Writes stopped after this seal.
