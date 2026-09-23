# D089 QTR calibration validation -2026-09-23 Asia/Dubai

Scope: P2 2.4/B13 actual raw-adapter -> Robot service intent -> bounded capture ->
atomic RAM threshold bank -> later classified Robot input -> real MotorGate API.
Config snippet formatting and matrix stage/progress rendering are implemented.
No physical sensor, transport printing, scheduler integration or human gate claim.

## Contract and implementation

D089/P2_qtr_cal_contract.md specifies eight requested stages,16 distinct raw
intervals per stage and a1000ms capture deadline. Every candidate threshold uses
white upper and black lower bounds; all four publish together with one version.
Native invalidity, STOP, context changes, missing freshness, stale replays and
source-era ambiguity cannot restore motion. Raw preparation retains fault/source/
receipt history. Handover requires later acquisitions, confirmation and fresh
neutral/START before the unchanged5100ms hold. No established test was modified.

Three bounded implementation owners worked on separate files. Independent test
expectations were derived from public headers/contract without D089 production
CPP access in a reused prior-native-implementation context (not a fresh author).
A genuinely fresh separate same-model reviewer inspected actual changes; this
is not cross-model review or human approval. See P2_qtr_cal_review.md.

## Observed validation (final target/review receipts appended at checkpoint)

- Root strict C++17 syntax: root_syntax.json exit0.
- Robot worker existing-focused143 cases/1,951,544assertions PASS; supplemental
  five implementation probes/6,464assertions PASS, correctly labeled nonindependent.
- Root full host: host_final.json exit0, two CTest targets PASS8.85s;
  1254main/24,477,190assertions and39enabledGate/3,843,500assertions.
- New host tests include actual eight menu requests, atomic bank, threshold
  activation, real MotorGate writes, all stage/progress pixels, export boundaries,
  STOP/context/deadline and wrap/era qualification.
- First target compile c7dde3d3 exit0,145720program/71900compiler globals,67files/
  threeELFs. Superseded by source-era repair; retained as historical evidence only.

## Preserved failures and disposition

- First new-fixture syntax used doctest REQUIRE with NO_EXCEPTIONS. Author replaced
  it with CHECK plus explicit-return preconditions; expectations retained. Display
  fixture needed initializer_list include. All original receipts are retained.
- First root full host main PASS, enabledGate failed only nonzero-after-GO. Fixture
  opp_raw_mask=0 actually asserted active-low MZ80s. Author set the inactive
  electrical mask to config::OPP_ACTIVE_LOW_MASK; kept every assertion and6000us
  observation. Final full host passes; production was not changed for this mistake.
- Fresh reviewer MAJOR: an unseen cached pre-handover frame could alias a small
  age after a full uint32 wrap. Reproduced in Robot and Calibration independently
  (review/source_era_reproducer_v2.txt). D089 source-era addendum adopted underD051.
  First bounded production repair rejects ambiguous half-range continuity and
  ties source deltas to accumulated decision age. Fixed probe returns Robot
  LINE_CONTRACT256/hold retained/no update and owner SOURCE_ORDER/no sample.
  Independent full-wrap and adjacent half-range tests now pass in the host suite.
- Reviewer initial build captured concurrent fixture REQUIRE syntax failure;
  reviewer /tmp build directory later disappeared for unknown reason. Root did
  not remove it or restart WSL. Isolated workspace rebuild retains both receipts.

## Limits and remaining work

All calibration frames in tests are synthetic fixtures, never competition or
physical threshold evidence. No actual QTR/button/motor was connected or exercised.
Compile-only uses board Linux; current MCU image remains last-known D088 inert
ui_matrix e50c6da3. No upload/reset/run is part of D089 validation. No pin, physical
button window, B16 threshold, wiring or fault-reset policy was relaxed.

The exporter is a bounded RAM formatter; actual permitted output transport remains
unfinished. App selection of raw preparation, sensor acquisition/scheduler and
lifetime management still require integration. Full RAM, independent clock SC-AJ,
Bridge hook F091, complete<800us tick and physical/human gates remain pending.

## Final accepted software evidence

- Full ASan/UBSan: sanitizer_final.json exit0,2/2 targets PASS26.44s;
  same1254main/39enabledGate cases and assertion counts as normal.
- Author scoped tooling: three initial methods PASS28.467s; additive config
  registry wrapper separately PASS; final four-method rerun follows filename-only
  .cpp->.cc isolation of tooling main fixtures from the host recursive source glob.
- Final board Linux compile-only: cc4819aabe25489ef3d8735e81a12ddb708b7bb3f452c56f8104e8cb1b1ca01c,
 145824program/72004compiler globals; exit0.67sourcefiles/3ELFs/40native42AEABI
 bindings checked; no missing math symbol. Upload-format ELF SHA256
 24a89a77f1e8c9f5c100607915a4a11bb75f9e861571147ff290fb33643e4572.
 Retains actual adapter/Robot/owner/export/render functions; setup stores only a
 function pointer and loop returns. This is compilation, not MCU execution.
- Fresh reviewer PASS/no open finding; own full host and30newcases/1900assertions
 PASS. Six existing inert registry keys independently approved then byte-checked
 and adopted; calibration probe is NOT a new upload key. Manifest adoption receipt
 records exact maps. No new upload occurred.
- Initial existing script suite was run before registry adoption and failed five
 expected old-hash subchecks; fail-closed refusal worked. No test was changed.
 Final script run uses independently approved exact hashes; receipts retained.
- Existing staging suite2methods PASS. Physical/Git/target equality is recorded
 in source_integrity.json after staging. All established locked tests remain intact.

## Frozen checkpoint

Implementation311bf40. One late independent varying-extrema/per-sensor-order
case was added before commit. Frozen full normal/san now1255main/24477205 plus
39enabledGate/3843500 PASS7.06s/28.14s (host_frozen/sanitizer_frozen).31newcases,
1915assertions. Fresh reviewer reran all31focused cases and updated review hashes.
Final4tooling methods PASS27.436s; additive registry runs18original cases. After
the added test, author variant-only rerun PASS20.501s; root variant run had already
started when that report arrived and alsoPASS (variants_frozen.json). No further
repeat needed. These are host substitutes, never successful hardware calibration.

Final25existing tool tests,5matrix-upload substitutes and2staging tests PASS.
Source-integrity67files PASS against staged Git blobs, which were committed
without further source edits. All runtime limits/phase gates remain as above.
