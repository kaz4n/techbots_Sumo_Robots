# D204 file-only ABI observation of constant motor metadata

26 September 2026. This is a proposed fresh ABI and complete-symbol-table
observation of D203 source
4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2.
Preparation does not accept the D203 artifacts: the independent review of the
actual compile evidence must close before native ABI admission. The saved
compile result reports COMPILE_CHECKED, one query, one compiler, 238 transports,
no first error and eight PASS final checks, at reviewed HEAD
dbeec127ba651b6a4346f70aaf5b78bc79718ce0. Those are saved compile claims pending
that separate review, not ABI, runtime or timing observations.

The profile remains app_motor_observe.ino, arduino:zephyr:unoq:link_mode=static,
default startup, -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1.
The expected serial is 2629958581 and boot is
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. Actual ABI addresses, sizes, sections,
types and offsets must be freshly obtained from these exact files. Even a
matching prior coordinate does not substitute for a current observation.

## Exact implementation boundary

Only the new executable subject
state/analysis/P7_motor_const_compile_raw/inspect_static_abi.py is proposed.
Do not create it until D204 is adopted and implementation ownership is assigned.
Derive it from the complete D199 wrapper
state/analysis/P7_motor_settle_compile_raw/inspect_static_abi.py:
16106 bytes, SHA256
0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea.
Preserve every byte except the ordered metadata substitutions below, including
line endings, bootstrap, summary logic, error strings and query construction.
No source execution is needed to derive the bytes or their identities.

The inherited semantic contract is
state/analysis/P7_motor_settle_abi_contract.md, 22405 bytes, SHA256
dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956.
Its ABI requirements remain binding with the target metadata changed here.
Its later entry-observation subsection is not authorization for a D204 entry
reader. This contract supersedes only its D198 artifact/source/owner/contract
identities and D199 status/private-module identity for this new wrapper.

Define C as the lowercase hexadecimal SHA256 of this complete final contract
file. Seal this file first, then calculate C and the derived wrapper identity
in abi_derivation01.json. The contract contains no final wrapper hash and the
derivation receipt is not a runtime input, avoiding a self-hash cycle. The
implementation receipt must independently reproduce that derivation.

Apply these 19 substitutions in order. Each occurrence count is mandatory at
its step; reject any mismatch. Literals are exact UTF-8 bytes without Markdown
backticks. The C placeholder denotes its 64 ASCII hash bytes, not the letter C.

| Step | Old literal | New literal | Count |
|---:|---|---|---:|
| 1 | D199 | D204 | 2 |
| 2 | P7_motor_settle_compile_raw | P7_motor_const_compile_raw | 2 |
| 3 | tools/compile_motor_settle_probe.py | tools/compile_motor_const.py | 2 |
| 4 | P7_motor_settle_abi_contract.md | P7_motor_const_abi_contract.md | 1 |
| 5 | dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956 | C | 1 |
| 6 | 7570 | 7557 | 1 |
| 7 | 13432 | 13559 | 1 |
| 8 | 1608 | 1605 | 1 |
| 9 | 9648 | 9645 | 1 |
| 10 | b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62 | 957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247 | 2 |
| 11 | aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 | 1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95 | 2 |
| 12 | 9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5 | 323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7 | 2 |
| 13 | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 | fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd | 2 |
| 14 | app-motor-settle-abi-static01 | app-motor-const-abi-static01 | 1 |
| 15 | app-motor-settle-static01 | app-motor-const-static01 | 1 |
| 16 | 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da | 4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2 | 1 |
| 17 | 17061 | 17051 | 1 |
| 18 | 67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6 | 938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6 | 1 |
| 19 | _sumox_d199_abi02_original | _sumox_d204_abi02_original | 1 |

These are 26 literal occurrences. Apart from the private ModuleType name in
load_reader, every function body remains byte-identical. No new function,
class, import, branch, exception handler, query or I/O operation is introduced.
Retain the SETTLE diagnostic names and error text; they still describe the
same report and their spelling is not part of this metadata change.

## Original-first projection and runtime input binding

The unchanged original-first chain reads and verifies ABI02 before privately
executing it, composes its projector before this wrapper's projector, then
delegates to its unchanged load_reader. The input to the new projector remains
16937 bytes / b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981.
The same 14 ordered projection steps and their occurrence checks remain;
only their destination metadata changes through the recipe above. The output
must be 17051 bytes /
938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6.
Type, length, digest, occurrence and final-identity checks are unchanged.
Never write a private projection over any historical source.

