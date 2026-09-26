# D222 commissioning application build review

Verdict: FINAL PASS for the reviewed source and host evidence. No open BLOCKER.
The fourteen native compilations below are conditionally admitted; none was
performed or verified by this review. This is not upload, execution, motor-run,
physical commissioning, timing/RAM qualification or human phase-gate approval.

Reviewed on 2026-09-26 (Dubai), with initial HEAD
`9cef302c3f1b551da474d6fb2dbf6191677ffad6`. The new files were uncommitted at
inspection, so that HEAD is the review baseline, not an admitted native HEAD.
Today is the scheduled P2 bench day in PLAN section 3; delegated software work
does not fill the physical gate. The reviewer read AGENTS.md, the D222 contract,
current decisions/progress, the independent test plan and tests, new production
sources, relevant inherited primitives and retained host output. The reviewer
ran no tests or native actions, accessed no credentials, and changed only this
review file. Source authoring, independent oracle authoring and coordinator test
execution remained separate.

## Reviewed identities and evidence

Current bytes for all six entries in `P7_commissioning_build_raw/host_inputs02.json`
match their retained sizes and SHA256 values:

| Input | Bytes | SHA256 |
|---|---:|---|
| tools/commissioning_app_static_policy.py | 4779 | 1e46cf058ccab40a2cb8e0aa9f3e9583b1f11d35fd22baaf93ff9b55d78ba931 |
| tools/commissioning_app_compile_remote.py | 5305 | 476f6025e55fa9c2bdd0f29341fb660197a9f7eead8fd34b7c71e277158014a3 |
| tools/compile_commissioning_app.py | 17992 | 038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462 |
| state/analysis/P7_commissioning_build_contract.md | 8404 | 2a623c69bd31616fe8132a68f0914d0effa6945599c4785dd1b19c4e263d08be |
| tests/tooling/test_commissioning_app_static_policy.py | 15194 | 1595d7d11fe1007b0d1ec38f7604e0db75c5e46fd718bb3a5bea2544a4073a68 |
| tests/tooling/test_commissioning_app_compile.py | 28254 | 788c02161d88db7d905e542258405c99a6ac5c82f03c96aaf2be2146e62717ba |

Saved results under that raw directory establish:

| Owner | Result | Outer elapsed seconds |
|---|---|---:|
| first_linux_static_policy02 | 11 passed | 20.225 |
| first_linux_compile01 | 19 passed, no skips | 39.141 |
| first_windows_static_policy01 | 11 passed | 6.197 |
| first_windows_compile01 | 18 passed, 1 explicit Linux descriptor test skipped | 81.997 |

All four final invocations exited zero with no changed frozen inputs. The
reviewer independently matched all ten stdout/stderr byte sizes and hashes
against the five saved result receipts, including the initial failed run.
These are host results with controlled Git/transport endpoints. The Linux
descriptor fixture runs the actual descriptor/artifact validation over synthetic
accepted ELF/TLS data; it is not native target compilation.

The original Linux policy run, original oracle and thirteen failed subcases are
retained in `first_linux_static_policy01`. Comparing that oracle to the current
one shows the sole correction adds `flags=expected_flags(profile, motors)` to
the expected full report. The expected report previously retained B4 M0 flags
for the other thirteen selections. The independent literal selector map,
fourteen selections, full-report equality and negative assertions remain.
Production bytes did not change for this correction. This fixes a fixture
expectation; it does not weaken the policy or discard the failure.

## Source findings

No required source changes were found.

- Admission closes the public request grammar and exact built-in types before
  primitive loading. Profile IDs, explicit integer M0/M1, attempt token and exact
  forty-hex HEAD are bounded. The complete current source/helper set is compared
  to Git blobs at the selected HEAD before mutation; subsequent admission must
  reproduce the same complete manifest and saved bytes. The inherited local
  guard independently requires the same current HEAD and clean worktree.
- Every caller and policy load uses an independent namespace. The predecessor
  and frozen primitives are hash checked. All five policy snapshot identities
  are validated before their execution, and checked byte snapshots satisfy
  nested reads. The remote adapter validates all nine supplied bundle roles,
  sizes and hashes before executing a supplied primitive. Old caller globals
  and historical files are not rewritten.
- The closed fourteen flag identities preserve static linking/default startup,
  MATCH0, explicit motor identity and exactly the selected existing profile.
  No arbitrary flag/FQBN/path/upload option is admitted. Caller flags must match
  the selected snapshot policy; full metadata checks preserve compiler, recipe,
  library, linker and installed input constraints.
