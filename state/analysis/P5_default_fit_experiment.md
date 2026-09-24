# Default app fit: isolated candidate 1

2026-09-24. **Both candidates compiled but failed conditional loader fit:
candidate1 deficit24 bytes; candidate2 deficit32 bytes.** Exactly two approved
actual native compilations ran, one per candidate. The optimization loop is
stopped for review. Production remains unchanged; neither candidate is adopted.
Production `src`, tools, tests, configuration, CMake and the frozen D135 pipeline
remain untouched. The candidate is three copied changed files under
`P5_default_fit_experiment_raw/candidate/src/core`; its exact diff is
[`candidate.patch`](P5_default_fit_experiment_raw/candidate.patch), with byte
identities in [`candidate_manifest.json`](P5_default_fit_experiment_raw/candidate_manifest.json).
Base production is `2d924f1f`; evidence HEAD at preparation is `8234afd7`, with
no intervening changes to these production files.

## Evidence and narrow hypothesis

D134's exact default app compiles but the retained pristine-pool model peaks
at262176 in262144 bytes: deficit32. Versus D128 its entire48-byte `.text` increase
is `startOpener`+12, Robot::step+4, runEscape+12, Escape::step+12 and
Escape::result+8. The required D134 availability-denial behavior is retained.

Existing checked DWARF shows Escape size208/alignment8, with episode at203,
pushed-out at204 and3 bytes of trailing padding. Thus one private bool placed
after pushed-out is expected to fit at205 without moving old members or enlarging
Escape/Robot/Runtime, but candidate target ABI must prove that expectation.
This is ordinary member storage, not an alias or union-lifetime change.

Corrected Thumb disassembly of the existing checked D128/D134 ELFs shows that
D134 runEscape adds a24-byte zeroing call while constructing EscapeSample,
with the associated literal entry; its +12 bytes are not all caused by the
extra helper argument. The new trailing push_eligible member is omitted in the
current aggregate initialization and receives its false default initializer.
Candidate1 spells that final false initializer explicitly. This preserves the
exact value while testing whether GCC avoids the implicit tail-clearing form.
Its actual code-size effect is unknown until the one authorized experiment.
The original GDB automatic ARM-mode decode was wrong and is retained as such;
only `*_thumb_disassembly.txt` is interpretable instruction evidence.

## Exact candidate changes

1. Add private `zero_window_active_` in Escape's existing trailing padding and
   two small inline helpers, `escapeActive` and `setEscapeActive`.
2. When EDGE_PUSH_THROUGH_MS is compile-time0, only that bool is read/written
   for active escape state. The episode field is unused for this authority.
3. When the window is positive, helpers read/write the existing Episode enum
   exactly as before. The additional bool remains unused; it is not a second
   positive-path authority. All DEFERRED/SPENT transitions and the existing
   mutually exclusive EpisodeData storage remain unchanged.
4. Replace the shared active checks, successful-row/fault activation and actual
   escape-exit clear with those helpers. Reset still assigns a default Escape.
   The initial positive-window row transition remains unchanged.
5. Explicitly initialize the existing final EscapeSample push field to false
   in Robot::runEscape. Positive builds still overwrite it with the same exact
   eligibility expression, including allow_push. No public structure field,
   signature, duration, admission, fault order, output or routing rule changes.

The candidate targets the20 bytes of enum-normalization growth in Escape and
the12-byte aggregate-clear growth in runEscape. It deliberately does not remove
the D134 check or assume the emitted32-byte reduction. Constructor/helper code
generation or alignment may change the result; a failed experiment is a valid
outcome and must remain recorded. No second candidate is authorized by this note.

## Review and validation boundary

Root reviewed this exact diff and authorized exactly one native default-app
compile using unchanged current
board_tool/app_build_policy and --jobs1, in isolated staging reconstructed from
the source commit plus this diff. It would not authorize production integration,
capacity/tuning/flag changes or upload/MCU activity.

Before adoption, require candidate Escape/Robot/Runtime ABI and old-member offset
comparison, exact ELF/loader account and function-size deltas. Run unchanged
default edge/Robot/locked safety regressions, positive-window20/100 edge and Robot
tests, and default/P4/P5 layout checks in isolated copied inputs. Positive-window
tests must verify the same Episode path; public oracle files stay untouched.
The root's currently running frozen D135 pipeline must finish before a second
host compiler is started. Native compilation and host tests do not establish
physical behavior, live RAM/stack or full800us WCET.

