# P1 B15 D-028 independent event buffer tests

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016.
Objective: specify retention of the first 4096 encoded events and observable
overflow using the committed public contract, independently of implementation.

Owned files:
- tests/test_event_buffer.cpp: 13 new doctest cases.
- state/analysis/P1_event_buffer_test_author.md: this report.

Sources read: current AGENTS.md, .claude/agents/test-author.md, PROGRESS.md,
PLAN.md section 3 and active P1 prompt during this session, BEHAVIOR.md B15,
DECISIONS.md D-028, and logframe.h committed as b1a8266. Existing tests were read
for doctest style. No src/core/*.cpp file was opened. No implementation, shared
configuration, locked test or another author's file was edited. The local date
matches the plan's Tuesday 22 September start; no phase gate is inferred.

Coverage: a literal 4096-capacity assertion; empty/default state; 4095/4096/4097
boundaries; a count for each of 129 rejected appends; verification of every byte
of every one of the first 4096 retained events after those rejections; copied
input lifetime; equal-tick insertion order at the full boundary; micros wrap and
descending timestamps without sorting; const bounds at logical size, capacity
and maximum size_t; reset hiding all 4096 previous entries; refill and repeated
reset; independent object status/storage. Fixtures use valid encoded events and
compare against explicit little-endian byte expectations.

The actual public production saturatingIncrement operation is checked at zero,
one, UINT32_MAX-1 and UINT32_MAX, with repeated saturation, the final 33 values,
and 10,000 fixed-seed inputs against an independent uint64 sum-and-clamp oracle.
Buffer-level tests establish one count per rejected append at reachable values.
No private-state mutation, extra test constructor or billions of calls are used.
The coordinator/reviewer must verify that production append uses this operation;
this author deliberately does not inspect its implementation.

After overflow, three successful independent frame-codec calls still produce a
literal 25-byte fixture while buffer status remains latched. This is container
and codec independence only: actual continued frame recording, acquisition,
scheduling, incomplete-evidence dump marking and transport remain unimplemented
integration responsibilities. No motion, board-memory or MCU timing claim follows
from allocating fixed-size objects on the host test stack.

Ambiguities/contradictions: none for the bounded committed EventBuffer contract.
append consumes successfully encoded bytes; tests check packEvent status before
calling it. Invalid encoding policy remains with callers, not this container.
Reset tests use only the public lifecycle API and do not select when a match or
HAL recorder should reset. No test dereferences a pointer after reset.

Validation at handoff: 13 cases authored using CHECK/CHECK_FALSE only. No shared
build or test execution by this author; coordinator owns normal and sanitizer
runs and the resulting pass/failure evidence. No commit created.
Next action: coordinator builds and runs these unchanged spec-derived cases,
resolves any failure against the public contract, and records validation in state/.
