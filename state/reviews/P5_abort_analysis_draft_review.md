# P5 abort-analysis companion draft review

Scope: read-only design review of draft SHA256 `306e64dd3254baea11d6af1c2686947694a18f6efe59a93320108b829a03f993`, against adopted D135 `eb61724fa8667e96beed4f4b82ad1a5e1b8c247fbde59844fe655774ee7fe36b`, D130 contract/current public tool usage and P5 acceptance. No implementation/test/board/compiler execution.
Provenance: separate same-model reviewer, reusing prior P4/D134/D135-design context; not a fresh D135 producer reviewer or cross-model review. Only this review file is owned here.

## Findings

- CLOSED MINOR, original `state/analysis/P5_abort_analysis_contract.md:54`: optional whitespace before U contradicted the claimed canonical C++ literal (`1000 U` is not `1000U`). Revised lines54-64 require contiguous decimal digits and U/u, distinguish surrounding whitespace, and reject other suffix/leading-zero/expression forms. UNSUPPORTED_CONFIGURATION is explicitly an error code.
- CLOSED MINOR, original `state/analysis/P5_abort_analysis_contract.md:214`: the exact report omitted error-path/count definitions. Revised lines231-281 define cohort-versus-source status, including invalid-source empty cohorts, require all bundle validations, prohibit decoding/fallback under invalid source, and fix nullability, invalidation and qualified-pass/trusted-failure counts. These resolve the previously divergent oracle possibilities.
- CLOSED MINOR, original `state/analysis/P5_abort_analysis_contract.md:201`: “source age” could be mistaken for effective-cue age. Revised lines205-209 explicitly separate the current acquisition from older held/debounced bits, reconstruct neither first detection nor physical onset, and add no effective-cue age threshold or GO-to-read constraint.

## Recommended D051 decisions

1. Adopt declared source/revision/flags plus byte-verified historical config. Keep signature/build/image/producer verification outside this companion; missing identity is incomplete, disagreement invalid, and matching hashes do not prove a common physical run.
2. Adopt the narrow seven-literal/exact-flag subset after the suffix clarification. Unsupported spellings are unsupported analysis inputs; the producer's broader configuration contract is unchanged. Reuse the CSV validator's public entry point and D130's bounded read/binding pattern; add no shared framework or board-tool dependency.
3. Adopt eligible HANDOVER_FAILED as a qualified evaluated failure, never an absent favorable timing sample. Ten evaluated attempts can produce FAIL; absent A stays null and contributes no elapsed extrema.
4. Adopt missing-GO INCOMPLETE versus later-GO INVALID, header-only INCOMPLETE, GO-to-D checking, and read-relative prefix chronology. Preserve full-order decision-suffix adjacency, six-record maximum and one candidate; do not invent CSV batch boundaries or reconstruct omitted endpoints.
5. Adopt ELIGIBLE only as declared hardware-origin eligibility for external review, with all acceptance booleans false. Synthetic M1 arithmetic, matching declarations and distinct file hashes cannot prove physical 10/10, permissions, clock calibration or producer behavior.

One cohort has one mode and one source/config/profile; left/right remain separate. Its ten scheduled slots retain every failure/exclusion; later blocks cannot overwrite them. No retry grammar, favorable substitution, dashboard, transport or tuning scope is introduced.
The draft correctly keeps A-D (inclusive historical TICK_US) distinct from source age, permits valid late values, records same-D handover without claiming zero computation, and admits neither zero-duty nor prior-positive-duty requirements. T/C/next-epoch chronology, full 64-bit ownership and acknowledged M1 EN remain producer-enforced because the wire omits them.
Closure checked against revised draft SHA256 `fea16ebd686c3616dd2f78c7f6f7c5037d39351546481e1fc1da71adeb1e97a7`; only the changed contract sections were reread. No implementation/tool/test or compiler/board execution was involved in closure.
Verdict: PASS for the design review, no open BLOCKER/MAJOR/MINOR. Recommend the five explicit D051 decisions above; coordinator adoption remains required before independent oracle freeze. This review does not adopt the draft or establish producer correctness, native fit, physical P5.3 acceptance, later ATTACK qualification, other P5 tests or a phase gate.
