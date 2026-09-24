# D148 actual static packet structural result

25 September 2026, Asia/Dubai. **TARGET ARTIFACT STRUCTURE/PACKAGING PASS.**
This is validation of existing D144 bytes under the separately tested D147
interface. It does not change the original D144 rejection or production admission.
There was no compiler invocation, upload, reset or MCU execution.

## Actual operation

Coordinator scope [D148 plan](P7_static_native_actual_plan.md) and exact-source
GO were committed in dbb5f1a4. [Independent composition review](../reviews/P7_static_native_actual_review.md)
initial hash960a693f passed after two receipt-only repairs; original glue/preflight
remain in8e3c4348. The reviewer also passed six in-memory finalization scenarios.
Final hostfbde2926 and remotec6099f6d were checked before execution and unchanged
afterward. D147 validatorcd52a29a and original based30372dd/helper8ba9b190 were
hash-bound and reused without edits. The prior70 host methods remain applicable;
this operation did not rerun them or substitute mocks for board observations.

The [launcher receipt](P7_static_link_probe_raw/native_actual_launcher.json) and
[five actual command receipts](P7_static_link_probe_raw/native_actual/0001.json)
record execution from22:16:51.359972 through22:16:53.138369 UTC on24September
(02:16:51–02:16:53 Dubai on25September):

| Sequence | Read-only action | Exit |
|---|---|---:|
| 0001 | Verify26 installed dependency hashes | 0 |
| 0002 | Observe102 staged source files | 0 |
| 0003 | Validate existing seven artifacts and exported package | 0 |
| 0004 | Repeat installed hash checks | 0 |
| 0005 | Repeat source observation | 0 |

No stderr, query0, compile0 and no postcheck errors. The exact old boot/directory
Claim, all eight FileRecords, installed TLS/loader identities and current source
fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2 remained
bound.17 local pins,103 source files and102 local staged files also revalidated.
The receipt retains the distinct `STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS` report;
no saved or production report is relabeled with the old admission status.

## Observed structure

The [result](P7_static_link_probe_raw/native_actual/result.json) binds final ELF
5cc2dfde (170616B), equal debug/temp0f7f2825 (1764708B each), raw BINbd03c2e7
(93080B), flat package5f08afe0 (93096B), ELF package1794da3d and map15da1417.
All seven hashes match the original D144 artifacts. Both package representations,
three normalized allocated images, initialization bounds and six exact inherited
TLS aliases pass. No unresolved weak symbol is reported.

| Quantity | Observed value |
|---|---|
| Thumb entry | 0x08100011 |
| Flash payload | [0x08100010,0x08116ba8),93080B |
| Remaining configured flash region | 693336B |
| Static RAM allocation span | [0x20013890,0x2003c800),167792B |
| Remaining configured RAM region | 94352B |
| Data copy | 208B from0x08116ad8 to0x20013890 |
| BSS zero interval | [0x20013960,0x2003c6c8),167272B |

The94352B value is a linker-region tail, **not measured available RAM, stack or
heap headroom**. It does not repair or reinterpret the separate D139 dynamic
loader deficit. Actual entry/constructor effects, native binding/ABI, loading,
startup/stack/heap/WCET and peripheral behavior still require qualification.
No static deployment/adoption, release tag, motor permission or human gate follows.

## Retention and next task

Seven compact command/input/result files total125141B; the small launcher record
is separate. No duplicate ELF, map, package, staging tree, fixture or compiler
cache was created. These receipts remain required evidence, not disposable data.
The independent final receipt review is recorded in the linked review file.
Continue the local entry/constructor audit against retained debug ELF/map, then
the missing exact native ABI/reference audit. Never rerun this consumed one-shot
composition or the earlier D144/D145/D146 operations.

Separate same-model actual receipt review PASS, no open findings; the initial
fresh context was reused for this result inspection. Final review SHA256
`12cbec6b11bcc6205b2257ec5bf7cc9ae00770e2e9dd2939150c19bef7660fff`.
It independently verified current pins/source/stage, both installed/source brackets,
captured-code tokens, Claim/artifact/report tuples and all27 historical D144 JSON
records unchanged against dbb5f1a4. It did not rerun board commands.
