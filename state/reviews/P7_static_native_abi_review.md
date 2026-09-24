# D149 file-only static ABI composition review

25 September2026, Asia/Dubai. Separate same-model review reusing D148/entry
review context, including a bounded second same-model command/parser inspection.
This is not fresh-context, cross-model, human or runtime review. Reviewer owns
only this file; no script main, GDB, board command, compiler/upload/reset,
implementation/test edit or commit was performed. Local source/receipt/hash,
historical-output and ELF-section inspections only.

## Verdict and fixed identities

**PASS for the exact revised one-shot file-only composition; no open BLOCKER,
MAJOR or MINOR findings.** Coordinator must record final source identity in
D149 before execution. No actual static ABI result exists at this review point.

| Input | SHA256 |
|---|---|
| P7_static_native_abi_plan.md | 9ad886b9ebeacc6f8285fbf61e5f3ccf2342650141732b1a7a890106ad31eba9 |
| P7_static_link_probe_raw/compare_native_abi.py | 7c7fa4769019c7aed0449fa3979d7c6c97edc3bf8625e60a5741313b88b6772b |
| P7_static_link_probe_raw/native_abi_preflight_final.json | 7c7caf2477da3c0b338ed98b0b0e42c2f205ba7e3a39b4e5817c9253788488fa |
| P7_default_qualification_raw/current_default_abi/receipt.json | 7a3e3fb9c67f023acae1c4efd5e2ee680123743f1f339edbed367d957728eb4f |
| P7_default_qualification_raw/abi_comparison.json | fe13798520a1d5688e7d3f7fe56a19f6d2df1e22af8162dc862109728efbd47c |

