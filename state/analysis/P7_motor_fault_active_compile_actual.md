# D172 active inert diagnostic target compilation

25 September 2026, 06:57:06–07:01:10 Asia/Dubai. TARGET-COMPILED.
Reviewed execution HEAD6bf5ecb1; actual evidence committed db1228ce.
Separate reused-context same-model actual review41ecc2c9: PASS, no findings.

One properties query and one compilation ran on UNO Q ADB2629958581,
UID1000/arduino, boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6.
FQBN arduino:zephyr:unoq; default wait startup and dynamic linking; jobs1.
Exact C/C++ flags: MATCH=0, MOTORS_ALLOWED=0, SUMOX_MOTOR_FAULT_PROBE=1.
All123 transports and ten child commands exited0. Every child was reaped without
timeout; compile226.631s within720s deadline, outer invocation244.092s.
All seven final checks PASS; no first error. No upload, reset or MCU read.

Current117 input pins and12 frozen host pins match. The104 source pushes,
local stage and both remote source maps match; previous manifests and retained
legacy stage are unchanged. Both query and compile match84 controlled properties.
Full source SHA256:8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36.
Input manifest SHA256:b91cf39c8fec322297181e08d160a987ec4bb8d79da338c61949aa5ae5fa5f14.

Exact artifact paths and18 installed hashes are in
P7_motor_fault_raw/active_verified.json (5241B, SHA45ec0da9).
Final ELF:f9460a16cb010d6a72d2304a9fe23f7b5a82aff486af2fe3a641abe2f96b0d81.
Debug ELF:7a4b2953f74e08eb80667466dc03f0d4f849f54f68bb6327cb4240b73f8a8b8f.
Export:b4416792a5bc228f34712fad9199a07c3c480aace979faa88aa12b50288b0a79.
Compiler reports29836B program/10432B globals. These are not live RAM, loader
viability, callback execution, original-fault causation or WCET measurements.
D160 remains the last upload; the active diagnostic has not run.

Raw packet: P7_motor_fault_raw/native_active01/ (525files/890157B), plus compact
invocation/metadata. All528 committed raw blobs byte-match working files. No
firmware binary downloaded. Review: ../reviews/P7_active_compile_actual_review.md.
This compile scope is consumed; do not reuse or repin it.

Next: bounded file-only final/debug ELF ABI and exact upload-recipe observation,
as mapped in P7_motor_fault_capture_dependencies.md. A later inert upload/capture
needs its own source/artifact scope and tested finite decoder. Physical/human
gates and motor-run permission remain absent.

Storage: cleanup of the exact new104-file/764719B stage was rejected before
execution by automatic approval review (blocked by policy, no further reason).
Read-only follow-up confirms it unchanged; no alternate deletion attempted.
Both legacy and active stage paths must remain excluded from implicit deletion.
See storage_cleanup_20260925_motor_fault_active01.json. Incremental Git packing
reclaimed720896 Git-reported bytes; new pack/connectivity and unchanged HEAD,
refs/reflogs verified in storage_repack_20260925_d172.json.
