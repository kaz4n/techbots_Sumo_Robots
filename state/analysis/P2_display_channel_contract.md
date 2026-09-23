# D108 correction of front sensor presentation

2026-09-23 Asia/Dubai; selected under D051/D075. This resolves OPP-VIEW-1
without changing sensor identity, wiring, polarity, fusion or motor behavior.

B0/D076 define opponent bits0..6 as FL15,FC,FR15,SL,SR,RL,RR.
The geometric SENSOR_VIEW must place these at (2,1),(4,1),(6,1),(0,3),
(8,3),(2,5),(6,5), respectively, with coordinates (column,row), zero based.
The existing D088 first two positions were swapped. Supersede that single
geometric mapping clause; retain every other D088 pixel, validity, availability,
fault, battery, state-selection and native matrix ownership rule.

displaySample continues to pass result.opponent_mask unchanged. Correct only
the first two coordinates in ui_display.cpp. No remapping of input/output masks,
native pins, polarity, tunables or core source is permitted for this task.
The D107 index strip remains correct and unchanged.

Tests: explicitly amend only the two corresponding expected positions in the
existing unlocked test_ui_display.cpp oracle, citing this decision. Preserve
its exhaustive128 masks,16 line masks,four availability combinations and every
assertion. Add independent literal single-channel cases across actual public
displaySample -> render, including the unknown group. Derive expected pixels
from this document/public headers, before implementation edits; no locked test
change. Run the full normal/sanitizer host suite and independent source review.
Compile current app default/MATCH without upload and verify source/ELF mapping
and conditional memory remains within the previously audited pool.

Coordinator owns this contract, decision, production one-line fix and evidence.
Independent author owns only the unlocked oracle amendment and additive tests;
reviewer owns review evidence only. This is software correctness, not optical
orientation, electrical qualification, a human gate or a new upload permission.