All paths above are relative to state/analysis. Frozen runner983e86d7,
helper8ba9b190 and17 local pins remain unchanged. The command's installed GDB
must match `8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778`.
Its existing debug ELF remains
`0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.

## Resolved pre-execution scope issue

Original source `f435e55854bd7542010c3ef6de6bd056356198c9dcb3c8a0ee319d89a6c7613f`
used only `-nx -nh -batch`. Those init-file flags and absence of embedded debug
script sections did not explicitly exclude object-associated script auto-loading.
This was a material gap in the stated no-script scope, resolved before any board
execution by the coordinator's parallel hardening and the second reviewer's
finding. Original source/preflight were preserved in3bf17a9c.

Final `compare_native_abi.py:82-84` inserts `-iex "set auto-load no"` before
the ELF argument, retaining every historical query unchanged. The
[official GDB manual](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html)
documents that exact option for forbidding automatic loading. Reviewer also
independently verified absence of .debug_gdb_scripts, .gnu_debuglink,
.gnu_debugaltlink and .debug_sup in the pinned local debug ELF.

## Command and parser checks

`baseline():67-88` hashes both original baseline files before decoding, requires
the expected GDB/prefix/465 original arguments and exact installed GDB pin,
then changes only the historical ELF argument and adds the two auto-load-disable
arguments. All230 original query strings were independently classified: two
language/print setup commands;16 each TYPE echo, sizeof, alignof and ptype;
82 each MEMBER echo and null-base address expression. None calls a function,
connects a target, runs an inferior, executes a shell or sources a script.

`parse():91-99` requires exactly16 type matches and82 member matches, then exact
expected key sets. Since the baseline contains16 and82 unique names, a repeated
name cannot disappear through dictionary overwrite while satisfying both checks.
Historical stdout independently yields all16 unique type pairs and82 unique
offsets with every value equal to pinned current_default. Final `finish()` uses
full dictionary equality, not selected fields or aggregate counts.

The original preflight records three malformed-output rejections and historical
parser agreement; its old465-argument result does not describe the final command.
The separately retained final preflight binds source7c7fa476,467 arguments,
11536 UTF16 units (below30000), all230 unchanged queries, parser agreement and
zero board dispatches. This reviewer inspected that preparation evidence without
rerunning the complete preparation or implementation entry point.

## Observation and failure semantics

`prepare():30-64` uses the same frozen local admission as D148: exact repo/-B,
ADB executable hash,17 pins,103-source/102-stage reuse, original boot identity,
D144 Claim and all eight original FileRecords. The new native_abi destination
must be absent and is created exclusively; old D144/native evidence is not
rewritten. Loading frozen modules does not invoke their CLI entry points.

At`:132-153`, only the reviewed helper's remote_postcheck, installed hashes,
one GDB command, final remote_postcheck and installed hashes are reachable.
The unchanged helper's postcheck independently attempts Claim, identity,
resources, process inspection, source and artifact checks. It does not create
a Claim or files. The host compares the original eight records, source and
identity. No compiler/property query, stage synchronization, upload/reset or
other mutation API is called.

Final remote, installed, local pins, local stage and baseline checks continue
independently after an observed failure, retaining the first exception and later
postcheck errors. Frozen dispatch preserves unsuccessful stdout/stderr/status
receipts. GDB must finish successfully within60s, with empty stderr and at most
1MiB stdout. At`:102-121`, ABI mismatch and command-count rejection occur before
writing status. A later result-file write failure cannot replace an already
captured exception; incomplete output cannot become STATIC_ABI_MATCH.

## Evidence boundaries

An eventual pass establishes only16 queried type size/alignment pairs and82
queried offsets for this exact ELF against the pinned current-default baseline.
It does not establish completeness of the selected fields, native function/
device/callback ABI, execution/loading, startup correctness, live RAM/stack,
WCET, static adoption, physical acceptance or a human gate. Existing dynamic
fit failures, original D144 rejection and D148 structural status remain separate.

## Actual D149 receipt review

25 September2026, after GO commit `2cd8d795`. This follow-up reuses the same
review context and bounded second reviewer; it is not fresh-context or runtime
review. Original review bytes had SHA256
`7d054afbd68a19a734053f69fc4c3992a55fee5498b675a44cb0194f316eb994`
before this append. Both reviewers only read/parsed local receipts and compared
hashes; no GDB/board invocation, retry, implementation/test edit or commit.

**PASS for actual D149 evidence; no open findings.**

The launcher spans2026-09-24T22:25:12.618302Z to22:25:14.803024Z
(25September02:25:12..14 Dubai), exits0 with empty stderr and records unchanged
source7c7fa476. All five command receipts have the expected board2629958581,
sequence/order and successful statuses, with empty stderr and no errors:
remote_postcheck, installed_pins, file_only_gdb, remote_postcheck, installed_pins.

Independent actual-output comparison verified that the full467 GDB arguments
equal the pinned baseline with only its ELF argument replaced and the early
`-iex "set auto-load no"` inserted before that file. All230 original query
strings are unchanged. The352801B GDB output independently parses to16 unique
type names and82 unique members; every size/alignment/offset equals the pinned
current_default baseline. The independently parsed dictionary exactly equals
`result.actual`. Result is STATIC_ABI_MATCH with matches_current_default true,
five reads, zero compiler/property-query attempts and no postcheck errors.

Independent binding checks also verified:

- Current wrapper hash, all17 local pins and both pinned ABI baseline files.
  All103 project source and102 stage files still match the frozen manifests and
  independently reproduce source aggregatefcddbd8e in full.
- Both captured helper commands decode to exact unchanged helper8ba9b190 and
  its exact bootstrap. Their action is postcheck, with the original run/Claim.
  Returned identities, including original boot, Claims and all eight FileRecords
  match historical D1440001/0021 and the new inputs. Both source observations
  match all102 local stage byte counts/hashes; compiler-candidate lists are empty.
- Both installed observations match all26 literal expected paths/hashes and each
  other. No partial hash-set comparison substitutes for this full match.
- All35 retained D144/D148 JSON evidence files are byte-identical to GO
  commit2cd8d795: original D14425 command receipts plus inputs/result, D148's
  five command receipts plus inputs/result and its launcher. Historical negative
  and structural evidence remains intact.

Exact inspected hashes under `P7_static_link_probe_raw/native_abi/`:

| File | SHA256 |
|---|---|
| inputs.json | 501aac4745a5a9a67cd4f73ec52956769476b8e1eb7352ae18a0f9d8f88aa75f |
| 0001.json | 8a5be8830f55cf221deb80dffd7c8412f047b61a42316e53641826a615631a60 |
| 0002.json | aac977915401c1e69701b0f8e57b6934e29e01a63f3d42625dc06c35b8df1b06 |
| 0003.json | a7c0c4797414e396e19d981b54e104d250cd77a32ac25e221f182e85c9da0994 |
| 0004.json | d12a0312535bd91f9e1f57e9d45dc043d66b344931676de438ea8e0f8b8937a6 |
| 0005.json | 887de51d16a9c6b1a6a110a65a474b6d45dcb3aa811cc5c08ecc78e8726425e9 |
| result.json | 797c84f4cd12266a963802a50d16923f6243666ae6e8151f748fec7b10a10676 |

Adjacent `native_abi_launcher.json`:
`0f40e70946c082e8228a35ffae2924b7b921197234f78fc97cc79880693d78bf`.

The result closes only this98-entry debug-layout comparison. It does not prove
full native function/device/callback ABI compatibility, field coverage, loading,
MCU behavior, live memory/stack, WCET, static production adoption, physical
acceptance or a human gate. Those evidence boundaries remain unchanged.
