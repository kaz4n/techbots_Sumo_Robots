# D146 installed TLS provenance

25 September 2026, Asia/Dubai. **DIAGNOSTIC_TLS_FILES_COLLECTED; inherited symbol
provenance verified.** Original D144 structural rejection remains unchanged.

The exact reviewed collector2443cedc/remote48ca3cdf was authorized in54f2f268.
One read-only remote Python command completed21:53:37.922041–21:53:39.297437UTC,
exit0, no stderr. No query, compiler, upload, reset, remote write or retry.
Original boot/directory Claim and all eight artifact FileRecords matched before
and after; local postchecks passed. The separate same-model collection review
also verified17 pins,103 source files,102 staged files and all25 original D144
command receipts. [Review](../reviews/P7_static_tls_collection_review.md).

## Actual inputs and interpretation

| File | Bytes | SHA256 |
|---|---:|---|
| Installed `tls-syms.S` | 977 | `68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70` |
| Existing `tls-syms.S.o` | 728 | `bf3b5c57a3646cdde3f38085fd30c1f3345ae025f973e06dfa9db69f48bc63c7` |
| Existing `app.ino.map` | 666298 | `15da1417d5a7f781195d86ba1554dd449e4e14548dde1ea8052e8da78cd16806` |
| Existing debug/temp ELF, identical bytes | 1764708 | `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd` |

Original command/input/result records and decoded files are under
[observed](P7_static_tls_raw/observed/result.json). Only one debug/temp payload
and local copy were retained after independently checking both original files.

The installed assembly header names the packaged firmware SHA256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`;
the actual packaged file still matches. The source emits six global `%tls_object`
constant definitions with an8-byte TCB adjustment and no storage directive.
Its ordinary object sections have zero allocation, no relocation records, and
exactly the six GLOBAL/default/ABS/type6/size0 tuples seen in debug and final ELF:
`_TLS_MODULE_BASE_=8`, `_rand_next=8`, `z_tls_current=16`, `errno=20`,
`_strtok_last=24`, `_localtime_buf=28`.

The map explicitly LOADs that exact object at line953; its empty ordinary
sections appear in the discarded section list at643–647. No actual `.tdata` or
`.tbss` input contribution appears; only linker wildcard selectors at3998/4012.
The10-byte `__aeabi_read_tp` wrapper from `core.a(llext_wrappers.c.o)` is discarded
at767–768. The final-image scan found no direct branch/call to the absolute
native accessor alias. See the independent [local analysis](P7_static_tls_local_use.md)
for commands, counts, addresses, comparisons and limitations.

This supports identifying inherited firmware-symbol metadata. It does not prove
absence of indirect/native TLS accesses, native ABI compatibility, runtime
correctness or physical acceptance. No frozen validator/oracle was changed.

## Next action and retention

A separately reviewed pure structural extension may admit exactly these six
identity-bound inherited symbols while retaining every D142 layout/package rule.
It must reject missing, additional, duplicate or changed aliases and arbitrary
TLS allocation/relocation forms. Independent expectations must be frozen before
implementation execution. Preserve the original validator, tests and rejection.
Native entry/constructor/binding/ABI audit remains required after structural work.

Retain the seven observed files totaling3560018 logical bytes, the two small
collection compositions and compact analysis/review. They bind provenance and
provide one reusable debug artifact for later inspection. No compiler tree,
duplicate temp ELF, broad source checkout, bytecode or large disassembly added.
