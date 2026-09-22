# P0 actual board build recovery, 2026-09-22

Target ADB2629958581, board user arduino, CLI1.5.1/core1.0.0. User D-052 authorizes
bare-board inert testing. Native Python drives explicit USB ADB; compile executes
on UNO Q in /home/arduino/sumox26-build/<source hash>/p0_timing. Every attempt below
uses --compile-only, MATCH=0 and MOTORS_ALLOWED=0, default dynamic/wait startup.

1. P0_timing_target_compile_20260922.txt: exit1, missing core/motion.h through
   edge.h. Host -Isrc masked unsupported internal include paths. No upload.
2. Independent staged regression reproduced10 failures; eight include-only fixes
   now pass unchanged2 cases. P0_staged_core_green_20260922.txt exit0, plus host
   rebuild P0_include_fix_host_20260922.txt CTest1/1 exit0. Separate exact-source
   review PASS; no established locked-test or config changes.
3. P0_timing_target_compile_fixed_20260922.txt: include error resolved; exit1 on
   core's mandatory Arduino_RouterBridge stub. This is a distinct missing
   installed dependency, not a second failed include repair. No upload.
4. Installed postvariant.h and official1.0.0 source confirm forced Bridge library
   discovery, even though this diagnostic never invokes Bridge/Serial/Monitor.
   Actual CLI `lib deps` resolves RouterBridge0.4.3, RPClite0.3.1, MsgPack0.4.2,
   ArxContainer0.7.0, ArxTypeTraits0.3.2, DebugLog0.8.4. Installed all six explicit
   versions with --no-deps --no-overwrite, exit0, prior library list empty.
   P0_board_libraries_install_20260922.txt preserves the installation receipt.
   No global WSL package or credential needed. Graphics is optional and omitted.
5. Repeat compile-only with those dependencies: exit0, recorded separately in
   P0_timing_target_compile_deps_20260922.txt. Default matrix also exit0 in
   P0_matrix_target_compile_20260922.txt. Only one include repair was needed.
6. Separate installed constructor/loop-hook inspection and review found no blocker
   for this bare-board inert artifact. Timing upload then completed exit0 at
   23:19:29+04; P0_timing_upload_20260922.txt. No debug attachment has yet occurred.

Primary sources checked:
- https://raw.githubusercontent.com/arduino/ArduinoCore-zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/postvariant.h
- https://raw.githubusercontent.com/arduino-libraries/Arduino_RouterBridge/0.4.3/library.properties
- https://raw.githubusercontent.com/arduino-libraries/Arduino_RPClite/0.3.1/library.properties

Two attempted unprefixed GitHub MsgPack/ArxTypeTraits tag URLs returned404; no
claims derive from them. Exact installed index/package provenance is recorded
separately. Dependency installation is not MCU execution, a Bridge timing proof,
R4 compliance or a passed gate. Inspect constructors before an inert upload.
