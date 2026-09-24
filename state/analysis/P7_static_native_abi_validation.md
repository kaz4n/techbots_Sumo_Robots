# D149 existing static debug-layout comparison

25 September 2026, Asia/Dubai. **FILE-ONLY TARGET ABI COMPARISON PASS.** All16
queried type size/alignment pairs and82 member offsets exactly match the pinned
current-default build. This is compiler debug-information evidence, not execution
or complete native driver/function ABI qualification.

## Execution and binding

GO2cd8d795 binds [plan](P7_static_native_abi_plan.md)9ad886b9 and
[composition](P7_static_link_probe_raw/compare_native_abi.py)7c7fa476.
Separate reused-context same-model [review](../reviews/P7_static_native_abi_review.md)
initial7d054afb has no open findings. Original draft/preflight remain in3bf17a9c;
the final adds explicit object-associated script auto-loading suppression before
opening the ELF. All230 baseline query strings are unchanged, with no target,
inferior or function-call command. Source hashes match before and after.

The [launcher](P7_static_link_probe_raw/native_abi_launcher.json) and
[command receipts](P7_static_link_probe_raw/native_abi/0001.json) record:

| Sequence | Action | Exit |
|---|---|---:|
| 0001 | Original helper checks Claim, identity, source and eight artifacts | 0 |
| 0002 | Verify26 installed dependencies, including GDB | 0 |
| 0003 | Pinned GDB reads existing static debug ELF;467 arguments | 0 |
| 0004 | Repeat original helper checks | 0 |
| 0005 | Repeat installed hashes | 0 |

Observed interval22:25:12.766715–22:25:14.754149 UTC on24September, or
02:25:12–02:25:14 Dubai on25September. GDB itself ran22:25:13.578912–13.982293 UTC,
returned0 with352801B stdout and empty stderr. Every command succeeded and all
independent local/remote/source/baseline postchecks passed. One GDB process, zero
Arduino property queries, zero compilers, no upload/reset or MCU command.

The current source isfcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2.
Debug ELF0f7f2825, original D144 boot/directory/file identities,103 sources,
102 staged files,17 local pins and26 installed dependencies remain bound.
GDB SHA2568e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778.
Pinned baseline command receipt7a3e3fb9 and comparisonfe137985 are unchanged.

## Result and limits

The [result](P7_static_link_probe_raw/native_abi/result.json) contains every
actual queried pair/offset and `matches_current_default=true`. For example,
`app::Runtime` remains166376B with8-byte alignment. Exact cardinality and key sets
reject missing, duplicate or renamed rows; every value was compared. No assertion,
source layout or baseline was altered to obtain equality.

These selected project layout entries do not establish complete native callback/
device ABI, loaded memory values, startup/stack/heap/WCET, peripheral operation,
static adoption or physical/human acceptance. D139's dynamic592B modeled deficit,
D144's original rejection and D148's distinct structural pass remain intact.

Seven command/input/result files total478121B, plus a small launcher record.
The full original GDB output remains in its single command receipt; no separate
stdout copy, ELF transfer, compiler tree, snapshot or bytecode cache was created.
Retain these required bytes; D149 is terminal and its one-shot scope consumed.
The next audit concerns the complete set of used native references, especially
driver dispatch through runtime device/API pointers, and an explicitly qualified
inert loading/startup path. No upload follows automatically from this comparison.

Separate reused-context same-model actual receipt review PASS, no open findings.
Final review SHA2563f4d20b77dcff244458d6b1e94ea0f93a66ba62b3ade238d98e597e7a8886997.
The reviewer independently reparsed the actual GDB output, verified every query
and value, current bindings and35 original D144/D148 JSON receipts unchanged
against2cd8d795. No board command or experiment was rerun.
