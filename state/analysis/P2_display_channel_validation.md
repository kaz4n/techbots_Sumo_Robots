# D108 front display identity correction

Status: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED; separate scoped review PASS.

2026-09-24 Asia/Dubai. Contract/decision9ff7405 resolves OPP-VIEW-1. The only
production edit swaps the first two geometric positions in ui_display.cpp:
bit0 FL15 now maps to column2,row1; bit1 FC to column4,row1. The remaining
channels, raw/result masks, core, pins, polarity and native ownership are unchanged.
Renderer SHA2569e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535.

The independent author read the public contract/headers, not renderer bodies.
Before implementation, they froze the authorized two-position correction in the
unlocked exhaustive oracle and added three literal projection tests. Original
15 cases and all47 CHECK/10 CHECK_FALSE/3 CAPTURE uses are preserved. No locked
test changed; the original D088 mapping text remains with an explicit correction.

| Actual validation | Result |
|---|---|
| Frozen old renderer, normal and ASan/UBSan | 18 cases,16 pass/2 fail;4,104 pixel failures solely offsets15/17 |
| Corrected renderer, same targeted suites | 18 cases/1,524,757 assertions each PASS |
| Full normal host | 1,446 main cases/45,736,428 assertions;187 active-Gate cases/4,536,952;CTest2/2 PASS |
| Full ASan/UBSan host | Same complete counts,CTest2/2 PASS; no skips or stderr |
| Separate review's private normal host | CTest2/2 PASS |

Original red source/results, unchanged green test hashes, all commands and exact
isolated source manifests are under P2_display_channel_raw/author. Reviewer
context is separate same-model, reused from prior bounded reviews; it is not
cross-model or human gate review. No hardware measurement is inferred.

## Exact app target evidence

Source618d3a96a33f2a74c5141ba8770620302135f398a04a43611af36b4535aed363:
91 frozen files,79 objects. Default receipt91229be5b4db46319f8ef2837c8868be;
MATCH/Immediate47128726fdb14c20acea7e194fcacefb. Both commands include
--compile-only; MATCH is a build configuration and was never uploaded.

Raw staged sources, installed-tool hashes, preflight/compiler receipts, all three
ELFs per profile and packages are under P2_display_channel_raw/target_618d3a96_*.
Separate ELF/diff/conditional-loader findings are in
state/reviews/P2_display_channel_review.md and its raw directory. Default ELF
765b1b027f8b5081363cf2ace66efab712a1cb3aa8140564458899c5bd8631ed differs
from D106 only in two read-only coordinate bytes (offset608:4->2;616:2->4).
Default compiler payload256880/conditional peak261688/span456 remain unchanged.
Compiler's5264-byte free estimate is not the ordered loader model's margin.

MATCH's final ELF also differs from its D106 predecessor by exactly the same
two read-only coordinate bytes. Final stripped instructions, sections, symbols
and relocations are unchanged; all three ELF forms preserve function bytes and
the intended table change (debug metadata identities are separately recorded).
MATCH payload255296/conditional peak260056/span2088 are unchanged. Independent
review closes OPP-VIEW-1 within software scope. Frozen sources/profile packages
are bound in final_review.json. Default's456-byte remaining span is still small
and must be checked for future actual app changes.

MCU stays frozen exact D1042bd817c4; no new upload/reset/run or sensor grant.
Physical optical orientation, hardware qualification, actual full-app loadedRAM/
stack/WCET and all human phase gates remain pending.
