# D105 loader-capacity finding

2026-09-23 Asia/Dubai. OPEN implementation blocker, not a physical measurement.

The initial full-app default build compiled successfully at source
`4c3487f4682b2b9f000aab12a9fe8abb818212814190fe4b6236c832dc9fe9ee`,
receipt `e95073506b474d0b9024b4cc462eb98e`. Its 258,396-byte compiler
payload fits the nominal 262,144-byte pool. However, the pinned loader model
requires **263,176 bytes**, exceeding that pool by **1,032 bytes**. The compiler
summary is insufficient for deployment acceptance. No D105 image was uploaded.

Exact 89-file staged source, three ELF files, package, objects and successful
receipt are preserved in `P2_calibration_delivery_raw/target_4c3487f4_bench-default`
and `target_sources_4c3487f4`. `initial_memory.json` contains region and metadata
charges; `initial_symbol_delta.json` compares target symbols with D103.

The largest added text is the existing formatter (368 bytes), issue predicate
(324), bounded write (296), ordering (232), service (216), preparation (192).
Runtime grows 72 bytes. These symbol sizes are descriptive; aliases must not be
summed as independent allocations. Exact copied-region/metadata charges decide fit.

One bounded refactor was validated: move the new private state to the end
of Runtime, and share the existing inhibited-IDLE predicate without changing
receipt/setup precedence. Root-owned target receipt `d105_target_refactor_default`
measured source c05916c6 / receipt57a85761. Compiler payload258324 and complete
peak263112 recover64 bytes of peak cost, leaving968 bytes deficient. Exact raw
artifacts and refactor_memory.json preserve the remaining BLOCKER. All recorder
capacities and safety checks are preserved. The separate D106 contract now
selects byte-preserving deduplication of four identical installed pin tables.

Separately, initial Runtime failure cleanup cancelled output before halting the
Gate. Root identified this and a separate reviewer reproduced six failed
assertions. It is corrected to halt first; unchanged reviewer regressions are
being run. This is distinct from the capacity finding.

Do not accept D105 as target-ready until complete ordered loader fit, independent
review and unchanged meaningful host/sanitizer tests pass. Further optimization
requires a measured bounded change. Current MCU remains the already verified,
frozen D104 inert probe; these board operations only compile/read Linux files.

2026-09-23 D106 closure: exactd72bff70 three-profile independent review PASS; default/Immediate peak261688 and MATCH260056 fit262144. D105-R2 closed only for these replacements. Read P2_pin_table_validation.md; original failing sources remain unchanged.
