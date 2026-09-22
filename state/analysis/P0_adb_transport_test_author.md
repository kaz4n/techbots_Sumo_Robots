# P0 independent ADB transport test author

Date: 2026-09-22, Asia/Dubai.

Objective: verify the supplied public ADB transport addition without reading
`tools/board_tool.py`. Owned files are `tests/tooling/test_adb_transport.py` and
this report. Existing tooling tests, their command substitute and public tooling
documentation supplied conventions. Production tools and reviewed inert sources
were copied as opaque fixtures; no implementation was inspected, existing tests
or ledgers were edited, or commits made.

Twenty-four independent cases cover:

- Explicit validated device serial, one non-PTY quoted remote command, optional
  executable name/path, paths containing spaces and no automatic device discovery.
- Default/explicit SSH behavior and strict host/authentication options; ADB works
  with an isolated local PATH containing no SSH or rsync.
- Preflight JSON preserves the exact serial, transport, checks, statuses, output
  and limitations. Exit 1/124/255 stops further ADB inventory queries; a missing
  remote utility with exit 127 remains recorded while other queries continue.
- Missing/invalid transport, serial, executable and dedicated absolute remote
  root fail locally. Root validation includes '/', '//' and '///', rejects root
  spaces/metacharacters and retains the existing strict root contract.
- Compile-only argument permutations, MATCH/default motor macros, startup
  selection, core 1.0.0 pin and distinct build artifacts. No compile-only path
  uploads, starts, resets, reboots or opens Monitor.
- Every staged regular file is pushed exactly once to its exact remote filename;
  sketch-local/config/core/HAL include files and local filenames with spaces are
  preserved byte-for-byte. Stable content reuses its address; changed content
  gets a different address without deleting the prior fixture directory.
- Reviewed default inert uploads follow successful compile and use its artifact;
  source hashes, allowlist, MATCH and Immediate-matrix restrictions remain enforced.
  Push/compile/transport/core errors cannot proceed to later unauthorized stages.
- Logs execute the real generated receive-only Monitor request under the existing
  socket substitute, accept no keyboard input and report disconnect as failure.
  A synthetic private environment sentinel is absent from stdout/stderr.

Authorized isolated execution:

```text
wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -p test_adb_transport.py -v
Ran 24 tests in 21.510s
OK
Process exit: 0
```

The tests' local PATH admits only their fake ADB executable and required local
Python/dirname helpers. Remote commands are parsed against a bounded substitute
allowlist; pushes copy solely inside the temporary fixture, and the CLI is fake.
No actual ADB server, board, SSH service, compiler/upload device or Monitor was
contacted. Passing results prove controlled script behavior, not installed ADB,
USB/device permissions, board compilation, physical isolation, motor authority
or a P0 gate. Coordinator/reviewer own full-suite validation and hardware evidence.

Test code frozen immediately after this passing run; the coordinator was told
its concurrent discovery already used the final file. Next action: independent
review, full tooling receipt, then separately authorized bare-board validation.
