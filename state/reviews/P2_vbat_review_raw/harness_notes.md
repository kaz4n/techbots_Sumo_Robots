# D110 reviewer harness notes

The first post-execution summary verifier incorrectly expected90 JSONL rows in
the inherited registry receipt. It contains five profile rows, each invoking
the existing18-check registry. That verifier stopped at `assert len(registry) == 90`
in review_execution.py:35 with AssertionError. This was a reviewer receipt-schema
mistake after all actual tests had passed. The corrected verifier requires five
profiles, an approved successful profile and four expected original-assertion
failures with18 checks each. No implementation, oracle, test execution or raw
command receipt changed; no redundant test rerun was made.
