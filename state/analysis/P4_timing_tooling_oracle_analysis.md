<!-- Records adjudication of one new, unaccepted D129 tooling oracle failure. -->
<!-- Preserves the original failure while removing an unsupported syntax constraint. -->
<!-- The replacement tests actual compiler rejection before any author-side execution. -->
# D129 wrapper guard oracle adjudication

2026-09-24. The first completed tooling run reported 148/149 methods passing.
The sole failure was the new
`test_wrapper_binds_actual_sources_empty_grants_and_all_four_compile_conditions`
at `tests/tooling/test_reactive_timing.py:204`. Root preserved its original
`tooling.txt`/`tooling.json` receipt and original oracle bytes separately.

Original test SHA256:
`178ae1a10e9e8850b7967c495776538c477b42423ad4a708f47e65f85cbf9bf7`.

## Finding and independent disposition

The adopted D129 contract requires the exact inert compiler-wide timing/reactive
profile and rejection of incompatible builds. It does not require a `#if` with
`#error` implementation. The new test accidentally required that spelling.

Root explicitly authorized inspection of the wrapper `.ino` to resolve this
oracle issue. That inspection found a C++ `static_assert` enforcing timing1,
reactive1, MATCH0, MOTORS_ALLOWED0, and exclusion of the four earlier motion
profiles. No production `.cpp` body or analyzer implementation was read.

The author recommended replacing the spelling check with direct syntax-only
compilation. A separate reviewer independently agreed, and root approved this
bounded correction to the new, unaccepted tooling draft. This does not change
the safety contract, production code or any established/locked assertion.

## Exact correction and retained expectations

The test retains the original native source, UnoQPort and Runtime binding
assertions, empty grants, `runtime.step()`, no local profile-macro overrides,
and every build-policy/refusal assertion. Only the `#if`/`#error` spelling
inspection is replaced; the tooling suite retains the same 14 named D129 methods
and original 149-method aggregate coverage.

The replacement copies exact wrapper bytes to a temporary translation unit and
provides declaration-only typed stub dependency headers. It uses `g++` with
C++17, warnings-as-errors and `-fsyntax-only`; nothing links or executes. The
exact intended profile must compile. Each of the eight profile macro values is
then independently replaced with its opposite0/1 value and with2, and every one
of those 16 invalid profiles must fail compilation. Stubs contain no profile
checks, ensuring rejection comes from the actual wrapper guard. A missing
compiler is an explicit test prerequisite failure, never a skipped check.

The corrected test hash and this analysis hash are frozen and returned to root
before any author-side compiler/test execution. Root will retain the replacement
oracle separately and run the revised suite. At this writing the author has
performed no test, compiler, WSL or hardware execution for this correction.
