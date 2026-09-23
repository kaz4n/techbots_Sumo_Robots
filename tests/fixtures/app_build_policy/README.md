# Independent D099 fixtures

`valid_result.json` is a synthetic minimal successful compile envelope, derived
from `state/analysis/P2_app_build_contract.md` and the CLI1.5.1 schema follow-up
in `P2_bridge_dependency_audit.md`. It is not output from a board or a compiler.
The empty library list is deliberately omitted, matching the pinned CLI's
`omitempty` serialization. Link, variant and boot property names/values come
from the previously captured installed core `boards.txt` and `platform.txt`.

The test author did not read `tools/board_tool.py` or `tools/app_build_policy.py`.
Only their public command/validator contracts and existing transport-fixture
interfaces inform the tests. Shared transport fixtures are implementation-independent
test infrastructure; their D099 protocol adaptation is tracked separately.

`fault_command.py` wraps only the documented synthetic command helper to inject
CLI, compile-result, process-exit, pin and artifact faults. Its commands never
reach a real transport. SHA mutations select rows by fixture path rather than
assuming separate hash calls for pins and artifacts.

`SumoPolicyFixture/` and `phase_probe/` provide an unconditional external include
with phase-independent contents. They have not been compiled on the board by
the author. The future compile-only experiment must use a temporary library
search path (not install a library), compare both discovery settings, retain the
actual CLI library arrays, and demonstrate validator rejection of the nonempty
array. No upload or runtime action belongs to this fixture.
