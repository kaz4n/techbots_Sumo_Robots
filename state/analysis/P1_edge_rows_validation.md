# B4.2 specified rows — 2026-09-22 Asia/Dubai

Status: HOST-TESTED at component scope; full Escape/Robot remains unfinished.
Contracts76e0360/c5e80b8 precede separate implementation and independent tests.
Worker owns edge.cpp; separate author reads specifications/public headers only
and owns test_edge_rows.cpp/report. Root owns headers/config/state/build files.

Supported selected masks1,2,4,5,6,8,9,A,C cover single-front, diagonal, rear and
side rows. Each segment starts at its actual observation; no backdating or
synthetic inward heading. Brakes and terminal results request zero. Governor
profiles and Guard veto remain explicit requirements on callers. Unsupported
head-on/three-white masks do not imply an approved fault/recovery policy.
All76 B16 values remain unchanged;45-degree side angle centralizes existing text.

Actual coordinator commands/results:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1;
  P1_edge_rows_build.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit0;
  P1_edge_rows_sanitizer_build.txt.
- `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0;
  P1_edge_rows_sanitizer.txt, **478 cases / 11,897,401 assertions**, no fail/skip
  or ASan/UBSan diagnostics.
- Worker strict C++17 syntax check reported exit0 with -Wall/-Wextra/-Wpedantic/
  -Werror/-Wconversion and no exceptions/RTTI. Root inspected actual source diff;
  git diff --check exit0.

34 new independent locked tests are now established and protected. They cover
256 mask values, exact/adjacent timing/angle limits, entry headings, timeout ties,
delayed calls, finite/nonfinite/IMU gaps, reset, wrap,10000 balanced mirrored
streams and Guard/governor composition. Existing locked tests were unchanged.
No failing production test or repair attempt occurred in this batch.

Separate reused read-only review PASS/no open findings; independent host totals
agree. Context limitation and exact approved23-file inert hashes are recorded in
../reviews/P1_edge_rows_codex.md. Full fresh phase review remains pending.
Controlled tooling checks after approved manifest refresh are recorded separately
in P1_edge_rows_tools.txt. These are script tests, never a target build.
`wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` passed48/48,
exit0. Implementation/new locked tests committed970e083.

No board connection, target compilation, upload/reset, motor run, physical timing,
trajectory, pin approval or human phase gate. SC-AC and earlier protected choices
remain unanswered; no approval is inferred from working on this row subset.
