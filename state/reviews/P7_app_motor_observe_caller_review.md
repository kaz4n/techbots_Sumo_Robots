# D195 observer caller/actions and selected ABI fields

26 September 2026, Asia/Dubai. **PASS for prepared caller/actions and the selected
field transcription; no open material finding.** Reviewer `/root/fresh_review`
is a separate same-model reused context. Review used local source/contract/
oracle/receipt reads, hashes and static/data comparisons. The reviewer did not
import subjects, run tests or contact the board. Only this review was written.

| Input | Bytes | SHA-256 |
|---|---:|---|
| P7_app_motor_observe_caller_contract.md | 8618 | `03b61d0c152fccd69775c458023ffe0a48d307a0a1056d2ea36d7fe2adf81a34` |
| P7_app_motor_observe_run_raw/run.py | 24944 | `95cc5cb695c8d9bbee85a2105aca46d7c371c1a3bec3c5e3a36ea8fb4dbd1471` |
| P7_app_motor_observe_run_raw/actions.py | 12515 | `6a730069e2511306459f5c3443976a84351b155fd04660a094606cfd98f2829f` |
| test_app_motor_observe_run.py | 10975 | `7af304d06b85de0f835856ecbd241d957c193b7d252c2849eea474e6043fbb9c` |
| test_app_motor_observe_actions.py | 13390 | `103493975bccdcab094b412a5ba26cf125a6f294a9b5efac167660f6fda8a563` |

The original run02 `0adabfc3...` and actions_run02 `4eeb19f1...` remain exact.
The diff contains the prescribed observer metadata/owners/pins, successful
ABI02 provenance predicates, projected D193 source selection and strict wait
validation. No transport or lifecycle rewrite is introduced. Thirteen InertRun
methods, including ownership/staging, dispatch, counters and run sequencing,
are AST-identical to the original. Other changed methods retain their original
structure with the specified metadata/evidence changes.

Independently hashed all13 hard pins and128 D193 manifest files: current bytes
match. The new caller privately loads checked compile_app_motor_observe.py
`70e1f016...` and calls only load_caller(root=ROOT). Its three originals remain
length/hash checked before private loading; no launcher main/build/claim path
is called. Independently reconstructing the launcher projection gives the
29904-byte caller `830299e5...`. Inspected source_names/source_mapping select
the observer bench, current src files and unchanged motor_fault Trace sources,
with duplicate/missing-name checks and the original sorted source digest.
The root/base fixture seam is consistent. It does not use the unprojected fault
CompileDiagnostic for observer source.

Preparation retains12 exact provenance paths; scope retains11 exact input keys
without self-hashing. Actual compile/source/boot/first-error and artifact success
predicates remain. ABI02 must now be STATIC_ABI_OBSERVED with no local first
error; the failed predecessor/offline interpretation cannot satisfy this path.
Raw ABI02 remains pinned provenance, and successful current entry evidence is
required. Reviews and actual evidence hashes are supplied by the later immutable
preparation/scope, not caller-selected native options. This review does not yet
approve a particular final scope file or clean HEAD.

Canonical fixed upload/capture binding comparison precedes claim. Old prefix
rewrites consistently yield the new schemas, source/build paths, adapter and
result owners. The stage is exclusively claimed before its single checked
adapter push; durable intent precedes staging dispatch. Native success still
requires13 transports across the same seven labels and exact per-label counts.
Upload195s/capture630s/prerequisite60s outer limits,180s/600s remote budgets,
unchanged local/source/ADB checks, closure and first-failure handling remain.
Check-only reaches local admission without staging, an owner or board calls.

Actions preserves the11-key envelope and requires a returned report before
success validation. Inline sources and the staged adapter retain exact checks;
65536-byte reply,196608-byte payload and30000-UTF16 command bounds remain.
The sole new successful-analysis key is pre_sample_wait. It requires exact
requested_seconds/before/after keys, an int30 excluding bool, finite nonnegative
numeric times excluding bool, start <= before <= after <= sample_wait.before,
and at least30 seconds elapsed. The unchanged two-second wait must still finish
by capture end. All26 reads/727152 bytes,12 snapshots, flash brackets, canonical
report hash and no-error conditions remain. No FROZEN/epoch/coherence assertion
is inferred from waiting. Invalid or unattributed outer results retain their
partial inner report and fail; durable fallback cannot promote an inner success.

