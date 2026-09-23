# Established controlled transport fixture adaptation

2026-09-23. Objective: extend the existing isolated SSH/ADB command protocol for
D099 while preserving every established assertion and test method.

Modified files:
- `tests/tooling/fake_command.py`: exact pinned plain CLI version response;
  independently constructed successful app JSON from documented core properties
  and compile argv; read-only synthetic GNU `sha256sum --` responses. The selected
  18 dependency identities come from the copied `tools/app_build_pins.json` data.
  Synthetic artifact digests explicitly do not establish real files or builds.
  Ordinary compile/upload responses and FAKE_FAIL exit43/44 remain unchanged.
- `tests/tooling/test_tools.py`: add `sha256sum` to isolated remote command copies.
- `tests/tooling/test_adb_transport.py`: dispatch the documented flash-mode hash
  command to the helper. No test or assertion changed.

Verification: WSL Ubuntu command `python3 -m unittest -v tests.tooling.test_tools
tests.tooling.test_adb_transport` passed all49 tests in58.926s, exit0. Exact outputs
are `established.stdout.txt`, `established.stderr.txt`, `established.exit.txt`.
`assertion_integrity.json` compares parsed working-tree assertions and complete
test methods against HEAD: all unchanged (25SSH methods,24ADB methods).
Scoped `git diff --check` passed. No test failures occurred in this run.

These are host fixture checks only. No real SSH/ADB target, installed dependency
file, MCU, upload, reset or motor action was used. Synthetic hashes cannot prove
target artifacts or dependency bytes. Separate independent new D099 tests and
real compile evidence remain the owning agents' work.
