# D099-R1 pinned CLI override and preflight source audit

2026-09-23 Asia/Dubai. Independent bounded source audit; no production
implementation inspected, no board/LAN/USB operation, no compile/upload/reset.
Read AGENTS, current PROGRESS, FACTS, D099 contract and checkpoint review. The
date is Wednesday 23 September; PLAN section 3 schedules P0 acceptance today,
but the recorded pending human gates are not changed by this audit.

## Result

The supported hook-free property preflight is **`compile
--show-properties=expanded --json`**, using the exact controlled FQBN,
build-property arguments, sketch, explicit build path and environment intended
for the later real compile. It returns before preprocessing, discovery compiler
commands and build hooks. It still initializes the CLI/platform instance and
creates the explicit build directory; it is not a general no-side-effects API.

Resolve directories first with **two separate calls**, `config get
directories.data --json` and `config get directories.user --json`. Each returns
one JSON string and includes defaults and environment aliases. `config dump
--json` is not a substitute: it can omit default directory values.

The original D099 contract forbids show-properties. Adoption of this remedy
therefore requires a recorded narrow amendment authorizing only the separate
property preflight, without weakening the real compile/JSON/artifact checks.
This report does not modify that contract or declare D099-R1 closed.

## Source identity and citation convention

All CLI sources are pinned to Arduino CLI 1.5.1 commit
`01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea`. Existing cached files remain in:

- `A/` = `state/analysis/P2_bridge_dependency_raw/primary/arduino-cli/`
- `B/` = `state/analysis/P2_bridge_dependency_raw/schema/primary/`
- `N/` = `state/analysis/P2_app_override_raw/source_audit/primary/`

The new files were retrieved only from
`https://raw.githubusercontent.com/arduino/arduino-cli/<commit>/<path>`.
`P2_app_override_raw/source_audit/retrieval*.json` records exact URLs, SHA256,
Git blob SHA1 and comparison with the previously cached commit tree. An initial
guessed `commands/service_init.go` is absent from that tree; its failure remains
in the initial receipt. The actual implementation is `commands/instances.go`.
The final `identity_verification.json` independently checks the new and reused
CLI sources against that same pinned tree. References below use the exact
on-disk line numbers of these primary files.

## Earliest property-only return and result shape

1. `N/internal/cli/arguments/show_properties.go:43-62` accepts `expanded` and
   sets the present-without-value default to `expanded`. Use the explicit value.
   The enum comment about a valueless flag at line 36 is stale; executable
   `NoOptDefVal` at line 62 controls that behavior.
2. `A/internal/cli/compile/compile.go:231-256` sends `ShowProperties=true` and
   `DoNotExpandBuildProperties=false` for expanded mode. It uses the same
   `CompileRequest` and service as a real compile.
3. `B/commands/service_compile.go:131-138` registers the common BuilderResult
   response and sets board/build platform references. Lines 256-279 construct
   the builder with the requested custom properties; lines 292-315 register
   build path, diagnostics and sorted build properties. Lines 312-313 expand
   those properties. Lines 317-320 return on ShowProperties, before the
   preprocessing branch at 322-331 or real Build call at 374-375.
4. `B/internal/arduino/builder/builder.go:140-165` merges selected board
   properties, runtime sketch/path values and custom build properties. Its
   constructor ends at 249 without running build recipes. The first build
   hook runs inside `preprocess()` at 304-306. `Build()` invokes that function
   at 371-372; `Preprocess()` also invokes it at 282-283. Thus preprocess is
   not a hook-free substitute. The compilation-database warning in
   `A/docs/platform-specification.md:523-525` independently confirms pre-hooks
   run in database-only mode.
5. `A/internal/cli/compile/compile.go:383-394` uses the same JSON compileResult
   wrapper and BuilderResult conversion for property-only and real compile.
   This supports strict envelope/property parsing for preflight. It does not
   prove a binary exists or that no library would be used: used-library
   collection is registered only after the early return, at
   `B/commands/service_compile.go:333-344`. Keep actual-compile acceptance
   separate, with its required library and artifact checks.
6. Explicit build path still causes `MkdirAll` at
   `B/commands/service_compile.go:210-212`. Omitting it also invokes cache
   directory creation/purge bookkeeping at 173-208. Use the intended fresh
   explicit path for both calls; do not label the preflight filesystem-read-only.

## Effective directory query, configuration and environment

- `N/internal/cli/config/get.go:56-85` calls SettingsGetValue once per named
  argument and prints its decoded value. With `--json`, one directory argument
  produces one JSON string. Two arguments produce two separate results, so use
  two calls when expecting exactly one JSON value per stdout.
