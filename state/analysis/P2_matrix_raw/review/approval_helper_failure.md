# Reviewer helper failure retained

The first direct invocation of approve_inert_sources.py failed before writing
approval: FileNotFoundError for repository src/adc_capture.h. The helper had
treated every staged src/ path as shared production code, but old inert benches
also carry private src/adc_capture.h and related files. The independent staging
snapshot already used the correct mapping. Changed only this reviewer helper
to distinguish shared src/core, src/hal and src/config.h from bench-local files.
No implementation, test, target or registry changed. This note reconstructs the
failure from the captured tool result rather than claiming a raw subprocess log.
