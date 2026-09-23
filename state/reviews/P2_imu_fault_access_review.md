# D097 independent setup-fault access review

2026-09-23 Asia/Dubai; contract cf3dfe1, D096 source 4cb637f9 baseline.
Read-only reviewer; writes limited to this report and P2_imu_fault_access_review_raw.
No implementation, established tests, shared build, board operation or commit by reviewer.

BLOCKER, open: src/app/app.ino:13 full app needs 275760B versus 262144B (13616B excess).
Actual target compile exits 1 for source 570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84.
No new getter/callback finding; exact source and linked evidence do not turn failure into acceptance.

src/hal/imu_acquisition.cpp:55 returns exact result_ only for actual setup FAULT.
The const getter performs no bus, clock, allocation, observer or lifecycle operation.
src/app/native_sources_unoq.cpp:45 ignores callback time and calls only the getter.
Legacy read, setup, mixed-API cancellation and asynchronous implementation are unchanged.
Runtime::setupImuFault at src/app/runtime.cpp:124 still publishes only once after setup FAULT.
Independent ASan/UBSan executable: 3 cases, 685111 assertions PASS (reviewer_cases.json).
All 48 setup-request failure positions, wrap/start failure and every Sample field checked.
Repeated getter reads preserve object bytes and all scripted Bus call counters.
Default absence covers pre-start, setup pending/ready, observations, runtime pending/fault.
Pending reads still finish once with sequence/gap preserved; returned-value edits stay local.
All 82 current source files match the receipt; three ELFs remove read/acquireMotion, retain setup/async.
Measured saving: 696B text only; the new 56B getter calls memcpy/memset, callback calls getter only.
All 188 imports, 40 native/42 AEABI export addresses, loader and 12 initializer targets unchanged.
setup/loop/main/strong loop hook/app initializer words and relative relocation targets unchanged.
Evidence: target_comparison.json, startup_comparison.json and native binding_object.json.
Seven existing inert keys and all 82-86 staged file hashes match independent reconstruction/refresh.
No new key/app upload grant; root tools/test_host.sh and sanitized final reruns PASS, 2/2 CTest targets each.
Original new-test REQUIRE build failures and three reviewer script mistakes remain; no old tests weakened.
No pins/config/capacity/rate/startup change, loaded RAM, timing, physical acceptance or human gate inferred.
Final verdict: FAIL for the open full-app RAM BLOCKER; bounded getter/callback contract PASS.