- `N/commands/service_settings.go:141-157` looks in active settings, then
  `settings.Defaults`, and JSON-encodes the value. This exactly matches the
  active-then-default lookup in
  `N/internal/cli/configuration/directories.go:55-60,77-81` for user/data.
  Relative configured paths are returned as relative strings; rejecting empty
  or nonabsolute values is a valid fail-closed wrapper policy, not a CLI promise.
- `N/internal/cli/config/dump.go:38-54,65-75` emits
  `{"config": <saved settings object>}`. ConfigurationSave serializes settings
  at `N/commands/service_settings.go:169-180`; embedded Map.MarshalJSON emits
  only `c.values` at `N/internal/go-configmap/json.go:20-22`. Defaults are held
  separately at `N/internal/cli/configuration/configuration.go:32-45`.
  Dump includes injected environment values, but missing directory keys must
  not be guessed from it.
- Startup reads the selected file in `N/main.go:41-61`; ConfigurationOpen
  unmarshals it then injects environment values at
  `N/commands/service_settings.go:190-213`. Modern environment keys use
  `ARDUINO_` plus uppercase dotted-key components separated by underscores
  (`N/internal/go-configmap/cli.go:113-145`).
- Legacy aliases are applied **after** modern environment injection at
  `N/internal/cli/configuration/defaults.go:83-98`: particularly
  `ARDUINO_SKETCHBOOK_DIR` overrides `directories.user` and `ARDUINO_DATA_DIR`
  overrides `directories.data`, even if modern aliases were supplied.
- Config-file selection is implemented in
  `N/internal/cli/configuration/configuration.go:120-149`: split argv
  `--config-file PATH`, then `ARDUINO_CONFIG_FILE`, then
  `ARDUINO_DIRECTORIES_DATA/arduino-cli.yaml`, then
  `ARDUINO_DATA_DIR/arduino-cli.yaml`, finally default data dir plus filename.
  Split `--config-dir PATH` changes that default data dir at 121-130 and 50-55.
  The startup scan checks exact tokens: do not assume `--config-file=PATH` has
  equivalent behavior here. Use split argv if explicitly controlling config.
- Linux defaults derive from the actual process home, not a hardcoded username:
  data is `HOME/.arduino15` at configuration.go:57-65 and user is `HOME/Arduino`
  at 82-91. `N/docs/configuration.md:81-92` documents flags over environment
  over file. Preserve identical effective config argv, environment and cwd
  across directory queries, property preflight and real compile.
- Neither config get nor config dump calls instance Init in its command body.
  They do perform common CLI startup/configuration work; do not generalize this
  into a guarantee of zero file writes or every possible subprocess.

## Applicable override files and merge order

| Route | Proven location and effect | Primary evidence |
|---|---|---|
| Base platform | Selected install directory `/platform.txt` | `N/internal/arduino/cores/packagemanager/loader.go:282-288` |
| Local platform | Same directory `/platform.local.txt`, merged after base | `N/.../loader.go:291-296` |
| Base/local boards | Selected install directory `/boards.txt`, then `/boards.local.txt`; board properties and menu choices come from their merged map | `N/.../loader.go:440-463`; `B/internal/arduino/cores/board.go:129-155` |
| Global package properties | Effective `directories.data/packages/platform.txt` | `N/commands/instances.go:83-98`; `N/.../loader.go:38-46,89-98` |
| Global sketchbook properties | Effective `directories.user/hardware/platform.txt`; loaded after data/packages and wins on duplicate global keys | Same sources, plus `N/.../loader.go:53-56` |
| Other platform references | Variant/core/board-platform properties are merged, then board/menu properties | `B/internal/arduino/cores/packagemanager/package_manager.go:332-346` |
| Runtime/tool properties | Added after platform/board merge; custom globals are merged last in ResolveFQBN | `B/.../package_manager.go:348-402` |
| Explicit custom properties | CLI `--build-property` request values merge after resolved board properties and sketch/build path additions | `A/internal/cli/compile/compile.go:231-239`; `B/internal/arduino/builder/builder.go:140-165` |

Here `N/.../loader.go` and `B/.../package_manager.go` abbreviate the full
packagemanager paths already shown in the table. The global loader explicitly
opens only root `platform.txt`; it does **not** load root `platform.local.txt`
or root `boards.local.txt` as global properties. Platform-local files remain
applicable in each selected/referenced install directory. The IDE 1.x hardware
root in the general platform specification is not an additional root loaded
by the audited ordinary CLI instance. The ordinary CLI uses exactly data and
user roots above; selected profiles have a separate route below.

