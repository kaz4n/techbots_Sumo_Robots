# D139 independent read-only reuse tests

`test_reuse_stage.py` contains 21 unittest methods and 52 bounded adapter calls.
Its expectations come from D139, the public adapter contract, the two public
manifests and the pre-existing `tools/board_tool.py` guards. The author has not
read `reuse_stage.py` or `invoke_checked.py`, imported either, or executed the
adapter. Only AST parsing of the test text has run; it passes syntax checking.
Same-model independent authorship is claimed, not different-model review.

## Coverage

- Exact 103-source/102-stage sets, app.ino mapping, excluded app/.gitkeep,
  sorted name/NUL/data digest, exact success receipt and repeated reuse.
- Missing, extra and changed source/stage files or manifest hashes; incorrect
  mapping; invalid digest; self-consistent one-tree changes; coherent replacement
  of both trees and manifests against an unchanged authorized digest.
- Wrong sketches; unsafe manifest paths; file, directory and staging-ancestry
  symlinks; empty sketch-local reserved-path conflicts.
- Real existing source, push-through and mode guards, including genuine invalid
  configurations with otherwise matching synthetic hashes.
- Mutation/process/socket/original-stage tripwires and source/stage snapshots
  before and after every adapter call. A tripwire AssertionError is never
  accepted as expected rejection. Rejection must use the distinct injected fail
  callback. The supplied manifests must also remain unchanged.

The real `AUTHORIZED_SOURCE_SHA256` is checked against the contract literal.
Only that named public constant is temporarily substituted in RAM for synthetic
fixture calls. Each fixture pins its initial authorization before fault stimuli.
Only the two actual-config-validator cases authorize their deliberately invalid
synthetic config so the original validator must be reached. No production value
is written. Source `bytes` fields are nonbinding metadata under the public
contract; name/SHA binding is tested independently of them.

## Execution and ownership

Root/reviewer runs this file after freezing its hash and the reviewed adapter:

```sh
D139_TEST_TMP=/dev/shm \
D139_REUSE_ADAPTER=/absolute/path/to/reviewed/reuse_stage.py \
python3 -B state/analysis/P7_default_qualification_test_draft/test_reuse_stage.py -v
```

Fixtures use the exact source filename list with small synthetic contents.
They are created only under uniquely named `sumox_d139_tests_*` RAM directories;
resolved ownership is checked before cleanup. At most eight fixtures coexist
within one test method. No actual build/stage/app path is modified. Source and
staging records are read only, and original board guards receive the synthetic
ROOT. No board, compiler, upload or reset is needed for these tests.

Only this draft directory is author-owned. Root owns test execution, immutable
failure capture, wrapper identity/argv review, acceptance and any later baseline
compile. Passing tests cannot authorize bypassing the rejected deletion or
establish physical or target qualification.
