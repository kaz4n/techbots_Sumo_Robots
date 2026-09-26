# P0 tooling contract

## D099/D100 checked app compilation

Canonical `app --compile-only` selects the fixed `native-app-v1` policy with
pinned CLI1.5.1/core1.0.0 and the reviewed discovery-phase override. It rejects
sketch profiles and local/global overrides, checks18 installed hashes, validates
84 effective command properties before compilation, then checks the real result,
absence of external libraries and four generated artifact hashes. Every build
uses fresh policy/source/mode paths. Raw preflight/compiler evidence is retained
under `build/app-receipts/<run-id>/`. Failure stops the workflow explicitly.
Compiler failure keeps its original exit status even if saving evidence fails.
Both output receipts are attempted independently; save and diagnostic failures
are reported without retrying or deleting partial evidence (D181).

Actual default, inert Immediate and MATCH compile-only builds passed on2026-09-23.
Their82sources, nineELFs, startup/import/motor-branch differences and explicit
library-discovery rejection experiment passed separate fresh same-model review.
D099-R1 is addressed. Read `state/analysis/P2_app_build_validation.md` and
`state/reviews/P2_app_acceptance_review.md` for exact evidence and limits.

The override is not an official Bridge-disable option and rejects every external
library. Stable CLI/configuration/files across commands remain an assumption;
this is not a sandbox against a compromised build host. Property-only output does
not prove compilation or library discovery. Compiler low-memory warnings remain;
loadedRAM, stack, physical timing and all human gates require separate evidence.
Bench commands/upload guards are retained; unscoped app uploads remain disabled.
The explicit precompiled MATCH route below requires separate evidence and permission.

## Inhibited full-app diagnostics

D188 compiled the fixed static `bench/app_motor_fault` image and audited its
actual ABI/entry. D190 run02 later uploaded it and observed four successful
application epochs/41callbacks followed by an explicit inhibited halt. These
owners/scopes are consumed; do not rerun `compile_app_motor_fault.py` or its old
manifests. Exact historical commands remain in their receipts and contracts.
Read the [actual result](../state/analysis/P7_app_motor_fault_run02_validation.md)
and [current handoff](../state/CODEX_HANDOFF.md).

D192 adds `bench/app_motor_observe` for a longer finite host-tested observation.
It keeps the unchanged Trace's first64 calls, reports subsequent omitted calls
explicitly, and preserves the first failure/current call after truncation.
It uses real Runtime epochs with empty peripheral grants and requires
`MATCH=0`, `MOTORS_ALLOWED=0`, `SUMOX_MOTOR_FAULT_PROBE=1` for future admitted use.
The checked-in probe default remains0. Its epoch/poll bounds live in config.h.

Generic flash/build commands reject both diagnostic sketches before staging or
transport. New staging requires a fresh attempt and exact canonical Trace files.
D193 provides the separate fixed compile-only launcher
`python -B tools/compile_app_motor_observe.py --check-only --reviewed-head <40hex>`.
It requires its exact prepared manifest and a clean reviewed HEAD. Execution uses
the same arguments with `--execute` and the required isolated pycache prefix;
read the [compile contract](../state/analysis/P7_app_motor_observe_compile_contract.md)
and current handoff before use. Each attempt is consumed once, including failure.
The launcher projects pinned existing validators privately and preserves their
original disk hashes, exact static/default/M0 flags and independent closing checks.
It cannot upload firmware. New actual artifact/ABI/entry and capture bindings
remain separate; no historical address layout substitutes for that evidence.
See the [D192 contract](../state/analysis/P7_app_motor_observe_contract.md).

## D182/D183 identified precompiled MATCH upload

Build-only remains `bash tools/flash.sh app --match --compile-only`. Once the
specific artifact, target and operation have real qualification and fresh human
permission, the separate upload command is:

```
bash tools/flash.sh app --match --deploy-scope <repo-relative-scope.json>
```

