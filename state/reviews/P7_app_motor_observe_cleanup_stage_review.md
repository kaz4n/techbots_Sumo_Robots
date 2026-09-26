# D196 actual staging and invocation readiness

26 September 2026, Asia/Dubai. **PASS for actual staging and the single bounded
invocation described below; no material finding.** Separate same-model reused
context reviewer `/root/fresh_review` read local receipts and decoded their
embedded programs as data. No subject execution, credential access or board
call was performed; only this review was written.

| Receipt in P7_app_motor_observe_run_raw | Bytes | SHA-256 |
|---|---:|---|
| cleanup_stage_intent01.json | 20298 | `65e4fa190919f72c533ca3fb3962f22b4ef426054db298f1cd30b67e4e111ad1` |
| cleanup_stage_result01.json | 2071 | `acd7328bcf83df35bdcf1daef68f94a978d873c91353d610abb7249606e05c8b` |
| cleanup_stage_verification01.json | 20295 | `d794fc0db1f3f57e3f4c9d1f76ac2f28a7fe6be96af19c0e8b289832dd649154` |

The staging intent predates completion. Its bounded program checks the exact
three source digests before loading only helper/recipe definitions, verifies
full board identity and retained originals, and inventories the fixed scratch.
It creates cleanup-app-observe-root03 exclusively, writes each source with
O_EXCL/O_NOFOLLOW, flushes/fsyncs it, rereads exact bytes and verifies ordinary
UID/GID1000 single-link files. It requires exactly three children, fsyncs the
directory/parent, and rechecks originals and identity. The reviewer independently
decoded the inline source packet and compared all three full byte strings to
the frozen local files. No cleanup/main/process scan or elevated call occurs
in either staging program.

Actual staging returns0 with empty stderr and STAGED_CHECKED_NOT_EXECUTED.
Stage identity is device66341/inode271887, mode0700, UID/GID1000. The separate
read-only verification also returns0 with empty stderr and matches that stage,
all three exact source pins, ordinary ownership/link counts and exact child set.
result_root03.json is absent. Both observations match the complete expected
arduino/Linux/aarch64/Python3.13.5 identity and boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Scratch remains device34/inode869 with
the three prescribed D190 copies; all retained originals hash correctly.

Together with source/host review `35aa618c...`, this supports the specifically
admitted D196 execution under the user's continuing cleanup authorization:
one sudo -S -H invocation of absolute /usr/bin/python3 -I -B and the fixed
staged cleanup_root03.py, credential supplied only through stdin, exclusive
result_root03.json redirection and a70-second outer bound. The wrapper's exact
source/identity/content/use/credential checks must still run; staging does not
replace them. No extra elevated command or general privilege follows. An
authentication error, partial deletion or uncertain transport consumes this
attempt and requires preserved evidence and separate assessment, not an
automatic retry or overwrite.

This is readiness and source-staging evidence only. At this review point no
authentication or cleanup result has been supplied, so deletion and retained-
original closure remain pending. It authorizes no firmware upload, MCU capture,
motor run, physical acceptance or human phase gate.
