# D126 stopping-trial software validation

2026-09-24, Asia/Dubai. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED.
Physical P3.3 measurements and phase acceptance remain pending.
Contract/public interface commit: `2a553830`; preceding accepted slice: `f39c9929`.

## Result

The exclusive stopping profile runs one actual Straight request at a selected
0.30, 0.40, 0.50, 0.60 or 0.70 final electrical cap. It preserves the genuine
START hold, source admission, Governor and MotorGate. Edge detection cancels
the trial and executes the existing complete escape before inhibition. Without
an edge, the observed 1000 ms timeout starts a full 500 ms brake, then inhibits
and enters STOP. A no-edge timeout is explicitly invalid distance evidence.
Default SEARCH cap and ordinary firmware behavior are unchanged.

Independent spec/public-header author froze 30 cases before execution, 31 for
configured button windows. All passed on first execution; no production, fixture
or assertion repair was needed. The newly accepted locked oracle is
`tests/locked/test_stop_trial_safety.cc`, SHA-256
`01213382cef215673973167663ac93acd24d5ae3d500d894fff0bed9a217261d`.
All 37 prior locked files remain exact. Original oracles and the 493-file freeze
are preserved in `P3_stop_trial_raw/`.

## Executed checks

| Check | Result |
|---|---|
| Full normal CMake/CTest | 10/10 targets PASS; main 1519 cases and Gate 187 cases; prior stand/drive/turn profiles unchanged |
| New stopping profile, M0 / M1 | 30 cases each; 269698 / 262866 assertions |
| ASan + UBSan, new M0 / M1 | Same 30 cases and assertions, PASS |
| Synthetic configured-button Runtime, normal and sanitizers | 31 cases each; 382601 / 375772 assertions, PASS |
| Synthetic duty overlays 0.40 / 0.50 / 0.60 / 0.70 | 30 cases per M0/M1 in each build, PASS |
| Tooling build-policy checks | 121 methods, PASS |
| Config registry | 2 methods, PASS; raw destination isolated from historical evidence |
| Separate reviewer | Four independent cases / 36170 assertions per M0/M1 at 0.70; all prior profile layouts identical |

`run_host.py` records exact commands, flags, return codes, timestamps, CMake
caches and LastTest logs for each profile. Every recorded process exited 0.
Windows commands used `wsl -d Ubuntu -- python3
state/analysis/P3_stop_trial_raw/run_host.py <profile>`; host tools were
g++ 13.3.0, CMake 3.28.3, Python 3.12.3. Builds were in `/dev/shm`; logs were
archived before WSL exit. Synthetic windows and duty overlays never changed
the repository's configuration or established tests.

The separate same-model reviewer inspected real implementation, wiring, receipts,
default isolation and tooling, and ran private tests. This is a separate Codex
context, not cross-model/human review. See `../reviews/P3_stop_trial_review.md`.

## Actual board-side compile-only receipts

The existing checked ADB fallback transferred staged sketches and ran the pinned
UNO Q compiler on Linux. There was no upload, reset or MCU execution.

| Build | Stopping profile | Default app |
|---|---|---|
| Source SHA prefix | 9fd0f6ed | f1d1292d |
| Receipt | b021685b32504d6695ade9efd91e7617 | b8b9a8dd0def46418d6bda375af00a07 |
| ELF SHA prefix | b4f15bfe | 21b28ee3 |
| ELF bytes | 155628 | 176040 |
| Compiler RAM payload | 245948 | 257272 |
| Conditional pristine loader peak / free span | 250232 / 11912 | 262128 / 16 |

Exact manifests, receipts, compiler outputs, ELFs and source/loader accounting
are under `P3_stop_trial_raw/stopping_distance/` and `app/`. All 101 stopping
and 100 app staged files matched current repository sources. Default ELF, ZSK
and loader are byte-identical to D125. Stopping route is present; normal combat
routing/opener/stall symbols are absent. Exact checked flags are MATCH=0,
MOTORS_ALLOWED=0, SUMOX_P3_STOP_TRIAL=1, default startup, compile-only.
The low-memory warning is retained. Loader figures are conditional source-model
results, not live RAM, stack or worst-case tick measurements.

## Limits and next action

No physical stopping distance, settling time, safe placement, peak excursion,
ring survival, electrical acceptance, motor permission or phase gate was
established. The report's terminal timestamp ends the trial request, not an
ongoing edge escape. D103 service reset may clear this report; the recorder
retains its existing wire format and does not serialize new report fields.

SC-AN retains the original at-rest measurement and supplements it with measured
peak outward excursion using the same reference as measured R_room. Actual
three-runs-per-duty data are required before cap advice or tuning approval.
Next eligible P3 software: analyze the existing countdown events for the 50-start
criterion, preserving distinctions between synthetic arithmetic, declared
provenance and physical acceptance.
