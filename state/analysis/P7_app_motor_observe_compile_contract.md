# D193 fixed static observation compile projection

26 September 2026. Host implementation under D051 follows D192. This contract
adapts the reviewed D188 compile-only lifecycle to app_motor_observe without
copying that lifecycle or changing historical sources. It creates no actual
manifest, board/boot claim, native invocation, upload, reset or MCU observation.
Native use requires separate fresh admission, reviewed source and clean HEAD.

## Public surface and private loading

Add only tools/compile_app_motor_observe.py for execution. Preserve the original
tools/compile_app_motor_fault.py, tools/app_motor_fault_static_policy.py and
tools/app_motor_fault_compile_remote.py bytes. No firmware or old test changes.
Public functions are parse_request(argv), project_caller(raw),
project_adapter(raw), project_remote(raw), read_original(relative, *, root=ROOT),
load_caller(*, root=ROOT), and main(argv). ROOT is this repository's absolute
root; the optional root argument supports controlled local fixtures only.

Import defines functions/constants only: no source reads, dispatch, writes or
native work. parse_request accepts exactly the original list-of-strings CLI:
--check-only|--execute --reviewed-head <40 lowercase hex>. It returns action/head;
reject wrong argument types, order or count before source loading. main first
validates arguments and Python -B, then calls load_caller(root=ROOT) and delegates
once to that private module's unchanged main(argv), returning its result. Only
the new launcher's own __main__ guard dispatches; never execute a historical
module with __name__='__main__'. No alternative executable mode or profile.

read_original accepts only the three exact original relative names below and
returns their bytes after ordinary-path, bound, identity and digest checks.
Require plain directories through the full ancestry and one ordinary regular
file with link count1; reject symlink/junction/reparse/special paths. Read at most
65537 bytes, require 1..65536 bytes, and compare pathname snapshots before/after
with descriptor snapshots before/after reading. Compare device, inode, mode,
link count, size, mtime_ns and Windows attributes across path/handle; ctime_ns
must remain stable within each API, but Windows path/handle ctime need not equal.
On other platforms ctime also matches across APIs. Preserve primary read/check
errors when descriptor closure also fails; a lone close failure fails loading.
No source may execute until all three originals and projections are verified.

Each project_* accepts exactly bytes, verifies its original byte count/SHA256,
performs only the table's ordered byte replacements with exact occurrence counts,
then verifies projected byte count/SHA256. It performs no I/O or execution.
No newline normalization, broad name replacement, AST reformatting or fallback.
Missing/additional occurrences, altered originals or projection drift fail closed.

load_caller reads all three originals, verifies all three projections, then
executes only the projected caller in a fresh private ModuleType. Its __file__
is root/tools/compile_app_motor_fault.py, keeping original ROOT/default-argument
derivation correct. Provide project_adapter and project_remote in that private
namespace before execution. Do not publish private modules in sys.modules or
alter another module's globals. The projected original caller's main guard must
remain false. Return the private module with its original CompileDiagnostic
class and methods; loading alone must not instantiate an owner or dispatch.

Before returning, extend its HARD_PINS with the original caller and original
remote-helper hashes below, and extend REQUIRED with these HARD_PINS. Keep every
inherited hard pin. ADAPTER and REMOTE_HELPER remain the original paths; both
local admission and closing check original disk bytes. self.code retains original
bytes, never projected replacements. The new launcher and contract are pinned by
the exact future manifest/clean reviewed HEAD, avoiding recursive self-hashes.

## Frozen byte identities

| Original relative file | Bytes | SHA256 |
|---|---:|---|
| tools/compile_app_motor_fault.py | 29802 | cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a |
| tools/app_motor_fault_static_policy.py | 8262 | 3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270 |
| tools/app_motor_fault_compile_remote.py | 6891 | 1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2 |

| Projected source | Bytes | SHA256 |
|---|---:|---|
| caller | 29904 | 830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884 |
| adapter | 8266 | e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d |
| remote | 6897 | f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c |

These are exact working bytes, including their line endings. The original
caller/remote hashes supplement the unchanged D188 dependency hard pins.

## Exact ordered substitutions

Caller substitutions, in this order:

| Old literal bytes | New literal bytes | Count |
|---|---|---:|
| CALLER = 'tools/compile_app_motor_fault.py' | CALLER = 'tools/compile_app_motor_observe.py' | 1 |
| P7_app_motor_fault_compile_contract.md | P7_app_motor_observe_compile_contract.md | 1 |
| P7_app_motor_fault_compile_raw | P7_app_motor_observe_compile_raw | 1 |
| app-motor-fault-static | app-motor-observe-static | 6 |
| 'app_motor_fault.ino' | 'app_motor_observe.ino' | 1 |
| bench/app_motor_fault | bench/app_motor_observe | 4 |
| 'app_motor_fault' | 'app_motor_observe' | 2 |
| '/app_motor_fault' | '/app_motor_observe' | 1 |
| STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS | STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS | 1 |
| self.code[ADAPTER] | project_adapter(self.code[ADAPTER]) | 2 |
| self.code[REMOTE_HELPER] | project_remote(self.code[REMOTE_HELPER]) | 2 |

