# D193 fixed static observation compile workflow

26 September 2026. A new small launcher privately projects the existing checked
D188 caller, policy and remote observer onto `app_motor_observe`. It retains the
original disk bytes and hard pins, exact finite substitutions and projected
hashes, fixed static/default/MATCH0/MOTORS_ALLOWED0/probe1 flags, original guarded
compiler execution and independent closing checks. Historical tools, source,
validators, tests and consumed owners are unchanged.

Source: `tools/compile_app_motor_observe.py`, SHA256
`70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827`.
Contract: `P7_app_motor_observe_compile_contract.md`, SHA256
`0301726f47c0c438a7984ddd232f81c4891c511651ba81a986b15f5ef91dbfb4`.
Three original/projected full hashes and literal counts are in that contract.
No generated tool copy is installed on disk; the remote packet contains the
verified projection and the original unchanged lower-level dependencies.

## Review findings and preserved first evidence

A separate same-model reviewer found a potential regular-file-to-FIFO race in
the initial local bootstrap reader, before execution. Source70e1 adds nonblocking
open where available and descriptor type/identity admission before reading;
original error precedence and final path/descriptor checks remain. The reversible
patch and original e7b8582b identity are in `bootstrap_review_fix01.json`.

Independent oracles were derived from the contract and historical public tests,
without reading the new launcher body. The first caller oracle4d2c634a passed
58/58 Linux methods. Windows passed55, skipped2 platform cases and errored once
while constructing a symlink without privilege, before the subject was called.
Both independent author and reviewer agreed this was a fixture issue. Commit
9eb8c9c7 preserves the original source/oracle/receipts. No subject code changed.

The corrected oracleae42938c splits the mixed link case: all three real hardlink
refusals execute on both platforms; real file/parent symlinks execute on Linux.
Only Windows error1314 during symlink construction produces an explicit skip;
other errors and every original refusal assertion remain. The reversible patch
and new freeze are `caller_fixture_repair01.json` and
`caller_independent_freeze02.json`.

Review also identified that caller packet checks alone did not execute the new
remote/adapter projection. Supplemental frozen oracle897ae6e4 reuses14 unchanged
remote assertions,15 metadata assertions,3 deep artifact assertions and3 binding
checks. They execute the actual projected remote/adapter against controlled
files and synthetic ELF/package data, preserving lower-level validators.

## Actual host evidence

HOST-VERIFIED:94 Linux methods pass, with no skips;75 Windows methods pass
and19 explicitly platform-limited methods are skipped. No subject code changed
after the pre-execution bootstrap repair.

| Suite | Linux | Windows |
|---|---|---|
| Corrected caller | 59 passed, no skips | 56 passed; 3 explicit platform skips |
| Projected remote/adapter | 35 passed, no skips | 19 passed; 16 Linux-only descriptor cases skipped |

Raw command/output/status/time/pin records live in
`P7_app_motor_observe_compile_raw`. The corrected final freeze includes197 source,
contract and oracle pins. The supplemental first run checked196 pins; its code
and dependencies are unchanged after the caller-only fixture split.

Coverage includes fail-before-I/O CLI/import behavior, exact original and
projected bytes, plain paths/link/reparse/drift/bounds, real FIFO swap refusal,
read/close error precedence, private namespace isolation, exact manifest/staging
and source reuse/refusal, fixed command flags, installed prerequisite failure,
compiler timeout/nonzero, result-write failure, independent closing, malformed
metadata/packets, actual corrupt artifacts, loader/TLS/export drift and rejection
of old project/owner/schema/bundle identities. The actual source packet's Windows
command composition fits the unchanged30,000 UTF16-unit limit; oversize commands
are refused before dispatch. All process/transport endpoints in these tests are
controlled substitutes. No native compiler or MCU runs within the tests.

Separate same-model source/host review is **PASS**, with no open material
findings: `../reviews/P7_app_motor_observe_compile_review.md` (`4d5b14ad`).
The reviewer independently inspected actual receipts and exact source hashes.

## Prepared actual scope

The separate read-only admission observed board2629958581, UID/GID1000, expected
Linux/Python identity, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 and matching CLI,
boards/platform hashes. Target free space was13,981,831,168 bytes and the new
remote owner was absent. This observation is not a new firmware run.

Prepared manifest `inputs_static.json` has SHA256
`aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e`:
128 inputs,109 source files,107 staged destinations/775,376 bytes, source
`3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0`.
It pins the new launcher/contract and original dependencies, with no self-hash
cycle. Local/stage/native owners are unused. Separate scope review is
`../reviews/P7_app_motor_observe_compile_scope_review.md`; its conditions are
complete host review, committed clean reviewed HEAD and live caller admission.

Native compilation remains pending in this host record. It must use the new
owner once, retain partial failures and complete all closing checks. A successful
compile supplies structural/artifact evidence only. New actual ABI/entry and
finite capture bindings precede any upload or MCU observation. The last firmware
remains D190's halted four-epoch inhibited image; original IO fault, production
memory/loading, actual recorder lifecycle and physical/human gates remain open.
