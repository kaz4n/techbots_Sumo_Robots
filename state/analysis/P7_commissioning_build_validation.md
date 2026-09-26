# Shared commissioning build path

D222 implements a compile-only main-application path for b4_stand, p3_drive,
p3_turn, p3_stop, p4_reactive, p4_timing and p5_abort_timing. Each requires explicit
M0 or M1, MATCH0, static linking and default startup. Existing firmware, inert
bench wrappers, prior callers, tunables and locked tests are unchanged.

Independent tests passed 11 policy plus 19 caller methods on Linux; Windows passed
11 policy plus 18 caller methods, with one explicit Linux descriptor test skipped.
All six source/contract/test inputs stayed unchanged during the successful runs.
The first policy run retained B4M0 flags in one new expected-report fixture,
causing 13 subcase failures. The original test and output are retained; correction
uses the independent literal flags for each tuple and preserves full equality and
all 14 combinations. No production edit was made to satisfy that failure.

[Source/host review](../reviews/P7_commissioning_build_review.md) is FINAL PASS,
SHA-256 dc6439f379ca3299f3c1022f035fcbcef89e116223562c97c3400220d1989e6a.
The [contract](P7_commissioning_build_contract.md),
[test plan](P7_commissioning_build_test_plan.md) and
[successful input identities](P7_commissioning_build_raw/host_inputs02.json)
bind the source and evidence. Native compilation is the next action, not an
outcome established by these host tests.

The review conditionally admits the 14 profile/motor tuples using token native01,
one query/compiler per fresh owner, sequential jobs=1 and clean exact committed
HEAD for each attempt. Retain and commit each completed owner's evidence before
the next tuple. Stop on failure without retrying or changing scope. This route has
no upload action; M1 compilation is not permission to run motors. Physical trials,
native log delivery, initialized timing/RAM and human gates remain open.
