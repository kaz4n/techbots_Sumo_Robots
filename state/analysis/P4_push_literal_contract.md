# D132 contract: admit raw push-through literals before target operations

Adopted under D051 as a linked P4 follow-up to the D131 review MAJOR. D131 host
validation continues against its frozen files before this tooling change lands.
No target or positive tuning permission follows; the shipped config stays exact0.

## Boundary

`board_tool.stage(sketch)` must validate `destination/src/config.h` immediately
after copying it, before returning a usable stage. Therefore ordinary flash and
the separately reviewed app-default stage caller share the check. Failure is a
ValueError through the existing fail() convention, with EDGE_PUSH_THROUGH_MS in
the message. A malformed value cannot reach verify_core, remote, sync_sources,
compile_app, upload or any reset action. Existing local argument/config/tool
checks may run first; they are not board operations.

Expose `validate_push_through_config(path)` for focused tests, but tests must also
exercise the actual stage/flash path. Read only the copied config, leave its bytes
unchanged, and retain existing source hashing, profile flags, compiler policy,
staging layout and all upload guards. Do not add a second tuning source.

## Supported source contract

Ignore ordinary C++ line/block comments and quoted literals when locating code.
Quoted declaration-shaped text cannot satisfy this check. Require exactly one
active occurrence of the identifier EDGE_PUSH_THROUGH_MS; it must be
the sole supported declaration `inline constexpr std::uint32_t
EDGE_PUSH_THROUGH_MS = <decimal>U;`, allowing whitespace and lowercase u.
The canonical unsigned decimal has no leading zeros except single0. No signed,
hex/octal, expression, macro, cast, alias, duplicate/reference or conditional
redefinition form is admitted. This is intentionally a narrow source contract,
not a general C++ evaluator; unsupported spelling fails explicitly.

Convert the literal without fixed-width truncation and require0<=value<=100.
0/20/100 pass;101, UINT32_MAX,4294967296 and4294967316 fail. Excessively long or
malformed digits fail explicitly rather than triggering an uncaught parser
exception. Missing/unreadable/non-UTF8 config and unterminated block comments
also fail through the same identified error. Never infer a default when missing.
Unterminated quoted literals and all physical backslash-newline splices are
unsupported and fail explicitly before lexical stripping, including line
comments, quoted text, directives, CRLF and whitespace before the newline. C++
splices before removing comments; do not let that change which declaration is
active. No unrelated directive or completed conditional is rejected merely for
being a directive when it contains no splice or push-through declaration.
Current config contains no conditional push declaration; an unrelated existing
preprocessor directive is not itself grounds for rejection. A definition inside
a conditional block is unsupported (even #if0); do not attempt macro evaluation.
Code-level physical lines beginning with the preprocessor digraph `%:` are also
unsupported and fail after comments/quoted text are masked. This prevents an
alternate directive spelling from hiding a conditional definition; quoted or
commented digraph text is not itself a directive.

## Test isolation and compatibility

Independent new unittest cases freeze before execution and use temporary roots,
controlled commands/callbacks and actual stage() behavior. Probe copied bytes
instead of assuming the root file was staged faithfully. Invalid flash fixtures
must make zero remote calls; valid cases retain exact inert/profile arguments.
Established tool fixtures with intentionally minimal config headers may receive
only the required canonical0 declaration plus cstdint include. Preserve every
existing assertion; archive originals and have the separate reviewer inspect
these protocol-fixture additions. Do not change any established locked test.

Run relevant unchanged tooling suites, the new admission tests and registry.
This closes raw-literal build admission only. D131 native image fit, target
compilation, real WCET, physical tuning and all human gates remain pending.
