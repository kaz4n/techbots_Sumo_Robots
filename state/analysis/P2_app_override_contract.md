# D100 correction of D099-R1: precompile effective configuration

2026-09-23 Asia/Dubai. Continue P2 tooling under D051/D075; no firmware/config,
wiring, startup choice, library policy, capacity or upload-authority change.
D099 adoption remains pending until its MAJOR is fixed and reviewed.

Use exactly the same CLI/config/environment context for the following sequence:
1. Existing CLI/core identity checks; reject staged root sketch.yaml/sketch.yml
   before a CLI operation can initialize a sketch profile.
2. `arduino-cli config get directories.data --json` and the corresponding
   directories.user query return resolved JSON strings including defaults and
   environment aliases. Reject malformed/empty/nonabsolute paths. Do not use
   config dump's explicit-values-only map as proof of resolved defaults.
3. Before properties/build, refuse presence (including dangling symlinks) of
   data/packages/platform.txt, user/hardware/platform.txt, platform.local.txt
   or boards.local.txt beside the expected pinned installed core, and remote
   sketch.yaml/sketch.yml (including stale files in the content-addressed tree).
   Check the18
   existing selected installed-file hashes before compile, as well as afterward.
   This checks documented global/local override sources; it is not protection
   against a compromised host changing files between individual commands.
4. Permit one newly scoped `compile --show-properties=expanded --json` preflight,
   using the exact same explicit FQBN/build path/output path/three properties and
   sketch as the real invocation. Pinned primary source proves this returns before
   prebuild/preprocess/build hooks. It can create its explicit directory; it is
   not labelled read-only compilation or a successful firmware build. CLI instance
   initialization/discovery is a distinct behavior, not ruled out by this return.
5. Validate the complete effective recipe/compiler/link/startup/hook property set
   against a reviewed reference derived from D098/D099 default evidence. Allow only
   explicit build/data path substitutions, the already approved0/0 or1/1 flags,
   and the known wait/Immediate packaging argument. Reject unknown added command
   or hook keys, removed required keys and changed values. Also require the
   expected core/compiler roots under the resolved data directory.
6. Run exactly one real compilation only after those checks pass. Repeat strict
   result/effective-command and installed/artifact checks. Preserve raw preflight
   and compiler stdout/stderr separately, including failures. A properties-only
   result never proves empty discovered libraries or successful compilation.

No arbitrary-property/environment override option is added to our wrapper. Normal
bench paths remain unchanged, app uploads remain refused before transport, and
no command performs upload/reset/start/MCU operations. The fixed absent-file shell
probe receives paths only as positional arguments and has no file mutation.

Public seams for independent tests:
- Existing validate_result(text,fqbn,flags,build_path) now also checks complete
  effective command properties. Its positive fixtures must contain truthful
  complete metadata; old assertions are not relaxed.
- validate_preflight(text,fqbn,flags,build_path,data_dir) validates the hook-free
  envelope/commands/core roots and returns the property dict. It does not require
  a completed binary or make a discovered-library claim.
- resolved_directory(text) accepts exactly one normalized absolute JSON string.
- preflight on the actual wrapper must occur before any real compile; existing
  script fixture tracing distinguishes properties-only queries from compilation.

Regression requirements: preserve the three original reviewer reproductions; test
every controlled effective property and unexpected hooks/numbered recipes; check
all supported modes and path relocation. Inject malformed directory/query results,
each override path, bad precompile pins and changed effective preflight properties:
no actual compilation or upload may follow. Profiles fail before board lookup.
Existing parser/transport assertions remain, with explicit fixture protocol/data
updates only; new independent tests derive from this contract and primary sources.
Target default/Immediate/MATCH and library fixture acceptance remain separate.

Implementation clarification (2026-09-23, before local review): the reference
contains84 effective command properties, including build.compiler_path,
build.crossprefix and build.zip.pattern in addition to the original81-prefix
set. All84 values and their presence are checked at both validator boundaries.
Resolved paths reject root-only, nonnormalized or multiple-leading-slash paths,
backslashes, control bytes, quotes, backticks and dollar signs. The latter
characters can become shell syntax inside the pinned platform's own recipes;
normal spaces remain permitted. The six absent-file paths include both remote
sketch metadata names, even if the current local source has neither file.
These are tooling constraints only; the recorded mode and firmware policy stays
unchanged. The independently authored tests use these explicit clarifications.
