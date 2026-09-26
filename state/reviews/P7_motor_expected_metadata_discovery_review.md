# D202 test-discovery documentation addendum

26 September 2026. Bounded documentation review only. The reviewer read the
changed documentation and command source but invoked no test, compiler,
production/tool module or device operation. Only this new addendum was written.
The completed source/evidence review remains untouched: 12702 bytes, SHA256
`f7b8a116464ac0590aa93dc19a66db0d4f4cebe4eed717a5a4f67780c75021ae`.

## Findings and disposition

**PASS; no open material documentation finding.** The README command now uses
`python3 -B -m unittest discover -s tests/tooling -v`. Its adjacent explanation
clearly states that broad discovery is not a wholly passing single-command
suite: it still includes D197's recorded symbol-equality failure, and newer
oracles need fresh evidence directories. It does not hide or exclude an
assertion. Adding -B addresses the bytecode setting without claiming to satisfy
every individual oracle's platform or evidence-owner prerequisites.

The separate `tools/test_host.sh` path configures/builds with CMake and runs
CTest; it does not perform Python unittest discovery. The README and validation
record distinguish that path from the scoped D202 commands and point to the
actual saved evidence. The validation record identifies its corrected command
and explicitly marks metadata_corrected_linux02 consumed. Documentation is a
record of those results, not permission to repeat that owner.

Two minor wording findings were reported and corrected by the coordinator:

- README now identifies the observed removals precisely as two read-only
  metadata symbols and one local helper symbol, consistent with the preserved
  DOMAINS/SELECTORS/candidateRate diff.
- Handoff now describes the serial D202/D197/locked executions as completed,
  retained and reviewed. Its obsolete imperative to run those checks was
  removed, preserving the refusal to reuse historical owners.

The validation record and handoff both preserve historical D197 FAIL, scoped
D202 host PASS and pending target evidence as separate statements. This
addendum introduces no source waiver, test exclusion, new execution result or
target authorization.

## Reviewed document pins

| Document | Bytes | SHA256 |
|---|---:|---|
| `tools/README.md` | 29281 | `ab701831387667d549295b5c8e426e5d930cff916f98bf45968143470b3c7c3f` |
| `state/CODEX_HANDOFF.md` | 7769 | `1442fec410fa27abe8c673d07950de180c863d137b5f551f2f4330361c71d542` |
| `state/analysis/P7_motor_expected_metadata_validation.md` | 6791 | `e3f0bb9b8ef20794448875ead24e2967f5ce13f07ee05a0495f35d12c6d64043` |
