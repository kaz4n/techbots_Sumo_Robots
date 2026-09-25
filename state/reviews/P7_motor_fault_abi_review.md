# D173 file-only ABI source review
Reviewer: separate fresh-context same-model agent; 2026-09-25, Asia/Dubai.
Scope: source inspection only; no board command, test, build, upload or reset.
Reader SHA256: ec9a88237d60c237722ae5d6dee94b6bc6cd76fea96e518f52ba8e3c18394d3b.
Plan SHA256: acc5a90feb1cad84238267ead7c5b5c84163928fe687a21e5f7643f0ebf2e561.
Reviewed AGENTS, current D173/ledgers, reader, pinned CompileOnce transport/preamble,
extracted stop_child/wait_child, active_verified and current 117-input manifest.

MAJOR 1 - inspect_active_abi.py:116-118 trusts an unbound current input manifest.
Removing entries (including all entries) silently weakens the promised 117 checks.
Pin its exact D172 bytes/hash before parsing and record/recheck that binding.
MAJOR 2 - :134-140 skips local final checks on transport/parse/remote failures;
it also saves OBSERVED before local drift can fail. Run retained local checks in
finally, preserve the original failure and independently record the final outcome.
MAJOR 3 - :51-53 decodes both streams before retaining either. Invalid UTF-8 or a
stream-read exception can discard child output and replace the original exception.
Retain each stream's raw bytes/base64 and separate collection errors; preserve the
first execution failure and continue independent final checks.

PASS boundaries: five literal file-reading commands; no target/run/upload/MCU path;
GDB -nx/-nh plus early auto-load disable and function-call disable; sanitized env,
shell=False, 60s child deadline/5s process-group kill/reap, 1MiB per-file cap;
ADB/caller/support/metadata pins, 25 remote file hash/identity brackets, exclusive
native_abi01 ownership and raw transport receipt retention. No retries in source.
FAIL pending the three evidence-control repairs and source re-review.
This is not execution evidence, cross-model review, physical acceptance or a gate.
