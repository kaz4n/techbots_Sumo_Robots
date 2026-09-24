# D141 static reference preparation

2026-09-25 Asia/Dubai. Source/reference preparation only, synchronized to the
final contract's policy-only host adoption. Policy implementation and host tests
may follow the independent oracle freeze; artifact/runner implementation,
properties queries and native compilation remain unapproved. No board command,
expanded-properties query, compiler, download, tool execution, source copy or
policy implementation occurred in this preparation.

## Public file schemas and identities

- `static_reference.json`: flat JSON object mapping all 84 controlled property
  keys to exact strings. SHA256
  `1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b`.
- `additional_pins.json`: flat JSON object mapping eight absolute path templates
  to lowercase SHA256 strings. SHA256
  `d8dc249656cef0a852af8385d59fbdd3e9e30ace2dcb113921bf7964483fe924`.

Only `@DATA_DIR@` and `@BUILD_PATH@` are variable template tokens in the property
map. They denote the validated CLI data directory and exclusively claimed new
build directory, respectively. They are substituted literally after path
validation, without adding or removing slashes. `@@DATA_DIR@` in a compiler
response-file argument is one literal `@` followed by the DATA_DIR token.
The pin map uses only `@DATA_DIR@` and must be merged additively with every
unchanged production pin; a duplicate/conflicting path must not replace a pin.

The reference fixes `app.ino`, `-DMATCH=0 -DMOTORS_ALLOWED=0`, static link mode
and wait/default startup. There is no SAFETY_FLAGS or BOOT_ARGUMENT parameter.
Existing recipe placeholders such as `{object_files}`, `{archive_file}`,
`{includes}`, `{source_file}`, `{object_file}` and `{archive_file_path}` remain
literal parts of the reference exactly as in the checked CLI property result.
The retained unresolved `{runtime.tools.imgtool.path}` literal likewise stays
unchanged in the inactive postbuild property; this is not an extra substitution.
Whitespace, quoting and inactive properties remain significant.

The coordinator-owned pure validators separately enforce fixed non-controlled
properties: FQBN `arduino:zephyr:unoq:link_mode=static`, core/variant/platform,
project/discovery/flags, compiler location, default boot mode, build path and
`upload.extension=bin-zsk.bin`. They must compare the controlled key set exactly,
not accept a subset, and verify the reference file's bytes against its reviewed
literal SHA256 before using it. Reference drift must not redefine acceptance.

## Derivation and reconciliation

Read the retained raw platform assignments and non-menu `unoq.*` board
assignments, with the board values overriding platform values. Expand their
nested brace references in the already-captured D139 CLI context, fixing safety
and discovery flags. All 84 controlled keys have source assignments; none was
invented from observed output. Unknown compiler recipe placeholders stay literal.
Normalize the validated baseline data/build paths to the two public tokens.

As a control, expansion with the original dynamic/default selection matched
all 84 production reference values exactly after resolving its two old
SAFETY_FLAGS/BOOT_ARGUMENT tokens to their fixed literals: zero mismatches.
Then select the two static menu assignments from boards.txt (`build.link_mode`
and `upload.extension`), keep wait startup, and expand again. No CLI was run.

Exactly 14 values differ from that fixed dynamic baseline:

1. `build.check_command-dynamic`, `build.link_command`, `build.link_mode`.
2. `recipe.c.combine.1.pattern` through `.4.pattern`, and
   `recipe.c.combine.pattern`.
3. Both `recipe.hooks.objcopy.postobjcopy.*.pattern` values,
   `recipe.output.save_file`, `recipe.output.tmp_file`,
   `recipe.size.pattern`, and `build.zip.pattern`.

The inactive `build.check_command-dynamic` also receives static wrap flags:
its source references the selected `build.link_command`. It retains its
dynamic check scripts and is not executed by static combine step 1 (`true`).
Retaining the old expanded inactive value would be an incorrect static map.
The single-pass legacy recipe and Windows variants also remain in the exact
84-key set; no inactive key has been dropped or relaxed.

## Additive dependency and audit pins

The existing 18 production pins remain authoritative and unchanged, including
`build-static.ld`, core `main.cpp`, compiler binaries and packaged loader.
Six build dependencies are newly bound: `memory-static.ld`, `syms-static.ld`,
the exact firmware config, gen-rodata-ld 0.1.1, zephyr-sketch-tool 0.4.1 and
zephyr-check-size 0.1.0. Their expected hashes come from D140 closing hashes.
D140 recovered embedded Go build information; module paths alone do not prove
source repository URLs. The coordinator owns that source mapping/review.

Two audit pins are supported by retained evidence:

- GDB: `8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778`,
  cross-bound by D140 installed/closing hashes and successful file-only queries.
- readelf: `c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e`,
  from the retained exit-0 identity receipt, also independently bound by the
  later exact-file fixture receipt. This is historical identity evidence;
  any eventual authorized run must check the installed bytes against it.

