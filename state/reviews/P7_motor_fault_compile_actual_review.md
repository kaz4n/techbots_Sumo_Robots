# D165 actual compile receipt review

25 September 2026, Asia/Dubai. Separate same-model reviewer, D164/pre-run context.
Verdict: collection/containment PASS; target compilation FAIL (one MAJOR).
Only local receipts inspected; no board command or compiler run by reviewer.
Preserve the pre-run report; this report assesses the actual attempt separately.

MAJOR bench/motor_fault/src/motor_fault.h:15 at attempt commit 3c291ea2:
CONFIG_PWM collides with native autoconf.h:402 (#define CONFIG_PWM 1), preventing
compilation. Rename CONFIG_ENABLE/CONFIG_PWM to CONFIGURE_ENABLE/CONFIGURE_PWM
without changing enum ordinals, then verify macro coexistence under a new scope.

All 117 manifest pins were independently exact before completion; final local
check passed. The 104 staged filenames/hashes match pinned inputs, saved evidence
and both remote source-set receipts. Independent source digest:
4ec345c0699866733ccc747f858cb3b30ba7b7f9a3e5687a4433fd6571402284.
All 122 transports exit 0 (including 104 pushes); nine checked child receipts
match actual packet argv/env/deadlines and exact raw streams. One query and one
compiler use --jobs 1, explicit CLI/config/env and M0/MATCH0. Compiler exit 1,
reaped=true, timed_out=false, 720-second limit; all seven final checks PASS.
Both prerequisite observations equal baselines; all 18 installed hashes remain
equal and final overrides are absent. No upload/reset/native runtime call occurred.
Final result e0d116e3 retains the primary CalledProcessError. Original compiler
JSON a8118922 is exact; app text receipt differs only by Windows CRLF conversion.
Receipt 9a3d963521ce419083aa0cc000656dfb has no verified.json, so no checked
artifact identity exists. This attempt is consumed; preserve its source/failure
evidence. Startup, physical behavior, motor timing, WCET and gates remain unqualified.
