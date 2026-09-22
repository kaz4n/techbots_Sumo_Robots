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
