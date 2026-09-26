# Current ordinary-app static build follow-up

Current update, 26 September 2026: D208 has completed the fixed ordinary
static/default/MATCH0/MOTORS_ALLOWED0/probe0 compilation described below.
The native result is COMPILE_CHECKED with all eight closing checks passing;
independent actual-result review8cd383e4 accepts this packet. Current source is9044ebbb, package
92944B/7fa9d41d and structural RAM tail94352B. See
P7_ordinary_app_static_compile_validation.md for exact evidence and limitations.
The next work is ordinary file-only ABI/entry preparation, then a separately
reviewed finite inhibited runtime scope. No ordinary upload has occurred.

The following source-planning note is historical; its former next actions are
superseded by that current validation and CODEX_HANDOFF.md.

Read-only source planning on 26 September 2026, after D198 compilation. This
is not an adopted build contract or evidence that the ordinary app fits or runs.
The diagnostic source117cc0e7 and its artifact do not represent production.

A fresh fixed compile-only launcher can reuse D188/D193's bounded compilation
and artifact checks with `PROJECT='app.ino'`, static linking, default startup,
and exact flags `-DMATCH=0 -DMOTORS_ALLOWED=0`. The probe remains at config's zero
default; preserve ordinary app.ino, all configuration values and zero grants.

Use D185's ordinary `source_names(root)` inventory of src, excluding diagnostic
benches. Match the canonical ordinary app mapping in
`tools/match_deploy.py::app_source_hash()`: config, core, HAL, ordinary app support
under staged src/app, sketch-local src/app/src under staged src, and top-level
sketch support in its canonical locations. Pin that helper and cross-check the
computed source digest. Keep bounds, collision checks, required app.ino and
override refusal. Do not reuse a diagnostic or historical ordinary-app digest.

The coupled caller changes lie in source_names/source_mapping, initialization,
admission, source_admission and stage. Use a fresh attempt with stage/source child
`app` and the existing `board.stage('app', attempt=...)`; preserve exact staged
file and directory verification. No generic board-tool admission change is needed.

The D187 static policy adapter can privately project to ordinary app.ino and the
two inhibited flags. Its seven artifact aliases become identities against the
original static-app validator. Preserve the checked dependency bytes, all template
occurrence checks, native TLS/package validation and exported-flat equality.
Project the remote helper only for fresh ownership, ordinary project/flags/schema
and the coupled adapter hash. Preserve descriptor checks, one property query,
one serial compiler operation, resource bounds, closure and first-error evidence.

Relevant independent fixtures are test_app_motor_fault_static_policy.py,
test_app_motor_fault_compile.py, test_app_motor_fault_compile_remote.py,
test_compile_current_app.py and test_compile_current_app_errors.py. Their old
metadata assertions require explicit fixture adaptation, not silent weakening.

This later build would establish current source's static file layout and package
checks. Loading, live RAM and stack headroom, production timing, native recorder
ownership/rearm and physical acceptance remain separate. It must not upload
firmware or imply motor-run permission. D199 ABI/entry and internal SETTLE fault
localization are the current task; this note saves the source inspection for the
subsequent production-memory work.
