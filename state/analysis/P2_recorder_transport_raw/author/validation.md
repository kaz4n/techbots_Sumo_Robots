# D116 independent author validation

PASS cumulatively against the unchanged first production freeze. This is reused
independent author context with earlier D104 runner knowledge, not a fresh model
or repository context. D116 expectations came from adopted public contracts and
headers plus established test fixtures. No production body was read. All test
expectations were frozen before the first production execution.

- Actual Pipeline normal and ASan/UBSan: **22 cases, 4,202,902 assertions each**.
- Actual native factory and default sketch, counted public owner: two binaries
  passed normal/sanitized; startup/default loops made no clock or I/O callback.
- Six non-inert compile refusals and eight checked compile policy methods passed.
- Five runtime CONFIG profiles: one case / 224 assertions each; two upstream
  zero-configuration compile refusals passed reason-specific diagnostics.
- Four complete strict receiver/publication/validator roundtrips and two
  truncated-prefix refusals passed. Every frame/status/event/summary value was
  independently encoded from retained public source bytes and compared.

The actual full attempt retained 5,001 OK frames and eight events, with 200,002
observed results, 194,901 zero-cost fixture timing receipts, no loss, and the
actual reset/menu/request lifecycle. Full and partial/PENDING sinks emitted the
same 532,562-byte stream: 5,015 lines, 10,027 payload chunks, CRC32 1022767091,
SHA256 `420b4657c0a13d813ca66e29d6217c406de4d13befd8f7584b625724e9dfdfef`.
Its 36 summary values, all source bytes, command receipts and exact source hashes
are retained in `run1_commands/` and `first_run_analysis.json`.

The one-byte-per-decision sink reached existing TOTAL after exactly 300,000
acknowledged bytes/calls, retaining all 5,001 source frames. Its bytes equal the
complete stream's first 300,000 bytes. Modeling the declared 15-byte native
packet overhead yields 682,967 wire bytes for the full stream, requiring average
progress above 2.27656 wire bytes per 1ms decision over 300 seconds. This is
protocol accounting and controlled host behavior, not native UART throughput.

The first run retained three fixture failures: existing countdown assertions
reject zero debounce, zero long duration, and MODE_SHORT_MS600 > long24 before
Runner execution. Root/reviewer approved the exact `fixture1.diff`: preserve the
two zero profiles as explicit static refusals and use copied debounce596/long600
for the runtime G==long boundary. The previous claim naming BOTH_STOP_MS was
corrected to MODE_SHORT_MS in `fixture1_proposal.json`. No production or C++/
receiver/native/policy assertions changed. `run2_config` reran only the affected
method and passed; all other first-run successes remain the relevant evidence.

Exact commands, counts and hashes are in `validation.json`. The first freeze is
`first_test_freeze.json`; the only amended file is the Python harness, now
`0fab202af4559143335489b1ade502d94925031d5a32a7a85e2eb78aec3a121e`.
Main C++ remains `7ecd1cdd58d516826508a85318fe6c90bb2483ae1a68e30b56a6e4991dbda792`;
policy remains `f933345e18cbf4eebe78eee4cbf288c11321a1ad9d1f481dfa64584406491557`.

No board action, sensor acquisition, motor energizing, native-throughput
qualification, hardware acceptance or phase gate follows. Counter saturation
and 64-bit token exhaustion were not seeded or claimed executed. Zero-debounce/
zero-long runtime guards are unreachable behind unchanged upstream static
assertions and remain source-review limits. Independent source/target review
and coordinator integration are separate evidence.
