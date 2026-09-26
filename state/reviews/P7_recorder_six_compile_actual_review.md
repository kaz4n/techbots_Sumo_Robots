# D235 actual six-store recorder compile review

Verdict: **PASS for this identified native compile and checked artifacts.** No
material blocker found. This is compile/link/package acceptance only; delivery,
the earlier timeout and cleanup failure, target timing and physical qualification
remain outside this verdict.

The reviewer read the closed compile evidence in isolated worktree
`C:/Users/narut/AppData/Local/Temp/sumox-recorder-six-native-20260927`, owner
`state/analysis/P7_recorder_delivery_raw/recorder-771c04943d4c4a75`.
Native HEAD is `1b2af246cd88e6207e846ee340f8c4e46a5bb980`, attempt
`771c04943d4c4a759055d794fa4b706e`, session `8582740024591403637`, source
`289300a4be9547cd294dc1f753bbe17a429d16776c46467fec5417b1290f4ffc`.
The profile is recorder.ino, static/default startup, MATCH=0 and MOTORS_ALLOWED=0.
The retained board boot is `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.

All 145 input SHA256 pins independently match both the isolated source bytes
and this native HEAD's Git blobs. All 110 actual staged files independently
rehash, and their sorted path-NUL-content digest reproduces the source identity.
Both remote source inventories equal that complete staged map. The staged config
matches the reviewed six-store candidate; its source-bound identity header uses
the expected positive uint64 session and statically requires the inert profile.
The source/host acceptance is separately recorded in
`P7_dump_six_store_review.md` (SHA256
`fab3176ecf70d804eabddaa192a118aed20f141505d3db6ae8af45a566be786f`).

The result is COMPILE_CHECKED with one property query, one compiler and 28 native
transports. All 28 transports return zero with empty stderr. All nine checked
children report COMPLETED, reaped=true, returncode=0 and timed_out=false; their
encoded stdout/stderr exactly match the retained raw child files. The actual
compiler uses `/usr/bin/arduino-cli --config-file /dev/null`, `--jobs 1`, a 720 s
deadline and 5 s reap. Query and compile JSON report success, empty compiler_err
and empty upload_result. Their C and C++ flags are exactly MATCH=0 and
MOTORS_ALLOWED=0, with the identified static FQBN and recorder project.

All nine closing checks pass with null errors: local, identity, initialization,
builtins, remote_sources, installed_pins, overrides, artifacts and artifact_sources.
The first and closing artifact replies both equal the saved artifact packet.
Loader, TLS source and artifact postchecks pass; first_error is null. The inherited
layout validator reports STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS, validates the
six native TLS symbols against the pinned loader/source, and reports no weak
undefined symbols. The outer compile process was reported closed with exit zero
after 272.453 s; the saved result spans 21:54:36.779420 to 21:59:08.092404 UTC.

| Checked artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Build/export flat package | 55376 | 3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d |
| Raw binary | 55360 | 03f55f4db1d7e173ce2d3b1064ec0a8b730289b094282799da8a743d01d59a71 |
| ELF | 101908 | eefe61948c05eee4f6042fb67ff4c45932d8aca5cca591a154d75c978c7ab2a4 |

All seven build artifacts and the exported package have checked regular-file
identities; build/export package hashes agree. The validated data-copy extent is
216 bytes, initialized BSS extent 164196 bytes, and structural remaining RAM
97424 bytes. These are linker/layout figures, not measured free RAM or stack
margin. Arduino's aggregate globals figure is 164724 bytes.

Principal closed receipt pins:

- inputs.json, 14542 bytes:
  `0d269bd6e15dca176b88dd7c1e9f9fd1a39d64d1cb98ec7775b83c1a82f8f026`.
- result.json, 2036 bytes:
  `09b497ef80dc4fe443cab995eec450dacbfc28f2a908d8a3c861dffda9525d86`.
- artifacts.json, 9575 bytes:
  `66186a0caae7667149bb1ccec4889fcc773859104cd8db112a2dfdbcee3626e2`.
- root_compile_closure01.json, 1557 bytes:
  `95d82fbc23203c0b95dc2ccfe6385edb9506400114ed72d51658dd4e23342986`.

The root closure's PENDING_FINAL_REVIEW host field records its earlier creation
time; the independently pinned source/host report above closes that review.
No upload occurred within the compile action. Later delivery receipts share the
owner but are outside this report: only compile transports 0001 through 0028 are
accepted here. The reviewer ran no tests or native command, changed no source or
native worktree file, and wrote only this review in MAIN. No motor permission,
runtime success or phase gate is implied.
