# Existing static packet: upload-route source audit

25 September 2026, Asia/Dubai. File/source inspection only. No upload, reset,
compiler or board command was run by this reviewer. This note defines command
resolution for a separately guarded run; it grants no execution authority.

## Exact packet and installed route

D144 query/compile receipts `P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/0011.json`
and `0017.json` select `arduino:zephyr:unoq:link_mode=static`, default/wait startup,
`MATCH=0`, `MOTORS_ALLOWED=0` and `upload.extension=bin-zsk.bin`. Retained
`P2_bridge_dependency_raw/installed/core/boards.txt:55-57,75,81-86` and
`platform.txt:197-198,319-323` bind the packaged loader and flat sketch to remoteocd.
The ELF-ZSK is diagnostic and must not replace the flat package.

Define the following exact existing directory, with no new staging or build:

`/home/arduino/sumox26_codex_build/_app_builds/static-app-probe-v1/fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2/bench-default/f0220228320c4b2aa20c3e5e8264c813/build`

| Existing file within that directory | Bytes | SHA256 |
|---|---:|---|
| `app.ino.bin` | 93080 | `bd03c2e7ff19e599f78f4e1c1861e6216ad88f949b009b4b7c93070028f704ed` |
| `app.ino.bin-zsk.bin` | 93096 | `5f08afe0fc2d261b093644f6bca6720182c277009d00e646207151e7f940629a` |

D148's `P7_static_link_probe_raw/native_actual/result.json` binds both files and
the equal exported flat package to the original D144 Claim/FileRecords.
`P7_static_startup_raw/upload_inventory.json` newly observes CLI executable
`/usr/bin/arduino-cli` SHA256 `b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433`
and remoteocd executable
`/home/arduino/.arduino15/packages/arduino/tools/remoteocd/0.1.1/remoteocd`
SHA256 `2a3f820b867d113a82a86470f2caa128bc15b52303ad4ce0a5cbd62002cb2b60`.
D144 version receipt `0002.json` reports CLI1.5.1 commit01f3d4f2b.

## Input-file resolution, before selecting executable arguments

