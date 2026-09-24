<!-- Reviews D139's fixed-baseline read-only staging adapter and default build evidence. -->
<!-- Keeps compile-only qualification separate from motor, runtime and physical authority. -->
<!-- Independent source and receipt inspection; reviewer performs no board action. -->
# D139 default-app qualification review

2026-09-24 Asia/Dubai. Separate same-model reviewer, continuing after the closed
D138 review. Scope: D139 unchanged current source, exact local stage reuse, and
one checked default-startup `MATCH=0 MOTORS_ALLOWED=0` compile-only baseline.
This is not a cross-model review, human phase gate or physical acceptance.

## Current disposition

**Precompile adapter, wrapper, plan and controlled-test review PASS.** The one
unchanged default/M0 compile-only baseline passed its compiler/policy checks.
**Default target fit FAIL: one open release-fit BLOCKER.** The completed local
ELF account, source/import/layout evidence and final packet have been independently
checked. Evidence review is complete, with the negative fit result preserved.
No other open finding was identified. No source repair, optimization retry,
upload or run follows this verdict.

## Target qualification blocker

**BLOCKER:** `state/analysis/P7_default_qualification_raw/app/loader_account.json:476`
records a conditional pristine-pool peak of 262736 bytes against a 262144-byte
pool, a 592-byte deficit. Ordered reconstruction first fails at the global-symbol
allocation: 4400 bytes required, only 3824 available. Compiler payload 257848 and
nominal remainder 4296 exclude loader overhead and do not establish fit. The
default/M0 profile cannot be marked target-fit-qualified from this baseline.
This is a negative release prerequisite, not an adapter implementation defect.

The independent [compile/account check](P7_default_qualification_review_raw/compile_account_check.json)
rehashes the final ELF, verifies the one actual compiler command and receipt,
and recomputes all 17 base model fields and ordered allocation arithmetic using
the unchanged retained model. Bound final ELF SHA-256:
`72a8bfcd320e8bfff7e5bcc6ef8607a98f9033866f3fa3d2be2cb95433e42f1d`.
Model SHA-256:
`1456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123`.
The original failed fit must remain visible; no second compile or repair is
authorized by D139. The account validator retained exit 1 and its original
assertion after saving the complete ordered negative account. Its first failed
allocation is 576 bytes short; the later 16-byte export copy brings the full
modeled deficit to 592. No real load was attempted.

The [target binding check](P7_default_qualification_review_raw/target_binding_check.json)
independently rechecks all 103 current sources and 102 local/remote staged hashes,
all 61 relocation-used imports against the hash-bound packaged loader, and the
raw GDB type/member query outputs for three checked debug ELFs. All 16 queried
size/alignment pairs and 79 legacy offsets equal historical D134 default. The
three new D138 metadata offsets are captured. Default `app::Runtime` is 166376
bytes versus 166304 in current MATCH, an expected profile-specific 72-byte
difference; the default layout was not substituted with the MATCH layout.
The packaged loader is unchanged at
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

The completed [validation report](../analysis/P7_default_qualification_validation.md),
SHA-256 `fad325468155c26f9321ddf5d87066291cf4bbfc7f5bd63d2baaf5da170773b0`,
accurately states compiler success and conditional-fit failure. The reviewer
rehashed all 86 files (1708702 bytes) and seven external dependencies in the
[final evidence index](../analysis/P7_default_qualification_raw/validation_index.json),
SHA-256 `deab85d74ed1e46f77cc08e0fe9e59119c5d068c0e5d97d9251a77e94f33003a`.
The [final review receipt](P7_default_qualification_review_raw/final_receipt.json)
binds this inspection and the earlier independent review receipts. Alignment and
baseline comparisons agree with the raw accounts. Cleanup receipts restrict
removal to 233 disposable files (7369554 bytes) in this unique build; all four
checked artifact hashes still match afterward. The local source stage remains
unchanged. The reviewer executed no deletion or board command.

## Finding resolved before execution

**MAJOR (resolved):** initial `reuse_stage.py:45` accepted an aggregate digest
provided by the caller, while initial `invoke_checked.py:20` loaded both mutable
manifest files without freezing their identity. A coherent source, stage and
manifest replacement with the same 103/102 counts could therefore authorize a
different baseline. This contradicted D139's fixed `fcddbd8e` source scope.
Original drafts `31eceb98` / `b8928332` remain under
[`draft_01/`](../analysis/P7_default_qualification_raw/draft_01/).