No cleanup was attempted; prior denied batches remain untouched. Retain the
commit/diff and three changed source files, not another full archived source
tree. Independent behavioral review and candidate host regressions remain pending.

## Retained setup failure and authorized attempt

The first fixture attempt stopped before any compiler invocation because the
isolated policy copy lacked its unchanged sibling `app_build_pins.json`.
Inspection also identified the required `app_build_commands.json`. Both are
now copied byte-for-byte from the verified working checkout. The pins file's
CRLF checkout differs from its LF Git blob only in line endings; both hashes
are recorded. No production policy or tool was repaired or altered.

The attempt-01 wrapper had failed to propagate `board_tool.main()`'s nonzero
return, so it incorrectly reported subprocess exit 0 before the outer collector
failed with exit 1 on the absent verified receipt. Original scripts, output,
receipt and a failure adjudication remain retained. The attempt-02 wrapper uses
`sys.exit(board_tool.main())`. Parent reconfirmed authorization because no actual
compiler had run in attempt 01. No second candidate or second actual compile is
authorized.

The same candidate is staged immutably as source
`9ba3caa4798c9531d8e3e3132a38c43e0aef2864782b5c4d1ee41246d58680fc`.
Actual compiler command is preserved in
`P5_default_fit_experiment_raw/remote_snapshot_ready_attempt02.json`, including
`arduino-cli compile --jobs 1 --json --fqbn arduino:zephyr:unoq`, exact inert
`-DMATCH=0 -DMOTORS_ALLOWED=0` C/C++ flags, fixed discovery flag, and unique build
receipt `cdbc469f97cb4de79cbdbea34513f316`. No upload or MCU action occurred.

## Actual result

The command `python -B state/analysis/P5_default_fit_experiment_raw/compile_target_attempt02.py`
ran the existing checked build pipeline once, from11:48:41 to11:52:36 UTC.
Wrapper, compiler and collector exits were0. The policy accepted the pinned
dependencies, exact commands, source identity and artifacts. No library was
added. Exact final ELF SHA-256 is
`c6d2a4da081b346784d75fc68cd306ead0fc133eb5c04e1ebcb9da29d23093a9`;
ZSK SHA-256 is
`3945698b1c5f27f1347707e15cdd46cc27ee466279c10a2044218fe9236faf0e`.
The packaged loader remains the checked `39d4a4fd…` image. One needed final ELF
is retained locally; debug ELF and ZSK identities are retained in the policy
receipt without another local copy.

| Measured/model quantity | D134 default | D135 candidate 1 | Delta |
|---|---:|---:|---:|
| Final ELF bytes |176116|176108|-8|
| Compiler-counted payload |257320|257312|-8|
| Compiler nominal remainder |4824|4832|+8|
| Conditional ordered loader peak |262176|262168|-8|
| Difference from262144-byte pool |−32|**−24**|+8|

`account_candidate.py` applies the unchanged retained `elf_review.py` model
(SHA-256 `1456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123`).
Every required persistent-flash peek alignment at0x08100010 passed. The61 used
relocation imports are all present with nonzero export addresses in the same
checked packaged loader, reusing the separately hashed D135 file-only export
receipt. Neither an unresolved import nor a library change explains this failure.

Actual copied payload is `.text`87696 + `.data`208 + `.rodata`2124 +
`.bss`167272 + `.exported_sym`8 + `.init_array`4. In pinned loader order,
after88 bytes of initial bookkeeping, allocation chunks are extension200,
section-map136, text87704, data216, rodata2136, BSS167280, export16 and
init-array8. This leaves4360 bytes before a4368-byte temporary global-symbol
allocation: **the first failing allocation is short8 bytes**. The final16-byte
export-copy allocation increases the hypothetical unreleased peak deficit to24.
These are conditional pristine-pool results; no object was actually loaded and
no live RAM, fragmentation, stack reserve, WCET or physical behavior was measured.

## Code-size and ABI findings

`Escape::step` shrank476→464 bytes and `Escape::result`172→164 bytes: the private
zero-window bool recovers the targeted20 bytes in those two functions. The
explicit final false initializer did **not** reduce `Robot::runEscape`: it remains
240 bytes. The D134 availability guard and its emitted size remain intact.

