# D196 cleanup source and host review

26 September 2026, Asia/Dubai. **PASS for the fixed prepared cleanup; no open
material finding.** Reviewer `/root/fresh_review` is a separate same-model
reused context. Review used local source, contract, fixture and receipt reads,
hashes and static comparisons. No subject import, tests, credentials, native
tools or board calls were performed by the reviewer. Only this review was written.

| Prepared input | Bytes | SHA-256 |
|---|---:|---|
| P7_app_motor_observe_cleanup_contract.md | 12460 | `7258230a63f48e09401186b8ad3bed09f958006909610cea835926427a3609f6` |
| cleanup_remoteocd02.py | 7735 | `1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a` |
| cleanup_root03.py | 9606 | `a089cc3bac9d8df3ffe53947e22b1bb4ffa139a733c7ebb1f5ba62e6d5bd804f` |
| tests/tooling/test_app_motor_observe_cleanup.py | 14429 | `18b150d239ba34aca30ce8b436036532a15e2c5aacb53ccf1166f51a68a831c0` |

The reviewer independently applied the contract's four ordered/count-checked
recipe substitutions and seven wrapper substitutions to the pinned original
bytes. Both new files match exactly; no operational change exists beyond that
recipe. Original recipe `23ef85ae...`, wrapper `4192f23e...`, helper `8ba9b190...`
and prior consumed-success receipt remain unchanged. The retained private
missing-link projection has one occurrence and produces 7732 bytes, SHA-256
`b4bdb4dd7cbe6ed2ff534a033507ad2c080c5b789dc02716f4189f557a34c0c1`.

The saved inventory `20db3c25...` independently agrees on boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, UID1000, directory device34/inode869
and exactly three payloads totaling 2399736 bytes. Its package is the retained
D190 app_motor_fault image, 95328 bytes / `deb40317...`, also bound by the old
artifact receipt `57b98c00...` at both build and export paths. The cleanup uses
the build original; it does not substitute the new observer image. Configuration
and loader originals/pins remain exact. Inventory is historical read-only
content evidence, not fresh process-use, staging or deletion evidence.

Source inspection confirms unchanged checked source ancestry, descriptor
identity, single links, bounded reads/hashes and all-descriptor closure. Initial
admission requires UID/GID triples all0, isolated Python -I -B and no arguments.
The recipe runs with real/effective UID/GID1000; only the process observer
temporarily sets effective UID0 and restores/verifies UID1000 in finally. Missing
cwd/FD links reach the outer surviving-PID check, so a surviving unreadable PID
is not silently skipped. Process names, same-user handle checks and their bounds
remain exact. The stated other-user FD limitation and observation races remain;
root observation is not a filesystem/process lock.

All three retained originals are hashed before mutation and again at closure.
Each of the three sorted unlinks retains the process-use, board identity,
remaining-content/full-child-stamp and named-directory checks. Only the emptied
fixed directory may be removed, followed by fsync and absence verification.
The 55-second alarm remains. Partial stdout, removed names and original errors
survive failures; terminal credential-drop errors are independent and prevent
success. Both permanent GID/UID triple drops are attempted following initial
root admission, including source or cleanup failures. No recursive cleanup,
fallback target, native-name exception or broader privileged operation is added.

The independent oracle froze before its author read the new subject bodies.
Its checked private fixture projection changes only metadata; static comparison
retains all 37 original methods and all 147 assertion calls. Ten additional
methods cover exact full source/projection bytes, preserved historical inputs,
new stage/dependencies, old basename/inode/payload/hash/path refusals and fixed
retained originals. The original credential, descriptor, process, first-error,
partial-deletion and privilege-drop fixtures execute on Linux. The supplements
run on both platforms. No material fixture defect was found.

| First host receipt in P7_app_motor_observe_run_raw | Observed result | SHA-256 |
|---|---|---|
| test_cleanup_linux01.json | 47 PASS, no skips; exit0, unittest0.365s | `340575f564151338ec8ab37ac3f56d31d8c5b645e64f299b2be1845bec3dd111` |
| test_cleanup_windows01.json | 10 PASS, 37 explicit Linux-only skips; exit0, unittest0.047s | `d230c74feb1297e7f53715064693d8469e237e9742a82c9e6398937915780508` |

Both commands use Python -I -B and verbose unittest discovery. Independent
freeze is `49587dc8427eb33dac95cc589834c4bbd5bd33c7562d441a0ec5f65145374b1a`;
first-run freeze is `965a10171e6e76eec132df634cecfdec296a4c939a43b0079d69da1b5bb15c1f`.
The reviewer checked every receipt's before/after set and independently hashed
all 12 current pins: unchanged. There was no failed first run or repair.

This PASS supports separate fresh staging/admission of only the three fixed
files in cleanup-app-observe-root03 and exclusive result_root03.json. Actual
stage identity/hashes, fresh board/scratch/original observations and one bounded
specifically authorized invocation still require separate evidence. No retry
or owner reuse follows from this review. Host fixtures establish no deletion,
authentication, firmware operation, physical acceptance or human phase gate.
