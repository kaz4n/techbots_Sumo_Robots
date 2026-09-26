# D200 actual cleanup review

26 September 2026, Asia/Dubai. **PASS: the fixed D200 cleanup removed exactly
the three admitted scratch copies and preserved their retained originals.**
The root04 owner/result is consumed. Reviewer `/root/fresh_review` is a
separate same-model, reused-context agent. Under a specific read-only scope,
the reviewer made one nonprivileged saved-result retrieval/post-cleanup
verification call, then inspected the exact saved bytes and local provenance.
The reviewer performed no authentication, credential transition, cleanup,
wrapper/recipe main, firmware or MCU operation. Only the assigned retrieval,
raw-result and review files were written.

| Actual evidence under P7_motor_settle_cleanup_raw | Bytes | SHA-256 |
|---|---:|---|
| cleanup_authenticated_intent01.json | 1072 | `5f78e1dc7c68d3aaa72883360b069b8fd790b4769e5e62e198251585b0d076d5` |
| cleanup_authenticated_transport01.json | 399 | `0c260a97923e585893d5669ec4a5c987be5afc87cd95f050f805c3042b1ecb18` |
| cleanup_actual_result.json | 6370 | `05507941ebbc8f9ba88c366dbf3c762e80042654a7c8de9166637ecc4e7c7ebd` |
| cleanup_retrieval01.json | 46397 | `b7b776c998ace2c3e8e44e6208db298298c935b587ad5bbdbf172f843aa35c06` |

The actual intent binds the unchanged root04 wrapper `13f33327...`, source/host
review `1ebd7342...`, final stage review `7e0181e5...` and independent staged
verification02 `2c7a1ad2...`. Its fixed command uses no-clobber redirection,
sudo -S -H, absolute /usr/bin/python3 -I -B and the exact root04 wrapper/result
paths, with a 70-second bound. The transport records one native invocation
from 06:52:01.922913 to 06:52:02.850410 UTC, return0, empty stdout/stderr and no
first error. The separate 605-byte local input-failure receipt
`8287a1e68194f58ab77e54e6de22f11ee2112b9d825844cca18ace309e7ca960`
records EOF before any credential or subprocess, with zero native invocations.
It is not a failed native cleanup or a second native attempt. Authentication
material was not inspected or retained by this reviewer; the saved command
contains no credential value.

The retrieved raw file is byte-identical to the descriptor-read base64 payload
in the independent receipt. It is a regular, single-link, UID/GID1000 file at
stage device66341/inode272573, result inode272577, and has stable complete
before/after stamps and matching hash on close/reopen. Its exact outer schema
is `d200-authenticated-settle-cleanup-v1`; the nested schema is
`d200-exact-settle-scratch-cleanup-v1`. Both have the expected complete field
sets and success status. Strict local JSON parsing found no duplicate keys or
nonfinite values. Parsed cleanup_stdout equals cleanup_result exactly;
cleanup_returncode is0, both first_error fields are null, and the privilege
drop error list is empty. This acceptance checks the actual schemas and full
evidence rather than relying on transport success or the wrapper's narrower
status predicate.

The actual removed list is exactly the sorted admitted set:

| Scratch basename | Bytes | SHA-256 |
|---|---:|---|
| app_motor_observe.ino.bin-zsk.bin | 95360 | `85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c` |
| flash_sketch.cfg | 680 | `38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c` |
| zephyr-arduino_uno_q_stm32u585xx.elf | 2303728 | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

Total payload removed is 2399768 bytes. The actual pre-removal directory stamp
is device34/inode1172; all child full stamps and hashes match independent
verification02 exactly. The result records directory_removed=true and
originals_unchanged=true. The package is the retained D193 observer image
uploaded in D195, not D198's new image. The checked cleanup source permits
only these three sorted unlinks followed by empty-directory rmdir; no recursive
or fallback deletion is introduced by this invocation.

The source pins and one-occurrence private projection in the actual receipt
match the reviewed recipe/helper and projected hash `96d1197e...`. Initial
real/effective/saved UID and GID triples are all 0. Each of exactly three process
observations records before/after UID/GID triples[1000,1000,0], during UID
triple[1000,0,0] with GID unchanged, no error, and a result identical to its
corresponding nested use_check. Each scan reports 167 process names and 3
same-user handles. The reviewed control flow restores and verifies Arduino
credentials before each mutation. Final UID and GID triples are both
[1000,1000,1000], with no permanent-drop error. Thus the receipt records removal
of the saved root identity in the cleanup process. The inherited limitation
on other-user FD coverage and races remains; these observations are not a
global process/filesystem lock or clearance for a later operation.

The independent retrieval ran once from 06:53:15.644361 to 06:53:16.066865 UTC,
return0 in 0.422 seconds, with empty stderr and no host or remote first error.
It uses a 24625-byte program, SHA-256
`0226fd90d810f34f13ffb52aeb3ca5b3ab3a2217e61d0e2762961191819ee0e2`,
28036 command units, Python -I -B, the 55-second alarm and 70-second outer bound.
The 15620-byte raw stdout hashes to
`564e816d9abb07bf711ee1ed96f62e031e4089afe01fdf03afd59f952bd43eac`.
All six remote closing checks PASS: stage/result reopen, scratch absence
reopen, retained-original reopen, board identity, credentials and root
descriptor close. Local source/ADB input closure PASS.

Actual post-cleanup verification found exactly the same three staged source
files plus the new result. All staged-source full stamps and complete hashes
equal verification02; source totals remain 50664 bytes. The stage's identity,
owner and 0700 mode are unchanged, with its expected timestamp change from
result creation recorded rather than confused with earlier full-stamp equality.
Both fresh no-follow checks find /tmp/remoteocd absent. Each retained original
was independently opened, hashed, closed and reopened; all full path stamps,
descriptor identities, lengths and hashes equal the pre-cleanup verification.
The original package remains at app-motor-observe-static01/build, and the
configuration/loader remain in the installed Arduino core paths. Full board
identity is unchanged throughout, including boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. The independent observer stayed at
real/effective/saved UID/GID1000 before and after its call.

The earlier verification01 observer defect, failed receipt and separately
authorized one-loop correction remain preserved; this actual review does not
erase or reinterpret them. D200's narrow cleanup objective is complete and
its owner must not be reused. No further cleanup or retry follows. No firmware
was uploaded, reset, run or read by this cleanup/retrieval, and no motor fault,
physical acceptance, RAM/WCET qualification or human phase gate is resolved
by this storage result.
