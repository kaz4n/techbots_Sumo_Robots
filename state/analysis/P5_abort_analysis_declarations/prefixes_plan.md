# D136 parenthesized and prefixed declaration follow-up

Seven new spec-only methods in `test_opener_abort_declarator_prefixes.py` extend the
independent declaration-uniqueness coverage. The prior eight-method file, its
freeze, and every established public/private suite remain unchanged. The author
has not read the analyzer implementation or imported/executed these new tests.

The adopted D136 source rule requires each of the seven reserved constants to
have a unique supported declaration. Parentheses around a declarator name and
leading `[[maybe_unused]]`/`alignas(8)` do not turn an extra declaration into an
ordinary read. Negative cases exercise all seven names, same/separate namespaces,
and placement before/after the canonical declaration. They cover parenthesized
copy/direct-list declarations, attributed direct/direct-list declarations, and
aligned copy/direct/direct-list declarations. These source spellings require
UNSUPPORTED_CONFIGURATION, INVALID binding/evidence, no config values, no timing
qualification and no elapsed extrema.

Four positive methods use the reserved constants only as read operands
while declaring a different name, including parenthesized declarators/operands,
leading attributes and alignment specifications, nested function calls, comma
operands and nested initializer lists. Balanced `((NAME))` and `alignas((8))`
are explicit cases; closing an inner initializer brace cannot turn a later read
operand into a declaration. The exact historical values
must still be extracted. This is restricted config admission, not a general C++
parser, compiler-correctness or firmware-validity claim.

The file reuses the prior source-text insertion helper and existing public
synthetic fixture API; it does not inherit the eight earlier test methods or
duplicate their discovery. No tests, producer artifacts, source or shared ledger
are edited. The accompanying new freeze binds the contract and reused helpers
before root's future execution.

Planned command after root authorization:

`python3 -B -m unittest discover -s state/analysis/P5_abort_analysis_declarations -p 'test_opener_abort_declarator_prefixes.py' -v`

Expected discovery is seven methods. The original eight can be run separately or
both new files discovered together, yielding fifteen methods. No new result,
physical trial, compiler run, board access or network action is claimed here.

The prior unexecuted six-method draft and plan are preserved in
`prefixes_pre_nested/`; `prefixes_freeze.json` retains their original hashes.
Root's additional pre-execution request for balanced delimiters and nested reads
produced this seven-method version, frozen separately in
`prefixes_nested_freeze.json`. Neither version has been executed by this author.
