# D214 fixed M0 B4 compile-only integration

Adopted under D051 after D213 acceptance (e7298bc7). The user has only the UNO Q
connected. This task compiles the existing ordinary app.ino with B4 selected and
motors disabled. It does not upload, reset, read MCU memory, change firmware,
configure grants, accept wiring or authorize motor operation.

Public launcher: tools/compile_b4_app_static.py, retaining D208's load_caller(root)
and exact --check-only|--execute --reviewed-head <40lowerhex> CLI. Its private
caller retains CompileDiagnostic and the established compile-only lifecycle.
Remote artifact validator: tools/b4_app_compile_remote.py. No historical file
or existing profile is modified. New code must remain small and explainable.

Fixed profile: app.ino, arduino:zephyr:unoq:link_mode=static, default startup.
Use D213's exact ten-macro flag string with MOTORS_ALLOWED=0. Reject M1, MATCH,
Immediate, dynamic, shortened/reordered/extra flags and stale ordinary results.
No parameter or CLI can select an alternative profile.

Fresh attempt: b4-app-m0-static01. Local stage is build/stage/b4-app-m0-static01/app.
Board command/build/artifact owner is
/home/arduino/sumox26_codex_build/b4-app-m0-static01.
Evidence lives in state/analysis/P7_b4_app_compile_raw; native_static01 is the
one-use local owner. Preserve exact existing-source admission under
/home/arduino/sumox26_codex_build/<source-sha256>/app. Expected current ordinary
source is9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a;
a fresh checked manifest and reviewed clean HEAD bind the actual attempt.

Reuse the checked D208 loader and all historical dependency pins. Keep its
ordinary source inventory/mapping/hash/helper crosscheck, bounds, reserved-path
and case-collision guards, staging, descriptor/no-follow checks, one-query/
one-compiler sequencing, jobs1, transport/stream/deadline/resource limits,
intent-before-dispatch, first-error attribution and every closing check.
Only explicit new profile/schema/path metadata may alter these inherited bodies.
No retry, cleanup, arbitrary override or new native action is introduced.

The necessary semantic seams are:
1. Local static policy binds the checked D213 module to integer motors_allowed=0
   and five already admitted exact snapshots. Both expanded-query and actual
   compiler-result metadata are validated against the identical full flags.
2. Artifact-program preparation transports D213 plus those five original
   snapshots, the existing descriptor helper and frozen artifact validator.
   Every source body is pinned before private execution. Preserve original TLS
   input acquisition, framing and Windows command-line ceiling30000 including NUL.
3. Remote bundle admission accepts only the explicit closed bundle and fixed
   identities, then calls D213 validate_artifacts with the exact original
   artifact bytes, native TLS source, frozen validator, exported package, int0
   and checked snapshots. Preserve descriptor reads and three closing observations.
4. Local layout admission requires STATIC_B4_APP_LAYOUT_PACKAGE_PASS and
   motors_allowed of exact int type/value0. Preserve every original artifact,
   aliases, metadata, hash and native-layout predicate; no input mutation.
5. Extend the required input/hard-pin set to bind new launcher, remote validator,
   D213 module and contracts while preserving all historical dependencies.
   Declare the exact closed manifest, native scope-role and bundle sets in a
   compact data-only interface receipt before independent oracle finalization.
   That receipt may expose names, types and source identities, not test outcomes.

Use new b4-app-m0-static input/scope/result/artifact schema labels wherever the
predecessor has a profile-specific schema; preserve generic lifecycle statuses.
No ordinary-app owner/manifest or previous native scope is repurposed. Original
D208 compile tool is26136B/40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89.
D213 policy is4055B/aadccdbb0a92338a90a789251f691a42e029c7f73b312b638b85d04c5d2d4ddf.
Its five snapshot identities remain exactly those in the accepted D213 contract.