This build also incorporates committed D135, whose unchanged `Direct::step`
is220 bytes versus D134's200. Its source changed the terminal return to a local
Result to attach P5 evidence; that local-return form remains outside the P5
preprocessor guard. This is a source-supported explanation for the20-byte
growth, not an isolated recompilation proving causality. No `openers.cpp` edit
was included in this candidate. The named function extents total87610 bytes in
both final ELFs; remaining text extent is94→86 bytes. Thus the actual8-byte
section reduction is fully accounted without treating20-byte function savings
as20-byte net whole-image savings. `text_extent_comparison.json` retains the
unclaimed byte ranges; they are not assumed to be additional callable code.

File-only GDB queries against both policy-checked debug ELFs returned0. No target
connection or inferior was created. The new bool is at offset205, using one of
Escape's three trailing padding bytes. Every old Escape member and all44 sampled
old member offsets across Escape, Robot, Runtime and Transaction are unchanged;
full `ptype /o` output is retained as well.

| Native type | Size | Alignment | Compared with D134 |
|---|---:|---:|---|
| Escape |208|8|identical|
| EscapeSample |28|4|identical|
| Robot |2640|8|identical|
| RobotInput |192|8|identical|
| RobotResult |400|8|identical|
| Robot::Pending |88|8|identical|
| Robot::Tick |180|4|identical|
| Runtime |166376|8|identical|
| Transaction |162544|8|identical|
| TransactionReport |504|8|identical|

Runtime's final ELF symbol size independently matches its DWARF size. The two
stored RobotResult copies, RobotInput and recorder owners remain within these
unchanged aggregate sizes. This proves the default candidate layout only;
positive-window/P4/P5 candidate layouts and behavior have not been compiled or
executed. The positive-window source retains the original Episode authority,
but the required regression runs remain a prerequisite to any adoption.

## Source binding and remaining work

`finalize_evidence.py` verified106 materialized inputs,102 exact staged files,
the same staged hash before/after fixture repair, exactly three candidate source
differences, and134 unchanged root source/tool/bench files from the D135 working
manifest. It counted exactly one actual compiler command with `--jobs 1` and
exit0. Source commit plus exact changed-file diff and byte manifests are retained;
there is no duplicate full archived source tree.

The one approved experiment is complete and failed its fit objective. No second
candidate, compile, production integration, host test execution or cleanup was
performed. Retain the isolated build inputs for review/reproduction, the compact
failure/policy/model/DWARF receipts and one checked final ELF. Previously denied
cleanup paths remain untouched. The next decision belongs to the parent: review
these findings before authorizing any further isolated change. This report
does not close the default-app target-fit blocker or any project/physical gate.

## Candidate 2 reviewed proposal

Parent requested a second bounded proposal after preserving candidate1's failed
fit. Its exact full diff is `P5_default_fit_experiment_raw/candidate2.patch`
(SHA-256 `4d196e2c901b56bca4c9d71812d24e522278b990041d00401803887d7aee67b2`);
`candidate2_incremental.patch` contains only its two changes from candidate1.
The four changed source copies and their byte hashes are under `candidate2/`
and `candidate2_manifest.json`. Escape's two files are byte-identical to
candidate1; no ABI, configuration, capacity, build, library or tool change is
proposed. Root production remains unchanged.

1. In `Direct::step`, retain the exact current local Result/evidence/return
   sequence within `#if SUMOX_P5_ABORT_TIMING`; use the original
   `return terminal(exit_);` in `#else`. Before either branch, snapshot clear,
   selected exit and `active_=false` remain identical. The P5-enabled token
   sequence is unchanged. In the disabled profile `terminal` has no side
   effects and Result is plain value storage, so the returned semantic fields
   are identical. D134's checked function was200 bytes; D135's otherwise
   unchanged candidate1 function is220. Recovery of those20 bytes is plausible
   but not yet measured.
2. In `Robot::startOpener`, combine admission and dispatch in one explicit
   Mode switch. DIRECT calls Direct; WAIT calls Wait only when the existing
   constexpr availability query allows WAIT; ARC_R/L break before dispatch
   when the same query disallows the ARC pair, otherwise fall through to the
   common SIDESTEP/ARC Flank call. The default switch case calls nothing.
   Cancellation, `started=false`, fault handling, opener-active assignment,
   and selected OPENER state remain in their original order.

| Mode value | Existing admission | Proposed invocation |
|---|---|---|
|1,2 SIDESTEP|always available|one Flank start with unchanged arguments|
|3 DIRECT|always available|one Direct start with unchanged arguments|
|4,5 ARC|both use MODE_ARC_ENABLED|one Flank start only if existing constexpr query is true|
|6 WAIT|MODE_WAIT_ENABLED|one Wait start only if existing constexpr query is true|
|all other underlying uint8 values|unavailable|none; started stays false|

