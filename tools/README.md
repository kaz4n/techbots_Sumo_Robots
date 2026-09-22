# P0 tooling contract

Use WSL Ubuntu (available on this machine), Bash, Python 3, CMake, g++, ssh and
rsync. `wsl -d Ubuntu -- bash tools/test_host.sh` runs host checks from PowerShell.
No board packages are installed by these scripts. doctest is vendored/pinned.

## Build and connection

Set `SUMO_SSH_TARGET` to the verified SSH alias or user@host, and
`SUMO_REMOTE_ROOT` to a dedicated absolute board directory such as
`/home/USER/sumox26-build`. These are examples, not actual connection settings.
Keep keys outside the repository. Establish the board host key through a trusted
human check first; scripts enforce StrictHostKeyChecking=yes and BatchMode=yes.

`bash tools/flash.sh bench/p0_matrix --compile-only` stages at
`build/stage/p0_matrix/p0_matrix.ino` plus `src/config.h`, `src/core`, `src/hal`.
The sketch includes `src/config.h`; sources nested in src use relative includes.
Sketch-local headers/subfolders, including a local `src/`, are retained. A local
`src/config.h`, `src/core`, or `src/hal` collision fails explicitly. Source
symlinks, including source-directory ancestors, are rejected. Local SSH and
rsync availability is checked before staging or contacting the board.
The remote staging directory includes a SHA-256 content identifier; no remote
deletion is performed. Core inventory must report arduino:zephyr **1.0.0** before
compilation. This pin is source-verified, not installed/hardware-verified.

`--match` selects MATCH=1, MOTORS_ALLOWED=1 and source-verified core 1.0.0
`arduino:zephyr:unoq:wait_linux_boot=no`. Default is MATCH=0, MOTORS_ALLOWED=0.
Both flag orders are valid. `--compile-only` invokes only inventory, mkdir,
rsync, compile; never upload, reset, start, or monitor. Missing target/config,
missing source/tool/core, invalid arguments, SSH/sync/build failure are errors.

P0 default uploads are allowlisted ONLY for the inert `bench/p0_matrix` and
`bench/p0_timing` sketches, after successful compilation. Their entire staged
contents must match the SHA-256 snapshots in `tools/p0_inert_sources.json`;
changed config, added core/HAL files, or extra sketch files fail before transport.
Updating those snapshots requires inspecting and independently reviewing the
new staged source as inert; never regenerate them merely to bypass a failure.
The manifest is a source-review record, not human motor-run authorization.
Before actually invoking
upload, confirm the bare-board setup and installed dependencies. No command here
implements a per-run motor authorization receipt; all motor-capable uploads
therefore fail. `--match` cannot grant permission.
The current official on-board upload command is `arduino-cli upload --fqbn
arduino:zephyr:unoq <staged-sketch>` using remoteocd, without the kit's reported
serial port. `/dev/ttyHS1` belongs to the router; do not use it as an upload port.
After setup is supplied, validate the inert upload branch on the actual board.
Later motor uploads require fresh scope/revision-bound human permission.

## Logs and validation limits

`bash tools/logs.sh` connects over SSH and receives only from the board's router
Monitor TCP endpoint 127.0.0.1:7500. It sends no keyboard/serial/motion command.
Requires Python 3 and the actual router service on the board. Disconnect/failure
is nonzero; Ctrl-C terminates. MCU logging API is separately blocked by SC-I:
RouterBridge Monitor/notify is not demonstrated bounded or allocation-free.

`python3 -m unittest discover -s tests/tooling -v` uses controlled SSH/rsync
substitutes. These tests must check argument rejection, all flag combinations,
default macros, actual staging include paths, strict host checking, no upload/
reset/start during compile-only, wrong core, and propagation of SSH/sync/compile
failures. A substitute returning zero is script-test evidence only.

Research/provenance: state/analysis/P0_G3.md and P0_G4.md. adb remains unavailable
and unvalidated; no fallback claims are made. `dump_match.sh` belongs to P2 and
`plot_match.py` to eligible P6; neither is falsely implemented as a successful stub.