The five ORIGINALS inputs, all checked before private source execution, are:

| Input relative to repository | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py | 8219 | a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421 |
| tools/compile_motor_const.py | 7557 | 957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247 |
| state/analysis/P7_motor_const_compile_raw/inputs_static.json | 13559 | 1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95 |
| state/analysis/P7_motor_const_compile_raw/native_static01/result.json | 1605 | 323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7 |
| state/analysis/P7_motor_const_compile_raw/native_static01/artifacts.json | 9645 | fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd |

The sixth pre-execution input is this contract with digest C. The new SELF is
bound through the clean reviewed HEAD. Retain all inherited original pins and
the consumed ABI01 failure provenance required by ABI02. Extend HARD_PINS by
copy exactly as before; no original-first dependency is removed or weakened.
The current manifest binds 129 files, including motor_port_unoq.cpp
19906 bytes / fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b.
Current source/admission/package checks use the actual projected D203 compiler
owner, without compiling. Old D198 receipts cannot substitute for these files.

The saved D203 packet currently identifies these eight artifacts under
/home/arduino/sumox26_codex_build/app-motor-const-static01. Their current
admission and complete closing rechecks remain required even after D203 review.

| Relative file | Bytes | SHA256 |
|---|---:|---|
| build/app_motor_observe.ino.elf | 172600 | 390b69c1f35dd85a56462e562561e16b4659c0e31aa44d99aaf5b87e4ccd7e13 |
| build/app_motor_observe.ino_debug.elf | 1838360 | b3520cacc96ccd3d410b011dd6b4e65761c503b940fa13f1fddfe59db3666066 |
| build/app_motor_observe.ino_temp.elf | 1838360 | b3520cacc96ccd3d410b011dd6b4e65761c503b940fa13f1fddfe59db3666066 |
| build/app_motor_observe.ino.bin | 95352 | 76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3 |
| build/app_motor_observe.ino.bin-zsk.bin | 95368 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 |
| artifacts/app_motor_observe.ino.bin-zsk.bin | 95368 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 |
| build/app_motor_observe.ino.elf-zsk.bin | 172600 | 5416c121deb8ff3cb0a27a3d8d150981fe945c5ab818fe3da788744f4980db7f |
| build/app_motor_observe.ino.map | 449499 | 23416a129a832bbbc4738814a7a1326a62f5e5f9e879d925ab7620e3ab1b88a3 |

The saved validator packet records .bss NOBITS at 536951136, size 171680,
alignment 8, with initialized zero subrange [536951136, 537121800),
170664 bytes. Those packet bounds constrain the fresh ABI observations. The
larger section does not substitute for the initialized interval. This contract
does not assign any Runner/report/function address or any capture window.

## Unchanged ABI meaning and file-only lifecycle

Preserve the complete D199 bootstrap: plain ancestry and single-link local
files, reparse refusal, O_NOFOLLOW/O_NONBLOCK, descriptor-before-read admission,
size and digest bounds, same-API opening/closing stamps, exact Windows 0111
executable-path adjustment and cross-API ctime exception, close behavior and
primary-error preservation. Do not import installed-compiler hardlink semantics
or relax local source checks. Import remains passive; CLI is exactly
--check-only|--execute --reviewed-head <40 lowercase hex>, with Python -B.

Retain exactly four file children: readelf --version, gdb --version,
readelf -hSWs on the current raw ELF, and guarded GDB on its debug ELF. The
readelf output is the complete current symbol table. Neither candidateRate
nor candidatePeriod is a required emitted symbol in this ABI task; D202 may
inline or eliminate helpers. Their presence, absence and any instruction
consequences require a separate evidence-derived entry scope later. Never
broaden symbol selectors, insert old addresses, or synthesize missing answers.

The existing 23 subjects plus terminal bool, all 11 Runner OFFSET queries and
all 223 GDB expressions remain exact. Preserve no-autoload/no-function-call
flags and the current report_.polls unsigned-int layout/alignment guard.
The 62 extra expressions still obtain all eleven field offset/width pairs
and nine enum values. Preserve the exact observed requirements: Sample 12/4,
Report 28/4, Reason 1/1, ordered markers and all D199 field/enum expectations.
Expected values do not replace observed answers. Missing debug information,
stderr, missing/duplicate/reordered/malformed tags or mismatches fail visibly.
Do not add queries for unused inline validity constants; their source-only
semantics remain separate from ABI observations.

