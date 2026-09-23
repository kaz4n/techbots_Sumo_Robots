# D107 independent author validation

Command: `python -m unittest tests.tooling.test_opp_view -v` from the repository
root. The Windows launcher invokes WSL/Linux g++ with isolated opaque source
copies and temporary binaries under /dev/shm. No shared build, board operation,
network call or production implementation body read was used.

The suite was frozen before first implementation execution. Its expectations
come from D107's public contract, including the adopted pre-test clarifications,
and public owner/header interfaces. No author test, assertion, expected result,
fixture or compiler warning was changed after freeze.

Final run2: PASS, exit 0. Exact outcomes:

| Profile | Executed cases | Assertions | Result |
| --- | ---: | ---: | --- |
| Pure Runner, normal | 24 | 40087 | PASS |
| Pure Runner, ASan/UBSan | 24 | 40087 | PASS |
| Actual Native binding/default sketch, normal | 2 | 51 | PASS |
| Actual Native binding/default sketch, ASan/UBSan | 2 | 51 | PASS |
| Six isolated invalid-config sanitizer profiles | 1 each | 29 each | PASS |
| All-active-high and all-active-low mask profiles, sanitizer | 1 each | 16002 each | PASS |
| Forbidden MATCH/MOTORS_ALLOWED combinations | 3 compilations | expected static-assert refusal | PASS |

All 12 executable variants passed. Run2 records 30 commands with zero unexpected
failures and three expected compile refusals. Native and alternate-polarity
variants deliberately select their scoped cases; their reported skip counts are
filter exclusions, while the complete 24-case Runner suite ran in both normal
and sanitizer profiles. Allocation counters remained zero during guarded work.

Run1 against the second source freeze passed every executed behavioral case but
failed to compile the TICK_US=0 profile: both constant division sites generated
division-by-zero warnings under unchanged -Werror. The author reported this
production compile finding and preserved run1.json/txt, run1_summary.json and
all original commands. The implementation worker corrected the division guards.
A separate reviewer identified an interim fix's passive-phase regression and
owns its separate verification; that interim source was not run by the author. Run2
uses the final third source freeze. No warning suppression or test weakening
was used to close the original failure.

SHA-256 identities:

| File | Hash |
| --- | --- |
| Frozen opp_view_cases.cc | f4e62547d1f3cb9e511ae0f5768ce0f42f698a40b0aa77c2f3dd63fcb623348c |
| Frozen test_opp_view.py | d1d45a5f152becf3c7ba067022dd442cac4fbdafc03b7764386402156ce0f3c0 |
| Frozen contract | e4e3dcbe77ee8a8a24a1ef12862a274c558e66ae3418df6d4acef5c3af5f9d9e |
| Final tested opp_view.cpp | 1be9bc511d0b1af5d1a95f664f20e93e0779c0cd617596cd272fe615ea1c55e3 |
| Tested opp_view.h | ba57008a94e65e9b2a21ffef8ec4a6d6d0086cb2f3a5aca9e9add49916c5b11a |
| Tested opp_view_native.cpp | 010dee72ba08cab784e4919a4b8e587606bdd51cbae4d4d79145cd71261c8f2f |
| Tested opp_view_native.h | 4e646e7c5aae3abc7f3813243661490d47585b30e947cb5aa9b72ac922519114 |
| Tested opp_view.ino | 42ac2b38b9ce5749aad674bbd82466f0de1f27f39d2cce4fc05dc9c375ad6960 |

See freeze.json, run2.json/txt, run2_summary.json, timestamped command/config
receipts and opaque_source_copy manifests for exact source/call outcomes.
Coverage and independence limits are in coverage.md. Actual HAL native suites,
target compile/source/ELF/import/startup checks, memory capacity and physical
measurements remain separate coordinator/reviewer evidence. Nothing here grants
electrical ownership, optical confirmation, hardware acceptance or a phase gate.
