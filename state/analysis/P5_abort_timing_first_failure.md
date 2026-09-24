# D135 first host execution, preserved before adjudication

2026-09-24 15:29 Asia/Dubai. The first independent public normal-profile run
compiled both targets successfully, then CTest exited8. M0:37/40 cases pass,
10 failed assertions. M1:33/40 pass,32 failed assertions. No sanitizer/private
execution occurred in this run. Scratch was released after exact receipts.

Evidence: P5_abort_timing_raw/normal_first.json, normal_first.txt and
normal_first_LastTest.log. All656 frozen source inputs matched before/after;
42 previously established protected sources remain unchanged. Original public
oracle/interface commit b0540500 precedes execution. The new locked candidate
has never passed or been accepted as established safety coverage.

Independent author identifies three classes for separate adjudication:

1. Ten assertions per motor profile require Fault::NONE when the actual Gate
   returns its documented latched STOPPED fault and inhibited receipt.
2. Four M1 assertions require ordinary diagonal braking for DIRECT masks6/9,
   despite centered front plus previous positive applied duties selecting the
   approved B4.3/D049 pushed-out pivot first. M0 cannot satisfy that qualifier.
3. Eighteen M1 assertions assume APPLIED is the first batch event. A legitimate
   previous-receipt FIRST_NONZERO_DUTY may precede it. D135 requires receipt
   closure before current-decision events, not before other prior-receipt events.

These are initial diagnoses, not permission to weaken assertions. The author
and separate reviewer must agree on narrow spec-derived replacements before
editing the new unaccepted candidates. Keep original counts, assertions and
receipts in Git. No production repair or existing locked-test amendment is
approved by this note. Native fit/physical trials/human gates remain separate.
