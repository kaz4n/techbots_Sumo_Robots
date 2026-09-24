# D132 independent literal-admission test plan

Independent author read the adopted `P4_push_literal_contract.md`, repository
rules and public tooling fixtures. `board_tool.py` implementation was not read.
The module is imported opaquely by the existing fixture only when tests execute.
No new test has been compiled, imported or run during authoring.

## Files and freeze boundary

- `tests/tooling/test_push_literal_admission.py`:32 unittest methods, with grouped
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

Before first execution, root and the separate reviewer clarified that every
physical backslash-newline splice rejects before lexical stripping. The original
28-method tests/plan are archived under `P4_push_literal_raw/pre_splice_oracle`.
The additional method retains every previous assertion and adds35 negatives:
line comments, block comments, quoted strings, quoted characters, directives,
bare splices and a comment-splice declaration trap, each with LF/CRLF and spaces
or tabs before newline. No source parser or macro evaluation is assumed.

Root's next pre-execution clarification rejects code-level physical lines whose
first non-whitespace token is%: after comment/quoted-literal stripping, closing
the C++ digraph conditional bypass. Only the prior29-method test file is archived
at `P4_push_literal_raw/pre_digraph_oracle/test_push_literal_admission.py`, SHA256
`ACB72B8063A5570F968C6B9588C28E1005D22AE03B909A604554B22310E1855B`.
Three new methods retain every prior assertion:51 direct rejection subcases cover
conditionals, other directives, spacing, comment prefixes and CRLF; six accepted
decorations keep digraphs inside ordinary comments/quotes inactive; three actual
app/bench flash cases require zero board operations for a digraph-hidden declaration.
The D131 timing oracle remains frozen, and the old-fixture patch remains unapplied.

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

## First execution and narrow layout-oracle correction

The first32-method run returned three failures, all in the app0/20/100 subcases
of `test_actual_app_and_bench_stages_keep_supported_config_bytes_and_layout`.
The assertion expected `output/local.h`, incorrectly generalizing bench-local
header staging to the app support directory. All other first-run subcases passed;
original results remain `P4_push_literal_raw/admission.txt` and `admission.json`.

Independent author, separate reviewer and root agreed that this is an oracle
layout correction, not a production admission repair. The preexisting public
`P2_app_transaction_contract.md`:135-137 places app support under staged `src/app`
with only the `.ino` at the root. Existing `test_app_transaction.py`:133-149 and
`test_app_runtime.py`:172-195 require nested app-header bytes and reject flattening.

The approved correction selects `src/app/local.h` for app and retains `local.h`
for benches. It preserves the existence assertion, adds exact source/staged
header-byte comparison, and asserts app root `local.h` is absent. All32 methods
and every other assertion remain unchanged. Original oracle SHA256
`FC1CA53858D5F55D3D6D08DE5AC766CBF3C6E574811FB7C00E127851625F1CAA` and its first
freeze are committed at `2bdc6eae`; Git provides provenance without another full
snapshot. The author performed no test execution or production-body read during
adjudication/correction. Root owns the revised freeze and unchanged-suite rerun.
