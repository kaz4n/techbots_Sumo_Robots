# D194 ABI02 supplementary source and host review

26 September 2026, Asia/Dubai. **PASS for prepared source / host scope; no open
material finding.** Reviewer `/root/fresh_review` is a separate same-model reused
context, not a fresh whole-project reviewer. Review used local source, contract,
fixture and receipt reads, hashes, and static AST/data comparisons. No subject
import, host test, native tool or device action was executed by the reviewer.
Only this review document was written.

## Evidence and fixed scope

Attempt01 remains FAILED and consumed. Its actual result records four reaped
file children with exit 0 and no timeout, but GDB 16.2 emitted 86 stderr bytes
for `alignof(((app_motor_observe::Runner*)0)->report_.polls)`. All 13 remote
closing checks passed, and the single-transport local closure passed. The
tagged polls block contains SIZE 4, no ALIGN value, LAYOUT `type = unsigned int`,
and OFFSET 168572. These partial observations are not a successful ABI.

The supplementary contract binds that observed member type to the unchanged
D193 source/debug/ELF. It requires a fresh numeric alignment observation and a
new owner; it does not supply alignment 4 or reinterpret the failed attempt.

| Input | Bytes | SHA-256 |
|---|---:|---|
| Supplementary contract | 6703 | `772615cda21858c3ca32eea6a541d97ec79985054cdbdad5ea029c225a5d673c` |
| New inspect_static_abi02.py | 8219 | `a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421` |
| Original inspect_static_abi.py | 9318 | `497f756e4eab440d659a4d26ef38ec8d92abdd9f92a5938d1da04705745f42d5` |
| Attempt01 result.json | 893217 | `e83afc5f10cec2ed72f88d6567f6f13e5809518e1b89f3d5988d988b297e78f5` |
| Attempt01 local_result.json | 336 | `589b78d1ff3cacbe96869f2f2c43d3fc546a9ff2cbfc26c34d1ad3a3d9b9ec01` |
| Independent 21-method oracle | 24242 | `9e50373e9c0f9d26ecd1e6f4097aa90bf7f346fa42476183b50ed2d0c1feddc3` |

The previous source, contracts, tests, failures and owners are preserved.
The fixed D193 artifact build remains `app-motor-observe-static01/build`;
new observation ownership is local `native_abi_static02` and remote absence
scope `app-motor-observe-abi-static02`. No new compile or artifact is implied.

## Source findings

Independent source-segment comparison confirms that `require`, `_stamp`,
`_plain_chain`, `_read_handle` and `pinned` are exact copies of the repaired
original functions. Thus the first bootstrap retains ordinary full ancestry,
single-link regular files, reparse rejection, pre-read descriptor checks, the
exact Windows executable-mode exception, full same-API stamps, bounded reads,
digest checks and primary-error preservation. The original wrapper, both failed
receipts and supplementary contract are verified before any private execution;
the three fixed lengths are also checked.

The original definitions execute in a fresh private ModuleType with the original
absolute __file__, never __main__ or sys.modules. Composition saves the original
projection, calls it first, then applies the supplementary projection. The
returned HARD_PINS retain every inherited pin and add all four new inputs.
SELF binds the new wrapper under the inherited reviewed-HEAD checks.

Without importing or executing either subject, the reviewer statically applied
both literal replacement tables to the preserved original reader. Every
occurrence count matched. The first projection is 16833 bytes / SHA-256
`f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14`;
the final projection is 16937 bytes / SHA-256
`b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981`.
Their complete byte diff changes only SELF, local/remote observation owners,
two scope-label occurrences, and the polls ALIGN command. D193 build OWNER,
SIZE/member LAYOUT/OFFSET, other tags/windows, and the entire lifecycle remain
unchanged. Only the polls ALIGN command becomes `p/d alignof(unsigned int)`.

The summary adapter requires an exact four-dict command packet and strict
Base64/UTF8 GDB stdout, then exactly one contiguous current polls block:
`SUMOX_LAYOUT report_.polls`, `type = unsigned int`, `SUMOX_SIZE bool`.
LF and CRLF are accepted; another type, duplicates, intervening text or missing
markers fail before delegation. It calls the saved normalized summary once
with the original arguments, does not rewrite raw evidence/layout, and returns
its fields plus explicit type/provenance metadata. The inherited numeric tags,
ET_EXEC/BSS/window checks and readelf normalization remain in force. Neither
strict empty stderr nor any transport/closure limit is weakened.

CLI validation rejects wrong types/order/count/head and missing Python -B before
input reads, then delegates once. No target/type/owner override or copied
transport framework was introduced. No material source finding remains.

## Oracle and first actual host runs

The independent oracle freeze declares derivation from contract772615cd and
unchanged public historical fixtures, without reading/importing/executing the
new implementation before freezing. Freeze SHA-256 is
`3d51c5c17b4591878948cbd4e488141d0c1bc2744db1da3aedf0da291c65ec4d`.
The reviewer read the complete oracle and the borrowed prepare/execute fixture
mechanics. The historical oracle remains exactly `b43b384a...`; no old assertion
or source was edited. Fixtures block subprocess/socket endpoints, use small
temporary files (Linux /dev/shm), and never launch a board or file tool.

Coverage includes passive import/invalid CLI, exact bootstrap bodies, all four
provenance failures before private execution, original-first projection,
complete inherited pins/private loading, and exactly one query argument change.
It exercises strict current-type rejection and raw preservation, numeric
alignments 2/4/8 to detect a hardcoded value, inherited numeric/BSS guards,
actual prepared command composition under mocked local admission/space,
new/old ownership separation, synthetic successful and failed execute flows,
raw-before-summary retention, independent closure and primary-error preservation.
The execution fixtures use controlled transport and ABI packets; they are not
native measurements. No material fixture/coverage defect was found for this
bounded supplementary change.

| Receipt in P7_app_motor_observe_abi_raw | Result | SHA-256 |
|---|---|---|
| abi02_first_windows01.json | 21 PASS, no skips, exit 0; 0.517 s | `e8f624ac5db9026479a7e9e47535897a7a55530182a08fadfa43fdd544270002` |
| abi02_first_linux01.json | 21 PASS, no skips, exit 0; 2.705 s | `a44b68d366456c9ce12f0c4aef249b99b178afd26d810aa1c6647c425e85d374` |

Both first runs use Python -B and verbose unittest discovery. There was no
failure-driven change to this new oracle/source. Earlier 44-method and
14-method results remain historical evidence for their unchanged inputs;
the two receipts above specifically cover the new 21-method supplement.

## Closure and limits

The reviewer independently hashed all 142 files in
`abi02_coordinator_freeze01.json`, SHA-256
`a1cfe5f24ba627813f833e1f201749468d3fa73a825f16921f4513348cfd2095`.
All match. Relative to the prior 136-pin freeze, all 136 remain unchanged, none
were removed, and exactly six entries were added: new wrapper, contract,
oracle, independent freeze, and the two preserved failed-attempt receipts.
Local owner01 exists; owner02 is absent.

This PASS supports a separately admitted execution after a clean reviewed HEAD
and fresh live admission. ABI02 check-only, actual file-tool syntax, observed
alignment, complete target layout and actual closing receipts remain pending.
No host result grants firmware execution, motor permission, physical acceptance,
fault resolution, live RAM/WCET qualification or any human phase gate.
