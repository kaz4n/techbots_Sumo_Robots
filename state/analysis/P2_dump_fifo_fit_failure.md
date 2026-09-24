Current disposition: the first-image deficit is CLOSED conditionally by D117 repair1 in ed5a9dea. The corrected default image has only8 bytes modeled span; actual loading remains unmeasured. Original failure and repair evidence follow unchanged.

# D117 first default application exceeds modeled loader capacity

2026-09-24. OPEN target acceptance blocker; no MCU run or upload occurred.

The first frozen four-file implementation compiled successfully, but the exact
default ELF `0ac42e6c` requires262152 bytes in the existing pinned pristine262144
byte loader model. This is an8-byte deficit, not a measured runtime heap result.
Compiler-reported payload257300 bytes alone did not reveal it. The model includes
ordered extension/section bookkeeping, region copying and symbol metadata.

Exact source is `5e30199705228299231025e1048c90566feaf625516763d1f1eae312d561b0ab`;
checked default receipt is `1e0119b9053c433e8ad511aa294704c5`. Original sources,
three ELFs, ZSK, objects, identities and new debug ABI query are under
`P2_dump_fifo_raw/target_5e301997_bench-default`. The reviewer calculation is
`P2_dump_fifo_raw/reviewer/first_app_fit.json`. The selected native owner is
208 bytes in initialized data; its old BSS placement/204-byte size cannot be
assumed. Debug/temp model results are not deployment alternatives.

The initial MATCH Immediate image also compiled and was collected under the same
source with receipt `9b0b6a8234534bcb92edada334da30d8`; its independent audit is
pending. No conclusion from MATCH replaces default acceptance. The recorder
image will be built after the coordinated bounded repair.

Next: one minimal semantics-preserving size repair within the adopted UART scope,
then new exact builds and ordered allocation review. Keep all capacities, frame
bytes, deadlines, checks, grants and established tests. The first image/failure
stays preserved. D117 host execution still awaits independent test freeze.

## Repair1 conditional disposition - 2026-09-24T03:47:36.209335+04:00

The original first-image failure above is preserved. Replacing the three-state
stack table with equivalent bounded-index expressions changes only beginFifo;
source/machine-code review and frozen independent tests pass. Corrected default
sourcee820c0e1/ELF8379f152 has ordered peak262136, remaining span8/largest4 in the
same pristine262144-byte model. MATCH Immediate peak260504 and recorder220744
also fit. This closes the exact default allocation deficit conditionally; it is
not an actual load/free-RAM/stack result. Debug/temp artifacts do not substitute
for the final image. All host tests used repaired native sourcefdd3df0b, with no
oracle amendment. See P2_dump_fifo_validation.md and the separate final review.
No upload/reset/MCU operation occurred.