This partition covers all256 underlying values and all four availability
settings without removing D134's no-dispatch-on-rejection requirement. Direct
public Flank/Wait entry validation remains untouched. A start that returns false
still produces SCRIPT_START, inactive opener and the same downstream inhibition;
there is no substitute strategy or additional invocation. ARC_R availability
also controls ARC_L because the canonical query defines both with the same
approved flag. This is a source equivalence argument, not executed coverage.

Checked Thumb disassembly in `*_candidate2_basis.txt` shows candidate1/D134's
124-byte startOpener performs a1..6 range admission and then DIRECT/WAIT
dispatch comparisons. D128's112-byte dispatch lacked the new required
admission. The proposed explicit switch expresses both requirements together
and may let GCC select a smaller branch structure. Its emitted size is unknown:
a jump table or additional branches could eliminate the expected benefit.
No byte saving, successful fit or margin is claimed before compilation. The
retained24-byte deficit is not rounded down or hidden behind nominal compiler
RAM, and no padding, optimization flag or source-order churn is proposed.

Parent reviewed the exact incremental diff and256-mode partition, and approved
one isolated default M0 native build. Preserve its failure if any and repeat
exact loader/ABI/source checks. Behavioral acceptance
still requires unchanged default/P4/P5, positive-window and all availability
regressions after the current frozen host pipeline releases its compiler slot.
The immutable staged candidate2 source is
`d77ccbc74d658ac296c0f1be37ee38e611b7e5462dac041a363f1a3e2451fb05`,
receipt `959c0c6ff79d40a59810b66ec54650e3`. Its one actual native compilation
started11:57:36 UTC using unchanged default M0 flags and --jobs1. No production
integration, host compiler, upload/reset or new physical/gate claim follows.
If candidate2 also fails fit, parent directs this optimization loop to stop
after preserving both results; no third compile is authorized.

## Candidate 2 terminal result and stop

`python -B state/analysis/P5_default_fit_experiment_raw/compile_candidate2.py`
completed with compiler, wrapper and collection exit0. Policy receipt
`959c0c6ff79d40a59810b66ec54650e3` accepted exact pinned dependencies and
unchanged default M0 flags. Final ELF is176148 bytes, SHA-256
`b0cc2375e87c3f886a13c347ff448e5f98c8e62fea73c8414fdec6d78768fed8`.
The checked package/debug/loader hashes remain in `app_candidate2/receipt/verified.json`;
only the final needed ELF is copied locally.

| Quantity | Candidate1 | Candidate2 | Change |
|---|---:|---:|---:|
| Compiler payload |257312|257320|+8|
| Conditional ordered peak |262168|262176|+8|
| Pool deficit |24|**32**|8 worse|
| Direct::step bytes |220|200|−20|
| Robot::startOpener bytes |124|144|+20|

The direct-return hypothesis succeeded in its narrow function-size measurement;
the switch hypothesis did not. Named function sizes changed only in those two
functions relative to candidate1, while total `.text` rose87696→87704. No ABI,
BSS, data, rodata, library, symbol-count or capacity reduction occurred. The
compiler's nominal4824-byte remainder still omits required loader overhead.

With the same88-byte initial bookkeeping and metadata/region order,4352 bytes
remain before the4368-byte global-symbol allocation, which is the first
failure and is short16 bytes. The subsequent16-byte export copy gives the full
32-byte hypothetical peak deficit. Flash peek premises pass; all61 used imports
resolve in the unchanged checked loader. This is not a measured load or free-RAM
result, and no upload or MCU action was performed.

Candidate2's checked DWARF reproduces every type size/alignment in the table
above and all44 old member offsets. Escape's added bool remains at205 in the
same208-byte object, Robot remains2640 and Runtime166376; the final Runtime
ELF symbol agrees. Candidate2 source verification binds106 materialized inputs,
102 staged files, the exact four-file proposal, and134 unchanged root production
inputs. Its one actual `--jobs1` compiler is separately logged from candidate1.

**Stop disposition:** retain both unique failed-fit ELFs, both source identities,
proposal diffs, policy results, ordered accounts and ABI receipts. No third
candidate or native compile, production integration or candidate host compiler
was run. Parent may review the findings, but neither candidate clears the target
blocker and no physical/project gate is claimed. The next authorized work is the
separate D136 offline analyzer; it does not continue this native optimization loop.
