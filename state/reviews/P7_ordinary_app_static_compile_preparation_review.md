# D208 ordinary-app static compile preparation review

Date: 26 September 2026, Asia/Dubai. Reviewer: independent review-only agent.
Disposition: PASS for the data-only proposal and its bounded implementation
specification. No open material finding. Formal coordinator adoption,
implementation, independent oracle freeze, source/host review and fresh native
admission remain future prerequisites; this review authorizes no execution.

This review read the complete proposal, companion data, pinned predecessor
APIs and relevant accepted reviews. Verification used only local file reads,
hashes, JSON/AST data parsing and independent in-memory byte/data calculations.
No project module/helper was imported or called, no new subject or oracle was
read, and no tests, compiler, transport, board, staging or owner operation ran.
Only this new review file was written; existing reviews and evidence remain
unchanged.

## Reviewed identities

| Input | Bytes | SHA-256 |
|---|---:|---|
| `state/analysis/P7_ordinary_app_static_compile_contract.md` | 21756 | `06cd96f1c84fb50368050344853e4f5dfe0540a2d9a95b43def853b402b87f5d` |
| `state/analysis/P7_ordinary_app_static_compile_raw/compile_derivation01.json` | 66454 | `09f0d107c0336f1831bdecc58dc53b11dabb9c15df30b5b3513ed1bc3cb99c91` |
| `tools/compile_motor_const.py` | 7557 | `957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247` |
| `tools/compile_app_motor_fault.py` | 29802 | `cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a` |
| `tools/app_motor_fault_static_policy.py` | 8262 | `3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270` |
| `tools/app_motor_fault_compile_remote.py` | 6891 | `1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2` |
| `tools/match_deploy.py` | 26266 | `3acacad6e95aff1012e9d0d1f8ef60905c026ebe865569fdb71384abd607d2a9` |
| Accepted D207 actual review | 14825 | `b562488423fce03712e0156deba21f52fddc826f096c70dcb1736d78aee71937` |

All 150 companion input records independently match their actual lengths and
SHA-256 hashes. The accepted D207 review is prerequisite diagnostic evidence;
neither its source digest, artifact addresses nor runtime result is promoted
to ordinary-app evidence.

## Profile and source-set reconstruction

The selected operation is one compile-only ordinary `src/app/app.ino` image,
FQBN `arduino:zephyr:unoq:link_mode=static`, default startup, and exactly
`-DMATCH=0 -DMOTORS_ALLOWED=0` for both language properties. The current config
has all ten listed profile macro defaults zero, including
`SUMOX_MOTOR_FAULT_PROBE`. Independently parsed declarations match all seventeen
listed `APP_GRANT_*` constants at zero. The pinned `app.ino` still constructs
the ordinary Runtime/native-source/motor-port/dump-port pipeline, calls
`configuredSetupGrants()` in setup and Runtime step in loop. The configured
grant mapping is unchanged. Compile mode creates no grant or motor permission.

I independently enumerated the current `src` file set and transcribed the
pinned helper's mapping as data. The result equals every companion destination
record, including source path, size and digest:

