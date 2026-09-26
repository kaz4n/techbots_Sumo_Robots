# D239 fresh recorder actual compile review

**PASS for this identified compile and checked native artifacts.** No material
blocker found. This is compile/link/package acceptance only; the separate run
must establish its own complete, correctly framed delivery.

Native owner:
`C:/Users/narut/AppData/Local/Temp/sumox-recorder-repeat-native-20260927/state/analysis/P7_recorder_delivery_raw/recorder-354cf1586a9648d8`.
Native HEAD `1b2af246cd88e6207e846ee340f8c4e46a5bb980`, attempt
`354cf1586a9648d88cb9dad105a6c992`, session `3840709944287840472`, source
`3d9306d7b804a68d6e7c2764171077526fbe14074b4564ea2e071ffd5a8e839b`.
The profile remains recorder.ino, static/default startup, MATCH=0 and
MOTORS_ALLOWED=0, with the fixed boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.

All 145 input pins independently match current source and this historical HEAD's
Git blobs. They equal the accepted six-store D237 inputs exactly. All 110 actual
staged files rehash, and the sorted path-NUL-content digest reproduces the source
above. The only staged hash change from D237 is recorder_run_identity.h, containing
the new positive uint64 session and unchanged inert grants/static guards. No
firmware policy or deadline changed. Both remote source inventories exactly match
this complete staged map.

The final result is COMPILE_CHECKED: one query, one compiler and 28 transports,
all with returncode zero and empty stderr. All nine checked children report
COMPLETED, reaped=true, returncode=0 and timed_out=false. Their retained raw
stdout/stderr bytes equal the encoded command replies. The actual compiler uses
`/usr/bin/arduino-cli --config-file /dev/null`, jobs=1, a 720 s deadline and
5 s reap. Query and compile JSON report success, empty compiler_err and empty
upload_result. Expanded C/C++ flags are exactly MATCH=0/MOTORS_ALLOWED=0, with
the expected static FQBN and recorder project.

All nine closing checks pass with null errors: local, identity, initialization,
builtins, remote_sources, installed_pins, overrides, artifacts and artifact_sources.
Both first and final artifact replies equal the saved artifact packet. Loader,
TLS-source and file postchecks pass; first_error is null. The native TLS/layout
validator passes, binds all six TLS symbols to the reviewed loader/source and
reports no weak undefined symbols. All seven build artifacts and the exported
package have checked regular-file identities; build/export package hashes agree.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Build/export package | 55376 | 3a1bbd2f277edb4617cafe0b4404c4753f1ad9141cb8d107cb07ed33bf24e724 |
| Raw binary | 55360 | d8643b9583b262ca625082af8c6e76cd5f8983f9b564b979a8c36108a060de95 |
| ELF | 101908 | 1aae919f2d2dddf5ba6f5e8d591b42918d34891612ccbfb0af0b4bf95446517c |

Validated data-copy extent is 216 bytes, initialized BSS extent 164196 bytes and
structural remaining RAM 97424 bytes. Arduino's aggregate globals figure is
164724 bytes. These are linker/layout figures, not measured free RAM, stack
margin or WCET. Root reported process exit zero after 254.374 s; the saved result
spans 22:25:59.952916 to 22:30:13.868783 UTC on 2026-09-26.

Closed receipt pins:

- inputs.json, 14542 bytes:
  `d701680efff3f33e7d65f25c85fd01d5c80afded3cb7069cd31f97907e14deac`.
- staged_files.json, 10590 bytes:
  `5daf8ae55a0aa1fcf9c4159da20ad26e5d7b3bce64446cb35b5fd60037ed5246`.
- result.json, 2039 bytes:
  `6afe88c08b705320dd2f04501825b2031b38ca377911eff0a936cbfbb9904e6c`.
- artifacts.json, 9575 bytes:
  `cbabc6ef58a214bd8979f97b68d1d498ae9ceee681c6c8553f7a7879214cd51b`.

No upload occurred within this compile action. Later transports in the same owner
are outside this report; only compile transports 0001 through 0028 are accepted
here. Prior D237's missing-envelope failure remains preserved and is not repaired
by this successful build. No further source-review chain is required for this
already accepted source and generated fresh identity, but actual delivery remains
unproven. Reviewer ran no test or native action, wrote nothing in the native
worktree, and wrote only this MAIN review. No motor permission, physical acceptance
or human phase gate follows.
