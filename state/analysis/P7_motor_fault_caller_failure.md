# D179 first frozen oracle adjudication

First execution: source d8418fad / 8b47b1d6, oracle 5fb59139 / d298ec01.
44 methods:42 PASS,1 FAIL,1 ERROR,0 skips. Original receipt is
P7_motor_fault_raw/caller_first.json (02d7e9ee); source/oracle remain in Git.
Native calls0, all24 pins exact, RAM fixture remnants0, real scope/owner absent.

Separate same-model reviewer and independent spec-only test author agree both
failures are new fixture errors. No production repair is indicated.

1. The dangling-owner test created a symlink then used a generic rejection helper
   asserting that the owner did not exist, contradicting required retention.
   Its original instance was also already consumed by a failed claim. Correct
   only this fixture to use a fresh caller and assert rejection, retained exact
   dangling link, and zero process/device calls. Keep the pin-drift assertion.
2. The maximum-eleven test repeated one prerequisite nine times. The ceiling
   does not require arbitrary repetitions: the caller additionally limits each
   prerequisite to three phases. Keep changed-command/timeout/label negatives
   before exhaustion; complete the specified three queries, upload, three
   queries, capture, three queries; assert11 and reject a twelfth with no call.

D051 permits these engineering corrections to this newly authored, nonlocked
oracle. No established assertion, locked test, source limit, historical scope or
firmware changes. The original failure remains visible; corrected tests must be
frozen before their next execution. This is not hardware or phase acceptance.
