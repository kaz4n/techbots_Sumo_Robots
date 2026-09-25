# One inert diagnostic compile

Scope: compile bench/motor_fault once through D164's existing checked policy,
default startup, dynamic link mode, MATCH=0 and MOTORS_ALLOWED=0. No upload,
reset, MCU read, extra hardware, source overlay or production admission.

Caller: P7_motor_fault_raw/compile_motor_fault.py. Input file compile_inputs.json
pins the caller, full src/ and bench/motor_fault/ sets, tools/recipes/installed-pin
manifest, wait/reap helper and two CLI initialization baseline receipts. Historical
consumed app probes and their original bindings remain untouched.

Target: ADB2629958581, UID1000/arduino, boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6.
The caller verifies the ADB and /usr/bin/arduino-cli executable hashes, uses
--config-file /dev/null and an explicit minimal environment. Fresh file-only
initialization prerequisites must match before any CLI invocation. At least1GiB
board and128MiB local free space are required; conflicting build/upload processes
cause refusal. The initial board check is read-only.

Local native_compile01 and remote motor-fault-compile01 are exclusive ownership
paths; no retry or reuse. Require build/stage/motor_fault absent before staging,
then push exact files with bounded ADB calls and compare complete filename/hash
sets before and after. Do not touch existing app stages or checked artifacts.

The explicit executor supplies --jobs1, Popen(shell=False,start_new_session=True),
720seconds for compilation and60seconds for other child commands. The unchanged
wait/reap helper kills the process group on deadline and waits at most5seconds;
the checked-command transport budget is child deadline+90seconds. No inherited
file-size limit may constrain compiler artifacts. Preserve actual argv/environment,
stdout/stderr, child exit/deadline/reap and all failures. Separate final checks
cover local inputs, identity, prerequisites, remote sources, installed pins and
overrides; a successful compiler alone cannot override a failed final check.

Launch Python with -B and -X pycache_prefix=<absolute native_compile01/pycache>,
then the fixed script and --execute. This per-process fresh cache location avoids
old caches without deleting them or modifying global configuration.

Before execution: commit exact inputs and separate source/manifest/child-control
review. Child-control tests use real harmless Linux subprocesses in RAM; they are
not board evidence. After execution: inspect actual checked compile results,
retain source/artifact identities and required diagnostics, assess disposable
staging/compiler output, and record the consumed scope. Target compilation cannot
prove startup, electrical behavior, MotorGate timing, WCET or any human phase gate.
