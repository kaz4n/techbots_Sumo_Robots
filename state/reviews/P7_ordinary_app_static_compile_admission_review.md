# D208 ordinary-app static compile admission review

26 September 2026, Asia/Dubai. Independent review-only agent.

**FINAL PASS, conditional on a clean committed reviewed HEAD and successful
local check-only for that exact HEAD before the single compile-only execution.**
No open material admission finding remains. This review accepts the saved
two-call read-only admission, current ordinary manifest and fixed native scope;
it does not claim an ordinary target artifact or a completed native compile.

I read the current project rules, D208 adoption and adjudications, handoff and
source/host reviews. The date remains before the 1 October code freeze and
3 October competition; calendar milestones do not create physical acceptance
or human phase gates. Review work consisted only of local reads, hashes,
JSON/AST literal inspection and independent byte/set calculations. No project
module, subject, oracle, test, transport, compiler or native program was imported
or executed. Only this new review file is written; previous reviews are immutable.

RAW denotes `state/analysis/P7_ordinary_app_static_compile_raw`.

## Evidence and exact binding closure

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| RAW `admission_preparation01.json` | 4892 | `5c775095995f7515da6496b1b7f089c556933339bc9588221add612a8725019a` |
| RAW `admission_intent01.json` | 754 | `7c559f6ed69579513706fa699fd1609553a75f7cc3c0f97e243788bbbada85c3` |
| RAW `admission01.json` | 64692 | `3dce8640708944cfcc4a32c38dc805191731e032a1d0c581ebfde26b254548a9` |
| RAW `inputs_static.json` | 12940 | `a5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7` |
| RAW `manifest_preparation01.json` | 15551 | `7dcc86b56e7326e4bc6c0eb86d2bf128ae08eb1a70bfc91a130ecf03412de4f1` |
| RAW `native_scope01.json` | 6216 | `6a17b23a9d6d68cd75e65c846aaeebf9868d3c30865e3e5d029c9fa1f5f1a5e1` |

The scope has exactly these fifteen roles, each resolving to its intended current
file, with no duplicate target, extra file or omitted role: launcher, contract,
contract_review, caller_review, adapter_remote_review,
readonly_admission_review, derivation, implementation, independent_freeze,
coordinator_freeze, host_closing, manifest, manifest_preparation,
admission_preparation and admission_actual. I independently recomputed all fifteen
byte-length/SHA-256 pairs, all fourteen admission-preparation bindings, all 191
coordinator03 pins, all 186 independent-freeze03 inputs and all 150 proposal
inputs. Every binding matches current bytes.

In particular, the launcher remains 26136 bytes /
`40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89`;
the adopted contract/data remain `06cd96f1`/`09f0d107`; concrete implementation
identity receipt remains `d81c0e82`. The final source/host review is exactly
27777 bytes / `87a81920b400154dbdd01d13fac163592ec716f2402bee0a3410db89b349902a`;
adapter/remote review is 19198 bytes /
`e69387e0aa28f993972c4eaf6bf8ffcd236a70fb076cf59f638afc1c94d4a78c`.
The prepared read-only review is 7987 bytes /
`40fc337d9001e8cecab0bb7281d7d180ef0e1da3f1c2612266dd66946cda97d5`.
Those immutable reviews close source/host and preparation; this file adds the
actual admission and native-scope disposition. Original host failures and both
bounded oracle corrections remain retained, with corrected Linux 135 PASS and
Windows 111 PASS/24 Linux-covered skips already closed by `host_closing01.json`.

## Actual two-call board observation

The receipt starts at 15:32:05.390186 +04:00 and finishes at
15:32:06.460517 +04:00. Its exclusive intent retains the initial FAILED status,
empty command list and exact opening local snapshot; this is the expected
pre-dispatch intent, not a hidden failed device attempt. The final receipt is
PASS with exactly two commands, no first error and no closing error.

I independently decoded the shell argv and required the complete submitted
program bytes to equal the saved reviewed files. The full observer is 10221
bytes / `051ca7806d85f2ac0fa28da91b38d666c4eb73dea1374eee45e1b0472210f5ef`;
the closing observer is 1912 bytes /
`405913a787fcd41f801c108503bb8fc5e4bae07abb4a3af71af791a680ac981d`.
The first is exactly the accepted D203 observer after its one attempt-name and
one scope-label replacement. Extracting the old closing body from D203's actual
saved argv and applying its one attempt-name replacement reproduces the second
body exactly. No new operational code or weakened check is introduced.

