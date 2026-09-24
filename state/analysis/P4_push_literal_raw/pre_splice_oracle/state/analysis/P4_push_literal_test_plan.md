# D132 independent literal-admission test plan

Independent author read the adopted `P4_push_literal_contract.md`, repository
rules and public tooling fixtures. `board_tool.py` implementation was not read.
The module is imported opaquely by the existing fixture only when tests execute.
No new test has been compiled, imported or run during authoring.

## Files and freeze boundary

- `tests/tooling/test_push_literal_admission.py`:28 unittest methods, with grouped
  subcases, temporary roots and controlled board-operation mocks.
- This plan. No existing tests, minimal fixtures, production tooling or config
  changed by the independent author. Shipped duration remains root-owned exact0.

Root must archive these exact new files/hashes before first execution. Run the
new unittest module with the repository's existing package discovery convention,
plus unchanged relevant tooling suites and config registry. Existing minimal
fixture compatibility additions belong to the separately reviewed implementation
task, not this author. Preserve all original failures before any correction.

## Direct source grammar and error coverage

All101 canonical decimal values0..100 pass without byte changes. Explicit0/20/100,
lowercaseu, C++ whitespace, CRLF, line/block comments, comment decoys and unrelated
preprocessor blocks are covered. Comment handling checks line/block delimiters
inside the other comment kind and an ordinary final line comment without newline.

Reject101,4294967295,4294967296,4294967316,64-bit overflow and up to100001 decimal
digits through ValueError identifying EDGE_PUSH_THROUGH_MS. Reject leading zeros,
signed/hex/binary/float/exponent/separated/non-ASCII digits, missing/extra suffixes,
expressions, casts, macros, aliases, parenthesized initializers, unsupported
qualifiers/type/name/terminator forms, missing declarations and comment-only text.
Duplicate definitions, references, defines and undefines are explicit negatives.
Declarations inside#if0/#if1/#ifdef/#ifndef/#else/#elif/nested/spaced directives
reject without macro evaluation; commented directives remain ordinary comments.
Unterminated blocks, non-UTF8, missing files, directories and controlled read
denial use the same identified ValueError boundary. Both successes and failures
preserve the input file bytes.

Root's pre-freeze clarification excludes quoted strings/characters from active
identifiers. Tests accept quoted identifier/declaration decoys alongside the
real declaration and reject a quoted declaration as the sole authority. Escaped
quotes and quoted comment delimiters remain inert. Unterminated/broken strings
or characters and declaration/directive backslash continuations fail explicitly.

## Actual stage and flash path

Build temporary app, p0_matrix and reactive_test project shapes with the required
canonical0 config protocol, core/hal/app headers and sketch-local headers. Invoke
actual stage() for0/20/100 and compare literal destination layout and CRLF bytes.
Spy at the public validator boundary to assert it receives the copied destination
config, exactly once, after those bytes exist. A fault hook then corrupts only
that copied config to4294967316 before the real validator reads it; actual flash
must refuse while the valid root config remains unchanged. This distinguishes
validation of the stage from validation of a convenient original root file.

Invalid raw values, grammar, duplicate, conditional, comment and encoding cases
exercise actual flash for all three shapes. verify_core, remote, sync_sources,
compile_app and artifact verification must receive zero calls. Transport setup
and local configuration checks may occur; no real command or board operation is
allowed. Re-staging after replacing a valid config with an overflowing literal
must reject the new copied bytes, with no reused valid admission.

Valid app/reactive compile-only routes preserve exact inert and reactive compiler
flags, default FQBN/startup, checked compiler project, actual source hash, and the
sole expected mocked remote mkdir. Neither root nor stage config is rewritten.
No compile, upload, reset or physical device runs occur in these tests.

## Scope and remaining ambiguity

This validates narrow source admission, not a general C++ parser, motor safety
of positive tuning, target image/loader fit, runtime RAM, WCET or a phase gate.
Quoted-identifier scope was clarified by root before freeze and is covered.
No unresolved ambiguity blocks execution. Existing fixture protocol additions
remain separately owned and deferred until the D131 validation barrier.
Next action: root freeze, execute and obtain separate review.
