# D128 reactive P4 profile validation

2026-09-24, Asia/Dubai. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED.
Contract/public identity commit `b8ae86b9`; prior accepted software `c58aeae0`.
No physical P4 acceptance, motor-capable upload or human gate is established.

The exclusive P4 profile preserves ordinary local match-menu admission and the
full START hold. Non-edge GO enters actual SEARCH for one observation; later
observations use the existing reactive arbitration, contact, Governor, stall
and re-flank paths. Effective targets at GO brake Search. Openers never run in
this profile. Selected mode remains metadata, and all six modes behave alike.
Default/P3 behavior, source grants, disabled push-through and B16 values remain.

## Verification

The independent author froze 34 public-header/spec cases per M0/M1 build, with
35 for configured buttons, before C++ execution. All passed on first execution.
No production, fixture or assertion correction was needed.

| Executed check | Result |
|---|---|
| Full normal CMake/CTest | 12/12 targets PASS; main1519 and Gate187 cases unchanged |
| New P4 M0/M1 normal and ASan/UBSan | 34 cases; 164726 / 157452 assertions, PASS |
| Synthetic configured-button Runtime, normal and ASan/UBSan | 35 cases; 241856 / 234582 assertions, PASS |
| Build-policy tooling | 135 methods PASS |
| Existing config registry | 2 methods PASS; historical evidence untouched |
| Separate reviewer private M0/M1 | 5 cases; 64487 / 63037 assertions, PASS |
| Prior object layouts | All five prior profiles unchanged; P4 equals default |

Coverage includes six modes times 128 effective masks, exact GO/next-observation
behavior, captured Search timing/heading, centered qualification/contact/caps,
loss braking, real-receipt stall/re-flank/ALL_IN, complete escapes, full hold and
wrap, source/receipt failures, duplicates and permanent service-only inhibition.

All 38 prior locked sources remain byte-identical to their accepted working
copies. The newly accepted locked file is
`tests/locked/test_reactive_profile_safety.cc`, SHA-256
`0e26c02edb244d7c8b42d69ea337a6bfe5209206f482edbb453e259f531295ff`.
The 499-file source freeze, original public oracles, commands, exit codes, CMake
caches and actual logs are in `P4_reactive_profile_raw/`. Every final host/test
process returned 0. WSL used g++13.3.0, CMake3.28.3 and Python3.12.3; builds in
`/dev/shm` archived their receipts before exit.

The independent same-model review is `../reviews/P4_reactive_profile_review.md`.
Its raw-hash check distinguishes Windows CRLF working bytes from Git-filtered
LF blobs; the initial diagnostic and corrected binding are retained. No source
file changed to reconcile line endings. This review is not cross-model or a
human phase gate.

## Actual compile-only builds

Existing checked ADB fallback ran the pinned compiler on UNO Q Linux. No upload,
reset or MCU execution occurred.

| Build | Reactive test | Default app |
|---|---|---|
| Source SHA prefix | 9ddaa2aa | 43d16734 |
| Checked receipt | 86cf43eb94ac4cd1808d05bd642f80f5 | fca06cbdfd124435af8b2c13eb609d0b |
| ELF SHA prefix | 01e39e39 | 21b28ee3 |
| ELF bytes | 164188 | 176040 |
| Compiler RAM payload | 251116 | 257272 |
| Conditional pristine loader peak / free span | 255632 / 6512 | 262128 / 16 |

Reactive routeNormal/checkStall symbols are present; opener execution symbols
are absent. The checked flags are exactly MATCH=0, MOTORS_ALLOWED=0,
SUMOX_P4_REACTIVE=1, default startup, compile-only. There is no new upload key.
All 101 reactive and 100 app staged sources match the repository. Default ELF,
ZSK and loader are byte-identical to D126. Exact manifests, ELFs, compiler output
and loader accounting are retained. Low-memory warnings remain visible.
These are conditional load-model figures, not live free RAM, stack or WCET.

## Remaining work

P4.1-4.7 need actual physical trials and evidence-backed tuning; no measured
performance follows from host mocks. SC-AO remains open: periodic40ms frames
cannot establish35ms target-loss braking. The next task is bounded P4-only
source-window and matched applied-receipt evidence. Read
`P4_timing_evidence_options.md` before adopting its implementation contract.
Default/P5 has only16bytes modeled load headroom, so unconditional trace growth
cannot be assumed to fit. Preserve recorder capacity and all old locked tests.
