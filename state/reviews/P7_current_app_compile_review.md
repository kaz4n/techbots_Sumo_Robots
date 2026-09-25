# D185 current-app compile-only composition review

25 September 2026, Asia/Dubai. Separate same-model Codex reviewer with reused
context from earlier P7 reviews. This is neither a fresh-context/cross-model
review nor a phase-gate review. The reviewer read source, contracts, test sources,
diffs, manifests and retained results; did not execute the implementation, tests,
compiler, transport or device operations. This new review is the only owned edit.

## Verdict and findings

PASS for the bounded compile-only composition and its controlled validation.
No open BLOCKER, MAJOR or MINOR finding in this scope.

Closed MINOR: local admission originally hashed ADB without first checking that
its path and ancestry were plain. Final compile_current_app.py:279 adds exactly
`plain(Path(ADB))` before the hash check. The source diff from the initially tested
97a730a1 version contains only this insertion; the final suites cover the final
source. No historical executor/helper or locked test was changed for this fix.

This verdict permits no inference of a successful current target compilation,
MCU loading, RAM fit, WCET, physical behavior, motor-run permission or phase pass.
It does not resolve the historical default profile's 592-byte modeled deficit,
the conditional MATCH memory margin, or the earlier static full-app I/O fault.

## Reviewed identities

Paths below are repository-relative unless explicitly absolute. Implementation
and oracle paths are under state/analysis/P7_current_app_compile_raw/.

| Input | SHA-256 |
| --- | --- |
| state/analysis/P7_current_app_compile_contract.md | 2f2c90d58913c208aadef126733e465d4bf6de249b5065147e2ff870391174d4 |
| compile_current_app.py, final | aed3fbf4db5c962761affd5a3e2e52b1002feaaefe4e44f9f34df6ec78ba5ede |
| test_compile_current_app.py, corrected frozen 27-method oracle | 9caf2709027af7184026d6d30f09f27e758663eb985c869380b6b74be43dca56 |
| test_compile_current_app_errors.py, corrected frozen seven-method supplement | 462e246693c4683e73d7a1992ce9413e8e9f237e7ca77c8fdfc7706d8b8d7183 |
| inputs_bench.json | 22e0250a9ca6044119865465a6b4655c374b1d4885fb1cde3fe27701a0878c47 |
| inputs_match.json | 1cd886ce62ef9f336520335a0e5786c0953438820e1e4840f43cb7173ee472e3 |

The final source/scopes commit is 6c938ada. Both actual manifests were separately
hash-checked against all 115 current files: 104 source files, including three
.gitkeep files, plus 11 exact caller/contract/dependency inputs. Their file maps
are identical; their profile fields differ. Both bind app source
37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29 and boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 on fixed ADB serial 2629958581.
These are coordinator-created invocation inputs, distinct from synthetic test
fixtures. A later actual invocation must supply its then-current committed,
clean reviewed HEAD; this review does not supply an execution result.

## Contract-to-source checks

- compile_current_app.py:74 rejects malformed CLI forms before I/O. The local
  path checks, finite bounded JSON, exact file set, historical hard pins, current
  source mapping and repeated admission at :243 bind actual bytes. Check-only
  at :288 performs local reads and read-only Git checks without ownership,
  staging, board commands or result writes. Execute additionally requires the
  selected absent isolated bytecode-cache path and fresh owners.
- At :142 and :153, whole-file and extracted wait/reap body hashes protect the
  current helper. Only enumerated original AST functions/methods and literal
  IDENTITY/REMOTE_CHILD are evaluated in a private namespace. Original owner
  constructors, main/run routines and historical module globals are not used or
  mutated. Frozen executor remains 84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d;
  current wait source remains 95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e.
- Fresh local owners/stages and remote command owners protect consumed attempts.
  Exact existing canonical source may be reused only after complete verification;
  partial, mismatched or colliding source is refused without overwrite. The
  existing board.stage mapping and source hash are checked against the fixed
  current source. Local free space must be at least 128 MiB and board free space
  at least 1 GiB. These checks provide admission bounds, not a storage guarantee.
- The original child process lifecycle, one query/one compile restriction,
  jobs=1, null CLI configuration, clean isolated environment, deadlines, process
  group termination and reap behavior remain inherited. The wrapper's :182
  failure_guard retains an already-raised subprocess exception; when a receipt
  write fails before the inherited code constructs a nonzero-child exception,
  it recovers the already-observed failure and attaches write diagnostics.
  It does not change the original sequential finally writes into best-effort
  writes: a first failed write can prevent subsequent writes.
