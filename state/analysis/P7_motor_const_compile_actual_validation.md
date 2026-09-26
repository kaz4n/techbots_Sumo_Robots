# D203 actual constant-metadata target compilation

26 September 2026. One compile-only attempt completed at clean reviewed HEAD
`dbeec127ba651b6a4346f70aaf5b78bc79718ce0`, using diagnostic source
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`.
The profile is app_motor_observe, static linking, default startup,
MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1. No upload, reset or MCU read ran;
D201 source117cc0e7 remains the latest flashed image.

[Saved invocations](P7_motor_const_compile_raw/native_invocations01.json),
SHA `d8b43e9561cb8a6193a5ee262dc4bae4cf06c65aa5ed15ef92e450390c3ec60a`,
preserve check-only exit0 and execute exit0/empty stderr. Execution took369.34s.
The [native result](P7_motor_const_compile_raw/native_static01/result.json),
1605B/SHA `323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7`,
reports COMPILE_CHECKED, one properties query, one serial compiler,
238 transports, no first error and all eight closing checks PASS.

## Checked files and static layout

[Artifact receipt](P7_motor_const_compile_raw/native_static01/artifacts.json),
9645B/SHA `fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd`,
binds all eight artifact observations with file identities and hashes, plus
the unchanged installed loader and TLS source. Its native TLS/layout/package
validator passes; the weak undefined symbol set is empty.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Raw ELF | 172600 | 390b69c1f35dd85a56462e562561e16b4659c0e31aa44d99aaf5b87e4ccd7e13 |
| Debug/temp ELF, each | 1838360 | b3520cacc96ccd3d410b011dd6b4e65761c503b940fa13f1fddfe59db3666066 |
| Raw binary | 95352 | 76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3 |
| Packaged binary, build/export copies | 95368 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 |
| Packaged ELF | 172600 | 5416c121deb8ff3cb0a27a3d8d150981fe945c5ab818fe3da788744f4980db7f |
| Map | 449499 | 23416a129a832bbbc4738814a7a1326a62f5e5f9e879d925ab7620e3ab1b88a3 |

Relative to D198, .text decreases128B and .rodata24B; .init_array, .data and
.bss sizes are unchanged. The raw binary decreases152B. These are file-size
observations, not proof of any particular removed instruction or runtime gain.

CLI reports95368B program and171892B globals (90252B arithmetic remainder).
The structural layout separately reports90256B RAM tail,208B initialized data
copy and170664B zeroed BSS. These distinct quantities are not live free RAM,
stack headroom, measured WCET or physical qualification.

## Closing evidence and next scope

[Local closing receipt](P7_motor_const_compile_raw/native_local_closing01.json),
SHA `cf3e16fb6884900e5ac662482118dc8a6a9fc14157978b6063c4965816f91135`,
verifies196 frozen inputs,129 manifest pins and10 scope pins unchanged. The
actual local stage has exactly108 files/781200B with all expected hashes.
The consumed native owner retains1004 compact receipt/stream files/1698674B.

The attempt owner is consumed. Preserve its evidence and checked target files;
do not rerun the compiler. Independent actual-evidence review closes this task.
Then a new file-only ABI inspection must establish this image's report/global
layout and complete symbol inventory. Candidate helpers may be inlined or absent;
their old D199 addresses and presence are not requirements for the new image.
A subsequent fixed instruction inspection and separately reviewed inhibited
runtime attempt are still needed. No timing improvement or repaired runtime
fault is established by compilation.


Independent [actual compile review](../reviews/P7_motor_const_compile_actual_review.md), 10135B/SHA9c3e8cfe07ae33cac8d4a91f74127c33d3929e299bd5da339934943d784f21df, PASS. It reconciles all238transports/nine reaped child commands, query1.597s/compiler228.509s, exact validator payloads, installed/source/artifact closure and local counts. No open actual-evidence finding; next ABI/entry work remains separate.
