<!-- Reviews the exact D141 policy implementation and independent host evidence. -->
<!-- Preserves a real path-binding failure and verifies its bounded repair. -->
<!-- Checked by source review, frozen receipts and an unchanged private reproducer. -->
# D141 static policy implementation review

2026-09-25 Asia/Dubai. Separate same-model review, continuing the contract/design
review. **PASS for the pure host-policy component after one bounded repair.**
One MAJOR finding was reproduced and closed; no open BLOCKER, MAJOR or MINOR
remains within this component. This is not a static artifact or phase acceptance.

## Exact implementation and independent oracles

| Input | SHA-256 |
|---|---|
| Original `static_policy.py`, preserved in `92d9bb8b` | `49389784b982c057b7298f6fa031770fceb73f3ed8c1224b74439e39a0d59cc3` |
| Reviewed repaired `state/analysis/P7_static_link_probe_raw/static_policy.py` | `ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775` |
| Original independent `test_static_policy.py` | `5c1b7a771c7982061e9a97db0c0dabd42f3a47a4ee8e5f6fff263a8845da36d1` |
| Original `freeze_policy.json` | `cdf83f9eb414e4fa62591ee9bdd2d76cbead5d34f27dc3c595df49bd21881774` |
| Independent supplement `test_static_policy_paths.py` | `ea044a6f4654c60985184300bf9833f28c61fda724819a934f98b16c8503dd16` |
| Supplement `freeze_paths.json` | `e1f56eafd17ae41d20e4854b4f170a7b997cb499e53a52248c924016dbb8bbb0` |

Oracle paths are under `state/analysis/P7_static_link_probe_test_draft/`.
All eight supplement-bound inputs were independently rehashed unchanged,
including the original oracle/freeze, contract, reference, source note and
production policy/reference. The supplement was frozen before its first run;
the original 27 methods and their expectations were not edited for the repair.

## MAJOR finding: literal caller paths were re-expanded - CLOSED

Original `static_policy.py:81-82` replaced BUILD_PATH and then DATA_DIR. A valid
canonical build path `/synthetic/@DATA_DIR@/build` therefore changed inside
effective commands after substitution, while builder metadata still identified
the original path. Both validators rejected correct literal commands and accepted
coherently redirected commands. The initial 27-method suite passed because its
path cases did not exercise this input; its helper also used sequential expansion.

The reviewer preserved a four-case independent one-pass reproducer and an
exit-1 result with zero passing cases. The separate test author then supplied
an additive eight-method path supplement without reading implementation. Its
first run against the original source reproduced two failing and six error
subcases. These failures are retained; they are not rewritten as first-run passes.

The repair adds only a regex import and one-pass substitution callback in
`_validate_commands`. Inserted path bytes are no longer interpreted as tokens.
It introduces no path restriction or altered expected behavior. The first repaired
run passed all 35 independent methods in 1.630 seconds. The reviewer reran the
unchanged original four-case probe: all four now pass, exit 0.

## Other reviewed requirements

- All eight implementation functions span 3-21 lines, below the 60-line limit.
  Public validation performs no transport, subprocess, network or write operation;
  its only data-file read is the frozen colocated reference, guarded by the literal
  SHA-256 `1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b`.
- Strict JSON checking rejects non-string input, duplicate keys, nonfinite tokens
  and exponent overflow such as `1e999`, including unused fields. Pure existing
  builder/path/property helpers remain unchanged and are not rebound.
- Fixed app/static/M0/wait metadata, upload-extension metadata, all 84 controlled
  values/key identities, existing empty overrides, installed-path relationships,
  successful builder envelope and compile-library rejection remain enforced.
- Independent I/O tripwires cover public calls. The unchanged production dynamic
  validator still rejects static input in the passing original suite. Production
  policy/reference/pin hashes remain those recorded in the design review.

## Compact retained evidence

All paths below are repository-relative; no failure file was replaced.

| Path | SHA-256 |
|---|---|
| `state/analysis/P7_static_link_probe_raw/policy_first.json` | `45cd2baceebf71c6ee2ab8c47ddd9eed4eef253b4346427125f41e52eb1ce350` |
| `state/analysis/P7_static_link_probe_raw/policy_first.txt` | `a69d5e8fe39d3a051f88f12e71ebfcee961701567aa3f30b51d5f2cae21028e3` |
| `state/analysis/P7_static_link_probe_raw/policy_fixed.json` | `fe5d1118cb354e8790e6f148f77b4fa923875d665795220584b0b40dfcc59ec6` |
| `state/analysis/P7_static_link_probe_raw/policy_fixed.txt` | `a38186e0d0a4e2a3788bd6a1189b9a7088d357662cecee8cd31c1f9562cab5f4` |
| `state/analysis/P7_static_link_probe_review_raw/path_token_probe.py` | `00611d402ba071ee0ee47915a90e549f7245e9349b45c103ee6ebaee9891786d` |
| `state/analysis/P7_static_link_probe_review_raw/original_path_token.json` | `c4f269325faf7812e661627744ceeb5158c34cb11df2c30cfb58250683cf49e4` |
| `state/analysis/P7_static_link_probe_review_raw/fixed_path_token.json` | `f840ada522aa28e88febf095b77c44a670a7fb17c3a1712ab419822781c74141` |

The independent supplement's original failure is separately retained as
`state/analysis/P7_static_link_probe_raw/paths_original.json` and
`state/analysis/P7_static_link_probe_raw/paths_original.txt` (log SHA-256
`d2d956a4236a44571fa57c61d62a2f501ee07bf3bf5fb56da49a4710ea0afbd3`).
The private reproducer command is
`python -B state/analysis/P7_static_link_probe_review_raw/path_token_probe.py`.

## Scope boundary

No artifact/runner implementation, properties query, native compiler, upload,
reset, hardware observation or full C++ test matrix was performed or authorized
by this review. D141 remains host-policy-only; full artifact interfaces, exact
ABI/section acceptance, independent artifact tests and later execution review
remain pending. D139's 592-byte dynamic default deficit is unchanged.

The reviewer edited only this new review and its compact private evidence.
Earlier reviews, implementation, frozen oracles, contract and ledgers were not
edited by the reviewer.
