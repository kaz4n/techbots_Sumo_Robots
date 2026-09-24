# D133 historical fixture review

The three adapter changes are appropriately limited to their source provider.
Existing source-map/count/aggregate, containment, safety and protocol assertions
remain. Coordinator AST evidence records all 102, 130 and 112 existing assertion
calls unchanged. The D118 archive's exact 91 files and e820c0e1 aggregate were
independently rehashed before recommending that adapter.

Pre-execution helper finding, MAJOR for fixture functionality:
`reviewed_source_fixture.py:55` calls `_safe_name` before handling directories.
The actual fixed-revision Git archive begins with the ancestor directory
`bench`, which `_safe_name:36` rejects because it is outside all three source
roots. Read-only enumeration of the real archive confirms this first entry.
Draft helper SHA-256:
`9cb381155e6e9103ededa3f4115e74ac8657d201d7bd9ef00ce052c46ec276cf`.
Allow only validated ancestor directories while retaining the strict file-root
restriction. Worker/coordinator notified before any D133 regression rerun.

Also recommended an explicit resolved destination-outside-repository guard;
the draft refuses existing paths and symlink ancestry, while its adapters
already supply contained TemporaryDirectory destinations. Keep current sources
and all real approval/run/evidence records outside the copy surface.

Final static review: helper SHA-256
`ff50369e697ed414f3002f5800b5a017cb5199608e45b0e5f8d4730d2c5561bb`
closes the ancestor-directory finding. Only directory entries may be exact roots
or their ancestors; regular files must remain below the approved roots. It also
rejects resolved repository destinations. Fixed Git revision, regular-only safe
archive paths, both exact maps/aggregate pins, verification before directory
creation, absent/non-symlink destination and exclusive file creation remain.
No fallback, live approval or production change is introduced. Scoped static
review PASS, no remaining material finding. Final coordinator-executed
`analysis/P4_push_literal_raw/regression_retry1.{json,txt}` reports the same
296 methods PASS, zero failures/errors/skips, with exact frozen inputs. The
original failed296-method run and pre-D132 baseline remain retained.