This uploads and starts motor-capable firmware. It never compiles, stages or
syncs sources. Plain `--match` is not permission; combining a deployment scope
with `--compile-only`, a bench sketch, default startup or an ADC run is rejected.
The wrapper uses Python `-B`; direct Python invocation must also use `-B`.

The exact scope schema is in
`state/analysis/P7_match_deploy_contract.md`. It binds current source, prior
checked dynamic/Immediate build receipts, raw and packaged artifacts, loader/
tool files, target/boot, qualification and a referenced current-session human
`STAND OK` or `RING OK`. Authorization lasts at most one hour and covers only
that identified request. A JSON record or test fixture cannot establish the
truth or authorship of physical evidence or a human message; the operator must
verify their provenance before invoking this command. No approved scope is
supplied by the software implementation.

Each attempt exclusively owns `state/analysis/match_deploy_<run_id>/`; failures
and partial claims consume it. The existing transport and uploader perform one
upload with checked prerequisites and independent closing checks. A timeout or
unaccepted result after dispatch is `UNKNOWN`: the MCU may have started. Preserve
both local and remote evidence and establish the actual state before considering
any newly authorized attempt. Never retry or delete the consumed attempt.
Remote full streams stay in the derived upload directory; compact replies carry
their report size/hash, which cannot independently verify omitted stream bytes.
Host tests validate this workflow; native execution and physical acceptance remain
separate requirements.

D104 applies the same checked policy to `bench/runtime_inert` with its existing
default-startup/inert-only restrictions and exact reviewed upload identities.
D107 also selects it for `bench/opp_view --compile-only`, with default or
Immediate startup and inert flags only. Its generic-build artifacts were rejected
for inherited Bridge initialization. Opponent-view uploads, MATCH and sketch
profiles are refused before transport; no upload manifest entry was added.
Other bench recipes retain their existing behavior. See the named bench README
and `state/analysis/P2_opp_view_contract.md` for the source and hardware limits.

D109 adds only `bench/qtr_raw` to those checked inert sensor-bench compile routes.
It also permits default/Immediate compilation, refuses MATCH/profiles/uploads,
and adds no upload identity. Its default pad grant is false and its finite RAM
capture does not establish physical QTR color or timing acceptance.

D-075 MotorGate target checks use
`python tools/board_tool.py flash bench/p2_motor_gate_compile --compile-only`
and the same command with `--match --compile-only`. Both only build on board
Linux; the probe never enters an upload allowlist. Its setup stores a function
address, with no motor backend or method execution. Active-branch compilation
does not grant motor-run permission. Host CMake runs both the normal suite and
a separate `motor_gate_enabled_tests` executable using simulated checked I/O.

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
Checked Python callers may use `stage(sketch, attempt='motor-fault-active01')`
to claim `build/stage/motor-fault-active01/<sketch-name>/` exclusively. The token
is 1–48 lowercase letters/digits/underscores/hyphens, starts with a letter or
digit, and cannot be a Windows reserved device name. Existing attempts and
linked staging ancestry fail explicitly; partial copies remain after failure.
This internal API performs source preparation only and has no CLI flag. Callers
must select fresh ownership and retain evidence before any later cleanup.
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
Both flag orders are valid. `--compile-only` permits staging, inventory, app
configuration/property/hash checks and compilation; never upload, reset, start
or monitor. Missing target/config,
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
upload, confirm the bare-board setup and installed dependencies. Unscoped
motor-capable uploads fail; only the separately identified precompiled MATCH
route above accepts a qualified, source-bound run. `--match` cannot grant permission.
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

`python3 -B -m unittest discover -s tests/tooling -v` uses controlled SSH/rsync
substitutes. These tests must check argument rejection, all flag combinations,
default macros, actual staging include paths, strict host checking, no upload/
reset/start during compile-only, wrong core, and propagation of SSH/sync/compile
failures. A substitute returning zero is script-test evidence only.

