# D154 upload implementation review

25 September 2026, Asia/Dubai. Separate same-model review sharing the earlier
design-review context; not cross-model review, native authorization or a phase
gate. Reviewer owns this note and the supplemental tests; no native execution.

Initial reviewed source:

- `analysis/P7_static_startup_raw/upload_remote.py`, SHA256
  `68ea5ee9e53ec6c4667a3dbf554ca95a4cdbb290b02f6736b4d1d1a462e82bf5`.
- Contract SHA256
  `7fa1c0f0a48793272994a96bed9871d4f515d3b9423f546eed0054f3e9325635`.
- Bindings SHA256
  `a31bca78bb619271e63a321173a68fca072e48bb22111ee20fc9f8c20d5e18fc`.

**Initial disposition: R1 open from source inspection before test receipts.**

R1 **MAJOR** - Preserve wait-error outcome before stream context unwinding.
Original `upload_remote.py:322`, `:332`, `:365-366`: execute calls
D153 wait_child inside the stdout/stderr context managers. A wait/kill/reap
exception can carry its known subprocess_result. If a stream close then raises
another exception, run receives that replacement and checks only the replacement
for subprocess_result. remember follows its context to retain the original
first_error, but the known process flags are lost and subprocess remains None.
This conflicts with preserving process flags when later work fails. Retain the
attached strictly typed outcome immediately around wait_child, before leaving
the stream contexts, then re-raise unchanged. Validate the nested wait-error plus
stream-close-error case with controlled substitutes after an independent freeze.

Otherwise the inspected source preserves fixed paths/argv/environment, strict
binding types, descriptor-bound no-symlink reads, consumed exclusive output,
durable claim before command, late pre-Popen timeout calculation, D153 process
limits, independent postchecks, original-fd failure receipts and no automatic
capture. The 180-second overall budget and 120-second child maximum are explicit.
These are source-review observations, not passed execution evidence.

R2 **MAJOR** - Preserve the process helper's outward error. Original
`upload_remote.py:129` traverses generic exception context back into an already
handled TimeoutExpired, replacing the outward kill failure selected by D153.
Frozen `test_upload_remote.py:721` and `:728` exposed this: original
`upload_first.json` records **53/55 PASS, two FAIL**, exit1, input pins unchanged.
The original negative receipt remains evidence; no oracle or support repair.

Repair1 source SHA256
`81668c798fdb53d9f81083977f098d36f873003041e55720a6170b9c7cf2cf08`:
reviewed the complete diff against preserved commit `4727ee2b`. The narrow
change adds an explicit process-error boundary (`:130-147`), retains the
strictly typed attached outcome (`:326-330`) before stream unwinding
(`:338-346`), and handles the injected executor boundary (`:377-381`).
Frozen contract, binding, descriptor helper, D153 support and public tests are
unchanged. `upload_repair1.json` records **55/55 PASS**, exit0, 3.685s and input
pins unchanged; its freeze links the reviewed source and original freeze.

Reviewer supplement `upload_private.py` was authored **after code inspection**,
using the unchanged public fixture. It is not an independent spec-only oracle.
Frozen before execution, SHA256
`ed0026a92a8f070b30f8a760415a9b72ab2543c5ad04d49dda06b24699af518b`.
Its three cases combine a later stream-close error with a kill failure/reaped
outcome, a wait failure/unknown outcome, and a known success. Assertions require
the original process flags, primary error, extra close failure where applicable,
one attempt, persisted FAILED receipt and independently recovered streams.
`upload_private_first.json` records **3/3 PASS**, exit0, 0.205s, all input pins
unchanged. Verified its freeze hash `2de81eef9d56ae28b53bb0943756cbe69a28ef74ef04c56f4f253507720e67df`,
pre-execution freeze timestamp, exact command and all eight current input pins.
**Final disposition: PASS for scoped D154 host implementation; R1 and R2
resolved by reviewed repair1 plus the unchanged 55 public and three reviewer
tests. No open material finding in this scope.** Processes are mocked and
fixtures synthetic; this is not real CLI/upload, MCU, transport, timing,
runtime-purity, quiescence or hardware acceptance evidence.

The separate CLI prerequisite follow-up is documented in
`analysis/P7_static_cli_initialization.md`. It does not qualify execution or
replace the future reviewed source/HEAD/D144/run admission and fresh rechecks.
