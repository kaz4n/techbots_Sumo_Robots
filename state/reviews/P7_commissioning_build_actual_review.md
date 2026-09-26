# D222 actual native commissioning matrix review

Verdict: FINAL PASS. All fourteen original-source commissioning tuples are accepted as native compile-only results. No open BLOCKER. This review grants no upload, firmware execution, motor-run, physical qualification or phase-gate approval.

Review finalized 2026-09-26T23:54:55.175030+04:00. The reviewer made no board calls, ran no test suites and changed no main-workspace file during the matrix or the later active D225 compilation. The sealed final was prepared in Temp for coordinator publication after active native work closes.

## Scope and evidence provenance

This review covers only source `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`, the seven closed commissioning profiles, both explicit M0/M1 identities and attempt `native01`. D224 later changed four HAL files and D225 is separate native work. Neither the changed current firmware nor any future image inherits these fourteen compile results.

The reviewer independently reconciled the first eleven closed tuples while original source was current. The coordinator then executed the unchanged reviewer-authored reconciler over all fourteen before D224 integration and archived it under `state/analysis/P7_commissioning_build_raw/matrix_closure01/`. The archived script is byte-identical to the reviewer original (SHA256 `2fb448e58f260f48280542cb39c7d720ffc482051e06708bfc17aa9c98b5945e`); archived summary SHA256 is `0820d56d5ea1c690fdf5bbf1e54a1952a817cc1a1dee98030460e7812d446e04`.

After integration, the reviewer independently reconciled the remaining three tuples against their historical Git blobs and unchanged staged bytes, deliberately excluding the changed current HAL source. Those three complete summary rows equal the archived rows. Last-three historical reconciliation summary SHA256 is `28629a808214edb2f9fecf2b4894fad6f5163f08f3f5081080c56551d7dfa3c6`. The reviewer also rechecked all twenty-eight saved result/artifact hashes against the archived summary. No native evidence was rewritten.

## Accepted actual result

Each tuple has 134 bound input files and 104 staged source files; its staged content reproduces the complete source digest above. All fourteen run records identify static/default-wait `app.ino`, MATCH0, exactly the selected profile and explicit motor identity. The invocation HEAD/evidence-commit sequence is continuous from `ee1bdcedf412903445c5076cae5980a43e0dc34e` through `c29e7bba6fcd268b673e6d07afe93e1c29f2c381`; each evidence commit directly descends from that invocation HEAD. No source/helper change occurred within that chain.

Accepted totals: fourteen expanded-properties queries, fourteen compilers, 350 successful transports, 126 completed/reaped checked child commands, and 126 PASS final checks. Every compiler uses jobs=1 and each tuple closes before the next starts. Emitted command arguments and native compiler metadata agree on selectors, paths and static/default settings. No upload/reset/monitor command appears in the checked child commands, and compiler upload_result is empty. Maximum actual Windows command length is 29376 units, below the unchanged 30000-unit bound.

For every tuple the review reconciled the input manifest digest, reviewed HEAD, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, serial `2629958581`, per-attempt owner paths, raw transport/child results, exact first/final artifact report equality, all seven artifact hashes and sizes, exported-flat-package equality, native TLS/loader identities, artifact-source transfer closure, initialization/builtin/source observation equality, and all nine independent final checks. Native artifact reports retain the full ELF/layout/package validation and all descriptor closing checks.

Every tuple reports a structural RAM tail of 94352 bytes. This is a layout result, not measured live free RAM, allocator/stack headroom or initialized WCET. Target artifact bytes were validated by the previously reviewed remote descriptor/ELF/TLS/layout code; this reviewer reconciled its retained reports and did not perform another binary retrieval or fresh board observation.

Retained compiler JSON in `compile/` has Windows CRLF conversion from board_tool.write_text. It was compared to unmodified base64/child stdout with that exact conversion. Raw child streams remain available and unchanged.

## Evidence limits

Outer check-only/execute driver messages reside in the coordinator tool/session transcript, not separate check-only files inside each owner. No additional check-only receipt was inferred and none was rerun. Clean-HEAD admission is supported by the reviewed mandatory runtime guard, matching input blobs and the per-owner commit chain; the outer transcript is separate coordinator evidence.

