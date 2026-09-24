# Proposed one-shot static/M0 runner

2026-09-25. Design only, following `76dc5b56` and the frozen
[parent contract](P7_static_link_probe_contract.md). D141's pure policy component
is host-complete; this proposal does not adopt a runner, artifact validator,
properties query or compile. No board, toolchain or helper was invoked here.

## Public interface and transport boundary

Propose one public function in a future scoped `run_static_probe.py`:

```python
run_probe(*, compile_only: bool, run_id: str, receipt_dir: Path,
          command: Callable) -> dict
# command(board: str, argv: list[str], *, capture: bool,
#         timeout: int) -> subprocess.CompletedProcess[str]
```

`compile_only` must be exactly `True`; `run_id` is exactly 32 lowercase hex digits.
`command` is required, with no default. It receives only runner-generated argv,
not caller-supplied commands. Synthetic tests supply a recording fake returning
`CompletedProcess` or raising the same process exceptions as the real transport;
they need no monkeypatch or private implementation access. The real adapter is
the unchanged `board_tool.remote`. It receives explicit `capture=True` and the
reviewed per-command timeout. Validators and filesystem/identity checks are not
replaceable callbacks. Tests may use a fresh temporary receipt directory while
reading the same fixed local inputs; the production launcher fixes its receipt
parent to this task's `runs/` directory.

Import has no command/write side effect. A future CLI refuses missing or unknown
arguments before transport access; its only execution form is explicit
`--compile-only --run-id <id>`. No MATCH/startup/FQBN/source/path/flags option,
upload route, retry or cleanup route. The real launch binds the reviewed runner
SHA and the existing ADB transport to serial `2629958581`, with the known ADB
executable identity. Permission to execute remains the coordinator's separate GO.

Do not call `board_tool.flash`, `stage`, `compile_app`, `app_preflight` or the
D139 `invoke_checked.py`: their embedded dynamic-policy calls, global transport
calls or monkeypatching do not fit this interface. Call unchanged
`verifiedStage(board_tool, 'app', source_manifest, stage_manifest)` directly.
Reuse common `validate_cli`, `resolved_directory`, `check_overrides`,
`installed_pins` and `verify_hashes`; the latter two remote-reading helpers receive
the runner's receipt-writing command adapter. Parse the captured `core list`
with the same installed `arduino:zephyr`/`1.0.0` predicate as `verify_core`, whose
global transport call prevents direct substitution without monkeypatching.

## Fixed local authority and locations

Verify each reviewed literal hash **before importing/using** that dependency,
and again at completion. No editable manifest may redefine these accepted bytes.
The launcher verifies the new runner's own reviewed hash before invocation;
the runner records that hash and pins its non-self inputs below. Additional future
artifact-validator code/data must get their own reviewed pins before composition.

| Repository-relative input | SHA256 |
|---|---|
| `tools/board_tool.py` | `3f2dac6d2b0f75209d335f5045e5233aab2dea8ca9edd740b69a652476ddf2bc` |
| `tools/app_build_policy.py` | `d5a4ce59870574ac601c3d8837b472adf7eec81e86982794fa16a7b3b354a7c6` |
| `tools/app_build_commands.json` | `63f6c41e34bae9fce1d945c3271b3fe86343f27544affe25ae14788438d62e1d` |
| `tools/app_build_pins.json` | `55720e65b03f6cd28964c675ceeec76619824cd11525549fbac0503b8efa972b` |
| `P7_static_link_probe_raw/static_policy.py`* | `ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775` |
| `P7_static_link_probe_raw/static_reference.json`* | `1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b` |
| `P7_static_link_probe_raw/additional_pins.json`* | `d8dc249656cef0a852af8385d59fbdd3e9e30ace2dcb113921bf7964483fe924` |
| `P7_default_qualification_raw/reuse_stage.py`* | `78e173296c1d4366e4866b947b017814d69be2055c739cf1d96d0980eb40900e` |
| `P7_default_qualification_raw/working_source_manifest.json`* | `c106c0fb8baaf0a6f2536558da0084bd7d236c4ee8e77a4110b60107ad073391` |
| `P7_default_qualification_raw/checked_stage_manifest.json`* | `56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a` |
| `P7_static_link_probe_contract.md`* | `d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae` |

\* These abbreviated paths start at `state/analysis/`. The ADB executable SHA is
`e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982`,
retained in D139 `inventory.json`; its absolute configured path must also match
the reviewed launcher. The source authority remains the literal digest
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.

Let `R=/home/arduino/sumox26_codex_build`, `S=R/<source-digest>/app`, and
`U=R/_app_builds/static-app-probe-v1/<source-digest>/bench-default/<run_id>`.
Only `U/build` and `U/artifacts` are compiler output locations. Reuse `S` read-only:
require its exact 102-file set, hashes/digest and nonsymlink ancestry. Missing,
extra or changed remote source is a stop, not permission to sync/overwrite it.

