# Read-only storage recommendation, 2026-09-24

No builds, deletion, target access or production edits performed. Prior cleanup preserved all21145 evidence hashes and removed only generated host objects/executables; apply the same boundary.

Safe disposable generated set, paths relative to this repository (85,484,611 logical bytes total; actual reclaimed NTFS-compressed allocation will be smaller):

- build/host_qtr_cal_robot/CMakeFiles/sumox26_tests.dir
- build/host_qtr_cal_robot/CMakeFiles/motor_gate_enabled_tests.dir
- build/host_qtr_cal_robot/sumox26_tests
- build/qtr_cal_fresh_review/CMakeFiles/sumox26_tests.dir
- build/qtr_cal_fresh_review/CMakeFiles/motor_gate_enabled_tests.dir
- build/qtr_cal_fresh_review/sumox26_tests
- build/qtr_cal_fresh_review/motor_gate_enabled_tests
- build/countdown-check.o
- build/motion-check.o
- build/ui-check.o
- build/opp-fusion-check
- build/logframe-check

Keep CMakeCache.txt, Testing/ logs, scripts and source probes. Keep build/app-receipts (5.95MB), build/p0_imu_review (10.72MB) and build/p0_pwm_irq_review (6.26MB): prior reports identify the fetched target ELFs as provenance evidence. Keep the73.44MB RM0456 Rev6 PDF: it is the exact hashed primary reference cited by multiple electrical audits. Do not blindly remove build/stage (23.97MB), memory_sources (2.54MB) or qtr_cal_fresh_review/staging_workspace; they include historical source snapshots, not just compiler objects. Exact deduplication against preserved source evidence is required first.

Additional reproducible host binaries have small upside: robot_failure_repro, p2_frame_size, p2_attempt_size and qtr_cal_fresh_review/source_era_probe; their source/scripts or build-command receipts exist. Leave the less-clearly-referenced source_era_fix_probe until its matching source is identified.

D131/D132 review draft and all private probes/failures remain saved. Latest open findings include default0 STOP+white trace classification and digraph conditional admission; no completion/gate verdict claimed.