Broad discovery also includes historical fixed-scope oracles and newer tests
that require a fresh evidence directory. It is not currently a wholly passing
single-command suite. In particular, D202 preserves D197's complete-symbol
equality failure after eliminating two read-only metadata symbols and one local
helper symbol; its successor
checks and locked motor suites pass separately. No assertion is filtered or
excluded. Use the exact commands and evidence owners in
`state/analysis/P7_motor_expected_metadata_validation.md` for that scoped result;
do not rerun a consumed owner. `tools/test_host.sh` remains the separate CMake/
CTest entry and does not discover these Python oracles.

## Explicit USB ADB fallback

Set `SUMO_TRANSPORT=adb`, `SUMO_ADB_SERIAL` to the observed USB serial, and optionally
`SUMO_ADB_EXECUTABLE` to the installed adb executable path (default: `adb`). The
serial is mandatory even with one device. The wrapper does not request device selection, server restart, root escalation,
package installation or network discovery. The ADB client can itself restart a
local server on a protocol mismatch; preserve its diagnostic output.
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

`p0_adc_capture.py` adds a separately pinned observer for D-063's default-startup
ADC diagnostic. It uses the same unchanged passive helper/config, verifies full
loader/sketch identity, and requires two identical completed1000-call RAM records
with unchanged extension metadata. Negative API results fail acceptance; zero is
valid raw data. Report first-call and999 subsequent-call statistics separately,
without subtracting the measured micros overhead. Setup can hang: the Linux
observer's deadline does not cancel a blocking MCU ADC call. This is empirical
bare-board API timing, not voltage calibration, runtime boundedness or a gate.
`python tools/board_tool.py flash bench/p0_adc --compile-only` only builds;
omitting compile-only is eligible solely for the reviewed inert default snapshot.
Immediate ADC uploads remain rejected. See the ADC contract, review and receipts.

`p0_gpio_capture.py` observes the separately pinned D-064 builtin-LED GPIO image.
The source readiness check and400 finite setup samples record configure/write/
read/pair timings and exact LOW/HIGH/HIGH readbacks. Capture requires final HIGH,
all records complete, full image identity and stable BSS/records; microsecond
quantization and possible debug overlap remain explicit. The named red LED is
PH10/index50, not D13; no external header pin is exercised. Default-only reviewed
upload, no motor authority. Build-only: `python tools/board_tool.py flash
bench/p0_gpio --compile-only`. See `state/analysis/P0_gpio_contract.md`.


## Offline recorder CSV validation (D-074)

Validate three existing D-073 CSV files locally:

```sh
python3 tools/validate_csv_bundle.py --frames logs/example_frames.csv --events logs/example_events.csv --summary logs/example_summary.csv
```

Add `--manifest logs/example_manifest.json` only when caller-declared metadata
exists. Exact schema and optional manifest format are in
`state/analysis/P2_csv_bundle_contract.md`. The validator uses the Python standard
library and writes one JSON report to stdout; it never changes input files or
contacts a board. It does not read today's config to infer historical settings.

Exit0 means local format and cross-file consistency checks passed; exit1 reports
a file/schema/consistency/manifest failure; exit2 is invalid CLI usage. A report
with recorded loss or an unfinished attempt can still exit0 because those facts
are valid evidence. Inspect `recording` separately. Missing provenance remains
ABSENT; supplied values are declarations, not verified MCU/session identity.

Validation accepts arbitrary ordinals, wrapped/equal timestamps, raw unknown
codes, INVALID/CLAMPED frames and lifetime loss counters without rewriting the
input files. Detailed evidence remains in those CSVs. Local byte hashes
cannot prove a common attempt, transport completion, live IDLE, free RAM or
physical200s/no-gap acceptance. D090 adds the receiver below; physical live
transport qualification remains pending.
Synthetic fixtures are test evidence only and must be labeled SYNTHETIC.

## IDLE recorder capture (D090)

`bash tools/dump_match.sh --input path/to/wire.txt --output-dir logs` validates
an offline wire fixture without contacting hardware. Omit `--input` to receive
from the board's loopback Monitor socket over the existing configured SSH/ADB
transport. Start capture before the local LOG_DUMP service trigger. The command
only receives; it never uploads firmware, requests motion, resets the robot or
restarts the router. D101/D103 implement the app dump and inhibited local reset
services in software; their physical native transport acceptance remains pending.

