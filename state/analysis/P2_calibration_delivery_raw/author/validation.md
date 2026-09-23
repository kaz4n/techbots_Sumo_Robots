# D105 independent author validation

Corrected opaque Runtime run completed with exit 0. Final tested copy hashes:

- runtime.h: c4bc1e97bc7c88521cf9a31b6a31e9e370ad371a54dfb95cdc98f96cb71717d0
- runtime.cpp: 5c10dda3eb1b2f071c7da7b8965520c8b99447d51e1f8590579e4dbc2bc75015
- runtime_dump.cpp: aedd9c81b39e524cbdda00dc0d4be7614001935b6d6001d3071c7a47b913d4df
- runtime_calibration.cpp: 18bf09803ad4140ac16ffe57646953d81020c16cadcaccb8539b31f48c60c3e6

`python -m unittest tests.tooling.test_app_calibration_output -v` delegates to
Linux/WSL for isolated `/dev/shm` builds. Non-MATCH normal and ASan/UBSan each
passed 26 cases / 8,441 assertions. MATCH normal and ASan/UBSan each passed
3 cases / 342 assertions. The separate short total-deadline sanitizer profile
passed 1 case / 47 assertions. Both non-MATCH runs produced the actual calibration
snippet and decoded it through the strict parser as `[350,350,350,350]` with
explicit timeout 1500 and UNATTRIBUTED_BARE_LINE provenance.

`wsl.exe --exec python3 -m unittest tests.tooling.test_qtr_config -v` passed all
10 parser/CLI methods, including symlink and FIFO cases without skips. Tested
parser SHA-256 cf09e26903417ba8f15a05cf1acf221eb2fd42239c24d0129eea209600c07562.
No Python/C++ D105 implementation body was inspected by this author.

Test files and hashes:

- calibration_output_cases.cc: 536098a9cfc317dd9d688a1561c10ddcf24f169805dd5f56bf37459f01a9f691
- test_app_calibration_output.py: 5546af5ee81ccdd8720d0018b7bff94fa3a7699908d1d57b16a24b494a8aa411
- test_qtr_config.py: 5d8b66a1d1059d99e6d663fa5ca9ecd8b63d68f295d1ddbb3d230b8af4574d49

Original first-run failures, original frozen C++ file and reviewer-approved
fixture corrections are retained in runtime_run1, command receipts,
calibration_output_cases_v1_frozen.cc and fixture_correction.md. No established
or locked assertion was changed. See coverage.md for unavailable public-owner
branches and the explicit independence boundary (prior D104 runner context).

Evidence: runtime_run2.json/txt, parser_run1.json/txt, append-only command,
opaque-source and actual-roundtrip JSON receipts. runtime_received_snippet.txt
is the exact 50-byte decoded fixture artifact; its receipt binds the actual
roundtrip and SHA-256 14ed0942477c6af355bf565c59fa6f9968bece61050805892fe29625db15dfd0.
No board, UART, physical calibration, motor or gate result is claimed.
