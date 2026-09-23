# D080 MPU6050 setup and coherent decoder review

2026-09-23 Asia/Dubai. Fresh, separate, same-model read-only software review.
The reviewer did not author the contract, implementation or specification tests.
Baseline `70b52c5`; initial contract `00f96ee`, including the explicit later
response-precedence clarification. Review ownership is this report and
`P2_imu_setup_raw/` only. No board connection, MCU operation, reset, upload or
register operation was performed by this reviewer.

## Findings

No open BLOCKER, MAJOR or MINOR in the bounded D080 software scope.

The draft probe comment referenced independent startup counters before those
tests existed. The author added actual-probe startup and upload-refusal tests;
the reviewer inspected and independently reproduced them. No production change
was needed. This closes an evidence gap, not a discovered sensor-driver defect.

The author's first focused compile failed because ordinary REQUIRE is disabled
by the established no-exceptions policy. Its receipt is retained in the author
evidence. Only new-test guards changed to CHECK followed by abort on failure,
preserving their predicates and preventing an invalid fixture from continuing.
The reviewer separately preserved a PowerShell parsing failure for an unquoted
comma in a sanitizer argument; quoting that argument fixed invocation only.

## Reviewed source and contract

- Actual `src/hal/imu.cpp` SHA256:
  `f38f0f2116f77534a9c812acd925c574d009fff8c3a521dd6af3c255f49e8a37`.
  Final header, config, tests, fake Bus and CMake hashes are recorded in
  `P2_imu_setup_raw/final_receipt_summary.json`.
- Independently counted all 48 operations and traced the exact reset/profile
  recipe, each full-byte readback, the selected successful-write wait anchors,
  one Bus operation per advance, exclusive deadline, saturating call limits,
  failure precedence and irreversible terminal states. Reset defaults match
  the retained manufacturer RM Rev4.0 pages 8 and 42. Full-byte rejection is an
  explicitly selected conservative policy, not a revision-independent claim
  about reserved silicon bits.
- Decoder layout, signed-word conversion, fixed scales, rail bits and complete
  failure zeroing agree with the contract. Bit 0 remains diagnostic; neither
  bit value establishes a new payload generation. Bus observation timestamps
  are not physical sample timestamps.
- No new motor write, remote motion path, clock read, retry, busy wait,
  allocation, unbounded loop or app integration. The 12 checked production
  functions have at most 32 lines. Core, app, existing locked tests and board
  wrapper have no diff from the baseline. Config adds only the 12 D080 constants;
  existing declarations and original behavior defaults are preserved.

## Independently reproduced checks

- Final normal and ASan/UBSan focused builds both pass: 26 D080 cases and
  1,562,374 assertions each, zero failures. One unrelated scaffold case is
  excluded by the explicit D080 filter. Exact commands, status, output hashes
  and before/after source identities are in `final_focused_build/run` and
  `final_sanitize_build/run` JSON/TXT receipts. The source set stayed unchanged
  during each run. Earlier 23-case receipts remain separately retained.
- Coverage includes all 65,536 signed patterns in every motion position,
  independent axis placement, each rail bit, all status-byte values, malformed
  counts, every transport status, every setup readback bit, completion-anchored
  waits, 599us acceptance, 600us rejection, wrap/backward time, every-stage
  deadline equality, final-completion deadline and terminal no-I/O behavior.
- Eight configuration/cap methods pass in 33.456s: 44 separately compiled
  variants, 201,164 executable assertions, 88 compiler/executable receipts,
  all exit 0. These use UBSan and test unsupported profiles, invalid bounds,
  maximum count values, frozen time, exact final allowed advances/requests,
  and decoder independence from setup-only bounds. See `variants.json`,
  `variants.txt`, `variants/` and the receipt summary.
- The two subsequently added probe methods pass independently in 0.752s.
  Actual .ino, probe and Setup sources run with a primitive zero-initialized
  bus-call counter that is never reset. Construction, setup and 10,000 loops
  make zero calls in both MATCH/MOTORS_ALLOWED 0/0 and 1/1 host builds.
  The retained entry is checked without invoking it. All eight upload-mode
  combinations reject before target, remote or transport lookup. Four separate
  compiler/executable receipts are in `probe/`; parent output is `probe_run`.
  These are host and wrapper checks, not MCU execution.
- The strict config suite passes all 13 methods, including original B16 equality
  and the new fixed D080 declarations. The ten D080 tooling methods above ran
  as eight existing methods plus two newly added methods, not one ten-method
  invocation. Parent full-regression and broader-tooling results belong to the
  separate validation ledger; this review does not invent a broad-suite pass.

## Actual compile-only source and ELF boundary

The actual board-Linux compile receipt exits 0, reporting 84,132 program bytes
and 34,748 compiler global-memory bytes. This is not measured runtime headroom.
Source identity:
`c45ffd3dda53de8b8fbf6c8008fc939362ca2024aedcb4cd23e4c55ce138cd41`.
The reviewer independently reconstructed all 44 staged files from local bytes
without modifying staging and matched the complete remote source map. The
three ELF identities and exact input-receipt hash are bound in `identity_audit.json`.

The final ELF retains Setup start/advance, decode and native Bus operations.
All 36 collected native bindings are nonzero, and the base ELF hash equals the
previous D079 receipt. Setup at 0x6c only stores the unused exercise pointer;
loop at 0x7c returns. Relocations bind those stores to entry/exercise. The new
probe constructor at 0x2490 writes Setup/reference and inherited RouterBridge
HCI memory; its only call resolves to memset through relocation 0x24e0. There
is no new imu.cpp initializer. Retained exercise calls are outside startup.
See `target_disassembly.txt` and the linked root target receipt. Existing
Bridge/Serial/library initializers and loop-hook behavior remain F091 limits.

## Exact existing inert-source replacements

Approved only after source and actual target-startup review; root's adopted
manifest matches all five values exactly. No key was added, and no upload or
runtime permission follows. Full constituent maps are in `identity_audit.json`;
the scoped approval is retained in `inert_approval.json`.

| Existing key | Reviewed SHA256 |
|---|---|
| `bench/p0_matrix` | `0aa2bd6a9b9f295fc70495aebdce528ad772dcb14d442a963e08a7361df644ba` |
| `bench/p0_timing` | `2e5ab081c622e080413835a1fe82e8d6703fa343fdb181e07e9dc256b8d79267` |
| `bench/p0_adc` | `ab34426472be4d6fcba2d9c46933d8326d0d87eb89d4e43332a7eb51b85889f7` |
| `bench/p0_gpio` | `ade5f8b47324e86a908dc3213ed3e3c46153564c359e31df05ceefd8c812a3d2` |
| `bench/p0_qtr` | `829ad2ba8c22d1341d0033a9f04b3969ab39a50453cb97373dcea3b66693de07` |

## Verdict

PASS for D080 finite setup, coherent sensor-coordinate decoding and the inert
compile-only boundary. SC-AJ clock qualification and F091 inherited runtime
paths remain global integration/deployment blockers. Physical identity, power,
address, pull-ups, settling, accepted sample rate/freshness, mounting, calibration,
yaw and full-tick WCET remain unqualified or unfinished. No physical B3 success,
application integration, PINMAP/EXPLAINED record, human phase gate or motor-run
authority follows.

Next action: parent records this bounded result with its full regression/tooling
receipts and continues the separately specified acquisition/freshness and later
bias/axis/yaw work. Two independent 600us transport allowances must not be
represented as an 800us complete control tick.