CLI commit01f3d4f2b forwards `--input-file` as `ImportFile`.
[Flag/request source, lines67-69 and175-187](https://github.com/arduino/arduino-cli/blob/01f3d4f2b/internal/cli/upload/upload.go#L67-L69).
It removes only the final extension, sets the parent as `build.path`, and sets
the remaining basename as `build.project_name`. The recipe then adds its own
`upload.extension`. Its tool launcher does not change working directory.
[Resolution and launch source, lines415-427,659-710,723-737](https://github.com/arduino/arduino-cli/blob/01f3d4f2b/commands/service_upload.go#L723-L737).

Consequently, the source-confirmed fixed selection is `--input-file` pointing
to the existing **raw `build/app.ino.bin`**. This resolves project `app.ino` and
uploads the checked sibling **`build/app.ino.bin-zsk.bin`**, not the raw BIN.
Passing `app.ino.bin-zsk.bin` as input-file would instead construct
`app.ino.bin-zsk.bin-zsk.bin` and is incorrect. Input-dir discovery is heuristic:
a directory containing only the flat package cannot supply the recognized
`.ino`/`.pde` basename after one extension is removed. The current receipt does
not enumerate every exported-directory entry; do not assert its completeness.
[Directory algorithm, lines740-804](https://github.com/arduino/arduino-cli/blob/01f3d4f2b/commands/service_upload.go#L740-L804).
[Valid sketch extensions](https://github.com/arduino/arduino-cli/blob/01f3d4f2b/internal/arduino/globals/globals.go#L23-L31).

The proposed exact argv has no port, programmer, property override or compile:

```text
/usr/bin/arduino-cli
upload
--fqbn
arduino:zephyr:unoq:link_mode=static
--input-file
/home/arduino/sumox26_codex_build/_app_builds/static-app-probe-v1/fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2/bench-default/f0220228320c4b2aa20c3e5e8264c813/build/app.ino.bin
/home/arduino/sumox26_codex_build/fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2/app
```

This argv is source-derived, not a successful native command receipt. The new
run must bind both raw selector and actual flat payload before use. It must
also preserve absent sketch profiles/default-programmer overrides. No old
consumed upload or compile approval covers this command.

## OpenOCD includes, working directory and activation

remoteocd0.1.1 copies loader, sketch and flash configuration into
`/tmp/remoteocd/`, preserving basenames. It calls `/opt/openocd/bin/openocd`
with `-s /opt/openocd`, then `-s /opt/openocd/share/openocd/scripts`, relative
`-f openocd_gpiod.cfg`, and absolute `/tmp/remoteocd/flash_sketch.cfg`.
[flash.go, lines19-77](https://github.com/arduino/remoteocd/blob/0.1.1/flash.go#L19-L77).
LocalCmd starts OpenOCD without setting its directory; it inherits the caller's
working directory, not the copied-file directory.
[local.go, lines19-27](https://github.com/arduino/remoteocd/blob/0.1.1/board/local.go#L19-L27),
[process.go, lines41-55 and150-167](https://github.com/arduino/go-paths-helper/blob/v1.14.0/process.go#L41-L55).

For the installed OpenOCD reported commit e6a2c12f4, resolution checks the
working directory first, then explicit `-s` paths in order. Environment/user
defaults are appended after those paths.
[configuration.c, lines54-87](https://github.com/arduino/OpenOCD/blob/e6a2c12f4/src/helper/configuration.c#L54-L87),
[options.c, lines275-277 and327-330](https://github.com/arduino/OpenOCD/blob/e6a2c12f4/src/helper/options.c#L275-L277).

The observed config chain is `openocd_gpiod.cfg` -> `stm32u5x.cfg` ->
`target/swj-dp.tcl`, `mem_helper.tcl`, `stm32x5x_common.cfg`. The last three
files have no further source directives. The second receipt,
`P7_static_startup_raw/upload_include_inventory.json`, supplies the only missing
included file pin: `/opt/openocd/share/openocd/scripts/mem_helper.tcl`,1021B,
SHA256 `01794a37e9a8bdc20e2304ee64e9d70549c0872f5f6c40fa032a165bcbba1fd2`.
It observes cwd `/home/arduino`, all five corresponding home shadow paths
absent, and `/tmp/remoteocd` absent. Its home checks are duplicated; they do not
check `/opt/openocd/mem_helper.tcl` or `/opt/openocd/target/swj-dp.tcl`.
Those two higher-priority candidate paths need an absence check before claiming
the exact include resolution. No broader filesystem audit follows from this.

The checked680B `flash_sketch.cfg` SHA256
`38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c`
initializes, resets/halts, conditionally writes loader and sketch, resets again,
waits100ms, writes `0xCAFFEEEE` to `0x40036400`, then shuts down. These are
intrinsic upload/activation effects and must be inside the single new run scope;
no separate reset is needed. Neither source inspection nor upload-command success
proves successful static startup, live memory, WCET or physical acceptance.

## Configuration isolation refinement, 25 September

For the later reviewed command, prepend `--config-file /dev/null` after the
absolute CLI executable and construct the child environment from literals:
HOME=/home/arduino, USER=LOGNAME=arduino, PATH=/usr/bin:/bin, LANG=LC_ALL=C,
ARDUINO_DIRECTORIES_DATA=/home/arduino/.arduino15,
ARDUINO_DIRECTORIES_USER=/home/arduino/Arduino,
ARDUINO_UPDATER_ENABLE_NOTIFICATION=false. Do not inherit ambient overrides.
Require /dev/null to be an unlinked character device with major/minor1/3.

The primary-source chain is recorded in the follow-on section of
[D153 design review](../reviews/P7_static_startup_design_review.md). Explicit config
selection reads /dev/null; the YAML parser accepts empty bytes; environment
directory settings override defaults. This needs no new config file or download.

Actual read-only receipts `P7_static_startup_raw/cli_isolated_config.json` and
`cli_isolated_directories.json` confirm unchanged pinned CLI1.5.1/01f3d4f2b and
both intended directories with update notification false. All three CLI queries
returned0/empty stderr. The first config projection mistakenly looked for
top-level directories and retained null; the corrected observation uses
`data['config']['directories']` and preserves complete output. The original
receipt remains unchanged. No upload, OpenOCD, compiler or MCU operation occurred.
This refines the proposed argv/environment; it is not a native execution grant.
