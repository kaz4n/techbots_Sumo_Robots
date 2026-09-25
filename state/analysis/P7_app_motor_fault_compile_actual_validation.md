# D188 actual inhibited static diagnostic compilation

TARGET-COMPILED / REVIEWED at 2026-09-25T19:11:07.512225+04:00. Reviewed source commit65b6d80e8a16b7178446014f498795e16a56a944.
Source21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950.
User-connected board2629958581, freshly checked boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8.
Fixed static/default/MATCH0/MOTORS_ALLOWED0/probe1. Existing implementation,
firmware, locked tests and installed dependencies unchanged.

Exact local check-only and native commands/exits are in
[P7_app_motor_fault_compile_raw/native_static01_invocation.json](P7_app_motor_fault_compile_raw/native_static01_invocation.json).
Check-only exit0; single execution session33591 exit0. Started15:01:33.336664UTC,
finished15:07:22.187446UTC. Result COMPILE_CHECKED,1query/1compiler/236transports,
all8closing checks PASS. Query1.646s, compiler226.963s, all9children reaped with
exit0/no timeout. Remote owner app-motor-fault-static01 and local native_static01
are consumed; never rerun. No upload/reset/MCU read/run occurred.

[Actual review](../reviews/P7_app_motor_fault_native_actual_review.md) independently
checked127inputpins,107stagedfiles, before/after source/inventory/18installedpins,
transport/child receipts and equal artifact observations. Separate same-model
reused context, no material findings; this is not a phase gate.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| artifacts/app_motor_fault.ino.bin-zsk.bin | 95328 | deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c |
| build/app_motor_fault.ino.bin | 95312 | 18598e13f2b5601db504f5272826b0952b95477dd2b1b8d397d20bd2ff899144 |
| build/app_motor_fault.ino.bin-zsk.bin | 95328 | deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c |
| build/app_motor_fault.ino.elf | 172632 | 2f8dc9f1bfece1e1e5e653cfbfcdf2b6ad43f62c9c666001b93e0c81722073a9 |
| build/app_motor_fault.ino.elf-zsk.bin | 172632 | 5202b44ce69bb17060dcf0ba3cfc8863a6455e81bd13c321b07ae26e6fdc5def |
| build/app_motor_fault.ino.map | 449228 | 839312197419f3ccc2e22d12708bf54f5e8e044732eeea13de9adbf34bfc4f44 |
| build/app_motor_fault.ino_debug.elf | 1836644 | d11a21035b384a66160ece2cf6112c3f199d3e200e6e3077ff747d05620cd7c3 |
| build/app_motor_fault.ino_temp.elf | 1836644 | d11a21035b384a66160ece2cf6112c3f199d3e200e6e3077ff747d05620cd7c3 |

D187 static layout/package and native TLS checks PASS. Static entry0x08100011;
RAM region0x20013890..0x2003d400 leaves91280B to0x20053890. CLI instead reports
170868Bglobals/91276Bremaining. These file-derived figures are not observed
runtime headroom, heap/stack safety or WCET. No warnings emitted with -w enabled.
No new ABI offsets, runtime success, physical qualification or human gate follows.
Last uploaded image remains D184's halted isolated inert diagnostic.

Next: file-only ABI/initialization observations of these exact static/debug files,
then review a distinct identified inert upload/capture scope. Do not reuse D149
addresses, D1732592Bdecoder or dynamic llext relocation. Original D160/D161
first-callback cause, production default592Bmodeled deficit, physical inputs,
RAM/stack/WCET, release/rehearsal and human gate evidence remain open.
