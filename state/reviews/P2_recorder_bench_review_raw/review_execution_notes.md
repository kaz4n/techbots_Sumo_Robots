# Reviewer command corrections

The first local startup-excerpt extractor split the disassembly into an empty
leading element and raised `IndexError` before writing its output. The corrected
extractor ignores empty elements and produced `target_startup_excerpts.txt`.
This was a reviewer helper error, not a firmware or test failure.

An attempted read of the target receipt in `P2_dump_raw` raced the coordinator's
documented relocation to `P2_recorder_bench_raw`. The unchanged receipt was then
read at its final path and its SHA-256 is recorded in `source_target_check.json`.

The coordinator and reviewer initially mistook the GNU nm display value for ELF
`st_value`. `final_symbols.json` established the actual readelf section-relative
value, and `layout_review.json` preserves the correction. No parser correction
was made or required. The source-only approval's pending-layout wording is a
historical provisional note, superseded by the final report/capture approval.
