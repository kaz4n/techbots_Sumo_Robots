# D136 extra-declaration admission regression draft

Scope: independently test the adopted D136 historical-config requirements that
all seven reserved names have unique supported unconditional declarations and
that unsupported declaration spelling is rejected. Ordinary unconditional reads
in other declarations remain allowed. This is a source-admission test, not a
claim that the supplied C++ is valid or invalid firmware.

`test_opener_abort_declarations.py` contains eight unittest methods. It reuses
the existing public `tests/tooling/opener_abort_fixture.py` API without changing
that helper or any frozen public/private source. Expectations come from the
adopted `P5_abort_analysis_contract.md` source-binding section. The author has
not read `tools/analyze_opener_abort.py`, imported tests, or executed anything.

The negative matrix covers all seven names with direct initialization, direct
list initialization and copy-list initialization, both before and after the
canonical declaration and both in the same and a separate namespace. Separate
cases cover clear scalar declarations with alternate types, const references,
arrays, and a later variable in a multiple-declarator statement. A differently
initialized declaration cannot satisfy the required canonical declaration by
itself. The extra declaration is rejected even if its value equals the valid
declaration; the unsupported spelling and ambiguity, not a numeric disagreement,
are the reason to refuse configuration binding.

Positive controls use the same reserved names only as read operands in scalar
direct/list initialization, references, arrays and derived arithmetic, including
qualified reads from another namespace. Declaration-shaped comments and quoted
text remain ignored. No type-alias, template, function-pointer or general C++
compiler/parser policy is added to this bounded test task.

Every source rejection requires input VALID, evidence/source binding INVALID,
timing NOT_QUALIFIED, error UNSUPPORTED_CONFIGURATION, unpublished config values,
zero qualification counts and null extrema. One full two-attempt cohort requires
both unchanged CSV validator reports to remain PASS while every decoded field is
withheld under invalid source binding. It verifies that rejection cannot skip
bundle validation or produce timing from an unknown configuration.

Planned command, only after root freezes these files and authorizes execution:

`python3 -B -m unittest discover -s state/analysis/P5_abort_analysis_declarations -p 'test_opener_abort_declarations.py' -v`

All fixtures are temporary synthetic data during that future run. Preparation
creates no binaries, board/network actions or large artifacts. Existing public
and private suites and their evidence remain unchanged. The accompanying freeze
records the exact contract, reused fixture and new artifact hashes before any
execution. No passing result is claimed by this draft.
