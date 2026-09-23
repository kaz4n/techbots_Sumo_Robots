# D102 independent author evidence

2026-09-23. Objective: independently test the frozen D102 public read/bytesAt and
lossless packed-status contract while preserving B15 cadence, capacity and losses.
The author read contracts/public headers and never opened implementation `.cpp`.
Compilation consumes source opaquely; exact input snapshots are retained below.
Oracle state is a host-only deque of ordinary StoredFrame values with independent
insertion/eviction/count accounting, not packed lanes or private storage hooks.

Owned edits: `tests/test_frame_packing.cpp` and this `author/` directory only.
No existing tests, locked tests, production/config source, board operation or
commit was changed/performed by this author.

## Results

`current_source/normal.log` and `current_source/sanitizer.log`: both PASS,
11 cases and 20,513,379 assertions each, with no skipped case. Normal and
ASan+UBSan compilation/runtime exits are all zero. ASan leak detection and
abort-on-error, UBSan halt-on-error/stacktrace were enabled. Binaries ran under
WSL Ubuntu in `/dev/shm`, with C++17, no exceptions/RTTI and warnings-as-errors.

Actual host ABI: FrameBuffer sizeof=126312, alignof=8; StoredFrame sizeof=26,
alignof=1; size_t sizeof=8. The frozen header reported FrameBuffer sizeof=130064.
The test upper bound is 125025 payload bytes + 1251 packed status bytes + a
bounded portable allowance for two size_t indices, four uint32 counters and
alignment gaps. It does not assume one exact host/target ABI. Cadence remains
25 Hz, capacity 5001, window 200000 ms and event capacity 4096.

Final test SHA-256:
`35b648f9acd38defbb24819bff62796ee5f1d0b734c0055a5396ef208520d21a`.
Tested implementation SHA-256:
`5f65157fe2c1ae699dfb041b08c271eef959c0d9664f3c6b98421403d57270dc`.
Tested header SHA-256:
`093ef637e29f3f84d685d12842eeb1a0540a21646cb42a9dbfa005a734113d53`.
Every remaining source hash, exact compiler/executable command, cwd, environment
and exit is recorded in each run's `receipt.json` with its immutable source tree.

## Coverage

- All three accepted status values in every lane, adjacent mixed statuses,
  repeated full-capacity replacements through OK/CLAMPED/INVALID/OK.
- Slots 3/4, capacity-1/capacity/capacity+1, final partial status byte and wrap.
- Fixed-seed mixed accepted/rejected/borrowed-input deque oracle spanning more
  than five full eviction wraps; exact 25-byte checks and original status.
- Repeated logical reset/reuse after all status values and losses.
- Every unknown code 3..255 at empty, partial, full and already-wrapped sizes;
  every retained output and all lifetime counters checked after each rejection.
- Outside-size, SIZE_MAX and SIZE_MAX-1 failures preserve both payload/status.
- Multiple caller snapshots survive other reads, two wraps, reset and destruction.
- Every simultaneously retained payload pointer survives all other reads;
  oldest/interior/newest genuine borrowed inputs append before/after full/wrap.
- Representation bound, DTO identity, noncopyable owner, cadence/capacity invariants.

## Preserved failures and exact launch commands

From PowerShell repository cwd:

```text
wsl.exe -d Ubuntu -- python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_frame_packing_raw/author/run.py frozen_contract --revision f6f65fc
wsl.exe -d Ubuntu -- python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_frame_packing_raw/author/run.py frozen_contract_corrected_asserts --revision f6f65fc
wsl.exe -d Ubuntu -- python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_frame_packing_raw/author/run.py current_source
```

The first frozen run preserved an author harness failure: REQUIRE assertions
are unavailable under the repository's DOCTEST_CONFIG_NO_EXCEPTIONS setting.
Only the new file was corrected to CHECK plus explicit guards; predicates remain.
The corrected frozen run compiles the same final tests and fails solely at the
expected stale `FrameBuffer::at` implementation versus frozen replacement header.
Both normal/sanitizer compiler failures are retained, not overwritten. Runner
itself returns zero after writing all receipts even if a nested compile fails;
the nested command exit codes are authoritative.

No spec ambiguity was found: D102 explicitly supersedes D069 read/representation
clauses while retaining original ordering, loss, saturation and reset policy.
No target ABI, actual loading/free RAM, WCET, physical B8, no-heap source audit or
human gate is established by these host tests. Parent/reviewer own those checks,
existing-fixture migration, full regression and integration evidence.

Next action: consume the frozen final test file in parent full regression and
review the final target/lifecycle evidence without changing these expectations.
