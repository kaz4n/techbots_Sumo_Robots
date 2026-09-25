# D173 observed diagnostic ABI and recipe

25 September 2026,07:14:30–07:14:32 Asia/Dubai. FILE-OBSERVED.
Reviewed execution HEAD089de986, reader50c07402. One transport/five children
exit0, all reaped without timeout;1.197s total. All26 remote and120 local final
checks PASS. No upload/reset/MCU access, compilation or dependency change.

Installed readelf2.43.1 and GDB16.2 (Zephyr SDK1.0.1) read the exact D172 files.
Final ELFf9460a16 is ARM ELF32 little-endian REL. Its LOCAL diagnostic OBJECT
has offset0/size2592 in section7 .bss (2632B,alignment8). Debug7a4b2953 confirms
Runner2592B/alignment8, trace report at44 and main report at2312.

| Type | Size | Alignment |
|---|---:|---:|
| Runner |2592|8|
| Trace |2180|4|
| TraceReport |2128|4|
| Call |32|4|
| Report |264|8|
| Port |44|4|
| MotorGate |88|8|
| Result |56|8|
| HaltResult |16|4|
| PreviousTick |48|8|

The64-call array occupies2048B; four applied Results occupy224B. Exact field
offsets and source/artifact bindings are in P7_motor_fault_raw/active_abi.json,
SHA822c917d. The separate reviewer independently compared all ten direct GDB
layouts with the compact manifest: zero size/alignment/member mismatches.

Exact loader ELF39d4a4fd confirms llext_list0x200017bc (8B),196B/alignment4
nodes, name[16] at4, mem[12] at20, mem_size[12] at80, BSS enum3 and base/size
offsets32/92. These are file ABI facts; no live relocation address was observed.
D172's recorded recipe selects dynamic motor_fault.ino, default wait startup,
and the build-directory .elf-zsk.bin. Both build/export copies match b4416792.
Recipe templates still require a separately qualified upload invocation.

Evidence: P7_motor_fault_raw/native_abi01/ (219185B), abi_native_invocation.json,
and ../reviews/P7_motor_fault_abi_actual_review.md. Raw tool streams remain exact
base64; no firmware or debug binary was downloaded. Temporary board streams
closed automatically. No denied cleanup path was retried.

Original reader draft273d1871 and initial FAIL review are retained. Manifest
binding, independent local closure and lossless stream collection were repaired
before execution. Nine root-authored controlled failure checks PASS/native0;
abi_failure_check_result.json also binds the final composed programc5f4793a.
The initial abi_local_check.json belongs to the old draft, not the executed reader.
Separate final source revieweb9e2d78 and actual review both PASS; same model,
reused context for re-review, not cross-model or phase-gate acceptance.

D173 is consumed. Next offline fixed-layout decoding and then a bounded exact
artifact upload/capture profile. Two future passive snapshots cannot prove
atomicity. Native callback behavior, original fault cause, WCET, physical tests
and human gates remain unqualified. D160 remains the last actual upload.