Adapter substitutions, in order: replace quoted 'app_motor_fault.ino' with
'app_motor_observe.ino' once; replace STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS
with STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS once. Keep seven legacy alias
values app.ino<suffix>, D187's84-property/24-name/5-flag reference guards, raw
response validation, pinned imports and all D147/D142 checks unchanged.

Remote substitutions, in order: app-motor-fault-static01 becomes
app-motor-observe-static01 once; quoted 'app_motor_fault.ino' becomes
'app_motor_observe.ino' once; app-motor-fault-static-artifacts-v1 becomes
app-motor-observe-static-artifacts-v1 once; original adapter SHA256
3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270 becomes
projected adapter SHA256 e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d
once. Keep its synthetic original tools/... __file__ and private dependency hook.
Derived aliases and file/path tables are constructed by executing these projected
definitions, never repaired after validation or bypassed by permissive lookups.

The two caller adapter substitutions select projected bytes for local metadata
validation and the remote artifact bundle. The two remote substitutions select
projected bytes for both the compressed source packet and its source_sha guard.
The remote bundle retains original helper/extension/base bytes and checks the
projected adapter hash. Keep payload/response/compression/canonical encoding bounds.

## Fresh fixed scope and inherited checks

The resulting fixed project is app_motor_observe.ino, static FQBN
arduino:zephyr:unoq:link_mode=static, default startup, exact unchanged flags
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1. No dynamic/generic route.
RAW is state/analysis/P7_app_motor_observe_compile_raw; inputs_static.json and
native_static01 belong only there. ATTEMPT is app-motor-observe-static01; stage
owner build/stage/app-motor-observe-static01 has child app_motor_observe. Remote
owner is /home/arduino/sumox26_codex_build/app-motor-observe-static01, and source
path is /home/arduino/sumox26_codex_build/<source_sha256>/app_motor_observe.
Old owners are neither reused nor repinned. Partial/uncertain attempts remain
consumed. Canonical source reuse requires the original exact file/directory/hash
checks; no repair, overwrite or deletion of a mismatched source.

The future manifest schema is app-motor-observe-static-inputs-v1, otherwise the
unchanged D188 exact schema/source/boot/files contract. Its exact input inventory
is the projected caller's REQUIRED union all ordinary files under src,
bench/app_motor_observe and bench/motor_fault/src. REQUIRED contains the new
launcher/contract, original caller/remote/adapter, current tools/board_tool.py,
tools/app_build_commands.json, tools/app_build_pins.json and every inherited
HARD_PINS dependency. The old app_motor_fault bench is not a new source tree.
No manifest/projected-source self-hash cycle. Staged mapping omits .ino under
src/app, retains allowed project support, and copies only the two canonical
motor_fault.h/.cpp into the new sketch's src. All mapping, directory, collision,
entry/file/byte, clean-HEAD, source hash and closing checks remain unchanged.

The unmodified D188 contract's lifecycle, validated metadata and artifact packet,
original D185 methods/executor/wait, CLI/F166/installed pins, first-error and
independent closing requirements remain in force, with only the table's names
and owners changed. Retain -B and absent selected output/pycache prefix, exact
one properties query/compiler, jobs1,60s query/720s compile/5s reap,30000 UTF16
Windows command bound,128MiB local/1GiB target space gates, no upload argument,
raw receipts, exclusive claims, loader/TLS hashes, eight-file observation and
full structural/package validation. Check-only performs local read-only checks;
it cannot claim/stage/contact the board. Actual compile proves neither runtime,
live memory/WCET, physical acceptance, motor permission nor a human phase gate.

## Independent validation before native use

Freeze independent contract-derived tests before execution; do not read the new
launcher implementation to derive expectations. Verify all original/projected
pins and counts, mutated/nonbytes inputs, import/no-dispatch, invalid-CLI-before-
load, bootstrap missing/link/reparse/hardlink/drift/close errors, private roots,
unchanged global modules, required inventory and added hard pins, no self-pin,
derived aliases/path tables, and projected bundle/source_sha consistency.
Exercise the projected owner's inherited source mapping/staging/local checks,
metadata/artifact acceptance and rejection, command/provenance bounds and error
closure through controlled fixtures; reject old project/owner/schema packets.
Reuse unchanged public D188 fixture builders and assertions where appropriate,
with explicit new-name projection; never weaken historical tests or validators.
Check realistic Windows packet length with zero native dispatch. Preserve first
failures and review exact changes before a separately prepared actual scope.
