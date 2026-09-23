# D109 QTR raw bench validation

2026-09-24 Asia/Dubai. Contract/interfaces/config f786fa5; checked build policy
524ea6b. Implementation first freeze remains unchanged: Runner54b0a21b,
headerca134b2b, Native775b8f4d, sketch24c64a25. Full SHA256 values and original
bytes are in P2_qtr_raw_raw/worker/first_source_freeze.json and first_sources.
Status: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED in default and Immediate profiles;
separate scoped source/host/policy/target review PASS, no BLOCKER or MAJOR.

The named P2 B2 bench owns one existing Reader and stores the first configured
128 complete raw frames without overwrite. Cooperative polls do one native
operation; partial captures survive faults/stop. Closing-clock rejection cannot
publish a tentative record. Native cleanup is bounded and attempted at most once,
with separate evidence from the primary fault. All pad grants default false;
there is no motor, transport, controller or unrelated peripheral owner.

## Independent tests

The separate author derived expectations from the adopted public contract/API
without reading implementation bodies. Author and implementer wrote in parallel;
executable tests froze before their first run. Both contexts are the same model
and reused earlier work; this is not cross-model review. Final runtime expectations
are unchanged from the first frozen tests. See author/freeze.json, validation.md,
run receipts and fixture_amendment1.json under P2_qtr_raw_raw.

| Profile | Actual result |
|---|---|
| Pure Runner, normal and ASan/UBSan | 32 cases /20,131 assertions each PASS |
| Real new Native binding and default sketch, substituted Reader | 2/39 each PASS |
| Capacity1, normal and sanitizer | 27/1,630 each PASS |
| Capacity0, normal and sanitizer | 4/104 each PASS |
| MATCH/motor forbidden combinations | Three expected compile refusals |
| Original registry through unchanged D106 wrapper | All18 assertions execute; accepted defaults and three original negative profiles behave as required |
| Additional wrong QTR capacity129 | Rejected by the original value assertion |
| Checked build routing | Root7 new +100 existing methods PASS; separate reviewer107 PASS |

The first test compilation failed because this doctest version lacks the five
STATIC_REQUIRE[_FALSE] macros. The coordinator reviewed all five and approved
equivalent C++17 static_assert expressions, preserving every predicate. Original
failure and frozen bytes remain. Cases changed d93a7b56 to80fec60e; harness
438ac88d remained unchanged. No production fix or weakened runtime assertion was
needed. The unlocked registry adds QTR_BENCH_FRAMES=128. The adjacent dictionary
opening line also changed CRLF to LF; no other token or assertion changed.
The reviewer caught the author's original byte-identical claim as inaccurate
by that one carriage-return byte. Preserve the original receipt with its explicit
correction; this formatting delta did not change any expected value or check.

Ordinary counters and capture boundaries execute in tests. Saturation paths are
source-reviewed, not billions of simulated polls or private-state injection.
Function review finds42 functions, maximum27 lines. Mock clocks/native substitutes
test accounting/delegation only, not actual sensor timing or GPIO behavior.

## Target evidence and scope

All board commands compile or read completed files on board Linux through ADB.
No upload/reset/MCU command occurred. MCU remains the frozen D1042bd817c4 image.

Default checked receipt234198a7663b4c6dadb135cfdbe524e8 binds exact96-file source
5c468e20a00597e18100fe80add771aa97965cee40f3281ffcc807d56a90d7cd.
P2_qtr_raw_target_collect.py verified every source/artifact hash and collected
three ELFs, package, offline ABI/sections/symbols/relocations/disassembly and
installed-tool identities. Exact frozen source and receipts are in
P2_qtr_raw_raw/target_sources_5c468e20 and target_5c468e20_bench-default_checked.
Immediate receipt4b7b3c53a16e4b52be8bf760fb62df3e binds the identical source;
its completed artifacts are in target_5c468e20_bench-immediate_checked. Both
collectors returned zero with complete exact file identities and offline tools.

The first Immediate invocation mistakenly used unsupported --immediate and
failed argument parsing before transport (exit2). It remains recorded as failure;
the correct --startup immediate invocation is separate. No tool was changed to
accept the erroneous option. Command receipts are P2_app_build_raw/d109_*.

Compiler success alone does not establish startup/import safety or loader fit;
the separate reviewer must qualify the exact artifacts. Default grants are
false, upload remains refused, and this software increment has no readout tool.
Physical black/white/brown captures, pad ownership, actual charge/frame bounds,
clock calibration, full-app800us WCET, PINMAP and human phase gates remain pending.

## Exact target review

Separate offline reviews pass both checked profiles, sharing final ELF SHA256
e65ffd462ffa558980d36804193b44deeddf2386b6e9792d1182239d78567806.
Each final ELF is24,628 bytes with31,929-byte compiler payload. Conditional
ordered loader peak is32,920 bytes of262,144, leaving229,224-byte span and
229,220-byte largest payload. This is a pristine-pool model, not loaded RAM.
Target Runner is23,568 bytes; Native280;128 fixed180-byte snapshots occupy23,040.
Actual startup has passive constructors, disabled setup and empty thread bounds;
excluded peripheral/controller/transport owners are absent. Retained thread
helper has empty bounds and exception allocator is an abort stub. Pin references
do not imply pin operations. Review artifacts bind every retained ELF form.

The reviewer also privately executes the full host CTest2/2 and all D109 profiles.
Its first registry-only check omitted the unchanged runtime-contract fixture;
that harness error was preserved and corrected by copying the exact fixture,
without changing source/tests. The resulting registry check passes. Source and
evidence review is separate from implementation, with reused same-model context.
Final bound verdict is state/reviews/P2_qtr_raw_review_raw/final_review.json,
SHA25659da19719804309c5da3ebf5324cd84fd63d7744e77fccfc0167f834c303f75b.
MINOR R1 is disposed by the explicit newline correction above and the author's
registry_amendment_correction.json; original inaccurate receipt is retained.
