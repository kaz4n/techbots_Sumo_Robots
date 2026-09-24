# Original positive20 M1 failure adjudication

Receipt: analysis/P4_push_through_raw/positive20.txt, B11/B9.4 test at test_push_through.cc:210; fixture assertion push_through_fixture.h:137 expected TRACK at entered+1250000us. M0 passed; initial M1 deferral revocation assertions preceding the helper passed.

This is a fixture assumption mismatch. Target10 supplies FC+SL to isolate the initial new-white/no-contact test from B5 phantom filtering. After a real FL escape, B11 selects RIGHT (away from the recent left edge). Unchanged Reflank implementation fsm.cpp:409-435 consumes inner SL immediately during SWING, can enter TURN_IN and leave to perception in the same bounded call with front present. The helper then supplies enough later observations to regain ATTACK before its fixed final TRACK expectation. Public fsm.h Reflank comments and B11 explicitly require inner-sensor priority.

Do not weaken the TRACK or later limiter assertions and do not change production. Clear the extra SL input, allowing actual OPP_CLEAR_MS observations before the later timer-only reflank helper. Setting the target to FC-only before the existing freshContactAfterEscape sequence provides that clearance. Root/test author informed; original failed receipt remains intact. This adjudication used source/public contract analysis; no new execution was performed by the reviewer.
