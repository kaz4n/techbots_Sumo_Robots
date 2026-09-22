# P0 0.4 ADC startup timing: validation and limits

2026-09-23 Asia/Dubai. D-063 contract7a88867 and verified signed-error correction
14f52d0 preceded code/tests. Bare-board authority D-052; no external connections
requested, no motor capability. P0 acceptance and P1 human gates remain pending.

## Software and target evidence

- Installed audit: P0_adc_installed_contract_20260923.md, F-078. A0 maps to
  PA4/channel9/index14; default return10-bit. Both ownership and conversion can
  wait indefinitely. ADC calls belong solely to this diagnostic's setup.
- Independent spec/header author:24 sketch/decoder cases and12 capture-boundary
  cases PASS;8 config cases PASS. Sketch compiled with C++17/g++13.3 and UBSan.
  Receipts: P0_adc_host_tests_20260923.txt and
  P0_adc_capture_boundary_tests_20260923.txt. No implementation inspection by author.
- Coordinator's5 new upload cases cover SSH/ADB default-only, matching artifacts,
  compile-only/match, changed source and failed compile. First run185 tests had
  two assertion failures in one new argument-format expectation. Corrected to
  assert both exact CLI properties; P0_adc_failure_analysis.md retains context.
- Full final tooling:197 tests PASS,65.791s, exit0. First/final receipts are
  P0_adc_tooling_20260923.txt and P0_adc_tooling_20260923_final.txt.
- Actual board-side compile-only: P0_adc_target_compile_20260923.txt, exit0.
  Sourcef5f637b2/default/MATCH0/MOTORS_ALLOWED0;74636B program/42384B globals/
  219760B remaining per compiler (not measured stack headroom). No upload during
  this compile. Full source map: P0_adc_inert_manifest_proposal.json.
- Separate exact target audit: P0_adc_binary_audit_20260923.md PASS, no findings.
  ADC setup/native dispatch, constructors, static-thread section and selected
  upstream weak loop hook inspected for this image. No Bridge start or motor path.
  Correct dynamic image is .elf-zsk.bin74636B, not separate .bin-zsk.bin41372B.
- Fresh same-model scoped review: reviews/P0_adc_codex.md; independently checked
  source maps,32 diagnostic/config and12 boundary tests,5 upload cases, and full
  core CMake/CTest. This is neither cross-model review nor human gate acceptance.

## Frozen identities

- ADC source f5f637b2f0799a3b08d9c4c1897c6706842e0a5ffd737e355d409ed881989c1c.
- Final ELF a8e02489b14145f06312db3578e3349033e8b07e732beb5baeebcb8ea3a66683.
- Wrapped dynamic image2cff4f0635d45c2d75c75c6b0f96444d7e28fec088973835b7b4038061d84fba.
- BSS19572B, p0Adc offset4/size12020. Existing helper and passive config unchanged.
- Current reviewed source maps additionally update matrix toaabfdebb and timing
  to3ff0baba; those sketches differ only by the two unused ADC config constants.
  Manifest refresh followed independent exact-file review. No old runtime result
  is transferred to these new source identities.

## Physical status

At this pre-upload checkpoint, no ADC measurement has run. Upload/capture receipts
will be appended only after execution. The current MCU still runs75ab5a22 matrix.
The measurement will separate sample0 first-use from999 subsequent raw API calls
and retain paired micros overhead without subtraction. Negative errors/incomplete
records fail acceptance; zero is valid. Setup liveness is not guaranteed.
Floating input codes prove no battery voltage, divider, accuracy or electrical
acceptance. Completion is checked after debug attachment; without independent
pre-attach completion evidence, possible debug overlap remains explicitly open.
No empirical maximum can override the proven unbounded driver or satisfy full
control-loop R4. GPIO/QTR, cold-start, optical, external hardware and human gates
remain separate. No B16 tuning, locked-test modification, motor action or P2 work.

## Actual upload

Revision9de8cd1/sourcef5f637b2 was rebuilt and uploaded to USB2629958581 at
2026-09-23 02:16:28.363+04, exit0; default/MATCH0/MOTORS_ALLOWED0. This replaced
the matrix/counter image. Receipt: P0_adc_upload_20260923.txt. A quiet interval
of at least60s is planned before passive attachment; its actual timestamps will
be retained. This paragraph supersedes pre-upload status above, not the remaining
measurement limits. Upload success alone does not establish completed ADC calls.

The9de8cd1 staged whitespace check flagged one trailing space in the preserved
initial failed unittest transcript. That raw evidence was retained verbatim;
there is no claim that the complete staged raw-receipt whitespace check passed.

## Actual MCU measurement

CAPTURED, remote/local exit0; raw transfer exit0. Same-host upload-end to capture
invocation wait was70.994558s. Board first passive read requested at02:17:40.437+04;
board and host clocks differ, so do not subtract them for a precise quiet interval.
Readout took109.156586s,
inside the unchanged120s attachment deadline, with10 reads/14 commands, all exit0.
Every deployed loader/sketch byte matched the pinned images. Two12020B frozen
records were identical; same extension/BSS mapping was confirmed afterward.
RAM header: version1, complete1, completed1000, start419450us/end563566us.

| Actual statistic | Result |
|---|---|
| First raw analogRead call (including any first-use initialization) |276us |
| Subsequent999 calls |minimum139us, maximum140us, nearest-rank p99140us |
| Paired micros overhead,1000 samples |minimum1us, maximum2us, p992us |
| Complete setup acquisition interval |144116us |
| Raw returned codes |124..306;1000 nonnegative/nonzero, no API-reported error |

No overhead was subtracted. The finite observed maximum is not a whole-call
deadline. Floating codes are not volts. The70.995s same-host quiet interval and frozen records
do not independently prove completion before first debug attachment; possible
overlap remains a stated limitation. No timing claim transfers to a full robot.
Evidence: P0_adc_capture_20260923.json, P0_adc_capture_invocation_20260923.json,
and39 files in P0_adc_run1_raw/ (10 binary reads,28 command streams, capture.json).
Coordinator independently checked all10 dumped lengths/hashes and the raw header.
