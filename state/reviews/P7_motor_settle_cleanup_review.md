# D200 cleanup source, host and staging-preparation review

26 September 2026, Asia/Dubai. **PASS for the fixed prepared software and
staging intent; no open material finding.** This is a separate same-model,
reused-context review by `/root/fresh_review`. The reviewer used local source,
contract, fixture and saved-receipt reads, hashes, AST inspection and byte
comparisons. No subject import, test execution, board call, credential access,
staging or deletion was performed. Only this review was written.

| Current input | Bytes | SHA-256 |
|---|---:|---|
| P7_motor_settle_cleanup_contract.md | 16277 | `6cb02590369cdce1edd748987df363f99f336c9736dfd06e72906c4578457f47` |
| cleanup_remoteocd03.py | 7740 | `6afeea1b9733670cdf315b2bf29b3e6e9c24016a2ba9217013e67496ec088f4d` |
| cleanup_root04.py | 9603 | `13f33327c5474d7c4dee56657a9d93b50e6fcdaee864e1855c916417a53c6290` |
| tests/tooling/test_motor_settle_cleanup.py | 12023 | `afbc97d1bd310646505d6fdc61b21db26418d27163b44700faa23a52a4842f2b` |
| cleanup_stage_intent01.json | 20649 | `09584e7a4dfe232705201c3f3f254736147813d43daed98fc98caddf673d74d9` |

Names without a directory above are under
`state/analysis/P7_motor_settle_cleanup_raw`, except the contract under
`state/analysis`. All seven contract input size/hash pairs were independently
verified, including the retained D196 sources, unchanged static helper,
admission observer/receipt and D193 artifact receipt.

The reviewer independently applied the four count-checked recipe substitutions
and six wrapper substitutions to the pinned D196 files. Both results equal the
new files byte-for-byte. Every operational byte outside those substitutions is
unchanged. The one-occurrence private missing-link projection produces 7737
bytes, SHA-256
`96d1197ec296906958f71c772102fdd34f7979525cde3e41222ee611025274c4`.
Historical source and consumed cleanup owners are preserved.

The saved admission `e95ebed4ee3d6441abccced02adbcc4857fe5f10418d94e158b009d3edecf922`
has transport0, empty stderr, no first error, local closure PASS and five remote
closing PASS. Its before/after full board identity and directory stamps agree:
boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, Arduino UID/GID1000, directory
device34/inode1172. The three ordinary, single-link copies and their retained
originals have matching size/hash pairs totaling 2,399,768 bytes. Recorded
path/descriptor identities agree. The 95,360-byte package is D193's
`85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c`, uploaded
in D195; it is not D198's 95,520-byte package. This admission is content and
identity evidence only: it explicitly excludes protected cwd/FD observation
and did not establish absence of the proposed root04 stage.

Source inspection confirms retained initial all-root credential admission,
Python -I -B/no-argument checks, fixed dependencies, descriptor-based ancestry,
ordinary single-link UID/GID1000 source files, exact length/hash checks and
full before/open/after stability checks. All closes are attempted while the
first error is preserved. The recipe performs mutations as UID/GID1000; only
the process observer temporarily raises effective UID0. Its finally restores
and verifies the Arduino credentials before any unlink is reachable. The
private projection sends missing cwd/FD links to the inherited surviving-PID
check; permission failures and missing links of surviving processes fail.
Native-process names, exact self-exclusion, same-user handle checks and
4096-PID/FD bounds remain unchanged. The inherited other-user FD limitation
and observation races remain; this scan is not a lock.

Before each of exactly three sorted unlinks, the recipe retains the process
scan, full board recheck, remaining-file content/full-stamp comparisons and
directory identity checks. It hashes all retained originals before and after,
removes only the emptied fixed directory, fsyncs and checks absence. No
recursive deletion, process exception or fallback path is introduced. The
55-second alarm, raw/partial stdout, removed names and first-error handling
remain. Once root admission succeeds, every exit independently attempts both
permanent GID and UID drops to triples1000; drop/restoration failure prevents
success. The wrapper's unchanged `run_original` checks object shape,
returncode0 and success status, not the nested schema. Fixed source pins bind
the emitted D200 schema literals. Acceptance of an actual saved receipt must
separately validate both schemas and the complete evidence fields, as the
contract explicitly requires.

