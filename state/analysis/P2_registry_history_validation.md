# Historical config-registry proof repair

Root reproduced the D110 registry method failure after the legitimate D111
addition: it removed only its own old literal from the live registry, then
compared that file with its pre-D110 snapshot. The later five approved literals
therefore caused a byte mismatch before the live value checks could run.
D111's newly established harness had the same future-coupling pattern.

The two-line repair changes only the input to each historical delta proof to
its already-recorded immutable adoption after-image. Original assertions,
before-images, literals, actual live run_registry calls, all18 legacy checks
and deliberately wrong live-value controls stay byte-for-byte unchanged.
This distinguishes historical evidence from current configuration validation;
it does not accept a newly generated baseline or bypass a failing value check.
No firmware, C++ oracle or locked test changed.

Original red and green argv/status/output are in P2_app_build_raw/
registry_history_{vbat_red,green}.{json,txt}. Both targeted methods pass after
the repair. Root retained original harness bytes and exact old/new hashes in
P2_registry_history_raw/change.json. Separate read-only review/private execution PASS in
reviews/P2_registry_history_review.md and raw/reviewer/run_1790197999487220910.json. Full native/C++/target reruns are unnecessary for two registry input
paths; their executed proof remains tied to the earlier recorded harnesses.
