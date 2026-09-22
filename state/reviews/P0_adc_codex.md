# P0 ADC scoped fresh review, 2026-09-23

Verdict: **PASS** for the exact D-063 inert/default diagnostic and passive capture; no open BLOCKER, MAJOR or MINOR.
Fresh separate same-model Codex reviewer; read-only except this report. Base 093a256; no board command, upload, debug attachment, register read, source/test/ledger edit or human gate.
Read AGENTS.md, .claude/agents/safety-auditor.md, P0 prompt, PLAN schedule, FACTS, PROGRESS, D-051 through D-063, ADC contract and installed/target audits. Local date 2026-09-23 matches scheduled P0 finish/P1; P0 remains active with no gates.

- PASS bench/p0_adc/p0_adc.ino:8-32: motor-enabled builds and changed A0 mapping reject; exactly 1000 ADC calls occur in setup, raw signed returns and paired clock overhead are retained, complete follows all record stores, and loop is empty. No sketch motor/PWM/GPIO output/Bridge path.
- PASS bench/p0_adc/src/adc_capture.h:8-26: volatile zero-initialized record, 12-byte samples and 12020-byte capture; source and host tests preserve first-use/subsequent costs and incomplete prefixes.
- PASS tools/p0_adc_capture.py:41-64: exact version/count/length, signed error and 10-bit range validation, wrap-safe intervals, non-overflowing aggregate checks and nearest-rank p99; zero remains valid and overhead is not subtracted.
- PASS tools/p0_adc_capture.py:67-145: reviewed helper hash enforced; exact artifact hashes/layout precede full loader/sketch comparison; two identical records and subsequent LLEXT identity check precede metrics acceptance. Maximum four-node traversals fit the existing 16-read cap; each record is below 16384 bytes; shared 120-second attachment deadline is retained.
- PASS tools/board_tool.py:182-223: ADC upload is default-only and source-allowlisted; Immediate/motor uploads reject before transport, failed compile prevents upload, and compile-only never uploads. Matrix Immediate prohibition remains.
- PASS src/config.h:118-119 and tests/tooling/test_p0_config.py:18-19: only two diagnostic constants added; all 76 B16 defaults preserved. No established locked test or passive helper/config changed from base.

Independently reconstructed exact staged filemaps: matrix 28 files, timing 24, ADC 25; all match P0_adc_inert_manifest_proposal.json and the refreshed allowlist. Matrix/timing differ from base only in the two config additions.
Approved matrix SHA256: aabfdebb058374ef7470415a10386044ac417e65e342ecf75b476cb3381051b3
Approved timing SHA256: 3ff0baba7122be37b6747905d9ca205583a7539ee81142b3df262712113c57ae
Approved ADC SHA256: f5f637b2f0799a3b08d9c4c1897c6706842e0a5ffd737e355d409ed881989c1c
Capture source SHA256: 8e27a440d7dac4be44539f6fd1b434af0b7b291e408db4b24cd8f7322a81e57d; unchanged helper 885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c.
Capture pins match separate P0_adc_binary_audit_20260923.md: ELF a8e02489b14145f06312db3578e3349033e8b07e732beb5baeebcb8ea3a66683; dynamic/default wrapped ELF 2cff4f0635d45c2d75c75c6b0f96444d7e28fec088973835b7b4038061d84fba; each 74636 bytes, BSS 19572, p0Adc offset 4/size 12020.
That auditor inspected final constructors/main/static threads/relocations and selected RouterBridge hook: no begin/worker, started=false, uncontended lock path, no post-setup transport/peripheral call. This reviewer checked its report and pin agreement, not the board binary directly.

Independently ran WSL tools/test_host.sh: build and CTest 1/1 PASS (2.77s); ADC 24/24, config 8/8, capture boundary 12/12 and corrected upload guard 5/5 PASS. No hardware was used by these tests.
Initial upload test had two subtest failures at test_p0_adc_upload.py:32: it expected bare flags instead of complete CLI build-property arguments. Coordinator corrected this new unlocked assertion to require both exact properties; independently reran successfully. Original failure and correction remain in P0_adc_failure_analysis.md and the initial receipt.
Final coordinator receipt P0_adc_tooling_20260923_final.txt: 197/197 tooling tests PASS (65.791s), plus diagnostic doctest 25/25 and 156553 assertions PASS.
Limits: fixed call count does not bound ADC completion; setup may hang. Floating A0 codes prove no voltage accuracy, battery/button acceptance or pin-map approval. Completion is checked after attachment, so record the quiet upload-to-attach interval and retain possible debug overlap; no independent unperturbed timing claim.
Next action: only the exact reviewed inert/default D-052 upload/capture is eligible. Verify deployed full-image identity and frozen records before reporting measured values. No production ADC HAL, complete-loop WCET, STAND/RING authority, PINMAP OK or human phase gate follows.
