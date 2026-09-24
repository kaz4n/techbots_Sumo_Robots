# D131 independent source review notes

Reviewed adopted contract, public headers, AGENTS.md, safety-auditor and REVIEW_GATE; current date 2026-09-24 precedes the 2026-10-01 freeze. D128/D131 permit software preparation ahead of physical gates.

- edge.cpp:269-296 admits only fresh eligible front-only IDLE observations. It captures one unsigned timestamp, changes only healthy finite coordinate history, and transitions irrevocably to SPENT on termination.
- edge.cpp:304-312,391-396,407-414,440-462 initialize replan storage on each ESCAPING transition and avoid reading timestamp storage as a counter. Fresh black spends deferral without entering/exiting a row. Real completed fresh-black exit rearms.
- edge.cpp:421-430 leaves pre-GO permission closed and consumes active deferral on permission loss; actual escape still latches PERMISSION_LOST.
- fsm_robot.cpp:400-413 derives authorization from previous ATTACK, sampled current effective bearing/FC and normalized raw FC. It does not hide line masks or new-white evidence.
- fsm_robot.cpp:119-123,433-439,755-788 revoke on later arbitration and qualified unsuppressed stall before limiter.request or executed-stall/reflank accounting. The second Escape call is bounded and happens only after an initial deferred/no-row result. Second routeMotion takes the escape/inhibited branch; no second perception/contact/Governor pass.
- fsm_robot.cpp:commitAndGovern, src/core/governor.cpp and src/hal/motors.cpp preserve one contact commitment and final governor shaping followed by actual MotorGate duty/hold checks. These boundaries were not edited.
- Changed production paths introduce no loop, heap operation, clock, bridge, serial, GPIO or network path. Existing loops have fixed compile-time limits. This is a source audit, not full-source target WCET proof.
- All40 prior protected file hashes matched. src/config.h and native app/build/flash sources are unchanged.
- Seven prior/current host profile layouts match. Escape remains208 bytes, EscapeSample28, Robot2640 and Runtime166624 in the default host layout; target ABI/image fit is not established by these measurements.
- MAJOR tools/board_tool.py:147 (current staging): Invalid101 and UINT32_MAX fail static assertion; the 2^32 literal fails only the HOST -Werror overflow diagnostic. Native policy pins warnings off and has no literal admission, allowing overflow to truncate before the typed static_assert. The represented duration remains bounded and shipped0 is unchanged, so this is not an unbounded-motion BLOCKER. It is an explicit D131 admission-contract gap; complete software-packet acceptance needs pre-remote rejection of invalid raw literals. Root acknowledged a linked P4 fix must close it before packet completion.
- Public tests cover configured Runtime/Transaction/MotorGate and real applied pulses, retained line expiry, raw polarity/FC loss, no fabricated history pulses, no limiter-slot consumption and seeded streams. An explicit pre-filled limiter + newly qualified deflection during deferral was suggested as an additional coverage edge; source ordering is already correct.

Initial private expectations were frozen before implementation/new public test reads. Two pre-execution fixture corrections are recorded separately; both original and corrected sources are retained. Awaiting coordinator-executed public/private receipts before verdict.