- 105 source files totaling 764405 bytes, with no bench input;
- 104 mapped destinations totaling 764405 bytes;
- only `src/app/.gitkeep` excluded from staging, retained in source inventory;
- sorted destination/NUL/raw-byte digest
  `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.

All current source entries are plain directories or regular files without
symlink/reparse entries. No current sketch-local reserved entry is present.
This is local data verification, not an invocation of `app_source_hash`,
`board.stage`, `board.source_hash` or admission. Those actual cross-checks remain
mandatory in the future controlled fixtures and actual preparation/admission.

Static reconstruction of the original caller's REQUIRED/HARD_PINS union, with
the specified metadata substitutions and pin extension, yields exactly the
twenty proposed runtime names. The twelve inherited hard pins, the D203
original-caller and original-remote additions, and the single match_deploy pin
give fifteen hard-pinned inputs. The exact required set union the 105 source
names is 125 prospective manifest names. Future admission must compare that
complete set, not merely its cardinality. The future launcher is intentionally
not given an invented current input identity.

## Ordinary mapping and refusal semantics

The proposed mapping matches the pinned `match_deploy.app_source_hash` and
ordinary `board_tool.stage('app', attempt=...)` source-selection rules:
config/core/hal retain paths, sketch-local `src` support maps under `src`,
other app C/C++ support maps under `src/app`, and other eligible top-level app
files retain basenames. Unmapped nested non-source files remain covered by the
source inventory/manifest even though they do not enter staging. Core/hal
`.gitkeep` files remain mapped, consistent with the real helper and stage.

The proposal expressly requires lexical refusal of sketch-local `config.h`,
`core`, `hal` and `app` entries, including empty directories and linked entries.
A destination-collision check alone cannot satisfy that condition: an empty
reserved directory supplies no mapped file. The future mapper must preserve
that distinction while computing file bodies from checked snapshots. The
existing source traversal's plain ancestry/type checks remain independently
required for both mapped and unmapped sources.

The required app file, forbidden `sketch.yaml`/`sketch.yml`/`sketch.json`, portable
relative-path validation, exact and case-insensitive destination collisions,
512-file and 4 MiB bounds are explicit. Existing 1024-entry, 512-source-file,
per-file and aggregate source bounds are also retained. Hash ordering is the
helper's `sorted(mapped, key=Path)`, followed by UTF-8 destination, NUL and exact
bytes. A raw string sort silently substituted for that ordering is not admitted.
The existing stage directory equality check also remains: unexpected empty
directories or extra copied entries cannot be accepted from a digest alone.

The three comparisons are distinct obligations: snapshot mapper versus
manifest; real pinned `app_source_hash(self.root)` versus both on each
admission; and actual staged-file hashes plus real `board.source_hash(stage)`
versus the reviewed mapping/digest. Re-admission must recompute the helper
result, not reuse a prior cached result or substitute the expected digest.
Checked match_deploy bytes are privately loaded through the existing
`module_from` seam. Its inspected top level contains imports, constants and
function definitions only; no operational entrypoint is run at loading.
The permitted public helper entrypoint is `app_source_hash`; its ordinary
internal read helpers do not expand this permission to deployment operations.

## Exact projection boundary

Independent byte reconstruction verifies every replacement count and every
intermediate byte-length/hash for all seventeen metadata steps:

| Projection | Steps | Result bytes | SHA-256 |
|---|---:|---:|---|
| Caller metadata intermediate | 9 | 29819 | `402fea3fdb0f2b1af99dff3f4a80afebf63529ae05466958b957ac1bd6038275` |
| Adapter | 3 | 8219 | `d1a78ad713d0550ed52805a6751640823a31ce4e96edafc3c058a7587c5e4863` |
| Remote | 5 | 6845 | `71c189ea3c354b7ccb969b35ae3f1a92a517380735059d00ff4c735b45cf4389` |

All six caller old method spans match the intermediate's line boundaries,
complete bytes, hashes and argument ASTs. They are `source_names`,
`source_mapping`, `__init__`, `admission`, `source_admission` and `stage`.
The proposal precisely limits their semantic changes: src-only enumeration;
ordinary mapping; app stage child; private real-helper comparison and app
canonical child; app-only canonical-owner child list; and ordinary app staging.
All unrelated checks inside those methods, every other caller byte, and all
signatures remain required. The intermediate alone is explicitly incomplete
and cannot be treated as a working future caller.

All eleven protected launcher spans independently match their recorded bytes,
hashes and argument ASTs. Their descriptor bootstrap, bounded original reads,
plain ancestry, one-link Python-source requirements, platform stamp handling,
primary error precedence, CLI validation and dispatch stay exact. The allowed
project_caller transformation helper must verify each old span/count and the
final body; permitted load_caller changes are confined to the private name and
explicit original/match_deploy pin extension. The historical `__file__`, private
module behavior, original self.code snapshots and no global module registration
remain required. No ABI executable-mode exception is imported.

I inspected the adapter's reference and artifact code. Changing project to
`app.ino` and flags to the original two inhibited flags makes its project/flag
reference replacements identities; it does not remove the 84-property,
24-project-occurrence and 5-flag-occurrence checks. All seven artifact aliases
become identity names while retaining exact byte objects, full legacy
validation, copied result maps and exported-flat/build-package equality.
The remote projection couples its adapter digest to the derived `d1a78ad7`
body. Loader/TLS/layout/package validators, descriptor checks, error precedence
and independent finalization remain outside the permitted change.

## Future identity and oracle barrier

The companion correctly leaves final caller and launcher identities null at
proposal time. They require real construction of the six changes. Those nulls
are documentation of absent implementation, not allowable runtime verification
values. Before any subject/test or native execution, all three originals and
all three final projections must have concrete enforced byte-length/SHA-256
checks. There must be no skipped `_verify`, wildcard, None comparison bypass or
unchecked projection. A separate immutable implementation receipt must seal
the actual caller/launcher identities; source review must independently match
that receipt and the allowed byte/span boundary.

The independent oracle author may receive the sealed identity metadata while
the new bodies remain unread. Behavioral fixtures must derive from this
contract and pinned predecessors, and freeze before implementation inspection,
hashing by the independent author, imports or execution. Receipt metadata does
not replace independent expectations or authorize the author to read the body
before freeze.

The baseline coverage obligations are coherent: retain applicable assertions
from the 69-method D203 caller and 38-method remote/adapter coverage, explicitly
transpose the metadata-only boundary assertion to metadata plus six spans, and
cover all 33 D187 adapter methods with overlap reported. The 27 D185 methods
and seven error methods supply applicable ordinary mapping/staging semantics;
their historical dynamic/MATCH profile is not admitted. Former ordinary-profile
negative fixtures require explicit stale diagnostic/probe replacements while
preserving rejection assertions. Historical fault/observe/settle negatives and
new const-owner/source/artifact negatives remain necessary. No future total
test count is guessed, and no old test is edited or silently omitted.

Required new checks address the material change: real helper agreement on
synthetic trees and re-admission, helper-pin/digest refusal, lexical reserved
entries, missing app/overrides, collisions, source inventory drift, identity
aliases through real validators, ownership and complete failures/closure.
Source, host and oracle reviews must still judge the eventual concrete cases;
this preparation PASS does not claim those tests exist or pass.

## Lifecycle and disposition

The fresh attempt is `ordinary-app-static01`, with local stage child `app`,
local output `native_static01` and its exact isolated pycache child, and remote
commands/build/artifacts owner beneath the new attempt. Current proposal-time
absence of the new launcher, local stage and local output was independently
confirmed. Remote owner absence, current boot/resources and use-time installed
identities are explicitly unobserved for D208. Canonical source reuse requires
the exact single app child and full source/directory equality; no repair or
owner reuse is permitted after failure/uncertainty.

The preserved lifecycle retains clean committed reviewed HEAD, exact pinned
manifest/scope, check-only without ownership/staging/native action, then at
most one properties query with 60-second bound and one jobs=1 compiler with
720-second bound and five-second reap. It retains 30000 UTF-16 command units,
128 MiB local/1 GiB board free minima, existing output/resource/conflict/UID
bounds, prerequisite checks, all eight artifact files, source and installed
loader/TLS closure and independent finalization evidence. Transport counts
must follow actual mapped pushes rather than a historical diagnostic total.
Compiler zero alone remains insufficient for COMPILE_CHECKED.

The proposal is suitable for formal adoption and bounded implementation with
these stated conditions intact. It supplies no ordinary compiled artifact,
memory fit, live RAM/stack, loading, recorder behavior, timing/WCET, motor-run
permission, physical acceptance or human phase gate. Later ABI/entry evidence
must come from the actual new ordinary ELF, and runtime/deployment needs its
own fresh scope.

Final preparation review. STOPPED WRITES after recording external length/hash.
