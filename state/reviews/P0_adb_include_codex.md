# P0 ADB and include repair scoped review, 2026-09-22

Coordinator records p1_next_task_audit's returned read-only review. Reused separate
Codex context, not newly fresh/cross-model/full gate. No reviewer hardware command
or source edit. Verdict PASS; no open BLOCKER/MAJOR/MINOR in this scope.

ADB commands select an explicit serial, quote remote argv as one POSIX command,
use argv-only local processes and DEVNULL stdin, and preserve existing compile,
startup, source-hash and motor restrictions. Failed sync/compile cannot upload.
Two MINOR issues found and fixed before board mutation: all-slash remote roots
were accepted, and ADB preflight exit1 did not stop potential transport retries.
New independent tests cover both fixes. Remote missing-rsync127 stays explicit.

The first real target compile failed on host-only include paths. Eight core
files changed only sibling includes and ../config.h; no logic/config/test change.
New staged-core tests reproduced ten compiler failures before repair and both
pass afterward. Complete23-file maps were checked against5ecc861: only these
eight files differ; all other15 files per sketch remain byte-identical.

Approved hashes:
- matrix72214f8aa1b6d84e21d2dc8a568ea01adb5fe0295f3f3d0f362e8696d2543e8f
- timing3de6da69f44c2317b82b246b0fe8e324e1001a531b4741c09e511269fb24e7f4

Root initial tooling72/72 exit0 preceded include changes. Reviewer's next74-test
run failed7 upload-fixture subcases solely because old inert hashes correctly
rejected changed source. After exact review/manifest refresh, independent final
full discovery passed74 tests in50.553s, exit0. Staged-core cases passed in both
of those74-test runs. No assertions were weakened. Root host rebuild also
passed CTest1/1. Target builds, installed dependencies and runtime evidence are
separate receipts, not inferred from these controlled substitutes.

Candidate MEM-AP-only debug configuration reviewed without execution: no MCU
reset/halt/flash/CPU target/hooks. Readout still requires exact sourced helper
inspection, loader/sketch identity and bounded address/capture validation.
