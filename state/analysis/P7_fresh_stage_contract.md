# D170: explicit fresh staging

Scope: additive local `tools/board_tool.py` API `stage(sketch, *, attempt=None)`.
This prepares source only; it does not build, transport, upload, reset or delete
an earlier attempt. D168's policy-blocked `build/stage/motor_fault` stays intact.

- Omitted/None keeps the legacy destination and behavior for unchanged callers.
- An explicit attempt is an exact `str` matching `[a-z0-9][a-z0-9_-]{0,47}`;
  Windows reserved device names con/prn/aux/nul/com1..9/lpt1..9 are rejected
  on every platform. Invalid values fail before creating staging directories.
- Destination is exactly `ROOT/build/stage/<attempt>/<sketch-name>`; the .ino
  stays at that sketch root and project source remains beneath its `src/`.
- Before creating anything, inspect ROOT, build and stage with lstat: each
  existing component must be a plain directory, not a symlink, junction or
  other reparse point. Require resolved containment beneath the project root.
- The attempt path must not already exist, even as a dangling link, file or
  empty directory. Claim it with exclusive mkdir; never remove/reuse an owner.
  Recheck staging ancestry after creating missing base directories. This handles
  pre-existing unsafe paths; it is not a hostile concurrent-filesystem guarantee.
- Reuse the existing source validation, copy/layout and config-validation body.
  Existing sketch-local reserved names and source links still fail as before.
  Both bench and app stages include project src/app C/C++ sources and headers
  (.c/.cc/.cpp/.h/.hpp) under staged src/app/, excluding src/app/src/. The app
  .ino is not copied there. App support files are not duplicated at sketch root;
  bench-local headers/subfolders and local src/ retain their existing positions.
- Explicit mode performs no deletion, overwrite of existing attempts, fallback
  to legacy staging or automatic cleanup. On a post-claim copy/config error,
  raise the error and retain the partial attempt; the same token cannot retry.
- No new CLI flag, ROOT rebinding in production, profile change, source overlay,
  historical manifest change or native call is included.

Independent host acceptance: exact path/content/hash/layout for bench and app;
legacy sentinel bytes and mtime preserved; valid token boundaries and invalid
types/paths/device names; existing file/directory/live and dangling links refused;
linked/non-directory ancestry refused before writes; partial copy/config failure
retained and reuse rejected; no delete/transport invocation; legacy call retained.
Use synthetic owned temporary trees. A passing fixture is not a board build.
