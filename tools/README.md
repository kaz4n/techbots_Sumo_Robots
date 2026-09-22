# P0 tooling contract

Use WSL Ubuntu (available on this machine), Bash, Python 3, CMake, g++, ssh and
rsync. `wsl -d Ubuntu -- bash tools/test_host.sh` runs host checks from PowerShell.
No board packages are installed by these scripts. doctest is vendored/pinned.

## Read-only inventory

After verifying the SSH target and its host key, run `bash tools/preflight.sh`.
Only `SUMO_SSH_TARGET` is required; `SUMO_REMOTE_ROOT` is not used. JSON stdout
records the time, target, commands, exit statuses and their output. Save each run
to a new evidence file, for example `state/analysis/P0_board_inventory_<run>.json`.
Exit 0 / `INVENTORY-COLLECTED` means all requested commands returned successfully,
not that their versions, wiring, or the P0 gate passed. Inspect the output.
`INCOMPLETE` and a nonzero exit preserve failed-command evidence; missing local
configuration/tool or invalid arguments produce a nonzero diagnostic.

Commands read kernel identity, CLI version, core list, UNO Q board options,
library list, rsync/Python versions, and TCP listener addresses. Each command has
a 30-second deadline; a transport failure/timeout stops remaining queries.
The command never compiles, uploads, resets, installs, syncs sources, connects a
Monitor socket, probes sensors, or dumps environment/credentials. Loader build
configuration, exact library sources and router identity still require separate
read-only inspection. Hardware observations are listed in
`docs/P0_MANUAL_CHECKLIST.md`.

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

For P0 startup comparisons, `--startup default` (wait for Linux) or
`--startup immediate` selects the startup option independently of motor macros.
Example build-only: `bash tools/flash.sh bench/p0_matrix --compile-only --startup immediate`.
An inert Immediate build remains MATCH=0 and MOTORS_ALLOWED=0. The default is
unchanged when this flag is omitted; MATCH still selects Immediate and explicitly
combining MATCH with default startup is rejected. Artifacts for each build/startup
combination use separate directories, and upload uses the same FQBN/artifacts as
its successful compile. A startup selection grants no new run permission.

Immediate `p0_matrix` **uploads are blocked** until the installed loader's matrix
ownership is verified: the official UNO Q manual warns against matrix access
before startup completes (FACTS F-061). Its compile-only route remains available;
the RAM-only timing sketch makes no matrix calls. A boot logo is not a sketch
start measurement. Neither startup option nor source hashing resolves this
hardware/API dependency.

Primary references: [CLI board details](https://docs.arduino.cc/arduino-cli/commands-reference/arduino-cli_board_details/),
[CLI core list](https://docs.arduino.cc/arduino-cli/commands-reference/arduino-cli_core_list/),
[core 1.0.0 startup definitions](https://github.com/arduino/ArduinoCore-zephyr/blob/1.0.0/boards.txt).
These verify command/option syntax; installed-board operation remains pending.

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
is nonzero; Ctrl-C terminates. Stock RouterBridge Monitor/notify remains unsuitable
under R3/R4. D-062's separate fixed P0 notification adapter has now delivered real
counters to this receiver on the bare UNO Q; production recorder transport is
still a later dependency. See `state/analysis/P0_counter_validation.md` for the
explicit8-second capture deadline, raw exits and scope. No receive command path
was added to the MCU or this logger.

`python3 -m unittest discover -s tests/tooling -v` uses controlled SSH/rsync
substitutes. These tests must check argument rejection, all flag combinations,
default macros, actual staging include paths, strict host checking, no upload/
reset/start during compile-only, wrong core, and propagation of SSH/sync/compile
failures. A substitute returning zero is script-test evidence only.

## Explicit USB ADB fallback

Set `SUMO_TRANSPORT=adb`, `SUMO_ADB_SERIAL` to the observed USB serial, and optionally
`SUMO_ADB_EXECUTABLE` to the installed adb executable path (default: `adb`). The
serial is mandatory even with one device. There is no automatic device selection,
server restart, root escalation, package installation or network discovery.
`SUMO_REMOTE_ROOT` remains a dedicated absolute directory on the UNO Q. The SSH
transport remains the default and retains strict host-key verification.

ADB executes quoted shell commands on the board and pushes each staged file to
its exact content-addressed path; compilation and upload still run on the board.
No local UNO Q core is needed. Errors propagate and all compile-only, inert hash,
startup and motor guards apply identically. No rsync dependency is needed for this
transport. Inventory still reports missing rsync explicitly; this does not prevent
an ADB build. See analysis/P0_connected_inventory_20260922.md for observed tools.
An ADB inventory exit1 conservatively stops remaining queries: that status can
represent a transport failure or a remote command failure. Other command failures
remain explicit, and any failed item makes the report INCOMPLETE/nonzero.

With Windows adb.exe, use native Python so local push paths use Windows syntax:
`python tools/board_tool.py preflight` or
`python tools/board_tool.py flash bench/p0_timing --compile-only`.
The Bash entry points remain available with a native Linux adb. Logs use the same
receive-only Python socket program on the board; ADB never reads local keyboard
input. Set connection variables in the invoking shell, never tracked credentials.

Research/provenance: state/analysis/P0_G3.md and P0_G4.md. USB discovery is now
observed; compile/upload evidence is recorded separately. `dump_match.sh` belongs to P2 and
`plot_match.py` to eligible P6; neither is falsely implemented as a successful stub.

## Reviewed P0 RAM observations

`p0_capture.py` runs with Python on the board and accepts only the exact reviewed
default timing artifact. `p0_matrix_capture.py` is a separate observer for the exact
default matrix artifact. Neither is a general debugger or firmware uploader.
Copy the reviewed script(s) and `p0_mem_read.cfg` together to a fresh board tools
directory, verify their recorded hashes, and supply the pinned `--artifact-dir`
and a fresh `--output` child under `/home/arduino/sumox26-capture/`.

The tools verify installed files, compare every loader/sketch flash byte, resolve
bounded runtime symbols, and retain raw results with explicit failures. The timing
tool requires60000 completed samples and identical snapshots. The matrix observer
only establishes counter advancement; it cannot verify optical appearance or clock
accuracy. MEM-AP readout uses the internal debug connection without reset/halt or
MCU memory writes; it still perturbs the bus and must not overlap a timing workload.
No Bridge/Monitor round trip, complete control-loop WCET or phase gate follows.

These helpers are deliberately tied to core1.0.0 and their specific artifact
hashes. A changed build requires a new inspected/reviewed identity record, not
blind hash replacement. Current receipts live in `state/analysis/P0_*20260922*`
and the corresponding `state/reviews/` reports. The README's older installed/
compile-pending statements are superseded by FACTS F-062 onward; outstanding
physical/API restrictions remain.
