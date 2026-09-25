# D182: current dynamic/Immediate precompiled MATCH adapter

25 September 2026, Dubai. Software preparation under D051 and the user's
offline-only continuation. This is not a run scope, qualification or motor
permission. Preserve D140's production dynamic link choice and every historical
uploader/source pin. No board or network operation in development/validation.

## Scope and public interface

Add `tools/match_upload.py`, a small versioned adapter to the frozen D175 uploader:

```
match_profile(uploader, support, source_sha256, build_id, run_id) -> dict
upload_match(helper, support, uploader, *, bindings, source_sha256, build_id,
             run_id, fs_root=Path('/'), executor=None, clock=None) -> dict
```

Modules are explicitly supplied by a future hash-checked outer caller. `uploader`
is exactly state/analysis/P7_static_startup_raw/upload_remote.py SHA256
e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1;
support/helper are the existing D179-pinned capture_remote/static_remote modules.
No module loading, CLI, subprocess or filesystem operation at import/profile
creation. This adapter alone is an internal mechanism, not admission of a human
authorization. Outer integration is a separate bounded task before deployment.

`source_sha256` must be exact str/lowercase64hex, and `build_id`/`run_id` exact
str/lowercase32hex. Reject malformed values before lifecycle dispatch. No caller
paths, flags, arbitrary profile dict or alternate build/startup mode are accepted.
`run_id` is the fresh attempt identifier; the build identifier is from the prior
checked compile receipt and never causes a compile here.

Root P is `/home/arduino/sumox26_codex_build`. Derive:

- sketch=P/source/app
- runroot=P/_app_builds/native-app-v1/source/match-immediate/build_id
- raw=runroot/build/app.ino.elf
- packaged=runroot/build/app.ino.elf-zsk.bin
- exported=runroot/artifacts/app.ino.elf-zsk.bin
- output=P/match-source8-run_id-upload (source8 is first eight source characters)

`profile` has exactly `fixed,schema_prefix,files,absent,argv`. Fixed values:
schema `fixed-match-upload-v1`, run_id exactly the caller's32hex, source_sha256,
and derived output. Prefix `match-upload-` supplies unchanged v1 lifecycle
schemas. Files copy uploader.FILE_PATHS'15 tool/config roles and replace `raw`
and `sketch` with the derived raw/packaged paths, then add `exported` (18 total).
Absences retain uploader.ABSENT[:-3] and replace final three with sketch.yaml,
sketch.yml, sketch.json at the derived sketch path. Keep absence as a tuple.
The exact argv is:

```
/usr/bin/arduino-cli --config-file /dev/null upload --fqbn
arduino:zephyr:unoq:wait_linux_boot=no --input-file <raw> <sketch>
```

## Construction and inherited lifecycle

The frozen uploader has no public profile injection. Use one small explicit
subclass/factory initializer; do not call its historical-profile constructor,
mutate module globals, impersonate an inert run or replace lifecycle methods.
Initialize helper/support, input_bindings/run_id, fs_root/executor/clock,
limit_files=uploader.limit_upload_files, started/latest via inherited now(),
report and descriptors/claimed/errors just as its constructor does, using the
MATCH profile/schema/source. If clock is None use time.monotonic; preserve any
supplied callable even if falsey. No altered runtime/output/safety limit.

Before invoking uploader._upload, use its _checked_bindings against the trusted
profile to reject malformed/unknown/missing binding fields and deep-copy input.
Bindings `files.sketch` and `files.exported` must have identical byte counts and
SHA256 (not necessarily identical to raw). Use checked copy in the instance so
later mutation of caller bindings cannot redirect it. Inherited admission again
checks bindings and every actual file; the exported sibling is therefore
actually included in both admission and final postchecks. Caller binding is not
proof of actual bytes. Python -B and the inherited fixed UID/boot/path rules apply.

Call uploader._upload(instance) unchanged exactly once and return its result.
It performs admit -> exclusive owned output claim -> one child -> independent
finalization -> close. No retries, compilation, capture, cleanup, additional
transport, environment overrides or return-value success fabrication. Propagate
its returned failed report or pre-claim exception unchanged. Preserve its <=120s
child timeout, 180s admission/run budget, independent unbudgeted postchecks,
2,303,728B upload file limit, streams strictly below1MiB, durable claim and failure
retention. These are host-verified mechanics, not a hard total wallclock guarantee.

## Independent host validation

Fresh author derives additive tests from this contract and frozen public APIs,
not the new implementation. Use memory-controlled spies and tiny owned RAM
fixtures; no native commands/compiler/device/network. Test exact paths/argv/
schemas, malformed type/hex inputs, strict bindings/unknown fields/roles, package
size/hash mismatch, input copy, falsey executor/clock preservation, inherited
method identity/no historical constructor/no global mutation, delegated result/
failure/exception identity, sole _upload dispatch and all initialization fields.
Run selected existing immutable uploader regressions if needed to establish the
reuse boundary; do not repin historical manifests/tests. Freeze before execution,
retain initial failures, separate fresh-context reviewer checks actual diff and
results. Hardware target/boot, installed files/prerequisites, current source/
artifact qualification and fresh STAND OK/RING OK remain outer admission needs.
