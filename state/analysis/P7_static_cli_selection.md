# Static startup: installed CLI selection evidence

25 September 2026, Asia/Dubai. Independent local review of the coordinator's
Linux file-only receipts. No CLI selection query, compiler, upload, reset or MCU
command ran for this investigation. Only this note was added by the reviewer.

## Receipts and corrections

All paths below are within `P7_static_startup_raw/`; originals remain unchanged.

| Receipt | Outcome and evidence boundary |
|---|---|
| `cli_selection_inventory.json` | FAILED exit 1: guessed 100000 B installed.json cap rejected the file; empty stdout. No completed inventory follows from this attempt. |
| `cli_installed_metadata_size.json` | Exit 0: installed.json is a nonsymlink regular file of 303397 B. |
| `cli_selection_inventory_observed_bound.json` | Exit 0/empty stderr: observed-size bound, core text/hashes, version directories and absence checks. Its empty installed_selected_platforms projection used the wrong root-level platforms path. |
| `cli_installed_dependencies.json` | Exit 0/empty stderr: correct packages[].platforms[] projection finds exactly one arduino:zephyr 1.0.0 and its 13 tool dependencies. |

The corrected installed metadata retains 303397 B/SHA256
`985d3ba102ebf440eca4fb9a9f767b35134e3d827919224bb7635b4b106f86f9`,
matching the complete inventory. Its wrapper version is 2 and IsTrusted is true;
those are observed metadata fields, not an independent authenticity proof.
Local comparison confirms its name/architecture/version/archive checksum and
all 13 tool dependencies equal the selected package_index.json entry, including
exactly one `arduino:remoteocd` dependency at 0.1.1. The original empty projection
does not establish missing platform metadata and is preserved as a parser error.

## Independent comparisons and selection inference

Raw UTF8 text from the complete receipt was encoded and compared byte-for-byte
with `P2_bridge_dependency_raw/installed/core/` and independently SHA256-hashed:

| File | Bytes | Equal retained, receipt and text SHA256 |
|---|---:|---|
| boards.txt |6101|`bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84`|
| platform.txt |20947|`d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638`|

The installed zephyr version directory contains only 1.0.0. The remoteocd
directory contains only 0.1.1; the checked package roots are SiliconLabs, arduino,
builtin and zephyr, with no other remoteocd directory observed. CLI SHA b8786322
and remoteocd SHA 2a3f820b match the prior full pins in upload_inventory.json.
UID 1000/boot 6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6 and /dev/null character-device
major/minor 1/3 were observed. All five checked override locations were absent:

- Selected core `boards.local.txt` and `platform.local.txt`.
- `/home/arduino/.arduino15/packages/platform.txt`.
- `/home/arduino/Arduino/hardware/platform.txt` and its `hardware` directory.

Together with pinned CLI source, these observations support selection of
`arduino:zephyr:unoq:link_mode=static`, core 1.0.0 and remoteocd 0.1.1 under the
fixed environment and `--config-file /dev/null` in [the route audit](P7_static_upload_route.md).
Board options override platform defaults: static chooses bin-zsk.bin, while
omitted wait_linux_boot retains wait. The recipe and raw app.ino.bin selector
therefore resolve the existing checked app.ino.bin-zsk.bin sibling. This is a
source-and-file inference, not a fresh executed CLI selection/upload result.
It does not establish future directory stability or exclusive ownership.

## Why no CLI property query was executed

Pinned CLI 1.5.1 supports `board details --fqbn arduino:zephyr:unoq:link_mode=static
--show-properties=expanded --json`. The command calls BoardDetails, but instance
initialization can create missing directories, download missing indexes, install
missing builtin tools and migrate old installed.json metadata. Updater=false
does not disable these paths; this inventory does not establish initialization
purity for every installed platform/tool. A selection query was unnecessary.
Official pinned sources: [command](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/cli/board/details.go),
[initialization](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/commands/instances.go),
[resolution and migration](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/packagemanager/package_manager.go),
[override loading](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/packagemanager/loader.go).

## Next task and limits

Implement, independently host-test and review the one-shot upload wrapper and
host coordinator using the existing D144 packet and completed D153 collector.
Bind reviewed HEAD/source, fresh file/tool/config/selection identities, raw
selector and actual payload; use exact fixed environment and bounded deadlines.
Consume a new identified inert attempt durably before upload, distinguish upload
outcome from capture, preserve independent postchecks and no reset/retry recovery.
Do not rebuild or copy another source tree. These receipts supply no native run
permission, startup/live-memory/WCET proof, physical acceptance or human gate.
No disposable scratch, binary copy, Python cache or new framework was created.