- Local output/stage and remote command owners are exclusive. The deterministic
  name binds profile, motors and SHA256(full source + NUL + attempt); full source
  and request identities remain in the manifest/receipts. A truncated owner
  collision refuses reuse. Source-addressed app reuse checks the complete
  file/hash/directory set. A claimed failed attempt is not automatically retried.
- The inherited executor selects board serial `2629958581`, checks the live
  boot/UID/CLI and conflicting process set, preserves initialization/builtin and
  installed-input checks, and emits one expanded-properties query plus one
  compiler with `--jobs 1`. The new path adds no upload, reset, monitor, motion or
  capture command. Compilation of M1 does not execute that image.
- Existing command, child deadline/reap, output, transport and space limits are
  retained: 30000 Windows command units; query 60 seconds; compiler 720 seconds;
  checked outer transport deadline plus 90 seconds; bounded captured child
  output; local 128 MiB and remote 1 GiB minimum free space. Artifact source
  transfer retains its checked two-part bounded payload and closing observation.
- The remote path retains all seven ELF/TLS/layout/package checks and separately
  compares the exported flat package. The local response checks exact profile,
  motor, attempt and full source identity before applying the inherited full
  artifact/layout report validation. Relabeling follows successful lower-level
  validation; invalid lower-level reports cannot become PASS.
- Early, compiler, transfer and late artifact failures preserve the first error
  and raw evidence. Available local/board/prerequisite/source/input/artifact
  closing checks are independent; failure in one does not skip later checks.
  Lost second-transfer replies preserve the partial closing path. Successful
  finish requires exactly one query/compiler and the checked artifact receipt.

The snapshot/projection ancestry remains a maintenance cost, but this additive
adapter leaves it frozen and does not introduce recursive prior-review pinning.
The new source is bound directly to the reviewed HEAD. No firmware/configuration,
locked-test, historical tool or physical-assumption change was present in the
reviewed diff.

## Conditional native compile admission

The coordinator may perform exactly this compile matrix after completing and
committing any concurrent read-only preparation. Use `native01` once for each
distinct profile/motor tuple, in the listed sequential order:

| Profile | Motor identities, in order | Attempt |
|---|---|---|
| b4_stand | 0, then 1 | native01 |
| p3_drive | 0, then 1 | native01 |
| p3_turn | 0, then 1 | native01 |
| p3_stop | 0, then 1 | native01 |
| p4_reactive | 0, then 1 | native01 |
| p4_timing | 0, then 1 | native01 |
| p5_abort_timing | 0, then 1 | native01 |

For each tuple, run the exact public command shape with `python -I -B`, first
`--check-only`, then exactly one `--execute`, the listed `--profile`, explicit
`--motors-allowed`, `--attempt native01`, and `--reviewed-head` equal to that
attempt's exact clean committed HEAD. Check-only is local and must retain
`board_observed=false`; it cannot substitute for live execute-time identity.

Admission conditions:

1. Commit the reviewed preparation and retain the six input identities above.
   Recheck required current/HEAD bytes and the canonical ordinary-app digest
   `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
   No source or helper edits are admitted by this review.
2. Keep source writers quiescent during each invocation. Run only one compiler
   process at a time. Existing local output/stage or remote command ownership
   refuses that tuple; do not remove or reuse a consumed owner to force a retry.
3. Preserve live serial `2629958581` and expected boot
   `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8` as execute-time guards, with all inherited
   identity/prerequisite/process/space/input checks intact. These are expected
   values from source and prior evidence, not freshly observed in this review.
4. Let each attempt close fully. Verify and retain raw results and checked
   artifact identities before committing that owner's evidence. The next tuple
   must use the resulting clean committed HEAD. The inherited dirty-tree guard
   permits only the current owner's untracked output; do not broaden its
   allowlist or ignore prior results to circumvent this requirement.
5. Stop the matrix on a failed admission, compile, artifact or closing check;
   preserve its first error and evidence. No automatic retry, new attempt token,
   altered boot/profile/source or unrelated native operation is covered here.
6. Preserve target artifacts and unique failure evidence. Any later scratch
   cleanup follows its own exact reviewed scope and the storage policy.

No STAND OK or RING OK is needed for these compilation-only actions. Neither
motor flag permits uploading or running the result. D223's read-only Linux
metadata observation is separate and is not native UART or MCU qualification.
Native compilation success must be reviewed from its actual retained receipts;
host acceptance alone supplies no such result.
