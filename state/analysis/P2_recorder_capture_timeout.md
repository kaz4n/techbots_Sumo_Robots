# D091 capture attempt1 timeout

2026-09-23 17:21 +04. First memory operation: read loader263680B at0x08000000.
OpenOCD identified MEM-AP successfully, then reached30s command ceiling with94208B
partial data. Reader terminated it, returnedFAILED/exit1, and interpreted no RAM.
Evidence: P2_recorder_bench_raw/runtime_run1/capture.json and00-loader.bin.
This is a capture-throughput failure, not a claimed failed or passed recorder run.

Bounded fix attempt1: subdivide identity into65536B blocks, each under the existing
30s command ceiling; whole image equality remains required before any RAM access.
No deadline/read/byte guard or established assertion is relaxed; new tests are
additive. All47planned actualreads fit the original48 bound for the single sketch.
More extensions may fail closed at the unchanged bound. Original P0 helper stays
unchanged. Review new helper hash before retrying readback; do not reset/reupload.

Other verification corrections retained: old tooling49tests passed, two imports
failed due missing tests/tooling PYTHONPATH; the remaining7passed with correctpath.
The suspected ELFoffset defect was retracted before code edits: GNU nm includes
sectionVMA; readelf st_value0x28928 was already correct. Six additive tests protect
that interpretation. A fresh reviewer independently reproduced it.

## Fix disposition

Final helperfd1932ac was separately reviewed and its51additive/current capture
methods passed. Retry runtime_retry1 succeeded with47reads,934892B,51commands
and281.632730s; longest command19.673451s, below30s. All original limits held.
No firmware change/reset/reupload. Both captured pools and terminal diagnostics
match; independent retained-row CRC verified. Attempt1 failure remains archived.
