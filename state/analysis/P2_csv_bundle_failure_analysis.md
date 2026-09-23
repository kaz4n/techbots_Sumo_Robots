# D-074 review findings and first repair - 2026-09-23

Fresh read-only reviewer found a MAJOR before release: the local path filter
rejected identical `//` and `\\` prefixes but accepted mixed Windows UNC
separators. Such a path could reach os.lstat and initiate a remote filesystem
lookup. Reproduction used only in-memory path analysis and mocked filesystem
calls; no network share was contacted.

Independent author added all four separator pairs for both frame and manifest
paths, guarding lstat/stat/open against any remote-looking lookup. First full
new-test run:38 methods, exit1, two failure reports in the UNC test (the guarded
lookup and its no-access assertion). Other cases, including actual C++ formatter
integration, passed. The pre-repair module and SHA are retained alongside this
red receipt in P2_csv_bundle_validation_raw/.

Root took ownership after worker completion. First repair rejects any pair of
leading Windows separator characters before filesystem access. No test predicates
changed. Retry38 methods PASS2.890s, exit0; separate reviewer reproduced38PASS
2.584s with no skips and closed the MAJOR. This does not claim an adversarial
filesystem or atomic multi-file snapshot guarantee; the contract preserves that
limit and verifies ordinary descriptor/path identity across each bounded read.

Reviewer MINOR: README said the report preserves individual ordinals/counters,
although detailed rows stay in input CSVs. Wording now says validation accepts
them without rewriting input files. No report-schema expansion; MINOR closed.
Failed evidence remains visible; no test weakened or physical result invented.