Both argv vectors select only board serial `2629958581`, `shell -T` and
`/usr/bin/python3 -I -B -c`. Independent Windows command-length reconstruction
matches 12767 and 2490 UTF-16 units, below 30000. Each has a 75-second outer
bound; the reviewed remote alarms remain 45 and 60 seconds. Actual elapsed
times are 0.568689300 and 0.338270000 seconds. Both return zero with empty stderr,
without a timeout/error field, and timestamps establish observer-then-closing
serial execution. Raw base64 bytes exactly equal their readable streams and
decode to the stored observed objects; no normalized summary substitutes for
the raw replies.

| Raw reply | Bytes | SHA-256 |
|---|---:|---|
| Full observer stdout | 11324 | `a9c8a843358e45b3e48040039da7e47582dc0b378741fafd96faae38b558b4bc` |
| Closing observer stdout | 301 | `706e1b2fda63e57b3572f94ae6f2db4042e669d747f8c75d9e5e74fb4e12892f` |

The full returned identity and closing identity both exactly equal the packet:
UID/GID 1000, user `arduino`, home `/home/arduino`, Linux
`6.16.7-g0dd6551ae96b`, aarch64, Python 3.13.5 and boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Four-entry UID/GID lists and real,
effective and saved triples are all 1000; opening/closing credential objects
agree. The inherited file-size limit is unlimited. The two recorded ancestry
stamps are directories, and new remote-owner absence is observed before and
after the full observer, then independently by the narrower closing call.

The full observer returned exactly the packet's 28 installed paths, every
expected SHA-256, positive bounded byte count and complete seven-field identity
stamp. Each stamp is regular-file mode with size matching the returned bytes.
This includes compiler inputs, linker scripts, loader/TLS, CLI initialization
and builtin prerequisites. Legitimate installed tool hardlinks remain governed
by the accepted observer; the launcher's one-link source rule is not imposed
on them. Descriptor before/open/read/after checks remain in the exact submitted
program. No additional closing 28-file reread is claimed: the second program
has its historically narrower CLI/identity/resources/conflicts/absence scope.

The actual resource values are root 2935255040 and home 13913214976 free bytes,
both above 1073741824, with tmp 1921687552, MemAvailable 3227373568 and
SwapFree 1924100096 bytes. There are 164 observed processes, no recognized
compiler/debugger/uploader conflicts and no departed-PID entries. The closing
reply retains home 13913214976, no conflicts, the same boot/UID triples and
CLI hash `b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433`.
These are bounded observation-time facts, not a reservation of future resources
or a claim that arbitrary unrecognized process names cannot exist.

Both local snapshots record all 191 frozen inputs unchanged, both compile
owners absent and free space 7399079936 then7399075840 bytes, above 134217728.
I independently rehashed the current local ADB file without invoking it and
matched `e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982`.
Current lexical checks still find both local compile owners absent. The actual
admission consumes its own intent/result only; it claims no compile owner and
performs no source staging, query, compiler, upload, reset, MCU access, sudo,
installation, process termination or cleanup.

## Ordinary manifest and real-helper admission

I independently enumerated the current plain `src` tree, checked its types and
absence of symlink/reparse entries, and reconstructed the ordinary destination
rules directly from the adopted mapping. The inventory has exactly 105 files
and 764405 bytes; the mapped set has 104 unique, case-distinct destinations and
the same 764405 bytes. Only `src/app/.gitkeep` is omitted from staging while
remaining checked by the manifest. `app.ino` is present; sketch.yaml/yml/json
are absent; all four reserved sketch-local entries are lexically absent.

Every calculated destination source, byte count and SHA-256 matches the adopted
data and the manifest-preparation mapped hashes. Sorting destinations by Path
and hashing UTF-8 destination, NUL and exact file bytes independently reproduces
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
The exact staged directory set is `src`, `src/app`, `src/core`, `src/hal`.

I independently reconstructed REQUIRED from the original caller's literal
metadata plus the reviewed ordinary caller/contract and hard-pin extensions.
It is exactly the twenty-name preparation/contract set. Its union with the 105
source names is exactly the 125 manifest names, with no diagnostic bench input
or count-only substitution. All 125 actual file hashes match. All inherited
hard pins match as well. Manifest fields/schema, source hash and observed boot
match the adopted ordinary scope; the file itself matches the preparation's
12940-byte identity.

