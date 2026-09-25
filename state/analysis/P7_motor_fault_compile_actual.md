# D165 actual target compile: failed macro collision

25 September 2026,05:44:32-05:45:44 Asia/Dubai. TARGET-COMPILE-FAILED; scope consumed.
Reviewed HEAD3c291ea2, callerf804f452, input manifestd1ba918d, staged source
4ec345c0699866733ccc747f858cb3b30ba7b7f9a3e5687a4433fd6571402284.

One properties query and one actual compiler were invoked. All122 ADB transports
returned0. The compiler child returned1, was reaped and did not time out. All seven
independent final checks passed: local inputs, identity, two prerequisite checks,
remote source set, installed pins and overrides. No upload, reset or MCU read.
The board reported14,102,024,192 free bytes initially and the expected UID/boot/CLI.

The installed generated Zephyr autoconf.h defines CONFIG_PWM=1 at line402. It
collides with the diagnostic enum identifier in bench/motor_fault/src/motor_fault.h:15,
causing the subsequent parse errors. This is an actual target-only integration
defect; prior host results do not prove target compatibility. No valid new target
artifact or startup claim follows. The native150us safety limit is untouched.

Raw evidence: P7_motor_fault_raw/native_compile01/result.json and the122 numbered
command folders; compiler evidence is0116-checked-command/child.stdout and its
remote_result.json. Outer reviewed-head/exit/timing evidence is
P7_motor_fault_raw/compile_native_invocation.json. Source filenames/hashes are in
native_compile01/staged_files.json. Policy receipts remain in
build/app-receipts/9a3d963521ce419083aa0cc000656dfb; no verified.json was emitted.

Next: rename the two CONFIG_* diagnostic enum labels to CONFIGURE_ENABLE and
CONFIGURE_PWM, retaining their numeric values and behavior. Adapt only corresponding
public test identifiers and add an independently authored regression that compiles
with the observed CONFIG_PWM macro. Preserve this failure and consumed ownership;
any later target compile needs fresh paths and an explicit source binding. Motor
capability, physical acceptance and human phase gates remain unavailable.
