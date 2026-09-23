# D-072 preserved failures and first repairs

1. Full normal CMake build exited2: promoted candidate fixture lost doctest-main's
   transitive initializer_list include. Test author added only the direct standard
   include to test_recorder_rate.cpp. No assertion changed. First repair builds and
   all975 normal and ASan/UBSan cases pass. normal_build.txt/json preserve failure;
   normal_build_retry1 and later test receipts preserve actual successful commands.
2. Fresh reviewer found a MINOR literal-editor ambiguity: conditional-only rates,
   backslash-spliced macro/comments and a duplicate rate array were accepted before
   copying. Independent author added rejection fixtures plus a positive closed-
   unrelated-guard fixture without reading implementation. Expected red run exits1
   (23tests,10 malformed subcases reach forbidden copy, plus aggregate mock failure).
   probe_tests_parser_red and parser_pre_fix retain evidence. First repair rejects
   line splices, requires the declaration outside conditional nesting and detects
   array duplicates. Same23 tests then pass; reviewer independently reproduces.
   Source/body of firmware, locked tests and earlier successful target ELF unchanged.

No second unsuccessful repair occurred; no escalation threshold was reached.
Do not erase/redescribe the red run as a passing suite. Full338 tooling pass predates
this repair; all_tool_tests_final is the separate final-source regression receipt.

Sanitizer build reported WSL makefile timestamp skew0.19/0.16s. Raw warning is
retained. Build exited0, rebuilt/linked the current test target and ran975 cases
with15667813 assertions successfully. Reviewer verified current inputs; no source
failure or repeated build is inferred from that warning alone.

Windows free space fell to about28MiB during builds. Only the two coordinator-owned
prior D-071 host-check binaries (normal1070208B/sanitize16165848B) were removed
after absolute-path containment checks under build/memory_sources. Source trees,
recipes, results and committed target ELF evidence remain. Subsequent free space
was45.32MiB; no unrelated/user artifact was deleted. Avoid new dependency installs
or retaining redundant generated binaries while disk space remains limited.