Successful capture publishes a unique directory with frames/events/summary CSV,
manifest, validation report, capture metadata and original wire bytes. Protocol,
CRC or connection failures retain a `.partial` directory and error report. If
saving the error report also fails (for example, the disk is full), the failure
diagnostic retains the original error, partial-directory path and failed-save
details. Existing partial files remain available; capture is not retried or
published as successful. A successful interrupted/loss-bearing capture still
reports its loss. Optional
`--firmware-revision`, `--source-sha256` and `--config-sha256` are caller declarations;
local hashes and an offline capture do not prove physical source or acceptance.
Live `--timeout` defaults to330seconds (range1..3600); connection timeout is at most
10seconds. Native UART cancellation permanently poisons that firmware instance's
transport; MCU reset alone does not establish a clean Linux decoder. Never
automatically restart `arduino-router`: its stop hooks can reset the MCU.

## Observable capture connection (D113)

The optional connection ticket lets a second terminal check whether a particular
capture has a live TCP connection while the capture command is still running.
Set `SUMO_TRANSPORT` explicitly to `ssh` or `adb`, with its corresponding target;
these optional modes require it even when ordinary SSH capture uses the default.
Generate a fresh ticket for every attempt; use the printed value in both commands:

```
python -c "import uuid; print(uuid.uuid4().hex)"
python tools/dump_match.py --connection-ticket <fresh-ticket> --output-dir logs/run-new --timeout 30
python tools/dump_match.py --observe-connection <same-ticket>
```

Start the observation command in a second terminal. The tool never backgrounds
itself or starts a transmitter. Observation exits0 for a valid JSON observation;
check its `state`, which can be PENDING, CONNECTED, TERMINAL, EXPIRED or UNKNOWN.
Operational failures exit1 with error evidence. Invalid argument combinations
exit2 before contacting the board. Observation cannot combine with capture or
offline options. Ordinary captures without a ticket retain their existing path.

CONNECTED proves only a sampled TCP connection to the board's loopback Monitor.
It does not acknowledge registration inside the router, guarantee future bytes,
prove clean UART framing, or grant MCU/motor permission. The connection may close
immediately after the query. Keep the corresponding capture process running and
associate its newly generated ticket with this attempt. Reusing a capture ticket
fails before connection; querying an old still-live ticket describes that original
capture, never a newly attempted one.

The receiver retains small immutable Linux receipt files under a fixed private
`/tmp/sumox26-dump-connection-<ticket>` directory. They record the actual claim,
connection and terminal outcome. The observer checks bounded process/socket
metadata and never opens a UART, sends application bytes/RPC, changes a service,
resets the MCU or uploads firmware. A missing or expired receipt is not readiness.
Receipts stay available for review; the tool does not remove or repair them.

Final `capture.json` or `error.json` includes `connection_evidence` for an opt-in
capture. Connection/metadata/receive failures preserve actual partial wire bytes;
an observed END still needs the existing CRC and CSV validation. A ticket adds
one final metadata query bounded to5seconds after the ordinary capture command's
timeout+15 outer bound. It never extends the remote receive deadline. No ticket
or offline capture has null connection evidence and needs no observation query.

## D091 inert recorder evidence

`python tools/board_tool.py flash bench/recorder_inert --compile-only` compiles the
bare-board synthetic recorder probe. Default-only inert uploads require its exact
separately reviewed source key in p0_inert_sources.json; MATCH uploads remain
blocked. For the identified D091 run, the already-built ELF/ZSK bytes were checked
and uploaded separately, preserving exact reviewed artifact identity.

