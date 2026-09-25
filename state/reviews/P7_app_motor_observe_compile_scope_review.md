# D193 prepared static observation compile scope review

26 September 2026, Asia/Dubai. **PASS for the prepared scope, conditional on
complete host review, a committed clean reviewed HEAD, and successful live caller
admission.** No material manifest or scope finding. This is not a completed
compile, artifact qualification, upload authorization or phase-gate review.

Reviewer `/root/fresh_review`: separate same-model reused context. The reviewer
read the contract, current launcher, inherited caller definitions, preparation,
manifest, read-only admission and saved host receipts. Independent local data
inspection used AST literal extraction, byte hashing and file enumeration; it
did not import/execute subjects, execute tests, or contact the board. Only this
review document was written.

## Exact prepared bindings

| Input | SHA-256 |
|---|---|
| `P7_app_motor_observe_compile_contract.md` | `0301726f47c0c438a7984ddd232f81c4891c511651ba81a986b15f5ef91dbfb4` |
| `tools/compile_app_motor_observe.py` | `70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827` |
| `inputs_static.json` | `aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e` |
| `preparation_static01.json` | `f3b5a6b053da355ecc88e6705175699caca75ed1683aca6a9ea71e74371b8664` |
| `admission_static01.json` | `c8587c5ef4a68cbebac302f59f4a0eddc66937a3bf53e80f4df2ea6aa23e22d7` |

The manifest is [inputs_static.json](../analysis/P7_app_motor_observe_compile_raw/inputs_static.json);
its exact schema is `app-motor-observe-static-inputs-v1`. All 128 current file
hashes match. Independently enumerating the three declared source roots gives
109 source files; the inherited/projected required set contributes 19 more,
with no missing or extra manifest names. All 14 inherited and added hard pins
match. Manifest files and ancestry are ordinary paths without reparse links;
each input file has one link.

Independently applying the declared source mapping produces 107 destinations,
775,376 staged bytes and source SHA-256
`3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0`.
The 109 inputs contain 776,244 bytes. The two omitted source entries are
`src/app/.gitkeep` and `src/app/app.ino`; the new bench supplies the entry sketch.
There are no destination collisions. The canonical historical Trace header and
implementation alone map from `bench/motor_fault/src` into the new sketch's src.
The historical `bench/app_motor_fault` tree is not a new source input.

The reviewer independently reproduced all three ordered byte projections as
data, without executing them. Original lengths/hashes, every occurrence count,
and all projected lengths/hashes match the contract: caller 29,904 bytes /
`830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884`;
adapter 8,266 bytes /
`e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d`;
remote 6,897 bytes /
`f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c`.
Original sources remain pinned on disk; no generated replacement becomes a
manifest source. The corrected bootstrap checks the opened descriptor before
reading and uses nonblocking open where supported. Its prior repair is recorded
in [bootstrap_review_fix01.json](../analysis/P7_app_motor_observe_compile_raw/bootstrap_review_fix01.json).

## Fixed operation and admission evidence

The prepared operation remains compile-only: project `app_motor_observe.ino`,
FQBN `arduino:zephyr:unoq:link_mode=static`, default startup and exact flags
`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`. Both language flag
bindings and the inherited strict metadata/artifact validators remain in force.
Trace requires MATCH0/MOTORS0; the observer supplies empty application setup
grants. No existing profile, generic upload route or motion authority is widened.

At review, both local owners are absent:
`build/stage/app-motor-observe-static01` and
`state/analysis/P7_app_motor_observe_compile_raw/native_static01`.
The fresh remote owner is
`/home/arduino/sumox26_codex_build/app-motor-observe-static01`; the canonical
source child is the new source digest followed by `/app_motor_observe`.
Old owners and artifact addresses are not reused. Failed or partial attempts
remain consumed under the inherited caller.

The saved [read-only admission](../analysis/P7_app_motor_observe_compile_raw/admission_static01.json)
observed at `2026-09-25T21:08:18.021152+00:00` exits0 with empty stderr. Its command
only reads Linux identity, three installed files, owner existence and free space.
ADB selects `2629958581`; output records UID/GID1000, user arduino, home
`/home/arduino`, Linux aarch64, Python3.13.5 and boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, matching the new manifest. The remote
owner was absent and target free space was 13,981,831,168 bytes. CLI, boards.txt
and platform.txt hashes match the inherited CLI pin and current app-build pins.
This three-file observation does not replace the caller's complete installed
dependency checks. Local free space observed during review was 210,399,232 bytes;
the live caller must recheck its 128MiB local and 1GiB target gates.

## Pending conditions and evidence boundary

Saved first caller receipts show Linux58 PASS and Windows58 with 55 PASS,
two skips and one WinError1314 during fixture symlink creation, before that
subject assertion. Both preserve unchanged pins. The first Windows receipt is
not relabeled PASS. Corrected caller fixture execution and its independent
closure are still pending at this review. Saved supplemental remote/adapter
receipts show Linux35 PASS and Windows35 with 19 PASS/16 platform skips, pins
unchanged. These results do not yet establish complete host-review closure.

Before native compilation, finish that host closure, commit the exact inputs
and reviewed source, select a clean 40-hex reviewed HEAD, then perform the
existing caller's check-only admission and one-shot execution. Its fresh owner,
identity, complete dependency/source, space, command, artifact and closing checks
must all remain active. No reviewed HEAD or new target artifact is asserted here.

This review performs and authorizes no compiler invocation, upload, reset or
MCU access. A successful future compile still requires new file-only ABI/entry
observation before any separately scoped inert run. D188/D190 sizes, addresses,
field maps and receipts are historical evidence, not the new artifact's layout.
No runtime, fault-resolution, RAM/WCET, physical acceptance or human gate follows.
