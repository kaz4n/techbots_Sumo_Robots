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
