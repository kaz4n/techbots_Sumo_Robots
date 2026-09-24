# P4 follow-up: raw push-through literal admission

Proposal from a read-only source map during D131 verification, 24 September2026.
The shipped literal remains0. No target command or malformed native build was run.

`board_tool.py:147` copies config verbatim; `flash` stages at353, hashes at354,
and only then inventories/synchronizes/compiles. The checked default upload route
also calls `stage` (`app_default_run.py:328`). Current preflight verifies tool,
profile, property and source identities; it does not validate this initializer.

`edge.cpp` rejects typed durations above100, but a raw initializer exceeding
UINT32_MAX can convert to0..100 first. Host compiler -Werror rejects that overflow;
the pinned native policy uses compiler.warning_flags=-w. The separately invoked
B16 registry parses Python unbounded numbers but is not a build admission step.
Thus D131's host overflow rejection must not be claimed as native admission.

Recommended bounded fix before positive target tuning: validate exactly one
supported decimal literal EDGE_PUSH_THROUGH_MS declaration on the copied staged
config bytes, immediately after the copy and before any remote action. Parse
with Python int and require0..100; reject duplicate, missing or unsupported
initializers explicitly. Preserve the exact shipped declaration, source hashing,
profile flags and existing C++ assertion. Do not add another tuning source.

Independent tests should cover actual stage/flash ordering,0/20/100 success,
101/4294967296/4294967316 failure, negative/expression/duplicate/missing forms,
and no transport invocation on refusal. Existing tooling fixtures must not be
silently weakened. Adopt a precise contract before dependent implementation.
Source-map author: separate read-only explorer `/root/p4_push_admission_map`;
coordinator recorded this proposal. This is an outstanding software dependency,
not a measured native failure or permission to tune/run hardware.