Corrected [`reuse_stage.py:4`](../analysis/P7_default_qualification_raw/reuse_stage.py)
pins `AUTHORIZED_SOURCE_SHA256` to
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`;
both declared and recomputed digests must match. Corrected
[`invoke_checked.py:18`](../analysis/P7_default_qualification_raw/invoke_checked.py)
pins both manifest byte hashes before parsing those same bytes. Reviewed hashes:

- Adapter: `78e173296c1d4366e4866b947b017814d69be2055c739cf1d96d0980eb40900e`.
- Wrapper: `e23c2e5a0b6901cacc14bd3095540963d5e52dc7c26a5d3717f465f9b109f59e`.
- Source manifest: `c106c0fb8baaf0a6f2536558da0084bd7d236c4ee8e77a4110b60107ad073391`.
- Stage manifest: `56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a`.

## Source and local identity checks

The adapter preserves the original `tools/board_tool.py:245` app/source guards,
`check_source` containment and symlink checks, reserved sketch-local conflicts,
stage ancestry/parent checks, and both configuration validators. Exact source
and staged file sets, every byte hash, `app.ino` mapping and ordered aggregate
digest are required. Missing, extra or changed inputs fail; there is no original
`stage()` call, copy, deletion, writer or repair fallback. The adapter returns the
existing directory. The wrapper writes only its own evidence receipts and logs.

The wrapper fixes `flash app --compile-only --startup default`, calls the
unchanged production `main`, and adds `--jobs 1` to native compile/property
commands. Existing `flash_profile`, configuration, toolchain, expanded-property,
build-policy and result checks remain active. Default flags remain exactly
`-DMATCH=0 -DMOTORS_ALLOWED=0`; no upload/reset follows compile-only. The local
stage reuse is read-only and is not a retry of the denied local deletion.

Independent [precompile binding receipt](P7_default_qualification_review_raw/precompile_binding.json)
rehashes all 103 current source files, 102 staged files, their exact mapping,
the pinned aggregate and five unchanged tooling dependencies. It also checks
the adapter/wrapper literals using AST inspection without executing either.

The independently authored frozen tests were read: 21 cases cover valid reuse, fixed
authorization/coherent drift, wrong sketches, file and manifest drift, mapping,
symlinks/ancestry, reserved names, validator failures and repeated read-only
calls. Synthetic authorization is substituted only in RAM, with the real literal
checked separately. Mutation, original staging, subprocess and network calls
are trapped; snapshots and manifest values must remain unchanged. Root's first
WSL run passed all 21 tests (52 bounded calls), 2.237 seconds, exit 0. The reviewer
checked every frozen input hash and all 21 individual `ok` results in the raw log,
whose SHA-256 is `c5769e4e26b44bc2bf98ff41c86ed5792562a6f87f4d57a771533f56338eb96c`.
Root's receipt binds unchanged actual 103-source/102-stage inputs before and
after the synthetic run. Frozen test SHA-256:
`4930c241bef7642b8a199004ce9f6e9632b3ff38e94c2c6b597d50fb51b8ff0f`.

The [qualification plan](../analysis/P7_default_qualification_plan.md), SHA-256
`406b1b6e7734a379696bafeda57145fcd4366595c1a7cace096cbd23fee2573a`,
preserves one immutable baseline and complete negative-result evidence. The
prepared accounting scripts preserve raw argv, source/artifact hashes and real
exit codes; the ordered account is written before a failed-fit assertion.
File-only GDB queries specify no target or inferior. The independent
[precompile acceptance receipt](P7_default_qualification_review_raw/precompile_acceptance.json)
binds the plan, freeze, tests and first raw execution receipt/log.

## Limits and next evidence

The reviewer has performed no adapter, wrapper, compiler, board, upload, reset
or motor execution. The checked default-profile compile and local conditional
memory account, source/import/layout checks and final packet review have
completed. A target compile alone does
not prove live memory, stack, WCET, native matrix behavior or physical acceptance.
No optimization candidate or source repair is authorized by this review.
