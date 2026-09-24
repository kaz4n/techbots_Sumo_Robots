# Independent static capture contract tests

Authored from `../P7_static_capture_contract.md`, `AGENTS.md`,
`.claude/agents/test-author.md`, and the public enum/report declarations in
`src/app/runtime.h` and `src/app/transaction.h`. No implementation `.cpp` or
`.py` source was read, imported, or executed. No board calls were made.

The coordinator clarified exact built-in scalar types, list/tuple container
semantics, phase-FAULT priority with numeric fault zero, and lowercase raw hex;
these are explicit in the contract version used. No unresolved ambiguity remains.

Frozen before first implementation execution:

- Contract SHA256: `ee1bb8d4acd969fa16330f2e7a55bf26daac71a6dbe4f6922c730f46bcb96fc3`.
- `test_static_capture.py` SHA256: `bcb6300574e55bd18c224ed916208239264b5452bbccd1fb14a228606b84a02d`.
- 37 test methods, with parameterized subtests covering the exact 18-read plan,
  argument rejection, every flash chunk endpoint and mismatch combination,
  both decoded prefix layouts, all declared enums/flag boundaries, error order,
  priority, counter wrap/half-range boundaries, and input/result independence.
- Fixture bytes are constructed in memory; no external dependencies or fixture files.
- Python `-B` AST parsing of this test file passed. This checks syntax only;
  the implementation has not been executed and no passing test result is claimed.

After the coordinator accepts the freeze, run:

```text
python -B state/analysis/P7_static_startup_raw/test_static_capture.py -v
```

The suite establishes only host contract behavior. It cannot establish native
origin, a common live attempt, atomicity, physical outputs, RAM/WCET or a gate.
