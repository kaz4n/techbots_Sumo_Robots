# Contact preview independent test author — 2026-09-23 Asia/Dubai

Objective: specify read-only Contact/Fusion contact candidates for D-056 while
preserving D-027 contact lifetime and the existing observe/commit protocol.

Owned files: `tests/test_contact_preview.cpp` (16 cases) and this report only.
Sources: root AGENTS.md; `.claude/agents/test-author.md`; BEHAVIOR B0/B1/B5;
D-027/D-051/D-056; `src/core/opp_fusion.h`, `types.h`, `config.h`; contract
`state/analysis/P1_contact_preview_contract.md` at coordinator commit c39c8e7.
Read existing B5 tests for framework conventions; no implementation `.cpp` read.
Date checked: Wednesday 23 September, the PLAN section 3 P0/P1 transition date;
PROGRESS retains P1 host work authorization and no passed human gate.

Coverage: all 12 states and 128 masks for Contact eligibility; const/repeated and
alternative-state previews; prospective rise versus real retained latch; exact
visual counts for 101/111, pattern replacement and strict finite impact cues;
pending, missing and consumed Fusion observations; retained real contact after
invalid preview versus clearing by invalid commit; cached timestamps with changed
data; final REFLANK/every other ineligible-state commitment; skipped commits;
cue continuity despite skipped commitment; micros wrap, reset and effective
phantom-filtered mask. Candidate `contact_started` is prospective per the public
same-result contract; only the actual commitment may supply the event.

Ambiguities or contradictions found in this scoped contract: none.
Static check: new file reviewed, 16 cases counted; no build/test run by this author
because the coordinator owns serial validation. This is test authorship evidence,
not passing runtime evidence. Existing tests, locked tests and config unchanged.
No hardware operation, physical qualification, full Robot/R1/R5 claim or commit.
Next action: coordinator builds/runs this frozen file and retains actual results;
independent reviewer checks the combined change and any failure before revision.

Reviewer compatibility finding: vendored doctest with
`DOCTEST_CONFIG_NO_EXCEPTIONS` does not support this file's `REQUIRE` macro calls.
Author resolution: replace every `REQUIRE` with `CHECK` in the new unlocked file,
preserving every predicate. No checked value gates memory access, indexing or a
resource lifetime, so no early return guard is required. No framework/CMake or
existing test changed. The 16 cases remain frozen for coordinator validation;
this edit alone is not a passing build or runtime claim.
