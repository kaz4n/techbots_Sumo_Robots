# D133: keep historical upload tests tied to their approved source

Adopted under D051 during P4 regression maintenance, 2026-09-24. The296-method
D132 regression retained80 failed subcases: eight in five P0 methods, and72 in
19 D118 methods. The pre-D132 tool reproduces the P0 failures; D118 fails in
its source-fixture guard before tool use. Production source approval correctly
refuses changed bytes. Do not change approval keys, run records or assertions.

Repair only the historical fixture source provider:

- P0 positive source fixtures use immutable commit
  `1b1d77dcc3fc9ecfe5f6cbc0e47cb2dac9e4f461`, for `src/`,
  `bench/p0_matrix/` and `bench/p0_timing/`. Verify reconstructed staged contents
  against the saved approved file maps and aggregate hashes in
  `state/reviews/P2_service_reset_review_raw/source_maps_1790187050866977000.json`.
  Current tools and production manifests remain the tools under test. Existing
  negative mutations still start from and alter that verified approved fixture.
- D118 reads the existing91-file exact staged source archive
  `state/analysis/P2_dump_fifo_raw/target_sources_e820c0e1` by staged name.
  Keep every file hash, count91 and aggregate e820c0e1 assertion. Map its root
  `app.ino` back to temporary `src/app/app.ino` as before; do not overwrite the
  real project source or reauthorize the consumed run.

A small test-only P0 source provider may read the fixed Git revision and cache
its bytes per Python process. Git failure, missing paths, non-regular entries,
unsafe paths or hash mismatch must fail explicitly. No checkout, network,
production mutation or fallback to today's source. Copy only to the existing
temporary fixture destinations. Prefer Git plus the existing evidence over
another permanent source archive; document the full-history checkout dependency.
No production file or established assertion is changed by this task.

Inspect all fixture diffs independently; compare their assertion syntax to the
pre-repair originals. Run the unchanged affected cases and repeat the same296
methods, preserving original failures and exact runner inputs. Passing simulated
upload protocol tests cannot establish a board build, actual upload permission,
physical acceptance or a gate. D131/D132 final disposition follows real results.