`recorder_capture.py` is a pinned board-Linux read-only MEM-AP collector with its own
48-read/2MiB/16KiB-RAM/64-command/600s-sequence/30s-command ceilings. Copy it alongside
unchanged p0_capture.py/p0_mem_read.cfg and recorder_heap.py, preserving reviewed
hashes. Its fixed artifact pins are run-specific; different firmware requires
new review. CAPTURED means collected evidence, including any actual failure/loss.
recorder_heap.py decodes only the pinned262144B LLEXT pool offline; capacity is a
point-in-time observation. None of these tools supplies motion commands or proves
native UART transfer, physical B8, calibrated MCU time or complete robot WCET.

## Bare A1 observation probe (D114)

`python tools/board_tool.py flash bench/ui_adc_probe --compile-only` uses the
checked default-startup, MATCH0/MOTORS_ALLOWED0 route. It stages the exact four
existing UI bench implementation files beneath src/ with one true-grant wrapper.
The ordinary bench/ui remains default-disabled. Immediate, MATCH, conflicting
profiles and uploads are refused. An actual run needs the separately reviewed
exact target/readout and identified run record described in
state/analysis/P2_ui_adc_probe_contract.md. Floating A1 codes have no expected
voltage or logical button meaning; SC-A and SC-AJ remain open.

## Full synthetic recorder transport bench (D116)

`python tools/board_tool.py flash bench/recorder --compile-only` selects the
checked default-startup, MATCH0/MOTORS_ALLOWED0 build. The sketch is disabled by
default and performs no native setup or transmission. MATCH, Immediate, sketch
profiles and every upload are refused. This is separate from the previously
reviewed terminal `recorder_inert` image.

The enabled software scenario records a full 200-second synthetic attempt,
completes the real STOP tail and inhibited service reset, then requests the
existing IDLE log dump through actual menu gestures. Host reception and native
UART success are separate checks. Read `state/analysis/P2_recorder_transport_contract.md`
and its validation status before use; UART ownership, clean framing, throughput
and an identified native run remain explicit prerequisites.

## P4 target-loss interval analysis (D130)

`python tools/analyze_target_loss.py logs/p4_loss/cohort.json` reads existing local
CSV bundles and prints a JSON report. It checks ten qualified D129 intervals
against the declared 35000us bound; incomplete, excluded or M0 evidence cannot
satisfy the cohort. Exit0 means arithmetic PASS, not physical acceptance or a
motor-run authorization. See [the schema and interpretation](../docs/target_loss_analysis.md).

## Fixed B4 retained-memory capture (D219)

`capture_b4_recorder.py` is the fixed, reviewed motor-disabled capture caller.
Its one admitted `capture01` has completed; the attempt owner is consumed and
must not be rerun. See the [actual capture and CSV evidence](../state/analysis/P7_b4_recorder_actual_validation.md).
The saved files contain an EMPTY recorder with zero frame/event samples.
`decode_b4_capture.py` validates that fixed packet and `decode_b4_recorder.py`
handles its exact compiled layout. Their integrity checks retain origin and
coherence as unproven. This path does not qualify native UART/Bridge delivery or
replace the match IDLE log dump. A different image or later capture needs its own
current artifact/layout bindings and fresh attempt scope.


## Shared commissioning app compilation (D222)

Use `python -I -B tools/compile_commissioning_app.py --check-only --profile PROFILE --motors-allowed 0 --attempt native01 --reviewed-head FULL_HEAD`, then the same arguments with `--execute` after admission. Profiles: b4_stand, p3_drive, p3_turn, p3_stop, p4_reactive, p4_timing, p5_abort_timing. Motors must be explicitly 0 or 1. This compiles the real main application with static/default startup and MATCH0; it never uploads. Keep one compiler at a time and retain/commit each owner before the next. See state/reviews/P7_commissioning_build_review.md for the admitted matrix and failure handling.

D223 observe_uart_holders.py produced one consumed privileged metadata-only observation; its exact source/transport and actual review are under state/analysis/P7_uart_holder_raw and state/reviews/P7_uart_holder_actual_review.md. It is evidence of two samples, not a general UART preparation or recurring privilege command.


## Identified full recorder delivery (D224/D225)

