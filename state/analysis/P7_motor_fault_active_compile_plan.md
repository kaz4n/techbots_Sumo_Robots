# Fresh active diagnostic compilation

Use D171's existing caller once with `--execute --run active01`, after independent
host validation, source/input review, commit and the identified execution decision.
New input binding: P7_motor_fault_raw/compile_inputs_active01.json,117 pins,
SHA256b91cf39c8fec322297181e08d160a987ec4bb8d79da338c61949aa5ae5fa5f14.
Only five pins differ from compile02: config.h, the sketch, caller, board_tool.py
and app_build_policy.py. Full source filename sets remain equal. Old manifests
and their consumed scopes remain unchanged.

Selected ownership:
- local receipts: P7_motor_fault_raw/native_active01 (must be absent);
- local stage owner: build/stage/motor-fault-active01 (must be absent);
- sketch root: that owner's motor_fault child, using D170 explicit staging;
- remote: /home/arduino/sumox26_codex_build/motor-fault-active01 (must be absent),
  with motor_fault child. Retained legacy build/stage/motor_fault is untouched.

Target: ADB2629958581, UID1000/arduino, boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6.
Verify exact local ADB/remote CLI hashes, board identity, conflicting processes,
unlimited inherited file-size limit, free space and the two unchanged file-only
CLI initialization prerequisites. A changed identity or prerequisite fails closed;
do not adjust the binding during execution or automatically retry.

One properties query and one compile only, default startup/dynamic linking,
arduino:zephyr:unoq, motor_fault.ino, exact C/C++ flags:
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`.
The selector activates only the inert diagnostic configuration; this operation
does not run it. Use --jobs1, fixed minimal environment and --config-file /dev/null.

Preserve existing720s compiler/60s other child deadlines, process-group kill and
5s bounded reap, checked-command transport deadline+90s, raw output bounds and
durable first-error evidence. Require complete stage/remote file maps and normal
recipe/artifact policy. Run all independent final checks even on failure. Launch
Python-B with -X pycache_prefix=<absolute native_active01/pycache>; no global or
old bytecode cleanup. Commit the reviewed plan/source/binding before dispatch.

No upload, MCU reset/read, dependency installation, source overlay, motor run,
extra hardware or automatic retry. Scope becomes consumed after its one attempt.
Target compilation is not execution, startup, WCET, physical acceptance or a gate.
Retain useful raw/checked identities; assess only the new disposable stage after
validation, excluding every policy-denied path and all earlier attempts.