## Independent first host evidence

The oracles were frozen before their authors read/imported the new subjects.
Static count-checked fixture projection retains all20 caller methods/104
assertion calls and13 actions methods/65 assertion calls. Metadata,128-input
source inventory, actual ABI02 shape and valid30-second fixtures are the scoped
changes. Actions privately injects the existing Linux pwd module, avoiding the
previous orphan-module fixture defect; no broad sys.modules rollback is used.

Five caller supplements cover the actual projected source mapping, exact scope/
owners/provenance, successful current receipts, wrong status/error/source/boot,
failed ABI predecessor and old manifest rejection before mapping/transport.
Eleven actions supplements cover exact wait shape/type/finite/order/bounds,
inclusive valid boundaries, preserved sample separation, rejection of extra
terminal/coherence claims, outer-error/unattributed failure and one-shot closing
after invalid wait. Original framing, descriptor and lifecycle fixtures are
retained. No material fixture defect was found.

| First receipt in P7_app_motor_observe_run_raw | Actual result | SHA-256 |
|---|---|---|
| test_caller_windows01.json | 5 PASS,20 Linux-only skips; exit0 | `65fb418d3cfc476d3ae214119368b4f160543e4956b78a49fb88255c4c44be64` |
| test_caller_wsl01.json | 25 PASS,no skips; exit0,137.782s unittest | `c59f609d7e60109267c5ff3c49bb6670606808a01e00db78aff30c419b6c4f46` |
| test_actions_windows01.json | 19 PASS,5 Linux-only skips; exit0 | `c91d994759ed6c60001dbeabc6e9ff82c648d28c6e6a0ddeb09d27b398deba4c` |
| test_actions_linux01.json | 24 PASS,no skips; exit0 | `a53c12b265e8630d090be8a337c9e0ae23045064520f506d8c588df2d1f8530b` |

All use Python -I -B; WSL caller uses TMPDIR=/dev/shm and the actions Linux
bootstrap fixtures use /dev/shm. Independent freezes are `9c8a3bb0...` caller
and `bec460b5...` actions; first-run closures are `d44b3f68...` and `caa43505...`.
The reviewer independently hashed all28 caller frozen inputs plus128 manifest
pins and every action receipt's15 before/after pins: unchanged. No repair/retry
occurred. Combined with separately reviewed remote tests, D195 totals91 Linux
passes and48 Windows passes with43 explicit Linux-only skips.

## Current selected field map

Independently compared current ABI02 result `a5e67635...` against preserved
old result `684670c5...` and old field map `2da7da21...`. All14 complete selected
GDB ptype blocks match after the namespace rename, except the single Report
change: its last_step_returned trailing hole shrinks7 to3 bytes and uint32_t
polls occupies offset12/size4. All14 comparison block hashes agree. The reviewer
also checked all104 selected direct member offsets, observed widths, primitive/
composite kinds and containing type sizes against the current blocks. The map
retains all103 old selected fields and adds polls; no host-layout inference was
used. Report remains1168 bytes, with Snapshot still at offset16.

The reviewed map is abi_static02_decode_fields.json,10447 bytes, SHA-256
`b96b6a3e7349baff471af3bb115c13ab2c1de07c6949a419ed3e9ed1afe16939`;
comparison is abi_static02_field_comparison.json,3257 bytes, SHA-256
`612aebbd783ec4ea1df73d729fe813ad8635bb09685879b796109f1f3d87faf5`.
Its TRANSCRIBED status is preserved; this review records the independent check.
These are selected layout facts, not SRAM values or a complete object decoder.

This PASS supports separate review of final preparation/scope and clean-HEAD
admission for one inhibited observer attempt. It does not establish a native
upload/capture, atomic SRAM coherence, complete callback history, runtime
acceptance, physical safety, RAM/WCET qualification, motor permission or a human
phase gate. The actual D196 cleanup closure is recorded in its separate review.