`platform.txt` byte pinning alone therefore cannot establish the effective
recipe policy. The narrow policy can reject presence of either global
platform.txt and any selected platform.local.txt/boards.local.txt, pin selected
base boards.txt as well as platform.txt, and compare the entire effective
recipe/compiler/hook/path configuration before compilation. Treat dangling
symlinks and unreadable/ambiguous paths as failures, not verified absence.

## FQBN, profiles and startup bounds

- There is no supported CLI configuration key named `custom_fqbn` in the
  complete defaults schema (`N/internal/cli/configuration/defaults.go:24-80`).
  `N/internal/go-configmap/configuration.go:63-68` rejects unknown settings
  keys; YAML loading turns setting errors into warnings
  (`N/commands/service_settings.go:195-199`). Do not invent a custom_fqbn
  override API. A wrapper-local setting by that name requires a separate
  wrapper audit, outside this source-only assignment.
- Supported selection includes explicit `--fqbn` and `--board-options`
  (`N/internal/cli/arguments/fqbn.go:38-55`), then selected profile/default FQBN,
  then port autodetection (`fqbn.go:75-98`). Exact controlled FQBN plus no
  uncontrolled board-options arguments is the minimal policy.
- Explicit FQBN does **not** suppress profile initialization:
  `A/internal/cli/compile/compile.go:174-187` initializes the selected/default
  profile before resolving FQBN. `N/internal/arduino/sketch/sketch.go:219-228`
  recognizes root `sketch.yaml` or fallback `sketch.yml`.
- Profile initialization can select global hardware or install/cache pinned
  platforms: `N/commands/instances.go:249-269`; profile cache is
  `directories.data/internal` (`N/internal/cli/configuration/directories.go:67-73`).
  `N/internal/arduino/cores/packagemanager/profiles.go:83-96` loads platform
  files from that cache, potentially installing missing content first. Reject
  either sketch metadata file and any explicit profile on this narrow policy
  before invoking show-properties. Do not merely check filename absence in the
  repository if stale metadata could remain in the staged sketch.
- Init can update missing indexes/install missing builtin tools
  (`N/commands/instances.go:179-205,276-310`) and registers discoveries at
  321-324. Registration adds clients; it starts them only if the discovery
  manager is already running
  (`N/internal/arduino/discovery/discoverymanager/discoverymanager.go:119-140`).
- `N/internal/cli/arguments/port.go:74-104` returns without BoardListWatch when
  there is no explicit/default/profile address, but starts watching when an
  address is present. With controlled FQBN, rejected sketch metadata and no
  port/profile arguments, the audited selection path does not request board
  enumeration. This is narrower than claiming no possible subprocess: ordinary
  initialization still has the missing-index/tool behavior just described.

## Minimal fail-closed remedy and tests

1. Before any app compile, enforce the already-pinned CLI identity, controlled
   mode/FQBN/property argv, and app-upload rejection. Resolve data/user via the
   two scalar JSON config queries in the same execution environment.
2. Reject ambiguous directory/query results. Check the two resolved global
   platform.txt paths, selected local overrides, and both staged sketch metadata
   names before show-properties. Pin the selected base boards/platform files
   and reviewed tools/dependencies before permitting hooks.
3. Run only the explicit expanded property preflight. Require its strict
   successful JSON envelope and expected board/build platform/path identities.
   Compare effective compiler commands, compiler/link flags, all recipe entries
   and all hooks with the reviewed policy, including absence of unexpected
   keys. Do not infer safety from only the extra_flags metadata. Dynamic values
   such as source/build paths must be bound to the chosen run, not ignored.
4. Permit the actual compile only after every check passes. Recheck properties
   and pinned identities afterward and retain the separate artifact/library
   requirements. Two processes have a possible concurrent file-change window;
   the policy should state its stable build-environment assumption or stage
   reviewed immutable inputs. Postcompile checks detect drift but cannot undo a
   hook already executed.
5. Independent failure tests should cover each global/local route; redirected
   roots through both modern and legacy environment keys; changed boards/menu
   properties; both sketch metadata names; preflight JSON errors; altered
   effective recipes/compiler executable/hooks; unexpected additional hook key;
   and assurance that real compile is never invoked after preflight failure.
   A harmless controlled fixture can separately confirm no hook sentinel is
   executed by the show-properties call. This report has not run such a CLI
   behavior fixture and does not replace it with source inference.

Modified files: this report and only its owned `P2_app_override_raw/source_audit/`
sources/receipts/helper. Source identification passes are evidence of source
identity and control flow, not target behavior. Next action: root records the
narrow contract amendment, implements/tests the remedy, and obtains separate
fresh review before any D099 adoption claim. No phase gate or physical claim.
