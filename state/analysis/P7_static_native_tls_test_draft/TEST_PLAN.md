# Independent D147 native TLS host-test plan

Author read the public D147 and D142 contracts, public D142 synthetic fixture and
test files, AGENTS.md, and the exact 977-byte public generated assembly fixture.
Author did not read either validator implementation or any collector body and
did not use a target ELF as an oracle. The original D142 files are unchanged.

`synthetic_native_elf.py` adds explicit symbol tuples by rebuilding synthetic
string/symbol tables in RAM. It imports the unchanged public fixture builder.
`test_static_native_artifacts.py` builds exact report expectations from the
contract. The legacy implementation bytes are opaque inputs read only when the
coordinator runs the frozen suite; tests never extract expectations from them.

Coverage: all six names and all three images; every symbol tuple field, missing,
renamed, anonymous, extra and duplicate aliases; non-TLS global/local shadows;
correct local-partition mutations; alias reordering and debug/map differences;
full exact report and original artifact hashes; source type/size/hash rejection
before execution; source and seven-artifact bounds; invalid argument arity;
immutability on success/failure and detached results; original parser rejection
before/after extension calls and imported-module identity preservation; retained
ELF bounds, forbidden TLS storage/relocations, normalized allocations including
empty sections, entry metadata, copy/zero boundaries, raw BIN and both packages.

Source byte limits are exercised using small buffers, and one transient 16 MiB
buffer exercises the unchanged artifact bounds. No files/builds/target runs are
created by fixtures. Run Python with `-B` to prevent bytecode caches.

The freeze manifest binds this plan, new suite/fixture, both public contracts,
unchanged public test support/fixture, and exact assembly fixture. It excludes
new implementation bytes deliberately, preserving implementation-independent
expectations. The frozen D142 implementation hash is fixed in the test contract.

Coordinator executes first and preserves any first failure without rewriting
the expectation oracle. No board collection, compile, upload, reset or gate is
authorized by this suite.

Command from repository root:

```powershell
python -B -m unittest discover -s state/analysis/P7_static_native_tls_test_draft -p 'test_static_native_artifacts.py' -v
```
