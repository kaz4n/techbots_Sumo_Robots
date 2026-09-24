# D144 native static attempt: compiler pass, structural rejection

Status: TARGET-COMPILED / ARTIFACT-VALIDATION-REJECTED. This is a retained negative
experiment, not static fit, runtime, release or phase acceptance.

Run `f0220228320c4b2aa20c3e5e8264c813` used the reviewed D143 runner/helper and
D144 invocation on ADB2629958581. Source remains
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`,
static/default/MATCH0/MOTORS_ALLOWED0. The expanded-properties query and sole
jobs1 compile returned0. Compilation ran from21:28:53.712875 to21:32:39.353441UTC
on24September (25September01:28-01:32Dubai). No compiler stderr was reported.

The exact seven build files plus selected export were present, stable and hashed.
The layout action returned2 with `LAYOUT_REJECTED: unsupported symbol encoding`.
Both independent postcheck groups passed; their eight artifact identities match.
The runner stopped with FAILED/phase layout, counts1query/1compile, no postcheck
errors, and no final-ELF transfer. The launcher returned1 with both source hashes
unchanged. No retry, upload, reset, motor run or cleanup occurred.

Evidence: [compact checked receipt](P7_static_native_attempt_receipt.json),
[run result](P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/result.json),
[compile](P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/0017.json),
[layout rejection](P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/0022.json),
[launcher](P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813.launcher/completed.json).
The separate [receipt review](../reviews/P7_static_native_attempt_review.md)
confirms the negative disposition without a material evidence inconsistency.
All25 numbered commands are terminal; only0022 returned nonzero. The local packet
retains31 files/448375logical bytes. Other build artifacts remain at their unique
Linux paths; no duplicate compiler tree was created on Windows.

The remote final ELF is170616bytes, SHA256
`5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
Its build directory is `/home/arduino/sumox26_codex_build/_app_builds/`
`static-app-probe-v1/fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2/`
`bench-default/f0220228320c4b2aa20c3e5e8264c813/build` (join these fragments).

The frozen D142 contract explicitly allows only bindings0/1/2, types0/1/2/3/4
and st_other0..3. Its combined check does not identify the offending symbol in
this error. Do not assume a symbol type, relax the parser, change linker flags,
or repeat compilation. The next task is a separately scoped, reviewed read-only
collection/inspection of this already hashed ELF to identify the exact encoding
and reconcile it with primary ABI/toolchain evidence. Preserve this negative
result and all frozen contracts/tests. D139's592-byte dynamic deficit is unchanged.

Later full native entry/copy/zero/constructor order, used bindings/wrappers/heap,
weak references and16-type/82-offset ABI audit remain pending. WSL already has
readelf, nm and arm-none-eabi-objdump; board file-only GDB can reuse D139's exact
query list after review. Do not run the historical hardwired collector or apply
the ET_REL/dynamic LLEXT allocator model to this ET_EXEC artifact.