## One command sequence

1. Validate request and literal local pins, then run `verifiedStage`: exact current
   103 source files, 102 stage files, source mapping/digest and both config checks.
   Exclusively create the new local receipt directory after validating its path
   and ancestry. Any existing destination, including a symlink, is a rejection.
2. Through the captured command adapter, confirm target identity/connectivity,
   CLI version, core list and resolved CLI data/user directories. Validate them
   with the existing rules. Record narrow resource/compiler inventory; a running
   compiler or inadequate resources stops this run rather than queues/retries it.
3. Verify `S` by exact relative file-set enumeration plus hashes, rejecting special
   files/symlinks. Run unchanged override checks against `S`. Merge all 18 existing
   dependency pins with the eight additional pins, rejecting any duplicate path,
   then verify all 26. Never drop an old pin or substitute a changed hash.
4. Atomically claim `U` with exclusive directory creation after checking its fixed
   ancestry. Missing intermediate policy/profile directories may be created only
   at the derived paths and checked for nonsymlink directories; an existing `U`
   fails. Exclusively create `build` and `artifacts`. Do not use `mkdir -p` to
   accept an existing run or remove anything to make a claim succeed.
5. Issue exactly one properties query, validate with
   `static_policy.validate_preflight(text, build_path=B, data_dir=D)`, then recheck
   local/remote source identity, pins/overrides and absence of all fixed output
   destinations. A properties query that produced an old-looking output still
   fails. Query scratch is not evidence of a compiler invocation.
6. Issue exactly one actual compile, validate its captured JSON with
   `static_policy.validate_compile_result(...)`. No second compiler invocation
   follows any outcome. After a terminal result, recheck local/remote source bytes,
   overrides and all dependency pins; retain these checks on compiler failure too.
7. For success, collect the seven fixed payloads below with regular-file,
   containment, size and hash checks. Validate artifact identity separately before
   any overall artifact-probe verdict. The runner alone can report only
   `STATIC_COMPILE_COLLECTED`, never `STATIC_ARTIFACT_PROBE_PASS`.

With `B=U/build` and `A=U/artifacts`, the compiler argv is exactly:

```text
arduino-cli compile --jobs 1 --json --fqbn arduino:zephyr:unoq:link_mode=static
  --build-path B --output-dir A
  --build-property "compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0"
  --build-property "compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0"
  --build-property "build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0"
  S
```

The sole query is this same argv with `--show-properties=expanded` inserted before
`S`. Pin/config/claim/source-check commands are literal reviewed command templates
with validated path arguments, not arbitrary shell text. No source synchronization
or new framework is needed.

## Fixed collection and failure evidence

| Public role | Canonical newly produced path |
|---|---|
| `elf` | `B/app.ino.elf` |
| `debug_elf` | `B/app.ino_debug.elf` |
| `temp_elf` | `B/app.ino_temp.elf` |
| `bin` | `B/app.ino.bin` |
| `elf_zsk` | `B/app.ino.elf-zsk.bin` |
| `bin_zsk` | `B/app.ino.bin-zsk.bin` |
| `map` | `B/app.ino.map` |

Also require the selected export `A/app.ino.bin-zsk.bin` to equal canonical
`bin_zsk`; it is a checked copy, not an eighth distinct payload. All eight paths
must be absent before compile. Record pre/post size/hash metadata and reject
missing/empty/nonregular/replaced files. Freshness rests on exclusive directories
and absent destinations, not timestamps. Enforce the artifact contract's frozen
byte limits before reads. Use base64 over the text transport to preserve bytes
(D140's failed CRLF-altered `cat` transfer remains a cautionary receipt), then
verify decoded hashes and rehash remote files after collection. Seven payloads
may be held transiently for the separate validator; persist only its required
compact evidence and one checked final ELF locally, retaining the others on Linux.

Every command gets a monotonically numbered planned-argv receipt before dispatch,
then start/end UTC, timeout, real return code and complete observed stdout/stderr
before validation. Preserve transport-decoded text as such; retain raw exception
bytes without lossy conversion if supplied. `CalledProcessError`, timeout and
launch failure are recorded and propagated; an unavailable return code is null,
never fabricated zero. Keep the first failure plus subsequent collection/check
failures separately. A timeout leaves remote compile completion **unknown**:
do not retry, claim terminal completion, accept artifacts or kill/reset anything.

The public result should contain receipt location, terminal status, query/compile
attempt counts, source identity and seven artifact identities; transient byte
delivery to the artifact validator is settled with its separate interface.
Synthetic tests can assert callback order/argv/counts, pre-compile tripwires,
stale outputs, partial responses, timeouts and original failure retention.
Runner/public artifact interfaces, command templates, output bounds and new code
still require coordinator adoption, independent frozen tests and separate review.
