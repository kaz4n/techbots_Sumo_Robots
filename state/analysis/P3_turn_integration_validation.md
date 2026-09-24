# D125 isolated turn-trial integration validation

Implemented, host-tested and target-compiled, 24 September 2026, Asia/Dubai. The implementation
connects D124's finite turn helper to actual Robot/Runtime/Governor/MotorGate in an
exclusive bench profile. No MCU upload/reset or physical turn occurred. Source
contract adoption is `ebe34983`; D124 helper acceptance is `0366d1d7`.

## Independent tests and preserved failures

The separate public author read specifications, public headers and fixtures, not
production implementation bodies. Its initial 28 ordinary cases and one configured
Runtime case were frozen before execution. `P3_turn_integration_raw/freeze_original.json`
binds 137 source/oracle files; `prior_locked.json` binds all 36 established safety
files. The accepted new safety oracle is `7d6c5193`; the original draft and failure
are retained. All 36 prior locked files remain byte-identical.

Initial full normal regression passed all eight targets: main 1,519 cases /
50,427,846 assertions; Gate 187 / 4,536,952; B4 18 cases each M0/M1; D123 27 each;
D125 28 each, with 233,121 M0 / 226,180 M1 assertions. Focused D125 ASan/UBSan
also passed those 28 cases in each build. The -90 config overlay passed both targets.

The initial configured Runtime case failed its setup precondition: immediately
after traversing QTR_CAL to DRIVE_TEST, it requested START while the real classified
line/neutral rearm was still active. Production correctly suppressed that release.
The independent private reviewer found the same fixture precondition separately.
Original public oracle `b90ab55d` and failing configured sanitizer receipts remain
in raw evidence; original private failure remains in review evidence. Correction
must establish actual readiness before requesting START, retaining every safety
assertion. The author added 30 ms of NONE and explicit line/button readiness
preconditions. No previous assertion was removed. All other 136 frozen identities
stayed exact. Corrected configured normal and ASan/UBSan each passed 29 cases,
338,964 M0 / 332,026 M1 assertions, no failures or skips. No production fix or
established locked-test amendment followed.

All four signed angles passed 28 cases per M0/M1. +90 normal/sanitizer and -90 used
the first draft; its only subsequent change is inside the configured-only case.
The +/-180 runs used the amended file. Their normal-build assertions remain the
same; no angle behavior or expectation was relaxed.

The separate same-model reviewer passed four additional cases per M0/M1,
including early START suppression/no replay, twelve edge/deadline combinations,
delayed timeout and full observed braking, and actual completed Runtime to D103
service-only reset with 5,200 inhibited ticks. It independently verified that
default/B4/D123 Robot, Result, Transaction and Runtime object sizes are unchanged.
See [the scoped review](../reviews/P3_turn_integration_review.md); this is separate
from the implementation and public test author, not cross-model or human review.

Controlled tooling passes 107 methods, with unchanged old policy tests. Its first
run had one literal wrapper assertion failure: the equivalent safety predicates
appeared in a different order. Reordering those same predicates fixed the source
check without changing the frozen test or any predicate. Both runs are preserved.
The additive runtime config registry passes both methods; only its receipt output
directory was redirected to this task, avoiding mutation of historical evidence.

## Checked compilation only

Exact commands and installed toolchain checks are in the archived native-app-v1
receipts. Build scripts invoked only `flash ... --compile-only` with MATCH0/M0;
the new profile has no upload allowlist entry. Staged source checks matched all
98 default app files and 99 turn-profile files to this repository.

| Build | Source SHA prefix | ELF SHA prefix | Bytes | Conditional peak / free span |
|---|---|---|---:|---:|
| Default app | 5c7df067 | 21b28ee3 | 176,040 | 262,128 / 16 |
| Turn accuracy | fcf43381 | f41e2cb7 | 155,996 | 250,720 / 11,424 |

Default app ELF, packed sketch and loader exactly match D123 bytes. The turn image
contains the dedicated route and no ordinary routeNormal/checkStall/startOpener
symbols; strong empty loopHook remains. Compiler low-memory warnings are retained.
The conditional loader model is not measured live RAM, stack clearance or WCET.
The historical actual D118 MCU image was not replaced or re-observed here.

Source and locked identities were rechecked after validation. No new full-stack
or physical timing claim follows. P3 turn accuracy and fallback calibration still
require real physical measurements. The current closed-loop duration alone cannot
calibrate fixed-duty fallback: future fallback measurements must use actual IMU
unavailability and externally measured rotation, not fabricated IMU flags.

Next software task: P3 3.3 finite stopping-duty trial. SC-AN records the separate
rest/maximum-excursion and common-reference issue before any speed-cap inference.
