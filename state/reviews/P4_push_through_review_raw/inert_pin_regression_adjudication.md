# D132 wider regression: historical inert-source prerequisites

Read-only preliminary adjudication while the full regression suite is running.
The positive upload and LF-checkout tests are not evidence that current sources
have an inert approval. `test_tools.py:78` and `test_adb_transport.py:189` copy
today's entire `PROJECT/src` into their temporary roots but call this the
reviewed source snapshot. Their production manifest remains historical.

The P0 matrix/timing entries were last adopted in commit `1b1d77dc`; later
manifest commits added other sketch entries. D105 explicitly preserves
historical exact keys and requires changed-source upload refusal until separate
review (`state/DECISIONS.md:1388`). That decision predates D131 and D132.

The D132 diff only adds copied-config validation and an identified copy error
at `tools/board_tool.py:239-243`. It does not alter stage layout, source bytes,
`source_hash`, inert approval keys or `verify_inert_source`. In `flash`, source
hash verification at lines 450-452 still precedes core verification, remote
directory creation, synchronization, compilation and upload. The expected
diagnostic is `inert upload source differs from reviewed P0 snapshot`.

Disposition: retain the full suite's actual failed status and all output. Run
selected failing positive-upload, LF-checkout and compile-failure sentinel
cases with the pre-D132 tool against the exact same current source tree. Only
failures reproduced with the same pin-refusal cause can be classified as
pre-existing unavailable approved-source prerequisites, rather than D132
regressions. A compile-failure sentinel cannot reach its mocked compile while
its source fails this earlier guard. Continue inspecting any other failures
separately. Do not refresh keys, accept current bytes as reviewed, skip failures
or weaken positive assertions to make the result green.

Positive upload-path protocol tests can later use an exact archived approved
snapshot in a separately reviewed fixture change. Actual approval of new
sources and any target/run prerequisites remain separate work. No new source
approval or successful broad-suite claim follows from this adjudication.

## Completed baseline and fixture repair recommendation

The full regression completed 296 methods with 80 failed subcases. The
coordinator's `prior_tool_baseline.{json,txt}` reruns all five affected P0 methods
with pre-D132 tool SHA `f609de1713450c4a583fcdfba762bd5c5172d35480cd94304e18710c4a5a0f0d`
and identical current sources/keys: the same eight subfailures recur. The
unchanged D118 fixture independently raises `Public source fixture changed:
src/app/runtime_inputs.cpp` before production tool use. The other 72 failed
subcases share this prerequisite in 19 methods. None of these 80 failures is
evidence of a new admission regression; they still leave the broad suite FAIL
and 24 methods unable to reach their intended assertions.

For a separately bounded fixture-maintenance change, use current tools against
historical test-only source bytes, preserving every safety assertion:

- D118: existing `state/analysis/P2_dump_fifo_raw/target_sources_e820c0e1` contains
  all 91 required staged files. This reviewer rehashed every file against
  `source_pin_proposal.json` and recomputed the exact aggregate
  `e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69` with no mismatch.
  Read those immutable bytes, map `app.ino` back to temporary
  `src/app/app.ino`, and retain the count, per-file and aggregate checks.
  `P2_app_default_run_oracle_review.md:11` anticipated explicit immutable-fixture
  maintenance after legitimate firmware evolution.
- P0: obtain `src` and the named matrix/timing bench trees from full immutable
  commit `1b1d77dcc3fc9ecfe5f6cbc0e47cb2dac9e4f461`, the adoption revision.
  Before relying on the fixture, check its actual staged per-file maps and
  aggregates against `P2_service_reset_review_raw/source_maps_1790187050866977000.json`
  (matrix91 files, timing87). Preserve current manifest keys and all upload,
  source-change, LF-checkout and compile-failure assertions. Reading Git blobs
  avoids a second permanent source archive; temporary extraction must be cleaned.

Do not mutate real approval keys, D118 approvals, consumed attempts, captured
evidence or current firmware. Re-run affected methods and required broader
regression after review of that fixture change. Focused D132 admission and
independent probes pass; complete broad-regression acceptance remains pending
this fixture repair and verification.