Independent spec-derived host tests must exercise real admission and both policy
calls, all snapshot/bundle pins, missing/extra/changed sources, ordinary/M1 and
bool-mode rejection, preserved mapper/ownership/child-failure/closing behavior,
no uploads, and actual compressed argv size. No success-only mapper or validator
stub may substitute for the real positive path. Keep all historical tests intact.
Implementation and test author stay mutually blind until implementation is sealed
and the independent oracle is FINAL; then source/host review is separate.
Run Linux and Windows focused suites serially with isolated fixtures and bounded
execution; preserve first failures. Do not invent a test count before selection.

After source/host acceptance: fresh read-only board identity/tool/source/resource
and owner checks, exact manifest/scope, independent native admission review,
clean reviewed HEAD, one check-only then at most one compile-only attempt.
Ordinary D212 remains the latest flashed image. B4 loading, addresses/ABI, live
memory/timing, recorder delivery and physical commissioning remain separate.
No /tmp/remoteocd cleanup or ABI query is needed merely to compile.

## Adopted transport amendment under D051

Before implementation seal or oracle finalization, data-only measurement found
the unchanged eight-source payload is116347 bytes and zlib9 is28087 bytes;
the former inline command is41318 Windows UTF-16 units including NUL. No board
operation occurred. The30000-unit ceiling remains unchanged. This amendment
supersedes only the inline artifact payload framing and the earlier prohibition
on new source-transport actions or corresponding lifecycle body changes.

After the one successful compile, complete metadata validation and exact query/
compiler count check, prepare_artifact_sources() sends exactly two bounded
source-only direct() commands before the first artifact observation. The payload
is the same closed eight-source JSON plus pinned remote source, compressed once
with zlib9. Require16384 < compressed bytes <=32768; split at16384. The current
second chunk is11703 bytes; actual sealed bytes/hash define the later attempt.
No payload source is executed by either transfer. Each full command remains
within30000 Windows UTF-16 units including NUL and inherited transport bounds.

The sole new leaf is artifact-sources.zlib under the existing exclusive fresh
remote compile owner, outside its build/artifacts children. The first transfer
uses O_CREAT|O_EXCL|O_RDWR|O_NOFOLLOW, mode0600; the second uses O_RDWR|O_NOFOLLOW
and admits the exact first identity, size and hash before appending once.
Use descriptor-relative no-follow ancestry and leaf access, regular single-link
uid/gid1000 files, path-versus-fd identities before/after, bounded readback,
exact chunk/complete hashes and all descriptor closes with first-error priority.
Set attempted state before dispatch; a second preparation call always refuses.
Existing files, partial failure and transport uncertainty consume the attempt;
there is no retry, repair, cleanup, replacement owner or extra compiler call.

Both transfer replies carry checked identity/hash data. Retain the second
identity for artifact_program(), which reads the same fixed leaf through the
descriptor/stability guards, checks the complete compressed size/hash/identity,
then uses the existing bounded zlib/JSON/source-hash validation and exact bundle
admission. The final artifact observation rereads the same immutable payload.
No extra local payload copy is required; all payload bytes are reproducible from
sealed source inputs. Keep the old decompressed262144-byte bound and framing
canonicality, EOF/trailing-data checks and all original artifact predicates.

Whenever preparation was attempted, closing independently checks the payload
and appends one artifact_sources result, even after a partial transfer failure.
Incomplete preparation cannot produce a successful payload closing row. Preserve
the earliest error and every inherited closing attempt/result. The authorized
body seams are __init__ state, one build insertion, artifact_program payload
acquisition and the extra closing row; small bounded payload helpers are allowed.

Before first tests, seal an updated data-only interface receipt and independent
oracle covering both transfers, exclusivity/identity/symlink/hash/partial failures,
call ordering, consumed state, closing behavior, exact byte roundtrip and actual
full Windows argv limits for both transfers and artifact observations. Preserve
the initial interface and failed size calculation as preparation evidence.