`run_recorder_delivery.py` runs one inhibited 200-second synthetic recording on
an identified bare UNO Q. Its checked-in bench identity remains disabled. Read
[the contract](../state/analysis/P7_recorder_delivery_contract.md) and
[accepted source/host review](../state/reviews/P7_recorder_delivery_review.md)
before a native attempt. One fresh 32-character lowercase hex attempt supplies
a positive uint64 wire session; use the same attempt and exact current committed
HEAD for `--check-only`, `--compile`, then `--run`. No automatic retry is allowed.

```
python -I -B tools/run_recorder_delivery.py --check-only --attempt HEX32 --reviewed-head HEAD40
python -I -B tools/run_recorder_delivery.py --compile --attempt HEX32 --reviewed-head HEAD40
python -I -B tools/run_recorder_delivery.py --run --attempt HEX32 --reviewed-head HEAD40
```

Keep HEAD unchanged between compilation and delivery. Compilation must close
successfully with all artifact and identity checks. Existing upload scratch must
be independently cleared by its exact reviewed cleanup; this caller never deletes
it. The receiver is armed before the single static/default M0 upload and requires
the expected identity on every wire record. A TCP connection alone is not readiness.
A complete result requires 5,001 zero-duty frames, eight expected events, SEALED,
no reported loss and the declared timing bounds. Raw partial/failed captures remain
saved. This establishes synthetic target software evidence only, not sensor,
motor, physical timing or human gate acceptance.


### Guarded commissioning deployment (D227)

`deploy_commissioning_app.py` selects an existing checked D222 build for one of
the seven fixed commissioning profiles. Use the exact source/artifact-bound scope
in [the contract](../state/analysis/P7_commissioning_deploy_contract.md):

```text
python -I -B tools/deploy_commissioning_app.py --check-only --scope RELATIVE_JSON --reviewed-head HEAD40
python -I -B tools/deploy_commissioning_app.py --execute --scope RELATIVE_JSON --reviewed-head HEAD40
```

M0 scopes must prove disabled setup. M1 additionally requires actual source-bound
qualification, the original human phase prerequisite and fresh specific STAND OK
or RING OK. Current BOARD ONLY supplies none of those M1 prerequisites. The tool
performs no compilation, capture, cleanup or retry. Host acceptance is recorded
in [validation](../state/analysis/P7_commissioning_deploy_validation.md).

## Identified application delivery (D240)

`run_app_identified_delivery.py` pairs a qualified commissioning upload with
the receiver and validates the complete recording. Use `--check-only`, then
`--execute`, with `--scope RELATIVE_JSON --reviewed-head HEAD40` as specified
in [the contract](../state/analysis/P7_app_identified_delivery_contract.md).
The compiled stream ID is 1; its positive session must equal the first 16 hex
digits of the run ID. Each image/session is single use, including failed runs.
The caller requires the existing dump setup grants, qualification and specific
motor-run permission. Current board-only setup cannot supply those facts.
Standalone commissioning deployment continues to refuse identified sessions.

## Static competition firmware (D241)

The fixed production selection is MATCH1/MOTORS_ALLOWED1, all diagnostic
profiles off, static linking and Immediate startup:

```text
python -I -B tools/compile_match_static.py --check-only --profile match --motors-allowed 1 --attempt TOKEN --reviewed-head HEAD40
python -I -B tools/compile_match_static.py --execute --profile match --motors-allowed 1 --attempt TOKEN --reviewed-head HEAD40
```

Compilation does not upload or run the firmware. Keep a single compiler active
and retain the complete result. The exact FQBN is
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`.

Future `deploy_match_static.py` and `run_match_identified_delivery.py` accept
`--check-only` or `--execute`, followed by `--scope RELATIVE_JSON
--reviewed-head HEAD40`. Both require exact source/artifact qualification and
fresh STAND OK or RING OK for that run. The paired route additionally requires
the compiled fresh session and dump grants and validates the full recording.
See [the fixed selection and scope contract](../state/analysis/P7_match_static_contract.md).
Host tests and a compile-only result do not supply physical qualification.
