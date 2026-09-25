# D164 per-call checked-build executor

25 September 2026. Host-tool preparation for the next inert diagnostic compile.
The existing checked compilation validates recipes, flags, dependencies and output
artifacts, but binds transport through module globals. Reusing it with explicit
CLI/environment and a board-side deadline must not require rebinding those globals
or copying the build policy into another implementation.

Add only keyword-only `command_runner=None` to board_tool.capture_app_command,
app_preflight and compile_app. None preserves all existing call behavior. An
explicit value must be callable or raise ValueError before any command dispatch.
The callable has the existing remote(board, argv, capture=False, timeout=None)
interface and returns a CompletedProcess-compatible result or raises. Do not
assign it to any module global or modify it. Each invocation chooses its own
runner; nested/sequential invocations must not leak selection.

With a runner supplied, every command in that build uses it: CLI version, both
directory queries, override and installed-pin checks, expanded-property query,
compiler, and postcompile dependency/artifact hashes. Preserve command arguments,
existing raw receipt writes and error propagation. No new flags are implicitly
inserted by these helpers. Existing defaults must keep the old signatures at
internal call sites when possible so established test substitutions still work.
The executor supplies execution bounds; this parameter alone does not do so.

All existing policy/recipe/pin/source-upload manifests and test assertions remain
unchanged. No new project admission, firmware behavior, upload, reset or board
operation. Independent companion tests should cover full routing, default parity,
invalid-runner refusal, nested/sequential isolation, and version/preflight/compile/
artifact failures without real commands. Freeze new expectations before running.
An identified native caller and source/artifact review remain separate work.