The coordinator's saved preparation records execution of the real pinned
`match_deploy.app_source_hash`, the snapshot mapper and actual local
`admission()` with the identical 9044ebbb digest, successful local admission,
zero new board/query/compiler calls and absent stage/native owners. I inspected
the actual projected admission method as literal source: it verifies the exact
manifest/name union, every snapshot/hash/hard pin and checked wait, then loads
the checked pinned `tools/match_deploy.py` bytes and requires the real
`app_source_hash(self.root)` return to equal the independently mapped source
on every admission. It neither substitutes a stored return nor calls the
match-deploy operational entrypoint. This review accepts that recorded local
execution and corroborates its data and real call path; it does not claim a
second reviewer execution or actual stage creation. The inherited later
`board.stage('app', attempt=ATTEMPT)` and source-hash check remain future native
lifecycle obligations.

All ten relevant macro defaults still read 0 and all seventeen APP_GRANT
declarations read 0U in the pinned config. Ordinary app.ino and
configuredSetupGrants bytes remain unchanged. The distinct 9044ebbb ordinary
source is not the consumed 4bc3a2e6 diagnostic source or evidence of an ordinary
runtime result.

## Fixed operation and final conditions

The fifteen-role native scope binds app.ino, static FQBN
`arduino:zephyr:unoq:link_mode=static`, default startup and exactly
`-DMATCH=0 -DMOTORS_ALLOWED=0` in the checked profile. Probe remains the pinned
zero default; no diagnostic or alternate-profile define is appended.

Attempt is `ordinary-app-static01`; local output is RAW `native_static01` and
stage owner is `build/stage/ordinary-app-static01` with child `app`. Remote
attempt owner is `/home/arduino/sumox26_codex_build/ordinary-app-static01`;
canonical source is
`/home/arduino/sumox26_codex_build/9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a/app`.
Canonical source has not been staged or admitted by this read-only observation.
Its future reuse remains conditional on complete plain-ancestry, single-app
child, exact source/hash/directory equality; there is no repair permission.

The scope preserves exactly one 60-second expanded-properties query, one
720-second compiler with jobs 1, 5-second reap, 30000-unit command bound,
128MiB local and 1GiB board minimums. All inherited preflight, checked pushes,
metadata/CLI prerequisites, exclusive ownership, durable intent, raw streams,
eight-artifact validation and independent remote/local closing checks remain
required. Compiler exit zero alone is insufficient for COMPILE_CHECKED. Any
claimed, partial, failed or uncertain owner is consumed; no retry/reuse follows.

Final PASS is conditional on committing the complete reviewed D208 evidence,
auditing current bytes against these pins, obtaining a clean reviewed HEAD and
passing the exact local check-only for that HEAD. Writers must remain stopped
through the single native attempt and closing evidence. The manifest records
its earlier preparation HEAD; that value does not replace the final clean
reviewed-head gate. The production caller must recheck current identity,
resources, manifest and ownership at use; this review does not waive those
checks or predeclare their outcome.

While this review was still open, the coordinator reported four inherited
index/working-byte EOL mismatches: D203 RAW `host_closing01.json`,
`inputs_static.json`, `native_local_closing01.json` and
`tools/app_build_pins.json`. Current working bytes still match the frozen pins;
the historical index had normalized CRLF to LF. The proposed correction is four
narrow `-text` attributes and restaging those unchanged working bytes. Narrow
blank-at-EOF whitespace-check attributes for frozen oracle files likewise
preserve their existing bytes and assertions. This is Git representation and
checking metadata, not a tested source/fixture change. The coordinator must
record the before/after audit and verify the final index bytes equal every
frozen input before the clean-HEAD/check-only condition is satisfied. This
review does not predeclare that later index/commit audit complete.

No upload, reset, MCU read, runtime action, source repair, installation or
cleanup is admitted. D207 remains the latest accepted flashed diagnostic.
Actual ordinary artifacts/layout need a separate result review; any subsequent
ABI or entry addresses must derive from those actual ordinary artifacts.
Loading, live RAM/stack, ordinary timing/WCET, UART ownership/rearm, physical
sensors/motors, motor-run permission and human gates remain separate.

Final review. STOPPED WRITES after external byte-length/SHA-256 recording.
