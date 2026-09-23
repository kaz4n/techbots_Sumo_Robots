# D114 firmware, staging and exact-target review

PASS_SCOPED_D114_FIRMWARE_STAGING_AND_EXACT_TARGET. No open BLOCKER, MAJOR or MINOR in this scope.
Reused separate same-model source-aware reviewer; not a cross-model review or human gate. Capture, upload and actual execution are excluded.

- `bench/ui_adc_probe/ui_adc_probe.ino:9` creates exactly one Native/Runner, grants native A1 setup once, and polls once per loop. MATCH/motor flags are compile-refused; old UI remains disabled.
- `tools/board_tool.py:159` stages only the four existing UI files for the literal probe, refusing source symlinks and every destination collision, including dangling links. The 94 shared target sources match D112 exactly.
- `tools/board_tool.py:296` and `tools/app_build_policy.py:75` permit only the checked default inert build. Immediate, MATCH, overrides and uploads refuse; no upload key was added.
- Independently frozen tests passed 24/24 in the author's run and this reviewer's private WSL copy, including actual normal/sanitized wrappers and three macro refusals. No assertions changed. Root's broader 145-method union also passes; original package-import invocation errors remain preserved.
- Exact 96-source hash `396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`, receipt `73d13df1e7244ddc8a71d1a7e52c0ed8`, three ELF byte sets, installed pins and default checked recipe verified.
- Final ELF `76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b`; package `567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9`. Both 19,840 bytes; differences are confined to ELF identification bytes 7–13; all section bytes and symbols agree.
- Only setup's grant differs in compiled functions from D112. Constructor path is passive; Native binds actual micros/Reader beginWithButtons/readButtons. Rank 10 A1 acquisition, no voltage read, motor/Runtime/Bridge/Serial/matrix/I2C owners, or sketch-created thread.
- Existing native guards check fixed analog pads, ADC ownership/IRQ state and nominal clock lineage; no reset forces admission. Stock driver initialization remains distinguishable from a competing post-admission producer. Live admission and SC-AJ remain unproved.
- Ordered pristine 256-KiB loader model fits: payload 16,245 B; peak 17,128 B; free span 245,016 B; largest payload 245,012 B. This is conditional allocator evidence, not measured free RAM or WCET.
- Closed draft-address issue: raw ET_REL Runner `st_value=0`, size 9,892, BSS section 8; `nm` VMA `0x1690` is not that value. RAM address is relocated BSS + 0; installed `llext_load.c:781` performs no section-address subtraction for ET_REL.

Evidence: `state/analysis/P2_ui_adc_probe_raw/reviewer/final_review.json`, `target_396bcc45_bench-default.json`, `policy_1790200987897358667.json`; unchanged full-host/native evidence is reused, with no redundant full-suite rerun.
No physical ladder/buttons/STOP/accuracy, completed acquisition, hardware acceptance, upload permission or phase pass follows.