The independent oracle froze before its author read, hashed or imported the
new implementation. The reviewer statically reconstructed its complete core
projection (37255 bytes / `4109c339f8d6a8faa195b671a8b20ce778810bd895e04846b84784f58610a33f`)
and metadata projection (14478 bytes /
`fc1ce156a78519c041a8836191583f4548fc7846d5c229060818dfbc9a33f0a2`).
Method names and assertion-call sequences are preserved: 37 methods/147
assertions in the core and 10 methods/34 assertions in the metadata class.
The metadata adaptations bind the current inode, package and owner identities.
Two additional methods reject D190/D198 package substitutions and old source
names/stage/schema substitutions. They correctly treat schema drift as source
drift, without inventing a runtime JSON-schema predicate. The inherited
credential, protected-process, descriptor, deletion and failure cases remain
controlled fixtures; no material fixture defect was found.

| First host receipt under the new raw directory | Actual result | SHA-256 |
|---|---|---|
| first_linux01/result.json | exit0; 49 PASS, no skips; unittest0.378s | `aab32dc8e99559dcd43d2d873256eeeda2e081653a77bdff4f9749dc6ce32d8e` |
| first_windows01/result.json | exit0; 12 PASS, 37 explicit Linux credential/proc skips; unittest0.052s | `99f920cdacc37ebdba0d36b8a04f9e2662d1a27548cdf82a5f03f118f602fd64` |

The recorded serial commands use Python -I -B; Linux uses TMPDIR=/dev/shm.
Raw stderr hashes are `77856aa0f969587feb3840477f823a6fbc41870adcb2c753805f507146f4794d`
and `a05906efbe91ab8c2a407dc6a363358a3ec7b12cc6b23480ea33a854bf2a984f`;
both stdout files are empty. Independent freeze
`b5d1721358f5dd8d6e8f6acdf9caaa192f791b876e6b91e7154b17e080ad873b`
precedes these runs. Coordinator freeze
`33c04281202bb235c5cadb1ecacc0a09b7366948070dfba8782c49025e3af035`
and host closure
`75f10900f85e4d6bee1e8f98ce9b9348320c98228525af91c27a926e91b635f4`
report no changed inputs. All 22 current coordinator pins were independently
hashed and match. There was no failed run, repair or retry.

The staging intent is preparation only. Its predecessor pin matches the saved
D196 intent `65e4fa190919f72c533ca3fb3962f22b4ef426054db298f1cd30b67e4e111ad1`.
The reviewer decoded its data packet without executing it: exactly the three
current pinned source files are embedded, including unchanged static_remote.py.
The 18,882-byte program hashes to
`958d331174d34442de4f3e3853a99a201ae7db4cce5ec4ed4fc287bdd2268db3`;
the Windows command size independently recomputes to 19,581 units. Apart from
fixed names, pins, inode and embedded source payload, its program is unchanged
from D196's staging template. It checks board/scratch/originals, exclusively
creates cleanup-app-settle-root04 and its three files, verifies bytes/ownership/
single links, fsyncs and closes. It contains no cleanup, sudo or credential
transition call. Its absolute Python -I -B path, 55-second alarm and 70-second
outer bound remain.

This PASS supports separately observing fresh owner absence and performing
that one fixed staging operation, followed by independent actual-stage review.
One specifically admitted authenticated cleanup still requires fresh bindings,
exclusive result_root04.json, unchanged runtime guards and saved-receipt review.
No owner reuse or automatic retry follows. This review establishes no actual
staging, authentication, deletion, process-use clearance, firmware operation,
fault resolution, physical acceptance or human phase gate.
