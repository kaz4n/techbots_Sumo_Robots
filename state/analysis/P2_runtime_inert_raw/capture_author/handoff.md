# Independent D104 decoder test handoff

Scope: pure `decode_diagnostics` contract and public 232-byte ABI. The author
read the frozen capture contract, public C++ header and existing D091 test style,
but did not inspect `tools/runtime_capture.py`. The author previously implemented
the C++ Runner; this is independence from the Python implementation, not a fresh
C++ review. All fixtures are synthetic local bytes and mocked external actions.

`tests/tooling/test_runtime_capture.py` was frozen before first import/run:
SHA-256 18f9350fc1abd99e5ac31601ca4a5d1cc666844a1206d2382a194dbd7abfc169.
There are 24 unittest methods with parameterized boundary cases. They cover exact
immutable bytes/length/endian, ABI fields, schema/reserved words, terminal/failure
pairs, every enum/mask/boolean domain, ordered and deduplicated acceptance reasons,
epoch/token/setup/write counters including multiplication overflow, all clock
ordering/half-range/window/maxima rules and natural wrap, stack SRAM/alignment/
range/headroom/saturation boundaries, partial FAILED reports, passive import and
pure repeatable decoding without I/O. No assertion was changed after the freeze.

First opaque run passed all 24 methods. `run1.txt` retains stdout/stderr;
`run1.json` records command, time, exit0, frozen test hash and actual implementation
hash. There was no failing run and no oracle correction. Syntax compilation and
git diff --check passed for the test file.

This suite does not inspect or validate live transport commands, artifact pins,
read budgets, deployment identity, upload guards or hardware. The coordinator
and separate reviewer own those prerequisites. No board command, upload, commit
or physical acceptance was performed by this author.