Retain original raw command encodings. Normalize only private copies, delegate
once to the saved summary on independent deep copies, preserve every field,
and add only the existing settle_probe key. The unique complete
_ZN6motors12_GLOBAL__N_119settle_probe_reportE symbol must be freshly observed
as LOCAL OBJECT DEFAULT in the same numeric .bss section as Runner, size 28,
alignment 4, wholly inside checked bss_zero and nonoverlapping Runner. Retain
all decimal/hex size parsing and duplicate-row rejection. No accessor symbol
is required. Summary status remains STATIC_ABI_OBSERVED; transport scope
changes only to D204_STATIC_FILE_ONLY_ABI.

Use the fresh exclusive local owner
state/analysis/P7_motor_const_compile_raw/native_abi_static01 and require the
remote scope /home/arduino/sumox26_codex_build/app-motor-const-abi-static01 to
be absent. The inherited reader checks but does not create that remote scope.
The checked build owner is app-motor-const-static01, never an old settle,
observe or fault owner. Preserve all prior consumed local/remote owners,
results, failures and attempted commands; do not delete, repair or reuse them.
Any partial or failed new native owner is consumed, with its first error kept.

Keep readelf SHA c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e,
GDB SHA 8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778,
the installed loader/TLS, ADB, identity and all helper pins unchanged. Preserve
clean reviewed HEAD/source checks, 60s child/5s reap/1MiB stream limits,
400s transport, 30000 UTF-16 command units, 128MiB local free-space minimum,
the complete 13 remote closing checks and independent local closure.
Preserve first-error precedence, evidence-write errors and full raw receipts.

Check-only remains local and read-only, with no owner claim or board dispatch.
One separately admitted execute may invoke only those four file children.
Save raw result.json before parsing, then abi.json and local_result.json.
No compile, upload, reset, MCU memory read, inferior attach/run, credential,
cleanup, pin/config change or motor operation is included in D204.

## Independent oracle, review and evidence boundary

Freeze an independently authored oracle before its author reads the new
implementation and before anyone executes it. Derive fixture metadata from
this contract and pinned historical oracle sources, not from observed new
behavior. The current complete D199 oracle is
tests/tooling/test_motor_settle_abi.py, 30983 bytes, SHA256
96763b42d61b80654503f4093d32ac3b174ab2152fdfb795b3801304e4e2b252.
Preserve its 66 methods and all assertions by explicitly counted private
fixture projections. Its established platform coverage is 66 Linux passes
and 64 Windows passes with two Linux-only skips. These counts describe the
historical baseline, not results of the new suite. Retain the corrected
duplicate-Runner and explicit report-row fixtures and their first-failure
history. Do not replace assertions or production lifecycle paths with success
mocks, change supported skip rules, or claim historical-only runs test D204.

Add independent checks for the exact 19-step wrapper derivative and unchanged
function bodies, current six-input binding before private execution, the
current source/manifest/artifact identities, and rejection of stale D199
source/compile/artifact/owner substitutions. Assert distinct new SELF/output/
scope/build owner and rejection of old consumed scopes; retain old fault and
observe negative cases rather than globally relabeling them. Preserve exact
14-step projected identity, four commands, queries, parser failures, untouched
caller packets and every closing/error assertion. Synthetic addresses remain
unrelated to actual saved D199 addresses. Record all selected names, fixture
substitutions/counts/digests and original pins in the freeze.

Run Linux then Windows serially under separate exclusive evidence owners and
record opening/closing pins, stdout/stderr, skips, first errors and cleanup.
Do not run board tools or compilers during host checks. After D203 actual
review, new source/oracle/host review and fixed scope/admission review close,
commit inputs to a clean reviewed HEAD, run local check-only, then at most one
native ABI attempt. A separate reviewer must close the actual raw evidence,
fresh symbol/layout answers, local closure and all source/tool/artifact pins.

Only those accepted actual observations can seed a separately adopted entry
contract or later inhibited capture. Fresh file evidence does not establish
runtime report contents, SETTLE repair, timing benefit, atomic publication,
WCET, physical wiring/sensor acceptance, motor permission or a human phase
gate. Last flashed D201 source remains unchanged by this preparation.
