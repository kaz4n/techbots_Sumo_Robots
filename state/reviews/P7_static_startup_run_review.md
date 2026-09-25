# One inert startup run: pre-run review

25 September 2026, Asia/Dubai. Bounded same-model review reusing D155 design/code
context. Read-only local inspection; no native command or new measurement.
The pinned D155 implementation review26fcf2f7 remains unchanged.

Reviewed plan SHA256
`1702591a0eec1bee71b35440377d01f46343047ea975f48177951c2f65b71931`
and native_run01_scope.json SHA256
`c7447815d44d082c9e8b70f24640a879e6b9bf5ddf8a1ef4e55a7fab76f1ae62`.
All five scope file digests match their actual launcher, independent tests,
contract, design review and code review. Launcher remains6f86e645.

**PASS for the stated single inert scope; no open material finding.**
The coordinator must record D156 and commit this concrete scope before launch;
the CLI reviewed-head must identify that actual clean commit. The launcher
must still pass fresh local/packet/dependency/prerequisite admission. This
review neither bypasses those checks nor asserts an observed current boot.

The fixed target is ADB2629958581, UID1000/aarch64, expected boot
6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6. Operation static-fcddbd8e-run01 is distinct
from retained artifact run f0220228320c4b2aa20c3e5e8264c813. Source is the full
fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2 digest.
Rechecked pinned D144 receipt0017 SHA3c8cc9df: successful static compile, exact
target/source paths, C and C++ flags MATCH=0/MOTORS_ALLOWED=0. Raw selector
bd03c2e7, flat93096B/5f08afe0, ELF5cc2dfde and ELF-derived loader reference
263680B/e9322826 agree with D155's fixed bindings and original FileRecords.

The existing user-reported bare-board permission and D051 delegated engineering
choices support this inhibited image only, consistent with the current handoff
and D137 context. No STAND/RING, motor-capable permission or physical acceptance
is inferred. Consumed D144/D118 scopes are evidence identity, not a new grant.

Six exact forms produce14 dispatches only on a clean path: four Linux-file
checks, upload, four checks, capture, four final checks. The prior local-only
composition has zero dispatches and28068/24981 UTF16 upload/capture units.
The one upload explicitly includes the reviewed recipe's loader/sketch program,
intrinsic reset,100ms wait and0xCAFFEEEE activation write to0x40036400. There is
no added reset/activation/rebuild/install, privilege change, recovery or retry.

Only known clean upload plus clean intermediate checks admits the separate
18-read/713656B passive capture with flash brackets and >=2s sample separation.
Host195s/630s and remote180s/600s budgets retain the bounded child/reap limits.
Failure or unknown upload suppresses capture; permitted file-only final checks
remain independent and evidence/claims stay consumed. The exact remote upload
and capture paths and exclusive local native_run01 path are correct; the local
output was absent at this review. No raw binary copy is added.

Collection completion remains separate from decoder progress/fault/no-progress
and from MCU quiescence, live memory/WCET, physical gates or production static
admission. Actual execution and its result require a separate evidence review.