Compile success, including M1, supplies no image execution, electrical inhibition measurement, sensor/motor result, UART delivery, live RAM/WCET qualification, match recording or human gate. These attempts never grant STAND OK or RING OK.

## Tuple identities

Full artifact hashes and metadata remain in each owner artifacts.json and the archived matrix summary. Prefixes below are only a compact index.

| Profile | M | Invocation HEAD | Evidence commit | ELF SHA prefix | Flat package bytes | Flat package SHA prefix |
|---|---:|---|---|---|---:|---|
| b4_stand | 0 | ee1bdcedf412 | 56fb7aba73a7 | 12a24abfb96e | 82912 | 84667b0a22ff |
| b4_stand | 1 | 56fb7aba73a7 | 07b47afb3a62 | 8ded5c882173 | 83284 | b9ecf795d029 |
| p3_drive | 0 | 07b47afb3a62 | 7779f81862d7 | 1d6bcb590503 | 85688 | 611521a497ed |
| p3_drive | 1 | 7779f81862d7 | 3d7ce7efc75b | 9a8d8cd1ce37 | 86056 | 25f29f1b35ef |
| p3_turn | 0 | 3d7ce7efc75b | 57b45d1c5a6c | 188df5652f0a | 84748 | b0312eb72ee1 |
| p3_turn | 1 | 57b45d1c5a6c | 3c8d350628dd | b0d2814cf883 | 85120 | e647b0bb49c7 |
| p3_stop | 0 | 3c8d350628dd | d2f58113b976 | 0be48d263ca4 | 84308 | 6da22c0bc788 |
| p3_stop | 1 | d2f58113b976 | 90a97dc4abf3 | 3ac801cbdabe | 84680 | ff7a25580d89 |
| p4_reactive | 0 | 90a97dc4abf3 | 3b4525b6835e | cb946d72db26 | 89616 | c2ef5a2bf86c |
| p4_reactive | 1 | 3b4525b6835e | 02d5cdc5185a | d5bf94064371 | 89984 | 8b6973c5224d |
| p4_timing | 0 | 02d5cdc5185a | de5529147f0d | 41d51bf4096b | 90888 | 0ee572efad35 |
| p4_timing | 1 | de5529147f0d | 4e1cb04c8d0e | 043149f38e36 | 91256 | c2c747b406c5 |
| p5_abort_timing | 0 | 4e1cb04c8d0e | ab8306480711 | 84582aa371ca | 94496 | eeb641564a0a |
| p5_abort_timing | 1 | ab8306480711 | c29e7bba6fcd | ca9bccf8c427 | 94872 | d330d5ba8092 |

## Local disposable staging candidates

Exactly fourteen `build/stage/commission-*-e9e91397f42f` owners are eligible as disposable local source snapshots after this review and after active native work closes. Each has exactly 104 checked plain files, 764405 bytes, and the expected directory set. Total: 1456 files and 10701670 bytes. The reviewer checked all fourteen complete file/directory sets and hashes against their committed staged_files.json manifests; these contain source copies, not checked target artifacts. Reproduction is preserved by the historical source commits, full source hash and retained manifests/receipts.

The exact absolute path list, per-owner counts and manifest hashes are in Temp `sumox_d222_local_stage_cleanup_candidates.json`, SHA256 `1e38536c2fa8c40315a1d28ef87b341de912d25e22bec3db7530700fdaeb4afd`. The coordinator should retain that compact list before cleanup. Immediately before any deletion, revalidate every literal target is confined to build/stage, remains plain, and has the same complete file/directory/hash set. Record actual removal sizes and outcomes in state/STORAGE_LOG.md.

**Absolutely exclude `build/stage/b4-app-m0-static01`.** Also exclude every D224/D225 or unrelated stage, all remote native builds, all checked target artifacts, all unique evidence, credentials, user files and Git history. No blanket build/ or state/ deletion is covered. Nothing was deleted by this review.

Next action: publish this sealed acceptance after the separate D225 operation closes; retain original D222 evidence and keep later-source qualification separate.
