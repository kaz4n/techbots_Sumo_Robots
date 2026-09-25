# Run02: one separate inert static startup observation

Target UNO Q ADB2629958581, expected boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6,
UID1000/aarch64. Existing user permission covers testing the board connected alone.
Firmware is the unchanged D144 static/default MOTORS_ALLOWED=0, MATCH_BUILD=0
packet: source fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2,
artifact run f0220228320c4b2aa20c3e5e8264c813. Both C/C++ flags are in the pinned
0017 build receipt. No compiler, new firmware/config, extra hardware or motor run.

Use reviewed D158 startup_run.py with --execute --run run02 --reviewed-head
naming the committed scope-containing current HEAD. native_run02_scope.json binds
the exact launcher, independent ownership tests, contract and final scoped review.
D156/run01 remains failed and consumed. One run02 upload and conditional capture
are permitted; failure or uncertainty ends this scope without an automatic retry.

Reuse the exact source/artifact/installed/F166 prerequisite checks, six command
forms,14 clean-path dispatches, exclusive intents and independent final checks
specified in P7_static_startup_run_plan.md. Changes: explicit per-instance run02
identity and paths; upload_loader sets the minimal2303728-byte process file cap;
accepted stdout/stderr remain strictly below1048576 each. D159 separately removed
the exact known temporary fragment. The uploader still requires fresh /tmp/remoteocd
absence and conflict checks; the cleanup receipt is not a substitute for admission.

The upload's intrinsic fixed loader/sketch programming, MCU reset,100ms wait and
0xCAFFEEEE activation write at0x40036400 are included, with no extra reset/recovery.
Budgets remain upload180s/child120s/+5s reap, host195s; conditional passive capture
600s/read30s/+5s reap, host630s. Capture has18 reads/713656B with full flash brackets
and two runtime samples separated by at least2s; no halt/reset/write in capture.

Local exclusive owner: state/analysis/P7_static_startup_raw/native_run02.
Remote owners: /home/arduino/sumox26_codex_build/static-startup-fcddbd8e-run02-upload
and -capture. Preserve run01, all negative/host receipts and original target files.
No duplicate firmware/source export. Capture starts only after strict upload
success and intermediate checks. Collected evidence does not itself prove startup,
RAM margin, whole-robot WCET, sensors/pins/motors, production static admission or
physical/human gates. Decoder observation remains separate from collection status.