- Identity and both exact F166 prerequisite inventories are checked before
  staging, with only the admitted boot replacement and original timestamp-only
  projection. Independent closure at :493 attempts local, identity and both
  prerequisites even after failure, plus remote source and installed-policy
  checks when their applicable state has been reached.
- :442 derives the canonical local verified receipt from the exact returned
  artifact UUID, never from latest mtime. It checks profile/source/FQBN/flags,
  startup path, integer compiler zero, true precompile checks, exact installed
  pins and four artifact digest entries, and the corresponding command.json.
  :511 retains the first error, attaches compile_outcome, and makes failed final
  evidence persistence fail the operation. Success requires all closing checks.
- Bench is MATCH0/MOTORS_ALLOWED0/default; match is MATCH1/MOTORS_ALLOWED1/Immediate.
  Both paths compile only. No upload, reset, capture, package installation,
  binary retrieval or deletion is introduced by this caller.

## Independent oracles and retained results

The separate oracle author reports no new implementation read during authoring;
its work is accurately labeled reused-context/same-model. The main suite uses
real local admission, source staging and orchestration with Git/native endpoints,
compile_app and final-policy endpoints controlled. The supplement calls the real
inherited receipt guards with substituted child replies or subprocess results
and selective ENOSPC writes. These are controlled host tests, not board evidence.

Original test evidence remains distinct:

- Main oracle 416581234aaf693e9d50b152138bcadeefba19cca12f9a169d4bc7ec65545fa7
  ran 27 methods and produced five errors across four method names: its synthetic
  verified receipt incorrectly used an empty file_sha256 map. Independent
  adjudication against existing policy and a real historical receipt corrected
  only the fixture to the exact 18 installed pins plus four artifact entries;
  the 27 test assertions were preserved. test_run01.json remains retained.
- Corrected main oracle passed 27 methods in 76.824 s on initial source 97a730a1,
  retained in test_run02.json, SHA-256
  789e1904709baeecb8da9bf29feaf4a2dac970eccff82ce735b1c451a461f569.
- Original supplemental oracle 723bc6b168456723251f23b42124ba32efb13cfb1487c71c2939b97945c7b6ac
  produced four errors from missing controlled prior source-ownership state and
  one assertion expecting all three sequential writes to be attempted after the
  first failed. supplement_run01.json retains these failures. The authorized
  fixture correction sets only the isolated prior-admission state and splits
  each reached finally-write failure into a fresh case. Exact primary exception
  identity, compiler status/output and secondary-write assertions remain.

The first final-source attempt hit real host ENOSPC while saving its result; no
result is inferred. A later RAM-first run was observed by the coordinator but
its raw files were absent on subsequent reads. Their cause of disappearance is
unproven, and those lost receipts are not durable validation. Repetition was
necessary to retain reviewable evidence, not to change a failing implementation.

The reviewer independently read and SHA-256 checked the final durable originals
under /home/ubuntu/sumox-d185-recovery-20260925/:

| Receipt | Result | SHA-256 |
| --- | --- | --- |
| test_final_main.json | 27 methods PASS, 36.333 s; exit 0, no timeout | 6bf5c9c90196a3ad4d14f7bb4e89335747da0a9677905f47801cbf04ee89e3f8 |
| test_final_errors.json | 7 methods PASS, 10.229 s; exit 0, no timeout | 49823ae62f6ab8fe8edb8c433aafc720666c4e87b1c6216bf1c83a3c8dab1038 |

Both record final source aed3fbf4 and the corrected oracle hashes above. The
coordinator fsynced these persistent-home receipts before printing their results;
they remained readable across the reviewer's separate WSL invocations. Exact
hashes identify canonical copies independently of restoration location.

## Storage and next action

Because C: evidence writes failed, this review is first saved and fsynced beside
the durable originals in WSL home. The coordinator may copy its exact bytes to
state/reviews/P7_current_app_compile_review.md and the receipts to their canonical
evidence directory, preserving failed/empty artifacts and recording restoration.
No source or test change is requested. Before any separate current compilation,
restore adequate local disk space and satisfy the caller's fresh admission. No
current target compilation or MCU activity is established by this review.
