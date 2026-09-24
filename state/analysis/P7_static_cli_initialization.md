# Static upload: CLI initialization prerequisites

25 September 2026, Asia/Dubai. Independent local receipt/source review only.
No board call, CLI invocation, installation, upload or MCU operation by reviewer.
Reviewed `P7_static_startup_raw/cli_initialization_inventory.json`, 19987 bytes,
SHA256 `aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62`.
The recorded file-only call exited zero with empty stderr at 03:45 Dubai.
Its bootstrap hashes the frozen helper before memory-only import; inspection
used descriptor file reads/directory enumeration, not the helper's command main.

Observed data, staging and packages directories exist. Package index remains
1691790 bytes/SHA3cb9691d; library index is 58226703 bytes/SHA36dad4c2. The
scanned hardware subtrees contain zephyr1.0.0 metadata303397 bytes/SHA985d3ba1,
wrapper version2. Identity remains UID1000, Linux/aarch64 and boot6d4aca1b.

These existing paths address the corresponding missing-directory and first-index
download triggers under the fixed empty config/environment; they do not prove
successful index parsing or complete initialization purity. The pinned CLI
creates missing download/packages directories, and firstUpdate downloads absent
library/package indexes. [Initialization source](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/commands/instances.go)

Metadata migration requires index.Version below packageindex.Version and a
nonnull indexed platform release. Current format is2, so the observed selected
version2 file does not take that write branch. [Migration condition](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/packagemanager/package_manager.go),
[format version](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/packageindex/index.go)

Initial review identified two concrete evidence gaps in that receipt:

1. The five latest indexed builtin version directories exist: ctags5.8-arduino11,
   dfu-discovery0.1.2, mdns-discovery1.1.0, serial-discovery1.5.2 and
   serial-monitor0.15.0. This is insufficient for IsInstalled: builtin releases
   additionally require `<name>` or `<name>.exe` within InstallDir to exist.
   Init installs a latest builtin release when this predicate is false.
   Check the five exact Linux tool files with bounded nonsymlink regular-file
   reads; preserve identities/hashes, without executing them.
   [Installed predicate](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/tools.go#L96-L102)
2. The inventory skips packages lacking a hardware child. CLI loading instead
   falls back to the package root, supporting both ARCH/boards.txt and
   ARCH/VERSION/boards.txt. Therefore the receipt does not yet establish that
   the selected zephyr metadata is the entire installed platform load set.
   Bounded listings of the SiliconLabs/builtin/zephyr package roots can close
   this if each contains only tools; otherwise inspect those observed candidates.
   Preserve the separately checked user-hardware absence.
   [Hardware loading paths](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/packagemanager/loader.go#L117-L237)

The bounded follow-up `P7_static_startup_raw/cli_builtin_files_inventory.json`
is17400 bytes/SHA256
`a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb`;
exit0/empty stderr, same identity, recorded03:47Dubai. It finds each of the five
exact latest-version Linux executables as a nonsymlink regular mode0755 file,
records full hashes/sizes and ELF magic, and observes absent .exe alternatives.
Those files satisfy the builtin existence predicate for the inspected versions.
Its three fallback package roots each contain only the tools directory; the
pinned loader explicitly excludes tools from platform discovery (loader.go
lines165-166). Thus both specific inventory gaps are closed at observation time.
This follow-up ran no tool binary and does not alter the original receipt.

Disposition: the stated bounded directory/index/builtin/selected-metadata
prerequisites have source-and-file support. Runtime purity, execution readiness,
future stability and target startup remain unproved. The native coordinator
still needs fresh prerequisite/path postchecks, reviewed source/HEAD/D144
bindings and one identified inert-run scope. No native grant follows.
