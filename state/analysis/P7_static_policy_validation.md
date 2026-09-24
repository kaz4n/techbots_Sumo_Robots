# D141 fixed static-policy host validation

2026-09-25 Asia/Dubai. **IMPLEMENTED / HOST-TESTED.** This is only the pure
policy component for a future fixed-source static/M0 experiment. It does not
run a compiler, qualify an artifact or change production dynamic admission.
The current default image's 592-byte modeled loader deficit remains open.

## Implemented behavior

The scoped [validator](P7_static_link_probe_raw/static_policy.py) accepts only
reviewed static/default/M0/app metadata and all 84 exact controlled settings.
Its reference bytes are SHA-256 pinned, including otherwise inactive recipes.
Canonical data/build paths are substituted once so literal token text in a path
cannot redirect the accepted commands. Invalid JSON, duplicate keys, all nonfinite
numbers (including exponent overflow), wrong profiles/paths, altered references
and external compile libraries fail. The two public functions perform no writes,
network calls or process operations; their only file read is the fixed reference.

The [design review](../reviews/P7_static_policy_design_review.md) independently
reconstructed all 84 strings and verified eight additive pins while preserving
all 18 production pins. ARM flags remain a derived future expectation, not an
observed or accepted static image. The future full probe is still a draft.

## Actual validation and retained failure

- The independent author froze 27 public methods before implementation existed.
  Original source `49389784` passed all 27 in 1.569 seconds. Exact output is in
  [policy_first.txt](P7_static_link_probe_raw/policy_first.txt).
- Separate review then found a real MAJOR path-binding defect: sequential
  replacement rejected correct literal paths and could accept redirected ones.
  Its original four-case reproducer passed 0/4. The original source is preserved
  in commit `92d9bb8b`, with
  [the private failure](P7_static_link_probe_review_raw/original_path_token.json).
- The independent author added an eight-method supplement without reading the
  implementation or changing the original tests. Its first execution against
  the original source reproduced two failing and six error subcases. See
  [paths_original.txt](P7_static_link_probe_raw/paths_original.txt).
- One bounded implementation repair changed substitution to a single-pass regex
  callback. Final source `ec3d8a5e` passed all **35 methods** in 1.630 seconds on
  the first repaired run. The eight frozen test/dependency inputs stayed exact;
  [policy_fixed.json](P7_static_link_probe_raw/policy_fixed.json) binds the command,
  source, oracle manifests, exit 0 and full log. This is synthetic host evidence.
- The reviewer reran its unchanged original four-case reproducer against the
  repair: **4/4 PASS**, exit 0, with exact source and probe hashes in
  [fixed_path_token.json](P7_static_link_probe_review_raw/fixed_path_token.json).

No established assertion was amended, no test was skipped and no acceptance
threshold was reduced. Root also rehashed all 687 D138 frozen inputs unchanged;
firmware, configuration, production tools, host build and existing tests have no
diff from D138. Each implementation function remains under 60 lines. Unchanged
C++ matrices were not rerun because no firmware/build/test source changed.

## Remaining work and evidence limits

Final separate code-review disposition is recorded in
[the scoped review](../reviews/P7_static_policy_review.md). This component cannot
produce `STATIC_ARTIFACT_PROBE_PASS`, issue a board properties query, compile,
upload or reset anything. No board command occurred during D141 policy work.

Next define and independently test the artifact validator and one-shot runner,
including exact native address/ABI, placement, initialization, package freshness
and payload checks from the parent contract. Preserve the now-frozen policy
contract and oracle inputs; put the remaining interface definition in a companion
scope document. Obtain the separate bounded adoption/review before implementation
or any target query/compiler. Physical acceptance, deployment, live RAM/stack/WCET
and all human gates remain separate pending work.
