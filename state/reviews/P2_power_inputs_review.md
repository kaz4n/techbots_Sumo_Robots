# D093 fixed ADC input-owner review

2026-09-23 Asia/Dubai. Separate fresh-context same-model reviewer; review-only production scope.
Baseline8e4544a, contract/headerd248782; reviewed AGENTS, safety-auditor role, precise D093 contract and actual implementation.

Findings: no open BLOCKER, MAJOR or MINOR in this bounded scope.
- `src/hal/power_inputs.cpp:102`: setup is attempted once; exact result admission, first-fault precedence and suppression agree with the contract.
- `src/hal/power_inputs.cpp:130`: source-bracket validation and saturating accumulated age prevent replay/cache revival; A1 failure invalidates young A0 immediately.
- `src/hal/power_inputs.cpp:201`: projection preserves unrelated inputs and turns rejected/faulted buttons into explicit INVALID.
- `src/hal/power_inputs_unoq.cpp:17`: actual Reader factory and new owner constructor are passive; no fresh native path starts in the seven existing inert sketches.
- `bench/p2_power_inputs_compile/p2_power_inputs_compile.ino:6`: actual target setup stores only a pointer; loop/strong hook return immediately; no upload key exists.

Evidence inspected:
- Reviewer normal and ASan/UBSan:6 cases/20059 assertions each PASS, including1350 source-bracket tuples and exhaustive enum/validity/reversed-clock priorities.
- Initial reviewer include/macro mistakes and aggregate/check-out ordering assumptions are retained in raw; only reviewer harnesses were corrected.
- Exact358 established source/test/tool files unchanged from baseline, allowing explicitly recorded pre-existing checkout CRLF; old core/locked/native tests remain intact.
- Seven prior inert hashes reconstructed exactly; current candidates change only config.h plus three new power_inputs files. Candidate map independently matches coordinator staging.
- Actual compile-only4d5e21cc:76 physical/target source files exact;3 retained ELFs,40 native/42 AEABI mappings and undefined imports unchanged from D092; constructor relocations inspected.
- Compiler321652 program/241524 globals,20620 residual; low-memory warning preserved. This is not measured loaded free RAM.
- Coordinator tools/test_host.sh and ASan/UBSan each PASS2/2:1327 main/24484165 assertions plus111 enabled-Gate/3850460; LastTest and sanitizer flags preserved.
- Independent author24 owner cases/2421 assertions per motor mode,5 native cases,2 seeded-limit cases,15 config profiles,2 inert-probe modes,8 upload refusals and additive registry PASS;61 existing tooling checks PASS.
- Initial new-test include and ternary-macro decomposition failures are preserved; explicit include/temporary bool fixes preserve expectations. Current production/test hashes match final receipts.

Verdict: PASS for D093 software/compile-only evidence; not a cross-model review, human approval or phase pass.
No reviewer hardware command, upload, reset, install, push or commit. D091 deployed inert runtime cannot establish D093 runtime.
Actual app scheduling, electrical/ADC/button/clock accuracy, full800us WCET, loaded RAM, physical acceptance and human gates remain unqualified.
