# P0 frozen-RAM capture scoped review, 2026-09-22

Coordinator records p1_next_task_audit's reused separate read-only review. No
source edit or hardware command by reviewer; not newly fresh/cross-model/gate.
No readout BLOCKER found. Exact reviewed files:
- tools/p0_capture.py:9d57569f6153a63a094bab0b71105d2955b59469c73687d7aade31cb3fda97fd
- tools/p0_mem_read.cfg:89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339

Config uses only the observed internal SWD lines and a MEM-AP target; no reset
GPIO, CPU target, flash driver or STM32 event hooks. Exact absolute swj-dp.tcl
helper was inspected and pinned to aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a.
Initialization affects debug-port infrastructure; it is not electrically passive.

Only dump_image memory reads are generated. Known loader/OpenOCD/helper/config/
final ELF/bin identities are checked, then flashed loader/sketch bytes compared
before interpreting RAM. At most4 unique nodes,16 memory reads,32 commands,
aligned/range-checked SRAM, exact normalized ET_REL BSS symbol sizes/ranges,
nonoverlap, list-tail/unique-sketch checks and a shared120-second attach deadline.
Incomplete, changed or inconsistent snapshots fail nonzero with captured evidence.

Independent17 histogram tests passed exit0. Root separately reproduced17/17.
Percentile rank59400 and overflow censorship are tested from the diagnostic
contract; no implementation cpp was read by test author. Import has no hardware
side effect. Firmware/established locked tests/config were unchanged.

Evidence limitation: samples-first is read after flash/list operations. Its value
alone cannot prove capture completed before the first SWD access. Preserve actual
upload-to-attach timestamps and report elapsed waiting, debug activity and cache
coherence limits honestly. Do not equate this bare installed-loop measurement
with full control-tick WCET, cold-boot timing or a phase gate.
