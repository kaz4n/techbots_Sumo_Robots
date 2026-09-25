# Corrected inert diagnostic target compile

Reuse the reviewed D165 compile procedure in P7_motor_fault_compile_plan.md,
with D166's identifier-only macro correction and D167's instance ownership.
No change to flags, startup, link mode, native limits, child process machinery,
deadlines, source/recipe/artifact verification or final checks.

Select `--execute --run compile02`. Local receipts belong exclusively to
P7_motor_fault_raw/native_compile02; inputs are compile_inputs02.json. Remote
ownership is /home/arduino/sumox26_codex_build/motor-fault-compile02, with the
motor_fault sketch child. Both receipt/remote paths and shared local stage must
be absent. Run Python with -B and -X pycache_prefix equal to the absolute selected
native_compile02/pycache path. The historical compile01 remains consumed.

The117-pin set matches the historical filename set; only the diagnostic header,
implementation and compile caller hashes differ. Bind the new inputs and caller
in the separate review after independent ownership tests. Child process code and
explicit environment retain their original hashes and four real-child checks.

Target remains ADB2629958581, UID1000/arduino,
boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6, with fresh identity, executable hashes,
two file-only CLI prerequisites, process-conflict checks and free-space checks.
One query and one compile only, jobs1, default startup/dynamic link,
MATCH=0/MOTORS_ALLOWED=0. Compile timeout720s; other children60s; group kill and
reap5s; transport child deadline+90s. Capture original success/failure and
independently check source, identity, prerequisites, installed pins and overrides.

Commit the reviewed plan, input binding and host evidence before this identified
attempt. No upload/reset/MCU read, dependency download, source overlay, automatic
retry or additional hardware. A checked compilation is not a runtime result.
After collection retain useful target identities/diagnostics and remove only
hash-verified disposable local staging. Windows policy-denied paths stay untouched.