No trustworthy retained objdump hash was found in the bounded receipt search.
Objdump is therefore neither pinned nor authorized by this manifest. Use the
bound GDB/readelf path or obtain separate exact evidence before adding it.
No new installed-file hash was requested during this preparation.

## ARM identity and remaining review decision

The retained boards/CLI recipe fixes cortex-m33, fpv5-sp-d16 and hard float;
the machine-flags response file remains pinned by the existing policy. Its
contents were not newly collected or inferred. Direct local ELF-header reads
give these exact existing-artifact observations:

| Artifact | SHA256 | Type | e_flags |
|---|---|---|---|
| Packaged loader, `P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf` | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` | ET_EXEC | `0x05000400` |
| Current D139 default app | `72a8bfcd320e8bfff7e5bcc6ef8607a98f9033866f3fa3d2be2cb95433e42f1d` | ET_REL | `0x05000000` |
| Current D138 MATCH app | `cb5fbb53ce4089ef682977a66fd5337491f150f17ca2cfdcd150a0dd6bca07d4` | ET_REL | `0x05000000` |

All three are little-endian ELF32, EM_ARM (40), ELF version 1, System V OSABI
and ABI version 0. The strongest proposed static expectation is exact
`e_flags=0x05000400` (EABI5/hard-float), matching the pinned executable loader
and hard-float architecture selection. **This is a derived expectation for
review, not an observed static app.** No retained app linked with this exact
static recipe was identified. The coordinator must settle/freeze this exact
acceptance value before artifact-validator implementation or native execution;
this note does not silently
accept both REL and EXEC flag values or infer flags from compiler success.

The packaged loader retains a 62-byte `.ARM.attributes` section, but the
static app linker script explicitly discards `.ARM.attributes` and descendants.
The proposed static expectation is absence, rather than requiring that loader
section verbatim. Thumb entry/address acceptance remains a separate check.
The loader attribute bytes are:

`413d000000616561626900013300000005382d4d2e4d41494e000611074d09030a0812041301140115011601170318011a011b011c011e04220126012e01`

No static section layout, flags, load extent or runtime has been measured.
The executable flag/section policy still needs coordinator adoption and fresh
independent tests/review under the contract. D139 remains negative by 592 bytes.

## Exact preparation inputs

Paths below are repository-relative. These hashes bind the files actually read;
they do not upgrade the draft or authorize execution.

| Path | SHA256 |
|---|---|
| `state/analysis/P7_static_link_probe_contract.md` | `d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae` |
| `state/reviews/P7_static_link_probe_contract_review.md` | `51cf270b10df947ffe0cdeaa2e2bf0f7417f55da0b55cd6d623094df39da2b6f` |
| `tools/app_build_policy.py` | `d5a4ce59870574ac601c3d8837b472adf7eec81e86982794fa16a7b3b354a7c6` |
| `tools/app_build_commands.json` | `63f6c41e34bae9fce1d945c3271b3fe86343f27544affe25ae14788438d62e1d` |
| `tools/app_build_pins.json` | `55720e65b03f6cd28964c675ceeec76619824cd11525549fbac0503b8efa972b` |
| `state/analysis/P2_bridge_dependency_raw/installed/core/platform.txt` | `d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638` |
| `state/analysis/P2_bridge_dependency_raw/installed/core/boards.txt` | `bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84` |
| `state/analysis/P7_default_qualification_raw/app/receipt/properties.stdout.json` | `e01b7a00c14465f84331745479869d98c3bcbeb8520d1cd5949c6b974d18bb62` |
| `state/analysis/P7_static_link_research_raw/memory-static.ld` | `cbe17b74e93d2a05f4e101366d036e6a9b3d89d400855349734d5419984d6341` |
| `state/analysis/P7_static_link_research_raw/build-static.ld` | `04be061156ebb88fa43537c811e0a8fdc2b721d1bcc0a1a9ac5990018536123e` |
| `state/analysis/P7_static_link_research_raw/syms-static.ld` | `f4f05a8a411196fad575360a1b6cc9f5f10a337864548e7387fb8580c4092d62` |
| `state/analysis/P7_static_link_research_raw/closing_hashes.stdout` | `f4531e2615303d8ccf7712ef66120ab9d7ff5757b25eb667dc0e4a83608ca488` |
| `state/analysis/P2_recorder_bench_raw/readelf_identity.json` | `c589d6ae66b01ab2be203298acb8570e31aea113a14ccf36b7299dd6f3fc5da6` |
| `state/analysis/P2_app_default_probe_raw/fixture_tools/receipt.json` | `4b2394f503177677cc5474139031194fc909e1ed8ab080bebec21035f9e3ad14` |

Only the three assigned new preparation files were written. JSON duplicate/key
and placeholder checks, dynamic-reference reconstruction, raw-byte hashes and
local ELF header reads were performed; no new independent oracle was read.
